#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pdfplumber>=0.11",
# ]
# ///
"""Measure rendered lines per bullet in a resume PDF.

Character counts are a pencil sketch; the render is the truth — line
fit depends on template, font, and margins. This reads the PDF's
geometry: bullet markers start items, and continuation lines are the
ones hanging at the body indent with no marker of their own.

Part of the builder's authoring loop (like the page budget), not the
evaluator's battery — screeners don't care how many lines a bullet
wraps to; readers do.

usage: check_bullets.py resume.pdf [--max-lines N] [--json]
  no --max-lines : report per-bullet line counts, exit 0
  --max-lines N  : exit 1 if any bullet exceeds N rendered lines
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

MARKERS = {"•", "●", "▪", "–", "-", "··"}
LINE_TOL = 2.5     # pt; words within this top-distance share a line
X_TOL = 3.0        # pt; alignment tolerance for indent matching


def lines_of(words):
    lines: dict[int, list] = {}
    for w in words:
        lines.setdefault(round(w["top"] / LINE_TOL), []).append(w)
    return [sorted(ws, key=lambda w: w["x0"])
            for _, ws in sorted(lines.items())]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--max-lines", type=int, default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if not args.pdf.is_file():
        print(f"error: no such file: {args.pdf}", file=sys.stderr)
        return 2

    import pdfplumber

    items = []
    with pdfplumber.open(str(args.pdf)) as pdf:
        for pageno, page in enumerate(pdf.pages, 1):
            words = page.extract_words(use_text_flow=False)
            # markers render smaller than body text (baseline-aligned, lower
            # top), so they can't share a naive top-bucket with their own
            # line — separate them and match by vertical overlap instead.
            marks = [w for w in words if w["text"] in MARKERS]
            rows = lines_of([w for w in words if w["text"] not in MARKERS])
            if not marks or not rows:
                continue

            def line_for(mark):
                for i, row in enumerate(rows):
                    top = min(w["top"] for w in row)
                    bot = max(w["bottom"] for w in row)
                    if mark["top"] < bot and mark["bottom"] > top:
                        return i
                return None

            starts = sorted({i for m in marks if (i := line_for(m)) is not None})
            if not starts:
                continue
            body_x = statistics.median(rows[i][0]["x0"] for i in starts)
            start_set = set(starts)
            for k, i in enumerate(starts):
                end = starts[k + 1] if k + 1 < len(starts) else len(rows)
                count = 1
                for j in range(i + 1, end):
                    if j in start_set:
                        break
                    if abs(rows[j][0]["x0"] - body_x) <= X_TOL:
                        count += 1
                    else:
                        break
                all_words = []
                for j in range(i, i + count):
                    all_words.extend(w["text"] for w in rows[j])
                text = " ".join(w["text"] for w in rows[i])
                items.append({"page": pageno, "lines": count,
                              "chars": len(" ".join(all_words)),
                              "first_line_chars": len(text),
                              "bullet": text[:70] + ("…" if len(text) > 70 else "")})

    if not items:
        print("no bullets found")
        return 0

    over = [b for b in items if args.max_lines and b["lines"] > args.max_lines]
    dist: dict[int, int] = {}
    for b in items:
        dist[b["lines"]] = dist.get(b["lines"], 0) + 1

    # Self-calibration: a wrapped bullet's first line is a FULL line, so
    # wrapped items measure this template's true capacity for their glyph
    # mix. With no wrapped items, capacity is at least the longest fit.
    wrapped = [b for b in items if b["lines"] > 1]
    if wrapped:
        capacity = int(statistics.median(b["first_line_chars"] for b in wrapped))
        cap_note = f"measured capacity ≈ {capacity} chars/line"
    else:
        capacity = max(b["chars"] for b in items)
        cap_note = f"capacity ≥ {capacity} chars/line (nothing wrapped to measure)"
    for b in items:
        b["over_by_chars"] = max(0, b["chars"] - capacity) if b["lines"] > 1 else 0

    if args.json:
        print(json.dumps({"bullets": items, "distribution": dist,
                          "measured_capacity_chars": capacity,
                          "max_lines": args.max_lines,
                          "violations": over}, indent=2, ensure_ascii=False))
    else:
        print(f"[bullets] {args.pdf.name}: {len(items)} bullets — "
              + ", ".join(f"{n} line{'s' if n > 1 else ''}: {c}"
                          for n, c in sorted(dist.items()))
              + f" · {cap_note}")
        show = over if args.max_lines else [b for b in items if b["lines"] > 1]
        for b in show:
            flag = "XX" if args.max_lines and b["lines"] > args.max_lines else "!!"
            print(f"  {flag}  {b['lines']} lines ({b['chars']} chars, cut ≳{b['over_by_chars']}): {b['bullet']}")
        if args.max_lines and not over:
            print(f"  ok  every bullet fits in {args.max_lines} line(s)")

    if over:
        print(f"\n{len(over)} bullet(s) exceed the {args.max_lines}-line budget. "
              f"Draft to ≈{capacity - 8} chars for headroom. The render is "
              "deterministic — re-rendering unchanged text is not an attempt. "
              "Escalate: (1) cut filler words; (2) still over → change structure "
              "(split the bullet, move stack/context to the tag row); (3) still "
              "over → the allocation is wrong (fewer bullets here, or drop "
              "meta.bullet_lines) — never delete a number to make weight.",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
