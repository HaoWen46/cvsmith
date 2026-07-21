# resume.yaml — data schema (v0.1)

The contract between the three parts of cvsmith. The **builder** writes this
file, the **templates** (`onecol.typ`, `compact.typ`, `classic.typ`) are pure functions of it,
and the **evaluator** checks that what the template rendered routes back into
these same fields when parsed. Content and presentation stay fully separated:
nothing in this file describes layout, and nothing in a template invents
content.

Conventions:

- Dates are ISO `YYYY-MM` strings; an ongoing entry uses `end: present`.
  Templates own the display formatting (e.g. "Jun 2025 – Present").
- Bullets are plain strings of finished prose. Writing quality (impact-first,
  quantified, no AI-slop vocabulary) is enforced upstream by the builder's
  writing rules — the schema doesn't try to encode it.
- Omitted optional keys mean "don't render this section". No nulls, no empty
  lists — absence is the signal.
- Section order in the rendered PDF is fixed by the template (standard,
  ATS-expected order), not by key order here.
- Every string is plain text. No markup, no Unicode tricks — the evaluator's
  integrity checks will flag anything that doesn't extract identically to how
  it renders.

## Top-level structure

```yaml
meta:                    # optional; knobs for template + evaluator
  target_field: ai-ml    # ai-ml | swe | academic | generic — field conventions
  page_budget: 1         # default 1 for students/early-career
  paper: us-letter       # us-letter (default) | a4 — match the target market
  lang: en               # BCP-47-ish code for PDF metadata + hyphenation
  accent: "#1f3a5f"      # compact template only: accent color (default navy)
  template: compact      # onecol (default) | compact | classic — render.sh
                         # uses this when no -t flag is given, so each
                         # projection re-renders with one command
  bullet_lines: 1        # optional: cap rendered lines per bullet;
                         # render.sh measures the PDF and fails on
                         # violations (scripts/check_bullets.py)

basics:                  # required
  name: Jordan Wu
  email: jordan.wu@example.com
  phone: "+1 555 010 0199"        # optional
  location: Berkeley, CA          # optional; city-level only
  links:                          # optional
    - label: GitHub
      url: https://github.com/jordanwu
    - label: Portfolio
      url: https://jordanwu.dev

summary: >-              # optional; discouraged for early-career (skim cost)
  One to two sentences, only when there is a non-obvious positioning story.

education:               # required for students/early-career
  - institution: University of California, Berkeley
    degree: B.S.
    field: Electrical Engineering and Computer Sciences
    start: 2023-08
    end: 2027-05
    gpa: "3.9/4.0"                # optional; builder decides if it helps
    coursework: [Machine Learning, Operating Systems]   # optional, short
    honors: [Regents' Scholar]                          # optional

experience:              # optional as a whole, but entries are structured
  - organization: Anthropic
    title: ML Engineering Intern
    location: San Francisco, CA   # optional
    start: 2026-06
    end: present
    group: industry               # optional: research | teaching | industry
    tags: [evals, tool use]       # optional: 2-4 domain descriptors; renders
                                  # as a muted tag row (compact only; onecol
                                  # and classic omit tags by design — pick
                                  # compact when tags carry weight)
    bullets:
      - Built an eval harness for tool-use regressions, cutting triage
        time for failed runs from hours to minutes across 40+ suites.

projects:                # optional; often the core section for students
  - name: cvsmith
    summary: agent-skill toolkit for verified resumes   # optional one-liner
    url: https://github.com/HaoWen46/cvsmith            # optional
    stack: [Typst, Python]                              # optional, rendered inline
    start: 2026-07                                      # optional
    end: present                                        # optional
    bullets:
      - Agent-skill toolkit that renders tagged PDFs and adversarially
        verifies them against 2026 screening-pipeline checks.

skills:                  # optional; grouped, never a keyword dump
  - label: Languages
    items: [Python, Rust, TypeScript]
  - label: ML
    items: [PyTorch, evals, RAG, agent frameworks]

publications:            # optional
  - citation: "Wu, J. et al. (2026). Title. Venue."
    url: https://arxiv.org/abs/...                      # optional

awards:                  # optional
  - name: Regional ICPC — 2nd place
    date: 2025-11                                       # optional
```

## Field notes

- **`meta.target_field`** routes the builder to the matching
  `references/fields/*.md` file and tells the evaluator which field
  conventions to score against. It never changes rendering.
- **`basics.links`**: templates print the URL itself — shortened for
  display (scheme stripped; `compact` also strips `www.`) — as both the
  visible text and the hyperlink target, so the URL survives as
  extractable text for screeners. `label` names the link in the data
  file for the builder and user; no template renders it. URLs carrying
  tracking parameters (`utm_*`, `fbclid`, `gclid`, `mc_cid`) fail
  `scripts/validate_yaml.py`.
- **`projects[].stack`**: rendered inline by `onecol` and as the tag row
  by `compact`; `classic` omits it by design (monochrome discipline).
- **`experience` vs `projects`**: paid/formal roles go in `experience`;
  everything else (OSS, research not under a formal title, hackathons) goes
  in `projects`. The evaluator's parse simulation checks that both sections
  route under standard headings ("Experience", "Projects").
- **`experience[].group`** (`research` | `teaching` | `industry`): for
  academic-track CVs (grad school, REUs, fellowships). When *any* entry
  carries a group, the template renders one standard-headed section per
  group — "Research Experience", "Teaching Experience", "Industry
  Experience", in that order — and ungrouped entries fall into the
  industry bucket, so group all entries when you group any. All three
  headings are in the parse simulator's recognized taxonomy. Omit
  `group` everywhere for a single "Experience" section (the industry
  default). See `references/fields/academic.md`.
- **Project right column**: in `onecol` and `classic` a project entry's
  right-hand meta shows its `url` when present, otherwise its date range
  — one slot per entry keeps the skim clean, so prefer `url` for living
  projects and dates for finished ones. `compact` has two meta slots by
  design (url on the name row, dates on the tag row) and renders both
  when both are given — no information is dropped there.
- **`skills`**: groups keep the section honest — 2–4 groups, each a short
  list the person can defend in an interview. The JD-alignment layer scores
  semantic coverage from bullets first; `skills` is a secondary signal.

## Open questions

- ~~Whether `meta.page_budget` > 1 changes template selection or just
  lints.~~ Resolved in M1: it lints only — `render.sh` warns when the
  output exceeds the budget; template choice stays explicit.
- Certifications / languages-spoken sections: add on first real demand
  rather than speculatively.
- ~~Schema validation~~ Decided: `scripts/validate_yaml.py`, run by
  render.sh before every compile. Builder-side beat the evaluator-side
  option because the evaluator's contract is the PDF (it never sees
  the yaml), while the silent-loss class this catches — a typoed
  optional key or section name rendering a clean page with content
  missing — must die before the render, not after.
