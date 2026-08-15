#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""Validate resume.yaml before Typst renders it."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import parse_qsl, urlsplit

import yaml

PASS, WARN, FAIL = "pass", "warn", "fail"
TOP = {"meta", "basics", "summary", "education", "experience", "projects", "skills", "publications", "awards"}
KEYS = {
    "meta": {"target_field", "target_level", "page_budget", "paper", "lang", "accent", "template", "vault", "thesis"},
    "basics": {"name", "email", "phone", "location", "links"},
    "link": {"label", "url"},
    "education": {"institution", "degree", "field", "location", "start", "end", "gpa", "coursework", "honors"},
    "experience": {"organization", "title", "location", "start", "end", "group", "tags", "bullets"},
    "projects": {"name", "summary", "url", "start", "end", "stack", "bullets"},
    "skills": {"label", "items"},
    "publications": {"citation", "url"},
    "awards": {"name", "date"},
}
REQUIRED = {
    "basics": {"name", "email"}, "education": {"institution", "degree", "field"},
    "experience": {"organization", "title", "bullets"}, "projects": {"name", "bullets"},
    "skills": {"label", "items"}, "publications": {"citation"}, "awards": {"name"}, "link": {"url"},
}
LIST_FIELDS = {"coursework", "honors", "tags", "bullets", "stack", "items"}
SECTIONS = ("education", "experience", "projects", "skills", "publications", "awards")
TARGET_FIELDS = {"ai-ml", "swe", "academic", "generic"}
TARGET_LEVELS = {"intern", "new-grad", "junior", "mid", "senior", "staff", "principal", "lead", "manager", "grad-applicant", "phd-applicant", "postdoc"}
TEMPLATES = {"onecol", "compact", "classic"}
GROUPS = {"research", "teaching", "industry"}
PAPERS = {"us-letter", "a4"}
DATE_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
YEAR_RE = re.compile(r"^\d{4}$")
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
TRACKING = {"fbclid", "gclid", "mc_cid"}


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader: UniqueLoader, node: yaml.MappingNode, deep: bool = False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise yaml.constructor.ConstructorError("mapping", node.start_mark, f"duplicate key {key!r}", key_node.start_mark)
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


@dataclass
class Check:
    check_id: str
    level: str
    detail: str


