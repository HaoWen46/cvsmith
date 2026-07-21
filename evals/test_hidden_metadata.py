"""hidden_text_check.py's metadata pass and poppler degrade, executable:
docinfo smuggling is caught and quoted, clean builder output stays clean,
and a poppler-less host loses only the ink check — never the verdict.

The stuffed fixture compiles straight from broken-src (metadata needs no
render pipeline); the clean PDF goes through the real render path.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "skills/resume-evaluator/scripts/hidden_text_check.py"
STUFFED_SRC = REPO / "evals/fixtures/broken-src/metadata_stuffed.typ"
GOOD_YAML = REPO / "evals/fixtures/resume-sample/resume.yaml"
RENDER_SH = REPO / "skills/resume-builder/scripts/render.sh"


@pytest.fixture(scope="session")
def stuffed_pdf(tmp_path_factory) -> Path:
    pdf = tmp_path_factory.mktemp("stuffed") / "metadata_stuffed.pdf"
    subprocess.run(["typst", "compile", str(STUFFED_SRC), str(pdf)],
                   check=True, capture_output=True, text=True)
    return pdf


@pytest.fixture(scope="session")
def clean_pdf(tmp_path_factory) -> Path:
    pdf = tmp_path_factory.mktemp("clean") / "good.pdf"
    subprocess.run(["bash", str(RENDER_SH), str(GOOD_YAML), "-o", str(pdf)],
                   check=True, capture_output=True, text=True)
    return pdf


def run_check(pdf: Path) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(pdf), "--json"],
        capture_output=True, text=True)
    assert proc.returncode in (0, 1), f"hidden_text_check crashed:\n{proc.stderr}"
    return proc.returncode, json.loads(proc.stdout)


def failed_ids(report: dict) -> set[str]:
    return {c["check_id"] for c in report["checks"] if c["level"] == "fail"}


def checks_by_id(report: dict, check_id: str) -> list[dict]:
    return [c for c in report["checks"] if c["check_id"] == check_id]


# ── the planted metadata failure is caught ───────────────────────────

def test_metadata_injection_is_exposed(stuffed_pdf):
    code, report = run_check(stuffed_pdf)
    assert code == 1
    assert "metadata_injection" in failed_ids(report)
    details = " ".join(c["detail"] for c in checks_by_id(report, "metadata_injection"))
    assert "ignore previous" in details, \
        "the report must quote the injection phrase itself"


def test_metadata_keyword_dump_is_flagged(stuffed_pdf):
    _, report = run_check(stuffed_pdf)
    assert "metadata_stuffing" in failed_ids(report), \
        "a >300-char keywords field must FAIL as a bulk dump"
    assert not checks_by_id(report, "metadata"), \
        "no 'metadata clean' line when metadata checks fired"


def test_stuffed_page_itself_is_honest(stuffed_pdf):
    # the plant lives only in docinfo — every on-page check must pass
    _, report = run_check(stuffed_pdf)
    assert failed_ids(report) <= {"metadata_injection", "metadata_stuffing"}


# ── zero false positives on the real render path ─────────────────────

def test_rendered_resume_metadata_is_clean(clean_pdf):
    code, report = run_check(clean_pdf)
    assert code == 0
    assert report["verdict"] == "pass"
    assert not failed_ids(report)
    clean = checks_by_id(report, "metadata")
    assert len(clean) == 1 and clean[0]["level"] == "pass"
    assert "metadata clean" in clean[0]["detail"]
    # templates emit real title/author — identity must not warn on them
    assert not checks_by_id(report, "metadata_identity")


# ── poppler-missing graceful degrade ─────────────────────────────────

def run_check_without_poppler(pdf: Path) -> tuple[int, dict]:
    """Run the script with pdf2image stubbed so convert_from_path raises,
    simulating a host with the Python deps but no poppler binaries."""
    wrapper = (
        "import sys, types, runpy\n"
        "stub = types.ModuleType('pdf2image')\n"
        "def convert_from_path(*a, **k):\n"
        "    raise RuntimeError('simulated: poppler not installed')\n"
        "stub.convert_from_path = convert_from_path\n"
        "sys.modules['pdf2image'] = stub\n"
        f"sys.argv = ['hidden_text_check.py', {str(pdf)!r}, '--json']\n"
        f"runpy.run_path({str(SCRIPT)!r}, run_name='__main__')\n"
    )
    proc = subprocess.run([sys.executable, "-c", wrapper],
                          capture_output=True, text=True)
    assert proc.returncode in (0, 1), f"degraded run crashed:\n{proc.stderr}"
    return proc.returncode, json.loads(proc.stdout)


def test_clean_pdf_without_poppler_degrades_not_fails(clean_pdf):
    code, report = run_check_without_poppler(clean_pdf)
    assert code == 0, "a clean PDF on a poppler-less host must not FAIL"

    warns = checks_by_id(report, "raster_available")
    assert len(warns) == 1 and warns[0]["level"] == "warn", \
        "the skipped ink check must be announced, not silent"
    assert "poppler" in warns[0]["detail"]

    ran = {c["check_id"] for c in report["checks"]}
    assert {"microscopic_text", "offpage_text", "zero_width_chars"} <= ran, \
        "pdfplumber-only checks must still run without poppler"
    assert "invisible_text" not in ran, \
        "no PASS line for the ink check that never ran"
    assert "faint_text" not in ran


def test_metadata_still_caught_without_poppler(stuffed_pdf):
    # docinfo needs no raster — the smuggling check survives degrade
    code, report = run_check_without_poppler(stuffed_pdf)
    assert code == 1
    assert "metadata_injection" in failed_ids(report)
