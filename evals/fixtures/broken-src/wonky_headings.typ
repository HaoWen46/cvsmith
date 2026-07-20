// Planted failure: creative section headings no field-router recognizes.
// The content is fine; the routing is doomed. parse_sim.py must fail
// core_sections and surface the unrecognized headings.
#set page(paper: "us-letter", margin: 1.4cm)
#set text(size: 10pt)
#align(center)[#text(size: 18pt, weight: 700)[Alex Wanderer]]
#align(center)[alex.wanderer\@example.com · +1 (555) 010-5555 · Chicago, IL]
#v(8pt)

#let wonky(t) = block(above: 12pt, below: 6pt)[#text(weight: 700, size: 11pt)[#upper(t)]]

#wonky[Where I Studied]
*Lakeshore University* — B.S. in Computer Engineering \
Sep 2021 – Jun 2025

#wonky[My Journey So Far]
*Windy City Robotics* — Controls Intern (Jun 2024 – Sep 2024)
- Tuned PID loops for a warehouse AGV fleet, cutting docking failures by half.
- Wrote a CAN-bus fuzzer that surfaced three firmware bugs before field rollout.

#wonky[Things I've Built]
*gantry-sim* · C++
- Physics simulator for gantry cranes used in two undergraduate courses.

#wonky[What I Know]
C++, Python, MATLAB, ROS2, Simulink, Git
