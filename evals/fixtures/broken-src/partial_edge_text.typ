// Planted failure: words cross each page edge; offpage_text must fail.
#set page(paper: "us-letter", margin: 0pt)
#set text(size: 10pt)

// Crosses the right edge.
#place(top + left, dx: 575pt, dy: 90pt)[RIGHTCROSSWORD]

// crosses the left edge: starts past x=0, ends inside.
#place(top + left, dx: -40pt, dy: 150pt)[LEFTCROSSWORD]

// crosses the top edge: starts above y=0, ends inside.
#place(top + left, dx: 250pt, dy: -5pt)[TOPCROSSWORD]

// crosses the bottom edge: starts inside (792pt page height), ends past it.
#place(top + left, dx: 250pt, dy: 785pt)[BOTTOMCROSSWORD]

// Wholly off-page control.
#place(top + left, dx: 650pt, dy: 210pt)[WHOLLYOFFPAGECONTROL]

// Legitimate on-page text.
#place(top + left, dx: 40pt, dy: 400pt)[
  Visible supporting text for evaluator geometry verification.
]
