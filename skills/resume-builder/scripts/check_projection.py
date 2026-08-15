#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""Report exact resume values absent from a career vault and list claims for review.

The program checks normalized record values, numbers, URLs, and listed skills. It
does not decide whether prose means the same thing as vault material.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

import yaml

PASS, FAIL = "pass", "fail"
DATE = re.compile(r"^(\d{4})-(\d{2})$")
NUMBER = re.compile(r"(?<![\w.])[~+]?\d[\d,]*(?:\.\d+)?(?:%|[kKmMbB])?(?![\w.])")
URL = re.compile(r"(?:https?://|doi:)[^\s)>\]}]+", re.I)
MONTHS = {"01": "jan", "02": "feb", "03": "mar", "04": "apr", "05": "may", "06": "jun", "07": "jul", "08": "aug", "09": "sep", "10": "oct", "11": "nov", "12": "dec"}
NON_ACTIVE = re.compile(r"\b(?:NOT-CLAIMABLE|PENDING-EVIDENCE|ARCHIVED|OMIT-FOR|SUPERSEDED|CUT):")


class CannotRun(Exception):
    pass


def sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise CannotRun(f"cannot read {path}: {exc}") from exc


def text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise CannotRun(f"cannot read {path}: {exc}") from exc


def normalize(value: Any) -> str:
    value = unicodedata.normalize("NFKC", str(value)).casefold().replace("–", "-").replace("—", "-")
    return " ".join(re.sub(r"[^a-z0-9+#.%/@_-]+", " ", value).split())


def active_vault(vault_text: str) -> tuple[str, list[dict[str, Any]]]:
    active, risk_notes = [], []
    in_archive = False
    for number, line in enumerate(vault_text.splitlines(), 1):
        heading = re.match(r"^\s*##\s+(.+?)\s*$", line)
        if heading:
            in_archive = heading.group(1).strip().casefold() == "archive"
        marked = NON_ACTIVE.search(line)
        if marked:
            risk_notes.append({"line": number, "text": line.strip()})
        if not in_archive and not marked:
            active.append(line)
    return "\n".join(active), risk_notes


def variants(value: str) -> set[str]:
    value = value.strip()
    match = DATE.fullmatch(value)
    if not match:
        return {normalize(value)}
    year, month = match.groups()
    return {normalize(value), f"{MONTHS[month]} {year}"}


def claims(value: Any, path: str = "") -> list[dict[str, str]]:
    if isinstance(value, dict):
        rows = []
        for key, child in value.items():
            if not path and key == "meta":
                continue
            rows.extend(claims(child, f"{path}.{key}" if path else key))
        return rows
    if isinstance(value, list):
        rows = []
        for index, child in enumerate(value):
            rows.extend(claims(child, f"{path}[{index}]"))
        return rows
    return [] if value is None or isinstance(value, bool) else [{"path": path, "claim": str(value)}]


def record_values(data: dict) -> list[dict[str, str]]:
    fields = {
        "basics": ("name", "email", "phone", "location"),
        "education": ("institution", "degree", "field", "start", "end", "gpa"),
        "experience": ("organization", "title", "location", "start", "end"),
        "projects": ("name", "url", "start", "end"),
        "publications": ("citation", "url"),
        "awards": ("name", "date"),
    }
    rows = []
    for section, names in fields.items():
        value = data.get(section)
        entries = value if isinstance(value, list) else [value]
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            prefix = f"{section}[{index}]" if isinstance(value, list) else section
            for name in names:
                if name in entry and not isinstance(entry[name], (dict, list)):
                    rows.append({"path": f"{prefix}.{name}", "value": str(entry[name])})
    basics = data.get("basics", {})
    if isinstance(basics, dict):
        for index, link in enumerate(basics.get("links", [])):
            if isinstance(link, dict) and "url" in link:
                rows.append({"path": f"basics.links[{index}].url", "value": str(link["url"])})
    return rows


