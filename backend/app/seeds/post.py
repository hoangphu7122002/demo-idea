"""Seeded English MDX post for the demo. Contains a code block, KaTeX and the demo sentence."""

from sqlalchemy.orm import Session

from app.models import Post, PostRevision

SLUG = "raft-consensus-in-practice"
TITLE = "Raft Consensus in Practice"

SOURCE = """\
# Raft Consensus in Practice

Raft keeps a replicated log consistent across servers. A cluster elects one leader, and the
leader accepts client writes and replicates them to followers.

## Quorums

A write is committed once a majority of servers has stored it. With a cluster of size $n$, a
majority is $\\lfloor n/2 \\rfloor + 1$ servers, so the cluster tolerates $f$ failures when
$n \\ge 2f + 1$.

To survive a single crashed server, a Raft cluster needs exactly 3 nodes, because two of them
still form a majority.

$$
\\text{quorum}(n) = \\left\\lfloor \\frac{n}{2} \\right\\rfloor + 1
$$

## Leader election

Each server waits for a randomized timeout. If it hears no heartbeat, it becomes a candidate:

```python
def on_election_timeout(state):
    state.term += 1
    state.role = "candidate"
    state.voted_for = state.id
    votes = 1 + request_votes(state.peers, state.term)
    if votes >= quorum(len(state.peers) + 1):
        state.role = "leader"
```

The randomized timeout makes split votes rare, and they resolve on the next term.
"""


def seed_post(session: Session) -> Post:
    """Insert the demo post with revision 1 (idempotent by slug)."""
    existing = session.query(Post).filter_by(slug=SLUG).one_or_none()
    if existing is not None:
        return existing
    post = Post(slug=SLUG, title=TITLE, source=SOURCE)
    post.revisions.append(PostRevision(number=1, source=SOURCE))
    session.add(post)
    session.commit()
    return post
