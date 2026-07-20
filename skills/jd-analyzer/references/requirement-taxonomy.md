# Requirement taxonomy — classifying and ranking what a posting says

Job postings are written by committees: a hiring manager's real needs,
a recruiter's template, HR's boilerplate, and legal's disclaimers,
interleaved without labels. The taxonomy separates them.

## Must-have signals (gates)

A requirement is a must-have when it shows any of:

- **Explicit gating language**: "required", "must have", "minimum
  qualifications", "you have" (vs. "you might have")
- **Title words**: anything in the job title is load-bearing ("ML
  Engineer, Evaluation" → evaluation is requirement #1 wherever it
  appears in the text)
- **Repetition**: mentioned in the intro AND the responsibilities AND
  the qualifications — the author couldn't stop thinking about it
- **Specificity**: named tools/methods with context ("Kafka at
  production scale") vs. list-filler ("familiarity with cloud")
- **Position**: first 3 bullets of qualifications carry more intent
  than the last 3; the responsibilities paragraph often states the
  real job better than the qualifications list
- **Credential/legal gates**: degree requirements, clearances, work
  authorization, licenses — binary, no tailoring possible, surface
  them to the user immediately if they might not clear

Rank must-haves by how many signals stack. Title + repetition +
specificity = requirement #1.

## Nice-to-have signals

"Preferred", "bonus", "a plus", "nice to have", "you might also",
single-mention tools, second-half list items, "or equivalent". Also:
requirements phrased as team description ("we use Rust") rather than
candidate description ("you have Rust experience").

Treat inflated wish lists calmly: a posting listing 15 technologies
wants 4 of them (the ones carrying must-have signals); candidates who
self-reject over the other 11 are the posting's main casualty. Tell
the user which 4.

## Culture noise (no resume action)

"Fast-paced environment", "wear many hats", "passionate about our
mission", "self-starter", DEI statements, benefits, values lists.
Classify it, list it as noise, and stop users from burning resume
space "demonstrating passion" — evidence sections cannot cover it and
screeners don't score it. (Cover letters and interviews are where it
lives, out of scope here.)

Exception: when a culture line encodes a real constraint — "on-call
rotation", "50% travel", "in-office 5 days" — it's not noise, it's a
fact for the user's go/no-go, not for the resume. Put it in notes.

## Seniority decoding

Ignore the title; read the scope:

| Signal | Junior | Mid | Senior+ |
|---|---|---|---|
| Verbs | assist, contribute, learn | own, build, ship | lead, define, drive org-wide |
| Scope | tasks within a project | a service/feature end-to-end | systems, teams, strategy |
| Years asked | 0–2 | 2–5 | 5+ (treat ±2 as negotiable when evidence is strong) |
| Support | "mentorship provided" | "works independently" | "mentors others" |

Contradictions are common ("Junior" title, senior scope = underpaying;
"Senior" title, task scope = title inflation). Report the *scoped*
level and note the contradiction — the user should pitch evidence at
the scoped level.

Years-of-experience lines are the most negotiable gate: strong direct
evidence beats a year count in most LLM-era screens (the embedding
doesn't count years; the human sanity-checks). Say when a user within
~2 years of the ask should apply anyway.

## Evidence-target patterns

A good evidence target names the *shape of proof*, not a rephrasing of
the requirement:

| Requirement type | Evidence target shape |
|---|---|
| Tool/stack ("Python, Postgres") | a bullet where the tool did load-bearing work, named inline |
| Practice ("testing culture", "code review") | a bullet with the practice's artifact (suite, CI gate, review process) + its effect |
| Scale ("high-traffic systems") | any number that anchors scale (RPS, rows, users, uptime) |
| Domain ("healthcare data") | domain nouns in a real project context; regulatory acronyms only if true |
| Soft-but-real ("cross-functional") | a bullet where another function appears as collaborator or customer |
| Communication ("writing", "presenting") | the artifact itself: docs, talks, papers, posts — linked |

The target's acceptance test: *a skeptical interviewer reading the
bullet would consider the requirement addressed and know what to probe
next.* If a target can be satisfied by a keyword, it's written wrong.

## Red flags worth reporting

- **Ghost-posting signals**: 30+ days old and reposted, no team
  specifics anywhere, all-boilerplate responsibilities. Users
  shouldn't over-invest in tailoring for these.
- **Unicorn stacks**: must-haves spanning 3 distinct specialties at a
  single-role level (or a junior salary) — calibrate expectations.
- **Level mismatch** (above): affects how every bullet gets pitched.
- **Requirements that can't be evidenced on any resume** ("genius",
  "rockstar", "work hard play hard") — noise category, but a strong
  density of them is itself a signal about the employer.
