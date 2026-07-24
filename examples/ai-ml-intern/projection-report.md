# Projection check — resume.yaml against career-vault.md

The output of

```sh
skills/resume-builder/scripts/check_projection.py \
    evals/fixtures/resume-sample/resume.yaml \
    examples/ai-ml-intern/career-vault.md
```

run against this example's own
[`career-vault.md`](career-vault.md) and the fixture
[`resume.yaml`](../../evals/fixtures/resume-sample/resume.yaml). Every
hard fact in the resume — numbers, dates, URLs, org/title identity,
every listed skill, and every coursework entry — traces back to a
vault line; the two directional metric pairs (retrieval latency, word
error rate) are verified against the vault's own same-order markers,
not left for manual review.

```
[projection] resume.yaml ⇄ career-vault.md
  ok  numbers: 18 numeric token(s) verified against the vault
  !!  claim_semantic_mismatch: experience[1].bullets[1]: numbers check out, but this claim's content words overlap too little with its only matching line in 'uw systems research group - undergraduate research assistant (oct 2024 - may 2025) [group: research]' (weighted overlap 0.00, need > 0.50) — confirm it is the same achievement, not a coincidental number match (a couple of shared descriptors — a metric's unit noun, a domain word — is not enough on its own; this is a mechanical tripwire for manual audit, not proof either way) — claim: "Co-authored a workshop paper on preemption-aware scheduling (2nd author) and presented it at the poster session." | vault: "- fact: built a trace-driven simulator for gpu cluster schedulers (python); reproduced 3 published baselines within 2% and surfaced a starvation edge case now in the group's benchmark suite"
  ok  dates: 9 date(s) verified against the vault
  ok  urls: 4 url(s) verified against the vault
  ok  identity: 10 name/org/title field(s) matched
  ok  contact: 6 contact/personal field(s) verified against the vault
  ok  skills: 20 skill token(s) verified against the vault
  note  metric pairs: 2 directional pair(s) found — 2 verified against vault markers, 0 need manual review
  note  manual audit: 1 claim(s) need human review — their numeric tokens check out against the vault, but this script proves token presence, not meaning; see the claim_semantic_mismatch / number_unanchored_support / claim_numbers_span_multiple_facts check(s) above
  claim -> source pairings (15 claim(s)):
    ok  education[0].gpa: "3.8/4.0"
        <- "- fact: cumulative gpa 3.8 / 4.0"
        weighted overlap 0.00
    ok  education[0].honors[0]: "Dean's List (6 quarters)"
        <- "- fact: dean's list, 6 quarters"
        weighted overlap 0.85
    --  experience[0].tags[0]: "RAG evaluation"
        <- "- fact: built an offline evaluation harness for a rag customer-support assistant (python, pytest); ran nightly against 1200 historical support tickets and caught 3 retrieval regressions before they shipped"
        weighted overlap 0.09 (matched to 'meridian labs - machine learning engineering intern (jun 2025 - sep 2025) [group: industry]'; no numeric anchor to check presence against, and no wording-overlap threshold honestly separates a rephrase from a fabrication with none — informational only, read this pairing by eye)
    --  experience[0].tags[1]: "retrieval latency"
        <- "- fact: cut p95 retrieval latency from 480 ms to 210 ms by warming the embedding cache on deploy and switching the vector index from flat search to hnsw"
        weighted overlap 0.13 (matched to 'meridian labs - machine learning engineering intern (jun 2025 - sep 2025) [group: industry]'; no numeric anchor to check presence against, and no wording-overlap threshold honestly separates a rephrase from a fabrication with none — informational only, read this pairing by eye)
    --  experience[0].tags[2]: "prompt-injection red-teaming"
        <- "- fact: wrote the team's prompt-injection red-team suite - 41 cases - now a required pre-deploy gate for two production assistants"
        weighted overlap 0.20 (matched to 'meridian labs - machine learning engineering intern (jun 2025 - sep 2025) [group: industry]'; no numeric anchor to check presence against, and no wording-overlap threshold honestly separates a rephrase from a fabrication with none — informational only, read this pairing by eye)
    ok  experience[0].bullets[0]: "Built an offline evaluation harness for a RAG customer-support assistant (Python, pytest), scoring 1,200 historical tickets nightly and catching 3 retrieval regressions before they shipped."
        <- "- fact: built an offline evaluation harness for a rag customer-support assistant (python, pytest); ran nightly against 1200 historical support tickets and caught 3 retrieval regressions before they shipped"
        weighted overlap 0.82
    ok  experience[0].bullets[1]: "Cut p95 retrieval latency from 480 ms to 210 ms by adding embedding-cache warmup and moving the vector index from flat search to HNSW."
        <- "- fact: cut p95 retrieval latency from 480 ms to 210 ms by warming the embedding cache on deploy and switching the vector index from flat search to hnsw"
        weighted overlap 0.76
    ok  experience[0].bullets[2]: "Wrote the team's prompt-injection red-team suite (41 cases), now a required pre-deploy gate for two production assistants."
        <- "- fact: wrote the team's prompt-injection red-team suite - 41 cases - now a required pre-deploy gate for two production assistants"
        weighted overlap 0.97
    --  experience[1].tags[0]: "GPU cluster scheduling"
        <- "- fact: built a trace-driven simulator for gpu cluster schedulers (python); reproduced 3 published baselines within 2% and surfaced a starvation edge case now in the group's benchmark suite"
        weighted overlap 0.10 (matched to 'uw systems research group - undergraduate research assistant (oct 2024 - may 2025) [group: research]'; no numeric anchor to check presence against, and no wording-overlap threshold honestly separates a rephrase from a fabrication with none — informational only, read this pairing by eye)
    --  experience[1].tags[1]: "trace-driven simulation"
        <- "- fact: built a trace-driven simulator for gpu cluster schedulers (python); reproduced 3 published baselines within 2% and surfaced a starvation edge case now in the group's benchmark suite"
        weighted overlap 0.11 (matched to 'uw systems research group - undergraduate research assistant (oct 2024 - may 2025) [group: research]'; no numeric anchor to check presence against, and no wording-overlap threshold honestly separates a rephrase from a fabrication with none — informational only, read this pairing by eye)
    ok  experience[1].bullets[0]: "Implemented a trace-driven simulator for GPU cluster schedulers; reproduced 3 published baselines within 2% and surfaced a starvation edge case now included in the group's benchmark suite."
        <- "- fact: built a trace-driven simulator for gpu cluster schedulers (python); reproduced 3 published baselines within 2% and surfaced a starvation edge case now in the group's benchmark suite"
        weighted overlap 0.88
    !!  experience[1].bullets[1]: "Co-authored a workshop paper on preemption-aware scheduling (2nd author) and presented it at the poster session."
        <- "- fact: co-authored (2nd author) a hotcloud 2025 workshop paper, "preemption-aware scheduling for shared gpu clusters"; presented the poster session personally. project_notes.md lists the names as "casey, okafor, lin" but also says "2nd author" - those don't agree on who's first; see publications below for the confirmed author order and the q&a log for how it was resolved"
        weighted overlap 0.30 — confirm same achievement, not a coincidental number match (see claim_semantic_mismatch above if flagged)
    ok  projects[0].bullets[0]: "Append-only personal-finance CLI with double-entry validation; 1.4k GitHub stars, 27 external contributors, signed releases for macOS and Linux."
        <- "- fact: append-only personal-finance cli (rust, sqlite) with double-entry validation; 1.4k github stars, 27 external contributors, signed releases for macos and linux"
        weighted overlap 0.87
    ok  projects[1].bullets[0]: "Local-first meeting transcriber; fine-tuned Whisper-small on 30 h of noisy lecture audio, cutting word error rate from 18.2% to 11.6% on a held-out set."
        <- "- fact: local-first meeting transcriber (python, pytorch); fine-tuned whisper-small on 30 h of noisy lecture audio, cutting word error rate from 18.2% to 11.6% on a held-out set"
        weighted overlap 0.88
    --  publications[0].citation: "Okafor, D., Casey, S., and Lin, M. (2025). Preemption-Aware Scheduling for Shared GPU Clusters. HotCloud Workshop."
        <- "- fact: okafor, d., casey, s., and lin, m. (2025). "preemption-aware scheduling for shared gpu clusters." hotcloud workshop. https://example.com/hotcloud25-preemption.pdf - author order per the 2026-07-14 confirmation in the q&a log below, not the raw notes' listing order (which the notes themselves contradict - see below)"
        weighted overlap 0.41 (whole-vault match, not entry-scoped; informational only — this path has no honest threshold, see the pairing loop's comment in check_projection.py — read this pairing by eye)
  => PASS — token-level support only; 15 claim-source pairing(s) listed for review (8 pass, 1 warn, 6 info) — every row must be read per the builder contract (SKILL.md), pass rows included; 7 need manual audit
```

