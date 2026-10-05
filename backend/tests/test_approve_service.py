from app.services.revision import escape_mdx


def test_escape_mdx() -> None:
    assert escape_mdx("a {b} <c> d") == r"a \{b\} \<c\> d"
    assert escape_mdx("at least 2f+1 nodes") == "at least 2f+1 nodes"


def test_literal_regions_not_escaped() -> None:
    from app.services.revision import in_literal_region

    src = "text\n```js\nif (a < b) {}\n```\nand $x < y$ and more"
    assert in_literal_region(src, src.index("if (a"))
    assert in_literal_region(src, src.index("x < y"))
    assert not in_literal_region(src, src.index("text"))
    assert not in_literal_region(src, src.index("and more"))
