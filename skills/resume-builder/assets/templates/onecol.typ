// onecol.typ — cvsmith's default resume template.
//
// Single column, standard headings, real heading tags in the structure
// tree, everything a 2026 parsing pipeline expects. A pure function of
// the resume.yaml data described in data-schema.md: templates never
// invent, reorder, or rewrite content.
//
// Compile with: --pdf-standard ua-1,a-2a  (PDF/UA-1 requires the
// document title this template sets from basics.name).

#let ink = rgb("#1c1c1c")
#let muted = rgb("#525a63")
#let faint = rgb("#c9ced4")
#let accent = rgb("#1a4f8b")

#let months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

// "2025-06" -> "Jun 2025", "present" -> "Present", "2025" -> "2025"
#let fmt-date(d) = {
  if d == none { return none }
  let s = str(d)
  if lower(s) == "present" { return "Present" }
  let parts = s.split("-")
  if parts.len() >= 2 { months.at(int(parts.at(1)) - 1) + " " + parts.at(0) }
  else { s }
}

#let daterange(start, end) = {
  let s = fmt-date(start)
  let e = fmt-date(end)
  if s == none and e == none { none }
  else if e == none { s }
  else if s == none { e }
  else { s + " \u{2013} " + e }
}

// visible text for a URL: scheme stripped, no trailing slash
#let short-url(u) = u.replace("https://", "").replace("http://", "").trim("/")

// one entry line: main content left, meta (dates/location) right
#let row(left-side, right-side) = grid(
  columns: (1fr, auto),
  column-gutter: 1.2em,
  align: (left + top, right + top),
  left-side,
  if right-side != none { text(size: 9.2pt, fill: muted, right-side) },
)

#let entry(spacing: 6.2pt, body) = block(above: spacing, below: 0pt, breakable: false, width: 100%, body)

