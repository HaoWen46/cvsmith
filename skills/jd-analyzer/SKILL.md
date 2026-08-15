---
name: jd-analyzer
description: Use when the user provides or links a job description, asks whether they qualify, wants the real must-haves and gates, needs a requirement-ranked targeting brief, or compares roles. Analyze each current posting separately for resume-builder and resume-evaluator. Do not use for candidate-history intake, resume drafting, PDF review, or application tracking.
---

# jd-analyzer

Turn one current posting into the target contract that the builder selects evidence against and the evaluator reviews against.

Read `references/requirement-taxonomy.md` before classifying requirements.

## 1. Capture the source

Use the posting the user supplied; when given a URL, fetch it fresh because postings change or disappear, and record the source URL and access date.

Save a plain-text snapshot beside the analysis when a workspace is available and the target will be used beyond this turn, preserving the wording and line breaks; number its lines for references without altering the snapshot itself.

Treat the snapshot and analysis as separate, target-specific, disposable working files rather than candidate evidence; keep them while the target is active or needed to identify what was sent against, and discard them when stale after any required at-send identity is recorded.

If the posting is unavailable, use a user-supplied copy and label it as such; do not reconstruct requirements from a title or company reputation.

## 2. Read the whole posting

Identify title, company, location, work arrangement, target market, application deadline when stated, and the scoped seniority implied by responsibilities rather than title alone.

Read every responsibility and qualification line; classify requirement-bearing lines as a gate, ranked must-have, or nice-to-have, and keep benefits, mission language, and generic culture prose out of resume targeting.

Anchor every classified requirement to a short quote and source line; combine repeated lines into one requirement only when all contributing source lines are cited.

Do not manufacture a numeric coverage certificate for this judgment; the cited inventory is what lets the next agent inspect omissions.

## 3. Settle gates first

A gate must be binary, externally settled, untailorable, and disqualifying even for an otherwise exceptional candidate; common gates are work authorization, clearance, required licensure, date-bound enrollment or graduation status, and hard location constraints.

Years of experience, tool lists, degree-field preferences, seniority, and any requirement with “or equivalent” are ranked requirements, not gates.

Use supplied records or the user's direct answer to mark each gate `met`, `not met`, or `unconfirmed`; ask one compact question only when an unconfirmed gate would change whether tailoring is worth doing.

If a gate is not met, recommend `DO NOT APPLY` for this posting and state the practical reason; still produce the brief when the user wants it for comparison or a future role.

## 4. Rank what matters

Rank must-haves by title relevance, repetition, specificity, placement, and explicit requirement language; distinguish core work from a long wish list.

For each requirement, write an evidence target describing what a skeptical reviewer would accept: an artifact, visible mechanism, scale, measured result, ownership, or collaborator rather than a keyword.

Decode the practical level from scope and autonomy; note contradictions such as a junior title with senior responsibilities or a broad role spanning several specialties.

Record the posting's useful vocabulary and register only where it should naturally influence resume wording.

## 5. Write the brief

Save `jd-<company>-<role>.md` beside the snapshot and use this compact structure:

```markdown
# JD analysis: <title> @ <company>
Source: <URL or supplied copy>, accessed <YYYY-MM-DD>
Snapshot: <path>; sha256 <digest>
Market: <location and work arrangement>
Decoded level: <level and one-line basis>
Recommendation: APPLY | CONFIRM GATE | DO NOT APPLY

## Gates
| Gate | Source | Status | Basis |
|---|---|---|---|

## Must-haves
| Rank | Requirement | Source | Evidence target |
|---|---|---|---|

## Nice-to-haves
| Requirement | Source | Evidence target |
|---|---|---|

## Vocabulary and register
<only terms and tone that should influence the resume>

## Notes
<level contradictions, unusual scope, deadline, or application risk>
```

Quotes stay short and source line references stay explicit; the analysis is a decision aid, not a restatement of the posting.

## 6. Hand off the target

Tell the user in one paragraph what the role is really hiring for, whether any gate blocks it, the candidate's strongest likely angle, and the largest evidence gap.

Pass the analysis file unchanged to `resume-builder` and `resume-evaluator`; they may challenge a classification by returning to the cited source, but they must not silently improvise a different target.

For multiple postings, analyze each separately, then compare shared requirements and role-specific deltas in temporary working state; never blend them into an average job or write target conclusions into candidate evidence.
