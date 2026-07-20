// classic.typ — cvsmith's conservative template: serif, centered,
// monochrome, strictly conventional. For registers where deviation is
// itself a negative signal — banking, consulting, law, government,
// traditional industries. No accent color, no tag rows, no design
// gestures: the discipline IS the design.
//
// Same data contract as onecol/compact (data-schema.md); ignores
// meta.accent by intent. Parse-safety identical: real H1/H2 tags,
// standard headings, single column, text URLs, vendored fonts.
//
// Compile with: --pdf-standard ua-1,a-2a

#let months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

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

#let short-url(u) = u.replace("https://", "").replace("http://", "").trim("/")

#let render(data) = {
  let b = data.basics
  let m = data.at("meta", default: (:))

  let ink = rgb("#111111")
  let muted = rgb("#444444")
  let hair = rgb("#999999")

  set document(title: b.name + " — Resume", author: b.name)
  set page(paper: m.at("paper", default: "us-letter"),
           margin: (x: 0.7in, top: 0.6in, bottom: 0.6in))
  set text(font: "Source Serif 4", size: 10pt, fill: ink,
           lang: m.at("lang", default: "en"), hyphenate: false)
  set par(justify: false, leading: 0.5em, spacing: 0.5em)
  set list(indent: 0.3em, body-indent: 0.5em, spacing: 0.45em,
           marker: text(size: 0.85em, "\u{2022}"))
  show link: it => it   // links stay ink-colored; conservative pages have no blue

  let meta-text(body) = text(size: 9pt, fill: muted, body)
  let row(left-side, right-side) = grid(
    columns: (1fr, auto),
    column-gutter: 12pt,
    align: (left + top, right + top),
    left-side,
    if right-side != none { meta-text(right-side) },
  )
  let entry(spacing: 6.5pt, body) = block(above: spacing, below: 0pt,
                                          breakable: false, width: 100%, body)

  show heading.where(level: 1): it => block(above: 0pt, below: 5pt, width: 100%,
    align(center, text(size: 17.5pt, weight: 600, it.body)))
  show heading.where(level: 2): it => block(above: 11.5pt, below: 6.5pt, width: 100%)[
    #text(size: 10pt, weight: 600, upper(it.body))
    #v(2.5pt, weak: true)
    #line(length: 100%, stroke: 0.6pt + hair)
  ]

  // ── header ──────────────────────────────────────────────────────
  heading(level: 1, b.name)
  {
    let sep = [#h(5pt)\u{00b7}#h(5pt)]
    let items = ()
    if "location" in b { items.push([#b.location]) }
    items.push(link("mailto:" + b.email)[#b.email])
    if "phone" in b { items.push([#b.phone]) }
    for l in b.at("links", default: ()) { items.push(link(l.url)[#short-url(l.url)]) }
    align(center, text(size: 9.2pt, fill: muted, items.join(sep)))
  }

  if "summary" in data {
    v(7pt, weak: true)
    data.summary
  }

  // ── education ───────────────────────────────────────────────────
  if "education" in data {
    heading(level: 2)[Education]
    for (i, e) in data.education.enumerate() {
      entry(spacing: if i == 0 { 0pt } else { 6.5pt })[
        #row(text(weight: 600, e.institution),
             daterange(e.at("start", default: none), e.at("end", default: none)))
        #v(2pt, weak: true)
        #row({
          emph[#e.degree in #e.field]
          if "gpa" in e [, GPA #e.gpa]
        }, e.at("location", default: none))
        #if "coursework" in e [
          #v(2pt, weak: true)
          #text(size: 9.3pt)[Coursework: #e.coursework.join(", ")]
        ]
        #if "honors" in e [
          #v(2pt, weak: true)
          #text(size: 9.3pt)[Honors: #e.honors.join(", ")]
        ]
      ]
    }
  }

  // ── experience (grouped or flat, same contract) ─────────────────
  let exp-entry(e, first) = entry(spacing: if first { 0pt } else { 7pt })[
    #row(text(weight: 600, e.organization),
         daterange(e.at("start", default: none), e.at("end", default: none)))
    #v(2pt, weak: true)
    #row(emph(e.title), e.at("location", default: none))
    #v(2.5pt, weak: true)
    #list(..e.bullets)
  ]
  if "experience" in data {
    let titles = (research: [Research Experience], teaching: [Teaching Experience],
                  industry: [Industry Experience])
    let grouped = data.experience.any(e => "group" in e)
    let buckets = if grouped {
      ("research", "teaching", "industry")
        .map(g => (g, data.experience.filter(e => e.at("group", default: "industry") == g)))
        .filter(bk => bk.at(1).len() > 0)
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
      entry(spacing: if i == 0 { 0pt } else { 7pt })[
        #row({
          text(weight: 600, p.name)
          if "summary" in p [ — #p.summary]
        }, if "url" in p { link(p.url)[#short-url(p.url)] } else { dates })
        #v(2.5pt, weak: true)
        #list(..p.bullets)
      ]
    }
  }

  // ── skills ──────────────────────────────────────────────────────
  if "skills" in data {
    heading(level: 2)[Skills]
    for (i, g) in data.skills.enumerate() {
      entry(spacing: if i == 0 { 0pt } else { 3.5pt })[
        #text(weight: 600)[#g.label:] #g.items.join(", ")
      ]
    }
  }

  // ── publications ────────────────────────────────────────────────
  if "publications" in data {
    heading(level: 2)[Publications]
    for (i, p) in data.publications.enumerate() {
      entry(spacing: if i == 0 { 0pt } else { 4.5pt })[
        #p.citation
        #if "url" in p [ #link(p.url)[#short-url(p.url)]]
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
