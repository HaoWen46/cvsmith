# Scoring rubric — L4 alignment and L5 human simulation

Deterministic layers are pass/fail; these two are scored judgments.
Scores exist to make iteration measurable, not to flatter: a 7 that
was a 5 last round is the story, not the absolute number.

## L4 — JD alignment (score /10)

Input: the jd-analyzer output (ranked requirements + vocabulary map +
evidence targets), or a raw posting you decompose on the fly (then say
you did — and prefer running jd-analyzer properly).

For each **must-have** requirement, classify the resume's evidence:

- **strong** — a specific bullet whose claim would satisfy a skeptical
  interviewer probing that requirement (number or artifact attached)
- **weak** — related material exists but doesn't commit (no scale, no
  outcome, or only a skills-list token)
- **absent** — nothing routes to this requirement

Gate rows are go/no-go facts, not evidence targets — exclude them from
the /10 coverage score. Their candidate status (met / not met /
unconfirmed) is whatever the cold-reader context block's Gate status
line already says — the L5 reader **reads that line, it does not
re-derive gate status on its own**. That line was settled UPSTREAM,
before dispatch, by SKILL.md's evidence-priority rule ("Judgment layers
need a cold reader": persisted jd-analysis → a fact in the attached
files → the user's own statement → otherwise `unconfirmed`); the "don't
re-derive" rule here is only the division of labor — the context block
owns settling the status, the cold reader consumes it — not a claim
that status can come only from a persisted file. A "not met" gate is a
named go/no-go finding at the top of the TARGET FIT verdict regardless
of the coverage score; an "unconfirmed" gate is named too (it's a
question for the user, not a pass). The score still measures tailoring
quality, but the report may not read as a pass.

Scoring bands:

- 9–10: every must-have strong; nice-to-haves covered opportunistically;
  no wasted sections
- 7–8: all must-haves at least weak, most strong; one gap with a known
  fix (a number to fetch, a bullet to reframe)
- 5–6: **one must-have absent**, or several merely weak with none
  absent — screener-ranked middle of pack. These two causes both name
  real gaps, and neither makes TARGET FIT READY-compatible on the
  strength of the score alone (see below — same rule as ≤4): a weak
  must-have is exactly as must-fix a `fit` finding as an absent one
  (see the Fix-list section), so this band never coexists with TARGET
  FIT READY until every must-have that drove it down is raised to
  strong.
- ≤4: multiple must-haves absent; wrong resume for this posting (or
  wrong posting for this person — say which)

This band is a hard floor on `resume-evaluator`'s TARGET FIT verdict:
at ≤4, TARGET FIT cannot be READY, full stop — not with a user decline,
not with a strong L5 score, not with mechanical layers all green. The
5–6 band is not a second, softer floor sitting above it: whether a 5–6
score is driven by an absent must-have or by several weak-but-present
ones, TARGET FIT is NOT READY for the identical reason as ≤4 — a
must-have that isn't strong is a **`fit` finding** (see the Fix-list
section), and a `fit` finding against a must-have is always must-fix,
so no numeric band compensates for it. This is a coverage gap, not a
dishonesty problem: the resume isn't claiming the requirement, so it
stays completely honest while still not being competitive for this
posting — that's exactly why `fit` findings are their own kind (see
SKILL.md's "Finding classification") and never touch MECHANICAL, only
TARGET FIT. An otherwise-clean resume that is honest about simply
lacking one requested technology is the textbook case: MECHANICAL:
READY (nothing dishonest on the page) alongside TARGET FIT: NOT READY
(a must-have gap) — two different verdicts telling two different
truths, never collapsed into one. Nothing short of raising every such
must-have to strong changes the TARGET FIT side (see SKILL.md's
Verdict rules for how MECHANICAL and TARGET FIT stay independent
axes). The 7–8 band's "most strong" case carries the same constraint:
whichever must-have is still merely weak remains an open must-fix
`fit` finding, so that gap — not the /10 number — is what SKILL.md's
conditions (a)/(c) key off of.

Also check, and name in the report:

