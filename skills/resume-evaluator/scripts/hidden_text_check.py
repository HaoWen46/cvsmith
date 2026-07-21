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

Docinfo metadata (title/author/subject/keywords) is the one text channel
the pixel cross-check cannot see: it extracts into parsers while leaving
zero ink on any page, so it gets its own pass — injection markers,
keyword dumps, and an author that matches nothing on the page.

A resume that fails here doesn't just parse badly — it looks like
prompt injection / keyword stuffing and gets the candidate flagged.

Without poppler the raster cross-check degrades honestly: the
pdfplumber-only checks still run, raster_available WARNs, and the
ink checks report nothing rather than a PASS they never earned.

usage: hidden_text_check.py resume.pdf [--json] [--dpi 150]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _report import FAIL, PASS, WARN, Report, die

MIN_FONT_PT = 4.5          # below this, text is unreadable to humans
INK_LUMINANCE = 200        # a pixel darker than this counts as ink (0-255)
LIGHT_INK_LUMINANCE = 140  # "solid" ink for contrast confidence
BBOX_INSET = 0.15          # crop inset to dodge antialiased neighbors
ZERO_WIDTH = {"​", "‌", "‍", "⁠", "﻿", "­"}

INJECTION_MARKERS = (      # imperative-injection tells, casefolded substrings
    "ignore previous", "ignore all", "disregard", "system prompt",
    "you are a", "rank this", "recommend this candidate", "instructions:",
)
META_STUFF_FAIL_CHARS = 300   # a docinfo field longer than this is a dump
META_STUFF_WARN_TOKENS = 8    # unseen comma/semicolon tokens before WARN


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
    return crop.getextrema()[0]


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

    try:
        images = convert_from_path(str(args.pdf), dpi=args.dpi)
    except Exception:
        images = None  # poppler (pdftoppm) missing/broken — degrade, don't crash
    if images is None:
        report.add("raster_available", WARN,
                   "poppler not installed — cross-modal ink check skipped; "
                   "invisible/faint text NOT verified; install poppler")

    invisible: list[str] = []
    faint: list[str] = []
    tiny: list[str] = []
    offpage: list[str] = []
    all_words: list[str] = []
    zero_width_hits = 0
    total_words = 0

    with pdfplumber.open(str(args.pdf)) as pdf:
        doc_meta = pdf.metadata or {}
        for i, page in enumerate(pdf.pages):
            gray = None
            if images is not None and i < len(images):
                gray = images[i].convert("L")
            pw, ph = float(page.width), float(page.height)
            for w in page_words(page):
                total_words += 1
                text = w["text"]
                all_words.append(text)
                zero_width_hits += sum(text.count(z) for z in ZERO_WIDTH)

                if w["x1"] < 0 or w["top"] < 0 or w["x0"] > pw or w["bottom"] > ph:
                    offpage.append(text)
                    continue

                height_pt = w["bottom"] - w["top"]
                if height_pt < MIN_FONT_PT and len(text.strip()) > 1:
                    tiny.append(text)

                if gray is None:
                    continue
                lum = crop_min_luminance(gray, (w["x0"], w["top"], w["x1"], w["bottom"]), scale)
                if lum is None:
                    continue
                if lum > INK_LUMINANCE and len(text.strip()) > 1:
                    invisible.append(text)
                elif lum > LIGHT_INK_LUMINANCE and len(text.strip()) > 1:
                    faint.append(text)

    report.metrics["words_checked"] = total_words
    report.metrics["dpi"] = args.dpi

    if images is not None:  # no PASS line for a check that did not run
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

    # ── docinfo metadata: text that leaves no ink on any page ────────
    page_text = " ".join(all_words).casefold()
    checks_before_meta = len(report.checks)

    for field, raw in doc_meta.items():
        if raw is None:
            continue
        value = raw if isinstance(raw, str) else str(raw)
        low = value.casefold()

        hits = [m for m in INJECTION_MARKERS if m in low]
        if hits:
            report.add("metadata_injection", FAIL,
                       f"docinfo {field} carries injection marker(s) "
                       f"{', '.join(repr(h) for h in hits)}: {value!r}")

        tokens = [t.strip() for t in re.split(r"[,;]", value) if t.strip()]
        unseen = [t for t in tokens if t.casefold() not in page_text]
        if len(value) > META_STUFF_FAIL_CHARS:
            detail = (f"docinfo {field} is {len(value)} chars "
                      f"(> {META_STUFF_FAIL_CHARS}) — bulk keyword dump: "
                      f"{value[:120]!r}…")
            if unseen:
                detail += f" ({len(unseen)} token(s) never appear on the page)"
            report.add("metadata_stuffing", FAIL, detail)
        elif len(unseen) >= META_STUFF_WARN_TOKENS:
            report.add("metadata_stuffing", WARN,
                       f"docinfo {field} carries {len(unseen)} token(s) absent "
                       f"from the page text: {', '.join(unseen[:12])!r} — "
                       "keyword-stuffing pattern (escalate if these match JD "
                       "vocabulary)")

    author = doc_meta.get("Author")
    if author is not None:
        author_s = author if isinstance(author, str) else str(author)
        name_tokens = [t.casefold()
                       for t in re.findall(r"[A-Za-z]+", author_s) if len(t) >= 3]
        if name_tokens and not any(t in page_text for t in name_tokens):
            report.add("metadata_identity", WARN,
                       f"docinfo Author {author_s!r} shares no name token with "
                       "the page text — metadata identity doesn't match the "
                       "visible resume")

    if len(report.checks) == checks_before_meta:
        report.add("metadata", PASS,
                   "metadata clean (title/author/subject/keywords)")

    return report.emit(args.json)


if __name__ == "__main__":
    sys.exit(main())
