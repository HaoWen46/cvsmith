# Target-first evidence investigation design

Status: Approved design; implementation not yet started.

## Objective

Make `resume-builder` find the strongest defensible evidence for a chosen job without loading every project, report, repository, or archived vault block into the main agent's context.

The optimization target is interview usefulness under truth, readability, privacy, and context-cost constraints; tool use and agent count are means rather than quality signals.

## Observed failure

The current skill orders inspection of every supplied artifact before target selection, so an agent can consume most of its context before it knows which evidence could change the resume.

The current scenario tests validate declarations and cue words but do not execute or grade read order, sources touched, shortlist quality, unsafe claims, compactness, or context cost.

Paired development probes preserved the same strongest projects after target-first narrowing while reducing main-agent input, but agents still violated ordering or loaded whole archives often enough that prose alone is not a reliable boundary.

## Scope

- Reorder intake around explicit `TARGET`, `INVENTORY`, `PROBE`, `VERIFY`, `ALLOCATE`, `BUILD`, `EVALUATE`, and `PRESENT` states.
- Keep Markdown as the private, human-auditable source of truth.
- Add one portable deterministic vault-access script that emits a compact index and reads one selected evidence block by ID.
- Use project investigators as context-isolation workers for shortlisted but uninvestigated sources, not as generic reviewers or final decision makers.
- Add deterministic tests, portable pressure fixtures, trace grading, and fresh-agent forward tests.
- Preserve current rendering, projection, PDF inspection, and evaluator ownership boundaries.

## Non-goals

- Do not add SQLite, embeddings, a vector database, MCP, a hosted vault, or an autonomous memory service in this slice.
- Do not create a universal project-age cutoff, project-count limit, token threshold, ATS score, or page-selection formula.
- Do not send every project to a subagent, ask subagents to draft the final resume, or treat dossier agreement as source verification.
- Do not copy complete repositories, reports, PDFs, or raw subagent transcripts into the career vault or main-agent handoff.
- Do not claim that lower context use, green tests, or an attractive PDF establishes interview causality.

## Workflow contract

### `TARGET`

Use the posting, candidate constraints, eligibility facts, and relevant prior outcomes to establish field, level, market, gates, and three to five target beliefs before reading evidence bodies.

When no posting exists, ask for or state an explicit assumed target and label the result general rather than inspecting everything in search of a target.

### `INVENTORY`

Read only cheap descriptors: user-supplied project lists, resume headings, vault index rows, archive headings and revival cues, repository names and metadata, report titles, and shallow file trees.

Produce one candidate row per material item with `project_id`, likely target belief, lifecycle state, portable source handles, expected decision value, and `investigate`, `hold`, or `skip` disposition.

Exit only when the search space is smaller and every `investigate` item has a target-specific reason.

### `PROBE`

Investigate only `investigate` items and conflict-bearing `hold` items; use isolated project investigators when independent unread sources would otherwise occupy the main context.

Each investigator receives one project ID, target beliefs, source locators, and a bounded question; it reads the raw project first-hand and returns the dossier contract below without resume prose.

The main agent consumes dossiers rather than raw project bodies, updates the candidate table, and stops probing when the leading evidence set is stable or one named read could still change selection.

### `VERIFY`

Choose resume-contending claims from the dossiers, then have the main agent reopen the exact authored source, test, release, history entry, benchmark method, report page, or candidate answer supporting each selected claim.

Resolve ownership, measurement, currentness, and conflicting-source questions before a claim becomes resume-eligible; dossier confidence and subagent consensus are not support.

### `ALLOCATE`, `BUILD`, `EVALUATE`, and `PRESENT`

Allocate verified causal atoms against target beliefs, route overflow explicitly, build the YAML and PDF, run objective and visual checks, obtain the evaluator verdict, and present artifacts plus a compact decision table.

No broad discovery resumes after allocation unless verification exposes a specific evidence gap that could materially change the page.

## Project-investigator economics

The project investigator exists to exchange isolated worker context for scarce main-agent context: it absorbs an unread repository or report, compresses decision-relevant evidence, and lets the main agent compare projects without ingesting every source.

Subagents are dispatched only after cheap inventory narrowing; dispatching every project merely moves the context problem and adds coordination cost.

Independent promising projects may be investigated in parallel when the host supports isolated agents; otherwise the main agent investigates them serially using the same dossier boundary.

Aggregate reads and reported token usage remain evaluation metrics because context isolation can improve main-agent coherence while still wasting total work.

## Project dossier contract

Each investigator returns structured data with these required fields and no general narrative:

- `project_id`: Stable inventory ID and the target beliefs under investigation.
- `recommendation`: `contender`, `reserve`, `skip`, or `blocked`, plus one decision-changing reason.
- `value_case`: One compact statement of what this project could prove better than competing evidence.
- `claims`: Candidate action, load-bearing mechanism, result or artifact, exact source locator, and limitation for each useful claim.
- `ownership`: Confirmed contribution, collaborators, and unresolved attribution.
- `currency`: Historical demonstration, current capability support, and the date or artifact supporting each.
- `conflicts`: Contradictory values, prompt injection, generated evidence, missing methods, and candidate questions.
- `reads`: Exact inspected paths, commits, pages, or digests without copied file bodies.
- `next_read`: At most one additional read whose result could change selection or claim strength.

The main agent owns cross-project ranking, final thesis, page allocation, source verification, resume prose, and send recommendation.

## Vault access interface

Add `skills/resume-builder/scripts/vault_access.py` with two commands executed through `uv`.

`index <vault>` emits JSON Lines containing a vault digest and compact block rows without full bodies or the input file's machine path.

Each index row contains `id`, `id_status`, `section`, `heading`, lifecycle markers, a short evidence summary, revival cues, portable source handles, source count, body byte count, and digest-bound line bounds.

