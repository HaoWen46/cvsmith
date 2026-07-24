#!/usr/bin/env -S uv run --script
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
appears somewhere in the vault — and, where the vault is structured
enough to say so, in the SAME entry the projection attributes it to.
Presence, not meaning — tokens are not bound to the claims they sit
in: a mechanical PASS proves every hard-fact token exists where it
should, never that the sentence around it is telling the truth about
what happened. Two slices of meaning ARE bound, both narrowly and
both only ever WARN, never FAIL, on top of the token check — neither
reintroduces the global ordered-pair/semantic heuristic round 1
rejected for false-failing honest rephrasings:
  - ordered pairs carrying an explicit direction marker
    ("480 ms -> 210 ms", "from 480 ms to 210 ms") are compared
    against vault lines holding both numbers. Same-order vault
    marker = verified; vault markers all reversed = FAIL (this one
    case IS a hard fact, not a maybe); no vault marker = WARN for
    manual review.
  - a claim's content words (stopwords and numbers excluded) are
    compared against its best-matching vault line, when one is
    matched to the claim's own entry — see `claim_semantic_mismatch`
    below.
The unverifiable residue — pairs whose vault support carries no
direction marker, plus unpaired numbers — stays bag-of-tokens, on the
human review; an audit note counts it out loud whenever directional
pairs exist.
Org/title/name wording is legitimately reframed per
application, so drift there only WARNs — but a drifted value is
still swept for numeric tokens, which FAIL like content numbers.

