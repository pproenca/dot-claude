#!/usr/bin/env python3 -S
"""
Validates Claude Code settings.json files across all locations.

Performs validation checks:
  1. JSON syntax validation
  2. Permission pattern validation (Bash(*), Skill(*) references)
  3. Tool/skill reference integrity
  4. Command executability (statusLine commands)
  5. Permission conflict detection (same tool in allow and ask)
"""

from __future__ import annotations

import json
import platform
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

# Tier mapping for nested plugin structure (from conftest.py)
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

# Known Claude Code tools
KNOWN_TOOLS = {
    "Bash", "Read", "Write", "Edit", "Glob", "Grep",
    "Task", "Skill", "SlashCommand", "TodoWrite",
    "AskUserQuestion", "WebFetch", "WebSearch",
    "BashOutput", "KillShell", "NotebookEdit", "EnterPlanMode", "ExitPlanMode"
}


def err(msg: str) -> None:
    """Print error message to stderr."""
    print(f"ERROR: {msg}", file=sys.stderr)


def warn(msg: str) -> None:
    """Print warning message to stderr."""
    print(f"WARNING: {msg}", file=sys.stderr)


def get_plugin_path(plugins_dir: Path, plugin_name: str) -> Path:
    """Get the path to a plugin, handling tier structure."""
    tier = PLUGIN_TO_TIER.get(plugin_name)
    if tier:
        return plugins_dir / tier / plugin_name
    # Fallback: check if exists at top level
    return plugins_dir / plugin_name


def discover_valid_skills(repo_root: Path) -> set[str]:
    """Discover all valid skills in the repository.

    Returns set of qualified names like 'commit:new', 'core:tdd'.
    """
    skills: set[str] = set()
    plugins_dir = repo_root / "plugins"

    if not plugins_dir.exists():
        return skills

    for skill_md in plugins_dir.rglob("**/SKILL.md"):
        # Parse YAML frontmatter for skill name
        content = skill_md.read_text()
        if content.startswith("---"):
            try:
                _, frontmatter, _ = content.split("---", 2)
                # Simple YAML parsing for name field only
                for line in frontmatter.strip().split("\n"):
                    if line.startswith("name:"):
                        skill_name = line.split(":", 1)[1].strip()
                        # Find the plugin name from the path
                        parts = skill_md.relative_to(plugins_dir).parts
                        if "skills" in parts:
                            skills_idx = parts.index("skills")
                            if skills_idx > 0:
                                plugin_name = parts[skills_idx - 1]
                                qualified_name = f"{plugin_name}:{skill_name}"
                                skills.add(qualified_name)
                        break
            except ValueError:
                continue

    return skills


def discover_valid_plugins(repo_root: Path) -> set[str]:
    """Discover all valid plugins in the repository.

    Returns set of plugin names like 'commit', 'core', 'workflow'.
    """
    plugins: set[str] = set()
    plugins_dir = repo_root / "plugins"

    if not plugins_dir.exists():
        return plugins

    # Check nested tier structure
    for tier_or_plugin in plugins_dir.iterdir():
        if not tier_or_plugin.is_dir():
            continue

        # Check if this is a direct plugin
        if (tier_or_plugin / ".claude-plugin" / "plugin.json").exists():
            plugins.add(tier_or_plugin.name)
        else:
            # This might be a tier directory, check subdirectories
            for plugin_dir in tier_or_plugin.iterdir():
                if plugin_dir.is_dir() and (plugin_dir / ".claude-plugin" / "plugin.json").exists():
                    plugins.add(plugin_dir.name)

    return plugins


def discover_valid_references(repo_root: Path) -> dict[str, set[str]]:
    """Build registry of all valid skills, plugins, tools.

    This is built once and reused for O(1) validation lookups.
    """
    return {
        'skills': discover_valid_skills(repo_root),
        'plugins': discover_valid_plugins(repo_root),
        'tools': KNOWN_TOOLS,
    }


def validate_json_syntax(path: Path) -> list[str]:
    """Check JSON parsing (fast-path: exit early if invalid)."""
    errors = []
    try:
        with open(path) as f:
            json.load(f)
    except FileNotFoundError:
        # Not an error - file may not exist at all locations
        pass
    except json.JSONDecodeError as e:
        errors.append(f"{path}: Invalid JSON syntax: {e}")
    except Exception as e:
        errors.append(f"{path}: Failed to read file: {e}")

    return errors


