#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
"""Validate resume.yaml against the data-schema contract before Typst sees it.

Two failure classes, one honest split. Required-key typos (basics.name,
experience[].bullets, ...) already hard-fail the compile — but cryptically,
as a Typst stack trace; the value here is a clear yaml-path message. The
class NOTHING downstream catches is silent content loss: an optional-key
typo (`honours:`), a top-level section typo (`project:` drops the whole
section — verified), or a mis-nested key renders a clean PDF that passes
render.sh's smoke check and the PDF-only evaluator without a whisper.

The key inventory is read off all three templates (onecol.typ, compact.typ,
classic.typ) and render.sh — not just the schema doc's example block — so
this validator is never stricter than what actually renders: meta.accent
(compact-only), meta.template and meta.bullet_lines (render.sh-only),
experience[].tags (compact-only) and projects[].summary are all known keys.

usage: validate_yaml.py resume.yaml [--json]
  exit 0: valid · 1: violations · 2: file unreadable or unparseable
"""

from __future__ import annotations

import argparse
import datetime
import difflib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

PASS = "pass"
WARN = "warn"
FAIL = "fail"

# ── key inventory ────────────────────────────────────────────────────
# Sources: the field reads in onecol.typ / compact.typ / classic.typ and
# the awk scrapes in render.sh. Every key below renders (or steers the
# render) somewhere; every key absent is silently ignored by every
# consumer — which is exactly the loss class this script exists to catch.

TOP_KEYS = {"meta", "basics", "summary", "education", "experience",
            "projects", "skills", "publications", "awards"}
META_KEYS = {
    "target_field",   # builder/evaluator routing; never changes rendering
    "page_budget",    # render.sh page-count warning
    "paper",          # all templates: set page(paper: ...)
    "lang",           # all templates: set text(lang: ...)
    "accent",         # compact only; onecol/classic ignore it by design
    "template",       # render.sh precedence: -t flag > meta.template > onecol
    "bullet_lines",   # render.sh: opt-in check_bullets.py gate
}
BASICS_KEYS = {"name", "email", "phone", "location", "links"}
LINK_KEYS = {"label", "url"}
EDU_KEYS = {"institution", "degree", "field", "start", "end",
            "gpa", "location", "coursework", "honors"}
EXP_KEYS = {"organization", "title", "location", "start", "end",
            "group",    # research | teaching | industry section buckets
            "tags",     # compact's muted tag row; onecol/classic omit
            "bullets"}
PROJ_KEYS = {"name", "summary", "url", "stack", "start", "end", "bullets"}
SKILL_KEYS = {"label", "items"}
PUB_KEYS = {"citation", "url"}
AWARD_KEYS = {"name", "date"}

CONTENT_SECTIONS = ("education", "experience", "projects",
                    "skills", "publications", "awards")
GROUPS = {"research", "teaching", "industry"}
TARGET_FIELDS = {"ai-ml", "swe", "academic", "generic"}
PAPERS = {"us-letter", "a4"}
DATE_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
YEAR_RE = re.compile(r"^\d{4}$")
HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
TRACKING_RE = re.compile(r"(?i)^(?:utm_|fbclid$|gclid$|mc_cid$)")

SILENT = "silently ignored at render — the content never appears"
CRASH = ("the Typst compile fails without it "
         "(fix it here, not from the stack trace)")

TYPE_NAMES = {"NoneType": "null", "str": "string", "int": "integer",
              "float": "number", "bool": "boolean", "list": "list",
              "dict": "mapping"}


def tn(v) -> str:
    return TYPE_NAMES.get(type(v).__name__, type(v).__name__)


def suggest(key, valid) -> str:
    m = difflib.get_close_matches(str(key), sorted(valid), n=1, cutoff=0.6)
    return f" (did you mean {m[0]!r}?)" if m else ""


def tracking_params(url: str) -> list[str]:
    """Query keys that are tracking junk: utm_*, fbclid, gclid, mc_cid."""
    try:
        query = urlsplit(url).query
    except ValueError:
        return []
    return [k for k, _ in parse_qsl(query, keep_blank_values=True)
            if TRACKING_RE.match(k)]


