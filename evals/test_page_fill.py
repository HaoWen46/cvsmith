from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pdfplumber
import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
RENDER = REPO / "skills/resume-builder/scripts/render.sh"
FILL = REPO / "skills/resume-builder/scripts/check_fill.py"
BULLETS = REPO / "skills/resume-builder/scripts/check_bullets.py"
SPARSE = REPO / "evals/fixtures/sparse-sample/resume.yaml"
GOOD = REPO / "evals/fixtures/resume-sample/resume.yaml"


def render(data: Path, out: Path, template: str = "compact") -> subprocess.CompletedProcess:
    return subprocess.run([str(RENDER), str(data), "-t", template, "-o", str(out)], capture_output=True, text=True)


def check(pdf: Path, budget: int = 1) -> dict:
    proc = subprocess.run(["uv", "run", "--script", str(FILL), str(pdf), "--budget", str(budget), "--json"], capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)


def check_bullets(pdf: Path, max_lines: int = 1) -> subprocess.CompletedProcess:
    return subprocess.run(["uv", "run", "--script", str(BULLETS), str(pdf), "--max-lines", str(max_lines), "--json"], capture_output=True, text=True)


def source_bullet_count(path: Path) -> int:
    data = yaml.safe_load(path.read_text())
    return sum(len(entry.get("bullets", ())) for section in ("experience", "projects") for entry in data.get(section, ()))


def line_bounds(pdf: Path, text: str) -> tuple[float, float]:
    with pdfplumber.open(pdf) as document:
        words = document.pages[0].extract_words()
    match = next(word for word in words if text in word["text"])
    line = [word for word in words if abs(float(word["top"]) - float(match["top"])) < 1.0]
    return min(float(word["top"]) for word in line), max(float(word["bottom"]) for word in line)


@pytest.mark.skipif(not shutil.which("typst"), reason="typst not installed")
@pytest.mark.parametrize("template", ("onecol", "compact", "classic"))
def test_rendered_templates_are_tagged_one_page_and_extractable(tmp_path, template):
    pdf = tmp_path / f"{template}.pdf"
    proc = render(GOOD, pdf, template)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout
    text = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    assert "Pages:           1" in info and "Tagged:          yes" in info
    assert text.splitlines()[0] == "Sam Casey"
    assert "RAG evaluation" in text and "Rust · SQLite" in text


@pytest.mark.skipif(not shutil.which("typst"), reason="typst not installed")
@pytest.mark.parametrize("template", ("onecol", "compact", "classic"))
def test_entry_title_and_metadata_do_not_touch(tmp_path, template):
    pdf = tmp_path / f"rhythm-{template}.pdf"
    proc = render(GOOD, pdf, template)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    _, title_bottom = line_bounds(pdf, "Meridian")
    metadata_top, _ = line_bounds(pdf, "Jun")
    assert metadata_top - title_bottom >= 1.5


@pytest.mark.skipif(not shutil.which("typst"), reason="typst not installed")
@pytest.mark.parametrize("template", ("onecol", "compact", "classic"))
def test_rendered_templates_use_exactly_one_line_per_bullet(tmp_path, template):
    pdf = tmp_path / f"bullets-{template}.pdf"
    proc = render(GOOD, pdf, template)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    measured = check_bullets(pdf)
    assert measured.returncode == 0, measured.stdout + measured.stderr
    report = json.loads(measured.stdout)
    assert report["distribution"] == {"1": source_bullet_count(GOOD)}


@pytest.mark.skipif(not shutil.which("typst"), reason="typst not installed")
def test_sparse_page_warns_without_blocking_render(tmp_path):
    pdf = tmp_path / "sparse.pdf"
    proc = render(SPARSE, pdf)
    assert proc.returncode == 0 and pdf.is_file()
    report = check(pdf)
    assert report["result"] == "warn"
    assert any(item["check_id"] == "lower_whitespace" and item["level"] == "warn" for item in report["checks"])


@pytest.mark.skipif(not shutil.which("typst"), reason="typst not installed")
def test_one_line_flagship_uses_the_page_with_intent(tmp_path):
    pdf = tmp_path / "flagship.pdf"
    proc = render(GOOD, pdf)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    ratio = check(pdf)["metrics"]["page_measurements"][0]["content_end_ratio"]
    assert 0.74 <= ratio <= 0.88


@pytest.mark.skipif(not shutil.which("typst"), reason="typst not installed")
def test_failed_render_preserves_last_published_pdf(tmp_path):
    pdf = tmp_path / "resume.pdf"
    assert render(GOOD, pdf).returncode == 0
    before = hashlib.sha256(pdf.read_bytes()).hexdigest()
    broken = tmp_path / "broken.yaml"
    broken.write_text(GOOD.read_text().replace("sam.casey@example.com", "sam@", 1))
    assert render(broken, pdf).returncode != 0
    assert hashlib.sha256(pdf.read_bytes()).hexdigest() == before


@pytest.mark.skipif(not shutil.which("typst"), reason="typst not installed")
def test_wrapped_bullet_blocks_publication_and_preserves_last_pdf(tmp_path):
    pdf = tmp_path / "resume.pdf"
    assert render(SPARSE, pdf).returncode == 0
    before = hashlib.sha256(pdf.read_bytes()).hexdigest()
    wrapped = tmp_path / "wrapped.yaml"
    wrapped.write_text(SPARSE.read_text().replace("Built a small internal tool used by the team.", "Built a deliberately overlong internal platform spanning release orchestration, incident response, metrics collection, access controls, deployment validation, service ownership, and cross-team operational reporting for a large engineering organization."))
    proc = render(wrapped, pdf)
    assert proc.returncode != 0
    assert "lines:" in proc.stdout + proc.stderr
    assert hashlib.sha256(pdf.read_bytes()).hexdigest() == before


@pytest.mark.skipif(not shutil.which("typst"), reason="typst not installed")
def test_repeat_render_is_byte_identical_and_reports_full_hashes(tmp_path):
    first, second = tmp_path / "a.pdf", tmp_path / "b.pdf"
    one, two = render(GOOD, first), render(GOOD, second)
    assert one.returncode == two.returncode == 0
    assert first.read_bytes() == second.read_bytes()
    for output in (one.stdout + one.stderr, two.stdout + two.stderr):
        assert any(len(line.rsplit(" ", 1)[-1]) == 64 for line in output.splitlines() if "sha256:" in line)


def test_fill_refuses_an_unreadable_artifact(tmp_path):
    bad = tmp_path / "bad.pdf"
    bad.write_text("not a PDF")
    proc = subprocess.run(["uv", "run", "--script", str(FILL), str(bad), "--json"], capture_output=True, text=True)
    assert proc.returncode == 2 and "could not measure" in proc.stderr
