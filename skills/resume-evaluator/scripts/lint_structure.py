#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pypdf>=5.0",
#     "pdfplumber>=0.11",
# ]
# ///
"""L3 — structure lint: is the file physically shaped like something a
parser handles well?

Checks the things that break extraction *before* content quality ever
matters: multi-column layouts (reading-order scrambler #1), missing font
embedding, image-based pages, encryption, absent tagging, page budget.

usage: lint_structure.py resume.pdf [--json] [--page-budget N]
"""

from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _report import FAIL, PASS, WARN, Report, die

PAPER_SIZES = {  # (w, h) in pt, small tolerance applied
    "letter": (612, 792),
    "a4": (595, 842),
}
COLUMN_MIN_SHARE = 0.25    # right-region share of words to suspect a column
COLUMN_BIN_PT = 4.0        # line-start alignment tolerance
COLUMN_MIN_LINES = 10      # aligned line-starts needed to call it a column


def detect_two_column(page) -> tuple[bool, str]:
    """A second text column = many lines whose first right-of-center word
    starts at the *same* x (the column's left edge), holding a substantial
    share of the page's words.

    Single-column pages produce right-of-center words too (wrapped body
    text, right-aligned dates), but their per-line start positions scatter
    with word boundaries and string widths — no dominant alignment bin.
    Binning instead of stddev keeps header/full-width outliers from
    masking a real column."""
    words = page.extract_words(use_text_flow=False)
    if len(words) < 30:
        return False, "too little text to judge"
    mid = float(page.width) / 2

    lines: dict[int, list] = {}
    for w in words:
        lines.setdefault(round(w["top"] / 3), []).append(w)

    right_starts = []
    right_words = 0
    for ws in lines.values():
        right = [w for w in ws if w["x0"] >= mid]
        right_words += len(right)
        if right:
            right_starts.append(min(w["x0"] for w in right))

    share = right_words / len(words)
    if len(right_starts) < COLUMN_MIN_LINES or share < COLUMN_MIN_SHARE:
        return False, f"right-of-center share {share:.0%} — single column"

    bins: dict[int, int] = {}
    for x in right_starts:
        bins[round(x / COLUMN_BIN_PT)] = bins.get(round(x / COLUMN_BIN_PT), 0) + 1
    top_bin, top_count = max(bins.items(), key=lambda kv: kv[1])
    if top_count >= COLUMN_MIN_LINES:
        return True, (f"{top_count} lines start a second column at "
                      f"x≈{top_bin * COLUMN_BIN_PT:.0f}pt "
                      f"({share:.0%} of words right of center)")
    return False, (f"right-side starts are ragged (largest alignment bin: "
                   f"{top_count} lines) — meta text, not a column")


def fonts_unembedded(reader) -> set[str]:
    missing = set()
    for page in reader.pages:
        res = page.get("/Resources")
        if not res or "/Font" not in res:
            continue
        for font in res["/Font"].values():
            f = font.get_object()
            name = str(f.get("/BaseFont", "?"))
            desc = f.get("/FontDescriptor")
            if desc is None and f.get("/Subtype") == "/Type0":
                for df in f.get("/DescendantFonts", []):
                    desc = df.get_object().get("/FontDescriptor")
            if desc is None:
                missing.add(name)
                continue
            desc = desc.get_object()
            if not any(k in desc for k in ("/FontFile", "/FontFile2", "/FontFile3")):
                missing.add(name)
    return missing


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--page-budget", type=int, default=None)
    args = ap.parse_args()
    if not args.pdf.is_file():
        die(f"no such file: {args.pdf}")

    import pdfplumber
    from pypdf import PdfReader

    report = Report(layer="L3-structure", file=str(args.pdf))
    try:
        reader = PdfReader(str(args.pdf))
        encrypted = reader.is_encrypted
        n_pages = len(reader.pages) if not encrypted else 0  # force the parse; pypdf is lazy
    except Exception as e:  # corrupt / not a PDF
        report.add("readable", FAIL,
                   f"pypdf could not open the file: {e} — a screening "
                   "pipeline rejects it unread")
        return report.emit(args.json)

    if encrypted:
        report.add("encryption", FAIL, "file is encrypted — many parsers refuse it")
        return report.emit(args.json)

    report.metrics["pages"] = n_pages
    if args.page_budget is not None:
        if n_pages > args.page_budget:
            report.add("page_budget", FAIL,
                       f"{n_pages} pages exceeds budget of {args.page_budget}")
        else:
            report.add("page_budget", PASS, f"{n_pages}/{args.page_budget} pages")

    box = reader.pages[0].mediabox
    w, h = float(box.width), float(box.height)
    size = next((nm for nm, (pw, ph) in PAPER_SIZES.items()
                 if abs(w - pw) < 4 and abs(h - ph) < 4), None)
    if size:
        report.add("page_size", PASS, f"{size} ({w:.0f}x{h:.0f}pt)")
    else:
        report.add("page_size", WARN,
                   f"unusual page size {w:.0f}x{h:.0f}pt — expected letter or A4")

    # tagging: cvsmith output is tagged; untagged third-party PDFs still parse,
    # so this is a warning, not a failure.
    mark_info = reader.trailer["/Root"].get("/MarkInfo")
    tagged = bool(mark_info and mark_info.get("/Marked")) \
        and "/StructTreeRoot" in reader.trailer["/Root"]
    if tagged:
        report.add("tagged_pdf", PASS, "structure tree present (tagged PDF)")
    else:
        report.add("tagged_pdf", WARN,
                   "no structure tree — extraction falls back to geometric "
                   "heuristics (cvsmith templates always emit tagged PDFs)")

    missing = fonts_unembedded(reader)
    if missing:
        report.add("fonts_embedded", FAIL,
                   "non-embedded font(s): " + ", ".join(sorted(missing))
                   + " — text may render/extract differently elsewhere")
    else:
        report.add("fonts_embedded", PASS, "all fonts embedded")

    with pdfplumber.open(str(args.pdf)) as pdf:
        col_pages = []
        image_pages = []
        for i, page in enumerate(pdf.pages, 1):
            is_two, detail = detect_two_column(page)
            if is_two:
                col_pages.append((i, detail))
            text_chars = len((page.extract_text() or "").strip())
            img_area = sum((im["x1"] - im["x0"]) * (im["bottom"] - im["top"])
                           for im in page.images)
            if text_chars < 100 and img_area > 0.6 * float(page.width) * float(page.height):
                image_pages.append(i)

    if col_pages:
        report.add("single_column", FAIL,
                   "multi-column layout detected — reading order scrambles in "
                   "most parsers. " + "; ".join(f"p{p}: {d}" for p, d in col_pages))
    else:
        report.add("single_column", PASS, "single-column layout")

    if image_pages:
        report.add("image_pages", FAIL,
                   f"page(s) {image_pages} are images with no real text layer")
    else:
        report.add("image_pages", PASS, "no image-only pages")

    return report.emit(args.json)


if __name__ == "__main__":
    sys.exit(main())
