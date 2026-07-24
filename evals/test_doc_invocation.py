"""Doc-reality tripwire for external review finding 2 (round-7): builder
SKILL.md documents `scripts/check_projection.py <resume> career-vault.md`
as something the user types directly, but the file shipped mode 0644 —
exit 126, permission denied, the instant anyone followed the doc. Every
existing test invoked the script via `[sys.executable, str(CHECK), ...]`,
which never touches the file's own execute bit or shebang, so the break
was invisible to the suite while being immediate for a user at a
terminal.

The fix has two layers (belt and braces): the doc now says `uv run
scripts/check_projection.py ...` (uv doesn't care about the exec bit —
it invokes its own interpreter on the file argument), and the script
itself is mode 0755 with a `#!/usr/bin/env -S uv run --script` shebang
so bare direct execution (no `uv run` prefix — muscle memory, tab
completion, an old copy-pasted command) also works.

This test does not hardcode either fix. It pulls the invocation text
straight out of the shipped SKILL.md, substitutes real fixture paths for
the placeholder, and runs the result exactly as a user would paste it —
via a shell, from the skill directory, with no sys.executable escape
hatch. If a future edit drops the `uv run` prefix *and* nobody notices
the script quietly lost its exec bit again, this fails with the same
exit 126 a real user would hit — docs cannot silently rot back to an
unrunnable form without tripping this.
"""

from __future__ import annotations

import re
import shlex
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO / "skills/resume-builder"
SKILL_MD = SKILL_DIR / "SKILL.md"

# Faithful vault/projection pair — deliberately tiny, only needs to clear
# check_projection cleanly (exit 0) so the test measures runnability, not
# the checker's own logic (that's evals/test_projection.py's job).
VAULT = """\
# Career vault — Sam Casey
Updated: 2026-07-01

## Basics
- FACT: Sam Casey · Springfield, USA
- FACT: sam.casey@example.com

## Experience
### Widget Corp — Software Engineering Intern (Jun 2025 – Sep 2025)
- FACT: cut API latency 40% across 3 services
"""

RESUME = """\
meta:
  page_budget: 1
  template: compact

basics:
  name: Sam Casey
  email: sam.casey@example.com

experience:
  - organization: Widget Corp
    title: Software Engineering Intern
    start: 2025-06
    end: 2025-09
    bullets:
      - Cut API latency 40% across 3 services.
"""


def extract_documented_invocation() -> str:
    """Pull the literal check_projection invocation out of shipped
    SKILL.md — not a copy the test maintainer typed, the actual doc
    text, backtick-fenced, whitespace-collapsed across its line wrap."""
    text = SKILL_MD.read_text(encoding="utf-8")
    m = re.search(
        r"`(uv run scripts/check_projection\.py.*?)`",
        text, re.DOTALL)
    assert m, (
        "SKILL.md no longer documents check_projection.py via a "
        "backtick-fenced `uv run scripts/check_projection.py ...` "
        "invocation — either the command moved/changed form, or the "
        "doc regressed to the bare (unrunnable-without-a-chmod) form "
        "this test exists to catch. Update the extraction or fix the doc.")
    return " ".join(m.group(1).split())


def test_documented_check_projection_invocation_actually_runs(tmp_path):
    documented = extract_documented_invocation()
    assert documented.startswith("uv run scripts/check_projection.py"), (
        f"documented form no longer opens with the uv-run invocation: "
        f"{documented!r}")

    resume = tmp_path / "resume-widget-swe.yaml"
    vault = tmp_path / "career-vault.md"
    resume.write_text(RESUME)
    vault.write_text(VAULT)

    # Substitute the doc's placeholder and its literal `career-vault.md`
    # arg with the real fixture paths, then run the command *exactly* as
    # extracted — same shell-splitting a user's terminal would do, cwd
    # at the skill root the doc assumes, no sys.executable prefix.
    command = documented.replace(
        "<the file you just named>", str(resume)
    ).replace("career-vault.md", str(vault))

    proc = subprocess.run(
        shlex.split(command), cwd=SKILL_DIR,
        capture_output=True, text=True)

    assert proc.returncode == 0, (
        f"documented invocation {documented!r} did not run cleanly on a "
        f"faithful fixture (this is exactly the exit-126-on-a-fresh-"
        f"checkout failure mode):\n"
        f"cmd: {command}\nstdout: {proc.stdout}\nstderr: {proc.stderr}")
