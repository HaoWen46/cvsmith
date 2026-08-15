"""Contact-routing checks for common email, phone, URL, and identifier forms."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "skills/resume-evaluator/scripts"
sys.dont_write_bytecode = True
sys.path.insert(0, str(SCRIPTS))

import parse_sim  # noqa: E402  (path insertion above is the point)

ACADEMIC_HEADER = (
    "Anna Dahl\n"
    "anna.dahl@uio.no | +47 902 55 118 | "
    "orcid.org/0009-0002-1234-5678 | github.com/adahl\n"
)


def routed(header: str) -> dict:
    lines = [l.strip() for l in header.splitlines() if l.strip()]
    return parse_sim.route_contact(header, lines)


def test_orcid_is_not_routed_as_a_phone():
    contact = routed(ACADEMIC_HEADER)
    assert contact["phones"] == ["+47 902 55 118"], (
        "an ORCID routed into the phone field is the L1 failure this "
        f"layer exists to predict, not to reproduce: {contact['phones']}")


def test_bare_orcid_without_the_orcid_org_prefix_is_not_a_phone():
    # Many CVs print the identifier alone, with no orcid.org/ around it,
    # so URL-masking alone cannot carry this case.
    contact = routed("Anna Dahl\nORCID: 0009-0002-1234-5678\n")
    assert contact["phones"] == [], contact["phones"]


def test_orcid_checksum_x_is_still_not_a_phone():
    contact = routed("Anna Dahl\nORCID 0000-0002-1825-009X\n")
    assert contact["phones"] == [], contact["phones"]


def test_orcid_is_recorded_not_silently_dropped():
    contact = routed(ACADEMIC_HEADER)
    assert "0009-0002-1234-5678" in contact["identifiers"], (
        "dropping the ORCID would trade one routing error for a lost "
        f"field: {contact}")


@pytest.mark.parametrize("header,expected", [
    ("Sam Casey\nsam@example.com | (555) 123-4567", "(555) 123-4567"),
    ("Sam Casey\nsam@example.com | 555-123-4567", "555-123-4567"),
    ("Sam Casey\nsam@example.com | +1 555 123 4567", "+1 555 123 4567"),
    ("Anna Dahl\na@b.no | +47 902 55 118", "+47 902 55 118"),
    ("Yuki Sato\ny@b.jp | +81 90-1234-5678", "+81 90-1234-5678"),
])
def test_real_phone_formats_still_route(header, expected):
    contact = routed(header)
    assert contact["phones"] == [expected], (
        f"the identifier guard swallowed a real phone number: {contact}")


def test_email_is_not_split_into_pseudo_urls():
    contact = routed(ACADEMIC_HEADER)
    assert contact["emails"] == ["anna.dahl@uio.no"]
    assert contact["urls"] == ["orcid.org/0009-0002-1234-5678",
                               "github.com/adahl"], (
        "the local part and domain of the email leaked into the URL "
        f"field as two pseudo-links: {contact['urls']}")


def test_email_domain_is_not_a_url_even_when_it_looks_like_one():
    contact = routed("Sam Casey\nsam.casey@github.com\n")
    assert contact["urls"] == [], contact["urls"]


ACADEMIC_TYPST = """\
#set page(paper: "us-letter", margin: 0.6in)
#set text(size: 10pt)
#align(center)[
  #text(size: 16pt, weight: "bold")[Anna Dahl] \\
  anna.dahl\\@uio.no | +47 902 55 118 | orcid.org/0009-0002-1234-5678 |
  github.com/adahl
]

*EDUCATION*

MSc Physics, University of Oslo, Aug 2023 - Jun 2025

*RESEARCH EXPERIENCE*

Research assistant, Oslo Lab, Jan 2024 - Jun 2025

- Ran lattice simulations on a 4M-cell grid.
"""


@pytest.mark.skipif(not shutil.which("typst"), reason="typst not installed")
def test_academic_header_routes_end_to_end(tmp_path):
    src = tmp_path / "academic_header.typ"
    src.write_text(ACADEMIC_TYPST)
    pdf = tmp_path / "academic_header.pdf"
    subprocess.run(["typst", "compile", str(src), str(pdf)],
                   check=True, capture_output=True, text=True)

    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "parse_sim.py"), str(pdf), "--json"],
        capture_output=True, text=True)
    report = json.loads(proc.stdout)
    contact = report["contact"]

    assert contact["emails"] == ["anna.dahl@uio.no"], contact
    assert contact["phones"] == ["+47 902 55 118"], contact
    assert "0009-0002-1234-5678" in contact["identifiers"], contact
    assert not [u for u in contact["urls"] if "@" in u or u == "uio.no"], (
        f"email fragments still leaking into the URL field: {contact}")
    # And the phone check must not now claim the header has no phone.
    phone_checks = [c for c in report["checks"]
                    if c["check_id"] == "contact_phone"]
    assert not phone_checks, (
        f"a real phone number was routed but still warned: {phone_checks}")
