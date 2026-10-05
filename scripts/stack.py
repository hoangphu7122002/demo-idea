"""App stack for parallel agents: isolated slots on shared Postgres + Redis.

Run via the `scripts/stack` wrapper (= `uv run --project backend python scripts/stack.py`).

    stack lease <owner>          reserve a slot, write .env.slot in this worktree
    stack run [--db dev|test] [--ports] [--heavy] -- <cmd>
    stack release [N]            drop the slot's DBs, free it
    stack ls | gc | doctor
    stack infra ensure           compose up db + redis from the main checkout (idempotent)
    stack template refresh       rebuild app_template (migrate + reseed), swap under a lock
    stack infra down|reset       human only (STACK_ROLE=human)

Slot N: API_PORT=api_base+N, WEB_PORT=web_base+N, DBs app_sN / app_test_sN, Redis /N.
"""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import json
import os
import re
import socket
import subprocess
import sys
import time
import tomllib
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any

SLOT_FILE = ".env.slot"
MAX_WAITS = 50

# ---------------------------------------------------------------- pure helpers


def interpolate(value: str, env: dict[str, str]) -> str:
    """Expand ${VAR} and ${VAR:-default}."""

    def sub(m: re.Match[str]) -> str:
        name, default = m.group(1), m.group(3)
        return env.get(name) or (default if default is not None else "")

    return re.sub(r"\$\{(\w+)(:-([^}]*))?\}", sub, value)


def parse_env(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip("'\"")
    return out


@dataclass(frozen=True)
class Config:
    project: str
    db_url: str
    db_test_url: str
    redis_url: str
    template: str
    api_base: int
    web_base: int
    slots: int
    heavy: int
    grace_s: int

    @staticmethod
    def load(toml_text: str, env: dict[str, str], project: str) -> Config:
        raw = tomllib.loads(toml_text)
        pools, lim, ports = raw["pools"], raw.get("limits", {}), raw.get("ports", {})
        return Config(
            project=project,
            db_url=interpolate(pools["db"]["url"], env).rstrip("/"),
            db_test_url=interpolate(pools["db_test"]["url"], env).rstrip("/"),
            redis_url=interpolate(pools["redis"]["url"], env).rstrip("/"),
            template=raw.get("template", {}).get("name", "app_template"),
            api_base=int(ports.get("api_base", 8100)),
            web_base=int(ports.get("web_base", 5200)),
            slots=int(lim.get("slots", 6)),
            heavy=int(lim.get("heavy", 2)),
            grace_s=int(lim.get("grace_s", 600)),
        )


def db_dev(n: int) -> str:
    return f"app_s{n}"


def db_test(n: int) -> str:
    return f"app_test_s{n}"


def slot_env(cfg: Config, n: int) -> dict[str, str]:
    """Everything a job in slot N needs: the port math lives here."""
    api, web = cfg.api_base + n, cfg.web_base + n
    return {
        "STACK_SLOT": str(n),
        "API_PORT": str(api),
        "WEB_PORT": str(web),
        "API_URL": f"http://127.0.0.1:{api}",
        "DATABASE_URL": f"{cfg.db_url}/{db_dev(n)}",
        "TEST_DATABASE_URL": f"{cfg.db_test_url}/{db_test(n)}",
        "REDIS_URL": f"{cfg.redis_url}/{n}",
    }


def render_env(env: dict[str, str], owner: str) -> str:
    head = f"# written by `scripts/stack lease {owner}`; do not commit\n"
    return head + "".join(f"{k}={v}\n" for k, v in env.items())


def live_worktrees(cwds: Iterable[str], worktrees: Iterable[str]) -> set[str]:
    """Worktrees that have at least one process whose cwd is inside them."""
    roots = {w.rstrip("/") for w in worktrees}
    live: set[str] = set()
    for cwd in cwds:
        for root in roots:
            if cwd == root or cwd.startswith(root + "/"):
                live.add(root)
    return live


def is_dead(slot: dict[str, Any], live: set[str], now: float, grace_s: int) -> bool:
    wt = slot["worktree"].rstrip("/")
    if not Path(wt).is_dir():
        return True
    if wt in live:
        return False
    return now - float(slot.get("last_used", slot["leased_at"])) > grace_s


def pick_slot(
    reg: dict[str, Any], cfg: Config, live: set[str], now: float
) -> tuple[int, int | None]:
    """Return (slot, reclaimed): lowest free slot, else the oldest dead one."""
    slots: dict[str, Any] = reg["slots"]
    for n in range(1, cfg.slots + 1):
        if str(n) not in slots:
            return n, None
    dead = [
        (float(s["leased_at"]), int(k))
        for k, s in slots.items()
        if int(k) <= cfg.slots and is_dead(s, live, now, cfg.grace_s)
    ]
    if not dead:
        raise StackError(
            f"all {cfg.slots} slots busy and alive; see `scripts/stack doctor`, "
            "release one, or raise limits.slots in stack.toml"
        )
    n = min(dead)[1]
    return n, n


def template_heads(files: dict[str, str]) -> set[str]:
    """Alembic heads from {filename: source} of the versions folder."""
    revs: set[str] = set()
    downs: set[str] = set()
    for src in files.values():
        rev = re.search(r"^revision\s*(?::\s*str\s*)?=\s*['\"](\w+)['\"]", src, re.M)
        if not rev:
            continue
        revs.add(rev.group(1))
        down = re.search(r"^down_revision[^=]*=\s*(.+)$", src, re.M)
        if down:
            downs.update(re.findall(r"['\"](\w+)['\"]", down.group(1)))
    return revs - downs


class StackError(Exception):
    pass


# ---------------------------------------------------------------- environment


def git(*args: str, cwd: Path | None = None) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


def worktree_root(cwd: Path | None = None) -> Path:
    return Path(git("rev-parse", "--show-toplevel", cwd=cwd or Path.cwd()))


def main_root(cwd: Path | None = None) -> Path:
    common = git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=cwd)
    return Path(common).parent


