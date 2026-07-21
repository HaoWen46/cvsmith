# Field guide: academic track — grad school, REUs, fellowships, research programs

For applications where the reader is **faculty or an admissions
committee**, not an HR pipeline: PhD/MS applications, REU and summer
research programs, fellowships, research-assistant openings.

## The reader model changes; the discipline doesn't

- A professor skims a CV in 15–60 seconds for: research experience
  (whose lab, doing what), publications/posters (venue, author
  position), grades in hard courses, and whether the person can be
  handed something open-ended.
- Most academic applications go through portals that store, not parse
  (no embedding-ranking ATS) — but parse-safety costs nothing and some
  university HR layers *do* parse. Keep every mechanical rule: single
  column, standard headings, real text. Only the *content emphasis*
  changes.
- Everything in `writing-rules.md` still applies. Academic bullets
  quantify too: datasets, baselines reproduced, sections taught,
  evaluation scores, cohort ranks.

## Structure: separate research from teaching from industry

Use the schema's experience `group` key (`research` / `teaching` /
`industry`): the template renders one standard-headed section per
group, in that order — the academic convention. Grouping mechanics and
edge cases (what happens to ungrouped entries, when grouping becomes
all-or-nothing) are specified in `assets/templates/data-schema.md`,
the authoritative statement, which you read anyway at the yaml step.

The template's actual academic-mode order: Education → Research
Experience → Teaching Experience → Industry Experience → Projects →
Skills → Publications → Awards. (The template fixes order; what you
control is which sections exist and what carries weight.) Note
publications-after-Skills deviates from academic-CV convention — say
so to the user, and offset by citing key papers inline in Research
Experience bullets.

## What counts as evidence (strongest first)

1. **Research output**: publications/posters with venue and author
   position, verbatim citations; submissions labeled honestly
   ("submitted", "in review" — never imply acceptance).
2. **Research process**: what they did in the lab, concretely —
   experiments designed/run, baselines reproduced (respected, say it),
   infrastructure others adopted, datasets built. Name the advisor/lab
   in the organization field: "Michigan AI Lab, Prof. E. Winters" —
   faculty read for names they know.
3. **Teaching**: course + role, sections/students, semesters,
   evaluation scores if strong, materials that outlived the semester.
4. **Hard coursework + GPA**: graduate courses taken as an undergrad
   are a signal; list the hardest relevant few. GPA matters more here
   than in industry — include unless genuinely weak.
5. **Industry experience**: include but compress — one entry, tightest
   bullets. It signals engineering competence, not research potential.

## Norms that differ from industry resumes

- **Page budget**: 1 page for undergrads applying to REUs/grad school;
  2 acceptable once publications + teaching genuinely overflow (set
  `meta.page_budget: 2` — never pad to reach it).
- **Advisor names and course numbers are welcome** (they'd be noise in
  industry).
- **"References available" lines**: never — recommenders are handled
  by the application portal, the line wastes space everywhere.
- **Objective/summary**: still omit. The statement of purpose does
  that job; the CV is evidence.

## Out of scope — say so, don't improvise

Statements of purpose, research statements, diversity statements,
cover letters, and full senior-academic CVs (exhaustive publication
lists, grants, committees) are different documents. Help with the CV;
name the boundary; don't force the one-page template onto a
20-publication faculty CV.
