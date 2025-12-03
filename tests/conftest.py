# tests/conftest.py
"""Shared fixtures for plugin structure tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

# Tier mapping for nested plugin structure
TIER_MAPPING: dict[str, list[str]] = {
    "essential": ["core", "commit"],
    "methodology": ["workflow", "review", "debug", "testing"],
    "domain": ["python", "doc", "shell"],
    "specialized": ["meta", "blackbox"],
}

# Reverse mapping: plugin -> tier
PLUGIN_TO_TIER: dict[str, str] = {}
for tier, plugins in TIER_MAPPING.items():
    for plugin in plugins:
        PLUGIN_TO_TIER[plugin] = tier


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Return the repository root directory."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def plugins_dir(repo_root: Path) -> Path:
    """Return the plugins directory."""
    return repo_root / "plugins"


@pytest.fixture(scope="session")
def marketplace_data(repo_root: Path) -> dict[str, Any]:
    """Load and return marketplace.json data."""
    marketplace_path = repo_root / ".claude-plugin" / "marketplace.json"
    return json.loads(marketplace_path.read_text())


def get_plugin_path(plugins_dir: Path, plugin_name: str) -> Path:
    """Get the path to a plugin, handling tier structure."""
    tier = PLUGIN_TO_TIER.get(plugin_name)
    if tier:
        return plugins_dir / tier / plugin_name
    # Fallback: check if exists at top level
    return plugins_dir / plugin_name


@pytest.fixture
def all_skills(plugins_dir: Path) -> list[dict[str, Any]]:
    """Return all skills with their metadata."""
    skills = []
    for skill_md in plugins_dir.rglob("**/SKILL.md"):
        content = skill_md.read_text()
        # Parse YAML frontmatter
        if content.startswith("---"):
            _, frontmatter, _ = content.split("---", 2)
            import yaml
            metadata = yaml.safe_load(frontmatter)
            if metadata:
                metadata["path"] = skill_md
                # Find the plugin name from the path
                # Path structure: plugins/tier/plugin/skills/skill-name/SKILL.md
                # or: plugins/plugin/skills/skill-name/SKILL.md
                parts = skill_md.relative_to(plugins_dir).parts
                # Find the part before "skills"
                if "skills" in parts:
                    skills_idx = parts.index("skills")
                    if skills_idx > 0:
                        metadata["plugin"] = parts[skills_idx - 1]
                skills.append(metadata)
    return skills


@pytest.fixture
def all_agents(plugins_dir: Path) -> list[Path]:
    """Return all agent markdown files."""
    return list(plugins_dir.rglob("**/agents/*.md"))


def count_lines(file_path: Path) -> int:
    """Count non-empty lines in a file."""
    return len([line for line in file_path.read_text().splitlines() if line.strip()])


def skill_exists(plugins_dir: Path, qualified_name: str) -> bool:
    """Check if a skill exists by qualified name (plugin:skill)."""
    if ":" not in qualified_name:
        return False
    plugin, skill = qualified_name.split(":", 1)
    plugin_path = get_plugin_path(plugins_dir, plugin)
    skill_path = plugin_path / "skills" / skill / "SKILL.md"
    return skill_path.exists()


def plugin_exists(plugins_dir: Path, plugin_name: str) -> bool:
    """Check if a plugin exists."""
    plugin_path = get_plugin_path(plugins_dir, plugin_name)
    return (plugin_path / ".claude-plugin" / "plugin.json").exists()
