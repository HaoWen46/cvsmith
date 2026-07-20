#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pdfplumber>=0.11",
#     "pdf2image>=1.17",
#     "pillow>=10.0",
# ]
# ///
"""L2 — integrity: does the rendered page show everything the text layer
claims? The cross-modal check screening vendors run against injection.

Rasterizes each page, then verifies every extracted word actually puts
ink on its own bounding box. White-on-white text, 0-opacity text,
invisible render mode, text hidden behind white shapes — all of them
extract "normally" but leave their pixels blank, so all of them are
caught by the same test. Also flags microscopic fonts, off-page text,
and zero-width/invisible Unicode, which survive rasterization but are
manipulation signals on their own.

A resume that fails here doesn't just parse badly — it looks like
prompt injection / keyword stuffing and gets the candidate flagged.

usage: hidden_text_check.py resume.pdf [--json] [--dpi 150]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _report import FAIL, PASS, WARN, Report, die

MIN_FONT_PT = 4.5          # below this, text is unreadable to humans
INK_LUMINANCE = 200        # a pixel darker than this counts as ink (0-255)
LIGHT_INK_LUMINANCE = 140  # "solid" ink for contrast confidence
BBOX_INSET = 0.15          # crop inset to dodge antialiased neighbors
ZERO_WIDTH = {"​", "‌", "‍", "⁠", "﻿", "­"}


def page_words(page):
    """Words with bboxes from pdfplumber, tolerant defaults."""
    return page.extract_words(use_text_flow=False, keep_blank_chars=False)


def crop_min_luminance(img, bbox, scale):
    """Darkest grayscale pixel inside the (inset) bbox, or None if empty."""
    x0, top, x1, bottom = bbox
    w, h = x1 - x0, bottom - top
    x0 += w * BBOX_INSET
    x1 -= w * BBOX_INSET
    top += h * BBOX_INSET
    bottom -= h * BBOX_INSET
    px0, py0 = int(x0 * scale), int(top * scale)
    px1, py1 = max(px0 + 1, int(x1 * scale)), max(py0 + 1, int(bottom * scale))
    px1 = min(px1, img.width)
    py1 = min(py1, img.height)
    if px0 >= px1 or py0 >= py1:
        return None
    crop = img.crop((px0, py0, px1, py1))
    return min(crop.getdata())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()
    if not args.pdf.is_file():
        die(f"no such file: {args.pdf}")

    import pdfplumber
    from pdf2image import convert_from_path

    report = Report(layer="L2-integrity", file=str(args.pdf))
    scale = args.dpi / 72.0

    images = convert_from_path(str(args.pdf), dpi=args.dpi)
    invisible: list[str] = []
    faint: list[str] = []
    tiny: list[str] = []
    offpage: list[str] = []
    zero_width_hits = 0
    total_words = 0

    with pdfplumber.open(str(args.pdf)) as pdf:
        for page, img in zip(pdf.pages, images):
            gray = img.convert("L")
            pw, ph = float(page.width), float(page.height)
            for w in page_words(page):
                total_words += 1
                text = w["text"]
                zero_width_hits += sum(text.count(z) for z in ZERO_WIDTH)

                if w["x1"] < 0 or w["top"] < 0 or w["x0"] > pw or w["bottom"] > ph:
                    offpage.append(text)
                    continue

                height_pt = w["bottom"] - w["top"]
                if height_pt < MIN_FONT_PT and len(text.strip()) > 1:
                    tiny.append(text)

                lum = crop_min_luminance(gray, (w["x0"], w["top"], w["x1"], w["bottom"]), scale)
                if lum is None:
                    continue
                if lum > INK_LUMINANCE and len(text.strip()) > 1:
                    invisible.append(text)
                elif lum > LIGHT_INK_LUMINANCE and len(text.strip()) > 1:
                    faint.append(text)

    report.metrics["words_checked"] = total_words
    report.metrics["dpi"] = args.dpi

    if invisible:
        sample = " ".join(invisible[:25])
        report.add("invisible_text", FAIL,
                   f"{len(invisible)} extracted word(s) leave no ink on the "
                   f"page (white/hidden text). Hidden content starts: {sample!r}")
        report.extra["invisible_words"] = invisible
    else:
        report.add("invisible_text", PASS,
                   "every extracted word puts ink on its own bbox")

    if faint:
        report.add("faint_text", WARN,
                   f"{len(faint)} word(s) are near-background luminance "
                   f"(low-contrast gray): {' '.join(faint[:10])!r}")

    if tiny:
        report.add("microscopic_text", FAIL,
                   f"{len(tiny)} word(s) under {MIN_FONT_PT}pt — unreadable to "
                   f"humans, visible to parsers: {' '.join(tiny[:15])!r}")
        report.extra["tiny_words"] = tiny
    else:
        report.add("microscopic_text", PASS, f"no text under {MIN_FONT_PT}pt")

    if offpage:
        report.add("offpage_text", FAIL,
                   f"{len(offpage)} word(s) positioned outside the page box: "
                   f"{' '.join(offpage[:10])!r}")
    else:
        report.add("offpage_text", PASS, "all text inside the page box")

    if zero_width_hits:
        report.add("zero_width_chars", FAIL,
                   f"{zero_width_hits} zero-width/invisible character(s) in the "
                   "text layer — classic keyword-cloaking artifact")
    else:
        report.add("zero_width_chars", PASS, "no invisible Unicode")

    return report.emit(args.json)


if __name__ == "__main__":
    sys.exit(main())
