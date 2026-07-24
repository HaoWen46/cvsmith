# Resume evaluation: examples/ai-ml-intern/resume.pdf

Evaluated 2026-07-24 against jd-analysis.md (Cascadia AI ML intern).

## Verdict
**MECHANICAL: READY** — all deterministic layers pass clean (L0–L3),
no L5 fabrication/inflation flag outstanding.
**TARGET FIT: NOT READY — for this specific posting** — the resume
itself is strong (evidence scores 9/10 against the scoreable
must-haves), but two Gate rows block it: the graduation gate ("Dec
2027 or later" vs. Sam's Jun 2026, status: **not met**) fails before
scoring matters, and the work-authorization gate is **unconfirmed** —
an open question, not a pass. No fix or decline changes the graduation
gate; it is a calendar fact. Even for an equivalent Summer-2026-eligible
posting, TARGET FIT would cap at NOT READY exactly as it does here
until the work-authorization gate is confirmed met — only then would
the file be TARGET FIT READY. Neither gate is resolved by declining it.
**CRAFT: 8/10 — 0 must-fix judgment findings declined, 0 open** (two
optional judgment items below — the "required pre-deploy gate"
interview-prep phrasing, and a **page-economy** finding: the compact
template renders ≈9pt body type yet the content ends at 522pt on a
792pt page, leaving 34% blank below it, so the typography and the
whitespace disagree about how much material there is [rubric.md Pass 1
"page economy"]. That caps the band at 8, not 9. Both are optional,
not must-fix — they don't move the score into ≤6 territory or hold the
run open. CRAFT never gates either READY verdict above; it names the
craft gap the two verdicts don't).

## Run status
**NOT DONE — TARGET FIT NOT READY** (graduation gate not met, a
calendar fact; work-authorization gate unconfirmed). MECHANICAL is
READY and CRAFT is 8/10 (≥ 7), so nothing on the truth or craft axes
holds the run open — but this is a JD-targeted run, and TARGET FIT is
below READY for reasons no rewrite fixes. The run ends only if the user
sees this and chooses to ship anyway — which would read `DONE (shipped
below target fit — user's call)`, never a bare `DONE` — or retargets to
an eligible posting. (A no-JD run of this same file would read `DONE
(no JD — not validated against any target)`: MECHANICAL READY + CRAFT
≥ 7, TARGET FIT not evaluated.)

## Deterministic layers
| Layer | Result | Notes |
|---|---|---|
| L0 extraction | PASS | 2,133 non-space chars (~265 are the compact template's right-aligned dot-leader glyphs, not resume prose; see note below), clean encoding (bad-char ratio 0.0004), extractor token overlap 1.00 |
| L1 parse sim | PASS | all 6 sections route under standard headings; name/email/dates parse |
| L2 integrity | PASS | 283 content words checked — every one puts ink on its bbox; no tiny/off-page/zero-width text (287 decorative leader tokens excluded from the count, still integrity-checked) |
| L3 structure | PASS | 1/1 pages, letter, tagged PDF, fonts embedded, single column (compact template) |

**Note on the dot leader:** the compact template's right-aligned date
rows use a spaced dot LEADER (real "." glyphs, 3pt apart, filling the
gap between an entry's title/institution and its date, table-of-
contents style) so that extraction order stays correct — see the
round-9 notes in `skills/resume-builder/assets/templates/compact.typ`
(a whitespace gap or a drawn rule both reorder the date out of its own
entry under poppler; only real glyphs preserve order). Those glyphs are
real, visible ink and land in the text layer, so they count toward L0's
raw char/token totals. They do **not** contaminate the content
metrics: L2 `words_checked` (283) excludes them as `decorative_tokens`
(287) — reported separately, never folded into the content-word count a
reader takes as a size measure (round-2 review finding 5) — and none of
the scoreable requirements below reference the leader.

## L4 — JD alignment: 9/10

**Go/no-go finding (named first, excluded from the score):** the
posting's graduation gate ("Dec 2027 or later") fails against the
resume's Sep 2022 – Jun 2026 — a calendar fact no tailoring changes,
status **not met**. The US work-authorization gate is **unconfirmed**
(a form question, not a resume line, per jd-analysis.md's Gates table)
— an open question that blocks TARGET FIT READY exactly as a "not met"
gate would, until the candidate answers it. The score below measures
tailoring quality against the scoreable must-haves.

| # | Requirement | Evidence | Strength |
|---|---|---|---|
| 1 | LLM evaluation | eval harness bullet: 1,200 tickets nightly, 3 regressions caught | **strong** |
| 2 | LLM application work | RAG latency bullet: p95 480→210 ms via cache warmup + HNSW | **strong** |
| 3 | Python + testing | "(Python, pytest)" load-bearing in the harness bullet | **strong** |
| 4 | Measurement mindset | WER 18.2→11.6% on held-out set; baselines reproduced within 2% | **strong** |

Nice-to-haves: HNSW (strong), OSS with 1.4k stars + 27 contributors
(strong, linked), workshop publication (strong, linked), Rust
(strong), GPU systems research (strong). Vocabulary already mirrors
the JD's real terms (harness, regressions, red-team, held-out) —
nothing bolted on.

## L5 — recruiter simulation: 9/10
**Six-second skim:** lands "Sam Casey — CS @ UW — ML intern with
eval/RAG numbers". The 480→210 ms and 1,200-ticket figures pop; GitHub
star count anchors the projects section. Visual hierarchy is clean;
nothing competes with the strongest facts.

**Skeptical read:** every major claim carries a number or artifact and
would survive probing ("how did you catch the regressions?" — the
harness bullet already names the mechanism). Flags: (1) "now a
required pre-deploy gate" is a strong claim an interviewer will probe
— Sam should be ready to name who required it; (2) the publications
URL must resolve to the real paper in a real application (synthetic
here).

## Fix list (ranked)
1. **Eligibility**: don't submit to this posting — target the Summer
   2026 cycle of the same teams. No resume change fixes a calendar —
   gate fact, not a resume finding; not classified truth/judgment.
2. Confirm work authorization before applying to US roles (not a
   resume line; a form answer) — gate fact, not a resume finding;
   until confirmed "met" this alone caps TARGET FIT at NOT READY for
   any US posting, this one included.
3. Keep a one-line answer ready for the "required pre-deploy gate"
   probe (who mandated it, when) — phrasing is fine, just be ready —
   kind: judgment, severity: optional (the claim is already true per
   the vault; this is interview prep, not a resume fix).