class Validator:
    def __init__(self, file: Path, template: str):
        self.file = file
        self.template = template
        self.checks: list[Check] = []

    def add(self, check_id: str, detail: str, level: str = FAIL) -> None:
        self.checks.append(Check(check_id, level, detail))

    def mapping(self, value, path: str, kind: str):
        if not isinstance(value, dict):
            self.add("shape", f"{path}: expected a mapping")
            return None
        unknown = sorted(set(value) - KEYS[kind])
        if unknown:
            self.add("keys", f"{path}: unknown key(s): {', '.join(unknown)}")
        missing = sorted(REQUIRED.get(kind, set()) - set(value))
        if missing:
            self.add("required", f"{path}: missing required key(s): {', '.join(missing)}")
        for key, item in value.items():
            if item is None or isinstance(item, str) and not item.strip() or isinstance(item, list) and not item:
                self.add("empty", f"{path}.{key}: omit empty values")
        return value

    def entries(self, data: dict, section: str):
        if section not in data:
            return []
        rows = data[section]
        if not isinstance(rows, list) or not rows:
            self.add("shape", f"{section}: expected a non-empty list")
            return []
        valid = []
        for index, row in enumerate(rows):
            path = f"{section}[{index}]"
            if self.mapping(row, path, section) is not None:
                valid.append((path, row))
        return valid

    def strings(self, row: dict, path: str, names) -> None:
        for name in names:
            if name in row and not isinstance(row[name], str):
                self.add("shape", f"{path}.{name}: expected a string")

    def string_list(self, row: dict, path: str, name: str) -> None:
        if name not in row:
            return
        value = row[name]
        if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item.strip() for item in value):
            hint = "; quote an item containing ': '" if isinstance(value, list) and any(isinstance(item, dict) for item in value) else ""
            self.add("shape", f"{path}.{name}: expected non-empty strings{hint}")

    def date(self, row: dict, path: str, name: str, *, present: bool = False, year: bool = False) -> None:
        if name not in row:
            return
        value = row[name]
        if not isinstance(value, str):
            self.add("date", f"{path}.{name}: quote dates as YYYY-MM" + (" or YYYY" if year else ""))
            return
        valid = DATE_RE.fullmatch(value) or year and YEAR_RE.fullmatch(value) or present and value.casefold() == "present"
        if not valid:
            self.add("date", f"{path}.{name}: expected YYYY-MM" + (", quoted YYYY" if year else "") + (", or present" if present else ""))

    def chronology(self, row: dict, path: str) -> None:
        start, end = row.get("start"), row.get("end")
        if isinstance(start, str) and isinstance(end, str) and DATE_RE.fullmatch(start) and DATE_RE.fullmatch(end) and start > end:
            self.add("date", f"{path}: start {start} is after end {end}")

    def url(self, value, path: str) -> None:
        if not isinstance(value, str):
            self.add("url", f"{path}: expected a URL string")
            return
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            self.add("url", f"{path}: expected an http(s) URL with a host")
        junk = [key for key, _ in parse_qsl(parsed.query) if key.casefold().startswith("utm_") or key.casefold() in TRACKING]
        if junk:
            self.add("url", f"{path}: remove tracking parameter(s): {', '.join(junk)}")

    def run(self, data: dict) -> None:
        unknown = sorted(set(data) - TOP)
        if unknown:
            self.add("keys", f"top level: unknown section(s): {', '.join(unknown)}")
        meta = data.get("meta", {})
        if self.mapping(meta, "meta", "meta") is not None:
            for key in ("target_field", "target_level", "paper", "template"):
                if key in meta and not isinstance(meta[key], str):
                    self.add("shape", f"meta.{key}: expected a string")
            for key in ("page_budget",):
                if key in meta and (isinstance(meta[key], bool) or not isinstance(meta[key], int) or meta[key] < 1):
                    self.add("value", f"meta.{key}: expected a positive integer")
            for key, allowed in (("target_field", TARGET_FIELDS), ("target_level", TARGET_LEVELS), ("paper", PAPERS), ("template", TEMPLATES)):
                if isinstance(meta.get(key), str) and meta[key] not in allowed:
                    self.add("value", f"meta.{key}: unsupported value {meta[key]!r}")
            if "accent" in meta and (not isinstance(meta["accent"], str) or not HEX_RE.fullmatch(meta["accent"])):
                self.add("value", "meta.accent: expected a six-digit hex color")
            if "vault" in meta:
                vault = meta["vault"]
                if not isinstance(vault, str) or PurePosixPath(vault).is_absolute() or vault.startswith("~") or any(ch.isspace() for ch in vault):
                    self.add("value", "meta.vault: expected a whitespace-free relative path")
        basics = data.get("basics")
        if basics is None:
            self.add("required", "basics: required section missing")
        elif self.mapping(basics, "basics", "basics") is not None:
            self.strings(basics, "basics", ("name", "email", "phone", "location"))
            if isinstance(basics.get("email"), str) and not EMAIL_RE.fullmatch(basics["email"]):
                self.add("value", "basics.email: expected a deliverable-looking address")
            links = basics.get("links", [])
            if "links" in basics and (not isinstance(links, list) or not links):
                self.add("shape", "basics.links: expected a non-empty list")
            elif isinstance(links, list):
                for index, link in enumerate(links):
                    path = f"basics.links[{index}]"
                    if self.mapping(link, path, "link") is not None:
                        self.strings(link, path, ("label", "url"))
                        if "url" in link:
                            self.url(link["url"], f"{path}.url")
        if "summary" in data and (not isinstance(data["summary"], str) or not data["summary"].strip()):
            self.add("shape", "summary: expected a non-empty string")
        for path, row in self.entries(data, "education"):
            self.strings(row, path, ("institution", "degree", "field", "location", "gpa"))
            if "gpa" in row and not isinstance(row["gpa"], str):
                self.add("shape", f"{path}.gpa: quote GPA to preserve formatting")
            for name in ("coursework", "honors"):
                self.string_list(row, path, name)
            self.date(row, path, "start")
            self.date(row, path, "end", present=True)
            self.chronology(row, path)
        grouped = []
        flat = []
        for path, row in self.entries(data, "experience"):
            self.strings(row, path, ("organization", "title", "location", "start", "end", "group"))
            for name in ("tags", "bullets"):
                self.string_list(row, path, name)
            self.date(row, path, "start")
            self.date(row, path, "end", present=True)
            self.chronology(row, path)
            (grouped if "group" in row else flat).append(path)
            if isinstance(row.get("group"), str) and row["group"] not in GROUPS:
                self.add("value", f"{path}.group: expected research, teaching, or industry")
        if grouped and flat:
            self.add("value", "experience.group: group every entry or none of them")
        for path, row in self.entries(data, "projects"):
            self.strings(row, path, ("name", "summary", "url", "start", "end"))
            for name in ("stack", "bullets"):
                self.string_list(row, path, name)
            if "url" in row:
                self.url(row["url"], f"{path}.url")
            self.date(row, path, "start")
            self.date(row, path, "end", present=True)
            self.chronology(row, path)
        for path, row in self.entries(data, "skills"):
            self.strings(row, path, ("label",))
            self.string_list(row, path, "items")
        for path, row in self.entries(data, "publications"):
            self.strings(row, path, ("citation", "url"))
            if "url" in row:
                self.url(row["url"], f"{path}.url")
        for path, row in self.entries(data, "awards"):
            self.strings(row, path, ("name", "date"))
            self.date(row, path, "date", year=True)
        if not any(section in data for section in SECTIONS):
            self.add("content", "no resume content section is present", WARN)

    def report(self) -> dict:
        failed = any(check.level == FAIL for check in self.checks)
        return {"layer": "schema", "file": str(self.file), "template": self.template, "result": FAIL if failed else PASS, "checks": [asdict(check) for check in self.checks] or [asdict(Check("schema", PASS, "valid resume projection"))]}


def die(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("yaml_file", type=Path)
    parser.add_argument("-t", "--template")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        data = yaml.load(args.yaml_file.read_text(encoding="utf-8"), Loader=UniqueLoader)
    except OSError as exc:
        return die(f"cannot read {args.yaml_file}: {exc}")
    except yaml.YAMLError as exc:
        return die(f"YAML parse error in {args.yaml_file}: {exc}")
    if not isinstance(data, dict):
        return die("top level must be a mapping")
    meta = data.get("meta", {})
    template = args.template or (meta.get("template", "onecol") if isinstance(meta, dict) else "onecol")
    validator = Validator(args.yaml_file, template)
    validator.run(data)
    report = validator.report()
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"[schema] {args.yaml_file}")
        icons = {PASS: "ok", WARN: "!!", FAIL: "XX"}
        for check in report["checks"]:
            print(f"  {icons[check['level']]}  {check['check_id']}: {check['detail']}")
        print(f"  => {report['result'].upper()}")
    return 1 if report["result"] == FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
