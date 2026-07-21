# Maintenance — keeping the perishable parts true

Most of cvsmith is stable mechanics. The parts that decay are listed
here, with their re-verification protocol. The design principle:
**users' agents never re-research doctrine at query time — the repo
re-verifies on a schedule.** CI checks the calendar (monthly cron
warns/fails on stale stamps); a maintainer (human or scheduled agent)
does the refresh.

## Stamp convention

Perishable references carry, near the top:

```
Last verified: YYYY-MM
Verify by: YYYY-MM
```

`.github/scripts/check_freshness.py` scans every `skills/**/references/*.md`:
past-due stamps warn on normal CI runs and fail the monthly scheduled
run. When re-verification finds nothing changed, still bump both dates
— "recently confirmed" is information.

## What to re-verify, where, how

| Claim cluster | Lives in | Cadence | How to check |
|---|---|---|---|
| Screening-pipeline behavior (semantic matching, manipulation flags, hidden-text detection stats) | resume-builder `references/screening-2026.md` | 12 mo | search recent vendor docs (Workday/Greenhouse/Ashby release notes), arXiv for injection-detection papers, Jobscan/ATS-research posts |
| Hot evidence & market direction for AI/ML | resume-builder `references/fields/ai-ml.md` | 6 mo (each recruiting season: ~Feb, ~Aug) | Indeed Hiring Lab, BLS JOLTS, a scan of 20 current JD postings for the skill vocabulary actually asked |
| Recruiting-season calendar, ghost-posting signals | jd-analyzer `references/requirement-taxonomy.md` | 12 mo | new-grad hiring guides, recruiter-community write-ups |
| Board API endpoints (Greenhouse/Lever/Ashby) | jd-analyzer `SKILL.md` (§1 Ingest) | opportunistic (they break loudly) | curl one known company per endpoint |
| Regional conventions (photo/personal-data/page norms) | resume-builder `references/regional.md` | 24 mo | spot-check 3 drifting cells (DACH photo, Korea/Singapore photo decline, Singapore personal-data) against current local career-center or government employment guidance |

## Tool updates (pinned, deliberate)

- Quarterly: `uv lock --upgrade && uv run pytest evals/ -q` — the
  planted-fixture tests are the regression net; an extractor behavior
  change surfaces as a test failure, not silent drift.
- Typst: bump `TYPST_VERSION` in ci.yml when release notes touch PDF
  export/tagging; re-run the suite; re-render `examples/` PDFs.
- Fonts are vendored and never drift.

## Why not re-verify per query (recorded so it isn't relitigated)

Per-query research would (a) burn latency/cost on facts that change
twice a year, (b) churn advice — identical questions on consecutive
days getting different doctrine destroys user trust and makes
evaluator scores incomparable across iterations, and (c) couple every
user session to network availability. The job market moves in
~6-month seasons; the calendar, not the query stream, is the right
trigger. Task-scoped facts (the posting, the company) are exempt —
those are always fetched fresh because they're *inputs*, not doctrine.
