#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pypdf>=5.0",
# ]
# ///
"""L1 — parse simulation: would an ATS route this resume's content into
the right fields?

Screening pipelines segment by section heading, then extract entities
(name, contact, employers, titles, date ranges) per section. This script
does the same segmentation with the same conservatism: only headings a
field-router recognizes count, everything else lands in a black hole.

usage: parse_sim.py resume.pdf [--json]
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _report import FAIL, PASS, WARN, Report, die

# Canonical section -> heading spellings routers actually recognize.
HEADINGS = {
    "summary": {"summary", "professional summary", "profile", "objective", "about"},
    "education": {"education", "academic background"},
    "experience": {"experience", "work experience", "professional experience",
                   "employment", "employment history", "work history",
                   "research experience"},
    "projects": {"projects", "selected projects", "personal projects",
                 "technical projects", "open source"},
    "skills": {"skills", "technical skills", "skills & tools", "core skills",
               "technologies"},
    "publications": {"publications", "papers"},
    "awards": {"awards", "honors", "honors & awards", "awards & honors",
               "achievements"},
    "certifications": {"certifications", "certificates", "licenses"},
    "activities": {"activities", "leadership", "volunteering", "volunteer experience",
                   "extracurricular activities"},
}
SYNONYM_TO_CANON = {s: c for c, syns in HEADINGS.items() for s in syns}

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+?\d[\d\s().-]{8,}\d)")
URL_RE = re.compile(r"(?:https?://)?(?:www\.)?[\w-]+(?:\.[\w-]+)+(?:/[\w./#-]*)?")
MONTHS = ("jan", "feb", "mar", "apr", "may", "jun",
          "jul", "aug", "sep", "oct", "nov", "dec")
DATE_RANGE_RE = re.compile(
    r"(?:(?:%s)[a-z]*\.?\s+\d{4}|\d{4})\s*[–—-]\s*"
    r"(?:(?:%s)[a-z]*\.?\s+\d{4}|\d{4}|present|current|now)"
    % ("|".join(MONTHS), "|".join(MONTHS)), re.IGNORECASE)


def extract_lines(pdf: Path) -> list[str]:
    if shutil.which("pdftotext"):
        out = subprocess.run(["pdftotext", "-enc", "UTF-8", str(pdf), "-"],
                             capture_output=True, text=True)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.splitlines()
    from pypdf import PdfReader
    text = "\n".join((p.extract_text() or "") for p in PdfReader(str(pdf)).pages)
    return text.splitlines()


def heading_key(line: str) -> str:
    return re.sub(r"[^a-z& ]", "", line.strip().casefold()).strip()


def looks_like_heading(line: str) -> bool:
    """Would a router mistake this line for a section heading?

    Only ALL-CAPS standalone lines qualify: title-case short lines are
    overwhelmingly entry content (company names, locations, degree
    lines), and flagging those would bury real signal in noise."""
    s = line.strip()
    if not s or len(s) > 40 or "," in s or s.endswith((".", ";", ":")):
        return False
    words = s.split()
    if len(words) > 5 or any(ch.isdigit() for ch in s):
        return False
    return s.isupper() and len(s) >= 3


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if not args.pdf.is_file():
        die(f"no such file: {args.pdf}")

    report = Report(layer="L1-parse-sim", file=str(args.pdf))
    lines = extract_lines(args.pdf)

    # ── segment into sections ────────────────────────────────────────
    sections: dict[str, list[str]] = {}
    unknown_headings: list[str] = []
    current = "_header"  # everything before the first recognized heading
    sections[current] = []
    for line in lines:
        key = heading_key(line)
        if key in SYNONYM_TO_CANON:
            current = SYNONYM_TO_CANON[key]
            sections.setdefault(current, [])
            continue
        if looks_like_heading(line) and len(sections.get(current, [])) > 0:
            # heading-shaped but unrecognized: a router would misroute here
            unknown_headings.append(line.strip())
        sections.setdefault(current, []).append(line)

    found = [k for k in sections if k != "_header" and any(
        l.strip() for l in sections[k])]
    report.extra["sections"] = {k: sum(1 for l in sections[k] if l.strip())
                                for k in found}
    report.extra["unknown_headings"] = unknown_headings

    if found:
        report.add("sections_found", PASS, f"recognized: {', '.join(found)}")
    else:
        report.add("sections_found", FAIL,
                   "no standard section headings recognized — the whole resume "
                   "routes into unstructured free text")

    core = {"experience", "projects"}
    if not core & set(found):
        report.add("core_sections", FAIL,
                   "neither Experience nor Projects found under a standard "
                   "heading — screeners score these fields directly")
    else:
        report.add("core_sections", PASS, "experience/projects route correctly")

    if "education" not in found:
        report.add("education_section", WARN,
                   "no Education section recognized (fine for senior CVs, "
                   "fatal for student/new-grad screening)")

    if unknown_headings:
        report.add("unknown_headings", WARN if found else FAIL,
                   "heading-shaped lines a router won't recognize: "
                   + "; ".join(repr(h) for h in unknown_headings[:6]))
    else:
        report.add("unknown_headings", PASS, "no unrecognized headings")

    # ── contact block ────────────────────────────────────────────────
    header_text = "\n".join(sections.get("_header", []))
    header_lines = [l.strip() for l in sections.get("_header", []) if l.strip()]
    contact = {
        "name_guess": header_lines[0] if header_lines else None,
        "emails": EMAIL_RE.findall(header_text),
        "phones": [p.strip() for p in PHONE_RE.findall(header_text)],
        "urls": [u for u in URL_RE.findall(header_text)
                 if "@" not in u],
    }
    report.extra["contact"] = contact

    if not contact["emails"]:
        report.add("contact_email", FAIL,
                   "no email found before the first section heading — "
                   "contact extraction will fail")
    else:
        report.add("contact_email", PASS, contact["emails"][0])

    name = contact["name_guess"]
    if not name or "@" in name or any(c.isdigit() for c in name) \
            or not 1 <= len(name.split()) <= 5:
        report.add("name_line", FAIL,
                   f"first line {name!r} doesn't look like a person's name — "
                   "name field will be misparsed")
    else:
        report.add("name_line", PASS, name)

    if not contact["phones"]:
        report.add("contact_phone", WARN, "no phone number detected in header")

    # ── dates ────────────────────────────────────────────────────────
    dated_sections = {}
    for sec in ("experience", "education", "projects"):
        if sec in sections:
            dated_sections[sec] = len(
                DATE_RANGE_RE.findall("\n".join(sections[sec])))
    report.metrics["date_ranges"] = dated_sections

    if "experience" in [s for s in found] and dated_sections.get("experience", 0) == 0:
        report.add("experience_dates", FAIL,
                   "Experience section has no parseable date ranges — "
                   "tenure fields come out empty, gap detection misfires")
    elif dated_sections:
        report.add("dates_parse", PASS, f"parsed ranges: {dated_sections}")

    return report.emit(args.json)


if __name__ == "__main__":
    sys.exit(main())
