#!/usr/bin/env python3 -S
"""Update release-please-config.json and sync marketplace.json with plugin metadata."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def update_config(root_dir: Path) -> bool:
    """Update release-please-config.json with extra-files for all plugins.

    Returns True on success, False on error.
    """
    config_path = root_dir / "release-please-config.json"
    plugins_dir = root_dir / "plugins"

    # 1. Read existing config
    try:
        config: dict[str, Any] = json.loads(config_path.read_text())
    except FileNotFoundError:
        print(f"ERROR: Config file not found: {config_path}", file=sys.stderr)
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {config_path}: {e}", file=sys.stderr)
        return False

    # 2. Find all plugins
    if not plugins_dir.is_dir():
        print(f"ERROR: Plugins directory not found: {plugins_dir}", file=sys.stderr)
        return False

    plugin_dirs = sorted(d.name for d in plugins_dir.iterdir() if d.is_dir())

    # 3. Prepare extra-files list
    extra_files: list[dict[str, str]] = [
        {
            "type": "json",
            "path": ".claude-plugin/marketplace.json",
            "jsonpath": "$.version",
        }
    ]

    for plugin in plugin_dirs:
        plugin_json_path = f"plugins/{plugin}/.claude-plugin/plugin.json"
        full_path = root_dir / plugin_json_path
        if full_path.exists():
            extra_files.append(
                {"type": "json", "path": plugin_json_path, "jsonpath": "$.version"}
            )
        else:
            print(
                f"Warning: Plugin {plugin} missing plugin.json at {plugin_json_path}",
                file=sys.stderr,
            )

    # 4. Update config
    config["packages"]["."]["extra-files"] = extra_files

    config_path.write_text(json.dumps(config, indent=2) + "\n")

    print(f"Updated {config_path} with {len(extra_files)} entries.")
    return True


# Fields to sync from plugin.json to marketplace.json
SYNC_FIELDS = ("description", "version", "keywords", "license")


def sync_marketplace_plugins(root_dir: Path) -> bool:
    """Sync plugin metadata from plugin.json files to marketplace.json.

    - Auto-discovers new plugins in plugins/ directory
    - Syncs: description, version, keywords, license
    - Preserves: name, source, and any marketplace-only fields

    Returns True on success, False on error.
    """
    marketplace_path = root_dir / ".claude-plugin" / "marketplace.json"
    plugins_dir = root_dir / "plugins"

    # 1. Read existing marketplace.json
    if not marketplace_path.exists():
        return True  # No marketplace.json, nothing to sync

    try:
        marketplace: dict[str, Any] = json.loads(marketplace_path.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {marketplace_path}: {e}", file=sys.stderr)
        return False

    # 2. Build dict of existing marketplace plugins by name
    existing_plugins: dict[str, dict[str, Any]] = {}
    for plugin_entry in marketplace.get("plugins", []):
        name = plugin_entry.get("name")
        if name:
            existing_plugins[name] = plugin_entry

    # 3. Scan plugins directory
    if not plugins_dir.is_dir():
        return True  # No plugins directory, nothing to sync

    updated: list[str] = []
    added: list[str] = []

    for plugin_dir in sorted(plugins_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue

        plugin_name = plugin_dir.name
        plugin_json_path = plugin_dir / ".claude-plugin" / "plugin.json"

        if not plugin_json_path.exists():
            print(
                f"Warning: Plugin {plugin_name} missing plugin.json, skipping",
                file=sys.stderr,
            )
            continue

        # Read plugin.json
        try:
            plugin_data: dict[str, Any] = json.loads(plugin_json_path.read_text())
        except json.JSONDecodeError as e:
            print(
                f"ERROR: Invalid JSON in {plugin_json_path}: {e}",
                file=sys.stderr,
            )
            return False

        # Get or create marketplace entry
        if plugin_name in existing_plugins:
            entry = existing_plugins[plugin_name]
            updated.append(plugin_name)
        else:
            entry = {
                "name": plugin_name,
                "source": f"./plugins/{plugin_name}",
            }
            existing_plugins[plugin_name] = entry
            added.append(plugin_name)

        # Sync fields from plugin.json
        for field in SYNC_FIELDS:
            if field in plugin_data:
                entry[field] = plugin_data[field]

    # 4. Rebuild plugins array sorted by name
    marketplace["plugins"] = [
        existing_plugins[name] for name in sorted(existing_plugins.keys())
    ]

    # 5. Write updated marketplace.json
    marketplace_path.write_text(json.dumps(marketplace, indent=2) + "\n")

    # 6. Print summary
    if updated or added:
        print("Syncing plugin metadata to marketplace.json...")
        if updated:
            print(f"  Updated: {', '.join(updated)} ({len(updated)} plugins)")
        if added:
            print(f"  Added: {', '.join(added)} ({len(added)} new plugins)")

    return True


def sync_version(root_dir: Path) -> bool:
    """Sync version from version.txt to marketplace.json.

    Returns True on success, False on error.
    """
    marketplace_path = root_dir / ".claude-plugin" / "marketplace.json"
    version_file_path = root_dir / "version.txt"

    if not version_file_path.exists():
        return True  # No version file, nothing to sync

    current_version = version_file_path.read_text().strip()

    if not marketplace_path.exists():
        return True  # No marketplace.json, nothing to sync

    try:
        marketplace: dict[str, Any] = json.loads(marketplace_path.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {marketplace_path}: {e}", file=sys.stderr)
        return False

    if marketplace.get("version") != current_version:
        print(
            f"Syncing marketplace.json version from {marketplace.get('version')} to {current_version}"
        )
        marketplace["version"] = current_version
        marketplace_path.write_text(json.dumps(marketplace, indent=2) + "\n")

    return True


def main() -> int:
    """Main entry point. Returns exit code."""
    root_dir = Path(__file__).resolve().parent.parent

    if not sync_marketplace_plugins(root_dir):
        return 1

    if not update_config(root_dir):
        return 1

    if not sync_version(root_dir):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