Per-entry scoping (education/experience/projects): a whole-vault
search alone cannot catch two real achievements swapped between two
employers — both numbers exist somewhere in the vault, just under
the wrong one. When the vault marks its own entries with the
documented `### <org> — <title> (<start>–<end>)` heading (career-vault.md,
Protocol; same shape for education/projects), each projection entry
is matched to ONE vault heading by its org/title (or
institution/degree, or name) tokens, and its numbers/dates/urls are
checked against that entry's own block first. A token missing from
its own block but present in a DIFFERENT one is a FAIL
(`*_misattributed`) — the swapped-fact class, not a generic miss. An
entry whose section the vault structures but whose anchor matches
zero (or more than one) heading can't be scoped at all: that is an
`entry_unscoped` WARN, and the entry falls back to the old
whole-vault check for its own facts — never a silent pass with no
signal that scoping failed. But "falls back to whole-vault" does not
mean an unscoped entry may borrow a fact a SIBLING entry in the SAME
projection is already matched to: for numbers, decided per CLAIM (a
whole string's numbers), not per lone token — a realistic vault reuses
small common numbers across unrelated entries constantly, so one
coincidental shared digit is not the swapped-fact signal, only a
single sibling entry's own block covering EVERY number the claim
states is. That single block match = `number_misattributed` FAIL, the
same swapped-fact class as the matched-entry case, even though this
entry has no own block to compare it to directly. No sibling entry's
block covers the whole claim (support exists only in unanchored free
text, or in a block no CURRENT entry claims — an honest rename not yet
reconciled is the common innocent case there, and must not be treated
as a swap just because nobody's anchor reaches it yet) = a real but
unconfirmable fact: `number_unanchored_support` WARN, never a silent
pass. A vault that never uses the heading format for a section (older
vaults, or a section still written as free text) gets no scoping and
no warning there either: nothing regresses, because there is nothing
to anchor against. Metric-pair direction markers use the same scoped
block when one is matched, unscoped falls back to the whole vault as
before.

Part of the builder's authoring loop (like check_bullets.py), not the
evaluator's battery — the cold read is vault-blind by design.

What is checked, and how leniently:
  numbers   numeric tokens in EVERY string value outside meta.* —
            content strings (bullets, summary, honors, gpa, citation,
            tags) and everything else (coursework, locations, phone,
            labels, skill items, ...), matched literally after
            normalizing dashes, thousands separators, and ~/$/+/%
            decoration.
            Checked against the entry's own vault block first when one
            is matched (see "Per-entry scoping" above); found only in
            a different block = FAIL number_misattributed; found
            nowhere = FAIL number_unsupported. An `entry_unscoped`
            entry (no own block to check against) gets the same split
            one level up, decided per claim string: every number in it
            covered by ONE sibling entry's own (matched) block = FAIL
            number_misattributed; not fully covered by any single
            sibling's block (even if a lone digit coincidentally
            recurs elsewhere, or the true block just isn't claimed by
            anyone this run) = WARN number_unanchored_support, not a
            silent pass. Numbers do not get to hide in fields the sweep
            never read.
  claims    (content strings only, entry matched to its own block
            only) presence is not meaning: a claim whose numbers
            verify but whose content words (stopwords/numbers
            excluded) overlap too little with the one vault line that
            holds all of them = WARN claim_semantic_mismatch, printing
            both lines side by side for a human to compare. Overlap is
            WEIGHTED LINE COVERAGE — the matched vault line's own
            content words, weighted by idf-like rarity (words the
            vault repeats everywhere count less, words unique to this
            fact count more), that the claim also contains; NOT a raw
            shared-word count, NOT a ratio against the smaller side,
            and NOT a symmetric Jaccard over both sides' combined
            vocabulary either (see CLAIM_LINE_OVERLAP_THRESHOLD — all
            three were tried and rejected, with numbers, in favor of
            this one). A plain smaller-side ratio rewards SHORT claims
            by construction (an ordinary 4-6-word bullet can clear a
            fixed ratio by accident, not just by design); a symmetric
            Jaccard fixes that but then penalizes an honest claim for
            its OWN extra elaboration exactly like it penalizes a
            fabrication, since both directions count. Measuring the
            LINE's coverage alone fixes both without that new cost: no
            claim-length term exists in the formula at all (a short
            claim earns nothing merely by being short — it must
            actually contain the line's distinctive words), and a
            claim that elaborates beyond the line is never penalized
            for doing so, since only the line's own vocabulary is the
            denominator. Clearing the bar requires the ratio to
            strictly EXCEED the threshold, not merely equal it —
            equality is treated as insufficient on purpose, closing
            the exact adversarial case a strict '<' comparison
            invited: a claim hand-tuned to land precisely on the
            boundary. An honest rephrasing of the SAME fact clears the
            bar with margin and stays silent; only a claim whose real
            content — verb, object, subject — diverges from its
            matched line is flagged, and only ever WARN, since a false
            claim proven wrong outright is already FAIL above. This is
            a mechanical tripwire, not proof of meaning either way: it
            has no grammar or synonym awareness, and a crafted claim
            can still clear the bar (or the vault can simply be
            edited) — WARN means send it to a human, not "fabricated",
            and clearing the bar is not confirmation of truth. When a
            claim's numbers are each present somewhere in the block
            but no SINGLE line covers all of them, there is no one
            line to compare content words against — a claim could be
            stitching a number from one real fact to a number from a
            different real fact in the same entry = WARN
            claim_numbers_span_multiple_facts, also manual-audit only,
            never FAIL (an honest claim can coincidentally share a
            number with an unrelated line too).
  skills    atomic tokens (SKILL_KEYS: `stack`, `coursework`, the
            top-level `skills:` groups' `items`) are not sentences —
            there is no leftover wording once the token's own words are
            accounted for, so the weighted-overlap tripwire above does
            not apply. Instead: every significant word (1+ letter-led
            chars, connective furniture dropped, a trailing +/# run
            absorbed into the token — round 8, finding 3a: a bare
            single-letter language like "R" or "C" and a symbol-
            suffixed one like "C++"/"C#"/"F#" tokenize to themselves
            now, not to nothing) of the skill/tool/course string must
            appear, boundary-matched, SOMEWHERE in the vault — not
            necessarily contiguous or in the same order (a compound
            entry like "PostgreSQL / Redis / MySQL", or a vault that
            records the same tool in a different sentence, is common
            and legitimate). A token that appears nowhere at all in the
            vault = FAIL skill_unsupported: "add it to the vault with
            evidence, or remove it from the projection" — fail-closed
            is correct here specifically because it is cheap for the
            user to fix, unlike a whole sentence's wording; an entry
            with NO checkable token (blank, or every word a connective
            stopword) is `unsupported` too now (round 8, finding 3a) —
            never a free pass. A token whose only vault trace sits
            inside a line the vault itself marks excluded (see
            "exclusions" below) is neither of those: labeled WARN
            skill_excluded_only, never folded into plain absence and
            never a silent pass. `tags` stays a claims-style content
            string, not a skill: career-vault.md's own worked example
            shows tags are short DESCRIPTOR phrases ("RAG evaluation"),
            not verbatim vaultable keywords, and fail-closed matching
            there false-fails legitimate paraphrased tags.
  exclusions  (round 8, finding 3b) career-vault.md documents two line
            prefixes — NOT-CLAIMABLE: and PENDING-EVIDENCE: — that mark
            a line as never usable support for anything it mentions,
            for every check above (numbers, dates, urls, skills, and
            every candidate support-line the pairing table searches).
            A token/date/url/skill found ONLY inside such a line is
            reported as its own labeled `*_excluded_only` WARN — neither
            a silent pass (what happened before this fix: the vault's
            own disclaimer text still counted as ordinary haystack
            support) nor an undifferentiated "no support anywhere" FAIL
            (which would erase the useful distinction between "the
            vault never mentions this" and "the vault explicitly says
            not to claim this").
  fields    (round 8, finding 4/systemic) every schema field this
            script does not explicitly classify (KNOWN_SCHEMA_KEYS,
            next to SKILL_KEYS) still gets the numeric-only "other"
            sweep, but ALSO raises a loud `unchecked_field` WARN — a
            field nobody taught this script a real check for can no
            longer look identical to one that was reviewed and is
            genuinely fine as numeric-only; schema drift surfaces
            instead of silently reopening whatever fact class the new
            field turns out to carry.
  pairing   VISIBILITY, not another tripwire: the report always carries
            a claim -> source pairing section listing EVERY content
            claim (bullets, summary, honors, gpa, citation, tags — every
            CONTENT_KEYS string, numeric or not) next to the exact vault
            line(s) that support it (or, when none does, its manual-
            audit/FAIL status and why). This exists because no lexical
            tripwire — this script's or any future replacement's — can
            fully tell a synonym swap (legitimate) from a verb+object
            swap (fabricated) from word overlap alone; the WARN checks
            above are the automatic, narrow, low-noise subset of what
            the pairing table shows in full. A claim the WARN checks
            miss is never invisible: it is still printed next to its
            source line for a human (or the evaluator reading this
            report) to compare by eye. The pairing table is the
            guarantee; the WARN is the automatic subset of it.

            Every row carries one of four levels, and they mean
            different things — "pass" is reserved for a claim this
            script actually mechanically confirmed (a numeric claim,
            scoped to its own matched vault entry, whose best-supporting
            line clears CLAIM_LINE_OVERLAP_THRESHOLD): "fail" and "warn"
            are the FAIL/WARN checks above, mirrored here for visibility;
            "info" is everything this script cannot honestly grade
            either way — a numeric claim in a section the vault never
            structures at all (basics.summary, a citation, any
            never-scoped field — matched against the whole vault, not
            one entry's own lines), AND every qualitative claim (no
            numbers at all — nothing for presence-checking to anchor
            to). Both of those used to be mislabeled "pass": a
            never-scoped claim's ratio cannot honestly separate a
            rephrase from a fabrication (measured — see the pairing
            loop's own comment in main()), and neither can a
            qualitative claim's best-scoring-line ratio (measured —
            see evals/test_projection.py's TestQualitativeLineOverlap:
            a legitimate paraphrase and an outright fabrication land in
            the same, overlapping score range once there is no number
            to narrow the candidate-line search). "info" rows still
            always show the best-matching line and its ratio — visible,
            never silently dropped — they are simply never promoted to
            WARN, never counted toward claim_pairings_manual_audit
            (that metric stays warn-only by definition), and no longer
            mislabeled as something this script confirmed. They ARE
            counted, alongside warn rows, in the separate
            claim_pairings_needs_audit total the verdict line reports
            (round 8, finding 8) — an "info" row is exactly as
            mechanically unconfirmed as a "warn" row, and SKILL.md's
            own builder contract says read both, so the verdict line's
            "N need manual audit" would otherwise understate how much
            of the pairing table still needs a human.
  dates     start/end values (YYYY-MM), matched against YYYY-MM,
            "Mon YYYY", "Month YYYY", MM/YYYY, YYYY/MM — own block
            first, same misattributed/unsupported split as numbers.
            Only the year found (anywhere) = WARN; nothing found =
            FAIL. An end of "present" is mechanically unverifiable in
            either direction, so every ongoing-role claim is listed in
            an ongoing_roles WARN for manual confirmation — an ended
            role projected as ongoing is fabrication this script
            cannot see on its own. Reversed chronology (start after
            end) is validate_yaml.py's job, not this script's — it
            needs no vault at all.
  urls      url fields (and any URL pasted into a content string),
            compared after stripping scheme, leading www., and the
            trailing slash — and matched with a right boundary, so
            github.com/user is never supported by the different
            account github.com/username. Own block first, same
            misattributed/unsupported split. Miss everywhere = FAIL.
  pairs     ordered numeric pairs in content strings with an explicit
            direction marker: X -> Y / X → Y / X ⇒ Y, or
            "from X ... to Y" inside one string (~40-char window, no
            sentence boundary). Vault line with both numbers and a
            same-order marker = verified; vault markers only in the
            reversed order = FAIL; both numbers co-occur but no
            marker = WARN (manual review). Pairs whose numbers
            already failed presence are not double-reported.
  identity  name / organization / institution / title / degree not
            found verbatim splits into two classes: some meaningful
            token still matches the vault = WARN (rename/reformat
            drift is legitimate); ZERO tokens match = FAIL (the
            fabrication class — a Google CRO projected from a
            Widget Corp internship shares no token with the vault).
            Numeric tokens in a drifted value are checked like
            content numbers either way. The remediation for a real
            rename is the invariant itself: record the alias in the
            vault first, then keep it in the yaml.
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
import math
import re
import sys
from pathlib import Path

PASS, WARN, FAIL, INFO = "pass", "warn", "fail", "info"
# Checks whose WARN means specifically "a human must look, meaning can't
# be mechanically confirmed either way" — as opposed to WARNs that are
# just legitimate-reframing notices (identity_drift, date_year_only,
# entry_unscoped, ongoing_roles, metric_direction's unmarked case all
# already say so in their own detail). Counted separately so the verdict
# line never reads as an unqualified PASS when one of these is present.
MANUAL_AUDIT_CHECK_IDS = {"claim_semantic_mismatch", "number_unanchored_support",
                          "claim_numbers_span_multiple_facts",
                          "claim_novel_wording", "claim_direction_conflict"}
# Round 9, finding 3: weighted_overlap() measures coverage of the VAULT
# LINE, by design (see its docstring) — a claim that repeats the line's
# long opening clause and its numbers, then states a DIFFERENT outcome,
# covers the line completely and scores a clean pass. The line-coverage
# asymmetry is right and is not being changed; what was missing is any
# signal about the claim's own words that the vault has never used
# anywhere. A word with document frequency 0 across the entire vault is
# vocabulary the vault cannot vouch for. One such word is an ordinary
# rewrite (a synonym for a verb); several is a claim saying something
# the vault does not. This is a visibility tripwire for manual audit —
# a WARN, never a FAIL — because an honest, heavily-reworded bullet can
# reach it too.
#
# Calibrated, not guessed, against this repo's own resume/vault pair
# (the zero-false-positive target — see the module docstring) and
# against the finding's own claim shape. Novel-word share of each
# claim's content words, measured:
#   honest rewrites, every bullet in the real pair:  0.00 – 0.25
#     (worst: "adding / moving / warmup" for the vault's "warming /
#     switching", 3 of 14 = 0.21)
#   shared-clause-then-different-outcome fabrications: 0.35 – 0.69
# The floor of 3 words keeps a single synonym swap in a short claim
# from tripping the ratio, and 0.30 sits in the measured gap.
NOVEL_WORD_AUDIT_FLOOR = 3
NOVEL_WORD_AUDIT_SHARE = 0.30

DATE_KEYS = {"start", "end", "date"}
URL_KEYS = {"url"}
CONTENT_KEYS = {"bullets", "summary", "honors", "gpa", "citation", "tags"}
# Atomic skill/tool tokens — a short list item, not a sentence. There is
# no leftover wording for a weighted-overlap tripwire to compare a
# rephrase against a fabrication with, so these get a different check
# entirely (see the `skills` block in main()): normalized whole-vault
# presence, fail-closed. `stack` moved out of CONTENT_KEYS into here
# (round 7, finding 1b/2) — a project's stack ("Rust", "SQLite") is the
# same atomic-token shape as a top-level skills item, not a claim
# sentence, and used to be silently invisible to both the numeric sweep
# (no digits) and the pairing table (no digits either). `coursework`
# joins them here (round 8, finding 4): a course name ("Quantum
# Computing") is the same short, keyword-shaped, vaultable-atom class
# as a skill or a stack entry, not a sentence — it used to have no
# dedicated check at all, landing only in the generic numeric-only
# "other" sweep (see the field-coverage registry below), so a course
# with zero digits in its name was invisible to every check in this
# script. `tags` stays in CONTENT_KEYS deliberately: career-vault.md's
# own worked example shows tags are short DESCRIPTOR phrases ("RAG
# evaluation", "GPU cluster scheduling"), not verbatim vaultable
# keywords — data-schema.md calls them "domain descriptors", and
# fail-closed exact matching on them false-fails legitimate paraphrased
# tags. The top-level `skills:` section's nested `items:` lists are
# collected separately in collect() below (their own key, "items", is
# what routes them here).
SKILL_KEYS = {"stack", "items", "coursework"}
IDENTITY_KEYS = {"name", "organization", "institution", "title", "degree"}
# ── schema field-coverage registry (round 8, finding 4/systemic) ──────
# Every scalar-bearing key the schema recognizes (validate_yaml.py's own
# key inventory: BASICS_KEYS, EDU_KEYS, EXP_KEYS, PROJ_KEYS, its
# SKILL_KEYS, PUB_KEYS, AWARD_KEYS, LINK_KEYS) must land in exactly one
# bucket below — DATE_KEYS, URL_KEYS, CONTENT_KEYS, SKILL_KEYS,
# IDENTITY_KEYS, or this one — so a field nobody taught this script
# about can never again silently ride the generic numeric-only "other"
# sweep with a human unable to tell the silence apart from "reviewed
# and fine" (that gap is exactly what let a coursework claim through
# with zero checks at all — see the SKILL_KEYS comment above). These
# two are reviewed and accepted as numeric-sweep-only on purpose, not
# an oversight:
#   - "label" (basics.links[].label, a skills group's own label like
#     "Languages") — a UI caption, not a fact to verify.
#   - "group" (experience[].group: research|teaching|industry) — a
#     section-routing enum, not a fact.
# Any OTHER schema field is, by definition, one this script has never
# been taught about — see collect()'s unchecked_field WARN, the loud
# signal that keeps schema drift from silently reopening this class.
NUMERIC_SWEEP_ONLY_KEYS = {"label", "group"}
# ── contact / personal facts (round 9, finding 1) ─────────────────────
# These four used to be NUMERIC_SWEEP_ONLY: checked for stray digits and
# nothing else, so a wrong reply-to email, a wrong phone number, a
# fabricated city, or an invented field of study all returned overall
# PASS. They are hard personal facts — the ones an employer actually
# uses to reach the person — and they get a fail-closed check of their
# own (see main()'s contact section):
#   - email/phone: the exact normalized string must appear in the vault.
#     Near-enough is not a category that exists for a reply address.
#   - location/field: every token must co-occur on ONE vault line, the
#     same rule the skills check uses.
CONTACT_KEYS = {"email", "phone", "location", "field"}
CONTACT_EXACT_KEYS = {"email", "phone"}
KNOWN_SCHEMA_KEYS = (DATE_KEYS | URL_KEYS | CONTENT_KEYS | SKILL_KEYS
                     | IDENTITY_KEYS | CONTACT_KEYS | NUMERIC_SWEEP_ONLY_KEYS)
PRESENT_WORDS = {"present", "current", "ongoing", "now"}
# Generic org/degree furniture: shared suffix words must not let a
# fabricated identity ride on them ("... Institute of Technology").
IDENTITY_STOP = {"the", "and", "for", "inc", "llc", "ltd", "corp",
                 "corporation", "company", "gmbh", "university",
                 "institute", "institution", "technology", "college",
                 "school", "department", "faculty", "national"}
# Function words excluded from the claim/vault-line content-word overlap
# test (below) — generic connective tissue that honest rephrasings and
# unrelated topic-swaps alike are full of, so it must not count as
# "shared meaning" in either direction.
OVERLAP_STOP = {
    "a", "an", "the", "and", "or", "but", "of", "to", "in", "on", "at",
    "by", "for", "with", "from", "as", "is", "are", "was", "were", "be",
    "been", "being", "this", "that", "these", "those", "it", "its",
    "across", "per", "into", "onto", "over", "under", "up", "down",
    "out", "off", "than", "then", "so", "not", "no", "nor", "also",
    "which", "who", "whom", "whose", "while", "during", "within",
    "without", "about", "between", "through", "after", "before",
    "above", "below", "more", "most", "less", "least", "each", "every",
    "some", "any", "all", "both", "few", "many", "much", "such", "own",
    "same", "other", "another", "new", "our", "their", "his", "her",
}

# round 5's fix (a raw shared-word count normalized by the SMALLER
# side's word count, threshold 0.5) still had two structural holes an
# adversarial verifier found in round 6, both against the vault line
# "reduced api latency 40% across 3 backend services for retail
# clients": "Boosted api retail clients 40% across 3 accounts." (3
# shared of min(5,7) = 0.60 — clears 0.5) and "Boosted retail clients
# 40% across 3 accounts." (2 shared of min(4,7) = 0.50 — the strict
# '<' comparison let an exact tie through too). Two separate defects,
# fixed together below:
#   1. min() rewards SHORT claims as a side effect of length alone —
#      an ordinary honest 4-6-word bullet can land at the same ratio a
#      short fabrication does, by accident, not by construction; N=2
#      is enough at that length. Length-normalizing against the
#      smaller side was never sufficient on its own.
#   2. every shared word counted equally, so a fabrication that kept
#      exactly the vault line's own generic filler ("api", "retail",
#      "clients" — words the vault repeats across unrelated lines
#      constantly) scored the same as one that kept the line's
#      distinctive content ("latency", "backend", "reduced" — words
#      that appear once, and actually identify the fact).
# The fix, in weighted_overlap() below: idf-like rarity weighting
# (word_weight() — rare-across-the-vault words score higher,
# vault-wide furniture scores near its floor of 1.0) defeats hole 2 —
# the two bypass claims above kept ONLY the vault line's cheapest,
# most-repeated words and dropped every distinctive one, and rarity
# weighting prices that trade correctly. Hole 1 is defeated more
# directly than a Jaccard union would (a symmetric weighted Jaccard
# was tried and rejected — see weighted_overlap()'s docstring for why
# it broke a legitimate verbose paraphrase): the score is the matched
# vault LINE's own weighted vocabulary covered by the claim, with no
# claim-length term in the formula at all, so a short claim earns
# nothing merely by being short — it must actually contain the line's
# distinctive words. Clearing the bar also now requires the ratio to
# strictly EXCEED the threshold — equality warns, closing the
# adversarial edge a strict '<' comparison invited (a claim tuned to
# land exactly on the line).
#
# Calibration (see evals/test_projection.py's TestClaimLineOverlap
# margin table for the full set, measured against real vault fixtures
# via the actual functions, not hand math):
#   legitimate (must stay clean, line coverage):
#     reorder                          1.000
#     compression ("Cut API latency 40%.")            0.768
#     compression, descriptor vault                    0.679
#     synonym swap ("Lowered ... latency ...")          0.732
#     synonym swap, descriptor vault                    0.601  <- tightest
#     verbose paraphrase ("Scaled from 3 services.
#       Brought p99 down to 210 ms.")                    0.684
#   fabrication / bypass (must warn, line coverage):
#     3-descriptor pad (existing adversarial case)      0.399  <- tightest
#     round-6 bypass 1 ("Boosted api retail clients
#       40% across 3 accounts.")                         0.358
#     fresh short generic-only variants (A, B)           0.358
#     round-6 bypass 2 ("Boosted retail clients 40%
#       across 3 accounts.")                              0.239
#     2-descriptor pad                                    0.239
#     topic swap ("Raised revenue 40% across 3
#       services.")                                        0.232
#     1-descriptor pad                                     0.119
#     semantic mismatch (no shared words at all)            0.000
# Legitimate minimum 0.601, fabrication maximum 0.399 — a symmetric
# ~0.10 margin on each side of 0.5. 0.5 is a tripwire calibrated
# against the cases above, not a proof of semantic identity — see
# weighted_overlap()'s docstring for what it does and does not
# establish, including the honestly-stated residue it cannot close: a
# single strategic word swap inside an otherwise-long, otherwise-
# verbatim line still clears this bar, no token-overlap metric closes
# that completely, which is exactly why the claim -> source pairing
# section exists as the non-lexical backstop (see the module
# docstring's `pairing` entry).
CLAIM_LINE_OVERLAP_THRESHOLD = 0.5

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
# "to Y ... from X" — the same direction stated in the other word order.
# Round 9, finding 3: without this, "cut latency to 73 ms from 11 ms"
# produced NO directional pair at all, so the reversal check had nothing
# to compare against the vault's own "from 73 ms to 11 ms" and the claim
# passed clean. Groups are emitted in canonical (from, to) order — see
# directional_pairs()'s swap — so a reversal is detected identically no
# matter which word order either side used.
TO_FROM_PAIR = re.compile(
    rf"\bto\b[^\d.;]{{0,12}}({NUM})[^.;]{{0,40}}?"
    rf"\bfrom\b[^\d.;]{{0,12}}({NUM})")


def directional_pairs(norm: str) -> list[tuple[str, str]]:
    """Ordered numeric pairs carrying an explicit direction marker,
    from one normalized string, always as (before, after) regardless of
    the surface word order. Pairing never crosses string values."""
    pairs = []
    for rex in (ARROW_PAIR, FROM_TO_PAIR):
        pairs.extend(m.groups() for m in rex.finditer(norm))
    # "to Y from X" states (X -> Y): swap back into canonical order, and
    # only when this span was not already claimed by "from X to Y" above
    # (a single "from a to b" cannot also match to-from, but a chained
    # "from a to b from c" can produce a duplicate — dedupe by identity).
    for m in TO_FROM_PAIR.finditer(norm):
        after, before = m.groups()
        if (before, after) not in pairs:
            pairs.append((before, after))
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


# Sections whose entries can be scoped to one vault block, and the field(s)
# whose tokens anchor an entry to a "### <heading>" (org/title, or
# institution/degree, or name — career-vault.md's Experience shape, assumed
# for education/projects too since the doc says "same shape").
SCOPED_SECTIONS = {
    "experience": ("organization", "title"),
    "education": ("institution", "degree", "field"),
    "projects": ("name",),
}
# Substring aliases matched against the vault's ## ancestor heading text
# (already casefolded by normalize()) — lenient about "Professional
# Experience" / "Work Experience" and singular "Project".
SECTION_ALIASES = {
    "experience": ("experience",),
    "education": ("education",),
    "projects": ("project",),
}


def _leaf_key(path: str) -> str:
    """The final key name a dotted/bracketed yaml path ends in —
    "education[0].coursework[1]" -> "coursework" — used only to name an
    unrecognized field for the unchecked_field WARN (round 8, finding
    4/systemic); list indices are noise for that purpose."""
    return re.sub(r"\[\d+\]", "", path.rsplit(".", 1)[-1])


def collect(node, path, out, entry_key=None):
    """One walk of the yaml tree, routing values by key. meta.* skipped.
    Scalars under no routed key land in "other" (every string field
    gets the numeric sweep, not just the famous ones) AND, when the key
    is not in KNOWN_SCHEMA_KEYS, also in "unchecked" — round 8, finding
    4/systemic: a schema field this script was never taught a bucket
    for used to fall silently into "other" with no signal that it was
    unclassified rather than reviewed-and-fine; now it still gets the
    same numeric-only fallback (nothing regresses) but also surfaces a
    loud unchecked_field WARN in main(), so schema drift can never
    silently reopen this class. Every item also carries entry_key:
    "experience[0]" etc. for anything under a scoped section's list
    entries, None otherwise — the scoping-lookup key. SKILL_KEYS
    ("stack", "coursework", the skills-group "items") land in "skills",
    checked separately (atomic-token presence, not claim overlap) —
    picked up here by KEY name alone, same as every other routed key,
    so a top-level `skills: [{label, items}]` group's `items` list gets
    the same treatment as a `projects[].stack` or `education[].
    coursework` list with no extra case."""
    if isinstance(node, dict):
        for key, value in node.items():
            if not path and key == "meta":
                continue
            p = f"{path}.{key}" if path else str(key)
            if not path and key in SCOPED_SECTIONS and isinstance(value, list):
                for i, item in enumerate(value):
                    ek = f"{key}[{i}]"
                    if isinstance(item, (dict, list)):
                        collect(item, f"{p}[{i}]", out, ek)
                    elif item is not None:
                        out["other"].append((f"{p}[{i}]", str(item), ek))
                continue
            if key in DATE_KEYS:
                out["dates"].append((p, value, entry_key))
            elif key in URL_KEYS:
                if value is not None:
                    out["urls"].append((p, str(value), entry_key))
            elif key in CONTENT_KEYS:
                out["content"].extend(
                    (pp, txt, entry_key) for pp, txt in iter_strings(value, p))
            elif key in SKILL_KEYS:
                out["skills"].extend(
                    (pp, txt, entry_key) for pp, txt in iter_strings(value, p))
            elif key in IDENTITY_KEYS:
                if value is not None:
                    out["identity"].append((p, str(value), entry_key))
            elif key in CONTACT_KEYS:
                if value is not None:
                    out["contact"].append((p, str(value), entry_key))
            elif isinstance(value, (dict, list)):
                collect(value, p, out, entry_key)
            elif value is not None:
                if key not in KNOWN_SCHEMA_KEYS:
                    out["unchecked"].append((key, p))
                out["other"].append((p, str(value), entry_key))
    elif isinstance(node, list):
        for i, item in enumerate(node):
            if isinstance(item, (dict, list)):
                collect(item, f"{path}[{i}]", out, entry_key)
            elif item is not None:
                key = _leaf_key(path)
                if key not in KNOWN_SCHEMA_KEYS:
                    out["unchecked"].append((key, f"{path}[{i}]"))
                out["other"].append((f"{path}[{i}]", str(item), entry_key))


HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*$", re.MULTILINE)
BULLET_START_RE = re.compile(r"^\s*[-*+]\s")
HEADING_START_RE = re.compile(r"^#{1,6}\s")
METADATA_LINE_RE = re.compile(r"^updated:\s")


def unwrap_lines(raw: str) -> list[str]:
    """Merge markdown soft-wrapped continuation lines into their parent
    bullet/paragraph line (round 7, finding 8/fix 4). A vault FACT
    written as `- FACT: built ...\\n  assistant ...; ran ... 1,200 ...\\n
    support ... 3 ...` is ONE sentence about one achievement, but
    line-level matching (best_full_support_line() et al.) previously saw
    three separate physical lines and reported the numbers as spanning
    multiple facts. A line starting with a bullet marker (-, *, +) or a
    heading marker (#) always starts (and, for a heading, also ends) its
    own logical line; a blank line always ends the current logical line
    too — wrapping never joins across a paragraph break or into a
    heading. Everything else is a continuation of whatever logical line
    is currently open, joined with a single space (leading/trailing
    whitespace from the physical line dropped, matching how a markdown
    renderer would reflow it)."""
    logical: list[str] = []
    for raw_line in raw.splitlines():
        if not raw_line.strip():
            logical.append(raw_line)
            continue
        stripped = raw_line.strip()
        if HEADING_START_RE.match(stripped) or BULLET_START_RE.match(raw_line):
            logical.append(raw_line)
            continue
        if logical and logical[-1].strip() and not HEADING_START_RE.match(logical[-1].strip()):
            logical[-1] = logical[-1].rstrip() + " " + stripped
        else:
            logical.append(raw_line)
    return logical


def is_furniture_line(normalized_line: str) -> bool:
    """Headings and top-of-file metadata are never a claim's support
    line — a heading names an org/dates, not an achievement, and a
    claim that coincidentally shares a token with one (a year, a name
    fragment) is not evidence of anything (round 7, finding 8/fix 5:
    this is exactly how a citation's "2025" token matched the Meridian
    Labs ### heading instead of the real Publications FACT line).
    Excluded from every candidate support/match-line search, scoped and
    whole-vault alike; never from `haystack`, which still needs to
    answer the coarser "does this token exist anywhere" question."""
    s = normalized_line.strip()
    return not s or bool(HEADING_START_RE.match(s)) or bool(METADATA_LINE_RE.match(s))


# ── exclusion-marker contract (round 8, finding 3b) ───────────────────
# career-vault.md documents two line-prefixes alongside FACT:/CONTEXT:/
# CUT: — NOT-CLAIMABLE: (a fact that must never be claimed: absent,
# disproven, or actively disclaimed) and PENDING-EVIDENCE: (something
# true-ish but not yet confirmed enough to claim). A line carrying
# either marker (case-insensitive; normalize()'s dash unification means
# any unicode dash variant counts too) is the vault author's own
# statement that this line's content is NOT usable support for
# anything it happens to mention — a Kubernetes skill claim must not
# verify off a vault line that says "no production Kubernetes
# experience, do not claim it". Matches inside such a line are excluded
# from EVERY check's positive-evidence surface (numbers, dates, urls,
# skills, and every candidate support-line search the pairing table
# uses) — never a silent pass, and (see haystack_text()/
# excluded_haystack_text() below) never silently conflated with a token
# that has no vault trace at all either: a token found ONLY inside an
# excluded line gets its own labeled WARN.
EXCLUSION_MARKER_RE = re.compile(r"\bnot-claimable\b|\bpending-evidence\b")
# Round 9, finding 2: an explicit denial written as ordinary prose, with
# no marker on the line at all — "no production Kubernetes experience",
# "never used Terraform" — was previously ordinary clean evidence, so
# the very sentence saying a skill is ABSENT was what verified it. This
# is deliberately narrow: only the denial IDIOM (a negator immediately
# governing a noun phrase that ends in experience/exposure/background,
# or "never used/never worked with/do not claim"). A bare "no"/"not"
# anywhere in a line is NOT enough — a real FACT line ("cut error rate
# 40% with no added infra cost") must keep counting as support.
DENIAL_RE = re.compile(
    r"\b(?:no|zero|little|minimal|without)\b[^.;]{0,40}?"
    r"\b(?:experience|exposure|background|familiarity)\b"
    r"|\bnever\s+(?:used|worked\s+with|shipped|touched|ran)\b"
    r"|\bdo\s+not\s+claim\b|\bdon't\s+claim\b")
# CUT: lines (career-vault.md's own third prefix) record material
# DROPPED from some earlier resume "so it isn't re-litigated". That is
# weaker than a FACT line but not a denial: the content is usually still
# true, it just did not earn space once. So a claim whose only trace in
# the vault is a CUT line is neither silently accepted (round 9,
# finding 2 — it was) nor hard-failed; it is a labeled WARN.
CUT_MARKER_RE = re.compile(r"(?:^|[-*]\s*)cut:")
# Round 9 (round-2 review), finding 1: `## Gaps & flags  (honesty
# ledger)` is, by career-vault.md's own definition, the section that
# records "known weak spots ... things tailoring must respect, not
# paper over." A line living under it — "Kubernetes remains a known
# gap" — is the vault stating an ABSENCE, even when it carries no
# NOT-CLAIMABLE marker and no prose-denial idiom DENIAL_RE would catch.
# So the whole section is treated as denied: nothing under it is ever
# positive support. (career-vault.md still tells authors to put the
# machine-readable disclaimer on a NOT-CLAIMABLE line; this is the
# backstop for when they write it as ordinary ledger prose instead.)
GAPS_SECTION_RE = re.compile(r"gaps\s*&\s*flags|honesty\s+ledger")
_HEADING_LINE_RE = re.compile(r"^(#{1,6})\s+(.*)")


def is_denied_line(normalized_line: str) -> bool:
    """True for a vault line that AFFIRMATIVELY says its content must
    not be claimed — the NOT-CLAIMABLE / PENDING-EVIDENCE markers, or a
    prose denial (DENIAL_RE). A claim supported only by such a line is a
    FAIL, not a warning: the vault is stating the opposite, or that the
    fact is not yet confirmed enough to put on a resume."""
    return bool(EXCLUSION_MARKER_RE.search(normalized_line)
                or DENIAL_RE.search(normalized_line))


def is_cut_line(normalized_line: str) -> bool:
    """True for a CUT: line — dropped-from-a-resume material, weak
    support rather than counter-evidence (see CUT_MARKER_RE)."""
    return bool(CUT_MARKER_RE.search(normalized_line))


def is_excluded_line(normalized_line: str) -> bool:
    """True for any vault line kept OUT of the positive-evidence
    surface — denied (is_denied_line) or merely cut (is_cut_line).
    `normalized_line` must already be normalize()'d (casefolded, dashes
    unified) for the lowercase/hyphen literal matches to work."""
    return is_denied_line(normalized_line) or is_cut_line(normalized_line)


def _classify_lines(raw: str) -> tuple[list[str], list[str], list[str]]:
    """Every normalized, non-blank logical line of `raw` (unwrap_lines()
    — soft-wrapped continuations already merged), sorted into three
    tiers by what the vault is SAYING about each line's content:

      denied  — must never count as support: a NOT-CLAIMABLE /
                PENDING-EVIDENCE marker, a prose denial (DENIAL_RE), OR
                any line under a `## Gaps & flags` (honesty-ledger)
                section (round-2 review finding 1);
      cut     — a CUT: line, dropped-from-a-resume material: weak, not
                counter-evidence;
      clean   — everything else, the positive-evidence surface.

    Furniture (headings/metadata) is NOT filtered here — that is
    content_line_pool()'s job; the haystack surfaces want furniture left
    IN. One shared base so the marker/section logic lives in one place.

    Section context is tracked from `##`-or-shallower headings. It only
    ever matters for the whole-vault pass: a per-block body starts at a
    `###` entry heading and contains no `##`, so its lines classify
    purely by their own markers — exactly as before."""
    clean: list[str] = []
    cut: list[str] = []
    denied: list[str] = []
    in_gaps = False
    for raw_line in unwrap_lines(raw):
        if not raw_line.strip():
            continue
        norm = normalize(raw_line)
        head = _HEADING_LINE_RE.match(norm)
        if head and len(head.group(1)) <= 2:
            in_gaps = bool(GAPS_SECTION_RE.search(head.group(2)))
        if in_gaps or is_denied_line(norm):
            denied.append(norm)
        elif is_cut_line(norm):
            cut.append(norm)
        else:
            clean.append(norm)
    return clean, cut, denied


def _partitioned_lines(raw: str) -> tuple[list[str], list[str]]:
    """(clean, excluded=cut+denied) — the two-tier view, kept for callers
    that don't need the denied/cut distinction. Thin wrapper over
    _classify_lines()."""
    clean, cut, denied = _classify_lines(raw)
    return clean, cut + denied


def haystack_text(raw: str) -> str:
    """The coarse whole-vault (or whole-block) presence surface: every
    line flattened to one normalized, whitespace-collapsed string,
    furniture (headings/metadata) included — see is_furniture_line()'s
    own docstring for why haystack wants that — but excluded lines
    (denied or cut) removed, the categories that must not count as
    support even for this coarsest "does this token exist anywhere"
    question, because the vault is explicitly saying the opposite (or
    "not yet"), not just mentioning it somewhere structurally
    uninteresting."""
    clean, _, _ = _classify_lines(raw)
    return " ".join(" ".join(clean).split())


def line_surfaces(raw: str) -> tuple[list[str], list[str], list[str]]:
    """(clean, cut, denied) normalized lines — _classify_lines() with
    furniture deliberately left in, exactly as haystack_text() leaves it
    in: this is the surface the skills check runs on, and a skill can
    legitimately be named in a ### heading. Round 9, finding 2: the
    skills check needs lines rather than one flattened string, because
    requiring a multi-word skill's tokens to co-occur on ONE line is what
    stops "Operating Systems" being assembled out of an "operating" here
    and a "systems" there."""
    return _classify_lines(raw)


def denied_haystack_text(raw: str) -> str:
    """The DENIED-only presence surface: just the lines that
    affirmatively say "do not claim this" (marker, prose denial, or
    Gaps & flags section), without the merely-cut ones. Lets a check
    separate the two tiers the single excluded surface used to flatten —
    denied support is a FAIL, cut-only support is a WARN (round 9,
    finding 2; round-2 review finding 1)."""
    _, _, denied = _classify_lines(raw)
    return " ".join(" ".join(denied).split())


def excluded_haystack_text(raw: str) -> str:
    """The excluded-only mirror of haystack_text() (cut + denied): every
    excluded line's own text, flattened the same way — lets a check tell
    "found ONLY in a line the vault marked unusable" apart from "found
    nowhere at all" (round 8, finding 3b), instead of collapsing both
    into the same plain FAIL."""
    _, cut, denied = _classify_lines(raw)
    return " ".join(" ".join(cut + denied).split())


def content_line_pool(raw: str) -> list[str]:
    """Normalized, unwrapped, furniture- and exclusion-filtered
    candidate lines for line-level matching — the single choke point
    both scoped (per-block) and whole-vault candidate pools run
    through, so the unwrap/furniture/exclusion fixes apply everywhere a
    "which vault line backs this claim" search happens, not just in one
    call site. An excluded line (round 8, finding 3b) can never win a
    best-matching-line search — it is not evidence, so it must never be
    shown as if it were."""
    clean, _, _ = _classify_lines(raw)
    return [line for line in clean if not is_furniture_line(line)]


def excluded_line_pool(raw: str) -> list[str]:
    """The excluded-marker mirror of content_line_pool() — used only to
    show a human WHICH excluded line a token/claim's only "support"
    traces back to (round 8, finding 3b), never as a match candidate."""
    clean, cut, denied = _classify_lines(raw)
    return [line for line in cut + denied if not is_furniture_line(line)]


def denied_line_pool(raw: str) -> list[str]:
    """Furniture-filtered DENIED lines only (NOT-CLAIMABLE / PENDING-
    EVIDENCE / prose denial / Gaps & flags). Round-3 review finding 1:
    a QUALITATIVE claim (no numbers) that repeats a denied line used to
    be invisible — the number-based denied check never fired, and the
    pairing table matched it to a clean line, hiding the very line that
    forbids it. This pool lets a claim be compared against what the
    vault says NOT to claim, so `claim_denied` can fail it."""
    clean, cut, denied = _classify_lines(raw)
    return [line for line in denied if not is_furniture_line(line)]


BASICS_SECTION_RE = re.compile(r"\bbasics\b|\bcontact\b")


def basics_lines(vault_raw: str) -> list[str]:
    """Normalized non-blank lines under the vault's `## Basics` (or
    `## Contact`) section — the candidate's OWN identity block. Round-3
    review finding 2: contact checks searched the whole vault, so a
    colleague's email sitting in a Q&A/Context line elsewhere could
    "support" the candidate's own email field. Scoping email / phone /
    location to Basics makes the check ownership-aware. Empty if the
    vault has no such heading; callers fall back to the whole vault
    then, degrading to the old behavior rather than failing every
    contact field on an unstructured vault."""
    out: list[str] = []
    in_basics = False
    for raw_line in unwrap_lines(vault_raw):
        if not raw_line.strip():
            continue
        norm = normalize(raw_line)
        head = _HEADING_LINE_RE.match(norm)
        if head and len(head.group(1)) <= 2:
            in_basics = bool(BASICS_SECTION_RE.search(head.group(2)))
            continue
        if in_basics:
            out.append(norm)
    return out


EMAIL_RE = re.compile(r"[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}")
# A run of phone-shaped characters (digits and the usual separators).
PHONE_RUN_RE = re.compile(r"[0-9][0-9()+.\-–— ]{5,}[0-9]")


def phone_supported(resume_digits: str, vault_phones: set[str]) -> bool:
    """A resume phone verifies only against a COMPLETE vault phone, by
    digits (round-3 review finding 2): `010-4477` (7 digits) must not
    ride on the full `+1 (555) 010-4477`. Exact digit equality, or —
    to allow an honest country-code difference — one being a suffix of
    the other when BOTH are full-length (>=10 digits). A short fragment
    (<10 digits) can only match by exact equality, so a partial number
    never passes off a longer one."""
    if not resume_digits:
        return False
    for p in vault_phones:
        if resume_digits == p:
            return True
        if len(resume_digits) >= 10 and len(p) >= 10 and (
                p.endswith(resume_digits) or resume_digits.endswith(p)):
            return True
    return False


# Negation that flips a claim's meaning — kept deliberately tight so a
# legitimate qualifier ("cut error rate with no added cost", "never an
# automated verdict" kept verbatim in the claim) is not mistaken for a
# denial. Round-3 review finding 3: the signal is a negation the VAULT
# line carries that the CLAIM has DROPPED, not the mere presence of a
# negator — so "never reduced latency" (vault) vs "Reduced latency"
# (claim) fails, while a claim that keeps the "never" does not.
# The metric/outcome nouns a "no <noun>" / "lack of <noun>" phrase
# negates. Kept to result nouns so a bare "no" in a legitimate qualifier
# ("cut error rate with no added cost") still doesn't trip this.
OUTCOME_NOUN = (r"reduction|increase|decrease|decline|improvement|change|"
                r"gain|growth|savings?|boost|rise|drop|cut|speedup|"
                r"speed-up|impact|effect|benefit")
NEGATION_RE = re.compile(
    r"\bnever\b|\bfailed\s+to\b|\bunable\s+to\b|\bdid\s+not\b|"
    r"\bcould\s+not\b|\bwas\s+not\b|\bwere\s+not\b|"
    r"\b(?:did|does|do|could|would|was|were|is|are|has|had|ca|wo)n['’]?t\b|"
    # Round-4/5 review finding: "no reduction in API latency of 40%",
    # "zero reduction", "lack of reduction", "without any improvement" —
    # a negator governing a result noun negates the achievement itself.
    rf"\b(?:no|zero|without)\s+(?:any\s+)?(?:{OUTCOME_NOUN})\b|"
    rf"\black\s+of\s+(?:{OUTCOME_NOUN})\b")
# "made/left/rendered X worse|slower|costlier|higher" — a worsening
# stated as a phrase rather than a single verb (round-5 review finding 2:
# "made latency worse" against an improvement fact).
MADE_WORSE_RE = re.compile(
    r"\b(?:made|left|rendered|kept)\b[^.;]{0,40}?"
    r"\b(?:worse|slower|costlier|higher|weaker|worse-performing)\b")
# Verbs/nouns that assert a WORSE outcome. A resume claims improvements;
# a bullet asserting a worsening is almost always a reversed metric
# ("Worsened API latency" off the vault's "cut API latency"). Round-3
# finding 3; noun forms (deterioration/degradation/…) added round-5.
NEGATIVE_OUTCOME = {
    "worsened", "worsen", "worsening", "degraded", "degrade", "degrading",
    "degradation", "regressed", "regress", "regression", "deteriorated",
    "deteriorate", "deteriorating", "deterioration", "slowed", "slow",
    "slowdown", "slowing", "inflated", "inflate", "inflation", "ballooned",
    "balloon", "hurt", "damaged", "damage", "weakened", "weaken",
    "harmed", "harm", "broke", "broken", "crippled", "cripple",
}


def asserts_worse_outcome(normalized_text: str, words: set[str]) -> bool:
    """True when the text claims a WORSE result — a NEGATIVE_OUTCOME
    word, or a 'made X worse'-style phrase. Round-5 review finding 2."""
    return bool(words & NEGATIVE_OUTCOME) or bool(MADE_WORSE_RE.search(normalized_text))


def has_negation(normalized_text: str) -> bool:
    return bool(NEGATION_RE.search(normalized_text))


# The negation-DROP check (below) fires on the STRONG subset only: forms
# that clearly negate an ACHIEVEMENT — "never <verb>", "failed/unable
# to", and a negator on a result noun ("no/zero/without/lack of
# reduction"). The generic auxiliaries ("did not", "don't", "isn't")
# are deliberately EXCLUDED here: round-5 review turned up a false
# positive where a vault line's incidental "those don't agree on who's
# first" (a naming meta-comment, nothing to do with the claim's result)
# shared a stray number with the claim and hard-failed it. A generic
# n't in descriptive prose is too weak a signal to invert a claim on;
# an achievement-negating form is not.
STRONG_NEGATION_RE = re.compile(
    r"\bnever\b|\bfailed\s+to\b|\bunable\s+to\b|"
    rf"\b(?:no|zero|without)\s+(?:any\s+)?(?:{OUTCOME_NOUN})\b|"
    rf"\black\s+of\s+(?:{OUTCOME_NOUN})\b")


def has_strong_negation(normalized_text: str) -> bool:
    return bool(STRONG_NEGATION_RE.search(normalized_text))


def vault_blocks(vault_raw: str) -> list[dict]:
    """### headings as candidate vault entry blocks, each tagged with its
    nearest preceding ## ancestor (the macro section — Experience,
    Education, Projects, ...). An orphan ### with no ## ancestor gets
    section "" and never matches any SECTION_ALIASES, by design — no
    scoping guess without the structure to support it. A block's span
    runs from its own heading to the next heading of any level (or EOF),
    so it never bleeds into a sibling entry or the next section."""
    heads = [(m.start(), len(m.group(1)), m.group(2)) for m in HEADING_RE.finditer(vault_raw)]
    blocks = []
    section = ""
    for i, (pos, level, text) in enumerate(heads):
        if level == 2:
            section = normalize(text).strip()
            continue
        if level != 3:
            continue
        end = heads[i + 1][0] if i + 1 < len(heads) else len(vault_raw)
        body = vault_raw[pos:end]
        blocks.append({
            "section": section,
            "heading": normalize(text),
            "haystack": haystack_text(body),
            "excluded_haystack": excluded_haystack_text(body),
            "denied_haystack": denied_haystack_text(body),
            "lines": content_line_pool(body),
        })
    return blocks


def anchor_tokens(entry: dict, fields: tuple[str, ...]) -> list[str]:
    """Significant tokens from an entry's identity fields — same stopword
    filter as the identity check, so "corp"/"university"/... furniture
    can't force a false non-match or a false match either."""
    text = " ".join(str(entry.get(f, "")) for f in fields if entry.get(f))
    return [t for t in re.findall(r"[a-z0-9]{3,}", normalize(text))
            if t not in IDENTITY_STOP]


def heading_tokens(block: dict) -> set[str]:
    """The anchor-comparable tokens of a vault ### heading — the same
    shape anchor_tokens() produces for a resume entry (3+ alnum runs,
    identity furniture dropped), so entry-to-heading matching compares
    whole tokens on both sides instead of testing one string for
    containment inside the other (round 9, finding 1). Computed once
    per block and cached on it: build_entry_scope() re-tests every
    entry against every block in its section."""
    cached = block.get("_heading_tokens")
    if cached is None:
        cached = {t for t in re.findall(r"[a-z0-9]{3,}", block["heading"])
                  if t not in IDENTITY_STOP}
        block["_heading_tokens"] = cached
    return cached


def build_entry_scope(
    data: dict, blocks: list[dict], add
) -> tuple[dict[str, dict | None], set[str]]:
    """entry_key -> its matched vault block, or None if unscoped (no
    anchor, zero matches, or an ambiguous multi-match). Emits one
    entry_unscoped WARN per entry the vault's own structure fails to
    place — but only when that section actually uses the heading
    format; a section with zero ### headings gets no scoping attempt
    and no warning, so an unstructured vault is unaffected. The second
    return value is exactly those entry_unscoped keys — entries scoping
    was ATTEMPTED for and failed — as opposed to keys mapped to None
    because their section was never structured to begin with; callers
    that must not silently let an unscoped entry borrow another
    (currently-claimed) entry's fact need that distinction."""
    scope: dict[str, dict | None] = {}
    unscoped: set[str] = set()
    for section, fields in SCOPED_SECTIONS.items():
        entries = data.get(section)
        if not isinstance(entries, list):
            continue
        aliases = SECTION_ALIASES[section]
        section_blocks = [b for b in blocks
                          if any(a in b["section"] for a in aliases)]
        structured = bool(section_blocks)
        for i, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            ek = f"{section}[{i}]"
            tokens = anchor_tokens(entry, fields)
            # Round 9, finding 1: this used to be a raw SUBSTRING test
            # (`t in b["heading"]`), so a fabricated employer whose name
            # is a substring of a real one — "Ace" inside "SpaceX" —
            # scoped cleanly to that real entry and then validated every
            # one of its achievements. Anchoring is a WHOLE-TOKEN match
            # against the heading's own tokens: "spacex" still matches
            # the heading "spacex — senior engineer" (extra heading
            # tokens are fine, an entry only needs its own covered), but
            # "ace" no longer rides inside "spacex".
            candidates = [b for b in section_blocks
                          if tokens and set(tokens) <= heading_tokens(b)]
            if len(candidates) == 1:
                scope[ek] = candidates[0]
            elif structured:
                scope[ek] = None
                unscoped.add(ek)
                add("entry_unscoped", WARN,
                    f"{ek}: could not be matched to one vault ### entry by "
                    "its org/title (or institution/degree, or name) — the "
                    "vault structures this section, but no single heading's "
                    "tokens cover this entry's; falling back to a "
                    "whole-vault check for its facts, which cannot catch a "
                    "fact swapped in from a different entry")
            else:
                scope[ek] = None
    return scope, unscoped


def content_words(normalized_text: str) -> set[str]:
    """Letter-led tokens (3+ chars, digits allowed after the first letter
    — "p99", "q4" count) with connective furniture stripped — what
    "meaning" means for the claim/vault-line overlap test: a conservative,
    cheap stand-in that never tries to parse grammar or synonyms, only
    whether two lines are plausibly about the same thing. Allowing
    trailing digits matters: a distinctive identifier like "p99" is
    exactly the kind of specific, non-generic token that marks two lines
    as the same fact, and excluding it would leave only generic metric
    nouns ("services") to carry that signal — the ones idf weighting
    (below) prices as cheap, common vault furniture rather than trusting
    them at face value."""
    return {t for t in re.findall(r"[a-z][a-z0-9]{2,}", normalized_text)
            if t not in OVERLAP_STOP}


def build_word_df(vault_raw: str) -> tuple[dict[str, int], int]:
    """Document frequency of every content word across the vault's own
    lines — the idf source for weighted_overlap()'s rarity weighting.
    One line = one document, over the WHOLE vault text (every heading,
    FACT bullet, and prose line), not just one block: a word repeating
    across many lines anywhere in the vault ("api", "retail", "clients")
    is vault-wide generic furniture regardless of which entry uses it;
    a word appearing once is what actually distinguishes that one
    fact, wherever it sits. Blank lines are skipped (nothing to weigh);
    everything else counts, including markdown headings — their
    vocabulary rarely collides with a claim under test, and excluding
    them would need a second, redundant pass over the same text for no
    real gain."""
    lines = [line for line in vault_raw.splitlines() if line.strip()]
    df: dict[str, int] = {}
    for line in lines:
        for word in content_words(normalize(line)):
            df[word] = df.get(word, 0) + 1
    return df, len(lines)


def word_weight(word: str, word_df: dict[str, int], n_lines: int) -> float:
    """Smoothed idf: log((N+1)/(df+1)) + 1. The '+1' floor means even a
    word that recurs on every single vault line still counts a little
    (some shared word is always at least weak evidence of a shared
    subject) rather than dropping to zero; a word unique to one line
    scores highest, up to log(N+1)+1 for N vault lines. A word never
    seen in the vault at all (df=0) scores the same as a word seen
    once — both are "as rare as this vault can show", which is the
    right ceiling since df=0 only reaches this function when it is
    still one of the CLAIM's own words being weighed for the
    denominator, never for a word absent from the matched line (it
    could not be in the shared set to begin with)."""
    df = word_df.get(word, 0)
    return math.log((n_lines + 1) / (df + 1)) + 1.0


def weighted_overlap(
    claim_words: set[str], line_words: set[str],
    word_df: dict[str, int], n_lines: int,
) -> float:
    """Weighted LINE coverage: the matched vault line's own content words,
    weighted by rarity (word_weight() — a word this vault repeats
    everywhere scores low, a word unique to this fact scores high),
    that the claim also contains — shared idf weight divided by the
    LINE's total idf weight alone, not the claim's and not the two
    sides' union. 0.0 if either side is empty — nothing to compare, so
    no evidence of a shared subject either way.

    Deliberately asymmetric, and deliberately not a (weighted) Jaccard
    over the union of both sides — two things were tried and measured
    against the calibration table in evals/test_projection.py before
    landing here (numbers below are from that table, not hand math):
      - a plain smaller-side ratio (round 5's version) rewards SHORT
        claims: min() ignores the LINE's extra unshared words
        entirely once the claim is the smaller side, so a short
        fabrication and a legitimately terse rephrasing can land at
        the same ratio by construction, not by design.
      - a SYMMETRIC weighted Jaccard (shared weight over the combined
        union of both sides) fixes that, but breaks the other
        direction: an honest, verbosely-worded paraphrase that adds
        its OWN connective words ("Scaled from 3 services. Brought
        p99 down to 210 ms." for vault line "p99 latency 210 ms
        across 3 services") gets penalized for its extra claim-side
        vocabulary exactly like a fabrication would be — Jaccard
        scored that legitimate case 0.36, indistinguishable from the
        adversarial "2-descriptor pad" bypass's 0.15-0.18 range, too
        close for a safe threshold. Extra words a claim adds beyond
        the line (elaboration, connective phrasing) are not evidence
        of fabrication; extra words a claim is MISSING from the
        line's own distinctive content are.
    Measuring coverage of the LINE alone fixes both: it cannot be
    gamed by claim length (there is no claim-length term in the
    formula at all — round 5's actual defect, the min() reward, is
    structurally gone, not just mitigated), and it does not punish a
    claim for elaborating beyond the line. On the same calibration
    table, line coverage separates every legitimate rephrasing shape
    (synonym swap, reorder, compression, and the verbose paraphrase
    above) from every fabrication shape (the two exact round-6 bypass
    claims, fresh short generic-only variants, and the original
    topic-swap case) with a symmetric ~0.10 margin on each side of
    CLAIM_LINE_OVERLAP_THRESHOLD — see that constant's comment and the
    test file for the full table. claim-side coverage was measured too
    and rejected: it does NOT cleanly separate the classes (one bypass
    claim's claim-coverage measured HIGHER than the legitimate p99
    paraphrase's), so requiring it in addition would either reject
    honest elaboration or add nothing — not applied, per instructions
    not to add complexity that doesn't earn its keep.

    This is still a mechanical tripwire, not a proof of meaning: it
    has no grammar, negation, or synonym awareness. A single
    strategic word swap inside an otherwise-verbatim, longer line
    (e.g. keeping 6 of a 7-word line and only swapping the one word
    that names the metric) still clears any fixed threshold this way
    — no token-overlap metric catches that, which is stated plainly
    rather than papered over, and is exactly why the claim -> source
    pairing section (module docstring, `pairing` entry) exists as a
    non-lexical backstop: a human sees the claim and its source line
    side by side regardless of what this ratio says. A PASS here
    means "no red flag was raised", never "this claim was verified
    true" — only a human confirming the claim against the source can
    do that; a low score means "send this pair to a human", not "this
    is definitely fabricated"."""
    if not claim_words or not line_words:
        return 0.0
    shared = claim_words & line_words
    shared_weight = sum(word_weight(w, word_df, n_lines) for w in shared)
    line_weight = sum(word_weight(w, word_df, n_lines) for w in line_words)
    return shared_weight / line_weight if line_weight > 0 else 0.0


def best_full_support_line(
    nums: set[str], lines: list[str],
    claim_words: set[str] | None = None,
    word_df: dict[str, int] | None = None, n_lines: int = 0,
) -> str | None:
    """The line, among a candidate set of vault lines, containing EVERY
    number in `nums` — the "best supporting vault line" a claim's
    numbers can be checked against for content-word overlap. `lines` may
    be one vault block's lines (own-entry scoping) or the whole vault's
    lines (the pairing table's fallback when no block is matched) — the
    function itself is scope-agnostic. None if no single line covers
    them all (numbers split across lines): skip rather than guess, same
    conservatism as the rest of this script.

    When more than one line fully covers `nums`, the one with the
    highest weighted_overlap() against `claim_words` wins (round 7,
    finding 8/fix 5) rather than whichever happened to come first in
    file order — the exact bug behind a citation's stray "2025" year
    matching a `###` heading ahead of its real Publications FACT line
    (headings are excluded from `lines` upstream by content_line_pool(),
    which closes that specific case outright; this tie-break is the
    general fix for any case with more than one genuine candidate).
    Falls back to plain first-match when no scoring context is given."""
    candidates = [line for line in lines if all(number_in(n, line) for n in nums)]
    if not candidates:
        return None
    if claim_words is None or word_df is None or len(candidates) == 1:
        return candidates[0]
    return max(candidates, key=lambda ln:
               weighted_overlap(claim_words, content_words(ln), word_df, n_lines))


def best_matching_line(
    claim_words: set[str], lines: list[str],
    word_df: dict[str, int], n_lines: int,
) -> tuple[str | None, float]:
    """The single highest-weighted_overlap-scoring line for a claim with
    NO numeric anchor to narrow the search — used by the pairing table
    for qualitative-only claims (round 7, finding 1/3). Unlike
    best_full_support_line(), there is no number-coverage gate here at
    all: nothing in `nums` to require, because there is no `nums`. The
    caller decides what the score means (see TestQualitativeLineOverlap
    in evals/test_projection.py: for a claim with no numeric anchor,
    NO threshold on this score honestly separates a rephrase from a
    fabrication, so it is reported informational-only, never turned
    into a WARN). (None, 0.0) if `lines` is empty or `claim_words` is
    empty — nothing to compare, same convention as weighted_overlap()."""
    if not claim_words or not lines:
        return None, 0.0
    best_line, best_score = None, -1.0
    for line in lines:
        line_words = content_words(line)
        if not line_words:
            continue
        score = weighted_overlap(claim_words, line_words, word_df, n_lines)
        if score > best_score:
            best_line, best_score = line, score
    return best_line, (best_score if best_line is not None else 0.0)


# Round 8, finding 3a: the old `[a-z][a-z0-9]{1,}` required 2+ alnum
# chars, so a single-letter language name ("R", "C") tokenized to
# NOTHING, and a symbol-suffixed name ("C++", "C#", "F#") lost its
# distinguishing suffix entirely and ALSO tokenized to nothing (the
# bare first letter has no second alnum char to pair with, since the
# next char is "+"/"#", not [a-z0-9]) — skill_supported()'s "if not
# tokens: return True" then auto-passed all five with zero vault
# support, on a vault that never mentioned any of them. The fix: allow
# a token to be a single letter, and let it absorb a trailing run of
# "+"/"#" so "c++"/"c#"/"f#" tokenize as themselves, not as a bare "c"
# that would then vacuously match inside an unrelated "C++" mention
# (see the boundary fix below).
# A LEADING "." is part of the token too (round 9, finding 2): ".NET"
# must tokenize as ".net", not as a bare "net" that then verifies off an
# unrelated vault mention of "net revenue". The dot is optional, so
# every other name tokenizes exactly as before.
SKILL_TOKEN_RE = re.compile(r"\.?[a-z][a-z0-9]*[+#]*")
# Separators inside one skill/coursework string that genuinely list
# SEPARATE items ("PostgreSQL / Redis / MySQL", "pytest, tox"). Each
# side is verified on its own — see skill_support_status()'s per-line
# co-occurrence rule for why the split matters.
# A SPACED dash separates clauses ("School of EECS — discussed with
# Prof. Lin"); an unspaced one is part of a compound word
# ("trace-driven") and must never split.
SKILL_ITEM_SPLIT_RE = re.compile(r"\s*[/,;|]\s*|\s+\band\b\s+|\s+-\s+")
# Boundary characters for a skill token match: alnum as usual, PLUS "+"
# and "#" — without this, a bare "c" would satisfy its right-boundary
# lookahead by landing right before the "+" in an unrelated vault
# mention of "C++" ("+" is not in [a-z0-9], so a plain alnum-only
# boundary would wrongly call that a word edge). Treating +/# as
# word-constituent closes that specific false-positive while still
# treating a space, comma, or period as a real boundary.
SKILL_BOUND = r"[a-z0-9+#]"


def skill_tokens(item_text: str) -> list[str]:
    """Significant word tokens of a skill/tag/tool string (shorter than
    content_words()'s 3+ floor — tech vocabulary is full of short
    acronyms and single-letter names: "ML", "AI", "SQL", "R", "C"),
    connective furniture (OVERLAP_STOP) dropped. Read-only reuse of
    OVERLAP_STOP — this function does not feed content_words()/
    weighted_overlap(), so it cannot disturb that calibration. Round 8,
    finding 3a: every token this regex can produce is non-empty by
    construction (SKILL_TOKEN_RE requires at least one letter); the
    empty-RESULT case (below, in skill_support_status()) is now only
    a genuinely blank or pure-stopword entry, never a language name
    the old regex happened to be too strict to see."""
    return [t for t in SKILL_TOKEN_RE.findall(normalize(item_text))
            if t not in OVERLAP_STOP]


def _skill_token_present(token: str, haystack: str) -> bool:
    """Boundary-matched literal presence of one skill token — "SQL"
    must not ride on the vault's different token "NoSQL", and (round 8,
    finding 3a) a bare "c" must not ride on the vault's different token
    "c++" either, hence SKILL_BOUND treating +/# as word-constituent
    alongside alnum (see SKILL_TOKEN_RE's comment above).

    Round 9, finding 2: a dot is word-constituent on the LEFT for an
    undotted token, so "net" can no longer match inside the vault's
    different token ".net". A token that itself starts with a dot keeps
    the looser left boundary (letters allowed) so it still matches where
    such names really appear — "asp.net", "node.js"."""
    left = r"(?<![0-9+#])" if token.startswith(".") else rf"(?<![a-z0-9+#.])"
    return bool(re.search(
        rf"{left}{re.escape(token)}(?!{SKILL_BOUND})", haystack))


def _sub_items(item_text: str) -> list[str]:
    """One skill string split into the separate items it actually lists
    ("PostgreSQL / Redis / MySQL" -> three). Each is verified on its own
    so a compound entry is not held to a single-line co-occurrence rule
    that a real vault would never satisfy, while a genuinely multi-word
    single item ("Operating Systems") still is."""
    parts = [p for p in SKILL_ITEM_SPLIT_RE.split(normalize(item_text)) if p.strip()]
    return parts or [normalize(item_text)]


def _sub_item_on_some_line(tokens: list[str], lines: list[str]) -> bool:
    """True when ONE line carries every token of one sub-item. Round 9,
    finding 2: the old test asked only whether each token appeared
    SOMEWHERE in the whole flattened vault, so "Operating Systems"
    verified off an "operating" in one unrelated line and a "systems" in
    another. Co-occurrence on a single line is the cheapest honest
    stand-in for "the vault actually says this thing"."""
    return any(all(_skill_token_present(t, line) for t in tokens)
               for line in lines)


def skill_support_status(item_text: str, clean_lines: list[str],
                         cut_lines: list[str] = (),
                         denied_lines: list[str] = ()) -> str:
    """'supported' / 'cut_only' / 'denied' / 'unsupported' for an atomic
    skill/tool/course entry (round 7, finding 1b/2; round 8, findings
    3a/3b) — "Kubernetes", "RAG pipelines", "PostgreSQL / Redis /
    MySQL", a coursework item. A skill is not a sentence: there is no
    leftover wording for a weighted-overlap tripwire to compare a
    legitimate variant against a fabrication with, so presence is the
    test — but presence of EVERY significant token, not the whole
    phrase verbatim-and-contiguous. An earlier version of this function
    required the exact phrase in order; measured against this repo's
    own real vault/resume pair (the zero-false-positive calibration
    target — see the module docstring), that was too strict: compound
    entries ("PostgreSQL / Redis / MySQL") and parenthetical
    elaboration ("ANN (HNSW / IVFFlat)") are common, and a real vault
    legitimately records the same tools in different order,
    punctuation, or a different sentence entirely, without the fact
    being any less true. Token-set presence is the honest fail-closed
    bar that survives that: it still catches a skill with NO trace
    anywhere in the vault (every one of its tokens absent), while not
    false-failing a real skill recorded in different words or order.

    Round 8, finding 3a: an entry with NO checkable token (blank, or
    every word a connective stopword) can never silently pass — that
    used to be the exact hole a single-letter/symbol language name fell
    through; a genuinely empty entry is `unsupported` now, not a free
    pass, and validate_yaml.py already rejects a truly blank list item
    upstream, so this only ever fires on a pure-stopword string here.

    Round 9, finding 2, replacing round 8's single `excluded_only`
    tier. Support is now judged against LINES, not one flattened
    whole-vault string, and lands in one of three non-passing tiers:

      `denied`      the vault affirmatively says not to claim this —
                    a NOT-CLAIMABLE / PENDING-EVIDENCE marker, or a
                    prose denial ("no production Kubernetes
                    experience"). A FAIL, not a warning: round 8's
                    WARN meant an explicit "do not claim this" still
                    exited 0.
      `cut_only`    the only trace is a CUT: line — dropped material,
                    usually still true. A labeled WARN.
      `unsupported` no trace anywhere. A FAIL.

    The line-level rule is what stops a multi-word item being assembled
    out of unrelated lines ("Operating Systems" from an "operating"
    here and a "systems" there); _sub_items() keeps that from
    false-failing genuinely compound entries."""
    subs = [(s, skill_tokens(s)) for s in _sub_items(item_text)]
    subs = [(s, t) for s, t in subs if t]
    if not subs:
        return "unsupported"
    unmet = [(s, t) for s, t in subs
             if not _sub_item_on_some_line(t, clean_lines)]
    if not unmet:
        return "supported"
    # Escalating tiers for whatever is still unmet, worst first: a
    # sub-item the vault DENIES (or marks not-claimable / pending) is a
    # hard failure, not a warning — round 9, finding 2. One that only
    # shows up on a CUT: line is real-but-dropped material: warn.
    if any(_sub_item_on_some_line(t, denied_lines) for _, t in unmet):
        return "denied"
    if all(_sub_item_on_some_line(t, clean_lines + cut_lines)
           for _, t in unmet):
        return "cut_only"
    return "unsupported"


def lines_covering_any(nums: set[str], lines: list[str]) -> list[str]:
    """One representative line per number in `nums` (the first line in
    `lines` that contains it), deduplicated in first-seen order — used
    by the claim -> source pairing section when no SINGLE line covers
    every number in a claim, so the report still shows the human
    something rather than an empty source list. Not a claim of "these
    lines together are the one true fact"; just the best mechanical
    pointer available when best_full_support_line() finds nothing.

    `nums` is iterated in sorted order regardless of whether the caller
    passed a set — a plain `for n in some_set` would iterate in
    Python's per-process hash order, which is randomized by default
    (PYTHONHASHSEED), making an example report's checked-in output
    non-reproducible from one run to the next for no reason connected
    to the vault or the claim."""
    out: list[str] = []
    seen: set[str] = set()
    for n in sorted(nums):
        for line in lines:
            if number_in(n, line) and line not in seen:
                out.append(line)
                seen.add(line)
                break
    return out


def token_present(needle: str, haystack: str) -> bool:
    """Whole-token presence of a normalized phrase in a normalized
    haystack — the identity/contact counterpart to number_in()'s digit
    boundaries. A raw `needle in haystack` is what let the fabricated
    employer "Ace" verify off the vault's real "SpaceX" (round 9,
    finding 1); requiring an alphanumeric boundary on both sides keeps
    "spacex propulsion" matching inside a longer heading while refusing
    a match that starts or ends mid-word."""
    if not needle:
        return False
    return bool(re.search(rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])",
                          haystack))


# Characters that can be interior to a single email / phone / handle
# token. The exact-contact boundary must reject a match that starts or
# ends in the MIDDLE of such a token: `casey@example.com` must not
# verify off the vault's different address `sam.casey@example.com` (the
# char before "casey" there is ".", an email-local-part character), and
# a phone fragment must not ride inside a longer number.
CONTACT_TOKEN_CHAR = r"[a-z0-9.@+_%#-]"


def contact_exact_present(needle: str, haystack: str) -> bool:
    """Whole-token presence of an email/phone string — stricter than
    token_present(): the boundary treats `.`/`@`/`+`/`-`/`_`/`%`/`#` as
    part of the surrounding token, so a match cannot begin or end inside
    a longer contiguous address or number (round-2 review finding 2).
    `sam.casey@example.com` no longer supports the different reply
    address `casey@example.com`."""
    if not needle:
        return False
    return bool(re.search(
        rf"(?<!{CONTACT_TOKEN_CHAR}){re.escape(needle)}(?!{CONTACT_TOKEN_CHAR})",
        haystack))


# Unambiguous metric-direction verbs, for the polarity tripwire (round-2
# review finding 4). "improved"/"optimized"/"changed" are DELIBERATELY
# absent — improving latency means lowering it but improving revenue
# means raising it, so they carry no fixed polarity and would false-flag.
DIRECTION_UP = {
    "increased", "increase", "raised", "raise", "grew", "grown", "grow",
    "boosted", "boost", "rose", "risen", "gained", "gain", "higher",
    "doubled", "tripled", "quadrupled", "up", "expanded", "expand",
    "more", "added",
}
DIRECTION_DOWN = {
    "reduced", "reduce", "cut", "decreased", "decrease", "lowered",
    "lower", "dropped", "drop", "shrank", "shrunk", "shrink", "fell",
    "fallen", "slashed", "slash", "trimmed", "trim", "halved", "down",
    "fewer", "less", "minimized", "minimize",
}


def direction_polarity(normalized_text: str) -> str | None:
    """'up' / 'down' / None for a claim or vault line, by its
    unambiguous direction verbs (DIRECTION_UP / DIRECTION_DOWN). None
    when the text has no such verb, or has BOTH polarities (a mixed
    sentence — "grew signups after cutting latency" — where no single
    direction is THE claim); either way there is nothing to compare."""
    words = set(re.findall(r"[a-z]+", normalized_text))
    up = bool(words & DIRECTION_UP)
    down = bool(words & DIRECTION_DOWN)
    if up and not down:
        return "up"
    if down and not up:
        return "down"
    return None


def novel_words(claim_words: set[str], word_df: dict[str, int]) -> list[str]:
    """Claim content words with document frequency 0 across the whole
    vault — vocabulary the vault has never used anywhere, in any entry.
    Sorted for a stable, reproducible report line. See
    NOVEL_WORD_AUDIT_FLOOR for why this is a manual-audit tripwire and
    not a verdict."""
    return sorted(w for w in claim_words if not word_df.get(w))


def full(text: str) -> str:
    """A claim or vault line, whitespace-collapsed but NEVER truncated.
    Round 9, finding 3: every human-facing comparison the report asks a
    reader to make used excerpt()'s 70-character cut on BOTH sides, so
    the promised manual audit could not actually see the part of a claim
    that diverged from its source — which is exactly the part that
    diverges last, after a shared opening clause. Anything a human is
    asked to compare goes through this; excerpt() is for labels only."""
    return " ".join(text.split())


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

    # haystack: the coarse whole-vault presence surface (round 8,
    # finding 3b: exclusion-marked lines removed — see
    # haystack_text()'s docstring). excluded_haystack is its mirror —
    # every exclusion-marked line's own text — so a token found ONLY
    # there can be told apart from a token absent everywhere.
    haystack = haystack_text(vault_raw)
    excluded_haystack = excluded_haystack_text(vault_raw)
    # Denied-only sub-surface (NOT-CLAIMABLE / PENDING-EVIDENCE / prose
    # denial / Gaps & flags): support found ONLY here is a FAIL for
    # numbers, dates, and URLs too, not just skills — round-2 review
    # finding 1. `excluded_haystack` (denied + cut) still backs the
    # weaker cut-only WARN.
    denied_haystack = denied_haystack_text(vault_raw)
    # The skills check runs on lines, not the flattened haystack, and
    # separates denied (FAIL) from merely-cut (WARN) — see
    # skill_support_status()/line_surfaces().
    skill_clean_lines, skill_cut_lines, skill_denied_lines = \
        line_surfaces(vault_raw)
    denied_vault_lines = denied_line_pool(vault_raw)
    # Ownership-scoped identity surface (round-3 review finding 2): the
    # candidate's own `## Basics` block, not the whole vault. Falls back
    # to the whole clean surface only when the vault has no Basics
    # heading, so an unstructured vault degrades rather than false-fails.
    basics = basics_lines(vault_raw)
    contact_pool = basics if basics else skill_clean_lines
    contact_flat = " ".join(" ".join(contact_pool).split())
    vault_emails = set(EMAIL_RE.findall(contact_flat))
    vault_phones = {re.sub(r"\D", "", run)
                    for run in PHONE_RUN_RE.findall(contact_flat)}
    vault_phones = {d for d in vault_phones if len(d) >= 7}
    # idf source for weighted_overlap() — computed once, over the whole
    # vault, and reused by both the claim_semantic_mismatch WARN check
    # and the claim -> source pairing section below.
    word_df, word_df_n = build_word_df(vault_raw)
    # Unwrapped (soft-wrap-joined), furniture- and exclusion-filtered
    # (no headings, no "Updated:" metadata, no NOT-CLAIMABLE/
    # PENDING-EVIDENCE line — see content_line_pool()). This is the
    # whole-vault candidate pool for every line-level match the pairing
    # table falls back to when no block is matched; block-scoped pools
    # get the identical treatment inside vault_blocks() itself.
    all_vault_lines = content_line_pool(vault_raw)
    # The excluded-marker mirror of all_vault_lines — never a match
    # candidate, only ever shown as the source of an excluded_only WARN
    # (round 8, finding 3b).
    excluded_vault_lines = excluded_line_pool(vault_raw)

    found = {"dates": [], "urls": [], "content": [], "identity": [],
             "other": [], "skills": [], "contact": [], "unchecked": []}
    collect(data, "", found)

    checks: list[dict] = []

    def add(check_id: str, level: str, detail: str) -> None:
        checks.append({"check_id": check_id, "level": level, "detail": detail})

    # ── schema field-coverage guard (round 8, finding 4/systemic) ─────
    # Every DISTINCT unrecognized key gets one WARN (not one per
    # occurrence — a field used across five experience entries is one
    # drift event, not five), naming an example path so it's findable.
    seen_unchecked: dict[str, str] = {}
    for key, p in found["unchecked"]:
        seen_unchecked.setdefault(key, p)
    for key, p in seen_unchecked.items():
        add("unchecked_field", WARN,
            f"schema field '{key}' (e.g. at {p}) is not classified by any "
            "check in this script — it only gets the generic numeric-only "
            "sweep. If this is a genuinely new schema field, teach "
            "check_projection.py its check bucket (see the field-coverage "
            "registry next to SKILL_KEYS) so a real fact in it cannot ride "
            "through unchecked; if it is already reviewed and intended to "
            "stay numeric-only, add it to NUMERIC_SWEEP_ONLY_KEYS instead "
            "of leaving it to fall through unlabeled")

    blocks = vault_blocks(vault_raw)
    entry_scope, unscoped_entries = build_entry_scope(data, blocks, add)
    # Blocks a SIBLING entry in THIS projection is actually matched to —
    # what an unscoped entry (no own block) may never silently borrow a
    # whole claim from (see the number loop below). Deliberately not
    # every ### block the vault happens to contain: an unscoped entry's
    # own real fact often sits under a block nobody in this run claims
    # either (an honest rename not yet reconciled — that block is not
    # "someone else's", it just isn't anchored to this entry YET), and
    # flagging that as a swap would be exactly the false-fail on a
    # legitimate rephrasing round 1 was rejected for risking. A fact
    # provably belonging to a DIFFERENT job that's actually listed
    # alongside it in the same projection is the strong, low-noise
    # signal; a bare "some heading somewhere in a big vault happens to
    # mention these numbers" is not.
    other_entry_blocks = [b for b in entry_scope.values() if b is not None]

    # ── numbers: every string value outside meta.* ───────────────────
    # Own entry's vault block first when one is matched (entry_scope);
    # missing there but present elsewhere in the vault is misattribution
    # (the swapped-fact class), not a plain miss.
    # found["skills"] (SKILL_KEYS: `stack`, the skills-group `items`) is
    # included here too (round 7 regression fix): moving these out of
    # CONTENT_KEYS so skill_supported() could fail-closed-check them
    # accidentally dropped them from this numeric sweep at the same
    # time, since SKILL_TOKEN_RE only matches letter-led words — a
    # digit substring in a skill string ("AWS (7 years)", "Python
    # 3.99") was invisible to skill_supported() AND absent from the
    # numeric sweep, a silent regression on exactly the fact class
    # finding 1 was about. Skill strings get both checks now: atomic
    # word-token presence (below) and numeric-token presence (here).
    n_tokens = 0
    n_clean = True
    for path, text, entry_key in found["content"] + found["other"] + found["skills"]:
        if entry_key in unscoped_entries:
            continue  # handled below, at claim granularity, not per-token
        norm = normalize(text)
        block = entry_scope.get(entry_key)
        for token in re.findall(r"\d+(?:\.\d+)?", norm):
            n_tokens += 1
            if block is not None and number_in(token, block["haystack"]):
                continue
            if number_in(token, haystack):
                if block is not None:
                    n_clean = False
                    add("number_misattributed", FAIL,
                        f"'{token}' at {path} is not supported by its own "
                        f"vault entry ({block['heading']!r}) — it appears "
                        "elsewhere in the vault; check for a swapped or "
                        f"misattributed fact — \"{excerpt(text, token)}\"")
                continue
            # Round 8, finding 3b: not found in the clean surface (own
            # block or global) — before calling this a plain absence,
            # check whether it exists ONLY inside a vault line the vault
            # itself marks excluded (NOT-CLAIMABLE/PENDING-EVIDENCE).
            # That is a materially different signal from "no trace at
            # all": the vault is actively saying not to claim this, or
            # that it isn't confirmed yet — surfaced as its own labeled
            # WARN, never silently folded into "unsupported" and never
            # a silent pass either.
            if number_in(token, denied_haystack) or (
                block is not None and number_in(token, block["denied_haystack"])
            ):
                # Round-2 review finding 1: DENIED-only support (a
                # NOT-CLAIMABLE/PENDING-EVIDENCE line, a prose denial,
                # or a Gaps & flags line) is a FAIL, not the round-8
                # WARN that let a disproven number ship at exit 0.
                n_clean = False
                add("number_denied", FAIL,
                    f"'{token}' at {path} appears in the vault ONLY on a "
                    "line that says not to claim it (NOT-CLAIMABLE / "
                    "PENDING-EVIDENCE, a prose denial, or the Gaps & flags "
                    "ledger) — that is counter-evidence, not support; "
                    "remove the claim, or confirm it with the user and "
                    f"record the confirmation in the vault — "
                    f"\"{excerpt(text, token)}\"")
            elif number_in(token, excluded_haystack) or (
                block is not None and number_in(token, block["excluded_haystack"])
            ):
                # Cut-only support (a CUT: line): weaker — dropped
                # material, usually still true. WARN, confirm before use.
                n_clean = False
                add("number_cut_only", WARN,
                    f"'{token}' at {path} traces only to a CUT: line "
                    "(material dropped from an earlier resume) — confirm "
                    "it still holds before claiming it — "
                    f"\"{excerpt(text, token)}\"")
            else:
                n_clean = False
                add("number_unsupported", FAIL,
                    f"'{token}' at {path} has no vault support — "
                    f"\"{excerpt(text, token)}\"")

    # An entry scoping was ATTEMPTED for but couldn't place
    # (unscoped_entries) may not silently borrow a DIFFERENT vault
    # entry's fact either — but the decision is made per CLAIM (string),
    # not per lone token: a realistic vault reuses small common numbers
    # (single digits, years, percents) across unrelated entries
    # constantly, so one coincidental digit landing in some other block
    # is not the swapped-fact signal — only one OTHER entry's block
    # covering EVERY number the claim states is. That mirrors "the whole
    # fact moved to the wrong heading", the actual failure mode round-5's
    # and this round's tests plant; a lone shared digit is exactly the
    # noise the round-1 semantic heuristic was rejected for chasing.
    for path, text, entry_key in found["content"] + found["other"] + found["skills"]:
        if entry_key not in unscoped_entries:
            continue
        norm = normalize(text)
        nums = re.findall(r"\d+(?:\.\d+)?", norm)
        n_tokens += len(nums)
        if not nums:
            continue
        present = []
        for token in nums:
            if number_in(token, haystack):
                present.append(token)
                continue
            # Round-2 review finding 1: denied-only is a FAIL, cut-only a
            # WARN — same split as the scoped loop above, unscoped
            # entries included.
            if number_in(token, denied_haystack):
                n_clean = False
                add("number_denied", FAIL,
                    f"'{token}' at {path} appears in the vault ONLY on a "
                    "line that says not to claim it (NOT-CLAIMABLE / "
                    "PENDING-EVIDENCE / prose denial / Gaps & flags) — "
                    "counter-evidence, not support; remove it or confirm "
                    f"and record it in the vault — \"{excerpt(text, token)}\"")
                continue
            if number_in(token, excluded_haystack):
                n_clean = False
                add("number_cut_only", WARN,
                    f"'{token}' at {path} traces only to a CUT: line — "
                    "confirm it still holds before claiming it — "
                    f"\"{excerpt(text, token)}\"")
                continue
            n_clean = False
            add("number_unsupported", FAIL,
                f"'{token}' at {path} has no vault support — "
                f"\"{excerpt(text, token)}\"")
        if not present:
            continue
        other = next(
            (b for b in other_entry_blocks
             if all(number_in(t, b["haystack"]) for t in present)),
            None)
        if other is not None:
            n_clean = False
            add("number_misattributed", FAIL,
                f"{path} ({entry_key} could not be matched to its own "
                f"vault entry) is fully supported by {other['heading']!r}, "
                "a DIFFERENT vault entry — an unmatched entry may not "
                f"borrow another employer's fact — \"{excerpt(text)}\"")
        else:
            n_clean = False
            for token in present:
                add("number_unanchored_support", WARN,
                    f"'{token}' at {path} ({entry_key} could not be "
                    "matched to its own vault entry) has vault support "
                    "only outside any entry matched this run — cannot "
                    "confirm it belongs to this entry; needs manual "
                    f"audit — \"{excerpt(text, token)}\"")
    if n_clean:
        add("numbers", PASS, f"{n_tokens} numeric token(s) verified against the vault")

    # ── claim/vault-line overlap: presence is not meaning ─────────────
    # A claim's numbers can verify cleanly above yet still be about a
    # different achievement than the vault line that happens to hold the
    # same numbers ("raised revenue 40% across 3 regions" verified by
    # "reduced latency 40% across 3 services" — same two numbers, nothing
    # else shared). Only checked within an entry's OWN matched block (an
    # honest rephrasing of that entry's own fact keeps a high share of
    # its WEIGHTED content words in common; a topic swap keeps the score
    # low even when it pads itself with a couple of the vault line's own
    # generic descriptors — see weighted_overlap()) — deliberately NOT
    # the ordered-pair-style heuristic round 1 rejected: this never
    # fails a claim, it only asks a human to look, and only when the
    # overlap score is at or below the bar. A mechanical tripwire, not
    # proof of meaning: it cannot see grammar, negation, or synonyms,
    # and a crafted claim can always clear the bar (or the vault can
    # just be edited) — see weighted_overlap()'s docstring.
    for path, text, entry_key in found["content"]:
        block = entry_scope.get(entry_key)
        if block is None:
            continue
        norm = normalize(text)
        nums = set(re.findall(r"\d+(?:\.\d+)?", norm))
        if not nums:
            continue
        if not all(number_in(n, block["haystack"]) for n in nums):
            continue  # a number already FAILed above; not double-reported
        line = best_full_support_line(nums, block["lines"])
        if line is None:
            # Every number is individually present somewhere in the block,
            # but no SINGLE line covers all of them — the claim's numbers
            # verify only when combined across ≥2 separate vault facts.
            # That is exactly the "presence, not meaning" gap this check
            # exists to close: a claim built by picking one number from one
            # real fact and another from a different real fact in the same
            # entry would otherwise sail through with no signal at all.
            # Never FAIL here — a legitimate claim can coincidentally share
            # a number with an unrelated line in the same block, the same
            # conservatism as claim_semantic_mismatch below.
            add("claim_numbers_span_multiple_facts", WARN,
                f"{path}: numbers check out, but no single vault line in "
                f"{block['heading']!r} covers all of them — they verify "
                "only when combined across separate facts; confirm this "
                f"claim is one real achievement, not a stitched-together "
                f"one — claim: \"{excerpt(text)}\"")
            continue
        claim_words = content_words(norm)
        line_words = content_words(line)
        # Round-2 review finding 4: same metric, same numbers, OPPOSITE
        # direction — "Increased API latency 40%" against the vault's
        # "cut API latency 40%". The word overlap is high (both share
        # "api"/"latency") and there's no from/to pair for the
        # metric_direction check to catch, so this sailed through clean.
        # A polarity conflict between the claim and its own matched vault
        # line is a WARN: honest paraphrases keep the direction, and a
        # flipped one inverts the achievement's meaning entirely.
        c_pol = direction_polarity(norm)
        l_pol = direction_polarity(normalize(line))
        if c_pol and l_pol and c_pol != l_pol:
            add("claim_direction_conflict", WARN,
                f"{path}: the claim says the metric went {c_pol.upper()} but "
                f"its matching vault line says {l_pol.upper()} — same numbers, "
                "opposite direction; confirm this is not a reversed "
                f"improvement — claim: \"{full(text)}\" | vault: \"{full(line)}\"")
        # Round-3 review finding 3: the claim asserts a WORSE outcome
        # ("Worsened API latency 40%") its matching vault line does not
        # ("cut API latency 40%"). A resume claims improvements; a
        # worsening verb here is almost always a reversed metric.
        elif asserts_worse_outcome(norm, claim_words) and not \
                asserts_worse_outcome(normalize(line), content_words(normalize(line))):
            bad = ", ".join(sorted(claim_words & NEGATIVE_OUTCOME)) or "made … worse"
            add("claim_direction_conflict", WARN,
                f"{path}: the claim asserts a WORSENED outcome ({bad}) that "
                "its matching vault line does not — a resume states "
                "improvements; confirm this is not a reversed metric — "
                f"claim: \"{full(text)}\" | vault: \"{full(line)}\"")
        ratio = weighted_overlap(claim_words, line_words, word_df, word_df_n)
        if claim_words and ratio <= CLAIM_LINE_OVERLAP_THRESHOLD:
            add("claim_semantic_mismatch", WARN,
                f"{path}: numbers check out, but this claim's content "
                f"words overlap too little with its only matching line in "
                f"{block['heading']!r} (weighted overlap {ratio:.2f}, need "
                f"> {CLAIM_LINE_OVERLAP_THRESHOLD:.2f}) "
                f"— confirm it is the same achievement, not a coincidental "
                f"number match (a couple of shared descriptors — a metric's "
                f"unit noun, a domain word — is not enough on its own; this "
                f"is a mechanical tripwire for manual audit, not proof "
                f"either way) — "
                f"claim: \"{full(text)}\" | vault: \"{full(line)}\"")
            continue
        # Round 9, finding 3: the claim covers this line's own words
        # (that is what ratio measures — see weighted_overlap()) but
        # brings vocabulary the vault has never used ANYWHERE. A claim
        # that repeats the line's opening clause and its numbers, then
        # states a different outcome, lands exactly here and used to
        # pass clean. WARN only: an honest, heavily-reworded bullet can
        # reach this too, so it is a prompt to compare by eye, not a
        # verdict.
        novel = novel_words(claim_words, word_df)
        if (len(novel) >= NOVEL_WORD_AUDIT_FLOOR and claim_words
                and len(novel) / len(claim_words) > NOVEL_WORD_AUDIT_SHARE):
            add("claim_novel_wording", WARN,
                f"{path}: numbers and wording both track the vault line, "
                f"but {len(novel)} of this claim's {len(claim_words)} "
                f"content words appear nowhere in the vault at all: "
                f"{', '.join(novel)} — confirm the claim "
                "says what the vault says (a claim can repeat a line's "
                "opening clause and its numbers, then assert a different "
                "outcome, and still score a clean overlap) — "
                f"claim: \"{full(text)}\" | vault: \"{full(line)}\"")

    # ── metric direction: resume markers vs the vault's own markers ──
    # Scoped to the entry's own block's lines when one is matched, the
    # whole vault otherwise — a same-but-reversed marker sitting under a
    # DIFFERENT entry must not verify this entry's claim. Reuses the
    # same unwrapped, furniture-filtered whole-vault pool as everything
    # else — a directional marker never legitimately sits in a heading.
    vault_lines = all_vault_lines
    pairs = []
    for path, text, entry_key in found["content"]:
        for x, y in directional_pairs(normalize(text)):
            if number_in(x, haystack) and number_in(y, haystack):
                pairs.append((path, text, x, y, entry_key))  # presence misses FAILed above
    n_verified = n_manual = 0
    for path, text, x, y, entry_key in pairs:
        block = entry_scope.get(entry_key)
        search_lines = block["lines"] if block is not None else vault_lines
        vault_marked: set[tuple[str, str]] = set()
        for line in search_lines:
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
    # Own entry's vault block first when matched; found only elsewhere in
    # the vault is misattribution (a date belonging to a different entry),
    # not a plain miss — same split as numbers, above.
    n_dates = 0
    d_clean = True
    ongoing: list[str] = []
    for path, value, entry_key in found["dates"]:
        if value is None:
            continue
        block = entry_scope.get(entry_key)
        if hasattr(value, "year") and hasattr(value, "month"):  # yaml date
            y, m = value.year, value.month
        else:
            text = str(value).strip()
            if text.casefold() in PRESENT_WORDS:
                ongoing.append(path)
                continue
            if re.fullmatch(r"\d{4}", text):
                n_dates += 1
                if block is not None and re.search(
                        rf"(?<!\d){text}(?!\d)", block["haystack"]):
                    continue
                if re.search(rf"(?<!\d){text}(?!\d)", haystack):
                    if block is not None:
                        d_clean = False
                        add("date_misattributed", FAIL,
                            f"{path}: year {text} is not supported by its "
                            f"own vault entry ({block['heading']!r}) — it "
                            "appears elsewhere in the vault; check for a "
                            "swapped date")
                    continue
                # Round-2 review finding 1 — denied-only is a FAIL, same
                # split as the numbers loop above; cut-only stays a WARN.
                if re.search(rf"(?<!\d){text}(?!\d)", denied_haystack) or (
                    block is not None and re.search(
                        rf"(?<!\d){text}(?!\d)", block["denied_haystack"])
                ):
                    d_clean = False
                    add("date_denied", FAIL,
                        f"{path}: year {text} appears in the vault ONLY on a "
                        "line that says not to claim it (NOT-CLAIMABLE / "
                        "PENDING-EVIDENCE / prose denial / Gaps & flags) — "
                        "counter-evidence, not support; remove it or confirm "
                        "and record it in the vault")
                elif re.search(rf"(?<!\d){text}(?!\d)", excluded_haystack) or (
                    block is not None and re.search(
                        rf"(?<!\d){text}(?!\d)", block["excluded_haystack"])
                ):
                    d_clean = False
                    add("date_cut_only", WARN,
                        f"{path}: year {text} traces only to a CUT: line — "
                        "confirm it still holds before claiming it")
                else:
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
        cands = date_candidates(y, m)
        if block is not None and any(c in block["haystack"] for c in cands):
            continue
        if any(c in haystack for c in cands):
            if block is not None:
                d_clean = False
                add("date_misattributed", FAIL,
                    f"{path}: {y}-{m:02d} is not supported by its own vault "
                    f"entry ({block['heading']!r}) — it appears elsewhere in "
                    "the vault; check for a swapped date")
            continue
        # Round-2 review finding 1 — denied-only is a FAIL; cut-only WARN.
        if any(c in denied_haystack for c in cands) or (
            block is not None and any(c in block["denied_haystack"] for c in cands)
        ):
            d_clean = False
            add("date_denied", FAIL,
                f"{path}: {y}-{m:02d} appears in the vault ONLY on a line "
                "that says not to claim it (NOT-CLAIMABLE / PENDING-EVIDENCE "
                "/ prose denial / Gaps & flags) — counter-evidence, not "
                "support; remove it or confirm and record it in the vault")
            continue
        if any(c in excluded_haystack for c in cands) or (
            block is not None and any(c in block["excluded_haystack"] for c in cands)
        ):
            d_clean = False
            add("date_cut_only", WARN,
                f"{path}: {y}-{m:02d} traces only to a CUT: line — confirm "
                "it still holds before claiming it")
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
    if ongoing:
        add("ongoing_roles", WARN,
            f"{len(ongoing)} entry(ies) claim an ongoing role: "
            f"{', '.join(ongoing)} — 'present' has no vault-verifiable end "
            "date; confirm each role is still current (an ended role "
            "projected as ongoing is fabrication this check cannot see)")
    if d_clean:
        add("dates", PASS, f"{n_dates} date(s) verified against the vault")

    # ── urls: url fields + URLs pasted into content strings ──────────
    # Own entry's vault block first when matched; same misattributed split.
    url_items = list(found["urls"])
    for path, text, entry_key in found["content"]:
        for tok in re.findall(r"(?:https?://|www\.)\S+", text):
            url_items.append((path, tok, entry_key))
    u_clean = True
    for path, url, entry_key in url_items:
        u = normalize_url(url)
        block = entry_scope.get(entry_key)
        # LEFT boundary too (round-3 review finding 2): without it,
        # "hub.com/samcasey" matched inside the vault's different host
        # "github.com/samcasey" (git‑HUB…). A host/domain char before
        # the match means it starts mid-token — not a real match.
        # Right boundary unchanged: /user must not ride on /username,
        # but a deeper path (/user/repo) still supports /user.
        pattern = r"(?<![\w.\-])" + re.escape(u) + r"(?![\w-])"
        # Round-5 review finding 1: a `basics.links[].url` is the
        # candidate's OWN profile link — its CLEAN support must be in
        # `## Basics`, like name/email/phone; a link found in the clean
        # vault only OUTSIDE Basics (a colleague's profile in a
        # Q&A/Context line) is a misattribution. This narrows only the
        # clean-support scope; the denied/cut cascade below is unchanged,
        # so a Basics link on a NOT-CLAIMABLE line still fails url_denied,
        # not url_unsupported. Other urls (projects/publications) keep the
        # whole-vault scope.
        is_basics_link = path.startswith("basics") and bool(contact_pool)
        if is_basics_link:
            if re.search(pattern, contact_flat):
                continue
            if re.search(pattern, haystack):
                u_clean = False
                add("url_misattributed", FAIL,
                    f"{path}: {url} (normalized '{u}') is a Basics profile "
                    "link but appears in the clean vault only OUTSIDE Basics "
                    "(a colleague's link in a Q&A/Context line is not yours) "
                    "— record your own profile URL in the vault's Basics")
                continue
            # fall through to the denied/cut/unsupported cascade below
        if block is not None and re.search(pattern, block["haystack"]):
            continue
        if not is_basics_link and re.search(pattern, haystack):
            if block is not None:
                u_clean = False
                add("url_misattributed", FAIL,
                    f"{path}: {url} (normalized '{u}') is not supported by "
                    f"its own vault entry ({block['heading']!r}) — it "
                    "appears elsewhere in the vault; check for a swapped "
                    "or misattributed link")
            continue
        # Round-2 review finding 1 — denied-only is a FAIL; cut-only WARN.
        if re.search(pattern, denied_haystack) or (
            block is not None and re.search(pattern, block["denied_haystack"])
        ):
            u_clean = False
            add("url_denied", FAIL,
                f"{path}: {url} (normalized '{u}') appears in the vault "
                "ONLY on a line that says not to claim it (NOT-CLAIMABLE / "
                "PENDING-EVIDENCE / prose denial / Gaps & flags) — "
                "counter-evidence, not support; remove it or confirm and "
                "record it in the vault")
        elif re.search(pattern, excluded_haystack) or (
            block is not None and re.search(pattern, block["excluded_haystack"])
        ):
            u_clean = False
            add("url_cut_only", WARN,
                f"{path}: {url} (normalized '{u}') traces only to a CUT: "
                "line — confirm it still holds before claiming it")
        else:
            u_clean = False
            add("url_unsupported", FAIL,
                f"{path}: {url} (normalized '{u}') has no vault support")
    if u_clean:
        add("urls", PASS, f"{len(url_items)} url(s) verified against the vault")

    # ── identity: drift WARNs, fabrication FAILs, drifted numbers FAIL ─
    i_clean = True
    for path, value, entry_key in found["identity"]:
        needle = " ".join(normalize(value).split())
        # Round-5 review finding 1: the candidate's own `name`
        # (basics.name specifically) is an OWNERSHIP field like
        # email/phone/location — it must appear in the vault's
        # `## Basics`, not anywhere in the vault. Without this, a
        # manager's name mentioned only in a Q&A/Context line verified
        # the candidate's name field. Only basics.name is scoped:
        # projects[].name, awards[].name, and org/title/institution/
        # degree legitimately live in their own sections, so they still
        # match the whole vault.
        is_own_name = path == "basics.name" and contact_pool
        own_scope = contact_flat if is_own_name else haystack
        # Round 9, finding 1: both tests here were raw substring tests,
        # the same defect as entry scoping — a fabricated "Ace" counted
        # as verbatim-present because it sits inside the vault's real
        # "SpaceX", so an invented employer was reported as a matched
        # identity field. Both are whole-token matches now.
        if not needle or token_present(needle, own_scope):
            continue  # verbatim in the vault: supported by definition
        i_clean = False
        tokens = [t for t in re.findall(r"[a-z0-9]{3,}", needle)
                  if t not in IDENTITY_STOP]
        if tokens and not any(token_present(t, own_scope) for t in tokens):
            add("identity_unsupported", FAIL,
                f"{path}: '{value}' shares no token with the vault — the "
                "fabrication class, not the rename class. If this is a "
                "real rename/alias, record it in the vault first (with "
                "the user's confirmation); projections never contain an "
                "identity the vault lacks")
        else:
            add("identity_drift", WARN,
                f"{path}: '{value}' not found verbatim in the vault — "
                f"fine if it's a rename/reformat, worth a look if not")
        for token in re.findall(r"\d+(?:\.\d+)?", needle):
            if not number_in(token, own_scope):
                add("number_unsupported", FAIL,
                    f"'{token}' at {path} has no vault support — "
                    f"\"{excerpt(value, token)}\" (rewording must not "
                    f"introduce numbers the vault lacks)")
    if i_clean:
        add("identity", PASS,
            f"{len(found['identity'])} name/org/title field(s) matched")

    # ── contact / personal facts: fail-closed (round 9, finding 1) ────
    # email, phone, location, education field-of-study. These were
    # numeric-sweep-only — checked for stray digits and nothing else —
    # so a wrong reply address or an invented field of study passed
    # clean. See CONTACT_KEYS for why each gets the bar it gets.
    c_clean = True
    for path, value, entry_key in found["contact"]:
        key = _leaf_key(path)
        needle = " ".join(normalize(value).split())
        if not needle:
            continue
        if key == "email":
            # Ownership + exact: the candidate's own Basics email set,
            # by whole address, so a colleague's email mentioned
            # elsewhere in the vault can't stand in (round-3 finding 2).
            if needle in vault_emails:
                continue
            c_clean = False
            add("contact_unsupported", FAIL,
                f"{path}: email '{value}' is not the address on file in the "
                "vault's Basics. A wrong reply address loses the "
                "application silently, and a colleague's address elsewhere "
                "in the vault is not the candidate's — record the correct "
                "one in Basics")
            continue
        if key == "phone":
            if phone_supported(re.sub(r"\D", "", needle), vault_phones):
                continue
            c_clean = False
            add("contact_unsupported", FAIL,
                f"{path}: phone '{value}' does not match the complete number "
                "in the vault's Basics (a partial or wrong number has no "
                "'close enough') — record the correct one in Basics")
            continue
        if key == "location":
            # One fact, own block, every token (state abbreviations
            # INCLUDED — "OR"/"ME"/"IN" are not stopwords here) on ONE
            # Basics line, so "Portland, OR" can't pass off "Portland,
            # ME" (round-3 review finding 2).
            toks = re.findall(r"[a-z0-9]+", needle)
            if toks and any(
                    all(_skill_token_present(t, line) for t in toks)
                    for line in contact_pool):
                continue
            c_clean = False
            add("contact_unsupported", FAIL,
                f"{path}: location '{value}' has no vault support — no single "
                "Basics line carries all of it (a wrong city or "
                "state/country can affect eligibility). Record it in Basics")
            continue
        # `field` (education field of study): one fact, every token on a
        # single vault line — the whole-vault clean surface, since it is
        # not an ownership-scoped identity field the way contact is.
        if _sub_item_on_some_line(skill_tokens(needle), skill_clean_lines):
            continue
        c_clean = False
        add("contact_unsupported", FAIL,
            f"{path}: '{value}' has no vault support — no single vault "
            "line carries all of it. Confirm it with the user and record "
            "it in the vault; projections never contain a personal fact "
            "the vault lacks")
    if c_clean and found["contact"]:
        add("contact", PASS,
            f"{len(found['contact'])} contact/personal field(s) verified "
            "against the vault")

    # ── skills: atomic tokens, fail-closed against the whole vault ────
    # Round 7, finding 1b/2: a skill string ("Kubernetes") carries no
    # digits, so it never touched the numeric sweep above, and it isn't
    # a sentence, so the claim-overlap machinery doesn't apply either —
    # it was invisible end to end. Skills (SKILL_KEYS: `stack`,
    # `coursework`, the skills-group `items`) get their own check
    # instead of being folded into either: normalized whole-vault
    # presence (skill_support_status()), fail-closed. Whole-vault, not
    # per-entry scoped — a tool used across roles is not "misattributed"
    # the way a swapped metric is, and the top-level `skills:` groups
    # have no entry to scope against in the first place.
    s_clean = True
    for path, item, entry_key in found["skills"]:
        status = skill_support_status(
            item, skill_clean_lines, skill_cut_lines, skill_denied_lines)
        if status == "supported":
            continue
        s_clean = False
        if status == "denied":
            # Round 9, finding 2: the vault affirmatively says not to
            # claim this — an explicit NOT-CLAIMABLE / PENDING-EVIDENCE
            # marker, or a prose denial ("no production Kubernetes
            # experience"). Round 8 made this a WARN, so the single
            # loudest thing a vault can say about a claim still exited
            # 0. It is a FAIL.
            add("skill_denied", FAIL,
                f"{path}: '{item}' appears in the vault ONLY on a line "
                "that says not to claim it (NOT-CLAIMABLE / "
                "PENDING-EVIDENCE, or an explicit denial such as \"no "
                "production X experience\") — that is counter-evidence, "
                "not support; remove the claim, or confirm it with the "
                "user and record the confirmation in the vault")
        elif status == "cut_only":
            # Only trace is a CUT: line — real material dropped from an
            # earlier resume, so usually true but never re-verified.
            add("skill_cut_only", WARN,
                f"{path}: '{item}' traces only to a CUT: line (material "
                "dropped from an earlier resume) — confirm it still "
                "holds before claiming it, or record it as a FACT")
        else:
            add("skill_unsupported", FAIL,
                f"{path}: '{item}' has no vault support — add it to the "
                "vault with evidence, or remove it from the projection")
    if s_clean:
        add("skills", PASS,
            f"{len(found['skills'])} skill token(s) verified against the vault")

    # ── claim vs vault denial / negation (round-3 review, findings 1/3) ─
    # Runs for EVERY content claim, numbered or not — the qualitative
    # path below only ever reports "info", so a claim that repeats a
    # NOT-CLAIMABLE line ("led the company-wide migration…") slipped
    # through with no signal and was even paired with an unrelated clean
    # line, hiding the very line that forbids it. Two fail-closed checks:
    #   claim_denied — the claim strongly matches a DENIED vault line
    #     (NOT-CLAIMABLE / PENDING-EVIDENCE / prose denial / Gaps &
    #     flags). The vault is saying "don't claim this"; the claim
    #     claims it anyway.
    #   claim_negation_dropped — the claim strongly matches a CLEAN vault
    #     line, but that line carries a meaning-flipping negation the
    #     claim has DROPPED ("never reduced latency 40%" -> "Reduced
    #     latency 40%"). Detecting the DROP, not the mere presence of a
    #     negator, is what keeps an honest claim that KEEPS the negation
    #     ("…is a signal, never an automated verdict") from false-failing.
    for path, text, entry_key in found["content"]:
        norm = normalize(text)
        claim_words = content_words(norm)
        if not claim_words:
            continue
        dline, dscore = best_matching_line(
            claim_words, denied_vault_lines, word_df, word_df_n)
        if dline is not None and dscore >= CLAIM_LINE_OVERLAP_THRESHOLD:
            add("claim_denied", FAIL,
                f"{path}: this claim restates a vault line the vault itself "
                "marks unusable (NOT-CLAIMABLE / PENDING-EVIDENCE / denial / "
                "Gaps & flags) — that is the vault saying do not claim it; "
                "remove it, or confirm with the user and record the "
                f"confirmation in the vault — claim: \"{full(text)}\" | "
                f"denied vault line: \"{full(dline)}\"")
            continue
        # Negation-drop: the claim restates a vault line but drops a
        # meaning-flipping negation the line carries. The claim itself
        # must NOT be negated (an honest claim that KEEPS the "never"
        # stays clean). Two anchors, whichever finds a negated source:
        #   - NUMBER-anchored (round-5 fix): a vault line that shares
        #     every one of the claim's numbers and carries a negation the
        #     claim lacks. Numbers + negation is a strong combined signal,
        #     so this fires without a lexical-overlap floor — a dropped
        #     "zero reduction … 55%" scores only ~0.4 on words alone
        #     ("reduced" ≠ "reduction") yet is unmistakable on the number.
        #   - LEXICALLY-anchored: for a claim with no numbers, the best
        #     content-word match, gated at the usual 0.5 bar.
        if not has_negation(norm):
            nums = set(re.findall(r"\d+(?:\.\d+)?", norm))
            neg_line = None
            if nums:
                neg_line = next(
                    (ln for ln in all_vault_lines
                     if all(number_in(n, ln) for n in nums)
                     and has_strong_negation(normalize(ln))
                     and len(content_words(normalize(ln)) & claim_words) >= 2), None)
            if neg_line is None:
                cline, cscore = best_matching_line(
                    claim_words, all_vault_lines, word_df, word_df_n)
                if (cline is not None and cscore >= CLAIM_LINE_OVERLAP_THRESHOLD
                        and has_strong_negation(normalize(cline))):
                    neg_line = cline
            if neg_line is not None:
                add("claim_negation_dropped", FAIL,
                    f"{path}: this claim's own matching vault line NEGATES "
                    "what the claim asserts, and the claim dropped the "
                    "negation (\"never …\", \"no reduction …\", \"did not "
                    "…\") — that inverts the fact; keep the vault's wording "
                    f"or remove the claim — claim: \"{full(text)}\" | vault: "
                    f"\"{full(neg_line)}\"")

    # ── claim -> source pairing: mandatory, always-emitted visibility ─
    # Every content claim (content strings only — same scope as the
    # overlap check above), paired with the exact vault line(s) that
    # support it, or its FAIL/manual-audit/informational status and why
    # when no single line does. This is NOT another lexical tripwire: it
    # adds no new FAIL, changes no verdict or exit code — it only makes
    # every claim's provenance visible, including the ones the WARN
    # checks above don't reach (an unscoped entry, a section the vault
    # never structured at all with ### headings, or a claim with no
    # number to anchor a lexical check to in the first place). No
    # content claim's source is ever invisible in this report, even
    # where token overlap alone cannot tell a synonym swap from a
    # fabrication — see the module docstring's `pairing` entry for why
    # this exists alongside, not instead of, the WARN checks.
    # ROUND 7 (finding 1a): a claim with no numbers used to `continue`
    # right here — no row, no signal, invisible. Every content claim now
    # gets a row: the branch below on `not nums` is the qualitative path
    # (best-scoring line, always "info" — see qualitative_row() and
    # TestQualitativeLineOverlap in evals/test_projection.py for why no
    # WARN threshold is honest there); everything after it is the
    # original numeric-anchored path, unchanged in its FAIL/WARN/PASS
    # logic, except the never-scoped fallback's level is now "info" too
    # (finding 8/fix 5 — "pass" is reserved for a claim this script
    # actually mechanically confirmed).
    def qualitative_row(row: dict, claim_words: set[str], lines: list[str],
                        scope_note: str) -> dict:
        """Fill in a pairing row for a claim with no numeric anchor —
        always "info": TestQualitativeLineOverlap's calibration table
        shows a legitimate paraphrase and an outright fabrication land
        in the same, overlapping score range once there is no number to
        narrow the candidate-line search, so no threshold here would be
        honest. The row still always shows the best-matching line (or
        says plainly that none shares any content word), so a human
        sees exactly what the mechanism found — never nothing."""
        line, score = best_matching_line(claim_words, lines, word_df, word_df_n)
        row["level"] = INFO
        if line is not None:
            row["sources"] = [line]
            row["detail"] = (
                f"weighted overlap {score:.2f} ({scope_note}; no numeric "
                "anchor to check presence against, and no wording-overlap "
                "threshold honestly separates a rephrase from a "
                "fabrication with none — informational only, read this "
                "pairing by eye)")
        else:
            row["sources"] = []
            row["detail"] = (
                f"no vault line shares any content word with this claim "
                f"({scope_note}) — informational only, read this pairing "
                "by eye")
        return row

    pairings: list[dict] = []
    for path, text, entry_key in found["content"]:
        norm = normalize(text)
        nums = set(re.findall(r"\d+(?:\.\d+)?", norm))
        claim_words = content_words(norm)
        block = entry_scope.get(entry_key)
        # Round 9, finding 3: the claim is stored in FULL here. It used
        # to be excerpt()'d to 70 characters before it ever reached the
        # report, so neither the JSON consumer nor a human reading the
        # CLI could perform the claim-vs-source comparison this table
        # exists to make possible.
        row = {"path": path, "entry": entry_key, "claim": full(text),
               "level": PASS, "sources": [], "detail": ""}

        if not nums:
            if not claim_words:
                row["level"] = INFO
                row["detail"] = "no content words to compare — informational only"
            elif block is not None:
                qualitative_row(row, claim_words, block["lines"],
                                f"matched to {block['heading']!r}")
            else:
                qualitative_row(row, claim_words, all_vault_lines,
                                "whole-vault match, not entry-scoped")
            pairings.append(row)
            continue

        missing = sorted(n for n in nums if not number_in(n, haystack))
        if missing:
            # Round 8, findings 3b/8: a number missing from the clean
            # surface is a plain FAIL only if it is missing from the
            # excluded surface too — one found ONLY inside a vault line
            # marked NOT-CLAIMABLE/PENDING-EVIDENCE must surface as a
            # labeled WARN here as well, never the silent "pass" this
            # row would otherwise have gotten once the raw haystack (pre
            # round-8) still counted that line as ordinary support, and
            # never double-counted as an unqualified FAIL either.
            # Round-2 review finding 1: a number found ONLY on a denied
            # line is a FAIL here too (the check-level number_denied
            # already fails the verdict); only a cut-only number is the
            # WARN this row used to always emit.
            denied_only = [n for n in missing
                           if denied_haystack and number_in(n, denied_haystack)]
            truly_unsupported = [
                n for n in missing
                if not (excluded_haystack and number_in(n, excluded_haystack))]
            if truly_unsupported or denied_only:
                row["level"] = FAIL
                bad = sorted(set(truly_unsupported) | set(denied_only))
                row["sources"] = lines_covering_any(set(denied_only), excluded_vault_lines)
                row["detail"] = (
                    f"no usable vault support for {', '.join(bad)} "
                    "(unsupported, or found only on a NOT-CLAIMABLE / "
                    "denied line) — see number_unsupported / number_denied "
                    "above")
            else:
                row["level"] = WARN
                row["sources"] = lines_covering_any(set(missing), excluded_vault_lines)
                row["detail"] = (
                    f"{', '.join(missing)} traces only to a CUT: line — "
                    "confirm this claim independently or remove it (see "
                    "number_cut_only above)")
            pairings.append(row)
            continue

        if block is not None:
            misattributed = sorted(
                n for n in nums if not number_in(n, block["haystack"]))
            if misattributed:
                row["level"] = FAIL
                row["sources"] = lines_covering_any(set(misattributed), all_vault_lines)
                row["detail"] = (
                    f"{', '.join(misattributed)} supported elsewhere in the "
                    f"vault, not in this entry's own block "
                    f"({block['heading']!r}) — see number_misattributed above")
                pairings.append(row)
                continue
            line = best_full_support_line(nums, block["lines"], claim_words,
                                          word_df, word_df_n)
            if line is not None:
                line_words = content_words(line)
                ratio = weighted_overlap(claim_words, line_words, word_df, word_df_n)
                row["sources"] = [line]
                if claim_words and ratio <= CLAIM_LINE_OVERLAP_THRESHOLD:
                    row["level"] = WARN
                    row["detail"] = (
                        f"weighted overlap {ratio:.2f} — confirm same "
                        "achievement, not a coincidental number match "
                        "(see claim_semantic_mismatch above if flagged)")
                else:
                    row["level"] = PASS
                    row["detail"] = f"weighted overlap {ratio:.2f}"
            else:
                row["level"] = WARN
                row["sources"] = lines_covering_any(nums, block["lines"])
                row["detail"] = (
                    "numbers verify only combined across separate vault "
                    f"lines in {block['heading']!r} (see "
                    "claim_numbers_span_multiple_facts above if flagged)")
            pairings.append(row)
            continue

        if entry_key in unscoped_entries:
            other = next(
                (b for b in other_entry_blocks
                 if all(number_in(n, b["haystack"]) for n in nums)), None)
            if other is not None:
                row["level"] = FAIL
                line = best_full_support_line(nums, other["lines"], claim_words,
                                              word_df, word_df_n)
                row["sources"] = [line] if line else lines_covering_any(nums, other["lines"])
                row["detail"] = (
                    f"fully supported by a DIFFERENT vault entry "
                    f"({other['heading']!r}) — see number_misattributed above")
                pairings.append(row)
                continue
            row["level"] = WARN
            line = best_full_support_line(nums, all_vault_lines, claim_words,
                                          word_df, word_df_n)
            row["sources"] = [line] if line else lines_covering_any(nums, all_vault_lines)
            row["detail"] = (
                "entry could not be matched to its own vault heading — "
                "support found outside any matched entry; needs manual "
                "audit (see number_unanchored_support above if flagged)")
            pairings.append(row)
            continue

        # Never scoped at all: no SCOPED_SECTIONS entry (basics.summary is
        # the real, templated case in all three .typ templates), or the
        # section has no ### structure to scope against — the whole-vault
        # fallback. This does NOT get "the same conservatism as everywhere
        # else" (an earlier version of this comment claimed that; it had
        # never actually been measured against this branch's own
        # conditions, and does not hold up under test — see
        # evals/test_projection.py's fallback-pairing-calibration tests).
        # weighted_overlap() here is scored against word_df built over the
        # WHOLE vault (every heading, contact line, and unrelated section's
        # FACT), not one coherent entry's own lines the way the scoped path
        # (above) uses — and that changes what the ratio means. A short,
        # frame-shaped claim ("led a team of N X shipping M Y per period")
        # has almost nothing but generic frame words as its "content
        # words", so a legitimate synonym-swapped rephrase and a
        # fabricated verb+object swap on the exact same vault line can
        # score IDENTICALLY (both keep exactly the frame words the other
        # side's verb swap didn't touch): measured, an honest paraphrase
        # ("Directed a squad of 8 engineers launching 4 releases per
        # quarter" against vault "led a team of 8 engineers shipping 4
        # releases per quarter") scores ~0.47, and a fabricated
        # verb+object swap on that SAME line ("Trained a squad of 8
        # engineers auditing 4 releases per quarter") also scores ~0.47 —
        # with a different fabrication shape ("Fired a team of 8 engineers
        # rejecting 4 releases per quarter") scoring HIGHER, ~0.61, than
        # that same honest paraphrase. No threshold separates the classes
        # here; a mechanical ratio without a coherent, single-entry
        # comparison set proves even less than the scoped path's already-
        # modest tripwire. So this branch never raises a flag: every claim
        # here is still listed (visibility never regresses — module
        # docstring's `pairing` entry), its ratio is still printed for a
        # human to read, and the row's level is "info" (round 7, finding
        # 8/fix 5 — "pass" is reserved for a mechanically-confirmed claim;
        # this branch never confirms anything, so labeling it "pass" was
        # itself the misleading part) — never counted toward
        # claim_pairings_manual_audit or the verdict line's manual-audit
        # count either, same as before. The pairing table — read and
        # attested to, pairing by pairing, by the builder per SKILL.md —
        # is the actual guarantee on this path; a ratio it cannot honestly
        # threshold would only add false confidence, not signal.
        line = best_full_support_line(nums, all_vault_lines, claim_words,
                                      word_df, word_df_n)
        row["level"] = INFO
        if line is not None:
            line_words = content_words(line)
            ratio = weighted_overlap(claim_words, line_words, word_df, word_df_n)
            row["sources"] = [line]
            row["detail"] = (
                f"weighted overlap {ratio:.2f} (whole-vault match, not "
                "entry-scoped; informational only — this path has no "
                "honest threshold, see the pairing loop's comment in "
                "check_projection.py — read this pairing by eye)")
        else:
            row["sources"] = lines_covering_any(nums, all_vault_lines)
            row["detail"] = (
                "numbers present in the vault but no single line covers "
                "all of them (whole-vault match, not entry-scoped; "
                "informational only — read this pairing by eye)")
        pairings.append(row)

    # ── report (evaluator verdict/checks[] contract) ─────────────────
    failed = any(c["level"] == FAIL for c in checks)
    manual_audit_claims = sum(
        1 for c in checks if c["check_id"] in MANUAL_AUDIT_CHECK_IDS)
    if manual_audit_claims:
        notes.append(
            f"manual audit: {manual_audit_claims} claim(s) need human "
            "review — their numeric tokens check out against the vault, "
            "but this script proves token presence, not meaning; see the "
            "claim_semantic_mismatch / number_unanchored_support / "
            "claim_numbers_span_multiple_facts check(s) above")
    n_pairings = len(pairings)
    n_pairings_fail = sum(1 for r in pairings if r["level"] == FAIL)
    n_pairings_manual = sum(1 for r in pairings if r["level"] == WARN)
    n_pairings_info = sum(1 for r in pairings if r["level"] == INFO)
    n_pairings_pass = sum(1 for r in pairings if r["level"] == PASS)
    # Round 8, finding 8: the old verdict line counted ONLY
    # claim_pairings_manual_audit (warn-level pairings) toward "needs
    # manual audit" — but SKILL.md's own builder contract says read
    # EVERY row, info included ("the informational (info) and
    # qualitative rows included, not only the ones marked warn"), and
    # an info row is exactly as mechanically-unconfirmed as a warn row
    # (see qualitative_row()/the never-scoped-fallback comment above:
    # "info" means "nothing was mechanically flagged, and nothing was
    # confirmed either"). A claim whose only source turned out to be an
    # excluded vault line (round 8, finding 3b) now lands here as a
    # warn row too, not a silent pass — so folding info into this count
    # closes finding 8's own repro at the same time: "0 need manual
    # audit" can now only print when both are genuinely zero.
    # claim_pairings_manual_audit itself is UNCHANGED (still warn-only)
    # — an existing test (test_projection.py) depends on that exact
    # narrower count staying warn-only; claim_pairings_needs_audit below
    # is the new, honest, warn+info total the verdict line reports.
    n_pairings_needs_audit = n_pairings_manual + n_pairings_info
    report = {
        "layer": "projection",
        "file": str(args.resume),
        "vault": str(args.vault),
        "verdict": FAIL if failed else PASS,
        "checks": checks,
        "notes": notes,
        "claim_pairings": pairings,
        "metrics": {"numbers_checked": n_tokens, "dates_checked": n_dates,
                    "urls_checked": len(url_items),
                    "identity_checked": len(found["identity"]),
                    "skills_checked": len(found["skills"]),
                    "metric_pairs_checked": len(pairs),
                    "manual_audit_claims": manual_audit_claims,
                    "claim_pairings_checked": n_pairings,
                    "claim_pairings_pass": n_pairings_pass,
                    "claim_pairings_manual_audit": n_pairings_manual,
                    "claim_pairings_info": n_pairings_info,
                    "claim_pairings_fail": n_pairings_fail,
                    "claim_pairings_needs_audit": n_pairings_needs_audit},
    }
    if args.as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        icon = {PASS: "ok", WARN: "!!", FAIL: "XX", INFO: "--"}
        print(f"[projection] {args.resume.name} ⇄ {args.vault.name}")
        for c in checks:
            print(f"  {icon[c['level']]}  {c['check_id']}: {c['detail']}")
        for note in notes:
            print(f"  note  {note}")
        # Mandatory, always-printed — every content claim (numeric AND
        # qualitative — see the pairing loop's own comment above) next
        # to its vault source, so a claim the lexical checks above miss
        # is still visible here for a human to compare by eye. n_pairings
        # counts every CONTENT_KEYS claim listed below, not just the
        # numeric ones — a qualitative claim or a whole-section tags
        # citation with zero digits still gets its own "info" row.
        print(f"  claim -> source pairings ({n_pairings} claim(s)):")
        if not pairings:
            print("    (no content claims found in this projection)")
        for row in pairings:
            print(f"    {icon[row['level']]}  {row['path']}: "
                  f"\"{row['claim']}\"")
            if row["sources"]:
                for src in row["sources"]:
                    print(f"        <- \"{full(src)}\"")
            else:
                print("        <- (no supporting vault line)")
            print(f"        {row['detail']}")
        # Always qualified, never a bare PASS/FAIL: the pairing section
        # above is the guarantee (every content claim's source is
        # visible), so the verdict line always says so and always
        # states how many of those pairings still need a human — a
        # human never has to notice the qualifier was silently dropped
        # because this run happened to have zero manual-audit claims.
        # Round 8, finding 8: the old line reported only the warn count
        # (n_pairings_manual), understating what SKILL.md's own builder
        # contract asks for — every row must be read, pass included, and
        # only warn+info are genuinely unconfirmed. The full pass/warn/
        # info breakdown is now always printed, and "0 need manual
        # audit" can only appear when n_pairings_manual and
        # n_pairings_info are BOTH actually zero.
        verdict_line = "FAIL" if failed else "PASS"
        verdict_line += (
            f" — token-level support only; {n_pairings} claim-source "
            f"pairing(s) listed for review ({n_pairings_pass} pass, "
            f"{n_pairings_manual} warn, {n_pairings_info} info) — every "
            "row must be read per the builder contract (SKILL.md), pass "
            f"rows included; {n_pairings_needs_audit} need manual audit")
        print(f"  => {verdict_line}")

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