- **Vocabulary**: does the resume use the JD's own terms where honest
  and natural? Flag both misses ("JD says 'evaluation', resume only
  says 'testing'") and stuffing (JD terms bolted on without evidence —
  that's a downgrade, not a credit).
- **Space allocation**: strongest real estate (top third, longest
  entries) should carry the JD's top requirements. Flag inversions.
- **Level match**: evidence pitched above/below the seniority the JD
  decodes to (jd-analyzer reports it) — miscalibration reads as either
  inflation or underselling.

Never suggest closing a gap by invention. A gap either has honest
evidence somewhere in the user's material (builder's job to surface),
or it stays a gap the user should know about before applying.

## L5 — human simulation (score /10)

Work from the rendered page image, not the source. You are simulating
two different readers.

### Reader by target field

Pass 2's interviewer isn't the same person for every CV. Read the
cold-reader context block's Target reader line (resume-evaluator's
SKILL.md derives it from `meta.target_field`) and pick the matching
persona — each is drawn from the builder's own field guide, so the
reader wants the same evidence the builder was told to prioritize:

| `meta.target_field` | Reader | Source |
|---|---|---|
| ai-ml | a practitioner who builds these systems day to day — screens for eval literacy, agent/tool-use evidence, precise metrics; hype vocabulary reads as outsider, not neutral | `resume-builder/references/fields/ai-ml.md` |
| swe (and any unlisted industry field) | a picky senior engineer deciding whether to interview | `resume-builder/references/fields/swe.md` |
| academic | faculty or an admissions-committee member doing a 15–60 second skim for research experience (whose lab, doing what), publication venue/authorship, and hard-course grades — not a corporate-screener read | `resume-builder/references/fields/academic.md` |
| generic / unrecognized | no fixed persona — adopt whatever reader that field's own screening process implies (hiring manager, licensing board, portfolio reviewer) and name which reader you used | `resume-builder/references/fields/generic.md`'s research procedure |

No context block (standalone review, no yaml/JD)? Default to the swe
reader and say so in the report.

**Seniority bar (`meta.target_level`).** The reader above judges
evidence against the bar of the level the CV aims at — the same field,
read for a `staff` role, is not read for an `intern` one. On a no-JD
run this is what makes the assessment a level-competitiveness read, not
just field style. Apply the target level as the deep-read expectation:

| `meta.target_level` | What the reader expects the evidence to show |
|---|---|
| intern / new-grad | coursework, projects, one real internship or research stint; *potential* and fundamentals over track record. Missing industry scale is normal, not a gap. |
| junior / mid | shipped production work owned end-to-end, measurable outcomes, growing scope; a portfolio of "I built and ran X". |
| senior | ownership of ambiguous/cross-team problems, design judgment, mentoring/leverage beyond own output; scope and impact, not task lists. |
| staff / principal / lead | org-level impact, technical direction others follow, initiatives not tickets; the evidence should read as "moved the org", and its absence is the finding. |
| manager | team outcomes, hiring/growth, delivery through others; individual-contributor bullets without team results are the mismatch. |

Report the level read explicitly (report format's Run status / L5):
whether the evidence plausibly clears the target level's bar, at, or
below it. If `meta.target_level` is absent, say so and read at the
field's default early-career bar (intern/new-grad), flagging that as an
assumption rather than a silent choice.

### Pass 1 — the six-second skim

Recruiters triage survivors of machine ranking in seconds. Simulate
honestly: look at the page as a whole for a few seconds, then write
down — without re-reading — what stuck:

- name and target identity (does the page instantly say what this
  person is?)
- one or two facts (which bullets/numbers grabbed?)
- any brand anchors (schools, companies, venues)
- any visual noise (dense walls, cramped sections, layout oddities)
- **page economy**: does the type size match how full the page is?
  Estimate where the content ends on the page. Two failure directions,
  both findings:
  - *Overfull*: content crammed to the margins, sub-9pt type, no
    breathing room — the dense-wall case above.
  - *Underfull with dense type*: small type (≈9pt or under) that still
    leaves roughly a fifth of the page (or more) blank below the last
    line. That is a self-contradiction — the type was shrunk to fit
    material that clearly had room to breathe — and it wastes the
    reader's most valuable space (the top third stays cramped while the
    bottom sits empty). Either the type should be larger / spacing more
    generous, or the layout should use the space; dense-and-underfull
    is neither choice made well.

If what stuck is not what the candidate most needs to land, that's a
finding: the page's visual hierarchy is misallocated.

### Pass 2 — the skeptical deep read

Now read every line as the reader selected above. Flag:

