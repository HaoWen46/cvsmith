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

Rows the analyzer lists under Gates are go/no-go facts, not evidence
targets — exclude them from the /10 coverage score. A gate the resume
contradicts (e.g. a stated graduation date outside the gate) is
reported as a named go/no-go finding at the top of the verdict — the
score still measures tailoring quality, but the report may not read
as a pass.

Scoring bands:

- 9–10: every must-have strong or convincingly weak; nice-to-haves
  covered opportunistically; no wasted sections
- 7–8: all must-haves at least weak, most strong; one gap with a known
  fix (a number to fetch, a bullet to reframe)
- 5–6: one must-have absent or several merely weak — screener-ranked
  middle of pack
- ≤4: multiple must-haves absent; wrong resume for this posting (or
  wrong posting for this person — say which)

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

### Pass 1 — the six-second skim

Recruiters triage survivors of machine ranking in seconds. Simulate
honestly: look at the page as a whole for a few seconds, then write
down — without re-reading — what stuck:

- name and target identity (does the page instantly say what this
  person is?)
- one or two facts (which bullets/numbers grabbed?)
- any brand anchors (schools, companies, venues)
- any visual noise (dense walls, cramped sections, layout oddities)

If what stuck is not what the candidate most needs to land, that's a
finding: the page's visual hierarchy is misallocated.

### Pass 2 — the skeptical deep read

Now read every line as a picky senior engineer deciding whether to
interview. Flag:

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
  read finds nothing to flag; every claim probe-able
- 7–8: skim lands; deep read flags 1–2 vague bullets
- 5–6: skim lands the wrong thing (or nothing); several bullets
  wouldn't survive probing
- ≤4: reads as generated or inflated — active harm territory

## Turning scores into the fix list

Rank fixes by (impact on verdict) × (cheapness): a missing number the
user probably knows > rewriting a weak bullet > reordering sections >
cosmetics. Every fix names its target line and its acceptance test
("bullet 2 gets the dataset size; passes when a skeptic can't ask
'how big?'"). Three to seven items; a twenty-item list is a report
nobody acts on.
