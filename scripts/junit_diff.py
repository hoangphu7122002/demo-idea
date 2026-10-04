#!/usr/bin/env python3
"""JUnit helpers (stdlib only).

  junit_diff.py summary <junit.xml>        -> "pass fail skip time"
  junit_diff.py diff <base.xml> <head.xml> -> markdown: newly failing / fixed / added / removed
"""
import sys
import xml.etree.ElementTree as ET


def load(path: str) -> dict[str, str]:
    """test id -> pass|fail|skip"""
    out: dict[str, str] = {}
    for tc in ET.parse(path).getroot().iter("testcase"):
        tid = f"{tc.get('classname', '')}::{tc.get('name', '')}"
        if tc.find("failure") is not None or tc.find("error") is not None:
            st = "fail"
        elif tc.find("skipped") is not None:
            st = "skip"
        else:
            st = "pass"
        out[tid] = st
    return out


def total_time(path: str) -> float:
    return sum(float(tc.get("time") or 0) for tc in ET.parse(path).getroot().iter("testcase"))


def summary(path: str) -> str:
    r = load(path)
    c = {k: sum(1 for v in r.values() if v == k) for k in ("pass", "fail", "skip")}
    return f"{c['pass']} {c['fail']} {c['skip']} {total_time(path):.1f}"


def section(title: str, ids: list[str], limit: int = 50) -> list[str]:
    lines = [f"- **{title}: {len(ids)}**"]
    for i in sorted(ids)[:limit]:
        lines.append(f"  - `{i}`")
    if len(ids) > limit:
        lines.append(f"  - ... and {len(ids) - limit} more")
    return lines


def diff(base_path: str, head_path: str) -> str:
    b, h = load(base_path), load(head_path)
    new_fail = [t for t in h if h[t] == "fail" and b.get(t) == "pass"]
    fixed = [t for t in h if h[t] == "pass" and b.get(t) == "fail"]
    added = [t for t in h if t not in b]
    removed = [t for t in b if t not in h]
    lines = section("Newly failing (was pass)", new_fail)
    lines += section("Fixed (was fail)", fixed)
    lines += section("Added", added)
    lines += section("Removed", removed)
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "summary":
        print(summary(sys.argv[2]))
    elif len(sys.argv) == 4 and sys.argv[1] == "diff":
        print(diff(sys.argv[2], sys.argv[3]))
    else:
        sys.exit(__doc__)
