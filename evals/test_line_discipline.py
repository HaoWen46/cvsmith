from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def instruction_files() -> list[Path]:
    return sorted(REPO.glob("skills/*/SKILL.md")) + sorted(path for path in REPO.glob("skills/*/references/**/*.md") if path.is_file()) + [REPO / "skills/resume-builder/assets/templates/data-schema.md"]


def test_agent_instruction_surface_stays_decision_dense():
    oversized = {str(path.relative_to(REPO)): len(path.read_text().splitlines()) for path in instruction_files() if len(path.read_text().splitlines()) > 180}
    assert not oversized


def test_instruction_prose_has_no_hard_wrapped_continuation_lines():
    offenders = []
    for path in instruction_files():
        lines = path.read_text().splitlines()
        fenced = False
        frontmatter = lines and lines[0] == "---"
        for index, line in enumerate(lines[:-1]):
            if frontmatter:
                if index > 0 and line == "---":
                    frontmatter = False
                continue
            if line.lstrip().startswith("```"):
                fenced = not fenced
                continue
            nxt = lines[index + 1]
            if fenced or not line.strip() or not nxt.strip():
                continue
            if line.startswith(("#", "-", "|", ">", "---")) or nxt.startswith(("#", "-", "|", ">", "```", "---")):
                continue
            if not line.rstrip().endswith((".", "!", "?", ":", "`", ")")):
                offenders.append(f"{path.relative_to(REPO)}:{index + 1}")
    assert not offenders
