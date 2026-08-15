# Maintenance

Keep the skills compact, current, and behaviorally useful; history belongs in git rather than in agent instructions.

## Change rule

Change the owning contract instead of adding a second explanation, sidecar status, or script that pretends to decide semantic judgment.

Every paragraph or list item stays on one physical line; every instruction must change agent behavior or be removed.

When a defect is found, add the smallest reproduction at the level that owns it, redesign that level, and delete stale tests and docs tied to the old architecture.

## Verification

Run focused tests while editing, then `uv run pytest evals/ -q`; render the flagship, run the four PDF layers, inspect its page image, and verify the projection inventory against its candidate evidence index or legacy vault.

Package into a temporary output directory with `uv run scripts/package_release.py -o <dir>` and inspect that every documented local path exists in the archive.

Agent behavior cannot be inferred from script tests; before release, use fresh agents on at least one strong case, one sparse case, one unsafe-claim case, and one ineligible target, then compare their artifacts and recommendations with the contract.

Do not publish hardcoded test counts, instruction word counts, review-round totals, or universal employer behavior claims; task-specific current facts belong in the task, not in a permanent skill reference.

## Release

Release only from a clean intended diff after the full tests, flagship render and visual review, behavioral pressure tests, and package inspection pass; set the version and changelog at release time rather than presenting an active checkout as released.