def available_templates() -> set[str]:
    """What render.sh would actually accept: assets/templates/*.typ."""
    tdir = Path(__file__).resolve().parent.parent / "assets" / "templates"
    found = {p.stem for p in tdir.glob("*.typ")} if tdir.is_dir() else set()
    return found or {"onecol", "compact", "classic"}


# ── result plumbing (mirrors resume-evaluator's _report contract; kept
#    inline because this script ships standalone with resume-builder) ──

@dataclass
class Check:
    check_id: str
    level: str
    detail: str


@dataclass
class Report:
    layer: str
    file: str
    checks: list[Check] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)

    def add(self, check_id: str, level: str, detail: str) -> None:
        self.checks.append(Check(check_id, level, detail))

    @property
    def failed(self) -> bool:
        return any(c.level == FAIL for c in self.checks)

    def emit(self, as_json: bool) -> int:
        if as_json:
            print(json.dumps({
                "layer": self.layer,
                "file": self.file,
                "verdict": FAIL if self.failed else PASS,
                "checks": [vars(c) for c in self.checks],
                "metrics": self.metrics,
            }, indent=2, ensure_ascii=False))
        else:
            icon = {PASS: "ok", WARN: "!!", FAIL: "XX"}
            print(f"[{self.layer}] {self.file}")
            for c in self.checks:
                print(f"  {icon[c.level]}  {c.check_id}: {c.detail}")
            for k, v in self.metrics.items():
                print(f"      {k} = {v}")
            print(f"  => {'FAIL' if self.failed else 'PASS'}")
        return 1 if self.failed else 0


def die(msg: str):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(2)


# ── the validator ────────────────────────────────────────────────────

class Validator:
    def __init__(self) -> None:
        self.violations: list[Check] = []
        self.keys = 0      # recognized keys seen
        self.dates = 0     # date values checked

    def flag(self, check_id: str, level: str, detail: str) -> None:
        self.violations.append(Check(check_id, level, detail))

    def known(self, mapping: dict, valid: set, path: str, hint: str) -> None:
        for k in mapping:
            if k in valid:
                self.keys += 1
            else:
                self.flag("known_keys", FAIL,
                          f"{path}.{k}: unknown key — {hint}{suggest(k, valid)}")

    def nulls(self, mapping: dict, path: str) -> None:
        for k, val in mapping.items():
            if val is None:
                self.flag("empties", FAIL,
                          f"{path}.{k}: null — omit the key instead "
                          "(absence is the signal)")

    def require(self, mapping: dict, path: str, keys, why: str = CRASH) -> None:
        for k in keys:
            if k not in mapping:
                self.flag("required_keys", FAIL,
                          f"{path}.{k}: required key missing — {why}")

    def str_of(self, e: dict, path: str, *keys, level: str = FAIL) -> None:
        for k in keys:
            if (val := e.get(k)) is not None and not isinstance(val, str):
                self.flag("shapes", level,
                          f"{path}.{k}: expected a string, got {tn(val)}")

    def url_of(self, e: dict, path: str, k: str = "url") -> None:
        if isinstance(u := e.get(k), str) and (junk := tracking_params(u)):
            self.flag("urls", FAIL,
                      f"{path}.{k}: tracking parameter(s) "
                      f"{', '.join(junk)} — strip the query; templates "
                      "print the url verbatim as visible text")

    def str_list(self, e: dict, path: str, k: str) -> None:
        if k not in e or e[k] is None:      # nulls() covers the None case
            return
        val = e[k]
        if not isinstance(val, list):
            self.flag("shapes", FAIL,
                      f"{path}.{k}: expected a list, got {tn(val)}")
            return
        if not val:
            self.flag("empties", FAIL,
                      f"{path}.{k}: empty list — omit the key instead "
                      "(absence is the signal)")
            return
        for j, item in enumerate(val):
            if not isinstance(item, str) or not item.strip():
                self.flag("shapes", FAIL,
                          f"{path}.{k}[{j}]: entries must be non-empty "
                          f"strings, got {tn(item)}")

    def date_of(self, e: dict, path: str, *keys) -> None:
        for k in keys:
            if k not in e or e[k] is None:
                continue
            val = e[k]
            self.dates += 1
            if isinstance(val, str):
                s = val.strip()
                if DATE_RE.match(s) or s.lower() == "present":
                    continue
                if YEAR_RE.match(s):
                    self.flag("dates", WARN,
                              f"{path}.{k}: {val!r} is year-only — templates "
                              "render it as-is, but the schema wants YYYY-MM")
                    continue
            elif isinstance(val, int) and not isinstance(val, bool):
                self.flag("dates", WARN,
                          f"{path}.{k}: bare year {val} — quote it as a "
                          "YYYY-MM string")
                continue
            elif isinstance(val, (datetime.date, datetime.datetime)):
                self.flag("dates", FAIL,
                          f"{path}.{k}: full date {val} — the schema wants "
                          "month precision: YYYY-MM")
                continue
            self.flag("dates", FAIL,
                      f"{path}.{k}: {val!r} is not YYYY-MM (month 01-12) "
                      "or 'present' — templates cannot format it")

    def entries(self, data: dict, key: str):
        """Validate a section's list shell; yield (path, entry) mappings."""
        val = data[key]
        if val is None:
            self.flag("empties", FAIL,
                      f"{key}: null — omit the key instead "
                      "(absence is the signal)")
            return
        if not isinstance(val, list):
            self.flag("shapes", FAIL,
                      f"{key}: expected a list of entries, got {tn(val)}")
            return
        if not val:
            self.flag("empties", FAIL,
                      f"{key}: empty list — omit the key instead "
                      "(absence is the signal)")
            return
        for i, e in enumerate(val):
            path = f"{key}[{i}]"
            if not isinstance(e, dict):
                self.flag("shapes", FAIL,
                          f"{path}: expected a mapping, got {tn(e)}")
                continue
            yield path, e


