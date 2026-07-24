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

Rasterizes each page, then verifies every extracted word draws glyphs of
its own. Two pixel tests per word bbox: light-and-empty (white-on-white,
0-opacity on a white page, text behind white shapes — no ink at all) and
zero-contrast (transparent or background-colored text over a dark or
colored shape — the shape supplies ink, the glyphs never do; a crop with
no luminance spread contains no distinguishable glyphs). Also flags
microscopic fonts, off-page text, and zero-width/invisible Unicode,
which survive rasterization but are manipulation signals on their own.
Known residual: transparent text over a busy image can still hide in
the image's own contrast — photos on a resume are their own L3 finding.

Metadata is the text channel the pixel cross-check cannot see: it
extracts into parsers while leaving zero ink on any page. BOTH channels
get the same pass — docinfo (title/author/subject/keywords) and the XMP
packet (every PDF/A file carries one) — injection markers, keyword
dumps, and an author that matches nothing on the page.

A resume that fails here doesn't just parse badly — it looks like
prompt injection / keyword stuffing and gets the candidate flagged.

Without poppler the raster cross-check cannot run, and integrity that
was not verified is integrity NOT verified: raster_available FAILs
(environment gap, not a file finding — install poppler and re-run).
The pdfplumber-only checks still run and report; the ink checks report
nothing rather than a PASS they never earned. Failing closed here is
deliberate: this layer's one forbidden output is a reassuring false
PASS.

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
MIN_GLYPH_CONTRAST = 45    # luminance spread below this = no visible glyphs
BBOX_INSET = 0.15          # crop inset to dodge antialiased neighbors
# Tolerance for the offpage/edge-crossing test below. Measured word bboxes
# across every legitimate fixture (good.pdf + every template's sparse/
# long-meta variants, generated via evals/fixtures/generate.py) never came
# closer than 34.89pt (top, twocol.pdf "Jordan") to any page edge — real
# templates keep >=0.5in margins, so no legitimate word's glyph metrics
# come anywhere near 0. This tolerance only absorbs float/rounding slop
# at the boundary itself, not real glyph overhang.
BBOX_EDGE_EPS = 0.5
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


_ALNUM_RE = re.compile(r"[^\W_]", re.UNICODE)


def is_decorative(text: str) -> bool:
    """A pure-punctuation extraction token that carries no resume
    content — a dot-leader glyph ("." or "...."), a bare "·"/"|"
    separator. It has no alphanumeric character at all. These are real,
    visible ink (they still get every integrity check below), but they
    are template decoration, not words the resume is 'made of', so they
    must not inflate the `words_checked` metric a human reads as a
    content measure (round-2 review finding 5: a right-aligned dot
    leader was 46–53% of the extractor's word count)."""
    return bool(text.strip()) and _ALNUM_RE.search(text) is None


def crop_luminance(img, bbox, scale):
    """(darkest, lightest) grayscale pixels inside the (inset) bbox,
    or None if the crop is empty."""
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
    return crop.getextrema()


