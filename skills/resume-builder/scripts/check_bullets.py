#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pdfplumber>=0.11"]
# ///
"""Measure rendered lines per bullet and optionally enforce a line limit."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

MARKERS = {"•", "●", "▪", "–", "-"}
ROW_TOL = 2.5
X_TOL = 3.0


def page_items(page, page_number: int) -> list[dict]:
    words = page.extract_words(use_text_flow=False)
    bands: dict[int, list[dict]] = {}
    markers = [word for word in words if word["text"] in MARKERS]
    for word in words:
        if word in markers:
            continue
        bands.setdefault(round(word["top"] / ROW_TOL), []).append(word)
    rows = [sorted(row, key=lambda word: word["x0"]) for _, row in sorted(bands.items())]
    starts = []
    for marker in markers:
        for index, row in enumerate(rows):
            top = min(word["top"] for word in row)
            bottom = max(word["bottom"] for word in row)
            if marker["top"] < bottom and marker["bottom"] > top and marker["x1"] <= row[0]["x0"] + X_TOL:
                starts.append((index, row[0]["x0"]))
                break
    starts = sorted(set(starts))
    items = []
    for position, (start, body_x) in enumerate(starts):
        stop = starts[position + 1][0] if position + 1 < len(starts) else len(rows)
        count = 1
        text = [word["text"] for word in rows[start]]
        for index in range(start + 1, stop):
            if not rows[index] or abs(rows[index][0]["x0"] - body_x) > X_TOL:
                break
            count += 1
            text.extend(word["text"] for word in rows[index])
        items.append({"page": page_number, "lines": count, "text": " ".join(text)})
    return items


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--max-lines", type=int)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.pdf.is_file():
        print(f"error: no such file: {args.pdf}", file=sys.stderr)
        return 2
    try:
        import pdfplumber
        with pdfplumber.open(args.pdf) as pdf:
            items = [item for number, page in enumerate(pdf.pages, 1) for item in page_items(page, number)]
    except Exception as exc:
        print(f"error: could not measure bullets: {exc}", file=sys.stderr)
        return 2
    violations = [item for item in items if args.max_lines and item["lines"] > args.max_lines]
    distribution = {lines: sum(item["lines"] == lines for item in items) for lines in sorted({item["lines"] for item in items})}
    report = {
        "layer": "bullets", "file": str(args.pdf), "file_sha256": hashlib.sha256(args.pdf.read_bytes()).hexdigest(),
        "max_lines": args.max_lines, "distribution": distribution, "bullets": items, "violations": violations,
        "result": "fail" if violations else "pass",
    }
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        summary = ", ".join(f"{lines} line(s): {count}" for lines, count in distribution.items()) or "no bullets found"
        print(f"[bullets] {args.pdf.name}: {summary}")
        for item in violations:
            print(f"  XX  p{item['page']} {item['lines']} lines: {item['text'][:100]}")
        if args.max_lines and not violations:
            print(f"  ok  every bullet fits within {args.max_lines} line(s)")
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
