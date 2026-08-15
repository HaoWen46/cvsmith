#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pypdf>=5"]
# ///
"""L1: check conventional English section, contact, and date routing."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).parent))
from _report import FAIL, PASS, WARN, Report, die

HEADINGS = {
    "summary": {"summary", "professional summary", "profile", "objective"},
    "education": {"education", "academic background"},
    "experience": {"experience", "work experience", "professional experience", "employment", "research experience", "teaching experience", "industry experience"},
    "projects": {"projects", "selected projects", "personal projects", "technical projects", "open source"},
    "skills": {"skills", "technical skills", "skills & tools", "core skills", "technologies"},
    "publications": {"publications", "papers", "publications & awards", "publications & honors"},
    "awards": {"awards", "honors", "honors & awards", "awards & honors", "achievements"},
    "certifications": {"certifications", "certificates", "licenses"},
    "activities": {"activities", "leadership", "volunteering", "volunteer experience"},
}
HEADING = {label: section for section, labels in HEADINGS.items() for label in labels}
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?:\+?\(?\d[\d\s().-]{8,}\d)")
URL = re.compile(r"(?:https?://)?(?:www\.)?[\w-]+(?:\.[\w-]+)+(?:/[\w./#-]*)?")
IDENTIFIER = re.compile(r"\b\d{4}-\d{4}-\d{4}-\d{3}[\dXx]\b")
MONTHS = "jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec"
DATE_RANGE = re.compile(rf"(?:(?:{MONTHS})[a-z]*\.?\s+\d{{4}}|\d{{4}})\s*[–—-]\s*(?:(?:{MONTHS})[a-z]*\.?\s+\d{{4}}|\d{{4}}|present|current|now)", re.I)


def extract_lines(pdf: Path) -> list[str]:
    if shutil.which("pdftotext"):
        result = subprocess.run(["pdftotext", "-enc", "UTF-8", str(pdf), "-"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.splitlines()
    from pypdf import PdfReader
    return "\n".join(page.extract_text() or "" for page in PdfReader(pdf).pages).splitlines()


def heading_key(line: str) -> str:
    return re.sub(r"[^a-z& ]", "", line.strip().casefold()).strip()


def looks_like_heading(line: str) -> bool:
    value = line.strip()
    return bool(value and len(value) <= 40 and len(value.split()) <= 5 and value.isupper() and not any(char.isdigit() for char in value) and not value.endswith((".", ";", ":")))


def identifier_like(value: str) -> bool:
    groups = [group for group in re.split(r"[^0-9Xx]+", value.strip()) if group]
    return len(groups) >= 4 and all(len(group) == 4 for group in groups)


def route_contact(text: str, lines: list[str]) -> dict:
    emails = EMAIL.findall(text)
    masked = EMAIL.sub(" ", text)
    urls = URL.findall(masked)
    url_spans = [match.span() for match in URL.finditer(masked) if any(char.isalpha() for char in match.group())]
    identifiers = IDENTIFIER.findall(masked)
    identifier_spans = [match.span() for match in IDENTIFIER.finditer(masked)]
    phones = []
    for match in PHONE.finditer(masked):
        in_url = any(start <= match.start() and match.end() <= end for start, end in url_spans)
        overlaps_identifier = any(match.start() < end and start < match.end() for start, end in identifier_spans)
        if not in_url and not overlaps_identifier and not identifier_like(match.group()):
            phones.append(match.group().strip())
    return {"name_guess": lines[0] if lines else None, "emails": emails, "phones": phones, "identifiers": identifiers, "urls": urls}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.pdf.is_file():
        die(f"no such file: {args.pdf}")
    report = Report(layer="L1-parse-sim", file=str(args.pdf))
    try:
        lines = extract_lines(args.pdf)
    except Exception as exc:
        report.add("readable", FAIL, f"could not extract text: {exc}")
        return report.emit(args.json)
    sections: dict[str, list[str]] = {"_header": []}
    current = "_header"
    unknown = []
    for line in lines:
        key = heading_key(line)
        if key in HEADING:
            current = HEADING[key]
            sections.setdefault(current, [])
        else:
            if looks_like_heading(line) and sections[current]:
                unknown.append(line.strip())
            sections[current].append(line)
    found = [name for name, content in sections.items() if name != "_header" and any(line.strip() for line in content)]
    report.extra["sections"] = {name: sum(bool(line.strip()) for line in sections[name]) for name in found}
    report.extra["unknown_headings"] = unknown
    report.add("sections_found", PASS if found else FAIL, f"recognized: {', '.join(found)}" if found else "no conventional English section headings recognized")
    report.add("core_sections", PASS if {"experience", "projects"} & set(found) else FAIL, "experience or projects recognized" if {"experience", "projects"} & set(found) else "neither Experience nor Projects recognized")
    if "education" not in found:
        report.add("education_section", WARN, "no Education section recognized")
    report.add("unknown_headings", FAIL if unknown and not found else WARN if unknown else PASS, "; ".join(unknown[:6]) if unknown else "no unrecognized heading-shaped lines")
    header_lines = [line.strip() for line in sections["_header"] if line.strip()]
    contact = route_contact("\n".join(sections["_header"]), header_lines)
    report.extra["contact"] = contact
    report.add("contact_email", PASS if contact["emails"] else FAIL, contact["emails"][0] if contact["emails"] else "no email before first section")
    name = contact["name_guess"]
    plausible_name = bool(name and "@" not in name and not any(char.isdigit() for char in name) and 1 <= len(name.split()) <= 5)
    report.add("name_line", PASS if plausible_name else FAIL, name if plausible_name else f"first line {name!r} is not a plausible name")
    if not contact["phones"]:
        report.add("contact_phone", WARN, "no phone number detected")
    dates = {section: len(DATE_RANGE.findall("\n".join(sections[section]))) for section in ("experience", "education", "projects") if section in sections}
    report.metrics["date_ranges"] = dates
    if "experience" in found and dates.get("experience", 0) == 0:
        report.add("experience_dates", FAIL, "Experience has no conventional date range")
    elif dates:
        report.add("dates_parse", PASS, f"parsed ranges: {dates}")
    return report.emit(args.json)


if __name__ == "__main__":
    raise SystemExit(main())
