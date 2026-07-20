# resume.yaml — data schema (draft v0.1)

The contract between the three parts of cvsmith. The **builder** writes this
file, the **templates** (`onecol.typ`, `compact.typ`) are pure functions of it,
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
  target_field: ai-ml    # ai-ml | swe | generic — selects field conventions
  page_budget: 1         # default 1 for students/early-career

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
    bullets:
      - Built an eval harness for tool-use regressions, cutting triage
        time for failed runs from hours to minutes across 40+ suites.

projects:                # optional; often the core section for students
  - name: cvsmith
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
- **`basics.links`**: templates render the label as the visible text with the
  URL as both hyperlink target and printed text where field conventions
  expect it (papers, portfolios). Bare tracking-parameter URLs are a lint
  error upstream.
- **`experience` vs `projects`**: paid/formal roles go in `experience`;
  everything else (OSS, research not under a formal title, hackathons) goes
  in `projects`. The evaluator's parse simulation checks that both sections
  route under standard headings ("Experience", "Projects").
- **Project right column**: a project entry's right-hand meta shows its
  `url` when present, otherwise its date range — one thing per line keeps
  the skim clean. If both are given, dates are dropped from display (they
  stay in the data), so prefer `url` for living projects and dates for
  finished ones.
- **`skills`**: groups keep the section honest — 2–4 groups, each a short
  list the person can defend in an interview. The JD-alignment layer scores
  semantic coverage from bullets first; `skills` is a secondary signal.

## Open questions

- ~~Whether `meta.page_budget` > 1 changes template selection or just
  lints.~~ Resolved in M1: it lints only — `render.sh` warns when the
  output exceeds the budget; template choice stays explicit.
- Certifications / languages-spoken sections: add on first real demand
  rather than speculatively.
- Schema validation: a small `validate_schema.py` under the evaluator's
  scripts, or JSON Schema shipped next to this file. Decide in M2.
