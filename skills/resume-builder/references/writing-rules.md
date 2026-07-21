# Writing rules — evidence, not prose

The unit of a resume is the bullet, and a bullet is a *claim with
evidence*, not a sentence that sounds employed. These rules exist
because 2026 screening scores specificity and flags fluff — and because
recruiters, who read thousands of AI-written resumes, now skim *past*
polish looking for facts.

## The bullet formula

```
<did what, concretely> + <how / with what> + <quantified outcome or artifact>
```

- "Built an offline evaluation harness for a RAG support assistant
  (Python, pytest), scoring 1,200 historical tickets nightly and
  catching 3 retrieval regressions before release."
- "Cut p95 retrieval latency from 480 ms to 210 ms by adding
  embedding-cache warmup and switching the index from flat to HNSW."

Order of information: impact-first is fine, action-first is fine — but
the *number or artifact must appear*, and the reader must be able to
tell what the person actually did versus what the team did.

## Quantification discipline

- Interrogate the material for numbers: scale (users, rows, requests,
  dollars), delta (before → after), frequency, rank, time saved. Ask
  the user for real numbers; **never invent them**, and never use
  suspicious template roundness ("increased X by 40%" three times).
- Absolute pairs beat percentages: "480 ms → 210 ms" > "56% faster".
  A percentage without a base reads as decoration.
- No number available? Use a concrete noun instead: the artifact, the
  adoption ("now a required pre-deploy gate for two services"), the
  named thing that exists because they worked. A bullet with neither a
  number nor an artifact is a candidate for deletion.
- One idea per bullet. Two ideas = two bullets or one cut.

## Anti-slop list

These words/patterns mark a resume as generated. Do not emit them:

- spearheaded, leveraged, utilized, synergy, dynamic, passionate,
  results-driven, detail-oriented, seasoned, cutting-edge, delve,
  robust (as praise), "proven track record", "extensive experience"
- verb-salad openings: "Led the development and implementation of…"
- responsibility framing: "Responsible for…", "Tasked with…",
  "Duties included…" — say what happened, not what the org chart said
- empty adverbs: successfully, effectively, seamlessly, efficiently
- em-dash-chained triads and "not just X, but Y" constructions
- every bullet starting with the same verb, or every bullet ending in
  a suspiciously round percentage

Plain strong verbs that survive: built, wrote, shipped, cut, designed,
measured, debugged, migrated, automated, profiled, benchmarked,
published, presented, maintained, reviewed, taught, launched, scaled.

## Tense, voice, mechanics

- Past roles: past tense. Current role: present tense. No "I".
- Numbers as digits ("3 services", "1,200 tickets"); units spaced
  ("480 ms"); ranges with en dash.
- Bullets are fragments, no terminal period needed — but be consistent
  (the templates render what you write; pick one style).
- 1–3 lines per bullet rendered; if it wraps past 2 lines, tighten.
- 3–4 bullets for a major entry, 1–2 for minor ones.

## Honesty mechanics (how "never fabricate" works in practice)

- Every claim must trace to something in the user's materials or their
  explicit answer to your question. When you sharpen phrasing, keep the
  fact constant; when a fact is missing, ask — one batch of questions.
- If the user asks you to inflate (title bump, date stretch, invented
  metric): decline, explain the verification reality (background
  checks, reference calls, interview probing — and inflated claims
  collapse spectacularly in technical interviews), and offer the honest
  strong version of the same material.
- Weak section? Say so: "Two bullets here are thin; a number for X or
  a link for Y would fix it." Users can often supply what's missing —
  they just didn't know it mattered.

## Register — same facts, different music

The bullet formula, quantification, honesty, and parse mechanics are
invariant. **Register** — tone, formality, self-presentation
amplitude — is not: it's a function of industry × market × employer
type × seniority, and the combinations are endless.

This file deliberately does *not* enumerate them. You have absorbed
millions of real resumes, postings, and hiring norms across every one
of these cells; that latent knowledge is deeper and more current than
any table this file could ship. The failure mode isn't ignorance —
it's **defaulting to Anglo-tech punch without noticing the choice**.
So:

1. **Name the cell out loud** before drafting: "US seed-stage startup
   SWE", "German industrial engineering", "US bulge-bracket banking
   analyst", "UK civil service". If you can't name it, ask.
2. **Sample the cell** (task-scoped fetch): 2–3 current postings or
   the employer's own careers page set the temperature better than
   any guide. Match *their* register, not your default.
3. **Confirm with the user in one line** when the register you're
   adopting differs from this file's baseline examples.

