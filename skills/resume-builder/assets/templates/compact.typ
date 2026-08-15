#import "base.typ": render-resume

#let render(data) = {
  let meta = data.at("meta", default: (:))
  render-resume(
    data,
    font: "Inter",
    body-size: 10pt,
    meta-size: 9pt,
    name-size: 24pt,
    margin-x: 0.58in,
    margin-y: 0.58in,
    accent: rgb(meta.at("accent", default: "#1f3a5f")),
  )
}