def token_set(pattern: re.Pattern, rows: list[dict[str, str]], key: str) -> set[str]:
    return {match.group().casefold().replace(",", "").lstrip("~+").rstrip(".,;") for row in rows for match in pattern.finditer(row[key]) if not DATE.fullmatch(row[key].strip())}


def build(resume: Path, vault: Path) -> dict:
    try:
        data = yaml.safe_load(text(resume))
    except yaml.YAMLError as exc:
        raise CannotRun(f"cannot parse {resume}: {exc}") from exc
    if not isinstance(data, dict):
        raise CannotRun("resume must contain a YAML mapping")
    vault_text = text(vault)
    active_text, risk_notes = active_vault(vault_text)
    normalized_vault = normalize(active_text)
    claim_rows = claims(data)
    records = record_values(data)
    missing_records = [row for row in records if not any(value and value in normalized_vault for value in variants(row["value"]))]
    resume_numbers = token_set(NUMBER, claim_rows, "claim")
    vault_numbers = {match.group().casefold().replace(",", "").lstrip("~+") for match in NUMBER.finditer(active_text)}
    resume_urls = token_set(URL, claim_rows, "claim")
    vault_urls = {match.group().casefold().rstrip(".,;") for match in URL.finditer(active_text)}
    skills = []
    for group_index, group in enumerate(data.get("skills", [])):
        if isinstance(group, dict):
            for item_index, item in enumerate(group.get("items", [])):
                skills.append({"path": f"skills[{group_index}].items[{item_index}]", "value": str(item)})
    missing_skills = [row for row in skills if normalize(row["value"]) not in normalized_vault]
    missing_numbers = sorted(resume_numbers - vault_numbers)
    missing_urls = sorted(resume_urls - vault_urls)
    checks = [
        {"check_id": "record_values", "level": FAIL if missing_records else PASS, "detail": missing_records or f"{len(records)} normalized record value(s) found in the vault"},
        {"check_id": "numbers", "level": FAIL if missing_numbers else PASS, "detail": missing_numbers or f"{len(resume_numbers)} numeric token(s) found in the vault"},
        {"check_id": "urls", "level": FAIL if missing_urls else PASS, "detail": missing_urls or f"{len(resume_urls)} URL(s) found in the vault"},
        {"check_id": "skills", "level": FAIL if missing_skills else PASS, "detail": missing_skills or f"{len(skills)} listed skill(s) found in the vault"},
    ]
    failed = any(check["level"] == FAIL for check in checks)
    return {
        "layer": "projection", "file": str(resume), "vault": str(vault),
        "resume_sha256": sha256(resume), "vault_sha256": sha256(vault),
        "result": FAIL if failed else PASS, "checks": checks,
        "metrics": {"claims_listed": len(claim_rows), "risk_notes": len(risk_notes)},
        "claims": claim_rows, "risk_notes": risk_notes,
        "scope": "Exact normalized values only, from active vault material; an agent must review meaning, lifecycle notes, and practical exposure.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("resume", type=Path)
    parser.add_argument("vault", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = build(args.resume, args.vault)
    except CannotRun as exc:
        if args.json:
            print(json.dumps({"layer": "projection", "result": "could-not-run", "reason": str(exc)}, indent=2))
        else:
            print(f"[projection] could not run: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"[projection] {args.resume.name} ⇄ {args.vault.name}")
        icons = {PASS: "ok", FAIL: "XX"}
        for check in report["checks"]:
            detail = check["detail"] if isinstance(check["detail"], str) else json.dumps(check["detail"], ensure_ascii=False)
            print(f"  {icons[check['level']]}  {check['check_id']}: {detail}")
        print(f"  review inventory: {report['metrics']['claims_listed']} claims and {report['metrics']['risk_notes']} risk note(s); use --json for the inventory")
        print(f"  => {report['result'].upper()}")
    return 1 if report["result"] == FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
