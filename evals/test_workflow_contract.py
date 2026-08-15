from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (REPO / path).read_text(encoding="utf-8")


def test_five_skills_have_distinct_owners_and_explicit_handoffs():
    evidence = read("skills/candidate-evidence/SKILL.md")
    builder = read("skills/resume-builder/SKILL.md")
    evaluator = read("skills/resume-evaluator/SKILL.md")
    jd = read("skills/jd-analyzer/SKILL.md")
    tracker = read("skills/application-tracker/SKILL.md")
    assert "target-neutral" in evidence
    assert "strongest role-specific resume" in builder
    assert "candidate-evidence" in builder and "Create or update `career-vault.md`" not in builder
    assert all(label in evaluator for label in ("READY TO SEND", "REVISE", "DO NOT APPLY"))
    assert "source line" in jd and "Gate" in jd and "disposable" in jd
    assert "candidate evidence" in evaluator
    assert "prepared" in tracker and "into `applied` only when the user confirms submission" in tracker


def test_programs_are_limited_to_observable_properties():
    readme = read("README.md")
    assert "Scripts measure observable properties" in readme
    assert "Agents decide meaning and usefulness" in readme


def test_practical_risk_and_completion_rules_are_explicit():
    rules = read("skills/resume-builder/references/writing-rules.md")
    evaluator = read("skills/resume-evaluator/SKILL.md")
    assert "Record-risk claims" in rules and "Social acceptability" in rules
    assert "no numeric score is a completion threshold" in evaluator
    assert "no accessible high-value improvement remains" in evaluator


def test_instruction_files_stay_compact():
    skills = sorted(REPO.glob("skills/*/SKILL.md"))
    assert len(skills) == 5
    assert all(len(path.read_text().splitlines()) <= 180 for path in skills)