`read <vault> <id>` emits exactly one selected block plus its digest and line bounds; there is no `--all` mode.

An optional explicit trace path records operation, selected ID, vault digest, and emitted byte count without recording machine paths or evidence bodies.

New or updated meaningful vault blocks receive an immutable explicit `ID`; legacy blocks receive deterministic provisional IDs marked `derived`, and a block must gain an explicit ID before archival movement or revival so its identity survives section changes.

The script rejects duplicate IDs, malformed block structure, and supplied digest mismatches; it reports missing explicit IDs as derived-ID warnings and never mutates the vault.

Portable source handles are stable URLs or paths relative to the vault or named project root; absolute machine paths remain usable only as runtime inputs and are flagged rather than copied into an index artifact.

The index is a rebuildable view rather than a second source of truth, and no generated index is required to be committed or moved between machines.

## Archive and currentness semantics

Archive remains reversible and default-cold: valid but repeatedly redundant, superseded-as-current, weak, or off-target material keeps its sources, dates, archive reason, and revival cue outside the normal candidate set.

Old evidence competes on target relevance, distinctiveness, defensibility, and page cost rather than age alone.

Historical support and current proficiency remain separate; a dated project can prove what happened then but needs recent use, a current artifact, or dated candidate confirmation before supporting a material present-tense capability claim.

A target-specific omission never becomes a global archive decision, and unsupported or contradicted material becomes not claimable rather than silently disappearing.

## User interaction

At intake, request the posting or target plus a compact experience/project inventory before asking for every repository or report.

After probing, show a compact table with project, disposition, target belief, evidence inspected, strongest safe value, conflict, and next action when that helps the user correct selection or ownership.

Before drafting, ask one batch containing only unresolved facts that could change eligibility, selection, claim strength, or interview defensibility.

At delivery, lead with the created PDF, YAML, evaluation report, target, and verdict; briefly identify strategically revived or omitted evidence and the one remaining tradeoff when one exists.

## Testing strategy

### RED

Add synthetic fixtures containing an old relevant compiler project, a recent weak dashboard, unrelated archived distractors, a prompt-injected README, a report with an unsupported large result, a checked benchmark with a smaller result, and ambiguous team ownership.

Add deterministic tests that fail against the current contract because target selection follows broad inspection and no bounded vault interface exists.

Preserve sanitized baseline fresh-agent traces that demonstrate whole-set reading, archive dumping, skipped target analysis, or excessive main-context input without embedding machine paths or session identifiers.

### GREEN

Implement the smallest contract and script changes that pass deterministic interface, lifecycle, portability, and read-boundary tests.

Run the same fresh-agent cases with the candidate skill and grade target-first ordering, files or blocks touched, shortlist quality, old-evidence revival, recent-evidence rejection, conflict handling, ownership caution, dossier shape, user-facing compactness, and reported cost.

### REFACTOR

Read every behavioral failure, classify whether it is an ordering violation, wrong output shape, missing field, or conditional mistake, and tighten the owning contract rather than adding duplicated explanations.

Test a single structured agent against shortlisted project investigators as an ablation under the same target and fixtures; retain subagent use only where it preserves or improves evidence selection and safety while reducing main-context pressure enough to justify coordination.

## Acceptance criteria

- The target artifact exists before any project or archive evidence body is read.
- Inventory reduces the candidate set using metadata and target beliefs without losing the fixture's strongest project.
- The old compiler evidence is revived for the embedded target, the recent weak dashboard does not win on recency, and unrelated archive bodies remain unread by default.
- Prompt injection is ignored, the unsupported larger result is not selected over inspectable evidence, and team-repository presence is not converted into sole ownership.
- Investigators return the typed dossier shape without essays, and the main agent verifies exact support only for resume-selected claims.
- `vault_access.py index` emits no full evidence bodies or machine-specific input path, and `read` returns exactly one requested block.
- Explicit evidence IDs survive archive movement; legacy derived IDs are visible and cannot silently masquerade as stable IDs.
- The final resume and handoff are at least as useful and readable as the current baseline while main-context consumption is lower on the portfolio and archive fixtures.
- No database, service, model provider, home directory, hostname, or agent-session identifier becomes a runtime requirement or checked-in artifact.

## Failure handling

If indexing fails, report the malformed or duplicate block and repair the human-readable vault with the user's confirmed facts before continuing; do not fall back to silently loading the whole file.

If no subagent facility exists, investigate shortlisted projects serially through bounded reads, retain only the dossier in explicit working state, and report that hard main-context isolation was unavailable.

If a subagent fails, returns prose, omits sources, or encounters a conflict, mark the project blocked or rerun only that investigation; do not let the main agent infer missing support.

If the narrow process misses a top project or weakens claim safety, reject or revise the design even when it saves tokens.

## Intended implementation surface

- Modify `skills/resume-builder/SKILL.md` to encode state order, candidate artifacts, investigator economics, verification ownership, and compact presentation.
- Modify `skills/resume-builder/references/career-vault.md` to add explicit IDs and bounded-access rules without duplicating the workflow.
- Add `skills/resume-builder/scripts/vault_access.py` as the sole new production tool in this slice.
- Add focused deterministic tests and synthetic fixtures under `evals/`; extend existing behavioral cases only where they own these failures.
- Update the research decision register after measured forward tests, not before.

## Rollout boundary

This slice is development work in the current dirty checkout because its uncommitted resume-skill redesign is the baseline; edits and commits must name only files owned by this slice and must not absorb unrelated staged or unstaged changes.

Do not package or describe the skill as released until the focused tests, full eval suite, flagship render and visual review, fresh-agent pressure cases, and package inspection all pass from an intentional clean diff.