def extract_permission_pattern(pattern: str) -> tuple[str, str] | None:
    """Extract tool name and reference from permission pattern.

    Examples:
      'Bash(git:*)' -> ('Bash', 'git')
      'Skill(commit:*)' -> ('Skill', 'commit')
      'Read' -> ('Read', '')
      'Invalid(...)' -> None
    """
    # Match: Tool(reference:*) or Tool(reference) or Tool
    match = re.match(r'^(\w+)(?:\(([^:)]+)(?::[^)]+)?\))?$', pattern)
    if match:
        tool, ref = match.groups()
        return (tool, ref or '')
    return None


def validate_permission_patterns(
    settings: dict[str, Any],
    registry: dict[str, set[str]],
    path: Path
) -> list[str]:
    """Validate Bash(*), Skill(*) pattern references."""
    errors = []
    permissions = settings.get("permissions", {})

    for permission_type in ["allow", "deny", "ask"]:
        patterns = permissions.get(permission_type, [])
        if not isinstance(patterns, list):
            errors.append(f"{path}: permissions.{permission_type} must be a list")
            continue

        for pattern in patterns:
            if not isinstance(pattern, str):
                errors.append(f"{path}: permission pattern must be string: {pattern}")
                continue

            parsed = extract_permission_pattern(pattern)
            if not parsed:
                errors.append(f"{path}: invalid permission pattern: {pattern}")
                continue

            tool, ref = parsed

            # Validate tool name (O(1) lookup)
            if tool not in registry['tools']:
                errors.append(f"{path}: unknown tool in pattern '{pattern}': {tool}")

            # Validate Skill references
            if tool == "Skill" and ref:
                # ref should be either "plugin:skill" or "plugin:*"
                if ":" not in ref:
                    # Simple plugin reference like Skill(commit)
                    if ref not in registry['plugins']:
                        errors.append(f"{path}: Skill pattern references unknown plugin: {pattern}")
                elif ref.endswith(":*"):
                    plugin = ref[:-2]  # Remove ":*"
                    if plugin not in registry['plugins']:
                        errors.append(f"{path}: Skill pattern references unknown plugin: {pattern}")
                else:
                    if ref not in registry['skills']:
                        errors.append(f"{path}: Skill pattern references unknown skill: {pattern}")

    return errors


def validate_command_executability(
    settings: dict[str, Any],
    path: Path,
    working_dir: Path
) -> list[str]:
    """Test statusLine command executability (timeout=5s)."""
    errors = []
    status_line = settings.get("statusLine", {})

    if not status_line:
        return errors  # No statusLine configured, skip

    if not isinstance(status_line, dict):
        errors.append(f"{path}: statusLine must be an object")
        return errors

    command_type = status_line.get("type")
    command = status_line.get("command")

    if command_type != "command" or not command:
        return errors  # Not a command type or no command specified

    # Test command executability with timeout
    try:
        # Parse command using shlex for proper shell parsing
        cmd_parts = shlex.split(command)
        if not cmd_parts:
            errors.append(f"{path}: statusLine command is empty")
            return errors

        # Run with short timeout to test executability
        result = subprocess.run(
            cmd_parts,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=5
        )
        # We don't care about exit code, just that it's executable
        if result.returncode != 0:
            warn(f"{path}: statusLine command exited with code {result.returncode}")
    except FileNotFoundError:
        errors.append(f"{path}: statusLine command not found: {cmd_parts[0]}")
    except subprocess.TimeoutExpired:
        warn(f"{path}: statusLine command timed out (>5s), may be slow")
    except Exception as e:
        errors.append(f"{path}: statusLine command failed: {e}")

    return errors


