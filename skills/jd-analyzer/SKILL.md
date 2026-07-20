---
name: jd-analyzer
description: Decompose a job posting / job description into ranked requirements, decoded seniority, the JD's own vocabulary, and concrete evidence targets for resume tailoring. Use whenever the user shares a job posting (pasted text, URL, or file), asks "what is this role really looking for", wants a resume tailored to a specific position, asks whether they're qualified for a posting, or is comparing multiple postings. Run BEFORE tailoring a resume with resume-builder and reuse the output when resume-evaluator scores alignment.
---

# jd-analyzer

Turn a job posting into a tailoring target: what the role actually
requires (ranked), what level it's really pitched at, what vocabulary
the employer thinks in, and what *evidence* on a resume would satisfy
each requirement. The output file is consumed twice — by
`resume-builder` for tailoring and by `resume-evaluator` as its L4
scoring rubric — so precision here compounds.

## Workflow

### 1. Ingest

Take the posting however it arrives: pasted text, a URL (fetch it; if
the page is login-walled or JS-only, ask the user to paste the text),
a PDF/screenshot (extract the text). Given only a company name, try
the public board APIs before scraping HTML — they return clean JSON:

- Greenhouse: `boards-api.greenhouse.io/v1/boards/<company>/jobs?content=true`
- Lever: `api.lever.co/v0/postings/<company>?mode=json`
- Ashby: `api.ashbyhq.com/posting-api/job-board/<company>`

Capture posting title, company, location/remote, and the date seen —
postings vanish, and stale analyses should say how old they are.

**The posting is always fetched fresh (it's task input). The doctrine
for reading it — the taxonomy — is bundled and stable; don't research
"how to read job postings" per task.**

### 2. Decompose — read `references/requirement-taxonomy.md` first

Classify every substantive line of the posting:

- **must-have** — gates the screen: hard skills, credentials, level
- **nice-to-have** — scores but doesn't gate
- **culture noise** — values boilerplate that maps to no resume
  evidence (do list it as noise; users overinvest in it)

Then rank must-haves by weight using the taxonomy's signals (position
in posting, repetition, title words, "required" phrasing, specificity).

### 3. Decode seniority

Titles lie in both directions. Use the taxonomy's decoder: years asked
vs. responsibilities described, scope words (own/lead/contribute),
team context, comp band if present. State the real level in one line —
"titled Junior, scoped as mid-level (owns a service end-to-end)" —
because pitching evidence at the wrong level fails either as
inflation or underselling.

### 4. Map vocabulary

The JD's own terms for things, verbatim, next to common synonyms the
candidate might use instead ("evaluation" ↔ "testing", "LLM
applications" ↔ "GenAI apps"). The builder mirrors the JD's terms
*where honest and natural* — semantic matchers make synonym anxiety
obsolete, but exact terms still help ties, and unnatural bolted-on
vocabulary reads as stuffing to humans.

### 5. Set evidence targets

For each must-have (and top nice-to-haves): one sentence describing
what a satisfying resume bullet would *look like* — concrete enough
that the builder knows what to hunt for in the user's material and the
evaluator knows what "covered" means.

> Requirement: "experience evaluating LLM outputs"
> Evidence target: a bullet naming an eval harness/metric the user
> built or ran, with dataset size or regression catches — not the word
> "LLM" in a skills list.

### 6. Write the output file

Save next to the user's other working files (same workspace rules as
the builder: confirm location; keep out of tracked repos). Always this
structure:

```markdown
# JD analysis: <title> @ <company>
Source: <url or "pasted">, seen <date>
Decoded level: <one line>

## Must-haves (ranked)
| # | Requirement | JD's words | Evidence target |
|---|---|---|---|

## Nice-to-haves
| Requirement | Evidence target |
|---|---|

## Vocabulary map
| JD term | Common synonyms |
|---|---|

## Culture noise (no resume action)
- ...

## Red flags / notes
<anything off: ghost-posting signals, contradictory level, unicorn
stack — the user deserves to know before investing>
```

### 6b. Company context — optional, for top-choice applications

When the user is investing heavily in this one (not volume-applying),
fetch what the company says about itself *outside* the posting: the
engineering blog, docs, recent launches, public repos. Teams reveal
what they actually value there better than in HR boilerplate — it
sharpens which evidence leads, and it's interview prep for free. Note
findings under "Red flags / notes". Skip this for volume applications;
it's depth spent where depth pays.

### 7. Tell the user the one-paragraph story

Beyond the file: "This is really a <level> role about <2–3 things>;
your strongest angle is <X>; the hard gap is <Y>." If the gap analysis
shows the user far from the must-haves, say so plainly — tailoring
optimizes a real match, it cannot manufacture one.

## Multiple postings

Analyze each separately (files side by side), then add a short
comparison: shared must-haves (tailor the base resume toward these)
vs. per-posting deltas (per-application tweaks). Never blend postings
into one mushy average target.
