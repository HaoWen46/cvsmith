# Field guide: unknown fields — a research procedure

No static rules can cover nursing, patent law, supply chain, UX
research, and mechanical engineering at once. What generalizes is the
*procedure* for discovering a field's conventions. Run it; don't guess
from tech norms — resume conventions differ sharply by field (some
expect 2+ pages, licenses up top, or a strict chronological format).

## The procedure

1. **Name the field and level precisely.** "Marketing" is not a field;
   "B2B SaaS product marketing, mid-level" is. Confirm with the user.

2. **Find 3+ exemplar resumes.** Search for real, recent, successful
   examples: "{field} resume example {current year}", university career
   center guides for the field, professional association templates.
   Prefer sources dated within ~2 years — conventions drift.

3. **Extract the norms** from the exemplars, explicitly:
   - Section set and order (certifications/licenses first? portfolio?)
   - Page-count expectation (one page is a *tech* norm; academia,
     medicine, and federal jobs differ)
   - What gets quantified in this field (revenue? caseload? patient
     volume? circulation? cost savings?)
   - Credential display (licenses with numbers? bar admissions? GPA
     conventions?)
   - Vocabulary register (clinical precision vs. business outcomes)

4. **Verify with the user.** One message: "For {field}, the norms I
   found are X, Y, Z — match what you've seen?" Users often know their
   field's quirks and will correct fast.

5. **Then apply the core rules**, which are field-invariant:
   - Evidence over prose; the bullet formula still holds — only *what
     counts as* an outcome changes per field
   - Standard-heading parseability still matters everywhere an ATS
     exists (which is nearly everywhere now)
   - The anti-slop list is universal
   - Never fabricate, anywhere, ever

## Adjustments the schema/template supports

- Extra sections (certifications, licenses, languages): raise it —
  the maintainer adds schema sections on first real demand rather than
  speculatively. Until then, `awards` or `publications` can host
  structured credential lines if the semantics genuinely fit.
- Multi-page: set `meta.page_budget` accordingly; the render check
  warns, not blocks.

## When the field resists this toolkit

Grad-school / research-program CVs are covered — use
`fields/academic.md`, not this procedure. What genuinely resists:
senior-academic CVs (exhaustive publication/grant/committee lists),
federal-format resumes (USAJOBS's own multi-page conventions — the
research procedure above *does* work for these, but expect norms
opposite to tech's), and design portfolios (a different artifact).
Say what transfers (evidence extraction, honesty, clean typesetting),
name what doesn't, and don't force the one-page template onto them.
