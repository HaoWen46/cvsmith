# Identity, education, and eligibility
Lifecycle: active
Scope: Candidate identity, education, contact, and application-gate records
Dates: 2023-09 to 2027-12 education record; inspected 2026-08-16

## Problem and context
The synthetic source supplies identity, contact, education, and work-authorization values needed by later applications, but no independent verification artifact.

## Candidate actions and ownership
- The record attributes the identity, enrollment, GPA, coursework, honors, links, and authorization statement to Sam Casey.
- Unknown: Whether any value is current or independently verified; every value is reserved synthetic test data.

## Mechanisms
- Preserve exact record values and visible uncertainty rather than treating a resume, link, or candidate statement as third-party verification.

## Outcomes and artifacts
- University of Washington B.S. Computer Science record from Sep 2023 through Dec 2027 with GPA 3.8/4.0, Dean's List for 6 quarters, and coursework in Machine Learning, Distributed Systems, NLP, and Databases.
- Contact record: Sam Casey, sam.casey@example.com, +1 (555) 010-4477, Seattle, WA, https://github.com/samcasey-demo, and https://samcasey.example.com.
- Eligibility record: US work authorization with no sponsorship required for internships.

## Evidence map
- FACT: Exact values above are present in the supplied synthetic legacy vault.
- SOURCE: `synthetic-source:../career-vault.md#basics` and `#education` — sha256 `268f01e810c350fa868898ddd6b13328b0d3979e97ada49d65d97d98908f0cbd`.

## Relationships
- Graduation and authorization may become gates in a target brief, but this record contains no target recommendation.

## Currentness
- Historical support: The fixture contains the values.
- Present capability: Not applicable; legal and educational currentness are unknown outside the fixture.

## Conflicts and questions
- Conflict: None supplied.
- Question: What current official records would verify identity, enrollment, expected graduation, GPA, and authorization for a real candidate?

## Lifecycle
- State: active.
- Reason: These records remain necessary inputs for future applications.
- Revive when: Not applicable while active.