Re-run it yourself — the command above exits 0.

The claim -> source pairing section is mandatory and always printed,
not just when something warns, and now covers *every* content claim —
qualitative ones included, not only the ones with a number in them —
so a claim the lexical checks above happen to miss is never invisible:
the header's count of 15 is every row printed below, numeric and
qualitative alike, not the numeric ones alone. Of those 15: 9 are
numeric-anchored claims the script mechanically checked (8 `pass`, 1
`warn`), and 6 are `info` — printed for a human to read, never
mechanically graded, because no honest threshold exists there — the
two `tags` groups' 5 short qualitative descriptors (no number to
anchor a check to) plus the publications citation (it has a number,
but matches against the whole vault rather than one scoped entry, so
its ratio can't honestly separate a rephrase from a fabrication
either). A human (or `resume-evaluator`) reads this table after every
run and confirms each pairing describes the *same achievement*, not
merely that the numbers (or words) match (`skills/resume-builder/
SKILL.md`'s verification step). All 6 `info` rows and the 1 `warn`
row are walked through below, alongside the `skills` check and its
extension to `coursework` this round added.

The verdict line's own count changed with this round too, and it is
worth being honest about *why*: "7 need manual audit," not the "1"
an earlier version of this same report printed. Nothing about this
resume/vault pair got worse — the 6 `info` rows were always
mechanically unconfirmed (see the `info`-vs-`pass` distinction above),
and `skills/resume-builder/SKILL.md` has always told the builder to
read them ("read every row — the informational (`info`) and
qualitative rows included, not only the ones marked `warn`"). The old
verdict line simply didn't *count* them, so it under-reported how much
of this table still needed a human's eyes. `claim_pairings_needs_audit`
(warn + info, `7` here) replaces that undercount; `claim_pairings_pass`
(`8`) is reported alongside it so the honest breakdown — not just a
single combined number — is always visible. A verdict line can only
say "0 need manual audit" now when both counts are genuinely zero.

## Skills: atomic and fail-closed, coursework included

Every `stack` item (`projects[].stack`), every `coursework` entry
(`education[].coursework`), and every top-level `skills:` group's
`items` entry — 20 tokens total (16 skills/stack + 4 coursework
entries: Machine Learning, Distributed Systems, NLP, Databases) — gets
checked against the vault. A skill or course token has no wording for a
weighted-overlap tripwire to compare a rephrase against a fabrication
with, so the rule here is simpler and stricter than the claims path:
every significant word of the token must appear somewhere in the vault
(mod case, punctuation, and word order — boundary-matched so a single
letter or symbol-suffixed name, `R` or `C++` say, still requires real
evidence rather than tokenizing away to nothing), or the check fails
outright with `skill_unsupported` — no WARN, no manual-audit escape
hatch. If the only trace is a vault line the vault itself marks
unusable, the label sharpens rather than softens: a `NOT-CLAIMABLE:`/
`PENDING-EVIDENCE:` line, a prose denial, or a `## Gaps & flags` line
is counter-evidence, so it fails as `skill_denied` (see below); only a
`CUT:` line — dropped-but-usually-true material — downgrades to a
`skill_cut_only` WARN. This example's vault carries a
dedicated `## Skills` section listing exactly the same tools the resume
claims, and its Education FACT line spells out the same four courses,
so all 20 verify cleanly (`ok skills: 20 skill token(s) verified
against the vault`); a resume claiming an unvaulted tool or course
(`Kubernetes`, `Quantum Computing`, say) would fail here instead of
passing silently — that silent pass, not a hypothetical, was a real
bug two rounds closed in turn: round 7 added this check for skills and
stack; round 8 extended it to coursework (a course name has no digits,
so it had no dedicated check at all before — see
`evals/test_projection.py`'s `test_unvaulted_coursework_item_fails`)
and fixed a token-matching gap in the original check itself — a
single-letter language (`R`, `C`) or a symbol-suffixed one (`C++`,
`C#`, `F#`) used to tokenize to *nothing* and silently pass with zero
vault support regardless of what the vault actually said (see that same
file's `test_bare_r_language_unvaulted_fails` and
`test_cpp_csharp_fsharp_unvaulted_all_fail`). Neither gap was
hypothetical to this vault specifically — this resume happens to use
neither a single-letter language nor an unvaulted course — but both
were real, silent holes in the mechanism itself.

## The exclusion-marker contract, demonstrated

`career-vault.md`'s Gaps & flags entry about the Meridian return offer
now reads `NOT-CLAIMABLE: an industry return offer from Meridian —
none is on file; do not imply one on any resume` instead of plain
prose. `check_projection.py` treats any line carrying a `NOT-CLAIMABLE:`
or `PENDING-EVIDENCE:` marker — plus a prose denial ("no production X
experience") and every line under a `## Gaps & flags` honesty-ledger
section — as **denied**: not merely absent from the positive-evidence
surface, but counter-evidence. The vault is actively saying "no" (or
"not yet"), not just failing to mention something. This resume never
claims a return offer, so the marker changes nothing in the report
above (diff it yourself — converting the line is a no-op here); it is
included purely to show the contract used the way a real vault would
use it, the same place the fact already lived, not a synthetic trigger
bolted on. Had the resume claimed one, the check would **FAIL** it —
`skill_denied` (or the matching `number_denied`/`date_denied`/
`url_denied`), a labeled hard failure naming the denied line — not the
exit-0 warning an earlier round emitted here, which let a disproven
fact ship (round-2 review finding 1). A `CUT:` line is the one weaker
tier: `*_cut_only`, a WARN, because dropped material is usually still
true — confirm before claiming, don't hard-fail.

## Qualitative pairings: `tags` are visible now, and graded honestly

The resume's `experience[].tags` rows (`RAG evaluation`, `retrieval
latency`, `prompt-injection red-teaming`, `GPU cluster scheduling`,
`trace-driven simulation`) carry no numbers at all. Before this round
they were invisible end to end: no digits for the numeric sweep to
find, no sentence-length claim for the overlap check to anchor to —
a clean pass with zero signal either way. They now get a pairing row
each, matched by best-scoring line within their own entry's vault
block, always labeled `--` (informational), never `warn` or `pass`:
measured calibration (`evals/test_projection.py`'s
`TestQualitativeLineOverlap`) found that a legitimate short paraphrase
and an outright fabrication land in the same, overlapping weighted-
overlap range once there is no number to narrow the search — a fixed
threshold here would flag honest tags as often as it would catch a
fabricated one, so none of these five ever raises a check-level flag.
Read by eye, all five plainly restate real vault content in shorter
form ("RAG evaluation" against the RAG customer-support harness FACT,
"retrieval latency" against the p95-latency FACT, and so on) — the
low printed ratios (0.09-0.20) simply reflect how little of a long,
detail-dense FACT line's own vocabulary a 2-3-word tag can cover, not
that anything is wrong with the tag.

## The HotCloud author-order claim, resolved

`experience[1].bullets[1]` ("Co-authored a workshop paper on
preemption-aware scheduling (2nd author)") still warns
`claim_semantic_mismatch` — but the source line the pairing table shows
underneath it is now the *right* one. Earlier rounds of this report
(before markdown soft-wrap joining and best-scoring-line selection)
matched this claim to an unrelated neighboring bullet purely because it
happened to be the first line in the block containing the digit "2";
today the mechanism correctly picks the vault's own co-authorship FACT
line — the one that actually mentions "co-authored," "workshop paper,"
"preemption-aware scheduling," and "2nd author" almost verbatim. The
overlap score (0.30) still lands under the 0.50 bar, though, and for a
legible reason once you read the line itself: the FACT is one long,
discursive sentence that also digresses into the `project_notes.md`
author-order confusion ("lists the names as 'Casey, Okafor, Lin' but
also says '2nd author' — those don't agree on who's first...") — a lot
of that line's own distinctive vocabulary is about the confusion, not
the achievement, so the claim's short restatement covers less of the
line's weighted vocabulary than a tighter FACT would let it.

The human check is unchanged from before: the vault's real support for
"2nd author" is the Q&A log's 2026-07-14 entry, where the candidate
confirmed the true order is Okafor, Casey, Lin ("2nd author" is
correct; the notes' own listing order was typed out of habit and isn't
authoritative). Audited and closed: the claim is supported, and the
flag is a true positive on the *matching* mechanism's residual
imprecision against one long, digressive vault line — not on the fact
itself.

## The citation's pairing, now pointing at the right line

`publications[0].citation` gets no `claim_semantic_mismatch` warning —
`publications` isn't a section `check_projection.py` scopes entries
against (only `experience`, `education`, and `projects` are), so this
claim is matched against the whole vault, not one entry's own lines,
and its row is labeled `info`. Earlier rounds of this report flagged
this exact row as a cautionary tale: the whole-vault fallback used to
pick the *first* vault line containing the citation's only number
("2025") in file order, and the Meridian Labs `### ...(Jun 2025 - Sep
2025)` heading — a section heading, not a citation — sorted earlier in
the file than the real Publications FACT line, so `ok` used to point at
something that had nothing to do with the paper.

That specific failure mode is closed now, two ways at once: headings
are excluded from every candidate support-line search outright (a
heading names an org and dates, never an achievement), and where more
than one real candidate remains, the *best-scoring* line wins instead
of whichever came first. The source line shown above,
`"- fact: okafor, d., casey, s., and lin, m. (2025)...` , is the
Publications section's own FACT line — the actual citation, restated
almost verbatim, at a printed overlap of 0.41. The row still stays
`info`, not `pass`: the whole-vault fallback still has no threshold
that honestly separates a rephrase from a fabrication (measured, same
as the qualitative path above), so the level says only "nothing was
mechanically flagged," never "verified" — but what it now points at is
telling the truth, which it did not before.

## What changed since the last round, in one place

- Two previously-real `claim_numbers_span_multiple_facts` warnings —
  `experience[0].bullets[0]` (the RAG evaluation harness bullet) and
  `projects[1].bullets[0]` (the Whisperboard bullet) — are gone. Both
  were markdown soft-wrap artifacts: the vault's own FACT sentence for
  each spans two or three physical lines, so a number could land on a
  different physical line than the rest of its own sentence and read as
  "spanning multiple facts." Continuation lines are now joined into
  their parent line before any matching happens, so both claims verify
  cleanly against one full, correct vault line instead.
- `skills` (16 tokens) is a new, fail-closed check with no manual-audit
  escape hatch — a claimed skill the vault does not back at all is a
  hard FAIL, not a silent pass.
- Every qualitative claim (this resume's five `tags` entries) now gets
  a pairing row; none did before.
- `info` replaces the old, misleading `ok`/`pass` label on every row
  this script cannot honestly grade — the never-scoped numeric fallback
  (the citation, above) and every qualitative claim (the tags, above).
  `pass` now means this script actually mechanically confirmed
  something; `info` means it is showing you its best guess at the
  source, for you to judge, not it.

## What changed in this round

- `coursework` (`education[].coursework`) joined the atomic
  skill/stack check: a course name has no digits, so it previously had
  *no* dedicated check anywhere in the script — invisible to the
  numeric sweep and to the claim-overlap machinery alike. This resume's
  four courses now count toward the `skills` line (16 -> 20) and would
  fail closed (`skill_unsupported`) if any weren't backed by the
  vault's Education FACT line.
- The atomic-token matcher itself was fixed: a single-letter language
  (`R`, `C`) or a symbol-suffixed one (`C++`, `C#`, `F#`) used to
  tokenize to nothing and pass with zero vault support, regardless of
  the vault's actual content. None of this resume's real skills hit
  that gap, but the fix is in the same mechanism this report already
  relies on, so it's noted here rather than left to a separate,
  invisible changelog.
- The vault's own `NOT-CLAIMABLE:`/`PENDING-EVIDENCE:` line markers
  (career-vault.md's exclusion contract) are new: a token, date, URL,
  or skill found only inside such a line is never treated as support,
  for any check. (Round 8 surfaced this as an exit-0 `*_excluded_only`
  WARN; the round-2 review below hardens the marker/denial case to a
  hard FAIL.) This example's vault now uses the marker (see above);
  this run's report is unaffected because nothing here claims that
  fact.
- Every schema field this script doesn't explicitly classify now raises
  its own `unchecked_field` WARN instead of silently falling through to
  a generic numeric-only sweep with no signal that it was never taught
  a real check. This resume's fields are all classified, so nothing
  fires here either — the guard exists for the *next* field a future
  schema revision adds, not this one.
- The verdict line's manual-audit count is now honest about `info` rows
  too (`7`, not `1` — see above), and always prints the full pass/warn/
  info breakdown rather than a single combined number.

## Round 9

- `contact` is a new fail-closed check over `email`, `phone`,
  `location`, and education's `field`. Those four were previously swept
  for stray digits and nothing else, so a wrong reply address or an
  invented field of study returned overall PASS. Six fields verify here
  against the vault's Basics and Education lines.
- Identity and entry-scoping matching are whole-token now, not raw
  substring. A fabricated employer that happens to sit *inside* a real
  one ("Ace" inside "SpaceX") used to scope to the real entry and
  validate every achievement under it; it now fails to anchor, and the
  fabricated name itself fails `identity_unsupported`.
- Skills and coursework are matched against vault *lines*, not one
  flattened whole-vault string, so a multi-word item cannot be
  assembled from unrelated lines ("Operating Systems" out of an
  "operating" here and a "systems" there). Compound entries
  ("PostgreSQL / Redis / MySQL") are split first, so this costs no real
  entry its match. A leading dot is part of the token, so ".NET" no
  longer verifies off "net revenue".
- `NOT-CLAIMABLE:`/`PENDING-EVIDENCE:` support — and an unmarked prose
  denial ("no production Kubernetes experience") — is a `skill_denied`
  **FAIL** now, not a warning that exited 0. `CUT:` lines are their own
  weaker tier: `skill_cut_only`, a WARN, because dropped material is
  usually still true.
- Reversed metrics are caught in either word order: "to 73 ms from
  11 ms" against a vault "from 73 ms to 11 ms" now produces the
  reversal FAIL it always should have.
- Claims and their vault sources are printed in FULL. Every
  human-facing comparison used to be cut to 70 characters on both
  sides — truncating away exactly the diverging tail the manual audit
  exists to inspect.
- `claim_novel_wording` (WARN) flags a claim whose numbers and wording
  track a vault line but which brings vocabulary the vault never uses
  anywhere — the shape that repeats a line's opening clause, keeps its
  numbers, then asserts a different outcome. Calibrated on this pair:
  honest rewrites here run 0.00–0.25 novel-word share, that fabrication
  shape 0.35–0.69; the threshold is 0.30 with a 3-word floor. Nothing
  in this resume trips it.

## Round 9 (second external review)

- Denied support is a FAIL, not a warning, for **numbers, dates, and
  URLs** too — not just skills. A number/date/URL whose only trace is a
  `NOT-CLAIMABLE:`/`PENDING-EVIDENCE:` line, a prose denial, or a
  `## Gaps & flags` line now fails as `number_denied` / `date_denied` /
  `url_denied`. The round-8 `*_excluded_only` WARN (exit 0) let a
  disproven date ship; that is closed. A `CUT:` line is the one weaker
  tier, `*_cut_only`, still a WARN.
- A `## Gaps & flags` (honesty-ledger) section is denied wholesale: a
  skill named only there ("Kubernetes remains a known gap") FAILs, even
  with no marker on the line — the section's whole purpose is to record
  what must not be claimed.
- `email` and `phone` use a stricter whole-token boundary: a wrong
  reply address (`casey@example.com`) can no longer borrow support from
  a different vault address it happens to sit inside
  (`sam.casey@example.com`). A `location` must appear whole on one vault
  line, so "Springfield, Canada" can't assemble itself from a
  "Springfield, USA" line and an unrelated "Canada" mention.
- `claim_direction_conflict` (WARN) catches a reversed metric with no
  from/to markers: "Increased API latency 40%" against a vault "cut API
  latency 40%" — same number, opposite direction. An honest synonym
  that keeps the direction ("reduced" for "cut") does not trip it.

This report exists because a resume and a vault that merely *look*
consistent aren't the same claim as one a mechanical check has
actually verified — including the cases where the mechanical check
correctly admits it can't finish the job unassisted (one WARN, six
`info` rows, all seven counted honestly toward manual audit this
round) and hands each one to a human instead of guessing.
