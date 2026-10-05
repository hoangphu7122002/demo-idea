"""Pure unit tests for scripts/stack.py (no DB, no Redis, no docker)."""

import fcntl
import importlib.util
import sys
import threading
import time
from pathlib import Path
from typing import Any

import pytest

_PATH = Path(__file__).resolve().parents[2] / "scripts" / "stack.py"
_spec = importlib.util.spec_from_file_location("stack", _PATH)
assert _spec and _spec.loader
stack: Any = importlib.util.module_from_spec(_spec)
sys.modules["stack"] = stack
_spec.loader.exec_module(stack)

TOML = """
[pools.db]
url = "postgresql+psycopg://app:app@127.0.0.1:${DB_PORT:-5432}"
[pools.db_test]
url = "postgresql+psycopg://app:app@127.0.0.1:${DB_TEST_PORT:-5443}"
[pools.redis]
url = "redis://127.0.0.1:${REDIS_PORT:-6379}"
[template]
name = "app_template"
[limits]
slots = 3
heavy = 2
grace_s = 60
"""


def cfg(**env: str) -> Any:
    return stack.Config.load(TOML, env, "proj")


def test_config_interpolates_env_and_defaults() -> None:
    c = cfg(DB_PORT="5442")
    assert c.db_url == "postgresql+psycopg://app:app@127.0.0.1:5442"
    assert c.db_test_url.endswith(":5443")
    assert c.redis_url == "redis://127.0.0.1:6379"
    assert (c.slots, c.heavy, c.api_base, c.web_base) == (3, 2, 8100, 5200)


def test_slot_env_port_math() -> None:
    env = stack.slot_env(cfg(DB_PORT="5442", REDIS_PORT="6389"), 4)
    assert env == {
        "STACK_SLOT": "4",
        "API_PORT": "8104",
        "WEB_PORT": "5204",
        "API_URL": "http://127.0.0.1:8104",
        "DATABASE_URL": "postgresql+psycopg://app:app@127.0.0.1:5442/app_s4",
        "TEST_DATABASE_URL": "postgresql+psycopg://app:app@127.0.0.1:5443/app_test_s4",
        "REDIS_URL": "redis://127.0.0.1:6389/4",
    }
    assert stack.parse_env(stack.render_env(env, "me")) == env


def test_live_worktrees_matches_prefix_on_path_boundary() -> None:
    cwds = ["/w/a/backend", "/w/ab", "/tmp"]
    assert stack.live_worktrees(cwds, ["/w/a", "/w/abc", "/w/b"]) == {"/w/a"}
    assert stack.live_worktrees(["/w/b"], ["/w/b/"]) == {"/w/b"}


def test_is_dead(tmp_path: Path) -> None:
    now = 1000.0
    slot = {"worktree": str(tmp_path), "leased_at": 0.0, "last_used": 990.0}
    assert not stack.is_dead(slot, set(), now, grace_s=60)  # idle but within grace
    assert stack.is_dead(slot, set(), now + 100, grace_s=60)  # idle past grace
    assert not stack.is_dead(slot, {str(tmp_path)}, now + 100, grace_s=60)  # process in it
    gone = {**slot, "worktree": str(tmp_path / "gone")}
    assert stack.is_dead(gone, {str(tmp_path / "gone")}, now, grace_s=60)  # worktree removed


def test_pick_slot_lowest_free_then_oldest_dead(tmp_path: Path) -> None:
    c = cfg()
    a, b, d = (tmp_path / x for x in "abd")
    for p in (a, b, d):
        p.mkdir()

    def s(wt: Path, at: float) -> dict[str, Any]:
        return {"worktree": str(wt), "leased_at": at, "last_used": at}

    reg: dict[str, Any] = {"slots": {"1": s(a, 10), "3": s(b, 20)}}
    assert stack.pick_slot(reg, c, set(), 1000) == (2, None)
    reg["slots"]["2"] = s(d, 5)
    # all taken: 1 and 2 dead, 2 is oldest
    assert stack.pick_slot(reg, c, {str(b)}, 1000) == (2, 2)
    assert stack.pick_slot(reg, c, {str(b), str(d)}, 1000) == (1, 1)
    with pytest.raises(stack.StackError, match="busy"):
        stack.pick_slot(reg, c, {str(a), str(b), str(d)}, 1000)


def test_registry_lock_is_exclusive(tmp_path: Path) -> None:
    reg = stack.Registry(tmp_path, "proj")
    with reg.locked() as data:
        data["slots"]["1"] = {"owner": "x"}
        with open(reg.lock_path, "a") as other, pytest.raises(BlockingIOError):
            fcntl.flock(other, fcntl.LOCK_EX | fcntl.LOCK_NB)
    assert reg.read()["slots"] == {"1": {"owner": "x"}}


def test_concurrent_leases_never_share_a_slot(tmp_path: Path) -> None:
    c = cfg()
    reg = stack.Registry(tmp_path, "proj")
    got: list[int] = []
    barrier = threading.Barrier(3)

    def lease(i: int) -> None:
        barrier.wait()
        with reg.locked() as data:
            n, _ = stack.pick_slot(data, c, set(), time.time())
            time.sleep(0.05)  # widen the race window
            data["slots"][str(n)] = {"worktree": str(tmp_path / str(i)), "leased_at": time.time()}
            got.append(n)

    threads = [threading.Thread(target=lease, args=(i,)) for i in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sorted(got) == [1, 2, 3]
    assert sorted(reg.read()["slots"]) == ["1", "2", "3"]


def test_heavy_semaphore_limits_and_reports_holders(tmp_path: Path) -> None:
    heavy = stack.Heavy(tmp_path, "proj", 2)
    a = heavy.try_acquire({"owner": "a", "slot": 1})
    b = heavy.try_acquire({"owner": "b", "slot": 2})
    assert a and b
    assert heavy.try_acquire({"owner": "c", "slot": 3}) is None
    assert sorted(h["owner"] for h in heavy.holders()) == ["a", "b"]
    a.close()
    c = heavy.try_acquire({"owner": "c", "slot": 3})
    assert c is not None
    assert sorted(h["owner"] for h in heavy.holders()) == ["b", "c"]
    b.close()
    c.close()
    assert heavy.holders() == []


def test_template_heads_from_migration_sources() -> None:
    files = {
        "a.py": "revision: str = 'aaa'\ndown_revision: str | None = None\n",
        "b.py": 'revision = "bbb"\ndown_revision = "aaa"\n',
        "c.py": "revision = 'ccc'\ndown_revision = ('bbb',)\n",
    }
    assert stack.template_heads(files) == {"ccc"}


def test_ident_refuses_shared_databases() -> None:
    assert stack.ident("app_s3") == '"app_s3"'
    assert stack.ident("app_template_new") == '"app_template_new"'
    for bad in ("app", "app_test", "app_review", "app_test_b1", "postgres", 'app_s1"; --'):
        with pytest.raises(stack.StackError):
            stack.ident(bad)


def test_destructive_infra_needs_human(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("STACK_ROLE", raising=False)
    st = stack.Stack(cfg(), tmp_path)
    for what in ("down", "reset"):
        with pytest.raises(stack.StackError, match="human-only"):
            st.infra_destructive(what)
