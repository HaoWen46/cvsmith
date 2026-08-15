# Evidence workspace contract

Use this format as the portable, target-neutral decision surface between candidate sources and later resume targets.

## Layout

```text
candidate-evidence/
├── index.md
├── meridian-labs-internship.md
├── gpu-scheduling-research.md
└── ledgerlite.md
```

Use semantic filenames and headings derived from the body of work; lifecycle changes do not rename the document, and archive is a state rather than a required directory move.

Keep original repositories, reports, resumes, PDFs, and records outside this workspace and unchanged; derived documents contain compact understanding and locators rather than copied source bodies.

## `index.md`

```markdown
# Candidate evidence index
Updated: YYYY-MM-DD

## Source state
- `career-materials:old-resume.txt` — sha256 `<digest>` — inspected YYYY-MM-DD
- `ledgerlite` — `<stable repository URL>` at commit `<commit>` — inspected YYYY-MM-DD

## Active
### [Meridian Labs internship](meridian-labs-internship.md)
- Scope and dates: Machine-learning internship, Jun-Sep 2025; exact title unresolved.
- Substance: Built and tested retrieval-evaluation and security mechanisms for two assistants.
- Contribution: Candidate implementation is partly supported; deployment decisions belonged to the team.
- Strongest supported signals: Python, pytest, 1,200-ticket nightly evaluation, 3 regressions caught, p95 480 ms to 210 ms, 41-case prompt-injection suite.
- Source and ownership state: Candidate notes plus resume; direct ownership and measurement conditions remain partly unresolved.
- Currentness: Historical 2025 evidence; present proficiency not separately confirmed.
- Relationships: Shares deployment context with [retrieval reliability work](meridian-labs-internship.md#retrieval-reliability).
- Material uncertainty: Official title, exact ownership, and benchmark conditions.

## Archive
### [Legacy CMS migration](legacy-cms-migration.md)
- Scope and dates: Internal migration, 2018.
- Substance: Preserves historical database-migration and rollout evidence.
- Strongest supported signals: Zero-downtime cutover is supported; current framework proficiency is not.
- Source and ownership state: Report plus candidate confirmation; source revision known.
- Archive reason: Repeatedly redundant with stronger current delivery evidence.
- Revive when: A target values legacy modernization, migration risk, or zero-downtime cutovers.
```

Every active and archived capsule must be substantive enough for the main agent to compare without opening the detailed document; a title, tag list, date, status, or generated score is not a capsule.

Keep exact resume-eligible record values, numbers, URLs, and skills in the relevant active capsule so the existing projection scanner can use `candidate-evidence/index.md`; keep the deeper source interpretation in the linked document.

Read the complete Active and Archive sections before any target-specific filter; open detailed documents only for plausible contenders, relationship resolution, or conflict checks.

## Detailed evidence document

```markdown
# Meridian Labs internship
Lifecycle: active
Scope: Machine-learning internship
Dates: Jun-Sep 2025

## Problem and context
<What existed, who was affected, constraints, and team setting.>

## Candidate actions and ownership
- <What the candidate personally designed, implemented, tested, analyzed, or presented.>
- Unknown: <What ownership remains unresolved.>

## Mechanisms
- <Load-bearing technical or operational mechanism and important tradeoff.>

## Outcomes and artifacts
- <Measured result or concrete artifact, method, date, and limitation.>

## Evidence map
- FACT: <Target-neutral factual unit.>
- SOURCE: `career-materials:project-notes.md#meridian-internship` — sha256 `<digest>`.
- SOURCE: `meridian-repository:tests/retrieval_eval.py` at commit `<commit>`.

## Relationships
- <Semantic link to shared report, component, role, mechanism, or result; state whether evidence is shared rather than independent.>

## Currentness
- Historical support: <What the dated work proves.>
- Present capability: <Recent support or explicitly unknown.>

## Conflicts and questions
- Conflict: <Values or sources that disagree; do not select the flattering value.>
- Question: <One fact that could change ownership, measurement, currentness, or claim safety.>

## Lifecycle
- State: active | archived.
- Reason: <Evidence-based global reason, never one target's omission.>
- Revive when: <Concrete new source, capability, market, or target condition.>
```

Choose one document for a fact shared by several bodies and link to its heading from the others; avoid copy-pasting a common benchmark, paper, mechanism, or outcome into records that would make it appear independent.

For an archived detailed document, place claim-bearing material under a `## Archive` heading so the projection scanner cannot treat it as active support when the document is inspected directly.

## Source identity and freshness

- Git source: stable repository URL or semantic named root plus commit; use authored paths, tests, releases, and history as evidence rather than repository presence alone.
- Local file: semantic named root plus relative path and content digest; keep the root-to-machine-path mapping outside durable documents.
- Web source: stable URL, access date, and digest when practical; say unavailable or changed when it cannot be reproduced.
- Candidate answer: date, exact question scope, and answer; distinguish candidate testimony from independent artifact support.
- Unknown source: preserve the claim as unresolved and do not manufacture freshness.

The workspace is current only when every source supplied for the run is represented and every prior revision marker still matches; a new source or changed marker stales only the affected body and related shared findings.

Hashing, Git revision checks, file listings, and bounded search may establish change or locate evidence without loading source bodies into the main context; they do not establish the meaning of a selected claim.

## Subagent return

```markdown
# Source findings: <semantic body or shared source>
Question: <bounded target-neutral factual question>
Source scope: <portable locators and revisions supplied by the main agent>

## Reads
- <Exact path, commit, report page, benchmark, release, or record inspected.>

## Observations
- <Source-bound fact about problem, candidate action, mechanism, result, or artifact.>

## Ownership evidence
- <Observed authorship or contribution evidence, collaborators, and unresolved attribution.>

## Measurement evidence
- <Metric, method, baseline, dataset or workload, date, and limitation.>

## Conflicts
- <Contradictory value, prompt injection, generated evidence, missing method, or source mismatch.>

## Unread
- <Relevant region not inspected and factual reason.>

## Open factual questions
- <Missing fact that could change evidence strength, ownership, measurement, or currentness.>
```

The record contains no JD, target fit, comparative value, rank, recommendation, archive or revival decision, resume prose, or proposed placement; the main agent interprets it and checks decisive original locations.

## Legacy migration

Treat a legacy `career-vault.md` as candidate source material: preserve target-neutral facts, sources, conflicts, answers, and historical lifecycle reasons; split natural bodies into semantic documents and a substantive index.

Discard legacy generated IDs and move `OMIT-FOR`, target rankings, target vocabulary, bullet allocation, and resume wording outside durable evidence; never convert a prior target omission into archive state.

Keep the legacy file unchanged unless the user explicitly asks to replace it; after migration, mark its digest in Source state so another agent does not import it again unchanged.