REPO = Path(__file__).resolve().parent.parent


def load_config() -> Config:
    main = main_root(REPO)
    env_file = main / ".env"
    file_env = parse_env(env_file.read_text()) if env_file.exists() else {}
    env = {**file_env, **os.environ}
    project = env.get("PROJECT_NAME") or main.name
    return Config.load((REPO / "stack.toml").read_text(), env, project)


def stack_home() -> Path:
    home = Path(os.environ.get("STACK_HOME", Path.home() / ".stack"))
    home.mkdir(parents=True, exist_ok=True)
    return home


def process_cwds() -> list[str]:
    out = subprocess.run(["lsof", "-w", "-d", "cwd", "-Fn"], capture_output=True, text=True).stdout
    return [line[1:] for line in out.splitlines() if line.startswith("n")]


# ---------------------------------------------------------------- registry


class Registry:
    """JSON file guarded by an exclusive fcntl lock on a sibling .lock file."""

    def __init__(self, home: Path, project: str) -> None:
        self.path = home / f"{project}.json"
        self.lock_path = home / f"{project}.lock"

    @contextlib.contextmanager
    def locked(self) -> Iterator[dict[str, Any]]:
        with open(self.lock_path, "a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                data = self.read()
                yield data
                tmp = self.path.with_suffix(".tmp")
                tmp.write_text(json.dumps(data, indent=2, sort_keys=True))
                tmp.replace(self.path)
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def read(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if self.path.exists():
            data = json.loads(self.path.read_text() or "{}")
        data.setdefault("slots", {})
        data.setdefault("heavy_waits", [])
        data.setdefault("template", {})
        return data


# ---------------------------------------------------------------- semaphore


class Heavy:
    """N slot files; holding an flock on one = holding a heavy permit."""

    def __init__(self, home: Path, project: str, limit: int) -> None:
        self.files = [home / f"{project}.heavy.{i}" for i in range(limit)]

    def try_acquire(self, info: dict[str, Any]) -> IO[str] | None:
        for path in self.files:
            f = open(path, "a+")
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                f.close()
                continue
            f.seek(0)
            f.truncate()
            f.write(json.dumps(info))
            f.flush()
            return f
        return None

    def holders(self) -> list[dict[str, Any]]:
        out = []
        for path in self.files:
            if not path.exists():
                continue
            with open(path, "a+") as f:
                try:
                    fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    fcntl.flock(f, fcntl.LOCK_UN)
                    continue  # free
                except BlockingIOError:
                    pass
                f.seek(0)
                try:
                    out.append(json.loads(f.read() or "{}"))
                except json.JSONDecodeError:
                    out.append({"owner": "?"})
        return out


# ---------------------------------------------------------------- postgres / redis


def pg_dsn(url: str, db: str = "postgres") -> str:
    return url.replace("+psycopg", "").rstrip("/") + "/" + db


@contextlib.contextmanager
def pg(url: str, db: str = "postgres") -> Iterator[Any]:
    import psycopg

    with psycopg.connect(pg_dsn(url, db), autocommit=True, connect_timeout=3) as conn:
        yield conn


def db_exists(url: str, name: str) -> bool:
    with pg(url) as c:
        return (
            c.execute("SELECT 1 FROM pg_database WHERE datname=%s", (name,)).fetchone() is not None
        )


def ident(name: str) -> str:
    if not re.fullmatch(r"app_(s\d+|test_s\d+|template|template_new)", name):
        raise StackError(f"refusing to touch database {name!r}")
    return f'"{name}"'


def drop_db(url: str, name: str) -> None:
    with pg(url) as c:
        c.execute(f"DROP DATABASE IF EXISTS {ident(name)} WITH (FORCE)")


def template_revision(cfg: Config) -> str | None:
    try:
        with pg(cfg.db_url, cfg.template) as c:
            row = c.execute("SELECT version_num FROM alembic_version").fetchone()
            return str(row[0]) if row else None
    except Exception:
        return None


def main_heads() -> set[str]:
    root = main_root(REPO)
    for ref in ("origin/main", "main"):
        try:
            names = git("ls-tree", "--name-only", ref, "backend/migrations/versions/", cwd=root)
        except subprocess.CalledProcessError:
            continue
        files = {
            n: git("show", f"{ref}:{n}", cwd=root) for n in names.splitlines() if n.endswith(".py")
        }
        return template_heads(files)
    return set()


def warn_template_stale(cfg: Config) -> None:
    rev = template_revision(cfg)
    heads = main_heads()
    if rev is None:
        print(
            f"stack: warning: {cfg.template} missing; run `scripts/stack template refresh`",
            file=sys.stderr,
        )
    elif heads and rev not in heads:
        print(
            f"stack: warning: {cfg.template} is at {rev}, main head is {','.join(sorted(heads))}; "
            "run `scripts/stack template refresh`",
            file=sys.stderr,
        )


def port_busy(port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.2)
        return s.connect_ex(("127.0.0.1", port)) == 0


# ---------------------------------------------------------------- commands


class Stack:
    def __init__(self, cfg: Config, home: Path) -> None:
        self.cfg = cfg
        self.reg = Registry(home, cfg.project)
        self.heavy = Heavy(home, cfg.project, cfg.heavy)
        self.template_lock = home / f"{cfg.project}.template.lock"
        self.permit: IO[str] | None = None

    def _free(self, reg: dict[str, Any], n: int) -> list[str]:
        """Drop the DBs slot N created, remove .env.slot, forget the slot."""
        slot = reg["slots"].pop(str(n), None)
        if slot is None:
            return []
        dropped = []
        for name in slot.get("dbs", []):
            url = self.cfg.db_test_url if name.startswith("app_test_") else self.cfg.db_url
            drop_db(url, name)
            dropped.append(name)
        f = Path(slot["worktree"]) / SLOT_FILE
        if f.exists() and parse_env(f.read_text()).get("STACK_SLOT") == str(n):
            f.unlink()
        return dropped

    def lease(self, owner: str) -> int:
        wt = str(worktree_root())
        with self.reg.locked() as reg:
            now = time.time()
            for k, s in reg["slots"].items():
                if s["worktree"] == wt:
                    n = int(k)
                    s.update(owner=owner, last_used=now)
                    print(f"stack: {wt} already holds slot {n}")
                    break
            else:
                live = live_worktrees(
                    process_cwds(), [s["worktree"] for s in reg["slots"].values()]
                )
                n, reclaimed = pick_slot(reg, self.cfg, live, now)
                if reclaimed is not None:
                    old = reg["slots"][str(n)]
                    dropped = self._free(reg, n)
                    print(
                        f"stack: reclaimed dead slot {n} from {old['owner']} ({old['worktree']}), "
                        f"dropped {dropped or 'nothing'}"
                    )
                reg["slots"][str(n)] = {
                    "owner": owner,
                    "worktree": wt,
                    "leased_at": now,
                    "last_used": now,
                    "dbs": [],
                }
        env = slot_env(self.cfg, n)
        (Path(wt) / SLOT_FILE).write_text(render_env(env, owner))
        print(
            f"slot {n}: API_PORT={env['API_PORT']} WEB_PORT={env['WEB_PORT']} "
            f"DB={db_dev(n)} TEST_DB={db_test(n)} REDIS=/{n} -> {wt}/{SLOT_FILE}"
        )
        warn_template_stale(self.cfg)
        return n

    def release(self, n: int | None) -> None:
        if n is None:
            n = current_slot()
        with self.reg.locked() as reg:
            if str(n) not in reg["slots"]:
                raise StackError(f"slot {n} is not leased")
            dropped = self._free(reg, n)
        print(f"stack: released slot {n}, dropped {dropped or 'nothing'}")

    def gc(self) -> None:
        with self.reg.locked() as reg:
            live = live_worktrees(process_cwds(), [s["worktree"] for s in reg["slots"].values()])
            now = time.time()
            dead = [
                int(k) for k, s in reg["slots"].items() if is_dead(s, live, now, self.cfg.grace_s)
            ]
            for n in sorted(dead):
                print(
                    f"stack: gc slot {n} ({reg['slots'][str(n)]['owner']}): "
                    f"dropped {self._free(reg, n) or 'nothing'}"
                )
        if not dead:
            print("stack: nothing to collect")

    def _rows(self) -> list[str]:
        reg = self.reg.read()
        live = live_worktrees(process_cwds(), [s["worktree"] for s in reg["slots"].values()])
        now = time.time()
        rows = [f"{'slot':<5}{'owner':<16}{'state':<8}{'age':>7}  {'dbs':<28}worktree"]
        for k in sorted(reg["slots"], key=int):
            s = reg["slots"][k]
            state = (
                "live"
                if s["worktree"].rstrip("/") in live
                else "dead"
                if is_dead(s, live, now, self.cfg.grace_s)
                else "idle"
            )
            age = f"{(now - s['leased_at']) / 60:.0f}m"
            dbs = ",".join(s.get("dbs", [])) or "-"
            rows.append(f"{k:<5}{s['owner'][:15]:<16}{state:<8}{age:>7}  {dbs:<28}{s['worktree']}")
        free = self.cfg.slots - len(reg["slots"])
        rows.append(f"{free} of {self.cfg.slots} slots free")
        return rows

    def ls(self) -> None:
        print("\n".join(self._rows()))
        holders = self.heavy.holders()
        print(
            f"heavy: {len(holders)}/{self.cfg.heavy} in use"
            + "".join(f"\n  {h_desc(h)}" for h in holders)
        )

    def doctor(self) -> None:
        self.ls()
        waits = self.reg.read()["heavy_waits"]
        if waits:
            secs = [w["wait_s"] for w in waits]
            print(
                f"heavy waits (last {len(secs)}): max {max(secs):.1f}s, "
                f"avg {sum(secs) / len(secs):.1f}s, latest {secs[-1]:.1f}s"
            )
        try:
            with pg(self.cfg.db_url) as c:
                n_conn = c.execute("SELECT count(*) FROM pg_stat_activity").fetchone()[0]
                max_conn = c.execute("SHOW max_connections").fetchone()[0]
                print(f"postgres: {n_conn}/{max_conn} connections")
                cp = c.execute(
                    "SELECT checkpoints_timed + checkpoints_req, "
                    "checkpoint_write_time + checkpoint_sync_time FROM pg_stat_bgwriter"
                ).fetchone()
                last = c.execute("SELECT checkpoint_time FROM pg_control_checkpoint()").fetchone()[
                    0
                ]
                avg = cp[1] / cp[0] / 1000 if cp[0] else 0.0
                print(
                    f"postgres: last checkpoint {last.astimezone():%Y-%m-%d %H:%M:%S %Z}, "
                    f"avg checkpoint duration {avg:.1f}s over {cp[0]}"
                )
                tmpl = c.execute(
                    r"SELECT datname FROM pg_database "
                    r"WHERE datname ~ '^app_(s\d+|test_s\d+|template\w*)$' ORDER BY 1"
                ).fetchall()
                print("postgres: stack DBs: " + (", ".join(r[0] for r in tmpl) or "none"))
        except Exception as e:  # noqa: BLE001
            print(f"postgres: unreachable ({e.__class__.__name__}: {e})")
        t = self.reg.read()["template"]
        print(
            f"template: {self.cfg.template} rev={template_revision(self.cfg)} "
            f"(recorded {t.get('revision')} at {t.get('built_at', '-')}), "
            f"main heads={','.join(sorted(main_heads())) or '?'}"
        )

    # -- run

    def ensure_db(self, n: int, kind: str) -> None:
        name, url = (
            (db_dev(n), self.cfg.db_url) if kind == "dev" else (db_test(n), self.cfg.db_test_url)
        )
        t = time.perf_counter()
        if not db_exists(url, name):
            if kind == "dev":
                with open(self.template_lock, "a") as lock:
                    fcntl.flock(lock, fcntl.LOCK_SH)
                    if not db_exists(url, self.cfg.template):
                        raise StackError(
                            f"{self.cfg.template} missing; run `scripts/stack template refresh`"
                        )
                    with pg(url) as c:
                        c.execute(
                            f"CREATE DATABASE {ident(name)} TEMPLATE {ident(self.cfg.template)}"
                        )
            else:
                with pg(url) as c:
                    c.execute(f"CREATE DATABASE {ident(name)}")
            print(f"stack: created {name} in {time.perf_counter() - t:.2f}s", file=sys.stderr)
        with self.reg.locked() as reg:
            slot = reg["slots"].get(str(n))
            if slot is None:
                raise StackError(
                    f"slot {n} is not leased (stale {SLOT_FILE}?); run `scripts/stack lease`"
                )
            if name not in slot["dbs"]:
                slot["dbs"].append(name)
            slot["last_used"] = time.time()

    def acquire_heavy(self, n: int, owner: str, cmd: list[str]) -> IO[str]:
        info = {
            "owner": owner,
            "slot": n,
            "pid": os.getpid(),
            "cmd": " ".join(cmd)[:80],
            "since": time.time(),
        }
        t0 = time.time()
        next_report = 0.0
        while True:
            f = self.heavy.try_acquire(info)
            if f is not None:
                break
            if time.time() >= next_report:
                hs = "; ".join(h_desc(h) for h in self.heavy.holders()) or "?"
                print(
                    f"stack: waiting for heavy permit ({self.cfg.heavy} in use: {hs})",
                    file=sys.stderr,
                )
                next_report = time.time() + 15
            time.sleep(0.5)
        waited = time.time() - t0
        if waited > 0.5:
            print(f"stack: got heavy permit after {waited:.1f}s", file=sys.stderr)
        with self.reg.locked() as reg:
            reg["heavy_waits"] = (
                reg["heavy_waits"]
                + [{"slot": n, "owner": owner, "wait_s": round(waited, 2), "at": time.time()}]
            )[-MAX_WAITS:]
        os.set_inheritable(f.fileno(), True)  # the permit lives until the exec'd command exits
        return f

    def run(self, dbs: list[str], ports: bool, heavy: bool, cmd: list[str]) -> None:
        if not cmd:
            raise StackError("nothing to run; usage: scripts/stack run [opts] -- <cmd>")
        slot_vars = read_slot_file()
        n = int(slot_vars["STACK_SLOT"])
        owner = self.reg.read()["slots"].get(str(n), {}).get("owner", "?")
        env = slot_env(self.cfg, n)
        if ports:
            busy = [p for p in (env["API_PORT"], env["WEB_PORT"]) if port_busy(int(p))]
            if busy:
                print(f"stack: warning: port(s) {', '.join(busy)} already in use", file=sys.stderr)
        if "dev" in dbs:
            warn_template_stale(self.cfg)
        for kind in dbs:
            self.ensure_db(n, kind)
        if heavy:
            self.permit = self.acquire_heavy(n, owner, cmd)  # keep open: closing it frees the lock
        os.environ.update(env)
        os.execvp(cmd[0], cmd)

    # -- infra

    def infra_healthy(self) -> bool:
        try:
            with pg(self.cfg.db_url) as c:
                c.execute("SELECT 1")
            import redis

            return bool(redis.Redis.from_url(self.cfg.redis_url + "/0", socket_timeout=2).ping())
        except Exception:
            return False

    def infra_ensure(self) -> None:
        if self.infra_healthy():
            print("stack: infra healthy (db + redis), nothing to do")
            return
        root = main_root(REPO)
        cmd = [
            "docker",
            "compose",
            "--env-file",
            str(root / ".env"),
            "up",
            "-d",
            "--wait",
            "--no-recreate",
            "db",
            "redis",
        ]
        print(f"stack: infra not healthy, running in {root}: {' '.join(cmd)}")
        subprocess.run(cmd, cwd=root, check=True)

    def infra_destructive(self, what: str) -> None:
        if os.environ.get("STACK_ROLE") != "human":
            raise StackError(
                f"`stack infra {what}` is human-only; set STACK_ROLE=human (agents: ask the human)"
            )
        root = main_root(REPO)
        base = ["docker", "compose", "--env-file", str(root / ".env")]
        if what == "down":
            subprocess.run([*base, "down"], cwd=root, check=True)
        else:
            subprocess.run([*base, "down", "-v"], cwd=root, check=True)
            with self.reg.locked() as reg:
                reg["slots"].clear()
                reg["template"] = {}
            self.infra_ensure()

    def template_refresh(self) -> None:
        new = f"{self.cfg.template}_new"
        url = self.cfg.db_url
        backend = REPO / "backend"
        drop_db(url, new)
        with pg(url) as c:
            c.execute(f"CREATE DATABASE {ident(new)}")
        env = {**os.environ, "DATABASE_URL": f"{url}/{new}"}
        try:
            for step in (
                ["uv", "run", "alembic", "upgrade", "head"],
                ["uv", "run", "python", "scripts/reseed.py"],
            ):
                print(f"stack: {' '.join(step)} -> {new}")
                subprocess.run(step, cwd=backend, env=env, check=True)
            with pg(url, new) as c:
                rev = c.execute("SELECT version_num FROM alembic_version").fetchone()[0]
        except BaseException:
            drop_db(url, new)
            raise
        with open(self.template_lock, "a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)  # no clone in flight
            drop_db(url, self.cfg.template)
            with pg(url) as c:
                c.execute(f"ALTER DATABASE {ident(new)} RENAME TO {ident(self.cfg.template)}")
        with self.reg.locked() as reg:
            reg["template"] = {
                "revision": rev,
                "built_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "from": git("rev-parse", "--short", "HEAD", cwd=REPO),
            }
        print(f"stack: {self.cfg.template} refreshed at revision {rev}")
        heads = main_heads()
        if heads and rev not in heads:
            print(
                f"stack: warning: built from {REPO} at {rev}, main head is "
                f"{','.join(sorted(heads))}",
                file=sys.stderr,
            )


def h_desc(h: dict[str, Any]) -> str:
    since = time.time() - float(h.get("since", time.time()))
    return f"slot {h.get('slot')} {h.get('owner')} pid {h.get('pid')} {since:.0f}s: {h.get('cmd')}"


def read_slot_file() -> dict[str, str]:
    try:
        f = worktree_root() / SLOT_FILE
    except subprocess.CalledProcessError:
        raise StackError("not inside a git worktree") from None
    if not f.exists():
        raise StackError(f"no {SLOT_FILE} in {f.parent}; run `scripts/stack lease <owner>` first")
    return parse_env(f.read_text())


def current_slot() -> int:
    return int(read_slot_file()["STACK_SLOT"])


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="stack", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("lease").add_argument("owner")
    sub.add_parser("release").add_argument("slot", type=int, nargs="?")
    sub.add_parser("ls")
    sub.add_parser("gc")
    sub.add_parser("doctor")
    r = sub.add_parser("run")
    r.add_argument("--db", action="append", choices=["dev", "test"], default=[])
    r.add_argument("--ports", action="store_true")
    r.add_argument("--heavy", action="store_true")
    r.add_argument("command", nargs=argparse.REMAINDER)
    sub.add_parser("infra").add_argument("action", choices=["ensure", "down", "reset"])
    sub.add_parser("template").add_argument("action", choices=["refresh"])
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    st = Stack(load_config(), stack_home())
    try:
        match args.cmd:
            case "lease":
                st.lease(args.owner)
            case "release":
                st.release(args.slot)
            case "ls":
                st.ls()
            case "gc":
                st.gc()
            case "doctor":
                st.doctor()
            case "run":
                cmd = args.command[1:] if args.command[:1] == ["--"] else args.command
                st.run(args.db, args.ports, args.heavy, cmd)
            case "infra":
                if args.action == "ensure":
                    st.infra_ensure()
                else:
                    st.infra_destructive(args.action)
            case "template":
                st.template_refresh()
    except StackError as e:
        print(f"stack: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
