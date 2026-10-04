from app.services.revision import escape_mdx


def test_escape_mdx() -> None:
    assert escape_mdx("a {b} <c> d") == r"a \{b\} \<c\> d"
    assert escape_mdx("at least 2f+1 nodes") == "at least 2f+1 nodes"
