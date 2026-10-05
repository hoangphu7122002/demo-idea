import os
from collections.abc import Iterator
from typing import Any

import pytest

os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    f"postgresql+psycopg://app:app@127.0.0.1:{os.environ.get('DB_PORT', '5432')}/app_test",
)
os.environ["DB_NULL_POOL"] = "1"

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import event, text  # noqa: E402

from app.api.main import app  # noqa: E402
from app.core.db import async_engine, sync_engine  # noqa: E402
from app.models import Base  # noqa: E402

_TRUNCATE = text(
    "TRUNCATE "
    + ", ".join(t.name for t in Base.metadata.sorted_tables)
    + " RESTART IDENTITY CASCADE"
)

# Guard: only `db` tests get the TRUNCATE cleanup, so an unmarked test that writes
# to Postgres would leak rows into the next test. Instead of letting it, every new
# DB connection opened while an unmarked test runs raises. Both engines use NullPool
# in tests, so each session opens a fresh connection and always passes through here.
# A plain global (not a ContextVar): TestClient runs the app in another thread.
_unmarked_test: str | None = None


class UnmarkedDbAccess(RuntimeError):
    pass


def _forbid_unmarked(*_: Any, **__: Any) -> None:
    if _unmarked_test is not None:
        raise UnmarkedDbAccess(
            f"{_unmarked_test} opened a DB connection but is not marked. "
            "Add @pytest.mark.db (or pytestmark = pytest.mark.db) so it gets cleaned up."
        )


for _engine in (sync_engine, async_engine.sync_engine):
    event.listen(_engine, "do_connect", _forbid_unmarked)


@pytest.fixture(scope="session")
def _schema() -> Iterator[None]:
    """Build the schema once per session, only if some `db` test runs."""
    Base.metadata.drop_all(sync_engine)
    Base.metadata.create_all(sync_engine)
    yield


@pytest.fixture(autouse=True)
def _clean_db(request: pytest.FixtureRequest) -> Iterator[None]:
    global _unmarked_test
    if request.node.get_closest_marker("db") is None:
        _unmarked_test = request.node.nodeid  # pure test: must never touch Postgres
        try:
            yield
        finally:
            _unmarked_test = None
        return
    request.getfixturevalue("_schema")
    yield
    with sync_engine.begin() as conn:
        conn.execute(_TRUNCATE)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