#let render(data) = {
  let b = data.basics
  let m = data.at("meta", default: (:))

  set document(title: b.name + " — Resume", author: b.name)
  set page(paper: m.at("paper", default: "us-letter"),
           margin: (x: 1.45cm, top: 1.25cm, bottom: 1.25cm))
  set text(font: "Source Sans 3", size: 10pt, fill: ink,
           lang: m.at("lang", default: "en"), hyphenate: false)
  set par(justify: false, leading: 0.56em, spacing: 0.56em)
  set list(indent: 0.55em, body-indent: 0.5em, spacing: 0.5em,
           marker: text(size: 0.8em, fill: muted, "\u{2022}"))
  show link: set text(fill: accent)

  // name = H1; section titles = H2 — real tags in the structure tree
  show heading.where(level: 1): it => block(above: 0pt, below: 6pt, width: 100%,
    align(center, text(size: 20.5pt, weight: 600, tracking: 0.01em, it.body)))
  show heading.where(level: 2): it => block(above: 13pt, below: 6.5pt, width: 100%)[
    #text(size: 9pt, weight: 600, tracking: 0.09em, upper(it.body))
    #v(3pt, weak: true)
    #line(length: 100%, stroke: 0.5pt + faint)
  ]

  // ── header ──────────────────────────────────────────────────────
  heading(level: 1, b.name)
  {
    let sep = [#h(4.5pt)#text(fill: muted, "\u{00b7}")#h(4.5pt)]
    let items = ()
    if "location" in b { items.push([#b.location]) }
    items.push(link("mailto:" + b.email)[#b.email])
    if "phone" in b { items.push([#b.phone]) }
    for l in b.at("links", default: ()) { items.push(link(l.url)[#short-url(l.url)]) }
    align(center, text(size: 9.2pt, fill: ink.lighten(12%), items.join(sep)))
  }

  if "summary" in data {
    v(7pt, weak: true)
    data.summary
  }

  // ── education ───────────────────────────────────────────────────
  if "education" in data {
    heading(level: 2)[Education]
    for (i, e) in data.education.enumerate() {
      entry(spacing: if i == 0 { 0pt } else { 7.5pt })[
        #row(text(size: 10.2pt, weight: 600, e.institution),
             daterange(e.at("start", default: none), e.at("end", default: none)))
        #v(2.4pt, weak: true)
        #row({
          emph(e.degree + " in " + e.field)
          if "gpa" in e [ #h(2pt)#text(fill: muted, "\u{00b7}")#h(2pt) GPA #e.gpa]
        }, e.at("location", default: none))
        #if "coursework" in e [
          #v(2.2pt, weak: true)
          #text(size: 9.2pt)[#text(weight: 600)[Coursework:] #e.coursework.join(", ")]
        ]
        #if "honors" in e [
          #v(2.2pt, weak: true)
          #text(size: 9.2pt)[#text(weight: 600)[Honors:] #e.honors.join(", ")]
        ]
      ]
    }
  }

  // ── experience ──────────────────────────────────────────────────
  // Entries may carry group: research | teaching | industry. When any
  // entry is grouped, each group renders as its own standard-headed
  // section (academic-CV convention); otherwise one "Experience".
  let exp-entry(e, first) = entry(spacing: if first { 0pt } else { 8pt })[
    #row(text(size: 10.2pt, weight: 600, e.organization),
         daterange(e.at("start", default: none), e.at("end", default: none)))
    #v(2.4pt, weak: true)
    #row(emph(e.title), e.at("location", default: none))
    #v(3pt, weak: true)
    #list(..e.bullets)
  ]
  if "experience" in data {
    let titles = (research: [Research Experience], teaching: [Teaching Experience],
                  industry: [Industry Experience])
    let grouped = data.experience.any(e => "group" in e)
    let buckets = if grouped {
      ("research", "teaching", "industry")
        .map(g => (g, data.experience.filter(e => e.at("group", default: "industry") == g)))
        .filter(b => b.at(1).len() > 0)
    } else {
      (("all", data.experience),)
    }
    for (gname, entries) in buckets {
      heading(level: 2, if grouped { titles.at(gname) } else { [Experience] })
      for (i, e) in entries.enumerate() { exp-entry(e, i == 0) }
    }
  }

  // ── projects ────────────────────────────────────────────────────
  if "projects" in data {
    heading(level: 2)[Projects]
    for (i, p) in data.projects.enumerate() {
      let dates = daterange(p.at("start", default: none), p.at("end", default: none))
      entry(spacing: if i == 0 { 0pt } else { 8pt })[
        #row({
          text(size: 10.2pt, weight: 600, p.name)
          if "stack" in p [ #h(2pt)#text(fill: muted, "\u{00b7}")#h(2pt) #text(size: 9.2pt, fill: muted, p.stack.join(", "))]
        }, if "url" in p { link(p.url)[#short-url(p.url)] } else { dates })
        #v(3pt, weak: true)
        #list(..p.bullets)
      ]
    }
  }

  // ── skills ──────────────────────────────────────────────────────
  if "skills" in data {
    heading(level: 2)[Skills]
    grid(
      columns: (auto, 1fr),
      column-gutter: 1.1em,
      row-gutter: 0.5em,
      ..data.skills.map(g => (
        text(size: 9.6pt, weight: 600, g.label),
        text(g.items.join(", ")),
      )).flatten()
    )
  }

  // ── publications ────────────────────────────────────────────────
  if "publications" in data {
    heading(level: 2)[Publications]
    for (i, p) in data.publications.enumerate() {
      entry(spacing: if i == 0 { 0pt } else { 4.5pt })[
        #p.citation
        #if "url" in p [ #h(2pt)#link(p.url)[#short-url(p.url)]]
      ]
    }
  }

  // ── awards ──────────────────────────────────────────────────────
  if "awards" in data {
    heading(level: 2)[Awards]
    for (i, a) in data.awards.enumerate() {
      entry(spacing: if i == 0 { 0pt } else { 3.5pt })[
        #row(a.name, fmt-date(a.at("date", default: none)))
      ]
    }
  }
}
