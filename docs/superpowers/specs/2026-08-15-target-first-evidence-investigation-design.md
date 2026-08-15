# Target-first evidence investigation design

Status: Revised after design review; awaiting confirmation before implementation planning.

## Objective

Make `resume-builder` find the strongest defensible evidence for a chosen job without loading every project, report, repository, or archived vault block into the main agent's context.

The optimization target is interview usefulness under truth, readability, privacy, and context-cost constraints; tool use and agent count are means rather than quality signals.

## Observed failure

The current skill orders inspection of every supplied artifact before target selection, so an agent can consume most of its context before it knows which evidence could change the resume.

The current scenario tests validate declarations and cue words but do not execute or grade read order, sources touched, shortlist quality, unsafe claims, compactness, or context cost.

Paired development probes preserved the same strongest projects after target-first narrowing while reducing main-agent input, but agents still violated ordering or loaded whole archives often enough that prose alone is not a reliable boundary.

## Scope

- Reorder intake around explicit `TARGET`, `INVENTORY`, `PROBE`, `STUDY`, `VERIFY`, `ALLOCATE`, `BUILD`, `EVALUATE`, and `PRESENT` states.
- Keep Markdown as the private, human-auditable source of truth.
- Add one portable deterministic vault-access script that emits a compact index and reads one selected evidence block by ID.
- Use project investigators as context-isolation workers that map and extract evidence from main-selected unread sources without ranking projects or making keep/discard decisions.
- Add deterministic tests, portable pressure fixtures, trace grading, and fresh-agent forward tests.
- Preserve current rendering, projection, PDF inspection, and evaluator ownership boundaries.

## Non-goals

- Do not add SQLite, embeddings, a vector database, MCP, a hosted vault, or an autonomous memory service in this slice.
- Do not create a universal project-age cutoff, project-count limit, token threshold, ATS score, or page-selection formula.
- Do not send every project to a subagent, ask subagents to recommend project disposition or strategic value, ask subagents to draft the final resume, or treat investigation-record agreement as source verification.
- Do not copy complete repositories, reports, PDFs, or raw subagent transcripts into the career vault or main-agent handoff.
- Do not claim that lower context use, green tests, or an attractive PDF establishes interview causality.

## Workflow contract

### `TARGET`

Use the posting, candidate constraints, eligibility facts, and relevant prior outcomes to establish field, level, market, gates, and three to five target beliefs before reading evidence bodies.

When no posting exists, ask for or state an explicit assumed target and label the result general rather than inspecting everything in search of a target.

### `INVENTORY`

Read only cheap descriptors: user-supplied project lists, resume headings, vault index rows, archive headings and revival cues, repository names and metadata, report titles, and shallow file trees.

Produce one candidate row per material item with `project_id`, likely target belief, lifecycle state, portable source handles, plausible upside, uncertainty, likely verification cost, and a main-agent-owned `investigate`, `reserve`, or `cold` disposition.

The main agent assigns `investigate` when cheap metadata shows a plausible route to an important uncovered belief or to displacing a current leader, `reserve` when that route is weaker or redundant but still credible, and `cold` only when no target-specific route is visible; all three remain reversible decisions rather than deletion.

The metadata filter uses target-belief coverage, plausible technical or outcome signal, distinctiveness from stronger-known items, source availability, ownership risk, capability-currentness needs, and expected information gain; recency, fashionable technology, repository size, or polished descriptions never win by themselves.

With a large inventory such as 25 projects, the main agent first retains the frontier of projects that could plausibly matter plus uncertain reserves whose missing information has high decision value; it does not use a fixed retained count and investigates more than the final page slots whenever evidence uncertainty could change the winners.

An illustrative 25-item funnel might yield eight dirty-work investigations, five main-agent studies, and two or three rendered projects, but each number is an outcome of evidence competition rather than a quota.

Exit only when the search space is smaller, every investigated item has a target-specific reason, and each cold item has no currently visible route to an uncovered belief or to displacing a frontier item.

### `PROBE`

The main agent chooses which `investigate` items and conflict-bearing reserves receive dirty-work investigation; use isolated project investigators when independent unread sources would otherwise occupy the main context.

