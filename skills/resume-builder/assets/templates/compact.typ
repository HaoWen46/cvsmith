// compact.typ — cvsmith's designed template: dense, modern grotesque,
// one accent color doing real work. Visual language: statement name,
// tracked accent section headers over hairlines, secondary meta pushed
// into gray, tag rows giving interviewers scent. Parse-safety identical
// to onecol: real H1/H2 tags, standard headings, single column, text
// URLs (never icon-only links), vendored fonts.
//
// Same data contract as onecol (data-schema.md). Extra knob:
// meta.accent — hex color, default deep navy.
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

  let ink = rgb("#1a1a1a")
  let muted = rgb("#5d646e")
  let hair = rgb("#cdd2d8")
  let accent = rgb(m.at("accent", default: "#1f3a5f"))

  set document(title: b.name + " — Resume", author: b.name)
  set page(paper: m.at("paper", default: "us-letter"),
           margin: (x: 0.52in, top: 0.5in, bottom: 0.5in))
  set text(font: "Inter", size: 9.2pt, fill: ink,
           lang: m.at("lang", default: "en"), hyphenate: false)
  set par(justify: false, leading: 0.5em, spacing: 0.5em)
  set list(indent: 0.15em, body-indent: 0.45em, spacing: 0.42em,
           marker: text(fill: accent, size: 0.75em, "\u{25CF}"))
  show link: set text(fill: ink.lighten(8%))

  let meta-text(body) = text(size: 8.6pt, fill: muted, body)
  let row(left-side, right-side) = grid(
    columns: (1fr, auto),
    column-gutter: 10pt,
    align: (left + top, right + top),
    left-side,
    if right-side != none { meta-text(right-side) },
  )
  let entry(spacing: 6pt, body) = block(above: spacing, below: 0pt,
                                        breakable: false, width: 100%, body)

  show heading.where(level: 1): it => block(above: 0pt, below: 4.5pt, width: 100%,
    text(size: 24.5pt, weight: 700, fill: accent, tracking: -0.3pt, it.body))
  show heading.where(level: 2): it => block(above: 11pt, below: 6pt, width: 100%)[
    #text(size: 8.8pt, weight: 700, fill: accent, tracking: 0pt, upper(it.body))
    #v(3pt, weak: true)
    #line(length: 100%, stroke: 0.55pt + hair)
  ]

  // ── header ──────────────────────────────────────────────────────
  heading(level: 1, b.name)
  {
    let sep = [#h(6pt)#text(fill: muted, "\u{00b7}")#h(6pt)]
    let items = ()
    if "location" in b { items.push([#b.location]) }
    items.push(link("mailto:" + b.email)[#b.email])
    if "phone" in b { items.push([#b.phone]) }
    for l in b.at("links", default: ()) { items.push(link(l.url)[#short-url(l.url)]) }
    text(size: 8.8pt, fill: muted, items.join(sep))
  }

  if "summary" in data {
    v(7pt, weak: true)
    text(size: 9.2pt, data.summary)
  }

  // ── education ───────────────────────────────────────────────────
  if "education" in data {
    heading(level: 2)[Education]
    for (i, e) in data.education.enumerate() {
      entry(spacing: if i == 0 { 0pt } else { 6pt })[
        #row(text(size: 9.6pt, weight: 600, e.institution),
             e.at("location", default: none))
        #v(2pt, weak: true)
        #row({
          emph(text(size: 8.9pt)[#e.degree in #e.field])
          if "gpa" in e [#h(4pt)#text(fill: hair, "\u{00b7}")#h(4pt)#text(size: 8.9pt)[GPA #e.gpa]]
        }, emph(daterange(e.at("start", default: none), e.at("end", default: none))))
        #if "coursework" in e [
          #v(2pt, weak: true)
          #text(size: 8.7pt)[#text(weight: 600)[Coursework:] #e.coursework.join(", ")]
        ]
        #if "honors" in e [
          #v(2pt, weak: true)
          #text(size: 8.7pt)[#text(weight: 600)[Honors:] #e.honors.join(", ")]
        ]
      ]
    }
  }

  // ── experience (grouped or flat, same contract as onecol) ───────
  let exp-entry(e, first) = entry(spacing: if first { 0pt } else { 6.5pt })[
    #row({
      text(size: 9.6pt, weight: 600, e.organization)
      [#text(size: 9.4pt)[: #e.title]]
    }, e.at("location", default: none))
    #v(2pt, weak: true)
    #row(
      if "tags" in e { meta-text(emph(e.tags.join(" \u{00b7} "))) } else { none },
      emph(daterange(e.at("start", default: none), e.at("end", default: none))))
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
      entry(spacing: if i == 0 { 0pt } else { 6.5pt })[
        #row({
          text(size: 9.6pt, weight: 600, p.name)
          if "summary" in p [#text(size: 9.2pt)[: #p.summary]]
        }, if "url" in p { link(p.url)[#short-url(p.url)] } else { none })
        #v(2pt, weak: true)
        #row(
          if "stack" in p { meta-text(emph(p.stack.join(" \u{00b7} "))) } else { none },
          if dates != none { emph(dates) } else { none })
        #v(2.5pt, weak: true)
        #list(..p.bullets)
      ]
    }
  }

  // ── skills ──────────────────────────────────────────────────────
  if "skills" in data {
    heading(level: 2)[Skills]
    grid(
      columns: (auto, 1fr),
      column-gutter: 1.4em,
      row-gutter: 0.55em,
      ..data.skills.map(g => (
        text(size: 8.9pt, weight: 600, g.label),
        text(size: 9pt, g.items.join(", ")),
      )).flatten()
    )
  }

  // ── publications ────────────────────────────────────────────────
  if "publications" in data {
    heading(level: 2)[Publications]
    for (i, p) in data.publications.enumerate() {
      entry(spacing: if i == 0 { 0pt } else { 4pt })[
        #text(size: 9pt, p.citation)
        #if "url" in p [ #link(p.url)[#short-url(p.url)]]
      ]
    }
  }

  // ── awards ──────────────────────────────────────────────────────
  if "awards" in data {
    heading(level: 2)[Awards]
    for (i, a) in data.awards.enumerate() {
      entry(spacing: if i == 0 { 0pt } else { 3pt })[
        #row(text(size: 9.2pt, a.name), fmt-date(a.at("date", default: none)))
      ]
    }
  }
}
