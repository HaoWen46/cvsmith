#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pypdf>=5.0",
# ]
# ///
"""L0 — extraction check: does this PDF have a healthy text layer at all?

If text extraction fails, no downstream intelligence ever sees the
candidate. Runs two independent extractors (poppler's pdftotext when
available, pypdf always) the way real screening stacks mix parsers, and
compares their output: a PDF that only one parser can read is a gamble.

usage: extract_text.py resume.pdf [--json] [--dump]
  --dump  print the extracted text (reading order) after the report
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _report import FAIL, PASS, WARN, Report, die

MIN_CHARS = 200          # below this, the text layer is effectively absent
MIN_AGREEMENT = 0.90     # cross-extractor token overlap: fail under this
WARN_AGREEMENT = 0.97    # ...warn under this
MAX_BAD_CHAR_RATIO = 0.005  # replacement/control chars per char


def pdftotext_extract(pdf: Path) -> str | None:
    if not shutil.which("pdftotext"):
        return None
    out = subprocess.run(["pdftotext", "-enc", "UTF-8", str(pdf), "-"],
                         capture_output=True, text=True)
    return out.stdout if out.returncode == 0 else None


def pypdf_extract(pdf: Path) -> tuple[str, list[str]]:
    from pypdf import PdfReader
    reader = PdfReader(str(pdf))
    pages = [(page.extract_text() or "") for page in reader.pages]
    return "\n".join(pages), pages


def token_agreement(a: str, b: str) -> float:
    """Bag-of-words overlap between two extractions.

    Different parsers legitimately order grid/table cells differently, so
    sequence similarity punishes healthy PDFs. What matters here is that
    both parsers recover the same *content*; reading order is judged from
    the primary extraction and by parse_sim."""
    ta = Counter(re.findall(r"\w+", a.casefold()))
    tb = Counter(re.findall(r"\w+", b.casefold()))
    inter = sum((ta & tb).values())
    total = sum(ta.values()) + sum(tb.values())
    return 2 * inter / total if total else 1.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dump", action="store_true")
    args = ap.parse_args()
    if not args.pdf.is_file():
        die(f"no such file: {args.pdf}")

    report = Report(layer="L0-extraction", file=str(args.pdf))

    try:
        pypdf_text, pypdf_pages = pypdf_extract(args.pdf)
    except Exception as e:  # encrypted / corrupt / not a PDF
        report.add("readable", FAIL, f"pypdf could not open the file: {e}")
        return report.emit(args.json)

    poppler_text = pdftotext_extract(args.pdf)
    primary = poppler_text if poppler_text is not None else pypdf_text

    chars = len(re.sub(r"\s", "", primary))
    report.metrics["chars"] = chars
    report.metrics["words"] = len(primary.split())
    report.metrics["pages"] = len(pypdf_pages)

    if chars < MIN_CHARS:
        report.add("text_layer", FAIL,
                   f"only {chars} non-space chars extracted (< {MIN_CHARS}) — "
                   "image-based or empty text layer; an ATS sees nothing")
    else:
        report.add("text_layer", PASS, f"{chars} chars across {len(pypdf_pages)} page(s)")

    # pages that extract to nearly nothing (image page in an otherwise fine PDF)
    thin = [i + 1 for i, p in enumerate(pypdf_pages) if len(re.sub(r"\s", "", p)) < 80]
    if thin and chars >= MIN_CHARS:
        report.add("thin_pages", WARN, f"page(s) {thin} extract almost no text")

    bad = sum(1 for ch in primary if ch == "�" or (ord(ch) < 32 and ch not in "\n\t\r"))
    ratio = bad / max(1, len(primary))
    report.metrics["bad_char_ratio"] = round(ratio, 5)
    if ratio > MAX_BAD_CHAR_RATIO:
        report.add("encoding", FAIL,
                   f"{bad} replacement/control chars ({ratio:.2%}) — broken "
                   "font encoding; parsed fields will be garbage")
    else:
        report.add("encoding", PASS, "no encoding damage detected")

    if poppler_text is not None:
        agreement = token_agreement(poppler_text, pypdf_text)
        report.metrics["extractor_agreement"] = round(agreement, 4)
        if agreement < MIN_AGREEMENT:
            report.add("extractor_agreement", FAIL,
                       f"pdftotext and pypdf recover different content "
                       f"(token overlap {agreement:.2f}) — at least one common "
                       "parser reads this PDF wrong")
        elif agreement < WARN_AGREEMENT:
            report.add("extractor_agreement", WARN,
                       f"extractors mostly agree (token overlap {agreement:.2f})")
        else:
            report.add("extractor_agreement", PASS,
                       f"two independent extractors recover the same content "
                       f"(token overlap {agreement:.2f})")
    else:
        report.add("extractor_agreement", WARN,
                   "pdftotext not installed — single-extractor check only")

    code = report.emit(args.json)
    if args.dump:
        print("\n----- extracted text (reading order) -----")
        print(primary)
    return code


if __name__ == "__main__":
    sys.exit(main())