Calibration of the axis (contrast, not a lookup table):

- **US tech startup** — energetic-concrete: "Shipped X; cut Y 40%."
  Visible ambition reads as fit.
- **German industrial / Nordic engineering** — sober-complete: the
  same numbers, framed for precision and duration over punch;
  superlatives read as unserious.
- **US banking / consulting** — dense-formal-conventional: strict
  one page, classical section grammar, polished parallel structure;
  deviation is itself a negative signal; awards and GPA carry real
  weight.
- **UK public sector / academia anywhere** — understated-evidential:
  claims sized carefully; "led" only when you truly led.

What never bends with register: the facts and numbers themselves (how
they're *framed* changes, never whether they appear), the anti-slop
list (slop is failure in every culture), honesty, and parse
mechanics (machines read every culture's PDFs the same way).

## The one-line discipline (optional, measured)

Some registers reward every bullet fitting exactly one rendered line:
uniform rhythm, zero orphan words, maximum skim speed. It's a choice,
not a law — evidence-dense bullets legitimately run two lines, and a
number must never be deleted to make weight.

Work budget-first, not retry-first — the loop is the safety net, not
the method:

1. **Measure the budget before drafting.** Render anything through the
   target template once (before content exists, a schema-minimal
   skeleton with three deliberately overlong bullets — see SKILL.md
   step 5) and run `scripts/check_bullets.py` on it: the summary line
   reports *measured capacity* (wrapped bullets' first lines are full
   lines, so the tool calibrates itself to the actual template + font
   + margins — e.g. compact ≈ 112 chars, tighter layouts 130+). No
   table to trust, nothing to go stale.
2. **Plan the division.** Before writing bullets, allocate: how many
   bullets per entry fit the page budget, strongest entry gets the
   most. Then draft each bullet to capacity minus ~8 chars of
   headroom (proportional fonts make any count approximate — that's
   why verification still exists).
3. **Verify every render** — `meta.bullet_lines: 1` makes `render.sh`
   measure the PDF and fail the build naming each violator with its
   overshoot ("138 chars, cut ≳26"). Unset, render.sh still prints the
   wrap report — read it; revision passes (cold-read fixes, folded-in
   answers) reintroduce wraps exactly when nobody is looking.
4. **Escalate on failure — never retry unchanged.** The render is
   deterministic: re-rendering the same text is a no-op, and a second
   identical failure means the *strategy* is wrong, not the luck.
   The ladder: (1) cut filler words; (2) still over → change
   structure — split into two self-sufficient bullets, or move
   stack/context into the tag row (compact); (3) still over → the allocation
   was wrong: fewer bullets for that entry, or unset the knob for
   this projection. Never delete a number to make weight.

The same failure-carries-information rule governs every check in this
toolkit: a page_budget overflow escalates through the typst-guide cut
order, not through re-rendering hope.

## Two readers, one line — the anti-yapping rule

Every line on the page is read by at most two people: the skimmer
(HR/recruiter, the six-second skim — screening-2026.md sources the
range — reads position and bold anchors) and the prober
(interviewer/professor, reads bullets as a list of things to ask
about). **A line that serves neither reader is yapping — delete
it**, however true or well-written it is.

- Skim-value lives in: name/identity line, section headers, bolded
  orgs and titles, the first bullet of the top entry, big numbers.
- Probe-value lives in: mechanisms ("by moving X to Y"), named
  artifacts, tag rows, precise scope claims — anything a prober can
  turn into a question you *want* to be asked.
- Serves neither: mission statements, adjectives about yourself,
  restatements of the section header, tool lists nothing evidences,
  duties everyone in the role has ("attended meetings", "collaborated
  with team members"), and any sentence whose deletion loses no fact.

The test when trimming: cover the line and ask (a) does the skim
story change? (b) does the interviewer lose a question? Two noes =
cut. Density is not the enemy — undifferentiated density is; a dense
page of probe-bait reads fast *because* every line pays.

## Section-level guidance

- **Ordering is field-dependent** (see the field file), but the
  student default is Education → Experience → Projects → Skills.
- **Summary**: omit for students/early-career (it spends 6-second-skim
  budget on words that aren't evidence). Include only when there's a
  non-obvious positioning story (career change, unusual combination).
- **Skills**: 2–4 groups, everything defensible in an interview.
  The skills list corroborates the bullets; it never introduces
  abilities the bullets don't evidence.
- **Projects**: for students, often the strongest section. Link them.
  A project bullet still follows the formula — what, how, outcome.
