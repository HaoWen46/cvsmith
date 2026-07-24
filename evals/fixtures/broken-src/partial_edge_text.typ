// Planted failure: text CROSSING a page edge (partially clipped, not
// wholly off-page). External review finding 4: hidden_text_check.py's
// offpage_text check (~line 188) only caught words wholly beyond an
// edge (x1<0, x0>width, ...) — a word straddling the boundary, half on
// the visible page and half clipped by the viewer/printer, sailed
// through as offpage_text: pass. One straddling word per edge, plus a
// wholly-off-page control (the case the old check already caught) so
// this fixture regression-tests both behaviors at once.
// hidden_text_check.py must flag offpage_text FAIL and name every word
// below, including the crossed edge.
#set page(paper: "us-letter", margin: 0pt)
#set text(size: 10pt)

// crosses the right edge: starts inside (x0=575 < 612pt page width),
// ends past it. Mirrors the external reviewer's proof image geometry.
#place(top + left, dx: 575pt, dy: 90pt)[RIGHTCROSSWORD]

// crosses the left edge: starts past x=0, ends inside.
#place(top + left, dx: -40pt, dy: 150pt)[LEFTCROSSWORD]

// crosses the top edge: starts above y=0, ends inside.
#place(top + left, dx: 250pt, dy: -5pt)[TOPCROSSWORD]

// crosses the bottom edge: starts inside (792pt page height), ends past it.
#place(top + left, dx: 250pt, dy: 785pt)[BOTTOMCROSSWORD]

// wholly off-page control (the pre-existing, already-caught case): entirely
// beyond the right edge, no part of the bbox on the page at all.
#place(top + left, dx: 650pt, dy: 210pt)[WHOLLYOFFPAGECONTROL]

// legitimate, fully on-page text so the fixture also proves the check
// still tells clipped text apart from normal content.
#place(top + left, dx: 40pt, dy: 400pt)[
  Visible supporting text for evaluator geometry verification.
]
