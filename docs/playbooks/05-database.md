# 5 · Database (Postgres + SQLAlchemy + Alembic)

- Postgres 16 with pgvector (`pgvector/pgvector:pg16`), in Docker.
- SQLAlchemy 2 with psycopg 3. One URL serves the async engine (API) and the sync engine (Celery tasks), see `backend/app/core/db.py`.
- Tests use a separate database: `app_test` by default (created by `backend/scripts/init-test-db.sql` on the first start of the db container), or `TEST_DATABASE_URL` (`app_test_sN` under `scripts/stack run --db test`). See [Tests and the `db` marker](#tests-and-the-db-marker).

## Change the schema

```sh
cd backend
uv run alembic revision --autogenerate -m "add tags to notes"
uv run alembic upgrade head
```

Always open the generated file in `backend/migrations/versions/` and review it. Autogenerate misses or mis-reads:
- column and table **renames** (it emits drop + add, which loses data),
- server defaults, enum changes, some index changes,
- data migrations (write those yourself with `op.execute`).

## Common commands

| Task | Command (from `backend/`) |
|---|---|
| apply all | `uv run alembic upgrade head` |
| undo the last one | `uv run alembic downgrade -1` |
| where am I | `uv run alembic current` |
| history | `uv run alembic history` |
| SQL shell | `docker compose exec db psql -U app app` |
| reset local data | **human only**: `docker compose down -v` (deletes the volume, every agent's DBs with it), then `make dev`. Agents: ask. |

## Tests and the `db` marker

The schema is built once per pytest session; after each test marked `db` all tables are truncated (`TRUNCATE ... RESTART IDENTITY CASCADE`). Unmarked tests never get cleanup, so they must not touch Postgres: a guard in `backend/tests/conftest.py` makes any DB connection from an unmarked test fail with `UnmarkedDbAccess`.

- A test that uses the DB (API calls that read/write, `SyncSessionLocal`, `reseed()`): add `@pytest.mark.db`, or `pytestmark = pytest.mark.db` for the whole file.
- `uv run pytest -m "not db"` runs the pure tests without any database.

## Slot DBs and the template (parallel agents)

`scripts/stack` (see the root `CLAUDE.md`) gives each worktree a slot N with its own `app_sN` (dev) and `app_test_sN` (tests) on the shared Postgres. `app_sN` is cloned from `app_template` (`CREATE DATABASE ... TEMPLATE`, under a second), which is migrated to head and seeded.

- After a migration merges to main, refresh the template from an up-to-date checkout: `make template-refresh` (= `scripts/stack template refresh`). It builds `app_template_new` (`alembic upgrade head` + `scripts/reseed.py`), then swaps it in under a lock. `stack lease`/`run --db dev` warn when the template revision differs from main's head.
- An existing `app_sN` keeps its data; to get a fresh clone, `scripts/stack release` and lease again, or migrate it in place: `scripts/stack run --db dev -- bash -c 'cd backend && uv run alembic upgrade head'`.
- `scripts/stack doctor` shows connections vs `max_connections`, checkpoint timing and every stack DB.

## Two heads after a merge

Two branches that each add a migration leave two heads; `upgrade head` then fails with "multiple heads". Fix it on main:

```sh
cd backend
uv run alembic heads
uv run alembic merge -m "merge heads" <rev1> <rev2>
uv run alembic upgrade head
```

## Safe migrations in production

Deploys run `migrate` before the new `api` and `worker` start, while old containers may still be running. Keep each migration backward-compatible:
1. **Expand**: add nullable columns or new tables; deploy code that writes both.
2. **Contract**: in a later release, drop the old columns once nothing reads them.

## pgvector

The extension is available in the image. Enable it in a migration with `op.execute("CREATE EXTENSION IF NOT EXISTS vector")`, then use `pgvector.sqlalchemy.Vector(dim)` columns. It handles RAG up to tens of millions of vectors before you need a dedicated vector DB.
