#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pdfplumber>=0.11"]
# ///
"""Measure lower-page whitespace in a rendered PDF.

This is an authoring diagnostic, not a quality decision. It warns when a one-page
resume ends unusually high or when a final continuation page looks like a spill.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

PASS, WARN = "pass", "warn"


def measure(path: Path) -> dict:
    import pdfplumber

    with pdfplumber.open(path) as pdf:
        if not pdf.pages:
            raise ValueError("PDF has no pages")
        pages = []
        for number, page in enumerate(pdf.pages, 1):
            words = page.extract_words(use_text_flow=False)
            if not words:
                pages.append({"page": number, "measurable": False})
                continue
            end = max(float(word["bottom"]) for word in words)
            height = float(page.height)
            pages.append({
                "page": number,
                "measurable": True,
                "height_pt": round(height, 1),
                "content_end_pt": round(end, 1),
                "content_end_ratio": round(end / height, 3),
                "lower_whitespace_ratio": round(max(0.0, (height - end) / height), 3),
            })
    return {"pages": len(pages), "page_measurements": pages}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--budget", type=int, default=1)
    parser.add_argument("--min-end", type=float, default=0.62, help="one-page content-end ratio that avoids a warning")
    parser.add_argument("--min-last-end", type=float, default=0.35, help="multi-page final-page content-end ratio that avoids a spill warning")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.pdf.is_file():
        print(f"error: no such file: {args.pdf}", file=sys.stderr)
        return 2
    try:
        metrics = measure(args.pdf)
    except Exception as exc:
        print(f"error: could not measure {args.pdf}: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    checks = []
    pages = metrics["pages"]
    checks.append({
        "check_id": "page_budget",
        "level": WARN if pages > args.budget else PASS,
        "detail": f"{pages} page(s), budget {args.budget}",
    })
    last = metrics["page_measurements"][-1]
    if not last["measurable"]:
        checks.append({"check_id": "lower_whitespace", "level": WARN, "detail": "final page has no extractable words; lower whitespace is unmeasured"})
    else:
        floor = args.min_last_end if pages > 1 else args.min_end
        ratio = last["content_end_ratio"]
        blank = round(last["lower_whitespace_ratio"] * 100)
        if ratio < floor:
            shape = "possible orphan spill" if pages > 1 else "large lower-page whitespace"
            detail = f"content ends at {round(ratio * 100)}% of page height; {blank}% remains below ({shape}; inspect the page, recover stronger evidence if available, and never pad to move this number)"
            level = WARN
        else:
            detail = f"content ends at {round(ratio * 100)}% of page height; {blank}% remains below"
            level = PASS
        checks.append({"check_id": "lower_whitespace", "level": level, "detail": detail})
    report = {
        "layer": "fill",
        "file": str(args.pdf),
        "file_sha256": hashlib.sha256(args.pdf.read_bytes()).hexdigest(),
        "result": WARN if any(check["level"] == WARN for check in checks) else PASS,
        "checks": checks,
        "metrics": metrics,
    }
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"[fill] {args.pdf.name}")
        icons = {PASS: "ok", WARN: "!!"}
        for check in checks:
            print(f"  {icons[check['level']]}  {check['check_id']}: {check['detail']}")
        print(f"  => {report['result'].upper()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
