#!/usr/bin/env python3
"""
Detect and fix plugin reference mismatches in settings.json files.

This script identifies plugins referenced in ~/.claude/settings.json that
don't actually exist in the project, and offers to fix them automatically.
"""

import json
import sys
from pathlib import Path
from typing import Set, List, Tuple


def get_actual_plugins(project_root: Path) -> Set[str]:
    """Scan project plugins directory and return set of actual plugin IDs."""
    project_plugins = set()
    plugins_dir = project_root / "plugins"

    if not plugins_dir.exists():
        print(f"Warning: {plugins_dir} does not exist")
        return project_plugins

    for plugin_json in plugins_dir.rglob("plugin.json"):
        try:
            with open(plugin_json) as f:
                data = json.load(f)
                name = data.get("name", "")
                marketplace = data.get("marketplace", "dot-claude")
                plugin_id = f"{name}@{marketplace}"
                project_plugins.add(plugin_id)
        except Exception as e:
            print(f"Warning: Error reading {plugin_json}: {e}")

    return project_plugins


def check_settings_file(settings_path: Path, actual_plugins: Set[str]) -> Tuple[List[str], List[str]]:
    """
    Check settings.json for plugin reference mismatches.

    Returns:
        Tuple of (missing_enabled_plugins, missing_skill_permissions)
    """
    if not settings_path.exists():
        return [], []

    with open(settings_path) as f:
        settings = json.load(f)

    # Check enabledPlugins
    enabled_plugins = settings.get("enabledPlugins", {})
    missing_enabled = [
        plugin for plugin, enabled in enabled_plugins.items()
        if enabled and "@dot-claude" in plugin and plugin not in actual_plugins
    ]

    # Check Skill() permissions
    allow_patterns = settings.get("permissions", {}).get("allow", [])
    missing_skills = []
    for pattern in allow_patterns:
        if pattern.startswith("Skill(") and pattern.endswith(")"):
            # Extract plugin prefix: Skill(commit:*) -> commit
            skill_prefix = pattern[6:-3].split(":")[0]  # Remove "Skill(" and ":*)"
            plugin_id = f"{skill_prefix}@dot-claude"
            if plugin_id not in actual_plugins and plugin_id not in ["core@dot-claude"]:
                missing_skills.append(pattern)

    return missing_enabled, missing_skills


def fix_settings_file(settings_path: Path, missing_enabled: List[str], missing_skills: List[str]) -> None:
    """Remove missing plugin references from settings.json."""
    with open(settings_path) as f:
        settings = json.load(f)

    # Remove from enabledPlugins
    if missing_enabled:
        for plugin in missing_enabled:
            del settings["enabledPlugins"][plugin]

    # Remove from permissions.allow
    if missing_skills:
        allow_patterns = settings.get("permissions", {}).get("allow", [])
        settings["permissions"]["allow"] = [
            p for p in allow_patterns if p not in missing_skills
        ]

    # Write back with nice formatting
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")


def main():
    """Main entry point."""
    # Determine project root
    project_root = Path(__file__).parent.parent

    # Get actual plugins
    print("Scanning project plugins...")
    actual_plugins = get_actual_plugins(project_root)
    print(f"Found {len(actual_plugins)} plugins in project")

    # Check home settings.json
    home_settings = Path.home() / ".claude" / "settings.json"
    print(f"\nChecking {home_settings}...")

    missing_enabled, missing_skills = check_settings_file(home_settings, actual_plugins)

    if not missing_enabled and not missing_skills:
        print("✓ No plugin reference errors found")
        return 0

    # Report errors
    print("\n✗ PLUGIN REFERENCE ERRORS FOUND:\n")

    if missing_enabled:
        print("Missing plugins in enabledPlugins:")
        for plugin in missing_enabled:
            print(f"  - {plugin}")

    if missing_skills:
        print("\nMissing plugins in permissions.allow Skill() patterns:")
        for pattern in missing_skills:
            print(f"  - {pattern}")

    # Ask to fix
    print("\nWould you like to fix these automatically? (y/n): ", end="")
    response = input().strip().lower()

    if response == "y":
        fix_settings_file(home_settings, missing_enabled, missing_skills)
        print(f"\n✓ Fixed {home_settings}")
        print("Removed:")
        for plugin in missing_enabled:
            print(f"  - {plugin} from enabledPlugins")
        for pattern in missing_skills:
            print(f"  - {pattern} from permissions.allow")
        return 0
    else:
        print("\nNo changes made. To fix manually, edit ~/.claude/settings.json")
        return 1


if __name__ == "__main__":
    sys.exit(main())