def xmp_text_nodes(xml: str) -> list[tuple[str, str]]:
    """(nearest element name, text) for every non-blank XML text node.

    A tolerant tag-stack scan, not a real XML parse — hostile metadata is
    exactly where a strict parser chokes first. Attribute values are not
    scanned; XMP carries its payloads in element text."""
    import html

    nodes: list[tuple[str, str]] = []
    stack: list[str] = []
    pos = 0
    tag = re.compile(r"<[!?][^>]*>|<(/?)([A-Za-z_][\w:.-]*)[^>]*?(/?)>")
    for m in tag.finditer(xml):
        text = xml[pos:m.start()].strip()
        if text:
            # attribute to the nearest ancestor that names a field, not
            # the rdf list plumbing wrapped around it
            owner = next((t for t in reversed(stack)
                          if not t.startswith("rdf:")), stack[-1] if stack else "xmp")
            nodes.append((owner, html.unescape(text)))
        pos = m.end()
        if m.group(2) is None:
            continue  # processing instruction / comment / doctype
        closing, name, selfclosing = m.group(1), m.group(2), m.group(3)
        if closing:
            if name in stack:
                del stack[stack.index(name):]
        elif not selfclosing:
            stack.append(name)
    return nodes


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
        pdf = pdfplumber.open(str(args.pdf))
    except Exception as e:  # encrypted / corrupt / not a PDF
        report.add("readable", FAIL,
                   f"pdfplumber could not open the file: {e} — a screening "
                   "pipeline rejects it unread")
        return report.emit(args.json)

    try:
        images = convert_from_path(str(args.pdf), dpi=args.dpi)
    except Exception:
        images = None  # poppler (pdftoppm) missing/broken
    if images is None:
        report.add("raster_available", FAIL,
                   "poppler not installed — the cross-modal ink check cannot "
                   "run, so invisible text is UNVERIFIED. This is an "
                   "environment gap, not a file finding: install poppler and "
                   "re-run; never treat this file as integrity-cleared")

    invisible: list[str] = []
    faint: list[str] = []
    tiny: list[str] = []
    offpage: list[dict] = []
    all_words: list[str] = []
    zero_width_hits = 0
    total_words = 0
    decorative_tokens = 0
    xmp_raw = ""

    with pdf:
        doc_meta = pdf.metadata or {}
        try:
            from pdfminer.pdftypes import resolve1
            meta_ref = pdf.doc.catalog.get("Metadata")
            if meta_ref is not None:
                xmp_raw = resolve1(meta_ref).get_data().decode("utf-8", "replace")
        except Exception:
            xmp_raw = ""  # no XMP packet / undecodable stream — nothing to scan
        for i, page in enumerate(pdf.pages):
            gray = None
            if images is not None and i < len(images):
                gray = images[i].convert("L")
            pw, ph = float(page.width), float(page.height)
            for w in page_words(page):
                total_words += 1
                text = w["text"]
                all_words.append(text)
                if is_decorative(text):
                    decorative_tokens += 1
                zero_width_hits += sum(text.count(z) for z in ZERO_WIDTH)

                # Any bbox edge past the page box is clipped visible text —
                # not just words wholly beyond an edge (old: x1<0 / x0>pw /
                # top<0 / bottom>ph, which missed a word straddling the
                # boundary, e.g. x0=575..x1=715 on a 612pt-wide page: x0 <
                # pw so the old right-edge test never fired). Testing each
                # word's own near/far coordinate against its own edge
                # catches both the wholly-offpage case (a word entirely
                # beyond an edge still has its far coordinate past it) and
                # the partial/crossing case in one pass.
                crossed = []
                if w["x0"] < -BBOX_EDGE_EPS:
                    crossed.append("left")
                if w["x1"] > pw + BBOX_EDGE_EPS:
                    crossed.append("right")
                if w["top"] < -BBOX_EDGE_EPS:
                    crossed.append("top")
                if w["bottom"] > ph + BBOX_EDGE_EPS:
                    crossed.append("bottom")
                if crossed:
                    offpage.append({
                        "text": text,
                        "bbox": [round(w["x0"], 2), round(w["top"], 2),
                                 round(w["x1"], 2), round(w["bottom"], 2)],
                        "edges": crossed,
                    })
                    continue

                height_pt = w["bottom"] - w["top"]
                if height_pt < MIN_FONT_PT and len(text.strip()) > 1:
                    tiny.append(text)

                if gray is None or len(text.strip()) <= 1:
                    continue
                extrema = crop_luminance(
                    gray, (w["x0"], w["top"], w["x1"], w["bottom"]), scale)
                if extrema is None:
                    continue
                lo, hi = extrema
                if lo > INK_LUMINANCE:
                    invisible.append(text)          # light and empty: no ink at all
                elif hi - lo < MIN_GLYPH_CONTRAST:
                    invisible.append(text)          # uniform crop: shape ink, no glyphs
                elif lo > LIGHT_INK_LUMINANCE:
                    faint.append(text)

    # words_checked is the CONTENT-word count a reader takes as a size
    # measure — decorative dot-leader / separator glyphs are excluded so
    # a template's right-aligned date leader can't inflate it (round-2
    # review finding 5). The raw extraction total and the decorative
    # count are reported alongside so nothing is hidden.
    report.metrics["words_checked"] = total_words - decorative_tokens
    report.metrics["extracted_tokens_total"] = total_words
    report.metrics["decorative_tokens"] = decorative_tokens
    report.metrics["dpi"] = args.dpi

    if images is not None:  # no PASS line for a check that did not run
        if invisible:
            sample = " ".join(invisible[:25])
            report.add("invisible_text", FAIL,
                       f"{len(invisible)} extracted word(s) draw no glyphs of "
                       f"their own (white, transparent, or background-matched "
                       f"text). Hidden content starts: {sample!r}")
            report.extra["invisible_words"] = invisible
        else:
            report.add("invisible_text", PASS,
                       "every extracted word draws visible glyphs on its own bbox")

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
        sample = "; ".join(
            f"{o['text']!r} crosses {'/'.join(o['edges'])} edge (bbox {o['bbox']})"
            for o in offpage[:10])
        report.add("offpage_text", FAIL,
                   f"{len(offpage)} word(s) positioned outside or crossing the "
                   f"page box, clipped visible text: {sample}")
        report.extra["offpage_words"] = offpage
    else:
        report.add("offpage_text", PASS, "all text inside the page box")

    if zero_width_hits:
        report.add("zero_width_chars", FAIL,
                   f"{zero_width_hits} zero-width/invisible character(s) in the "
                   "text layer — classic keyword-cloaking artifact")
    else:
        report.add("zero_width_chars", PASS, "no invisible Unicode")

    # ── metadata: text that leaves no ink on any page ────────────────
    # Two channels, same scrutiny: docinfo and the XMP packet. Injection
    # markers, bulk dumps, and token sets absent from the visible page.
    page_text = " ".join(all_words).casefold()
    checks_before_meta = len(report.checks)

    def scan_meta_value(channel: str, field: str, value: str) -> None:
        low = value.casefold()
        hits = [m for m in INJECTION_MARKERS if m in low]
        if hits:
            report.add("metadata_injection", FAIL,
                       f"{channel} {field} carries injection marker(s) "
                       f"{', '.join(repr(h) for h in hits)}: {value!r}")

        tokens = [t.strip() for t in re.split(r"[,;]", value) if t.strip()]
        unseen = [t for t in tokens if t.casefold() not in page_text]
        if len(value) > META_STUFF_FAIL_CHARS:
            detail = (f"{channel} {field} is {len(value)} chars "
                      f"(> {META_STUFF_FAIL_CHARS}) — bulk keyword dump: "
                      f"{value[:120]!r}…")
            if unseen:
                detail += f" ({len(unseen)} token(s) never appear on the page)"
            report.add("metadata_stuffing", FAIL, detail)
        elif len(unseen) >= META_STUFF_WARN_TOKENS:
            report.add("metadata_stuffing", WARN,
                       f"{channel} {field} carries {len(unseen)} token(s) absent "
                       f"from the page text: {', '.join(unseen[:12])!r} — "
                       "keyword-stuffing pattern (escalate if these match JD "
                       "vocabulary)")

    for field, raw in doc_meta.items():
        if raw is None:
            continue
        scan_meta_value("docinfo", field, raw if isinstance(raw, str) else str(raw))

    for field, value in (xmp_text_nodes(xmp_raw) if xmp_raw else []):
        scan_meta_value("XMP", field, value)

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
                   "metadata clean (docinfo + XMP)")

    return report.emit(args.json)


if __name__ == "__main__":
    sys.exit(main())
