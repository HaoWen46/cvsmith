# cvsmith

cvsmith is a small set of agent skills for organizing reusable candidate evidence, producing the strongest role-specific resume a candidate can safely defend, testing the resulting PDF, and learning from real application outcomes.

The product is the workflow, not a scoring program: understand the candidate and target, select and frame evidence, render a professional document, inspect it like a recruiter and interviewer, revise while material value remains, then record what was actually sent.

## Skills

| Skill | Responsibility |
|---|---|
| `candidate-evidence` | Target-neutral source intake, refresh, conflict handling, reversible archive, and portable evidence index |
| `resume-builder` | Target-specific evidence selection, positioning, drafting, Typst rendering, and iteration |
| `jd-analyzer` | Current-posting gates, ranked requirements, level, and evidence targets |
| `resume-evaluator` | Objective PDF checks plus agent-owned exposure, fit, craft, and send recommendation |
| `application-tracker` | At-send target and file identity, stages, outcomes, and scoped learnings |

## Decision boundary

Scripts measure observable properties: YAML validity, exact source mismatches, extraction health, basic parsing, hidden or off-page content, PDF structure, page fill, and bullet wrapping.

Agents decide meaning and usefulness: whether framing is practically defensible, whether the target is worth pursuing, what the page communicates, what remains improvable, and whether the recommendation is `READY TO SEND`, `REVISE`, or `DO NOT APPLY`.

No local script predicts a named employer's parser, judges whether two claims mean the same thing, certifies a candidate's account, or attributes an application outcome to resume wording.

## Install

cvsmith is a repository bundle of five Agent Skills, not a standalone app, package, daemon, or single agent. The [Agent Skills specification](https://agentskills.io/specification) defines what belongs inside each skill directory; it does not define a universal installer or registry.

### Install with your agent

Give a repository-aware agent or harness this instruction:

```text
Install every Agent Skill from https://github.com/HaoWen46/cvsmith using this host's native user-level skill or plugin mechanism. The canonical skills are the five directories under skills/ that contain SKILL.md. If this host cannot install from a repository URL, clone the repository and import or copy those directories without rewriting their contents.
```

The canonical skill roots are `skills/application-tracker/`, `skills/candidate-evidence/`, `skills/jd-analyzer/`, `skills/resume-builder/`, and `skills/resume-evaluator/`. A capable harness can enumerate these roots, read each `SKILL.md`, preserve its sibling resources, and adapt installation to its own supported scope.

The repository URL is enough only when the host can access GitHub and supports repository import or can clone files. The name `cvsmith` alone becomes installable only after a registry searched by that host lists it.

### Claude Code

Use Claude Code's native marketplace flow:

```sh
claude plugin marketplace add HaoWen46/cvsmith
claude plugin install cvsmith@cvsmith
```

### Codex and ChatGPT

Use the native Codex plugin flow:

```sh
codex plugin marketplace add HaoWen46/cvsmith
codex plugin add cvsmith@cvsmith
```

In ChatGPT desktop, the same repository marketplace appears as the `cvsmith` source in the Plugins Directory; selecting the plugin there is the UI equivalent. Public name-only discovery requires publication to the host's plugin directory rather than another repository file.

### Direct skill import

Every canonical directory above is a complete Agent Skill and can be imported independently. Clients commonly scan `~/.agents/skills/` for user scope and `<project>/.agents/skills/` for project scope, although the host's native location takes precedence. To install a checkout into the cross-client user scope on macOS or Linux:

```sh
git clone --depth 1 https://github.com/HaoWen46/cvsmith.git
mkdir -p ~/.agents/skills
cp -R cvsmith/skills/. ~/.agents/skills/
```

If the host does not scan `~/.agents/skills/`, import the same five directories through its skill settings or copy them into its documented native skill directory. Cloud and sandboxed hosts may instead require repository URLs or uploaded archives because they cannot read the user's local filesystem.

To build one upload archive per skill from a checkout:

```sh
uv run scripts/package_release.py
```

The packager writes licensed `dist/<name>.skill` compatibility archives and rejects missing referenced files, invalid metadata, and non-portable paths. Use those archives only with hosts that accept skill uploads.

## Use from a checkout

Create a projection following [the data schema](skills/resume-builder/assets/templates/data-schema.md), then render it:

```sh
skills/resume-builder/scripts/render.sh /absolute/path/resume.yaml -o /absolute/path/resume.pdf
```

Run the PDF battery from `skills/resume-evaluator/`:

```sh
uv run scripts/extract_text.py /absolute/path/resume.pdf --json
uv run scripts/parse_sim.py /absolute/path/resume.pdf --json
uv run scripts/hidden_text_check.py /absolute/path/resume.pdf --json
uv run scripts/lint_structure.py /absolute/path/resume.pdf --json
```

The intended path is to invoke the skills through a capable agent; the commands are the objective substrate, not a standalone resume generator.

## Start the workflow

Give the agent your candidate materials and one current job posting, then ask: `Use cvsmith to organize my evidence and build the strongest defensible resume for this role.` The agent should route source intake, job analysis, resume construction, exact-PDF evaluation, and application tracking through the five focused skills rather than treating cvsmith as a standalone executable.

## Status

The deterministic tools have repository tests, but end-to-end quality still depends on an agent following the skill, reading the actual artifact, and making sound hiring judgments; a green test suite does not establish that behavioral result.

Run the current tests with:

```sh
uv run pytest evals/ -q
```

## Requirements

- Python 3.11+ through [uv](https://docs.astral.sh/uv/)
- [Typst](https://typst.app/) 0.15+ for tagged PDF rendering
- Poppler for the strongest extraction and raster checks

## Personal data

Candidate evidence workspaces, projections, PDFs, and application ledgers belong in a private user workspace, not this repository; gitignore and local file permissions do not prevent cloud sync or a hosted agent from processing content it reads.

Everything under `examples/` and `evals/fixtures/` is synthetic or sanitized.

## License

[MIT](LICENSE)
