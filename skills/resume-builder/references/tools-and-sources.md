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
| 2 — Slow-cycle facts | ~6–24 months | vendor screening behavior, detection stats, which evidence is "hot", recruiting-season calendar, regional conventions | bundled with `Last verified:` / `Verify by:` stamps; verify a load-bearing fact at use when its date has expired |
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
- These extractors serve the verification loop only — intake never
  goes through them. A deterministic resume-to-yaml parser is an
  adjudicated non-tool: it would reproduce exactly the parse failures
  this stage exists to simulate, and a wrong mechanical draft poisons
  the vault; the agent reading the source document natively is the
  better instrument.

### Semantic matching (L4)
- Deliberately **judgment, not a local embedding score**. A sentence-transformers cosine would look objective while measuring the wrong model (vendors' matchers are unknowable and varied) — precision theater. The agent reading requirements against evidence *is* the honest simulation. Revisit only if a vendor publishes enough current detail to validate a different method, and verify that primary source before changing this contract.

### JD ingestion (tier-3: always fetch fresh)
- Given a company name, postings often live on public board APIs
  (Greenhouse/Lever/Ashby) that return clean JSON instead of
  scrape-hostile HTML. Posting fetch is jd-analyzer's job and its
  SKILL.md carries the current endpoints — invoke that skill (or
  follow its Ingest step) rather than re-deriving URLs here.
- Login-walled/JS-only pages (LinkedIn, Workday tenants): ask the
  user to paste — built into jd-analyzer already.

### Company context (tier-3, optional depth)
For a top-choice application: the company's engineering blog, docs,
recent launches, and repo activity say what the team actually values
better than the posting's boilerplate — it sharpens which evidence
leads and preps interviews. Spend this fetch only when the user is
investing heavily; skip it for volume applications.

### Market context (dated tier-2; light tier-3 checks)
- Indeed Hiring Lab, BLS JOLTS (monthly releases), layoffs trackers,
  levels.fyi (comp reality-check — remember: this toolkit never gives
  the user financial advice, just points at data).
- Recruiting seasons are calendar facts (new-grad cycles often open Aug–Oct and internships Jul–Sep for the following summer): treat bundled field-guide dates as tier-2, and verify them only when they are load-bearing and past their `Verify by:` date.

## Tool updating (the bundled ones)

Versions are pinned so behavior is reproducible; treat updates as deliberate changes, not drift: run `uv lock --upgrade` and the full test suite, review fixture deltas, inspect Typst PDF-export release notes before upgrading Typst, and keep fonts vendored.
