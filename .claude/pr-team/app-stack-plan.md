# App stack for parallel agents: plan

Decided 2026-10-05 (grilling session). Goal: parallel builders/reviewers never collide on ports or databases, and never spawn infra ad hoc. One app stack hands out isolated slots.

## Decisions

| # | Question | Choice |
|---|---|---|
| 1 | Isolation level | **Shared infra, logical isolation**: one Postgres + one Redis; per-slot DB names, Redis DB index and ports |
| 2 | How agents get a slot | **`stack` CLI + JSON registry + file lock** (no daemon) |
| 3 | Dead slots | **Reclaimed on lease** when no process runs in the slot's worktree; plus `stack gc` |
| 4 | Slot DB contents | **Clone from `app_template`** (migrated + seeded); drop on release |
| 5 | Load on shared Postgres | **Lazy resources + heavy-job semaphore** (default 2); separate `db-test` pool deferred until metrics say so |
| 6 | Who runs infra | **Self-service by capability**: safe ops (lease/run/release/ensure/template refresh/gc) for all; destructive ops (down, reset, recreate, config) human/lead only; raw docker blocked for all agents via PreToolUse hook on `agent_id` |
| 7 | Test DB isolation | **C: schema once per session + one TRUNCATE after each `db` test** (measured: WAL −86% at parallel=4, 156/156 pass; B rejected, 13/39 fail). C3 (sync pool) as later follow-up |

## Architecture

```
                 ┌─────────────── APP STACK ────────────────┐
 agent ─ lease ─▶│ scripts/stack  (CLI)                      │
 agent ─ run ───▶│  registry ~/.stack/demo-idea.json + flock │
                 │  stack.toml: pools, limits                │
                 │  semaphore: heavy jobs                    │
                 └──┬───────────────┬───────────────┬───────┘
                    │               │               │
           pool db :5442     pool db_test       pool redis :6389
           app_template      (= :5442 now,      /N per slot
           app_sN (clone)     :5443 later)
                             app_test_sN
 hook guard-infra: blocks raw docker/compose for any agent (has agent_id)
```

Slot N resources (created only when a job needs them):

| Resource | Value |
|---|---|
| API port | 8100 + N |
| Web port | 5200 + N |
| Dev DB | `app_sN` (clone of `app_template`) |
| Test DB | `app_test_sN` (empty; schema made by pytest session) |
| Redis | `redis://127.0.0.1:6389/N` |

## Commands

| Command | Who | What |
|---|---|---|
| `stack lease <owner>` | all | reserve a free slot (reclaims dead ones), write `.env.slot` |
| `stack run [--db dev\|test] [--ports] [--heavy] -- <cmd>` | all | create needed resources lazily, export env, queue heavy jobs |
| `stack release <N>` | all | drop the slot's DBs, free the slot |
| `stack ls` / `stack doctor` | all | owners, liveness, semaphore wait, Postgres health signals |
| `stack gc` | all | reclaim slots with no live process |
| `stack infra ensure` | all | `compose up` from the main repo with main `.env`, idempotent, never recreates |
| `stack template refresh` | all (locked) | rebuild `app_template` at main head (build new, then rename swap) |
| `stack infra down` / `reset` | human / lead when asked | destructive |

## Work items (PRs, in order)

| # | PR | Folder | Content | Acceptance |
|---|---|---|---|---|
| 1 | `test-db-truncate` | backend/tests | conftest variant C; `db` marker on 6 files + 4 tests; check that unmarked tests can't reach the DB | 39 tests pass; `pytest -m "not db"` passes with DB down; WAL at par=4 ≤ 5 MB |
| 2 | `stack-cli-core` | scripts/stack | lease/release/ls/gc, registry + flock, liveness by worktree processes, `.env.slot` | two concurrent leases never share a slot; dead slot reclaimed |
| 3 | `stack-cli-resources` | scripts/stack | `run --db dev\|test --ports --heavy`, template clone, semaphore, `stack.toml` | slot DB ready ≤ 2 s; 3rd heavy job waits; `ls` shows waits |
| 4 | `stack-infra` | scripts/stack + Makefile | `infra ensure`, `template refresh`, `doctor`; `make check-*` stop calling compose and use `stack run` | `make check-backend` from a worktree without `.env` never touches containers |
| 5 | `guard-infra-hook` | .claude | PreToolUse hook: block docker/compose/`make dev`/`down -v` when `agent_id` present | builder call blocked with hint; main session allowed |
| 6 | `docs-parallel-agents` | docs + CLAUDE.md | root CLAUDE.md "Parallel agents"; playbook 05 marks `down -v` human-only | — |
| 7 | plugin: pr-team | bach-workflow | builder/reviewer prompts use `stack lease/run`; lead preflight `stack infra ensure` + `template refresh` | — |
| 8 | (later) `test-db-pool` | backend/tests | C3: small sync pool | WAL ≤ C −15% |
| 9 | (later, on metrics) `db-test-pool` | compose + stack.toml | `db-test` fsync=off tmpfs :5443 | enable when heavy wait > 60 s or checkpoint > 30 s |

Order: 1 is independent. 2 → 3 → 4 serial (same folder). 5 and 6 parallel after 4. 7 after 4.

## Risks

- Agent forgets `stack run` → mitigated by Makefile targets calling it and by the hook.
- Template stale vs main → `lease` warns; refresh after migration merges.
- Unmarked DB test not cleaned → check in PR 1.
- Liveness by worktree processes may misjudge a slot whose agent is idle with no process → only reclaim when a new lease needs it, oldest first.

## Not yet decided

- Celery worker per slot or shared (queues on Redis `/N` keep them apart).
- Max slots (default 6) and heavy limit (default 2): tune from `stack doctor`.