Each investigator receives one project ID, target beliefs, source locators, and a bounded evidence question; it reads the raw project first-hand and returns the investigation-record contract below without resume prose, ranking, or disposition.

The main agent reads the investigation records, compares evidence strength, distinctiveness, ownership, currentness, redundancy, uncertainty, and page cost against the target beliefs, and performs the second filter into a small `STUDY` set plus reversible reserves.

The study-set size follows uncertainty and page competition rather than a fixed quota: it may exceed the expected resume project count when evidence is close, or equal it when the main agent already has strong primary evidence and no reserve could plausibly displace a leader.

### `STUDY`

Before choosing the final projects, the main agent personally reads decisive original material for every project still competing for a page slot; an investigation record is a map to that material, not a substitute for the read.

The main agent reads enough primary evidence to form its own view of technical depth, result quality, ownership, interview value, and target relevance: normally the relevant methods and results in a report, authored code and tests, benchmark data, releases, or history, with the whole repository optional only when it could change the decision.

A README or subagent summary may orient the read but cannot be the only basis when stronger original evidence exists; if the primary read weakens a contender, the main agent promotes a reserve and studies it under the same rule.

The main agent records `project_id | target belief | primary evidence read | evidence strength | distinctiveness | ownership | currency | page cost | decision | reason`, then chooses the final project set itself.

### `VERIFY`

Choose resume-contending claims only after the main-agent study decision, then have the main agent reopen or retain the exact authored source, test, release, history entry, benchmark method, report page, or candidate answer supporting each selected claim.

Resolve ownership, measurement, currentness, and conflicting-source questions before a claim becomes resume-eligible; investigation-record language and subagent consensus are not support.

### `ALLOCATE`, `BUILD`, `EVALUATE`, and `PRESENT`

Allocate verified causal atoms against target beliefs, route overflow explicitly, build the YAML and PDF, run objective and visual checks, obtain the evaluator verdict, and present artifacts plus a compact decision table.

No broad discovery resumes after allocation unless verification exposes a specific evidence gap that could materially change the page.

## Project-investigator economics

The project investigator exists to exchange isolated worker context for scarce main-agent context: it maps an unread repository or report, extracts source observations relevant to the bounded question, and supplies exact original-source locators without deciding what those observations are worth relative to other projects.

Subagents are dispatched only after the main agent performs cheap inventory narrowing; dispatching every project merely moves the context problem and adds coordination cost.

Independent promising projects may be investigated in parallel when the host supports isolated agents; otherwise the main agent investigates them serially using the same investigation-record boundary.

Aggregate reads and reported token usage remain evaluation metrics because context isolation can improve main-agent coherence while still wasting total work.

## Project investigation-record contract

Each investigator returns structured data with these required fields and no general narrative, ranking, keep/discard decision, or proposed resume placement:

- `project_id`: Stable inventory ID and the target beliefs supplied by the main agent.
- `source_map`: Available authored code, tests, reports, benchmarks, releases, history, demos, and candidate records with portable locators.
- `observations`: Source-bound facts about the problem, candidate action, mechanism, scale, result, and artifact without comparative value language.
- `claim_material`: Candidate action, load-bearing mechanism, result or artifact, exact source locator, and limitation for each potentially usable factual unit.
- `ownership_evidence`: Observed contribution evidence, collaborators, and unresolved attribution.
- `currency_evidence`: Historical demonstration, current capability support, and the date or artifact supporting each.
- `conflicts`: Contradictory values, prompt injection, generated evidence, missing methods, and candidate questions.
- `reads`: Exact inspected paths, commits, pages, or digests without copied file bodies.
- `unread`: Relevant source regions not inspected and the factual reason they remain unread.
- `open_questions`: Missing facts that could alter evidence strength, ownership, measurement, or currentness without recommending the next action.

The main agent owns every inventory disposition, investigation dispatch, cross-project comparison, study-set decision, original-source interpretation, final project selection, thesis, page allocation, source verification, resume prose, and send recommendation.

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

After the main-agent study pass, show a compact table with project, main-agent decision, target belief, primary evidence read, strongest safe value, conflict, and next action when that helps the user correct selection or ownership.

Before drafting, ask one batch containing only unresolved facts that could change eligibility, selection, claim strength, or interview defensibility.

