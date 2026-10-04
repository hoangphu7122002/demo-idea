#!/usr/bin/env python3
"""Derive routes to screenshot from changed frontend files (one path per stdin line).

Prints a comma-separated route list, or nothing if none can be derived.
Rules: pages/<X>Page.tsx -> its route in router.tsx; features/<f>/* -> routes of pages importing
features/<f>; router.tsx / AppShell / shared components / theme -> all static routes.
Routes with params (':slug') are skipped; pass SHOT_ROUTES for those.
"""
import re
import sys
from pathlib import Path

SRC = Path("frontend/src")


def routes_by_page() -> dict[str, str]:
    """PageName -> '/path' parsed from router.tsx lazy imports."""
    text = (SRC / "app/router.tsx").read_text()
    out: dict[str, str] = {}
    for m in re.finditer(r"path:\s*'([^']+)'.*?pages/(\w+)'", text):
        out[m.group(2)] = "/" + m.group(1)
    return out


def main() -> None:
    changed = [ln.strip() for ln in sys.stdin if ln.strip().startswith("frontend/src/")]
    by_page = routes_by_page()
    static = {p: r for p, r in by_page.items() if ":" not in r and "*" not in r}
    picked: set[str] = set()
    for f in changed:
        rel = f[len("frontend/src/"):]
        if rel.startswith("pages/"):
            page = Path(rel).stem
            if page in static:
                picked.add(static[page])
        elif rel.startswith("features/"):
            feat = rel.split("/")[1]
            for page_file in (SRC / "pages").glob("*.tsx"):
                if f"features/{feat}/" in page_file.read_text() and page_file.stem in static:
                    picked.add(static[page_file.stem])
        elif rel.startswith(("app/", "components/")):
            picked.update(static.values())
    print(",".join(sorted(picked)))


main()
