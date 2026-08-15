#import "base.typ": render-resume

#let render(data) = render-resume(
  data,
  font: "Inter",
  body-size: 10pt,
  meta-size: 9pt,
  name-size: 20pt,
  margin-x: 0.58in,
  margin-y: 0.58in,
  accent: rgb("#1a4f8b"),
)
