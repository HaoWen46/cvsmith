# cvsmith

cvsmith is a small set of agent skills for organizing reusable candidate evidence, producing the strongest role-specific resume a candidate can safely defend, testing the resulting PDF, learning from real application outcomes, and optionally planning a current JD-specific project that could create missing hiring evidence.

The product is the workflow, not a scoring program: understand the candidate and target, select and frame evidence, render a professional document, inspect it like a recruiter and interviewer, revise while material value remains, then record what was actually sent.

## Skills

| Skill | Responsibility |
|---|---|
| `candidate-evidence` | Target-neutral source intake, refresh, conflict handling, reversible archive, and portable evidence index |
| `resume-builder` | Target-specific evidence selection, positioning, drafting, Typst rendering, and iteration |
| `jd-analyzer` | Current-posting gates, ranked requirements, level, and evidence targets |
| `hiring-project-planner` | Current research, target reduction, and a bounded project-and-demonstration handoff or explicit no-project decision; never implementation |
| `resume-evaluator` | Objective PDF checks plus agent-owned exposure, fit, craft, and send recommendation |
| `application-tracker` | At-send target and file identity, stages, outcomes, and scoped learnings |

## Decision boundary

Scripts measure observable properties: YAML validity, exact source mismatches, extraction health, basic parsing, hidden or off-page content, PDF structure, page fill, and bullet wrapping.

Agents decide meaning and usefulness: whether framing is practically defensible, whether the target is worth pursuing, what the page communicates, what remains improvable, and whether the recommendation is `READY TO SEND`, `REVISE`, or `DO NOT APPLY`.

No local script predicts a named employer's parser, judges whether two claims mean the same thing, certifies a candidate's account, or attributes an application outcome to resume wording.

## Quickstart

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

## Install

Use the skill directories directly from a checkout, symlink or copy each `skills/<name>/` directory into the personal skill directory recognized by the host, or package all six:

```sh
uv run scripts/package_release.py
```

The packager writes `dist/<name>.skill` archives and rejects missing referenced files or invalid skill metadata.

## Status

This checkout contains uncommitted workflow changes; do not infer its behavior from an installed or previously built archive.

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
