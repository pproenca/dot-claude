# tests/test_plugin_structure.py
"""Tests for plugin structure validation."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest

from conftest import count_lines, plugin_exists, skill_exists


class TestPluginValidation:
    """Tests that all plugins pass claude plugin validate."""

    def test_all_plugins_validate(self, plugins_dir: Path) -> None:
        """All plugins should pass claude plugin validate."""
        for plugin_path in plugins_dir.iterdir():
            if plugin_path.is_dir():
                result = subprocess.run(
                    ["claude", "plugin", "validate", str(plugin_path)],
                    capture_output=True,
                )
                assert result.returncode == 0, f"Plugin {plugin_path.name} failed validation"


class TestSkillMetadata:
    """Tests for skill YAML frontmatter."""

    def test_all_skills_have_name(self, all_skills: list[dict[str, Any]]) -> None:
        """All skills must have a name in frontmatter."""
        for skill in all_skills:
            assert "name" in skill, f"Skill at {skill.get('path')} missing name"

    def test_all_skills_have_description(self, all_skills: list[dict[str, Any]]) -> None:
        """All skills must have a description in frontmatter."""
        for skill in all_skills:
            assert "description" in skill, f"Skill {skill.get('name')} missing description"


def agent_exists(plugins_dir: Path, qualified_name: str) -> bool:
    """Check if an agent exists by qualified name (plugin:agent)."""
    if ":" not in qualified_name:
        return False
    plugin, agent = qualified_name.split(":", 1)
    agent_path = plugins_dir / plugin / "agents" / f"{agent}.md"
    return agent_path.exists()


class TestCrossReferences:
    """Tests for cross-plugin reference integrity."""

    def test_super_skill_references_exist(self, plugins_dir: Path) -> None:
        """All super:* references should point to existing skills or agents."""
        import re

        super_refs = set()
        for md_file in plugins_dir.rglob("*.md"):
            content = md_file.read_text()
            # Match super:skill-name patterns
            refs = re.findall(r"super:([a-z0-9-]+)", content)
            super_refs.update(refs)

        for ref in super_refs:
            exists = skill_exists(plugins_dir, f"super:{ref}") or agent_exists(plugins_dir, f"super:{ref}")
            assert exists, f"Reference super:{ref} not found as skill or agent"

    def test_python_skill_references_exist(self, plugins_dir: Path) -> None:
        """All python:* references should point to existing skills or agents."""
        import re

        python_refs = set()
        for md_file in plugins_dir.rglob("*.md"):
            content = md_file.read_text()
            # Match python:skill-name patterns (must contain hyphen or letters, not just numbers)
            refs = re.findall(r"python:([a-z][a-z0-9-]+)", content)
            python_refs.update(refs)

        for ref in python_refs:
            exists = skill_exists(plugins_dir, f"python:{ref}") or agent_exists(plugins_dir, f"python:{ref}")
            assert exists, f"Reference python:{ref} not found as skill or agent"


class TestCurrentState:
    """Tests documenting current state (baseline)."""

    def test_super_plugin_exists(self, plugins_dir: Path) -> None:
        """Super plugin should exist in current state."""
        assert plugin_exists(plugins_dir, "super")

    def test_super_has_expected_skill_count(self, all_skills: list[dict[str, Any]]) -> None:
        """Super should have 19 skills in current state."""
        super_skills = [s for s in all_skills if s.get("plugin") == "super"]
        assert len(super_skills) == 19, f"Expected 19 super skills, found {len(super_skills)}"

    def test_debug_plugin_exists(self, plugins_dir: Path) -> None:
        """Debug plugin should exist."""
        assert plugin_exists(plugins_dir, "debug")
