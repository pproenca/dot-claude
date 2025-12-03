# tests/test_plugin_structure.py
"""Tests for plugin structure validation."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from conftest import count_lines, get_plugin_path, plugin_exists, skill_exists


def find_all_plugins(plugins_dir: Path) -> list[Path]:
    """Find all plugin directories (supports nested tier structure)."""
    plugins = []
    for tier_or_plugin in plugins_dir.iterdir():
        if not tier_or_plugin.is_dir():
            continue
        # Check if this is a direct plugin
        if (tier_or_plugin / ".claude-plugin" / "plugin.json").exists():
            plugins.append(tier_or_plugin)
        else:
            # Tier directory - check subdirectories
            for plugin_dir in tier_or_plugin.iterdir():
                if plugin_dir.is_dir() and (plugin_dir / ".claude-plugin" / "plugin.json").exists():
                    plugins.append(plugin_dir)
    return plugins


class TestPluginValidation:
    """Tests that all plugins pass claude plugin validate."""

    def test_all_plugins_validate(self, plugins_dir: Path) -> None:
        """All plugins should pass claude plugin validate."""
        for plugin_path in find_all_plugins(plugins_dir):
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
    plugin_path = get_plugin_path(plugins_dir, plugin)
    agent_path = plugin_path / "agents" / f"{agent}.md"
    return agent_path.exists()


class TestCrossReferences:
    """Tests for cross-plugin reference integrity."""

    def test_no_super_references_in_plugins(self, plugins_dir: Path) -> None:
        """No super:* references should exist in plugin code after migration."""
        import re

        super_refs = []
        for md_file in plugins_dir.rglob("*.md"):
            content = md_file.read_text()
            refs = re.findall(r"super:([a-z0-9-]+)", content)
            if refs:
                super_refs.append((str(md_file), refs))

        assert not super_refs, f"Found deprecated super:* references: {super_refs}"

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

    def test_core_skill_references_exist(self, plugins_dir: Path) -> None:
        """All core:* references should point to existing skills or agents."""
        import re

        core_refs = set()
        for md_file in plugins_dir.rglob("*.md"):
            content = md_file.read_text()
            refs = re.findall(r"core:([a-z][a-z0-9-]+)", content)
            core_refs.update(refs)

        for ref in core_refs:
            exists = skill_exists(plugins_dir, f"core:{ref}") or agent_exists(plugins_dir, f"core:{ref}")
            assert exists, f"Reference core:{ref} not found as skill or agent"

    def test_workflow_skill_references_exist(self, plugins_dir: Path) -> None:
        """All workflow:* references should point to existing skills or agents."""
        import re

        workflow_refs = set()
        for md_file in plugins_dir.rglob("*.md"):
            content = md_file.read_text()
            refs = re.findall(r"workflow:([a-z][a-z0-9-]+)", content)
            workflow_refs.update(refs)

        for ref in workflow_refs:
            exists = skill_exists(plugins_dir, f"workflow:{ref}") or agent_exists(plugins_dir, f"workflow:{ref}")
            assert exists, f"Reference workflow:{ref} not found as skill or agent"

    def test_review_skill_references_exist(self, plugins_dir: Path) -> None:
        """All review:* references should point to existing skills or agents."""
        import re

        review_refs = set()
        for md_file in plugins_dir.rglob("*.md"):
            content = md_file.read_text()
            refs = re.findall(r"review:([a-z][a-z0-9-]+)", content)
            review_refs.update(refs)

        for ref in review_refs:
            exists = skill_exists(plugins_dir, f"review:{ref}") or agent_exists(plugins_dir, f"review:{ref}")
            assert exists, f"Reference review:{ref} not found as skill or agent"

    def test_testing_skill_references_exist(self, plugins_dir: Path) -> None:
        """All testing:* references should point to existing skills or agents."""
        import re

        testing_refs = set()
        for md_file in plugins_dir.rglob("*.md"):
            content = md_file.read_text()
            refs = re.findall(r"testing:([a-z][a-z0-9-]+)", content)
            testing_refs.update(refs)

        for ref in testing_refs:
            exists = skill_exists(plugins_dir, f"testing:{ref}") or agent_exists(plugins_dir, f"testing:{ref}")
            assert exists, f"Reference testing:{ref} not found as skill or agent"

    def test_meta_skill_references_exist(self, plugins_dir: Path) -> None:
        """All meta:* references should point to existing skills or agents."""
        import re

        meta_refs = set()
        for md_file in plugins_dir.rglob("*.md"):
            content = md_file.read_text()
            refs = re.findall(r"meta:([a-z][a-z0-9-]+)", content)
            meta_refs.update(refs)

        for ref in meta_refs:
            exists = skill_exists(plugins_dir, f"meta:{ref}") or agent_exists(plugins_dir, f"meta:{ref}")
            assert exists, f"Reference meta:{ref} not found as skill or agent"


class TestCurrentState:
    """Tests documenting current state (baseline)."""

    def test_super_plugin_removed(self, plugins_dir: Path) -> None:
        """Super plugin should NOT exist after migration."""
        assert not plugin_exists(plugins_dir, "super"), "super plugin should be removed"

    def test_debug_plugin_exists(self, plugins_dir: Path) -> None:
        """Debug plugin should exist."""
        assert plugin_exists(plugins_dir, "debug")


class TestPhase1TokenEfficiency:
    """Tests for Phase 1: Token efficiency improvements."""

    def test_mermaid_expert_under_100_lines(self, plugins_dir: Path) -> None:
        """Mermaid expert agent should be <100 lines after extraction."""
        agent_path = get_plugin_path(plugins_dir, "doc") / "agents" / "mermaid-expert.md"
        lines = count_lines(agent_path)
        assert lines < 100, f"mermaid-expert.md has {lines} lines, expected <100"

    def test_mermaid_reference_exists(self, plugins_dir: Path) -> None:
        """Mermaid syntax reference file should exist."""
        ref_path = get_plugin_path(plugins_dir, "doc") / "agents" / "references" / "mermaid-syntax.md"
        assert ref_path.exists(), "mermaid-syntax.md reference not found"

    def test_devops_troubleshooter_under_80_lines(self, plugins_dir: Path) -> None:
        """DevOps troubleshooter should be <80 lines after trimming."""
        agent_path = get_plugin_path(plugins_dir, "debug") / "agents" / "devops-troubleshooter.md"
        lines = count_lines(agent_path)
        assert lines < 80, f"devops-troubleshooter.md has {lines} lines, expected <80"

    def test_diagram_generator_under_50_lines(self, plugins_dir: Path) -> None:
        """Diagram generator should delegate to mermaid-expert."""
        agent_path = get_plugin_path(plugins_dir, "doc") / "agents" / "diagram-generator.md"
        lines = count_lines(agent_path)
        assert lines < 50, f"diagram-generator.md has {lines} lines, expected <50"

    def test_diagram_generator_delegates(self, plugins_dir: Path) -> None:
        """Diagram generator should reference mermaid-expert."""
        agent_path = get_plugin_path(plugins_dir, "doc") / "agents" / "diagram-generator.md"
        content = agent_path.read_text()
        assert "mermaid-expert" in content.lower() or "doc:" in content


class TestPhase2Naming:
    """Tests for Phase 2: Naming improvements."""

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


class TestPhase4SplitSuper:
    """Tests for Phase 4: Split super plugin."""

    def test_core_plugin_exists(self, plugins_dir: Path) -> None:
        """Core plugin should exist."""
        assert plugin_exists(plugins_dir, "core")

    def test_core_has_essential_skills(self, plugins_dir: Path) -> None:
        """Core should have essential skills."""
        essential = ["using-core", "verification", "tdd", "brainstorming"]
        for skill in essential:
            assert skill_exists(plugins_dir, f"core:{skill}"), f"core:{skill} not found"

    def test_workflow_plugin_exists(self, plugins_dir: Path) -> None:
        """Workflow plugin should exist."""
        assert plugin_exists(plugins_dir, "workflow")

    def test_workflow_has_planning_skills(self, plugins_dir: Path) -> None:
        """Workflow should have planning skills."""
        planning = ["writing-plans", "executing-plans", "subagent-dev", "git-worktrees", "finish-branch", "parallel-agents"]
        for skill in planning:
            assert skill_exists(plugins_dir, f"workflow:{skill}"), f"workflow:{skill} not found"

    def test_review_plugin_exists(self, plugins_dir: Path) -> None:
        """Review plugin should exist."""
        assert plugin_exists(plugins_dir, "review")

    def test_review_has_code_review_skill(self, plugins_dir: Path) -> None:
        """Review should have merged code-review skill."""
        assert skill_exists(plugins_dir, "review:code-review")

    def test_testing_plugin_exists(self, plugins_dir: Path) -> None:
        """Testing plugin should exist."""
        assert plugin_exists(plugins_dir, "testing")

    def test_testing_has_skills(self, plugins_dir: Path) -> None:
        """Testing should have anti-patterns and condition-wait."""
        skills = ["anti-patterns", "condition-wait"]
        for skill in skills:
            assert skill_exists(plugins_dir, f"testing:{skill}"), f"testing:{skill} not found"

    def test_meta_plugin_exists(self, plugins_dir: Path) -> None:
        """Meta plugin should exist."""
        assert plugin_exists(plugins_dir, "meta")

    def test_meta_has_skills(self, plugins_dir: Path) -> None:
        """Meta should have plugin development skills."""
        skills = ["writing-skills", "testing-skills"]
        for skill in skills:
            assert skill_exists(plugins_dir, f"meta:{skill}"), f"meta:{skill} not found"


class TestPhase5Degradation:
    """Tests for Phase 5: Graceful degradation."""

    def test_python_has_fallback_text(self, plugins_dir: Path) -> None:
        """Python skills should have fallback text for core dependency."""
        python_skill = get_plugin_path(plugins_dir, "python") / "skills" / "python-testing-patterns" / "SKILL.md"
        content = python_skill.read_text()
        # Either has fallback text or doesn't reference core:verification
        has_fallback = "If the `core` plugin is installed" in content
        no_reference = "core:verification" not in content
        assert has_fallback or no_reference, "Python skill references core without fallback"