def detect_permission_conflicts(
    settings: dict[str, Any],
    path: Path
) -> list[str]:
    """Find tools in both allow and ask lists."""
    errors = []
    permissions = settings.get("permissions", {})

    allow_patterns = set(permissions.get("allow", []))
    ask_patterns = set(permissions.get("ask", []))
    deny_patterns = set(permissions.get("deny", []))

    # Check for exact duplicates between allow and ask
    conflicts_allow_ask = allow_patterns & ask_patterns
    if conflicts_allow_ask:
        for pattern in conflicts_allow_ask:
            errors.append(f"{path}: permission conflict - pattern in both allow and ask: {pattern}")

    # Check for exact duplicates between allow and deny
    conflicts_allow_deny = allow_patterns & deny_patterns
    if conflicts_allow_deny:
        for pattern in conflicts_allow_deny:
            errors.append(f"{path}: permission conflict - pattern in both allow and deny: {pattern}")

    # Check for exact duplicates between ask and deny
    conflicts_ask_deny = ask_patterns & deny_patterns
    if conflicts_ask_deny:
        for pattern in conflicts_ask_deny:
            errors.append(f"{path}: permission conflict - pattern in both ask and deny: {pattern}")

    return errors


def validate_settings_file(
    path: Path,
    registry: dict[str, set[str]],
    working_dir: Path
) -> tuple[bool, list[str], list[str]]:
    """Validate single settings file.

    Returns (success, errors, warnings).
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Fast-path: Check JSON syntax first
    syntax_errors = validate_json_syntax(path)
    if syntax_errors:
        errors.extend(syntax_errors)
        return (False, errors, warnings)  # Exit early on parse failure

    # File doesn't exist - not an error
    if not path.exists():
        return (True, [], [])

    # Load settings for further validation
    try:
        with open(path) as f:
            settings = json.load(f)
    except Exception as e:
        errors.append(f"{path}: Failed to load settings: {e}")
        return (False, errors, warnings)

    # Validate permission patterns
    errors.extend(validate_permission_patterns(settings, registry, path))

    # Validate command executability
    errors.extend(validate_command_executability(settings, path, working_dir))

    # Detect permission conflicts
    errors.extend(detect_permission_conflicts(settings, path))

    return (len(errors) == 0, errors, warnings)


def get_settings_locations() -> list[tuple[str, Path, Path]]:
    """Get all settings.json locations to validate.

    Returns list of (label, path, working_dir) tuples.
    """
    locations: list[tuple[str, Path, Path]] = []

    # User global settings
    home = Path.home()
    locations.append(("Global", home / ".claude" / "settings.json", home / ".claude"))

    # Project shared settings
    cwd = Path.cwd()
    locations.append(("Project", cwd / ".claude" / "settings.json", cwd / ".claude"))

    # Project local settings
    locations.append(("Project Local", cwd / ".claude" / "settings.local.json", cwd / ".claude"))

    # Enterprise managed settings (platform-specific)
    system = platform.system()
    if system == "Darwin":
        enterprise_path = Path("/Library/Application Support/ClaudeCode/managed-settings.json")
        enterprise_dir = Path("/Library/Application Support/ClaudeCode")
    elif system == "Windows":
        enterprise_path = Path("C:/ProgramData/ClaudeCode/managed-settings.json")
        enterprise_dir = Path("C:/ProgramData/ClaudeCode")
    else:  # Linux/WSL
        enterprise_path = Path("/etc/claude-code/managed-settings.json")
        enterprise_dir = Path("/etc/claude-code")

    locations.append(("Enterprise", enterprise_path, enterprise_dir))

    return locations


def main() -> int:
    """Main entry point. Returns exit code."""
    # Setup paths
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent

    print("Discovering valid skills and plugins...")
    registry = discover_valid_references(repo_root)

    print(f"Found {len(registry['skills'])} skills across {len(registry['plugins'])} plugins")
    print("")

    # Get all settings.json locations
    locations = get_settings_locations()

    all_valid = True
    validated_count = 0

    for label, path, working_dir in locations:
        if not path.exists():
            continue  # Skip non-existent files (not an error)

        print(f"Validating {label}: {path}")
        validated_count += 1

        success, errors, warnings = validate_settings_file(path, registry, working_dir)

        if not success:
            all_valid = False
            for error in errors:
                print(f"  ✗ {error}", file=sys.stderr)
        else:
            print("  ✓ Valid")

        for warning in warnings:
            print(f"  ⚠ {warning}", file=sys.stderr)

    print("")
    if validated_count == 0:
        print("No settings.json files found to validate")
        return 0
    elif all_valid:
        print(f"All {validated_count} settings.json files passed validation")
        return 0
    else:
        print("Some settings.json files have validation errors")
        return 1


if __name__ == "__main__":
    sys.exit(main())
