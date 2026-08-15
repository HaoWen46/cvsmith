#import "base.typ": render-resume

#let render(data) = render-resume(
  data,
  font: "Source Serif 4",
  body-size: 10pt,
  meta-size: 9pt,
  name-size: 18pt,
  margin-x: 0.72in,
  margin-y: 0.58in,
  accent: rgb("#222222"),
  centered-header: true,
  serif: true,
)
