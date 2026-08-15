from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EVALS = REPO / "evals/evals.json"
SKILLS = {
    "application-tracker",
    "candidate-evidence",
    "hiring-project-planner",
    "jd-analyzer",
    "resume-builder",
    "resume-evaluator",
}


def load() -> dict:
    return json.loads(EVALS.read_text())


def test_behavioral_evals_are_well_formed_and_cover_every_skill():
    data = load()
    blocks = data["skills"]
    assert {block["skill_name"] for block in blocks} == SKILLS
    for block in blocks:
        assert block["evals"]
        for index, case in enumerate(block["evals"], 1):
            assert case["id"] == index
            assert case["prompt"].strip() and case["expected_output"].strip()
            assert isinstance(case["files"], list)
            assert case["assertions"] and all(item.strip() for item in case["assertions"])


def test_referenced_fixtures_exist():
    for block in load()["skills"]:
        for case in block["evals"]:
            for file in case["files"]:
                path = REPO / file
                if "evals/fixtures/build/" in file:
                    continue
                assert path.is_file(), f"missing {file}"


def test_scenarios_use_the_current_decision_contract():
    text = EVALS.read_text()
    assert "READY TO SEND" in text and "REVISE" in text and "DO NOT APPLY" in text


def test_scenarios_cover_decisive_product_cases():
    text = EVALS.read_text().casefold()
    for cue in ("hidden text", "ineligible", "sparse", "must-have", "actually sent", "no caus"):
        assert cue in text


def test_candidate_evidence_scenarios_cover_lifecycle_and_artifact_intake():
    block = next(item for item in load()["skills"] if item["skill_name"] == "candidate-evidence")
    text = json.dumps(block).casefold()
    for cue in ("archive", "fixed age", "source revision", "target-neutral", "github", "project report", "untrusted"):
        assert cue in text


def test_hiring_project_planner_scenarios_cover_reduction_research_and_boundary():
    block = next(item for item in load()["skills"] if item["skill_name"] == "hiring-project-planner")
    text = json.dumps(block).casefold()
    for cue in (
        "fresh session",
        "current research",
        "candidate evidence",
        "augment the jd",
        "main agent",
        "research dispatch",
        "plausible answers",
        "percentage",
        "acceptance quota",
        "no project recommended",
        "execution window",
        "do not implement",
        "every jd term",
    ):
        assert cue in text
