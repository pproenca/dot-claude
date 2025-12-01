#!/usr/bin/env python3 -S
"""
Validates Claude Code plugins in the repository.

Performs validation checks:
  1. Repository root validation via claude CLI
  2. marketplace.json references existing directories
  3. All plugin directories are listed in marketplace.json
  4. Release config consistency
  5. Individual plugin validation via claude CLI
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def run_command(command: list[str], cwd: Path | str | None = None) -> bool:
    """Runs a shell command and returns True if successful."""
    try:
        subprocess.run(command, cwd=cwd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        print(f"ERROR: Command not found: {command[0]}", file=sys.stderr)
        return False


def err(msg: str) -> None:
    """Print error message to stderr."""
    print(f"ERROR: {msg}", file=sys.stderr)


def validate_marketplace(repo_root: Path) -> bool:
    """Validate the repository root marketplace configuration."""
    print("Validating marketplace...")
    return run_command(["claude", "plugin", "validate", str(repo_root)])


def validate_marketplace_references(
    repo_root: Path, marketplace_data: dict[str, Any]
) -> bool:
    """Validate that marketplace.json plugin references exist on disk."""
    print("\nValidating marketplace.json plugin references...")
    has_error = False

    for plugin_entry in marketplace_data.get("plugins", []):
        source = plugin_entry.get("source", "")
        if not source:
            continue

        # Remove leading ./ if present
        clean_source = source.removeprefix("./")

        plugin_path = repo_root / clean_source
        if not plugin_path.is_dir():
            err(f"marketplace.json references non-existent plugin: {source}")
            has_error = True

    return not has_error


def validate_all_plugins_listed(
    repo_root: Path, marketplace_data: dict[str, Any]
) -> bool:
    """Validate all plugin directories are listed in marketplace.json."""
    print("Validating all plugin directories are listed...")
    has_error = False
    plugins_dir = repo_root / "plugins"

    # Get sources from marketplace.json
    marketplace_sources: set[str] = set()
    for plugin_entry in marketplace_data.get("plugins", []):
        source = plugin_entry.get("source")
        if source:
            marketplace_sources.add(source.removeprefix("./"))

    # Check file system
    if plugins_dir.is_dir():
        for item in plugins_dir.iterdir():
            if item.is_dir():
                relative_path = f"plugins/{item.name}"
                # O(1) lookup in set
                if relative_path not in marketplace_sources:
                    err(
                        f"Plugin directory not listed in marketplace.json: {relative_path}"
                    )
                    has_error = True

    return not has_error


def validate_release_config_consistency(
    repo_root: Path, marketplace_data: dict[str, Any]
) -> bool:
    """Validate release-please-config.json includes all plugins."""
    print("Validating release-please-config.json consistency...")
    has_error = False
    release_config_path = repo_root / "release-please-config.json"

    try:
        release_config: dict[str, Any] = json.loads(release_config_path.read_text())
    except FileNotFoundError:
        err("release-please-config.json not found")
        return False
    except json.JSONDecodeError:
        err("release-please-config.json is invalid JSON")
        return False

    # Build a set of configured paths for O(1) lookup
    configured_paths: set[str] = set()

    # Traverse config structure: packages -> . -> extra-files
    try:
        extra_files = (
            release_config.get("packages", {}).get(".", {}).get("extra-files", [])
        )
        for file_entry in extra_files:
            if isinstance(file_entry, dict):
                path = file_entry.get("path")
                if path:
                    configured_paths.add(path)
    except AttributeError:
        err("release-please-config.json has invalid structure")
        return False

    for plugin_entry in marketplace_data.get("plugins", []):
        source = plugin_entry.get("source", "")
        if not source:
            continue

        source = source.removeprefix("./")

        plugin_json_path = f"{source}/.claude-plugin/plugin.json"

        # O(1) lookup
        if plugin_json_path not in configured_paths:
            err(f"Plugin missing from release-please-config.json: {source}")
            has_error = True

    return not has_error


def validate_individual_plugins(repo_root: Path) -> bool:
    """Validate each individual plugin directory."""
    print("\nValidating plugins...")
    has_error = False
    plugins_dir = repo_root / "plugins"

    if plugins_dir.is_dir():
        for item in plugins_dir.iterdir():
            if item.is_dir():
                if not run_command(["claude", "plugin", "validate", str(item)]):
                    has_error = True

    return not has_error


def main() -> int:
    """Main entry point. Returns exit code."""
    # Setup paths
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    marketplace_json_path = repo_root / ".claude-plugin" / "marketplace.json"

    # Load marketplace.json
    try:
        marketplace_data: dict[str, Any] = json.loads(marketplace_json_path.read_text())
    except (FileNotFoundError, json.JSONDecodeError) as e:
        err(f"Failed to load marketplace.json: {e}")
        return 1

    failed = False

    if not validate_marketplace(repo_root):
        failed = True

    if not validate_marketplace_references(repo_root, marketplace_data):
        failed = True

    if not validate_all_plugins_listed(repo_root, marketplace_data):
        failed = True

    if not validate_release_config_consistency(repo_root, marketplace_data):
        failed = True

    if not validate_individual_plugins(repo_root):
        failed = True

    print("")
    if not failed:
        print("All validations passed")
        return 0
    else:
        print("Some validations failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())