At delivery, lead with the created PDF, YAML, evaluation report, target, and verdict; briefly identify strategically revived or omitted evidence and the one remaining tradeoff when one exists.

## Testing strategy

### RED

Add synthetic fixtures containing an old relevant compiler project, a recent weak dashboard, unrelated archived distractors, a prompt-injected README, a report with an unsupported large result, a checked benchmark with a smaller result, and ambiguous team ownership.

Add deterministic tests that fail against the current contract because target selection follows broad inspection and no bounded vault interface exists.

Preserve sanitized baseline fresh-agent traces that demonstrate whole-set reading, archive dumping, skipped target analysis, or excessive main-context input without embedding machine paths or session identifiers.

### GREEN

Implement the smallest contract and script changes that pass deterministic interface, lifecycle, portability, and read-boundary tests.

Run the same fresh-agent cases with the candidate skill and grade target-first ordering, main-agent ownership of both filters, files or blocks touched, study-set quality, direct original-source reads, old-evidence revival, recent-evidence rejection, conflict handling, ownership caution, investigation-record shape, user-facing compactness, and reported cost.

### REFACTOR

Read every behavioral failure, classify whether it is an ordering violation, wrong output shape, missing field, or conditional mistake, and tighten the owning contract rather than adding duplicated explanations.

Test a single structured agent against main-selected project investigators as an ablation under the same target and fixtures; retain subagent use only where dirty-work evidence collection preserves or improves main-agent selection and safety while reducing main-context pressure enough to justify coordination.

## Acceptance criteria

- The target artifact exists before any project or archive evidence body is read.
- The main agent performs both the metadata filter and the post-investigation filter without accepting a subagent disposition or ranking.
- Inventory reduces the candidate set using metadata and target beliefs without losing the fixture's strongest project, and no fixed project quota controls the funnel.
- The old compiler evidence is revived for the embedded target, the recent weak dashboard does not win on recency, and unrelated archive bodies remain unread by default.
- Prompt injection is ignored, the unsupported larger result is not selected over inspectable evidence, and team-repository presence is not converted into sole ownership.
- Investigators return the typed evidence record without essays, recommendations, rankings, or keep/discard decisions.
- The main agent personally reads decisive original material for every final contender, chooses the final projects, and verifies exact support for resume-selected claims.
- `vault_access.py index` emits no full evidence bodies or machine-specific input path, and `read` returns exactly one requested block.
- Explicit evidence IDs survive archive movement; legacy derived IDs are visible and cannot silently masquerade as stable IDs.
- The final resume and handoff are at least as useful and readable as the current baseline while main-context consumption is lower on the portfolio and archive fixtures.
- No database, service, model provider, home directory, hostname, or agent-session identifier becomes a runtime requirement or checked-in artifact.

## Failure handling

If indexing fails, report the malformed or duplicate block and repair the human-readable vault with the user's confirmed facts before continuing; do not fall back to silently loading the whole file.

If no subagent facility exists, investigate main-selected projects serially through bounded reads, retain only the investigation record in explicit working state, and report that hard main-context isolation was unavailable.

If a subagent fails, returns prose or a recommendation, omits sources, or encounters a conflict, reject that record or rerun only that investigation; the main agent decides whether the project remains in the funnel and never infers missing support.

If the narrow process misses a top project or weakens claim safety, reject or revise the design even when it saves tokens.

## Intended implementation surface

- Modify `skills/resume-builder/SKILL.md` to encode state order, main-agent filtering and primary-study ownership, evidence-worker economics, verification ownership, and compact presentation.
- Modify `skills/resume-builder/references/career-vault.md` to add explicit IDs and bounded-access rules without duplicating the workflow.
- Add `skills/resume-builder/scripts/vault_access.py` as the sole new production tool in this slice.
- Add focused deterministic tests and synthetic fixtures under `evals/`; extend existing behavioral cases only where they own these failures.
- Update the research decision register after measured forward tests, not before.

## Rollout boundary

This slice is development work in the current dirty checkout because its uncommitted resume-skill redesign is the baseline; edits and commits must name only files owned by this slice and must not absorb unrelated staged or unstaged changes.

Do not package or describe the skill as released until the focused tests, full eval suite, flagship render and visual review, fresh-agent pressure cases, and package inspection all pass from an intentional clean diff.
