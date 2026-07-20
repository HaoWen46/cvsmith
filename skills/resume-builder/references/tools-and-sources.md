# External tools & sources — what exists per stage, and when to reach for it

The skills bundle deterministic local tools for everything in the
verification loop. This catalog covers what else exists in the world,
what it's for, and the discipline for using it. The point of "getting
hired" is bigger than the document; fresh outside information has its
place — governed, not sprayed.

## The three knowledge tiers (the whole doctrine)

| Tier | Decay | Examples | Policy |
|---|---|---|---|
| 1 — Mechanics | years | parsing physics, single-column, honesty discipline, bullet formula | bundled in references; **never** researched at runtime |
| 2 — Slow-cycle facts | ~6–12 months | vendor screening behavior, detection stats, which evidence is "hot", recruiting-season calendar | bundled with `Last verified:` / `Verify by:` stamps; re-verified **on schedule by the repo** (see MAINTENANCE.md), not per query |
| 3 — Task-scoped facts | per task | the posting itself, the company's stack/team/blog, this role's comp, this board's data | **always fetched fresh at use** — this is task input, not research spam |

**When to research, in one rule:** fetch tier-3 always; touch tier-2
only if a *load-bearing* fact for the current decision is past its
`Verify by:` date; never re-derive tier-1. Everything else is spam:
it burns latency, and worse, it churns answers — the same user asking
twice must get the same doctrine, or the verification loop stops being
measurable and trust dies. Stable rubrics are a *feature*: iteration
N's score is only comparable to iteration N−1's if the rules held
still between them.

## Stage-by-stage catalog

### Extraction / parse simulation (bundled, local, pinned)
- **Bundled**: poppler `pdftotext`/`pdfinfo`, `pypdf`, `pdfplumber`,
  `pdf2image` — pinned via `uv.lock` + PEP 723 ranges. Deterministic,
  CI-tested, no API keys: this is deliberate (skills, not services).
- **Known alternatives** if a PDF defeats the bundled pair: Apache
  Tika (JVM, heavyweight), `docling`, `unstructured`, `marker`
  (layout-aware, ML-heavy). Reach for one only when the two bundled
  extractors *disagree* and the user's PDF can't be rebuilt — a
  third opinion, installed ad hoc, never a standing dependency.
- **Commercial parser APIs** (Affinda, HireAbility): what real ATSs
  license. Useful for one thing — a ground-truth check if a user
  reports a real-world parse failure our simulation missed. Requires
  keys and uploads a person's data to a third party: user consent
  first, and record the failure in failure-modes.md so the local
  simulation learns it.

### Semantic matching (L4)
- Deliberately **judgment, not a local embedding score**. A
  sentence-transformers cosine would look objective while measuring
  the wrong model (vendors' matchers are unknowable and varied) —
  precision theater. The agent reading requirements against evidence
  *is* the honest simulation. Revisit only if a vendor publishes
  their matcher (tier-2 fact; it would go through MAINTENANCE.md).

### JD ingestion (tier-3: always fetch fresh)
- Given a company name, postings often live on public board APIs —
  fetch the JSON instead of scraping HTML:
  - Greenhouse: `https://boards-api.greenhouse.io/v1/boards/<company>/jobs?content=true`
  - Lever: `https://api.lever.co/v0/postings/<company>?mode=json`
  - Ashby: `https://api.ashbyhq.com/posting-api/job-board/<company>`
- Login-walled/JS-only pages (LinkedIn, Workday tenants): ask the
  user to paste — built into jd-analyzer already.

### Company context (tier-3, optional depth)
For a top-choice application: the company's engineering blog, docs,
recent launches, and repo activity say what the team actually values
better than the posting's boilerplate — it sharpens which evidence
leads and preps interviews. Spend this fetch only when the user is
investing heavily; skip it for volume applications.

### Market context (tier-2, scheduled; light tier-3 checks)
- Indeed Hiring Lab, BLS JOLTS (monthly releases), layoffs trackers,
  levels.fyi (comp reality-check — remember: this toolkit never gives
  the user financial advice, just points at data).
- Recruiting seasons are calendar facts (new-grad cycles open
  Aug–Oct, internships Jul–Sep for the following summer): bundled in
  field guides as tier-2, refreshed on the seasonal schedule — this
  is why the repo re-verifies twice a year, not per query.

## Tool updating (the bundled ones)

Versions are pinned so behavior is reproducible; updates are
deliberate events, not drift: `uv lock --upgrade` + full test suite
(the fixtures are the regression net — an extractor behavior change
shows up as a failing planted-fixture test), Typst bumped when release
notes touch PDF export, fonts vendored so they never drift. Cadence
and steps live in MAINTENANCE.md.
