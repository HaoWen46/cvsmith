---
name: resume-evaluator
description: Review, test, and improve a resume PDF before it is sent. Use for ATS and extraction checks, hidden-text and structure inspection, target-fit review against a job analysis, practical claim-risk review, recruiter skim simulation, version comparison, or a final send decision. Objective scripts report observable file behavior; the agent reads the actual PDF and owns the READY TO SEND, REVISE, or DO NOT APPLY recommendation.
---

# resume-evaluator

Decide whether this exact resume should be used for this target and identify the smallest set of changes that would materially improve the candidate's odds.

All `scripts/` and `references/` paths below are relative to this skill directory.

## Inputs

Require the PDF; accept the YAML, candidate evidence index, selected evidence documents, decisive original sources, legacy career vault, and jd-analyzer output when available, and state which inputs were absent rather than silently assuming them.

Read `references/rubric.md` for target, exposure, and CRAFT judgment; use `references/failure-modes.md` only when an objective layer reports or suggests that class of defect.

## 1. Inspect the artifact first

Open every rendered page before reading build notes; judge the hierarchy, density, whitespace, wrapping, visual finish, and what a six-second skim makes memorable.

When fresh-reader support exists, ask a fresh-context reader to inspect the PDF plus the target analysis and return its remembered thesis, strongest evidence, doubts, and recommended changes.

## 2. Run the objective battery

Run all four programs against the same current PDF and retain their JSON reports:

```sh
uv run scripts/extract_text.py resume.pdf --json > L0.json
uv run scripts/parse_sim.py resume.pdf --json > L1.json
uv run scripts/hidden_text_check.py resume.pdf --json > L2.json
uv run scripts/lint_structure.py resume.pdf --json > L3.json
```

Each program exits `0` when no check fails, `1` when it found a failure, and `2` when it could not run; warnings remain visible and require judgment but do not become failures by wording alone.

Confirm each report names the current PDF hash before relying on it; rerun a stale report instead of copying its result forward.

Interpret the layers narrowly: L0 tests extraction health, L1 tests basic field routing, L2 tests manipulation and invisible-content risk, and L3 tests structural compatibility; none predicts a particular employer's parser or hiring decision.

## 3. Review source exposure

When YAML and a candidate evidence index or legacy vault are available, run the builder's `check_projection.py` through the builder skill; fix its exact record, number, URL, or skill mismatches, then review each listed claim against selected evidence and decisive originals yourself.

Classify practical exposure directly: record-risk contradictions likely to surface in a background, reference, credential, or public-artifact check are blockers; framing that a candidate cannot explain naturally under a skeptical interview is high priority; assertive but defensible framing with no realistic contradiction is acceptable.

Do not require public proof for every claim and do not mistake unverifiable for unsafe; the question is whether ordinary hiring scrutiny is likely to expose a contradiction or make the phrasing collapse.

## 4. Review target fit

Read the jd-analyzer output and compare every gate and ranked must-have with visible resume evidence; score each requirement `strong`, `credible`, `weak`, or `absent` and cite the page line that carries it.

A hard eligibility gate that is not met leads to `DO NOT APPLY`; an unconfirmed gate leads to `REVISE` until answered; missing evidence for a must-have leads to `REVISE` only when a defensible reframing, selection, or one focused question can materially improve it.

Also judge vocabulary, space allocation, and level calibration; a resume can mention every requirement and still misallocate its strongest real estate.

Without a posting, evaluate against the stated field and level and label target fit as general rather than pretending there was a requirement set.

## 5. Review hiring craft

Use the two-pass method in `references/rubric.md`: first record what the page communicates at a skim, then probe every major line for specificity, credibility, differentiation, and interview survivability.

Report CRAFT as a diagnostic `0–10` score with reasons, not a software gate; no numeric score is a completion threshold.

An available high-value improvement blocks `READY TO SEND` even at a high score; a thin but intentional resume may be ready at a lower score when no stronger evidence or framing is available without increasing practical risk.

## 6. Make one recommendation

- `DO NOT APPLY` when a hard eligibility gate fails, a likely external contradiction remains, or the role is materially outside the candidate's plausible positioning and tailoring cannot change that.
- `REVISE` when an objective check failed or could not run, a practical-exposure issue remains, a required fact is unresolved, or a specific accessible change is likely to materially improve target fit or the human read.
- `READY TO SEND` when objective failures are absent, gates are met, the claims are practically defensible, target requirements are credibly represented, the page looks professionally normal, and no accessible high-value improvement remains.

Optional polish never blocks readiness; identify it as optional and keep it out of the required fix list.

## Report

Write one compact report:

```markdown
# Resume evaluation: <file>
Target: <role or general field/level>
Recommendation: READY TO SEND | REVISE | DO NOT APPLY

## Why
<two to four sentences naming the decisive evidence>

## Objective checks
| Layer | Result | Evidence |
|---|---|---|

## Target fit
| Requirement or gate | Evidence | Read |
|---|---|---|

## Practical exposure
<none, or ranked record-risk and interview-risk findings>

## CRAFT
Score: <n>/10
Skim thesis: <one sentence>
Level read: <below | at | above target bar, with evidence>

## Required changes
<only changes blocking the recommendation; write `None` when ready>

## Optional improvements
<small tradeoffs that do not block sending>
```

Every finding must name the observed problem, why it matters in practice, and the concrete redesign; vague advice such as “improve impact” is not a finding.

## Iteration and comparison

When invoked by the builder, return control after each ranked review so the builder can fix the source, re-render, and rerun checks; evaluate the new artifact, not the previous report.

When comparing versions, hold the target constant, inspect both PDFs blind when possible, and choose the version more likely to earn the interview; never average scores when one version has a decisive gate or exposure defect.
