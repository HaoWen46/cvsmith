# cvsmith research index

Status: Active evidence register; research notes are not production behavior contracts unless a later design or implementation record adopts them.

Updated: 2026-08-15

## Read first

- [Agent behavior, portfolio retrieval, and hiring evidence](agent-behavior-and-hiring-evidence.md) records the current primary-source review, local pressure tests, adopted evidence boundary, unsupported claims, and remaining validation before release claims.

## Research-note contract

- Separate `OBSERVATION`, `LIMITATION`, `BOUNDED INFERENCE`, and `UNRESOLVED` so an agent cannot silently promote a benchmark result or plausible mechanism into product truth.
- Prefer real hiring outcomes for resume claims and paired end-to-end agent runs with objective traces for workflow claims; recruiter simulations, narrow benchmarks, vendor studies, and anecdotes may generate hypotheses but do not set policy alone.
- Record a stable primary URL, study design, measured outcome, transfer limit, and cvsmith consequence for every adopted finding.
- Keep machine-specific paths, user data, credentials, copied source corpora, and ephemeral agent transcripts out of research notes.
- Keep source truth in ordinary portable files; any search index, database, or cache must be rebuildable and must not become the only copy of candidate evidence.
- Recheck claims dated 2026 or marked as preprints before production adoption because revisions may change methods or results.
