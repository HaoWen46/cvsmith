#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pypdf>=5.0", "pdfplumber>=0.11"]
# ///
"""L3 — inspect observable PDF structure and likely column geometry."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).parent))
from _report import FAIL, PASS, WARN, Report, die

PAPERS = {"letter": (612, 792), "a4": (595, 842)}
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[A-Za-z]{2,}")
ROW_TOL = 3.0
MIN_GUTTER = 14.0
MIN_SIDE_ROWS = 3
MIN_ALIGNED_ROWS = 8
MIN_ALIGNED_SHARE = 0.45


def rows(words) -> list[list[dict]]:
    bands: dict[int, list[dict]] = {}
    for word in words:
        bands.setdefault(round(float(word["top"]) / ROW_TOL), []).append(word)
    return [sorted(row, key=lambda word: word["x0"]) for _, row in sorted(bands.items())]


def column_evidence(page) -> tuple[str, str]:
    words = page.extract_words(use_text_flow=False)
    content_rows = rows(words)
    if len(words) < 30:
        return WARN, f"only {len(words)} words; column geometry is inconclusive"
    left = min(float(word["x0"]) for word in words)
    right = max(float(word["x1"]) for word in words)
    step = 2.0
    best = None
    x = left + step
    while x < right - step:
        spanning = sum(any(float(word["x0"]) <= x <= float(word["x1"]) for word in row) for row in content_rows)
        if spanning <= max(1, round(len(content_rows) * 0.05)):
            start = x
            while x < right - step and sum(any(float(word["x0"]) <= x <= float(word["x1"]) for word in row) for row in content_rows) <= max(1, round(len(content_rows) * 0.05)):
                x += step
            width = x - start
            left_rows = sum(all(float(word["x1"]) <= start for word in row) for row in content_rows)
            right_rows = sum(all(float(word["x0"]) >= x for word in row) for row in content_rows)
            if width >= MIN_GUTTER and min(left_rows, right_rows) >= MIN_SIDE_ROWS:
                candidate = (width, (start + x) / 2, left_rows, right_rows)
                if best is None or candidate[0] > best[0]:
                    best = candidate
        x += step
    if best:
        width, center, left_rows, right_rows = best
        return FAIL, f"{width:.0f}pt vertical gutter near x={center:.0f}pt with {left_rows} rows wholly left and {right_rows} wholly right; likely multi-column reading-order risk"
    right_starts = []
    midpoint = float(page.width) / 2
    for row in content_rows:
        candidates = [float(word["x0"]) for word in row if float(word["x0"]) >= midpoint]
        if candidates:
            right_starts.append(min(candidates))
    bins: dict[int, int] = {}
    for start in right_starts:
        key = round(start / 4)
        bins[key] = bins.get(key, 0) + 1
    if bins:
        key, count = max(bins.items(), key=lambda item: item[1])
        share = count / len(right_starts)
        if count >= MIN_ALIGNED_ROWS and share >= MIN_ALIGNED_SHARE:
            return FAIL, f"{count} of {len(right_starts)} right-half rows ({share:.0%}) start near x={key * 4:.0f}pt; likely second text column"
    return PASS, "no persistent interior gutter with text blocks on both sides"


def fonts_unembedded(reader) -> set[str]:
    missing = set()
    for page in reader.pages:
        resources = page.get("/Resources") or {}
        fonts = resources.get("/Font") or {}
        for font in fonts.values():
            font = font.get_object()
            descriptor = font.get("/FontDescriptor")
            if descriptor is None and font.get("/Subtype") == "/Type0":
                descendants = font.get("/DescendantFonts", [])
                descriptor = descendants[0].get_object().get("/FontDescriptor") if descendants else None
            descriptor = descriptor.get_object() if descriptor else None
            if not descriptor or not any(key in descriptor for key in ("/FontFile", "/FontFile2", "/FontFile3")):
                missing.add(str(font.get("/BaseFont", "unknown")))
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--page-budget", type=int)
    args = parser.parse_args()
    if not args.pdf.is_file():
        die(f"no such file: {args.pdf}")
    from pypdf import PdfReader
    import pdfplumber
    report = Report(layer="L3-structure", file=str(args.pdf))
    try:
        reader = PdfReader(args.pdf)
        pages = len(reader.pages)
    except Exception as exc:
        report.add("readable", FAIL, f"could not open PDF: {exc}")
        return report.emit(args.json)
    if reader.is_encrypted:
        report.add("encryption", FAIL, "PDF is encrypted")
        return report.emit(args.json)
    if pages == 0:
        report.add("page_count", FAIL, "PDF has no pages")
        return report.emit(args.json)
    budget = args.page_budget
    if budget is None:
        report.add("page_budget", WARN if pages > 1 else PASS, f"{pages} page(s); no explicit budget supplied")
    else:
        report.add("page_budget", FAIL if pages > budget else PASS, f"{pages}/{budget} page(s)")
    box = reader.pages[0].mediabox
    width, height = float(box.width), float(box.height)
    paper = next((name for name, (w, h) in PAPERS.items() if abs(width - w) < 4 and abs(height - h) < 4), None)
    report.add("page_size", PASS if paper else WARN, f"{paper or 'custom'} ({width:.0f}x{height:.0f}pt)")
    root = reader.trailer["/Root"]
    marked = root.get("/MarkInfo")
    tagged = bool(marked and marked.get("/Marked") and root.get("/StructTreeRoot"))
    report.add("tagged_pdf", PASS if tagged else WARN, "structure tree present" if tagged else "no structure tree; parsers must infer reading order")
    missing = fonts_unembedded(reader)
    report.add("fonts_embedded", FAIL if missing else PASS, "non-embedded: " + ", ".join(sorted(missing)) if missing else "all fonts embedded")
    with pdfplumber.open(args.pdf) as pdf:
        image_only = []
        column_results = []
        for number, page in enumerate(pdf.pages, 1):
            level, detail = column_evidence(page)
            column_results.append((number, level, detail))
            text = page.extract_text() or ""
            image_area = sum((image["x1"] - image["x0"]) * (image["bottom"] - image["top"]) for image in page.images)
            if len(text.strip()) < 100 and image_area > 0.6 * float(page.width) * float(page.height):
                image_only.append(number)
        contact_lines = [line for line in (pdf.pages[0].extract_text() or "").splitlines() if line.strip()]
    failed_columns = [(number, detail) for number, level, detail in column_results if level == FAIL]
    warned_columns = [(number, detail) for number, level, detail in column_results if level == WARN]
    if failed_columns:
        report.add("single_column", FAIL, "; ".join(f"p{number}: {detail}" for number, detail in failed_columns))
    elif warned_columns:
        report.add("single_column", WARN, "; ".join(f"p{number}: {detail}" for number, detail in warned_columns))
    else:
        report.add("single_column", PASS, "no likely multi-column gutter detected")
    email_line = next((index for index, line in enumerate(contact_lines) if EMAIL.search(line)), None)
    report.add("header_order", PASS if email_line is not None and email_line < 5 else WARN, f"contact line is extracted at line {email_line + 1}" if email_line is not None else "no email found in page-one extraction")
    report.add("image_pages", FAIL if image_only else PASS, f"image-only page(s): {image_only}" if image_only else "no image-only pages")
    report.metrics.update({"pages": pages, "page_width_pt": round(width, 1), "page_height_pt": round(height, 1)})
    return report.emit(args.json)


if __name__ == "__main__":
    raise SystemExit(main())