- **Inflation smells**: solo-credit for team outcomes ("led" on an
  intern bullet), suspicious roundness, impact claims with no
  mechanism ("improved reliability" — how?)
- **Vagueness**: bullets with neither number nor artifact; skills
  listed but never evidenced in bullets
- **AI slop**: slop vocabulary (spearheaded, leveraged, passionate,
  results-driven, "proven track record", empty adverbs like
  seamlessly — and their kin), uniform bullet rhythm,
  interchangeable-candidate phrasing (could this line appear on 500
  other resumes unchanged?)
- **Probe points**: for each major claim, what would the interviewer
  ask, and does the resume's phrasing survive the question? Phrasing
  that survives probing is the honesty test in miniature.

Scoring bands:

- 9–10: skim lands the right identity + one memorable number; deep
  read finds nothing to flag; every claim probe-able; the page is
  economical — type size matches how full the page is (no dense-and-
  underfull contradiction from Pass 1's page-economy check)
- 7–8: skim lands; deep read flags 1–2 vague bullets
- 5–6: skim lands the wrong thing (or nothing); several bullets
  wouldn't survive probing
- ≤4: reads as generated or inflated — active harm territory

A page-economy failure (Pass 1) is a craft finding like any other: a
resume in dense ≈9pt type that still leaves ~a fifth or more of the
page blank cannot reach 9–10 — the typography and the whitespace
disagree about how much material there is, and a strong document
doesn't send that mixed signal. Cap it at 7–8 (a real but fixable
craft issue) unless something worse also applies.

This band is also SKILL.md's **CRAFT** score verbatim — the same /10,
reported as a third always-on surface next to MECHANICAL and TARGET
FIT. "Active harm territory" describes what a ≤4 CRAFT score means
for the candidate's odds, not a reason to fail MECHANICAL or TARGET
FIT: a resume can be perfectly honest and perfectly on-target while
still reading this badly (generic phrasing, flat emphasis, buried
lede), and CRAFT exists precisely to name that instead of letting two
READY verdicts imply a stronger document than what shipped. It never
gates either READY verdict (see SKILL.md's "Verdict rules") — but the
must-fix `judgment` findings that drove the score down do gate the
*run*: SKILL.md's iteration protocol won't let a run end while one
sits open-undecided, only fixed or explicitly declined.

## Turning scores into the fix list

Rank fixes by (impact on verdict) × (cheapness): a missing number the
user probably knows > rewriting a weak bullet > reordering sections >
cosmetics. Every fix names its target line, its acceptance test
("bullet 2 gets the dataset size; passes when a skeptic can't ask
'how big?'"), and its classification per SKILL.md's "Finding
classification" — kind (`truth`/`fit`/`judgment`) and severity
(`must-fix`/`optional`). Any L4/L5 fabrication, inflation, or other
honesty flag against a claim the resume actually makes is a `truth`
finding and therefore always `must-fix` (gates MECHANICAL). An absent
or weak must-have requirement is a `fit` finding, not a truth finding
— it's a coverage gap in an otherwise honest resume — and is must-fix
against MECHANICAL's counterpart, TARGET FIT (a `fit` finding against
a nice-to-have is `optional`, since nice-to-haves are never a TARGET
FIT gate). Style, emphasis, ordering, and length preferences are
`judgment` findings; they gate neither READY verdict, and their
severity is tied to the same L5/CRAFT score this section computes —
`must-fix` when the finding materially contributes to a ≤6 band score,
`optional` when fixing it wouldn't move the score (SKILL.md's "Finding
classification"). This mirrors how a `fit` finding's severity is tied
to the JD's must-have/nice-to-have split: an objective anchor, not a
free discretionary tag. Concretely, a ≤6 score (this section's bands
above: "skim lands the wrong thing" or worse) with zero must-fix
`judgment` findings reported is a reporting defect — something drove
the score down, and it must be named as must-fix or the report must
explain why not. A `judgment` finding tagged `must-fix` still doesn't
block MECHANICAL or TARGET FIT — but it does feed the CRAFT tally
(SKILL.md's "Verdict rules") and it blocks the *run* from ending until
it's fixed or explicitly declined by the user (SKILL.md's "Iteration
protocol") — silence is never a resolution.
Three to seven items; a twenty-item list is a report nobody acts on.
