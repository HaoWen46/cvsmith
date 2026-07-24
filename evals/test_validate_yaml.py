"""validate_yaml.py catches every planted schema violation with the right
yaml path and raises zero false positives on the real fixtures.

Same harness style as test_evaluator.py: scripts run under the ambient
interpreter (pyyaml present), --json output is the assertion surface.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "skills/resume-builder/scripts/validate_yaml.py"
FIXTURES = {
    "resume-sample": REPO / "evals/fixtures/resume-sample/resume.yaml",
    "academic-sample": REPO / "evals/fixtures/academic-sample/resume.yaml",
}


def run_validator(path: Path) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(path), "--json"],
        capture_output=True, text=True)
    assert proc.returncode in (0, 1), f"validator crashed:\n{proc.stderr}"
    return proc.returncode, json.loads(proc.stdout)


def fails(report: dict) -> list[dict]:
    return [c for c in report["checks"] if c["level"] == "fail"]


def mutated(tmp_path: Path, fixture: str, old: str, new: str) -> Path:
    src = FIXTURES[fixture].read_text()
    assert old in src, f"fixture drifted: {old!r} not found in {fixture}"
    out = tmp_path / "resume.yaml"
    out.write_text(src.replace(old, new))
    return out


# ── zero false positives on the real fixtures ────────────────────────

@pytest.mark.parametrize("fixture", sorted(FIXTURES))
def test_real_fixture_passes_clean(fixture):
    code, report = run_validator(FIXTURES[fixture])
    assert code == 0, f"false positive on {fixture}: {report}"
    assert report["verdict"] == "pass"
    assert not fails(report)
    warns = [c for c in report["checks"] if c["level"] == "warn"]
    assert not warns, f"unexpected warnings on {fixture}: {warns}"


# ── duplicate keys: the later block silently replaces the earlier ────

def test_duplicate_top_level_section_is_caught(tmp_path):
    src = FIXTURES["resume-sample"].read_text()
    dup = src + textwrap.dedent("""
        projects:
          - name: shadow-project
            bullets:
              - The second projects block silently replaced the first.
    """)
    out = tmp_path / "resume.yaml"
    out.write_text(dup)
    code, report = run_validator(out)
    assert code == 1, "a duplicate top-level section must fail validation"
    f = [c for c in fails(report) if c["check_id"] == "duplicate_keys"]
    assert f, f"expected a duplicate_keys violation: {fails(report)}"
    assert "projects" in f[0]["detail"]
    assert "line" in f[0]["detail"], "both definitions must be locatable"


def test_duplicate_nested_key_is_caught(tmp_path):
    bad = mutated(tmp_path, "resume-sample", "  name: Sam Casey\n",
                  "  name: Sam Casey\n  name: Casey Sam\n")
    code, report = run_validator(bad)
    assert code == 1
    f = [c for c in fails(report) if c["check_id"] == "duplicate_keys"]
    assert f, f"expected a duplicate_keys violation: {fails(report)}"
    assert "name" in f[0]["detail"]


def test_no_duplicates_reports_pass_line(tmp_path):
    code, report = run_validator(FIXTURES["resume-sample"])
    assert code == 0
    line = [c for c in report["checks"] if c["check_id"] == "duplicate_keys"]
    assert len(line) == 1 and line[0]["level"] == "pass"


# ── every planted violation is caught, with the right yaml path ──────

def test_optional_key_typo_is_caught(tmp_path):
    bad = mutated(tmp_path, "resume-sample", "honors:", "honours:")
    code, report = run_validator(bad)
    assert code == 1
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert f[0]["check_id"] == "known_keys"
    assert "education[0].honours" in f[0]["detail"]
    assert "honors" in f[0]["detail"], "suggestion must surface the fix"


def test_top_level_section_typo_is_caught(tmp_path):
    bad = mutated(tmp_path, "resume-sample", "\nprojects:\n", "\nproject:\n")
    code, report = run_validator(bad)
    assert code == 1
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert f[0]["check_id"] == "known_keys"
    assert f[0]["detail"].startswith("project:")
    assert "projects" in f[0]["detail"], "suggestion must surface the fix"
    assert "render" in f[0]["detail"], \
        "the silent-content-loss consequence must be named"


def test_bad_month_is_caught(tmp_path):
    bad = mutated(tmp_path, "resume-sample",
                  "start: 2025-06", "start: 2025-13")
    code, report = run_validator(bad)
    assert code == 1
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert f[0]["check_id"] == "dates"
    assert "experience[0].start" in f[0]["detail"]
    assert "2025-13" in f[0]["detail"]


def test_reversed_experience_dates_fail(tmp_path):
    # start after end, both resolvable, end not "present" — this is not a
    # format problem (date_of already passes both), it's a chronology lie
    yml = textwrap.dedent("""\
        basics:
          name: Test Person
          email: test@example.com
        experience:
          - organization: Somewhere Labs
            title: Intern
            start: 2025-09
            end: 2025-06
            bullets: [Did a thing.]
        """)
    path = tmp_path / "resume.yaml"
    path.write_text(yml)
    code, report = run_validator(path)
    assert code == 1
    f = fails(report)
    ids = [c["check_id"] for c in f]
    assert "chronology" in ids, f"reversed start/end must fail: {f}"
    detail = " ".join(c["detail"] for c in f if c["check_id"] == "chronology")
    assert "experience[0]" in detail
    assert "2025-09" in detail and "2025-06" in detail


def test_reversed_education_dates_fail(tmp_path):
    yml = textwrap.dedent("""\
        basics:
          name: Test Person
          email: test@example.com
        education:
          - institution: Somewhere State
            degree: B.S.
            field: Computer Science
            start: 2026-09
            end: 2022-06
        """)
    path = tmp_path / "resume.yaml"
    path.write_text(yml)
    code, report = run_validator(path)
    assert code == 1
    f = fails(report)
    ids = [c["check_id"] for c in f]
    assert "chronology" in ids, f"reversed education dates must fail: {f}"
    assert "education[0]" in " ".join(
        c["detail"] for c in f if c["check_id"] == "chronology")


def test_year_only_reversed_dates_fail(tmp_path):
    # year-only precision is still enough to catch an unambiguous reversal
    yml = textwrap.dedent("""\
        basics:
          name: Test Person
          email: test@example.com
        experience:
          - organization: Somewhere Labs
            title: Intern
            start: "2026"
            end: "2024"
            bullets: [Did a thing.]
        """)
    path = tmp_path / "resume.yaml"
    path.write_text(yml)
    code, report = run_validator(path)
    assert code == 1
    ids = [c["check_id"] for c in fails(report)]
    assert "chronology" in ids


def test_ongoing_role_end_present_does_not_trigger_chronology(tmp_path):
    # the round-4 ongoing-role WARN must not regress into a chronology FAIL
    yml = textwrap.dedent("""\
        basics:
          name: Test Person
          email: test@example.com
        experience:
          - organization: Somewhere Labs
            title: Intern
            start: 2025-09
            end: present
            bullets: [Did a thing.]
        """)
    path = tmp_path / "resume.yaml"
    path.write_text(yml)
    code, report = run_validator(path)
    assert code == 0, f"'present' must never be treated as reversed: {report}"
    assert not fails(report)


# ── 'present' is only meaningful as an end value ──────────────────────

def test_experience_start_present_fails(tmp_path):
    # start: present, end: 2025-06 is an impossible chronology that the
    # old code let through silently: date_of accepted 'present' anywhere,
    # and chronology() treats an unresolvable 'present' start as nothing
    # to compare — so neither check ever saw the entry as broken.
    yml = textwrap.dedent("""\
        basics:
          name: Test Person
          email: test@example.com
        experience:
          - organization: Somewhere Labs
            title: Intern
            start: present
            end: 2025-06
            bullets: [Did a thing.]
        """)
    path = tmp_path / "resume.yaml"
    path.write_text(yml)
    code, report = run_validator(path)
    assert code == 1, f"start: present must fail, not render an impossible chronology: {report}"
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert f[0]["check_id"] == "dates"
    assert "experience[0].start" in f[0]["detail"]
    assert "end date" in f[0]["detail"]


def test_education_start_present_fails(tmp_path):
    yml = textwrap.dedent("""\
        basics:
          name: Test Person
          email: test@example.com
        education:
          - institution: Somewhere State
            degree: B.S.
            field: Computer Science
            start: present
            end: 2022-06
        """)
    path = tmp_path / "resume.yaml"
    path.write_text(yml)
    code, report = run_validator(path)
    assert code == 1, f"start: present must fail for education too: {report}"
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert f[0]["check_id"] == "dates"
    assert "education[0].start" in f[0]["detail"]


def test_project_start_present_fails(tmp_path):
    yml = textwrap.dedent("""\
        basics:
          name: Test Person
          email: test@example.com
        projects:
          - name: Ledger Lite
            start: present
            end: 2025-06
            bullets: [Built a thing.]
        """)
    path = tmp_path / "resume.yaml"
    path.write_text(yml)
    code, report = run_validator(path)
    assert code == 1, f"start: present must fail for projects too: {report}"
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert f[0]["check_id"] == "dates"
    assert "projects[0].start" in f[0]["detail"]


def test_award_date_present_fails(tmp_path):
    # awards[].date is a singleton — no 'end' to pair 'present' against,
    # the same absurdity the start: present acceptance enabled elsewhere
    yml = textwrap.dedent("""\
        basics:
          name: Test Person
          email: test@example.com
        awards:
          - name: Dean's List
            date: present
        """)
    path = tmp_path / "resume.yaml"
    path.write_text(yml)
    code, report = run_validator(path)
    assert code == 1, f"awards[].date: present must fail: {report}"
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert f[0]["check_id"] == "dates"
    assert "awards[0].date" in f[0]["detail"]


def test_link_missing_url_is_caught(tmp_path):
    bad = mutated(
        tmp_path, "resume-sample",
        "- label: GitHub\n      url: https://github.com/samcasey-demo\n",
        "- label: GitHub\n")
    code, report = run_validator(bad)
    assert code == 1
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert f[0]["check_id"] == "required_keys"
    assert "basics.links[0]" in f[0]["detail"]
    assert "url" in f[0]["detail"]


def test_empty_bullets_is_caught(tmp_path):
    yml = textwrap.dedent("""\
        basics:
          name: Test Person
          email: test@example.com
        experience:
          - organization: Somewhere Labs
            title: Intern
            start: 2025-06
            end: 2025-09
            bullets: []
        """)
    path = tmp_path / "resume.yaml"
    path.write_text(yml)
    code, report = run_validator(path)
    assert code == 1
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert f[0]["check_id"] == "empties"
    assert "experience[0].bullets" in f[0]["detail"]


def test_bad_group_enum_is_caught(tmp_path):
    # unknown group values silently drop the entry from a grouped render
    bad = mutated(tmp_path, "academic-sample",
                  "group: industry", "group: volunteer")
    code, report = run_validator(bad)
    assert code == 1
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert f[0]["check_id"] == "values"
    assert "experience[3].group" in f[0]["detail"]
    assert "volunteer" in f[0]["detail"]


# ── values that pass validation but crash the render ─────────────────

def test_out_of_enum_paper_fails(tmp_path):
    # templates feed meta.paper straight to set page(paper:); anything
    # outside us-letter | a4 crashes the compile with a 100-name enum dump
    bad = mutated(tmp_path, "resume-sample",
                  "page_budget: 1", "page_budget: 1\n  paper: legal")
    code, report = run_validator(bad)
    assert code == 1
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert f[0]["check_id"] == "values"
    assert "meta.paper" in f[0]["detail"]
    assert "legal" in f[0]["detail"]
    assert "crash" in f[0]["detail"], \
        "the render-crash consequence must be named"


def test_blank_name_fails(tmp_path):
    # "" satisfies presence + isinstance(str); the compile then dies with
    # 'PDF/UA-1 error: heading title is empty'
    bad = mutated(tmp_path, "resume-sample", "name: Sam Casey", 'name: ""')
    code, report = run_validator(bad)
    assert code == 1
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert "basics.name" in f[0]["detail"]
    assert "compile" in f[0]["detail"], \
        "the compile-failure consequence must be named"


def test_blank_email_fails(tmp_path):
    bad = mutated(tmp_path, "resume-sample",
                  "email: sam.casey@example.com", 'email: "  "')
    code, report = run_validator(bad)
    assert code == 1
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert "basics.email" in f[0]["detail"]


def test_blank_organization_fails(tmp_path):
    # "" satisfies presence + isinstance(str) in every entry section; the
    # entry renders with the employer silently missing — a title floating
    # over an orphaned date line
    bad = mutated(tmp_path, "resume-sample",
                  "organization: Meridian Labs", 'organization: ""')
    code, report = run_validator(bad)
    assert code == 1
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert f[0]["check_id"] == "empties"
    assert "experience[0].organization" in f[0]["detail"]
    assert "missing" in f[0]["detail"], \
        "the silent-loss consequence must be named"


def test_whitespace_only_degree_fails(tmp_path):
    bad = mutated(tmp_path, "resume-sample", "degree: B.S.", 'degree: "   "')
    code, report = run_validator(bad)
    assert code == 1
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert f[0]["check_id"] == "empties"
    assert "education[0].degree" in f[0]["detail"]


def test_all_nine_blankable_identity_fields_fail(tmp_path):
    # one blank per guarded identity field across all six entry sections
    yml = textwrap.dedent("""\
        basics:
          name: Test Person
          email: test@example.com
        education:
          - institution: ""
            degree: ""
            field: ""
        experience:
          - organization: ""
            title: ""
            bullets: [Did a thing.]
        projects:
          - name: ""
            bullets: [Built a thing.]
        skills:
          - label: ""
            items: [Python]
        publications:
          - citation: ""
        awards:
          - name: ""
        """)
    path = tmp_path / "resume.yaml"
    path.write_text(yml)
    code, report = run_validator(path)
    assert code == 1
    f = [c for c in fails(report) if c["check_id"] == "empties"]
    paths = ("education[0].institution", "education[0].degree",
             "education[0].field", "experience[0].organization",
             "experience[0].title", "projects[0].name", "skills[0].label",
             "publications[0].citation", "awards[0].name")
    assert len(f) == len(paths), f"expected all nine blanks flagged: {f}"
    for p in paths:
        assert any(p in c["detail"] for c in f), f"{p} not flagged: {f}"


def test_tracking_param_url_fails(tmp_path):
    # data-schema.md promises tracking-parameter URLs are a lint error
    bad = mutated(
        tmp_path, "resume-sample",
        "url: https://github.com/samcasey-demo\n",
        "url: https://github.com/samcasey-demo?utm_source=chatgpt.com\n")
    code, report = run_validator(bad)
    assert code == 1
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert f[0]["check_id"] == "urls"
    assert "basics.links[0].url" in f[0]["detail"]
    assert "utm_source" in f[0]["detail"]


def test_tracking_param_project_url_fails(tmp_path):
    # templates print projects[].url verbatim too
    bad = mutated(
        tmp_path, "resume-sample",
        "url: https://github.com/samcasey-demo/ledgerlite\n",
        "url: https://github.com/samcasey-demo/ledgerlite?fbclid=abc123\n")
    code, report = run_validator(bad)
    assert code == 1
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert f[0]["check_id"] == "urls"
    assert "projects[0].url" in f[0]["detail"]
    assert "fbclid" in f[0]["detail"]


def test_tracking_param_publication_url_fails(tmp_path):
    # and publications[].url
    bad = mutated(
        tmp_path, "resume-sample",
        "url: https://example.com/hotcloud25-preemption.pdf\n",
        "url: https://example.com/hotcloud25-preemption.pdf?gclid=x1\n")
    code, report = run_validator(bad)
    assert code == 1
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert f[0]["check_id"] == "urls"
    assert "publications[0].url" in f[0]["detail"]
    assert "gclid" in f[0]["detail"]


# ── render.sh fails closed when uv is missing ────────────────────────

def test_render_sh_fails_closed_without_uv(tmp_path):
    """No uv means no schema gate — render.sh must refuse to render,
    not ship a PDF with content silently missing."""
    render = REPO / "skills/resume-builder/scripts/render.sh"
    if shutil.which("typst") is None:
        pytest.skip("typst not installed; render.sh exits before the uv gate")
    bindir = tmp_path / "bin"
    bindir.mkdir()
    for name in ("bash", "awk", "dirname", "basename", "grep", "typst",
                 "mktemp", "cp", "cat", "rm", "tr", "wc", "stat"):
        real = shutil.which(name)
        if real is None:
            pytest.skip(f"{name} not on PATH; cannot assemble restricted PATH")
        (bindir / name).symlink_to(real)
    data = tmp_path / "resume.yaml"
    data.write_text(FIXTURES["resume-sample"].read_text())
    env = {"PATH": str(bindir),
           "HOME": os.environ.get("HOME", str(tmp_path)),
           "TMPDIR": os.environ.get("TMPDIR", "/tmp")}
    proc = subprocess.run(
        [str(bindir / "bash"), str(render), str(data)],
        capture_output=True, text=True, env=env, cwd=tmp_path)
    assert proc.returncode == 1, (
        f"must fail closed without uv, got exit {proc.returncode}\n"
        f"stdout: {proc.stdout}\nstderr: {proc.stderr}")
    assert "error" in proc.stderr and "uv" in proc.stderr, \
        f"stderr must name the missing gate: {proc.stderr}"
    assert not (tmp_path / "resume.pdf").exists(), \
        "no PDF may ship unvalidated"


# ── the exit-code contract's third leg ───────────────────────────────

def test_unparseable_yaml_exits_2(tmp_path):
    path = tmp_path / "broken.yaml"
    path.write_text("basics: [unclosed\n")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(path), "--json"],
        capture_output=True, text=True)
    assert proc.returncode == 2
    assert "error:" in proc.stderr