def validate(data: dict) -> Validator:
    v = Validator()

    # ── top level ────────────────────────────────────────────────────
    for k in data:
        if k in TOP_KEYS:
            v.keys += 1
        else:
            v.flag("known_keys", FAIL,
                   f"{k}: unknown top-level key — every template silently "
                   f"ignores it, so the whole section never "
                   f"renders{suggest(k, TOP_KEYS)}")

    # ── meta ─────────────────────────────────────────────────────────
    if "meta" in data:
        m = data["meta"]
        if m is None:
            v.flag("empties", FAIL, "meta: null — omit the key instead")
        elif not isinstance(m, dict):
            v.flag("shapes", FAIL, f"meta: expected a mapping, got {tn(m)}")
        else:
            v.known(m, META_KEYS, "meta",
                    "no template and no render.sh scrape reads it, so the "
                    "knob silently does nothing")
            v.nulls(m, "meta")
            for k in ("page_budget", "bullet_lines"):
                if (val := m.get(k)) is not None and (
                        isinstance(val, bool)
                        or not isinstance(val, int) or val < 1):
                    v.flag("values", FAIL,
                           f"meta.{k}: {val!r} — expected a positive integer")
            if (val := m.get("paper")) is not None and val not in PAPERS:
                v.flag("values", FAIL,
                       f"meta.paper: {val!r} — must be us-letter | a4; "
                       "templates feed it straight to set page(paper:), "
                       "so the render crashes on anything else")
            if (val := m.get("target_field")) is not None \
                    and val not in TARGET_FIELDS:
                v.flag("values", WARN,
                       f"meta.target_field: {val!r} — schema knows "
                       "ai-ml | swe | academic | generic")
            if (val := m.get("lang")) is not None and not isinstance(val, str):
                v.flag("shapes", FAIL,
                       f"meta.lang: expected a string, got {tn(val)}")
            if (val := m.get("accent")) is not None and (
                    not isinstance(val, str) or not HEX_RE.match(val)):
                v.flag("values", FAIL,
                       f"meta.accent: {val!r} — not a hex color like "
                       "'#1f3a5f' (compact's rgb() rejects it)")
            if (val := m.get("template")) is not None:
                avail = available_templates()
                if val not in avail:
                    v.flag("values", FAIL,
                           f"meta.template: {val!r} — no such template "
                           f"({' | '.join(sorted(avail))}); render.sh "
                           "refuses it")

    # ── basics ───────────────────────────────────────────────────────
    b = data.get("basics")
    if "basics" not in data:
        v.flag("required_keys", FAIL,
               "basics: required section missing — nothing renders without it")
    elif b is None:
        v.flag("empties", FAIL,
               "basics: null — the section must carry name and email")
    elif not isinstance(b, dict):
        v.flag("shapes", FAIL, f"basics: expected a mapping, got {tn(b)}")
    else:
        v.known(b, BASICS_KEYS, "basics",
                "templates read basics field-by-field; an unknown key "
                "never renders")
        v.nulls(b, "basics")
        v.require(b, "basics", ("name", "email"))
        v.str_of(b, "basics", "name", "email")
        if isinstance(val := b.get("name"), str) and not val.strip():
            v.flag("empties", FAIL,
                   "basics.name: blank — an empty name fails the compile "
                   "(PDF/UA-1 rejects an empty heading); whitespace-only "
                   "renders a blank one")
        if isinstance(val := b.get("email"), str) and not val.strip():
            v.flag("empties", FAIL,
                   "basics.email: blank — the contact line renders with "
                   "a dead mailto: link")
        v.str_of(b, "basics", "phone", "location", level=WARN)
        if isinstance(b.get("email"), str) and b["email"].strip() \
                and "@" not in b["email"]:
            v.flag("values", WARN,
                   f"basics.email: {b['email']!r} has no '@' — the mailto: "
                   "link will be broken")
        links = b.get("links")
        if "links" in b and links is not None:
            if not isinstance(links, list):
                v.flag("shapes", FAIL,
                       f"basics.links: expected a list, got {tn(links)}")
            elif not links:
                v.flag("empties", FAIL,
                       "basics.links: empty list — omit the key instead")
            else:
                for i, link in enumerate(links):
                    p = f"basics.links[{i}]"
                    if not isinstance(link, dict):
                        v.flag("shapes", FAIL,
                               f"{p}: expected a mapping with label + url, "
                               f"got {tn(link)}")
                        continue
                    v.known(link, LINK_KEYS, p,
                            "link entries carry label + url only")
                    v.nulls(link, p)
                    if "url" not in link:
                        v.flag("required_keys", FAIL,
                               f"{p}: required key 'url' missing — templates "
                               "print and hyperlink the url; the compile "
                               "fails without it")
                    elif not isinstance(link["url"], str) \
                            or not link["url"].strip():
                        v.flag("shapes", FAIL,
                               f"{p}.url: expected a non-empty string, "
                               f"got {link['url']!r}")
                    else:
                        v.url_of(link, p)
                    if "label" not in link:
                        v.flag("required_keys", WARN,
                               f"{p}: 'label' missing — no template renders "
                               "it, but the schema names every link for the "
                               "builder")

    # ── summary ──────────────────────────────────────────────────────
    if "summary" in data:
        s = data["summary"]
        if s is None:
            v.flag("empties", FAIL,
                   "summary: null — omit the key instead (absence is the "
                   "signal)")
        elif not isinstance(s, str):
            v.flag("shapes", FAIL, f"summary: expected a string, got {tn(s)}")
        elif not s.strip():
            v.flag("empties", FAIL, "summary: empty — omit the key instead")

    # ── education ────────────────────────────────────────────────────
    if "education" in data:
        for p, e in v.entries(data, "education"):
            v.known(e, EDU_KEYS, p, SILENT)
            v.nulls(e, p)
            v.require(e, p, ("institution", "degree", "field"))
            v.str_of(e, p, "institution", "degree", "field", "location")
            v.date_of(e, p, "start", "end")
            v.str_list(e, p, "coursework")
            v.str_list(e, p, "honors")

    # ── experience ───────────────────────────────────────────────────
    if "experience" in data:
        for p, e in v.entries(data, "experience"):
            v.known(e, EXP_KEYS, p, SILENT)
            v.nulls(e, p)
            v.require(e, p, ("organization", "title", "bullets"))
            v.str_of(e, p, "organization", "title", "location")
            v.date_of(e, p, "start", "end")
            v.str_list(e, p, "bullets")
            v.str_list(e, p, "tags")
            if (g := e.get("group")) is not None and g not in GROUPS:
                v.flag("values", FAIL,
                       f"{p}.group: {g!r} — must be research | teaching | "
                       "industry; a grouped render SILENTLY DROPS entries "
                       "with any other value")

    # ── projects ─────────────────────────────────────────────────────
    if "projects" in data:
        for p, e in v.entries(data, "projects"):
            v.known(e, PROJ_KEYS, p, SILENT)
            v.nulls(e, p)
            v.require(e, p, ("name", "bullets"))
            v.str_of(e, p, "name", "summary", "url")
            v.url_of(e, p)
            v.date_of(e, p, "start", "end")
            v.str_list(e, p, "bullets")
            v.str_list(e, p, "stack")

    # ── skills ───────────────────────────────────────────────────────
    if "skills" in data:
        for p, e in v.entries(data, "skills"):
            v.known(e, SKILL_KEYS, p, SILENT)
            v.nulls(e, p)
            v.require(e, p, ("label", "items"))
            v.str_of(e, p, "label")
            v.str_list(e, p, "items")

    # ── publications ─────────────────────────────────────────────────
    if "publications" in data:
        for p, e in v.entries(data, "publications"):
            v.known(e, PUB_KEYS, p, SILENT)
            v.nulls(e, p)
            v.require(e, p, ("citation",))
            v.str_of(e, p, "citation", "url")
            v.url_of(e, p)

    # ── awards ───────────────────────────────────────────────────────
    if "awards" in data:
        for p, e in v.entries(data, "awards"):
            v.known(e, AWARD_KEYS, p, SILENT)
            v.nulls(e, p)
            v.require(e, p, ("name",))
            v.str_of(e, p, "name")
            v.date_of(e, p, "date")

    if not any(k in data for k in CONTENT_SECTIONS):
        v.flag("content", WARN,
               "no content sections — only the header would render "
               "(render.sh's smoke check will fail it)")

    return v


