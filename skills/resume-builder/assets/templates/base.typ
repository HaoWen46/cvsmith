// Shared linear resume renderer. Metadata stays inline so extraction order follows visual order.

#let months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

#let fmt-date(value) = {
  if value == none { return none }
  let value = str(value)
  if lower(value) == "present" { return "Present" }
  let parts = value.split("-")
  if parts.len() == 2 { months.at(int(parts.at(1)) - 1) + " " + parts.at(0) } else { value }
}

#let date-range(start, end) = {
  let start = fmt-date(start)
  let end = fmt-date(end)
  if start == none { end } else if end == none { start } else { start + " – " + end }
}

#let short-url(value) = value.replace("https://", "").replace("http://", "").replace("www.", "").trim("/")

#let render-resume(
  data,
  font: "Inter",
  body-size: 10pt,
  meta-size: 9pt,
  name-size: 21pt,
  margin-x: 0.7in,
  margin-y: 0.55in,
  accent: rgb("#1f3a5f"),
  centered-header: false,
  serif: false,
) = {
  let basics = data.basics
  let meta = data.at("meta", default: (:))
  let ink = rgb("#171717")
  let muted = rgb("#565d66")
  let rule = rgb("#c9ced4")
  let separator = [#h(4pt)#text(fill: muted)[·]#h(4pt)]
  let title-meta-gap = 6pt
  let meta-body-gap = 4pt
  let meta-line(parts) = {
    let parts = parts.filter(item => item != none)
    if parts.len() > 0 { text(size: meta-size, fill: muted, parts.join(separator)) }
  }
  let entry(body, first: false) = block(above: if first { 0pt } else { 10.5pt }, below: 0pt, breakable: false, width: 100%, body)
  let title-line(primary, secondary: none) = [
    #text(weight: 600)[#primary]
    #if secondary != none [ — #emph(secondary)]
  ]

  set document(title: basics.name + " — Resume", author: basics.name)
  set page(paper: meta.at("paper", default: "us-letter"), margin: (x: margin-x, top: margin-y, bottom: 0.78in))
  set text(font: font, size: body-size, fill: ink, lang: meta.at("lang", default: "en"), hyphenate: false)
  set par(justify: false, leading: 0.58em, spacing: 0.55em)
  set list(indent: 0.25em, body-indent: 0.48em, spacing: 0.58em, marker: text(size: 0.78em, fill: accent)[•])
  show link: set text(fill: if serif { ink } else { accent })
  show heading.where(level: 1): it => block(above: 0pt, below: 5pt, width: 100%)[
    #if centered-header { align(center, text(size: name-size, weight: "semibold", fill: accent, it.body)) } else { text(size: name-size, weight: "bold", fill: accent, it.body) }
  ]
  show heading.where(level: 2): it => block(above: 14pt, below: 8pt, width: 100%)[
    #text(size: meta-size, weight: 700, fill: accent, tracking: 0.06em, upper(it.body))
    #v(2pt, weak: true)
    #line(length: 100%, stroke: 0.55pt + rule)
  ]

  heading(level: 1, basics.name.replace(" ", "\u{00a0}"))
  {
    let contacts = ()
    if "location" in basics { contacts.push(basics.location) }
    contacts.push(link("mailto:" + basics.email)[#basics.email])
    if "phone" in basics { contacts.push(basics.phone) }
    for item in basics.at("links", default: ()) { contacts.push(link(item.url)[#short-url(item.url)]) }
    if centered-header { align(center, meta-line(contacts)) } else { meta-line(contacts) }
  }

  if "summary" in data { v(7pt, weak: true); data.summary }

  if "education" in data {
    heading(level: 2)[Education]
    for (index, item) in data.education.enumerate() {
      entry(first: index == 0)[
        #title-line(item.institution, secondary: item.at("location", default: none))
        #v(title-meta-gap, weak: true)
        #meta-line((item.degree + " in " + item.field, date-range(item.at("start", default: none), item.at("end", default: none)), if "gpa" in item { "GPA " + item.gpa } else { none }))
        #if "coursework" in item [#v(meta-body-gap, weak: true)#text(size: meta-size)[#text(weight: 600)[Coursework:] #item.coursework.join(", ")]]
        #if "honors" in item [#v(meta-body-gap, weak: true)#text(size: meta-size)[#text(weight: 600)[Honors:] #item.honors.join(", ")]]
      ]
    }
  }

  let experience-entry(item, first) = entry(first: first)[
    #title-line(item.organization, secondary: item.title)
    #v(title-meta-gap, weak: true)
    #meta-line((date-range(item.at("start", default: none), item.at("end", default: none)), item.at("location", default: none), if "tags" in item { item.tags.join(" · ") } else { none }))
    #v(meta-body-gap, weak: true)
    #list(..item.bullets)
  ]
  if "experience" in data {
    let grouped = data.experience.any(item => "group" in item)
    let titles = (research: [Research Experience], teaching: [Teaching Experience], industry: [Industry Experience])
    let buckets = if grouped {
      ("research", "teaching", "industry").map(group => (group, data.experience.filter(item => item.group == group))).filter(pair => pair.at(1).len() > 0)
    } else { (("all", data.experience),) }
    for (group, entries) in buckets {
      heading(level: 2, if grouped { titles.at(group) } else { [Experience] })
      for (index, item) in entries.enumerate() { experience-entry(item, index == 0) }
    }
  }

  if "projects" in data {
    heading(level: 2)[Projects]
    for (index, item) in data.projects.enumerate() {
      entry(first: index == 0)[
        #title-line(item.name, secondary: item.at("summary", default: none))
        #v(title-meta-gap, weak: true)
        #meta-line((date-range(item.at("start", default: none), item.at("end", default: none)), if "stack" in item { item.stack.join(" · ") } else { none }, if "url" in item { link(item.url)[#short-url(item.url)] } else { none }))
        #v(meta-body-gap, weak: true)
        #list(..item.bullets)
      ]
    }
  }

  if "skills" in data {
    heading(level: 2)[Skills]
    for (index, item) in data.skills.enumerate() {
      entry(first: index == 0)[#text(weight: 600)[#item.label:] #item.items.join(", ")]
    }
  }

  if "publications" in data {
    heading(level: 2)[Publications]
    for (index, item) in data.publications.enumerate() {
      entry(first: index == 0)[#item.citation#if "url" in item [#h(4pt)#link(item.url)[#short-url(item.url)]]]
    }
  }

  if "awards" in data {
    heading(level: 2)[Awards]
    for (index, item) in data.awards.enumerate() {
      entry(first: index == 0)[#item.name#if "date" in item [#separator#fmt-date(item.date)]]
    }
  }
}
