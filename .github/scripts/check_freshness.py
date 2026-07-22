#!/usr/bin/env python3
"""Check `Verify by:` stamps in skill references against today.

Normal runs warn about stale references; --strict (the monthly
scheduled CI run) fails on them. See MAINTENANCE.md for the doctrine:
the repo re-verifies perishable facts on a schedule so user sessions
never have to.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

STAMP = re.compile(r"^Verify by:\s*(\d{4})-(\d{2})", re.MULTILINE)
LAST = re.compile(r"^Last verified:", re.MULTILINE)


def main() -> int:
    strict = "--strict" in sys.argv
    root = Path(__file__).resolve().parents[2]
    stale: list[str] = []
    unstamped: list[str] = []
    today = date.today()

    for ref in sorted(root.glob("skills/*/references/**/*.md")):
        text = ref.read_text(encoding="utf-8")
        m = STAMP.search(text)
        if m:
            due = date(int(m.group(1)), int(m.group(2)), 1)
            if (due.year, due.month) < (today.year, today.month):
                stale.append(f"{ref.relative_to(root)} (due {due:%Y-%m})")
        elif LAST.search(text):
            unstamped.append(str(ref.relative_to(root)))

    for f in unstamped:
        level = "error" if strict else "warning"
        print(f"::{level} file={f}::has 'Last verified' but no 'Verify by' "
              "stamp — unstamped perishables never come due, so strict runs "
              "fail them")
    for f in stale:
        level = "error" if strict else "warning"
        print(f"::{level}::stale reference: {f} — run the MAINTENANCE.md refresh")

    if not stale and not unstamped:
        print("all perishable references are within their verify-by window")
    return 1 if (strict and (stale or unstamped)) else 0


if __name__ == "__main__":
    sys.exit(main())