# Fixed report order; a category with no violations gets one PASS line,
# matching the evaluator scripts' one-line-per-check style.
CATEGORIES = (
    ("known_keys",
     "all {keys} keys recognized (inventory read from onecol/compact/"
     "classic + render.sh)"),
    ("required_keys", "every required key present"),
    ("dates", "{dates} date(s) well-formed (YYYY-MM / present)"),
    ("shapes", "field shapes match the schema"),
    ("empties", "no nulls, no empty lists — absence is the signal"),
    ("values", "enums and meta knobs in range"),
    ("urls", "link urls free of tracking parameters"),
)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("yaml_file", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if not args.yaml_file.is_file():
        die(f"no such file: {args.yaml_file}")

    import yaml

    try:
        raw = args.yaml_file.read_text(encoding="utf-8")
    except OSError as exc:
        die(f"cannot read {args.yaml_file}: {exc}")
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        die(f"YAML parse error in {args.yaml_file}: {exc}")
    if data is None:
        die(f"{args.yaml_file}: empty file")
    if not isinstance(data, dict):
        die(f"{args.yaml_file}: top level must be a mapping "
            f"(basics:, education:, ...), got {tn(data)}")

    v = validate(data)
    report = Report(layer="schema", file=str(args.yaml_file))
    for cid, pass_detail in CATEGORIES:
        hits = [c for c in v.violations if c.check_id == cid]
        if hits:
            report.checks.extend(hits)
        else:
            report.add(cid, PASS,
                       pass_detail.format(keys=v.keys, dates=v.dates))
    report.checks.extend(c for c in v.violations if c.check_id == "content")
    report.metrics = {
        "recognized_keys": v.keys,
        "dates_checked": v.dates,
        "violations": sum(c.level == FAIL for c in v.violations),
        "warnings": sum(c.level == WARN for c in v.violations),
    }
    return report.emit(args.json)


if __name__ == "__main__":
    sys.exit(main())
