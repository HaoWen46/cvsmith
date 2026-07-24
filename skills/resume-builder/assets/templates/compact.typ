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

#let short-url(u) = u.replace("https://", "").replace("http://", "").replace("www.", "").trim("/")

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
  // one entry line: main content, then meta (dates/location) trailing
  // right behind it with a small fixed gap — never flush to the page's
  // right margin. A meta column that's *always* right-aligned to the
  // same x, with nothing else ever occupying the gap between it and
  // the body text, reads as an independent column to poppler's default
  // (non -layout) text extraction once a section is sparse enough that
  // no other line ever crosses that gap — the whole "column" then gets
  // flushed to the end of the page, after later sections' headings,
  // even though the visible PDF is correctly ordered. Tying the meta
  // text's x position to the body text (small fixed gap, not a
  // 1fr-vs-auto grid) keeps it from ever lining up into a repeatable
  // column, at any content density. See evals/test_sparse_density.py.
  //
  // Round-6 (external review finding 7): a real right-aligned rail was
  // re-tried two ways — a single-line `h(1fr)` fill and a grid cell
  // with an inline `align(right)` sub-box — and both reproduce the
  // exact sparse-density misordering above, on every template, because
  // poppler's column heuristic keys on final glyph geometry (a
  // consistent right edge with an uncrossed gap), not on which Typst
  // construct produced it. Extraction order is the hard invariant, so
  // the rail stays inline.
  //
  // Round-8 (finding 9 + direct user feedback: "the date ... isn't
  // properly placed on the right hand side ... aesthetically bad"): a
  // third rail construct was tried and measured — a same-baseline
  // title+fill+date line boxed unbreakable (box(width:100%) with
  // h(1fr)) and place(right + horizon) anchored per entry — and BOTH
  // still reproduce the exact reordering above in a minimal repro,
  // independent of density (see scratch evidence,
  // /private/tmp/.../dates8/repro/cand_a_*, cand_b_*): poppler's
  // default (non -layout) text extraction clusters any text that has a
  // consistently uncrossed horizontal gap in front of it into its own
  // "column" and flushes that column to the end of the page, and this
  // triggers on final glyph geometry regardless of which Typst
  // primitive produced that geometry. True right-alignment is
  // therefore impossible under this repo's extraction-correctness
  // invariant (round-5/6 doctrine confirmed, not just re-asserted) —
  // reported plainly rather than attempted again.
  //
  // What round-6's fix got wrong per finding 9: unconditionally
  // prefixing right-side with a "\u{00b7}" marker meant that whenever
  // nothing preceded it on its own visual line — this template's tag
  // row has no left-side when an entry carries no `tags`/`stack` — the
  // line rendered as a lone "\u{00b7} date", a punctuation mark with
  // nothing attached to it, floating at the left margin. That reads as
  // broken, not as metadata. The round-8 fix: drop the marker
  // character entirely and keep only the small fixed gap. Extraction
  // order is unaffected (the gap was always what kept this construct
  // out of poppler's column heuristic, not the dot — confirmed in the
  // scratch repro, cand_c_sparse: same fixed-gap construct minus the
  // dot still extracts in-order). The gap alone, plus this text's
  // distinct muted/italic styling, is enough to read as "this is the
  // entry's meta," and a bare date with a small consistent lead-in gap
  // reads as an intentional, stable position on every entry — never a
  // detached, contextless marker — which is the best available
  // fallback once true right-alignment is off the table.
  //
  // Round-9 (finding 9, reopened — user: "the date somehow isn't
  // properly placed on the right hand side ... aesthetically bad"):
  // round-8 only fixed the detached-marker half; dates still landed at
  // a 40-500pt scatter with nothing near the right margin (measured
  // fresh against this file and examples/ai-ml-intern/resume.pdf). The
  // "impossible" conclusion above was about *rail* constructs — a
  // separate right-aligned column with an uncrossed whitespace gap in
  // front of it. An inline dot LEADER — repeated "." glyphs filling
  // `box(width: 1fr)` in the same run as the left content and the date
  // (a table-of-contents leader, not a grid column) — is a different
  // geometry: the gap is filled with real glyphs, so there is no
  // uncrossed whitespace column for poppler to key on. Measured this
  // round (scratch: dates9/expt3, dates9/expt4) on every
  // template/density: when the row has real left-side content, the
  // leader+date now lands exactly at the content box's right edge on
  // every entry, and reading order stays correct (SKILLS still follows
  // the dates in default-mode `pdftotext`). When the row has NO
  // left-side content, the identical construct (leader spanning the
  // whole line width alone) DOES reproduce the reading-order
  // regression — reconfirmed fresh this round (scratch: dates9/expt2)
  // — so that case (and the rare atomic-wrap-alone-under-an-extreme-
  // length-name case) deliberately keeps the round-8 fixed-gap,
  // left-flush fallback below instead of the leader. See
  // evals/test_sparse_density.py's round-9 section for the
  // right-alignment test and the hidden-text-contrast test (the
  // leader must use `muted`, not `hair` — `hair` is faint enough that
  // hidden_text_check's luminance heuristic flags it as
  // background-matched/invisible text).
  // Round-9 follow-up (external review finding 9, still-open half): the
  // doctrine above claimed the extreme-length-name case's "leader+
  // date, boxed atomically... wraps whole to its own new line", but no
  // code ever enforced that — `box(width: 1fr, ...)` is not nested
  // inside the atomic date box, so Typst is free to lay the leader's
  // repeated "." glyphs out on the CURRENT line (running to the right
  // margin) and push only the date box down to a new line by itself:
  // the exact "punctuation with nothing attached to it" defect
  // finding 9 originally named, reproduced with a leader instead of a
  // "·". Reproduced against the committed long-meta fixture (classic's
  // Experience row: "Meridian Laboratories...International
  // ......................." with x1=558.1 and nothing after it, then
  // "Jun 2025 – Sep 2025" alone at x0=50.4 on the next line).
  // `box(width: 1fr)` also can't simply nest one level deeper inside
  // an outer atomic box — 1fr needs paragraph-level context to
  // resolve, which an inner box doesn't provide.
  //
  // Fix: predict, before emitting anything, whether the leader
  // construct fits on the current line at all. `layout()` gives the
  // row's actual available width; `measure()` gives the left-side
  // content's and the date box's natural (single-line) widths under
  // the same ambient text styles. If left-side + a minimum viable
  // leader + both small gaps + the date box doesn't fit — which also
  // naturally covers left-side alone already needing multiple lines —
  // row() falls back to round-8's plain fixed-gap construct (no
  // leader) instead of emitting one that might dangle. The fallback's
  // atomic date box still wraps to its own line when needed, but
  // left-flush with no leader preceding it, so there is never a
  // trailing run of periods with nothing after it. Verified against
  // the long-meta fixture: the Education/Experience rows that used to
  // split now render on one line via the fallback. See
  // evals/test_sparse_density.py::test_no_dangling_leader_before_a_wrapped_date.
  // atomic: true wraps the meta text (dates/location) in a box so the
  // whole thing moves to the next line as a unit instead of splitting
  // internally (finding 7, round-7). Only safe for bounded content
  // like date ranges — an unbounded string (e.g. a long location)
  // boxed the same way would run past the page edge instead of
  // wrapping, so row() callers pass atomic: true only for dates.
  let row(left-side, right-side, atomic: false) = block(width: 100%)[
    #if left-side != none and right-side != none [
      #layout(size => {
        let gap = 0.35em
        let min-leader = 12pt
        let meta = meta-text(right-side)
        let meta-box = if atomic { box(meta) } else { meta }
        let left-w = measure(left-side).width
        let date-w = measure(meta-box).width
        let gap-w = measure(h(gap)).width
        if left-w + min-leader + gap-w * 2 + date-w <= size.width {
          left-side
          h(gap)
        // Round-9 (external review finding 7 — extraction pollution): a
        // solid-run dot leader put 1,165 period glyphs into the example's
        // extracted text, in 8 runs, the longest 202 glyphs long. L0 does not
        // see it (punctuation is dropped before token comparison) but every
        // ordinary `pdftotext` and every copy/paste does. Two replacements
        // were rendered and measured this round, not reasoned about:
        //   - a drawn rule (`line(length: 100%)` filling the same 1fr box):
        //     zero glyphs, and it REPRODUCES the exact reading-order
        //     regression documented above — the date is pulled out of order
        //     ("University of Washington / B.S. ... / Sep 2022 - Jun 2026").
        //     A vector stroke does not cross the whitespace column that
        //     poppler's layout analysis keys on; only real glyphs do. The
        //     doctrine above is confirmed, not superseded.
        //   - a SPACED dot (3pt on each side of each "."): keeps every
        //     property — right-aligned dates, correct reading order — and cuts
        //     the example from 1,165 periods to 357, with zero runs of 3+
        //     consecutive periods (the runs are what made copy/paste
        //     unreadable). That is what is used below.
        // The remaining 357 glyphs are the price of right-aligned dates that
        // still extract in order; the two are not separable with a text-glyph
        // leader, and the leader is the only construct measured to preserve
        // both.
          box(width: 1fr, repeat(text(fill: muted, size: 0.7em)[#h(3pt).#h(3pt)]))
          h(gap)
          meta-box
        } else {
          left-side
          h(0.6em)
          meta-box
        }
      })
    ] else if left-side != none [
      #left-side
    ] else if right-side != none {
      let meta = [#h(0.6em)#meta-text(right-side)]
      if atomic { box(meta) } else { meta }
    }
  ]
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
    // box() keeps each contact item unbreakable: the line wraps between
    // items at a separator, never mid-URL or mid-name.
    if "location" in b { items.push(box[#b.location]) }
    items.push(box(link("mailto:" + b.email)[#b.email]))
    if "phone" in b { items.push(box[#b.phone]) }
    for l in b.at("links", default: ()) { items.push(box(link(l.url)[#short-url(l.url)])) }
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
        }, emph(daterange(e.at("start", default: none), e.at("end", default: none))),
           atomic: true)
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
      emph(daterange(e.at("start", default: none), e.at("end", default: none))),
      atomic: true)
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
          if dates != none { emph(dates) } else { none },
          atomic: true)
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
