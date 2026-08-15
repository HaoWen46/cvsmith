from __future__ import annotations

import json
import tomllib
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
EXPECTED_SKILLS = {
    "application-tracker",
    "candidate-evidence",
    "jd-analyzer",
    "resume-builder",
    "resume-evaluator",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_skills() -> set[str]:
    return {
        path.name
        for path in (REPO / "skills").iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    }


def test_canonical_skill_set_is_the_public_five():
    assert canonical_skills() == EXPECTED_SKILLS


def test_codex_plugin_exposes_the_canonical_skill_tree():
    manifest = load_json(REPO / ".codex-plugin/plugin.json")
    project = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert manifest["name"] == "cvsmith"
    assert manifest["version"] == project["version"]
    assert manifest["license"] == "MIT"
    assert manifest["skills"] == "./skills/"
    assert (REPO / manifest["skills"]).resolve() == (REPO / "skills").resolve()


def test_codex_marketplace_installs_the_root_plugin():
    marketplace = load_json(REPO / ".agents/plugins/marketplace.json")
    assert marketplace["name"] == "cvsmith"
    assert marketplace["interface"]["displayName"] == "cvsmith"
    assert len(marketplace["plugins"]) == 1
    entry = marketplace["plugins"][0]
    assert entry["name"] == "cvsmith"
    assert entry["source"] == {"source": "local", "path": "./"}
    assert entry["policy"] == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}
    assert entry["category"] == "Productivity"


def test_claude_marketplace_exposes_every_canonical_skill_once():
    marketplace = load_json(REPO / ".claude-plugin/marketplace.json")
    project = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert marketplace["name"] == "cvsmith"
    assert marketplace["metadata"]["version"] == project["version"]
    assert len(marketplace["plugins"]) == 1
    plugin = marketplace["plugins"][0]
    assert plugin["name"] == "cvsmith"
    assert plugin["source"] == "./"
    assert plugin["strict"] is False
    declared = [Path(path) for path in plugin["skills"]]
    assert {path.name for path in declared} == EXPECTED_SKILLS
    assert len(declared) == len(EXPECTED_SKILLS)
    assert all((REPO / path / "SKILL.md").is_file() for path in declared)


def test_readme_leads_with_repository_driven_host_neutral_installation():
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    install = readme.split("## Install", maxsplit=1)[1].split("## Start the workflow", maxsplit=1)[0]
    assert "### Install with your agent" in install
    assert "https://github.com/HaoWen46/cvsmith" in install
    assert "native user-level skill or plugin mechanism" in install
    assert "~/.agents/skills/" in install
    assert "<project>/.agents/skills/" in install
    assert "does not define a universal installer" in install
    assert "npx skills" not in install
    for skill in EXPECTED_SKILLS:
        assert f"`skills/{skill}/`" in install


def test_readme_documents_complete_native_plugin_commands():
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    assert "claude plugin marketplace add HaoWen46/cvsmith" in readme
    assert "claude plugin install cvsmith@cvsmith" in readme
    assert "codex plugin marketplace add HaoWen46/cvsmith" in readme
    assert "codex plugin add cvsmith@cvsmith" in readme


def test_readme_does_not_require_the_third_party_npm_installer():
    text = (REPO / "README.md").read_text(encoding="utf-8")
    assert "npx skills" not in text
    assert "cross-client `skills` installer" not in text
