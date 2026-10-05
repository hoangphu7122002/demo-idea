# demo-idea

FastAPI + Celery backend (`backend/`), React + Vite frontend (`frontend/`, see `frontend/CLAUDE.md`).
Playbooks in `docs/playbooks/`.

## Parallel agents

Many agents share one Postgres (:5442) and one Redis (:6389). Each agent works in its own git worktree and its own **slot**.

1. `scripts/stack lease <your-name>` first, once per worktree. It writes `.env.slot`.
2. Run every job that needs the DB, Redis or a port through `scripts/stack run`:
   - tests: `make check-backend` (= `scripts/stack run --db test --heavy -- ...`), `make check-frontend`
   - dev DB: `scripts/stack run --db dev -- <cmd>` (clone of `app_template`, migrated + seeded)
   - servers: `scripts/stack run --db dev --ports -- <cmd>` (use `$API_PORT` / `$WEB_PORT`)
3. Never run `docker`, `docker compose`, `make dev`, `make up` or `make down`; a hook blocks them for agents. If Postgres/Redis are down: `scripts/stack infra ensure`. Anything destructive: ask the human.
4. Done: `scripts/stack release` (drops your slot's DBs).

Slot N (1–6): API `8100+N`, web `5200+N`, dev DB `app_sN`, test DB `app_test_sN`, Redis `/N`. `scripts/stack ls` / `doctor` show who holds what. After a migration lands on main: `scripts/stack template refresh`.
