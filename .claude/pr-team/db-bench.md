# Backend test-DB isolation benchmark (2026-10-05)

Spike worktree: `/Users/hoangphu/wt-db-bench` (branch `spike/db-bench`, not pushed). Postgres 16.15 `bench-pg` :5499, DBs bench_1..4. Harness: `tests/conftest.py` (BENCH_VARIANT=A|B|C|C2|C3) + scratchpad `bench.py`.
Method: CHECKPOINT → snapshot → run → WAL diff (`pg_wal_lsn_diff`, cluster-wide) → CHECKPOINT → snapshot. "Buffers written" = Δ(pg_stat_bgwriter buffers_checkpoint+buffers_clean+buffers_backend), *including the post-run CHECKPOINT* so dirtied pages are counted. 3 reps per cell, median. par=4 = 4 pytest processes concurrently on bench_1..4, one WAL/buffer window around all 4.

Tests: 39 total → **15 pure** (no `db` marker; verified passing with psycopg connect patched to raise), **24 `db`** (4 of those — 422 validation tests — also pass without DB but kept marked to be safe).

| Variant | par | wall s | WAL MB | buffers written | pass/fail/err (sum of procs) |
|---|---|---|---|---|---|
| A drop/create per test, NullPool | 1 | 9.30 | 6.53 | 6794 | 39/0/0 |
| A | 4 | 11.39 | 26.81 | 27395 | 156/0/0 |
| B txn+SAVEPOINT rollback | 1 | 8.64 | 0.51 | 636 | **26/13/0** |
| B | 4 | 9.92 | 3.04 | 2802 | **104/52/0** |
| C schema once + TRUNCATE after each db test | 1 | 6.39 | 0.89 | 4276 | 39/0/0 |
| C | 4 | 9.03 | **3.87** | 17155 | 156/0/0 |
| C2 = C + skip TRUNCATE if clean | 1 | 7.09 | 0.85 | 3388 | 39/0/0 |
| C2 | 4 | 13.77* | **3.59** | 13613 | 156/0/0 |
| C3 = C2 + sync pool_size=3 | 1 | 5.73 | 1.19 | 3490 | 39/0/0 |
| C3 | 4 | 6.78 | **3.23** | 13506 | 156/0/0 |

\* C2 par=4 wall reps: 9.16 / 13.77 / 34.80 s — one outlier; WAL stable (3.33–3.95).
Rep spreads (WAL MB, par=4): A 25.7–27.7, B 1.8–3.7, C 3.81–4.00, C2 3.33–3.95, C3 3.17–3.35.

## Decision (agreed rule)
1. **B dropped**: 13/39 failures every run. App code commits on its own engines — sync `SyncSessionLocal` (seeds, Celery tasks, reseed) *and* async `AsyncSessionLocal` (API). Two engines ⇒ two connections ⇒ two outer txns: rows seeded via sync are invisible to the API (404s), and reseed's TRUNCATE holds AccessExclusive in the sync txn so the API blocks → **hard deadlock/hang** without `lock_timeout` (bench used 2s lock_timeout to turn hangs into failures). No committed-row leakage seen (leak check clean), but sequences leak (nextval isn't rolled back → ids drift between tests).
2. Lowest WAL at par=4: C3 3.23 MB < C2 3.59 < C 3.87 (A 26.81, ~7–8x more).
3. C vs C3 = 19.8% (within 20%) ⇒ **pick the simplest: C**. Borderline — rep ranges don't overlap (C 3.81–4.00 vs C3 3.17–3.35), so C3 is really ~15–25% lower; if the rule is re-run on noisier data it may flip.

**Recommendation: C** (schema once per session + one TRUNCATE … RESTART IDENTITY CASCADE after each `db` test, NullPool kept). Vs today (A) at par=4: WAL −86% (26.8 → 3.9 MB), buffers written −37%, wall −21%; all 156 pass.

## Caveats
- WAL is cluster-wide; the cluster was otherwise idle as far as I saw (only bench DBs). The CHECKPOINT before each run means first-touch pages emit full-page images — same for all variants.
- TRUNCATE is still the dominant cost in C (new relfilenodes for 4 tables + indexes per db test). C2's dirty check (row EXISTS on each table + `pg_sequences.last_value`) saves ~7% WAL; `pg_stat_xact_*` is useless here because the app opens a fresh connection per session (NullPool).
- C3 pools only the sync engine (pool_size=3, max_overflow=0); the async engine must stay NullPool because `TestClient` (no `with`) and `asyncio.run` create a new event loop per call. C3 gives the best wall time (6.78 s) but replaces the app's engine objects from conftest — more moving parts.
- `pg_stat_io` writes (also collected: A 1524, C 395, C2 425, C3 326 at par=4) disagree with bgwriter counters by ~40x — probably checkpointer IO stats not flushed when sampled; trust the bgwriter column.
- Wall times are noisy (laptop; ±1–2 s, one 35 s outlier). Rank WAL, not wall.
- Suite is small (39 tests); savings scale with number of `db` tests.
- Needs the `db` marker on tests — unmarked DB tests would not get cleaned. Diff in the worktree: `pytestmark = pytest.mark.db` in test_jobs/notes/posts/spam_api/spam_service/suggestions, `@pytest.mark.db` on 2 tests each in test_reseed and test_summary.

## Recommended `backend/tests/conftest.py` (not committed)
Validated: 39 passed ×2 on bench_1; ruff clean.

```python
import os
from collections.abc import Iterator

import pytest

os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    f"postgresql+psycopg://app:app@127.0.0.1:{os.environ.get('DB_PORT', '5432')}/app_test",
)
os.environ["DB_NULL_POOL"] = "1"

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.api.main import app  # noqa: E402
from app.core.db import sync_engine  # noqa: E402
from app.models import Base  # noqa: E402

_TRUNCATE = text(
    "TRUNCATE "
    + ", ".join(t.name for t in Base.metadata.sorted_tables)
    + " RESTART IDENTITY CASCADE"
)


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "db: test needs Postgres (schema + TRUNCATE after)")


@pytest.fixture(scope="session")
def _schema() -> Iterator[None]:
    """Build the schema once per session, only if some `db` test runs."""
    Base.metadata.drop_all(sync_engine)
    Base.metadata.create_all(sync_engine)
    yield


@pytest.fixture(autouse=True)
def _clean_db(request: pytest.FixtureRequest) -> Iterator[None]:
    if request.node.get_closest_marker("db") is None:
        yield  # pure test: never touches Postgres
        return
    request.getfixturevalue("_schema")
    yield
    with sync_engine.begin() as conn:
        conn.execute(_TRUNCATE)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
```
