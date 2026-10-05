from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import SyncSessionLocal, sync_engine
from app.models import Base
from app.seeds.post import seed_post
from app.seeds.suggestions import seed_suggestions


def reseed(session: Session | None = None) -> dict[str, int]:
    """Reset post, revision and suggestion data, then seed post + 10 suggestions."""
    Base.metadata.create_all(sync_engine)
    own = session is None
    s = session or SyncSessionLocal()
    try:
        s.execute(text("TRUNCATE suggestions, post_revisions, posts RESTART IDENTITY CASCADE"))
        s.commit()
        post = seed_post(s)
        rows = seed_suggestions(s, post)
        return {"posts": 1, "suggestions": len(rows)}
    finally:
        if own:
            s.close()
