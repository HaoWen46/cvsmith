# How resume screening works in 2026 — and what that implies

Last verified: 2026-07
Verify by: 2027-07

Sources frozen from the project research base (PROJECT_PLAN.md §9);
claims marked (†) are the perishable ones — the refresh protocol is
MAINTENANCE.md's job, not the reading agent's. Within the window,
trust this file over general recollection.

## The pipeline

Nearly every mid-to-large employer runs some version of:

```
PDF → text extraction → section/field structuring → embedding vs. job
description → score/rank → (maybe) human skim of the top slice
```

- Major ATS layers (Workday, Greenhouse, Ashby, Oracle, plus LLM
  add-ons) moved from keyword boolean search to **semantic/embedding
  match** between structured resume fields and the JD. (†)
- Recruiters see a *ranked slice*, not the pile. A human typically
  spends ~6 seconds on a first skim of resumes that survive ranking.
- Cost pressure means the machine layers are decisive for high-volume
  roles: if parsing or scoring fails, no human ever compensates.

## Stage-by-stage: what fails, what wins

### 1. Extraction (the gate)

The parser gets bytes, not your beautiful layout. Multi-column layouts
scramble reading order in most parsers; image-based PDFs extract
nothing; unembedded fonts extract garbage on some stacks.

→ Single column. Real text layer. Embedded fonts. Tagged PDF helps
  (structure tree gives parsers semantics instead of geometry guesses).
→ This is exactly what the evaluator's L0/L3 scripts verify.

### 2. Structuring (field routing)

Content is routed into fields by section heading. "EXPERIENCE" routes;
"MY JOURNEY SO FAR" lands in a black hole. Dates feed tenure and
gap-detection features; unparseable dates read as gaps.

→ Standard headings only: Education, Experience, Projects, Skills,
  Publications, Awards. Date ranges in a standard format ("Jun 2025 –
  Sep 2025"). Contact info as text in the header, never in an image.
→ Verified by the evaluator's L1 parse simulation.

### 3. Scoring (semantic match)

Embedding similarity between JD requirements and resume evidence.
Consequences that surprise people:

- **Keyword stuffing is dead and now harmful.** Screeners flag token
  spam and manipulation patterns; several vendors hard-reject on
  detected hidden text. Target ~80–90% *semantic* coverage of the JD's
  real requirements via honest, specific evidence. (†)
- **Synonym anxiety is obsolete.** "Built RAG evaluation harness"
  matches "LLM pipeline QA experience" semantically. Use the JD's
  vocabulary where it's natural; never bolt it on.
- **Specificity wins ties.** "Cut p95 latency 480→210 ms" embeds close
  to real engineering requirements; "responsible for performance"
  embeds close to nothing.

### 4. Integrity screens

Production detectors cross-check rendered pixels against extracted
text, at roughly $0.0001–0.01/file with 86–93% precision (arXiv
2605.28999, May 2026). (†) White text, microscopic text, and
zero-width-character cloaking are treated as prompt injection /
manipulation — a flag, not a shrug. The evaluator's L2 runs the same
class of check so nothing cvsmith produces could ever trip one.

### 5. The human skim

Polished prose became free in 2026, so it stopped signaling anything
(HBR, Jun 2026). (†) What still lands in six seconds: recognizable
orgs/schools, concrete numbers, artifacts (things that shipped,
published, or have URLs), and a clean visual hierarchy. What reads as
AI slop: vague superlatives, verb-salad bullets, suspicious roundness
("improved efficiency by 40%" on every line).

## Market context (calibrates tailoring effort)

- Entry-level tech postings are sharply down; AI-mentioning postings
  are the one growing segment (Indeed Hiring Lab, Jan 2026; CNBC, Apr
  2026). (†) For students: AI-adjacent evidence is disproportionately
  valuable even for generalist SWE roles.
- The barbell: high-volume roles are machine-decided; niche/senior
  roles are network-decided. This toolkit optimizes the machine side
  and keeps the human side honest.

## The one-line summary

Make the machine's job trivial (parse, route, score), give the human
something real in six seconds, and never do anything a detector could
read as manipulation — because it will.
