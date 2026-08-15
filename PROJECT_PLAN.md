# cvsmith product contract

## Objective

Increase a candidate's chance of reaching interviews and offers by helping an agent produce the strongest role-specific resume available from the candidate's real material, while avoiding claims or presentation tactics likely to backfire under ordinary hiring scrutiny.

Engineering exists to support that outcome; no checker score, PDF build, or internal completion label is the product goal.

## Workflow

1. Build or refresh a reusable target-neutral candidate evidence workspace from supplied material and focused follow-up questions.
2. Analyze the actual current posting into strict eligibility gates, ranked requirements, level, market, and evidence targets.
3. Choose a positioning thesis, select the strongest relevant evidence, and write assertive interview-defensible content.
4. Render a conventional single-column tagged PDF and run objective compatibility checks.
5. Have an agent inspect the actual PDF for practical exposure, target fit, recruiter skim, interviewer probing, and remaining high-value improvements.
6. Iterate until the recommendation is `READY TO SEND`, or stop with `DO NOT APPLY` when the target itself is nonviable.
7. Bind a confirmed application to its target, recommendation, and sent file hashes; record later stages and use comparable patterns to inform the next variant.

## Architecture

| Component | Owns | Does not own |
|---|---|---|
| `candidate-evidence` | Source intake, revision checks, conflicts, relationships, currentness, and reversible lifecycle | JD fit, comparative resume selection, prose, or page placement |
| `resume-builder` | Target-specific evidence selection, positioning, prose, layout, rendering, iteration | Durable source intake, global archive decisions, or final independent recommendation |
| `jd-analyzer` | Posting-grounded gates and ranked target contract | Candidate evidence invention or resume prose |
| `resume-evaluator` | Objective battery orchestration and human hiring judgment | Automated meaning or employer-outcome prediction |
| `application-tracker` | At-send identity, status history, descriptive outcome learning | Causal claims about variants |

The candidate evidence index plus semantic documents are the reusable private source record; the JD analysis is a separate disposable target contract; the resume YAML is one target-specific projection; the PDF is the application artifact; the evaluation report is the current decision; the application ledger is the feedback record.

## Invariants

- Record-risk facts remain consistent with records or likely third-party checks; favorable framing may be aggressive when the candidate can defend it naturally and no realistic contradiction is exposed.
- Eligibility gates are narrow binary constraints; years, tools, degree preferences with equivalency, and seniority are ranked evidence requirements rather than automatic refusal rules.
- Objective software reports only observable file or exact-value properties; lexical similarity never certifies meaning, defensibility, quality, or completion.
- CRAFT is a diagnostic quality score; no numeric threshold ends iteration.
- `READY TO SEND` requires no objective failure, all gates met, acceptable practical exposure, credible target representation, professional presentation, and no accessible high-value improvement.
- Prepared is not applied; an outcome is attributed only to the target and bytes actually sent.
- Outcome comparisons are scoped associations, never causal proof.
- Missing input or verification remains explicit and never becomes a pass by default.
- The main agent reads every substantive index capsule before target filtering, chooses every investigation and lifecycle change, checks decisive originals, and owns every selection; subagents return bounded source facts only.
- Age, fashionable technology, and a prior target omission never decide durable lifecycle alone; archived evidence retains substance, sources, reason, and a concrete revival condition.

## Objective tools

The renderer validates YAML, checks exact resume/evidence-index mismatches when an index is available, compiles with vendored fonts, checks extractability, measures page fill, and measures bullet wrapping before atomically publishing the PDF.

The evaluator battery independently checks text extraction, basic field routing, hidden or off-page content, and PDF structure; each report includes the PDF digest it read.

These tools reduce avoidable compatibility and manipulation risk; they do not simulate a proprietary employer system or replace direct artifact review.

## Success evidence

Artifact evidence: objective checks pass, reviewers remember the intended thesis, important requirements have visible credible evidence, claims survive probing, and the page has no accessible high-value revision.

Behavioral evidence: independent agents can follow the skills on unseen cases, reach sensible recommendations, and avoid threshold optimization or unsupported confidence.

Outcome evidence: applied rows retain exact at-send context, stage progression is recorded, and repeated patterns across comparable targets guide future variants without overstating causality.

## Current state

The current checkout contains an uncommitted redesign; an installed or previously built archive does not contain this contract.

Remaining release work is evidence, not more architecture: run focused and full deterministic tests, rebuild and inspect the flagship example, pressure-test all five skills with fresh agents on contrasting cases, inspect packaged archives, and record the limits observed.
