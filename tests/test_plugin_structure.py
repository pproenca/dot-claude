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

    def test_debug_skill_references_exist(self, plugins_dir: Path) -> None:
        """All debug:* references should point to existing skills or agents."""
        import re

        debug_refs = set()
        for md_file in plugins_dir.rglob("*.md"):
            content = md_file.read_text()
            # Match debug:skill-name patterns
            refs = re.findall(r"debug:([a-z][a-z0-9-]+)", content)
            debug_refs.update(refs)

        for ref in debug_refs:
            exists = skill_exists(plugins_dir, f"debug:{ref}") or agent_exists(plugins_dir, f"debug:{ref}")
            assert exists, f"Reference debug:{ref} not found as skill or agent"


class TestCurrentState:
    """Tests documenting current state (baseline)."""

    def test_super_plugin_exists(self, plugins_dir: Path) -> None:
        """Super plugin should exist in current state."""
        assert plugin_exists(plugins_dir, "super")

    def test_super_has_expected_skill_count(self, all_skills: list[dict[str, Any]]) -> None:
        """Super should have 16 skills after Phase 3 (moved 3 to debug)."""
        super_skills = [s for s in all_skills if s.get("plugin") == "super"]
        assert len(super_skills) == 16, f"Expected 16 super skills, found {len(super_skills)}"

    def test_debug_plugin_exists(self, plugins_dir: Path) -> None:
        """Debug plugin should exist."""
        assert plugin_exists(plugins_dir, "debug")


class TestPhase1TokenEfficiency:
    """Tests for Phase 1: Token efficiency improvements."""

    def test_mermaid_expert_under_100_lines(self, plugins_dir: Path) -> None:
        """Mermaid expert agent should be <100 lines after extraction."""
        agent_path = plugins_dir / "doc" / "agents" / "mermaid-expert.md"
        lines = count_lines(agent_path)
        assert lines < 100, f"mermaid-expert.md has {lines} lines, expected <100"

    def test_mermaid_reference_exists(self, plugins_dir: Path) -> None:
        """Mermaid syntax reference file should exist."""
        ref_path = plugins_dir / "doc" / "agents" / "references" / "mermaid-syntax.md"
        assert ref_path.exists(), "mermaid-syntax.md reference not found"

    def test_devops_troubleshooter_under_80_lines(self, plugins_dir: Path) -> None:
        """DevOps troubleshooter should be <80 lines after trimming."""
        agent_path = plugins_dir / "debug" / "agents" / "devops-troubleshooter.md"
        lines = count_lines(agent_path)
        assert lines < 80, f"devops-troubleshooter.md has {lines} lines, expected <80"

    def test_diagram_generator_under_50_lines(self, plugins_dir: Path) -> None:
        """Diagram generator should delegate to mermaid-expert."""
        agent_path = plugins_dir / "super" / "agents" / "diagram-generator.md"
        lines = count_lines(agent_path)
        assert lines < 50, f"diagram-generator.md has {lines} lines, expected <50"

    def test_diagram_generator_delegates(self, plugins_dir: Path) -> None:
        """Diagram generator should reference mermaid-expert."""
        agent_path = plugins_dir / "super" / "agents" / "diagram-generator.md"
        content = agent_path.read_text()
        assert "mermaid-expert" in content.lower() or "doc:" in content


class TestPhase2Naming:
    """Tests for Phase 2: Naming improvements."""

    def test_skill_names_are_concise(self, all_skills: list[dict[str, Any]]) -> None:
        """Super plugin skill names should not exceed 20 characters."""
        # These skills will be merged in Phase 4, not renamed in Phase 2
        phase4_merge_candidates = {"requesting-code-review", "receiving-code-review"}
        long_names = []
        for skill in all_skills:
            # Phase 2 only renames super plugin skills
            if skill.get("plugin") != "super":
                continue
            name = skill.get("name", "")
            if name in phase4_merge_candidates:
                continue
            if len(name) > 20:
                long_names.append(f"{name} ({len(name)} chars)")
        assert not long_names, f"Super skills with names >20 chars: {long_names}"

    def test_descriptions_use_when_pattern(self, all_skills: list[dict[str, Any]]) -> None:
        """All descriptions should start with 'Use when'."""
        non_compliant = []
        for skill in all_skills:
            desc = skill.get("description", "")
            if not desc.lower().startswith("use when"):
                non_compliant.append(f"{skill.get('name')}: {desc[:50]}...")
        assert not non_compliant, f"Skills not starting with 'Use when': {non_compliant}"


class TestPhase3Debugging:
    """Tests for Phase 3: Consolidate debugging."""

    def test_debugging_skills_in_debug_plugin(self, plugins_dir: Path) -> None:
        """All debugging skills should be in debug plugin."""
        debug_skills = ["systematic", "root-cause", "defense-in-depth"]
        for skill in debug_skills:
            assert skill_exists(plugins_dir, f"debug:{skill}"), f"debug:{skill} not found"

    def test_super_no_debugging_skills(self, plugins_dir: Path) -> None:
        """Super should not have debugging skills after move."""
        old_skills = ["systematic-debugging", "root-cause-tracing", "defense-in-depth"]
        for skill in old_skills:
            assert not skill_exists(plugins_dir, f"super:{skill}"), f"super:{skill} should be removed"
