# resume.yaml schema

`resume.yaml` is one target-specific projection of candidate evidence; templates render its content without rewriting it.

## Rules

- Omit optional keys instead of using `null`, blank strings, or empty lists.
- Use quoted `YYYY-MM` dates; `end: present` is allowed for ongoing entries and an award may use a quoted year.
- Keep bullets and list items as plain strings; quote any YAML string containing `: `.
- Keep markup and layout out of YAML; choose presentation through `meta`.
- `meta.thesis` is a private positioning note and never renders.

## Complete shape

```yaml
meta:                              # optional
  target_field: ai-ml              # ai-ml | swe | academic | generic
  target_level: intern             # see levels below
  template: compact                # onecol | compact | classic
  paper: us-letter                 # us-letter | a4
  page_budget: 1                   # positive integer
  lang: en                         # optional language code
  accent: "#1f3a5f"               # optional compact-template accent
  vault: ../candidate-evidence/index.md  # optional compatibility field; relative evidence-index path
  thesis: Evaluation-first ML engineer with measurable systems depth.

basics:                            # required
  name: Jordan Wu                  # required
  email: jordan.wu@example.com     # required
  phone: "+1 555 010 0199"        # optional
  location: Seattle, WA            # optional
  links:                           # optional
    - label: GitHub                # optional authoring label
      url: https://github.com/jordanwu

summary: One short positioning sentence when it adds information.  # optional

education:                         # optional
  - institution: University of Washington
    degree: B.S.
    field: Computer Science
    location: Seattle, WA          # optional
    start: 2023-09                 # optional
    end: 2027-12                   # optional
    gpa: "3.8/4.0"                 # optional; always quote
    coursework: [Machine Learning, Distributed Systems]  # optional
    honors: [Dean's List]          # optional

experience:                        # optional
  - organization: Meridian Labs
    title: Machine Learning Engineering Intern
    location: Seattle, WA          # optional
    start: 2025-06                 # optional
    end: 2025-09                   # optional
    group: industry                # optional; research | teaching | industry
    tags: [RAG evaluation, retrieval latency]  # optional; rendered by every template
    bullets:                       # required, non-empty
      - Built a nightly evaluation harness over 1,200 support tickets.

projects:                          # optional
  - name: ledgerlite               # required
    summary: append-only finance CLI  # optional
    url: https://github.com/jordanwu/ledgerlite  # optional
    start: 2024-01                 # optional
    end: present                   # optional
    stack: [Rust, SQLite]          # optional; rendered by every template
    bullets:                       # required, non-empty
      - Added double-entry validation and signed releases.

skills:                            # optional
  - label: Languages               # required
    items: [Python, Rust, SQL]      # required, non-empty

publications:                      # optional
  - citation: "Wu, J. (2026). Title. Venue."  # required
    url: https://example.com/paper.pdf         # optional

awards:                            # optional
  - name: Regional ICPC — 2nd place  # required
    date: 2025-11                    # optional; YYYY-MM or quoted YYYY
```

## Target levels

- Industry: `intern`, `new-grad`, `junior`, `mid`, `senior`, `staff`, `principal`, `lead`, `manager`.
- Academic: `grad-applicant`, `phd-applicant`, `postdoc`.

## Rendering behavior

- Every template renders all content keys, including `experience[].tags` and `projects[].stack`.
- When no experience entry has `group`, all entries render under `Experience`; when any entry has `group`, every entry must have one and the templates render Research, Teaching, and Industry Experience sections.
- Links render their URL as visible linked text; `label` helps the author identify the link but does not replace the URL.
- Project dates and URLs may both be present and both render.
- `classic` stays monochrome; `accent` changes the `compact` theme only.

## Practical notes

- Put a thesis title or supervisor in `education[].field` when it belongs on the degree line; put a research lab or advisor in `experience[].organization` when it describes the work setting.
- Use `gpa` only for an actual GPA; put classifications or distinctions in `honors`.
- Use `experience` for formal roles and `projects` for independent, open-source, or informal work.
