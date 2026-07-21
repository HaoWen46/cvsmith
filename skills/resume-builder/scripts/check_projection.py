#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml>=6",
# ]
# ///
"""Check projection hard-fact tokens for vault presence, mechanically.

Projections never contain a fact the vault lacks (career-vault.md,
Protocol). This script enforces the token-level shadow of that
invariant: every numeric token, date, and URL in the projection
appears somewhere in the vault. Presence, not meaning — tokens are
not bound to the claims they sit in. One slice of meaning IS bound:
ordered pairs carrying an explicit direction marker ("480 ms ->
210 ms", "from 480 ms to 210 ms") are compared against vault lines
holding both numbers. Same-order vault marker = verified; vault
markers all reversed = FAIL; no vault marker = WARN for manual
review (a global ordered-pair heuristic was rejected: it false-fails
legitimate rephrasings — only the vault's own markers are trusted to
contradict). The unverifiable residue — pairs whose vault support
carries no direction marker, plus unpaired numbers — stays
bag-of-tokens, on the human review; an audit note counts it out
loud whenever directional pairs exist.
Org/title/name wording is legitimately reframed per
application, so drift there only WARNs — but a drifted value is
still swept for numeric tokens, which FAIL like content numbers.

Part of the builder's authoring loop (like check_bullets.py), not the
evaluator's battery — the cold read is vault-blind by design.

What is checked, and how leniently:
  numbers   numeric tokens in content strings (bullets, summary,
            honors, gpa, citation, stack, tags), matched literally
            after normalizing dashes, thousands separators, and
            ~/$/+/% decoration. Miss = FAIL.
  dates     start/end values (YYYY-MM), matched against YYYY-MM,
            "Mon YYYY", "Month YYYY", MM/YYYY, YYYY/MM. Only the
            year found = WARN; nothing found = FAIL.
  urls      url fields (and any URL pasted into a content string),
            compared after stripping scheme, leading www., and the
            trailing slash. Miss = FAIL.
  pairs     ordered numeric pairs in content strings with an explicit
            direction marker: X -> Y / X → Y / X ⇒ Y, or
            "from X ... to Y" inside one string (~40-char window, no
            sentence boundary). Vault line with both numbers and a
            same-order marker = verified; vault markers only in the
            reversed order = FAIL; both numbers co-occur but no
            marker = WARN (manual review). Pairs whose numbers
            already failed presence are not double-reported.
  identity  name / organization / institution / title / degree not
            found verbatim = WARN (formatting drift is legitimate);
            numeric tokens in a drifted value are checked like
            content numbers. Miss = FAIL.
meta.* is skipped entirely: page budgets and accent colors are
knobs, not facts.

A FAIL is never fixed by deleting the fact silently: confirm it with
the user, record it in the vault (with the answer), then keep it in
the yaml.

usage: check_projection.py resume.yaml career-vault.md [--json]
exit: 0 clean / 1 hard-fact miss / 2 unreadable input
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PASS, WARN, FAIL = "pass", "warn", "fail"

DATE_KEYS = {"start", "end", "date"}
URL_KEYS = {"url"}
CONTENT_KEYS = {"bullets", "summary", "honors", "gpa", "citation", "stack", "tags"}
IDENTITY_KEYS = {"name", "organization", "institution", "title", "degree"}
PRESENT_WORDS = {"present", "current", "ongoing", "now"}

MONTHS = {
    1: ("jan", "january"), 2: ("feb", "february"), 3: ("mar", "march"),
    4: ("apr", "april"), 5: ("may",), 6: ("jun", "june"),
    7: ("jul", "july"), 8: ("aug", "august"), 9: ("sep", "sept", "september"),
    10: ("oct", "october"), 11: ("nov", "november"), 12: ("dec", "december"),
}

DASHES = str.maketrans({c: "-" for c in "–—−‒‑"})
QUOTES = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'})


def normalize(text: str) -> str:
    """Casefold; unify dashes and quotes; drop thousands separators."""
    text = text.translate(DASHES).translate(QUOTES)
    text = re.sub(r"(?<=\d),(?=\d)", "", text)
    return text.casefold()


def normalize_url(url: str) -> str:
    url = normalize(url.strip()).rstrip(".,;)]")
    url = re.sub(r"^[a-z][a-z0-9+.-]*://", "", url)
    url = re.sub(r"^www\.", "", url)
    return url.rstrip("/")


def number_in(token: str, haystack: str) -> bool:
    """Literal match with digit boundaries: 25 must not ride on 250,
    nor 4.0 on 4.0.1 — but a period is a boundary unless a digit
    follows it, so sentence-final "…GPA is 4.0." still supports 4.0."""
    return re.search(
        rf"(?<!\d)(?<!\d\.){re.escape(token)}(?!\d)(?!\.\d)",
        haystack) is not None


NUM = r"\d+(?:\.\d+)?"
# X -> Y with only unit/space chars (no digits) between number and arrow
ARROW_PAIR = re.compile(
    rf"({NUM})[^\d]{{0,20}}?(?:->|→|⇒)[^\d]{{0,20}}?({NUM})")
# "from X ... to Y": numbers anchored to their keywords; the gap may
# hold units or digits (p95) but never a sentence boundary (. or ;)
FROM_TO_PAIR = re.compile(
    rf"\bfrom\b[^\d.;]{{0,12}}({NUM})[^.;]{{0,40}}?"
    rf"\bto\b[^\d.;]{{0,12}}({NUM})")


def directional_pairs(norm: str) -> list[tuple[str, str]]:
    """Ordered numeric pairs carrying an explicit direction marker,
    from one normalized string. Pairing never crosses string values."""
    pairs = []
    for rex in (ARROW_PAIR, FROM_TO_PAIR):
        pairs.extend(m.groups() for m in rex.finditer(norm))
    return pairs


def date_candidates(y: int, m: int) -> list[str]:
    cands = [f"{y}-{m:02d}"]
    for name in MONTHS[m]:
        cands += [f"{name} {y}", f"{name}. {y}"]
    cands += [f"{m:02d}/{y}", f"{m}/{y}", f"{y}/{m:02d}", f"{y}/{m}"]
    return cands


def iter_strings(node, path):
    """Scalar leaves under a content key, with their yaml paths."""
    if isinstance(node, (list, tuple)):
        for i, item in enumerate(node):
            yield from iter_strings(item, f"{path}[{i}]")
    elif node is not None and not isinstance(node, dict):
        yield path, str(node)


def collect(node, path, out):
    """One walk of the yaml tree, routing values by key. meta.* skipped."""
    if isinstance(node, dict):
        for key, value in node.items():
            if not path and key == "meta":
                continue
            p = f"{path}.{key}" if path else str(key)
            if key in DATE_KEYS:
                out["dates"].append((p, value))
            elif key in URL_KEYS:
                if value is not None:
                    out["urls"].append((p, str(value)))
            elif key in CONTENT_KEYS:
                out["content"].extend(iter_strings(value, p))
            elif key in IDENTITY_KEYS:
                if value is not None:
                    out["identity"].append((p, str(value)))
            else:
                collect(value, p, out)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            collect(item, f"{path}[{i}]", out)


def excerpt(text: str, around: str = "", width: int = 70) -> str:
    text = " ".join(text.split())
    pos = text.find(around) if around else -1
    if pos > width // 2:
        text = "…" + text[pos - width // 2:]
    return text[:width] + ("…" if len(text) > width else "")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Check a resume projection against the career vault.")
    ap.add_argument("resume", type=Path, help="resume yaml (the projection)")
    ap.add_argument("vault", type=Path, help="career-vault.md")
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args()

    def die(msg: str) -> int:
        print(f"error: {msg}", file=sys.stderr)
        return 2

    import yaml

    for f in (args.resume, args.vault):
        if not f.is_file():
            return die(f"no such file: {f}")
    try:
        data = yaml.safe_load(args.resume.read_text(encoding="utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError) as e:
        return die(f"unreadable yaml: {args.resume}: {e}")
    if not isinstance(data, dict):
        return die(f"yaml root is not a mapping: {args.resume}")
    try:
        vault_raw = args.vault.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        return die(f"unreadable vault: {args.vault}: {e}")

    haystack = " ".join(normalize(vault_raw).split())

    found = {"dates": [], "urls": [], "content": [], "identity": []}
    collect(data, "", found)

    checks: list[dict] = []

    def add(check_id: str, level: str, detail: str) -> None:
        checks.append({"check_id": check_id, "level": level, "detail": detail})

    # ── numbers: from content strings only ───────────────────────────
    n_tokens = 0
    n_clean = True
    for path, text in found["content"]:
        norm = normalize(text)
        for token in re.findall(r"\d+(?:\.\d+)?", norm):
            n_tokens += 1
            if not number_in(token, haystack):
                n_clean = False
                add("number_unsupported", FAIL,
                    f"'{token}' at {path} has no vault support — "
                    f"\"{excerpt(text, token)}\"")
    if n_clean:
        add("numbers", PASS, f"{n_tokens} numeric token(s) verified against the vault")

    # ── metric direction: resume markers vs the vault's own markers ──
    vault_lines = [normalize(line) for line in vault_raw.splitlines()]
    pairs = []
    for path, text in found["content"]:
        for x, y in directional_pairs(normalize(text)):
            if number_in(x, haystack) and number_in(y, haystack):
                pairs.append((path, text, x, y))  # presence misses FAILed above
    n_verified = n_manual = 0
    for path, text, x, y in pairs:
        vault_marked: set[tuple[str, str]] = set()
        for line in vault_lines:
            if number_in(x, line) and number_in(y, line):
                vault_marked.update(directional_pairs(line))
        if (x, y) in vault_marked:
            n_verified += 1
        elif (y, x) in vault_marked:
            add("metric_direction", FAIL,
                f"{path}: resume states {x} -> {y}; the vault's own marker "
                f"says {y} -> {x} — reversed improvement — "
                f"\"{excerpt(text, x)}\"")
        else:
            n_manual += 1
            add("metric_direction", WARN,
                f"{path}: pair {x} -> {y} listed for manual review — no "
                f"vault direction marker co-occurs with both numbers, so "
                f"direction cannot be machine-verified")
    notes = []
    if pairs:
        n_reversed = len(pairs) - n_verified - n_manual
        notes.append(
            f"metric pairs: {len(pairs)} directional pair(s) found — "
            f"{n_verified} verified against vault markers, "
            f"{n_manual} need manual review"
            + (f", {n_reversed} reversed" if n_reversed else ""))

    # ── dates ────────────────────────────────────────────────────────
    n_dates = 0
    d_clean = True
    for path, value in found["dates"]:
        if value is None:
            continue
        if hasattr(value, "year") and hasattr(value, "month"):  # yaml date
            y, m = value.year, value.month
        else:
            text = str(value).strip()
            if text.casefold() in PRESENT_WORDS:
                continue
            if re.fullmatch(r"\d{4}", text):
                n_dates += 1
                if not re.search(rf"(?<!\d){text}(?!\d)", haystack):
                    d_clean = False
                    add("date_unsupported", FAIL,
                        f"{path}: year {text} appears nowhere in the vault")
                continue
            match = re.fullmatch(r"(\d{4})-(\d{2})(?:-\d{2})?", text)
            if not match:
                continue  # format enforcement is the validator's job
            y, m = int(match.group(1)), int(match.group(2))
        if not 1 <= m <= 12:
            continue
        n_dates += 1
        if any(c in haystack for c in date_candidates(y, m)):
            continue
        if re.search(rf"(?<!\d){y}(?!\d)", haystack):
            d_clean = False
            add("date_year_only", WARN,
                f"{path}: {y}-{m:02d} — vault has only the year {y}; "
                f"confirm the month before keeping it")
        else:
            d_clean = False
            add("date_unsupported", FAIL,
                f"{path}: {y}-{m:02d} appears nowhere in the vault "
                f"(tried YYYY-MM, Mon YYYY, MM/YYYY forms)")
    if d_clean:
        add("dates", PASS, f"{n_dates} date(s) verified against the vault")

    # ── urls: url fields + URLs pasted into content strings ──────────
    url_items = list(found["urls"])
    for path, text in found["content"]:
        for tok in re.findall(r"(?:https?://|www\.)\S+", text):
            url_items.append((path, tok))
    u_clean = True
    for path, url in url_items:
        if normalize_url(url) not in haystack:
            u_clean = False
            add("url_unsupported", FAIL,
                f"{path}: {url} (normalized '{normalize_url(url)}') "
                f"has no vault support")
    if u_clean:
        add("urls", PASS, f"{len(url_items)} url(s) verified against the vault")

    # ── identity: drift WARNs, but drifted numbers FAIL ──────────────
    i_clean = True
    for path, value in found["identity"]:
        needle = " ".join(normalize(value).split())
        if not needle or needle in haystack:
            continue  # verbatim in the vault: supported by definition
        i_clean = False
        add("identity_drift", WARN,
            f"{path}: '{value}' not found verbatim in the vault — "
            f"fine if it's a rename/reformat, worth a look if not")
        for token in re.findall(r"\d+(?:\.\d+)?", needle):
            if not number_in(token, haystack):
                add("number_unsupported", FAIL,
                    f"'{token}' at {path} has no vault support — "
                    f"\"{excerpt(value, token)}\" (rewording must not "
                    f"introduce numbers the vault lacks)")
    if i_clean:
        add("identity", PASS,
            f"{len(found['identity'])} name/org/title field(s) matched")

    # ── report (evaluator verdict/checks[] contract) ─────────────────
    failed = any(c["level"] == FAIL for c in checks)
    report = {
        "layer": "projection",
        "file": str(args.resume),
        "vault": str(args.vault),
        "verdict": FAIL if failed else PASS,
        "checks": checks,
        "notes": notes,
        "metrics": {"numbers_checked": n_tokens, "dates_checked": n_dates,
                    "urls_checked": len(url_items),
                    "identity_checked": len(found["identity"]),
                    "metric_pairs_checked": len(pairs)},
    }
    if args.as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        icon = {PASS: "ok", WARN: "!!", FAIL: "XX"}
        print(f"[projection] {args.resume.name} ⇄ {args.vault.name}")
        for c in checks:
            print(f"  {icon[c['level']]}  {c['check_id']}: {c['detail']}")
        for note in notes:
            print(f"  note  {note}")
        print(f"  => {'FAIL' if failed else 'PASS'}")

    if failed:
        n = sum(1 for c in checks if c["level"] == FAIL)
        print(f"\n{n} hard fact(s) in the projection have no vault support. "
              "Deleting them silently is not the fix: confirm each with the "
              "user, record it in the vault (with the answer), then keep it "
              "in the yaml — projections never contain a fact the vault lacks.",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
