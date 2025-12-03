#!/usr/bin/env python3 -S
"""
Validates cross-references in Claude Code plugins.

Catches regressions like:
  1. Template references pointing to non-existent files
  2. Stale plugin prefixes (super: instead of workflow:)
  3. Skill/agent references that don't exist
  4. Orphaned templates (files nothing references)

Run: python3 scripts/validate-references.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import NamedTuple


class ValidationError(NamedTuple):
    file: Path
    line_num: int
    message: str
    severity: str  # "error" or "warning"


def err(msg: str) -> None:
    """Print error message to stderr."""
    print(f"ERROR: {msg}", file=sys.stderr)


def warn(msg: str) -> None:
    """Print warning message to stderr."""
    print(f"WARNING: {msg}", file=sys.stderr)


def find_all_markdown_files(plugins_dir: Path) -> list[Path]:
    """Find all markdown files in plugins directory."""
    return list(plugins_dir.rglob("*.md"))


def find_all_skill_names(plugins_dir: Path) -> set[str]:
    """Find all valid skill names (plugin:skill-name format)."""
    skills: set[str] = set()

    for skill_file in plugins_dir.rglob("skills/*/SKILL.md"):
        # Parse the skill name from frontmatter
        content = skill_file.read_text()
        match = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
        if match:
            skill_name = match.group(1).strip()

            # Determine plugin name from path
            # Path like: plugins/methodology/workflow/skills/foo/SKILL.md
            parts = skill_file.relative_to(plugins_dir).parts
            if len(parts) >= 2:
                # Could be plugins/tier/plugin/... or plugins/plugin/...
                plugin_dir = skill_file.parent.parent.parent
                plugin_json = plugin_dir / ".claude-plugin" / "plugin.json"
                if plugin_json.exists():
                    import json
                    plugin_data = json.loads(plugin_json.read_text())
                    plugin_name = plugin_data.get("name", plugin_dir.name)
                    skills.add(f"{plugin_name}:{skill_name}")

    return skills


def find_all_agent_names(plugins_dir: Path) -> set[str]:
    """Find all valid agent names (plugin:agent-name format)."""
    agents: set[str] = set()

    for agent_file in plugins_dir.rglob("agents/*.md"):
        # Parse the agent name from frontmatter
        content = agent_file.read_text()
        match = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
        if match:
            agent_name = match.group(1).strip()

            # Determine plugin name from path
            plugin_dir = agent_file.parent.parent
            plugin_json = plugin_dir / ".claude-plugin" / "plugin.json"
            if plugin_json.exists():
                import json
                plugin_data = json.loads(plugin_json.read_text())
                plugin_name = plugin_data.get("name", plugin_dir.name)
                agents.add(f"{plugin_name}:{agent_name}")

    return agents


def check_template_references(
    file_path: Path, content: str, repo_root: Path
) -> list[ValidationError]:
    """Check that template file references point to existing files."""
    errors: list[ValidationError] = []

    # Patterns for template references
    patterns = [
        r"[Tt]emplate at [`'\"]?([^`'\">\n]+\.md)[`'\"]?",
        r"[Ss]ee template at [`'\"]?([^`'\">\n]+\.md)[`'\"]?",
        r"[Uu]se template at [`'\"]?([^`'\">\n]+\.md)[`'\"]?",
    ]

    for line_num, line in enumerate(content.split("\n"), 1):
        for pattern in patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                # Resolve path - could be relative or from repo root
                template_path = match.strip()

                # Try as absolute from repo root
                full_path = repo_root / template_path
                if not full_path.exists():
                    # Try relative to file's directory
                    full_path = file_path.parent / template_path
                    if not full_path.exists():
                        errors.append(ValidationError(
                            file=file_path,
                            line_num=line_num,
                            message=f"Template reference to non-existent file: {template_path}",
                            severity="error"
                        ))

    return errors


def check_stale_prefixes(
    file_path: Path, content: str
) -> list[ValidationError]:
    """Check for stale plugin prefixes like 'super:'."""
    errors: list[ValidationError] = []

    # Known stale prefixes that should have been migrated
    stale_patterns = [
        (r"\bsuper:", "super:", "workflow:, review:, or core:"),
    ]

    for line_num, line in enumerate(content.split("\n"), 1):
        for pattern, old_prefix, new_suggestion in stale_patterns:
            if re.search(pattern, line):
                errors.append(ValidationError(
                    file=file_path,
                    line_num=line_num,
                    message=f"Stale prefix '{old_prefix}' found. Should be '{new_suggestion}'",
                    severity="error"
                ))

    return errors


def check_skill_references(
    file_path: Path, content: str, valid_skills: set[str]
) -> list[ValidationError]:
    """Check that skill references point to existing skills."""
    errors: list[ValidationError] = []

    # Patterns for skill references
    patterns = [
        r"Use (?:Skill tool|skill)[:\s]+[`'\"]?(\w+:\w[\w-]*)[`'\"]?",
        r"REQUIRED SUB-SKILL[:\s]+Use [`'\"]?(\w+:\w[\w-]*)[`'\"]?",
        r"\*\*(\w+:\w[\w-]*)\*\*\s*-\s*\*\*REQUIRED",
    ]

    for line_num, line in enumerate(content.split("\n"), 1):
        for pattern in patterns:
            matches = re.findall(pattern, line, re.IGNORECASE)
            for match in matches:
                skill_ref = match.strip()
                if skill_ref not in valid_skills:
                    # Check if it's a valid prefix at least
                    prefix = skill_ref.split(":")[0] if ":" in skill_ref else ""
                    if prefix not in ["python", "doc", "meta", "debug", "shell"]:
                        # These are external/optional plugins, only warn
                        errors.append(ValidationError(
                            file=file_path,
                            line_num=line_num,
                            message=f"Skill reference may not exist: {skill_ref}",
                            severity="warning"
                        ))

    return errors


def check_agent_references(
    file_path: Path, content: str, valid_agents: set[str]
) -> list[ValidationError]:
    """Check that agent references in Task tool calls are valid."""
    errors: list[ValidationError] = []

    # Pattern for Task tool agent references
    patterns = [
        r"Task tool \((\w+:\w[\w-]*)\)",
        r"subagent_type[=:]\s*['\"]?(\w+:\w[\w-]*)['\"]?",
    ]

    for line_num, line in enumerate(content.split("\n"), 1):
        for pattern in patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                agent_ref = match.strip()
                # general-purpose is a built-in, skip
                if agent_ref == "general-purpose":
                    continue
                if agent_ref not in valid_agents:
                    errors.append(ValidationError(
                        file=file_path,
                        line_num=line_num,
                        message=f"Agent reference may not exist: {agent_ref}",
                        severity="warning"
                    ))

    return errors


def find_orphaned_templates(
    plugins_dir: Path, all_files: list[Path]
) -> list[ValidationError]:
    """Find template files that nothing references."""
    errors: list[ValidationError] = []

    # Find all templates directories
    template_files: set[Path] = set()
    for template_dir in plugins_dir.rglob("templates"):
        if template_dir.is_dir():
            for f in template_dir.glob("*.md"):
                template_files.add(f)

    if not template_files:
        return errors

    # Build set of all content
    all_content = ""
    for f in all_files:
        try:
            all_content += f.read_text() + "\n"
        except Exception:
            pass

    # Check if each template is referenced
    for template in template_files:
        # Check by filename
        if template.name not in all_content:
            errors.append(ValidationError(
                file=template,
                line_num=0,
                message=f"Template file appears to be orphaned (not referenced anywhere)",
                severity="warning"
            ))

    return errors


def check_required_sections(
    file_path: Path, content: str
) -> list[ValidationError]:
    """Check that critical skills have required sections."""
    errors: list[ValidationError] = []

    # Define required sections for specific skills
    required_sections: dict[str, list[str]] = {
        "code-review": [
            "Gracefully Correcting",
            "Push Back",
            "Forbidden Responses",
        ],
        "executing-plans": [
            "Code Review After Batch",
            "When to Stop",
            "Verify Isolation",
        ],
        "subagent-dev": [
            "Review Subagent",
            "Apply Review Feedback",
            "Final Review",
        ],
        "writing-plans": [
            "Bite-Sized",
            "Execution Handoff",
            "Task Structure",
        ],
    }

    # Determine skill name from frontmatter
    match = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
    if not match:
        return errors

    skill_name = match.group(1).strip()

    if skill_name in required_sections:
        for section in required_sections[skill_name]:
            if section.lower() not in content.lower():
                errors.append(ValidationError(
                    file=file_path,
                    line_num=0,
                    message=f"Skill '{skill_name}' missing required section: '{section}'",
                    severity="error"
                ))

    return errors


def main() -> int:
    """Main entry point."""
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    plugins_dir = repo_root / "plugins"

    if not plugins_dir.exists():
        err("plugins/ directory not found")
        return 1

    print("Validating plugin cross-references...\n")

    # Collect valid names
    valid_skills = find_all_skill_names(plugins_dir)
    valid_agents = find_all_agent_names(plugins_dir)

    print(f"Found {len(valid_skills)} skills, {len(valid_agents)} agents\n")

    # Find all markdown files
    all_files = find_all_markdown_files(plugins_dir)

    all_errors: list[ValidationError] = []

    # Run checks on each file
    for file_path in all_files:
        try:
            content = file_path.read_text()
        except Exception as e:
            err(f"Could not read {file_path}: {e}")
            continue

        all_errors.extend(check_template_references(file_path, content, repo_root))
        all_errors.extend(check_stale_prefixes(file_path, content))
        all_errors.extend(check_skill_references(file_path, content, valid_skills))
        all_errors.extend(check_agent_references(file_path, content, valid_agents))
        all_errors.extend(check_required_sections(file_path, content))

    # Check for orphaned templates
    all_errors.extend(find_orphaned_templates(plugins_dir, all_files))

    # Report results
    errors = [e for e in all_errors if e.severity == "error"]
    warnings = [e for e in all_errors if e.severity == "warning"]

    if warnings:
        print("Warnings:")
        for w in warnings:
            relative_path = w.file.relative_to(repo_root)
            if w.line_num:
                print(f"  {relative_path}:{w.line_num}: {w.message}")
            else:
                print(f"  {relative_path}: {w.message}")
        print()

    if errors:
        print("Errors:")
        for e in errors:
            relative_path = e.file.relative_to(repo_root)
            if e.line_num:
                print(f"  {relative_path}:{e.line_num}: {e.message}")
            else:
                print(f"  {relative_path}: {e.message}")
        print()
        print(f"Found {len(errors)} errors, {len(warnings)} warnings")
        return 1

    print(f"All reference checks passed ({len(warnings)} warnings)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
