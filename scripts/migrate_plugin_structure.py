#!/usr/bin/env python3 -S
"""Migrate plugins to tier-based directory structure.

Reorganizes plugins from flat structure to tier-based domains:
- essential/   : core, commit (Tier 0: Always loaded)
- methodology/ : workflow, review, debug, testing (Tier 1: Workflow patterns)
- domain/      : python, doc, shell (Tier 2: Domain expertise)
- specialized/ : meta, blackbox (Tier 3: Optional/Meta)
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any

# Tier mapping: tier_name -> list of plugin names
TIER_MAPPING: dict[str, list[str]] = {
    "essential": ["core", "commit"],
    "methodology": ["workflow", "review", "debug", "testing"],
    "domain": ["python", "doc", "shell"],
    "specialized": ["meta", "blackbox"],
}


def build_plugin_to_tier_map() -> dict[str, str]:
    """Build reverse mapping: plugin_name -> tier_name."""
    result: dict[str, str] = {}
    for tier, plugins in TIER_MAPPING.items():
        for plugin in plugins:
            result[plugin] = tier
    return result


PLUGIN_TO_TIER = build_plugin_to_tier_map()


def get_new_path(plugin_name: str) -> str:
    """Get new path for a plugin based on tier mapping."""
    tier = PLUGIN_TO_TIER.get(plugin_name)
    if tier:
        return f"plugins/{tier}/{plugin_name}"
    return f"plugins/{plugin_name}"  # Unknown plugin stays at root


def migrate_directories(root_dir: Path, dry_run: bool = True) -> bool:
    """Move plugin directories to tier-based structure.

    Returns True on success, False on error.
    """
    plugins_dir = root_dir / "plugins"
    if not plugins_dir.is_dir():
        print(f"ERROR: Plugins directory not found: {plugins_dir}", file=sys.stderr)
        return False

    # Create tier directories
    for tier in TIER_MAPPING:
        tier_dir = plugins_dir / tier
        if dry_run:
            print(f"  [DRY-RUN] Would create: {tier_dir}")
        else:
            tier_dir.mkdir(exist_ok=True)
            print(f"  Created: {tier_dir}")

    # Move plugins
    for plugin_name, tier in PLUGIN_TO_TIER.items():
        old_path = plugins_dir / plugin_name
        new_path = plugins_dir / tier / plugin_name

        if not old_path.exists():
            print(f"  SKIP: {plugin_name} (not found at {old_path})")
            continue

        if new_path.exists():
            print(f"  SKIP: {plugin_name} (already at {new_path})")
            continue

        if dry_run:
            print(f"  [DRY-RUN] Would move: {old_path.name}/ -> {tier}/{plugin_name}/")
        else:
            shutil.move(str(old_path), str(new_path))
            print(f"  Moved: {old_path.name}/ -> {tier}/{plugin_name}/")

    return True


def update_marketplace(root_dir: Path, dry_run: bool = True) -> bool:
    """Update marketplace.json source paths.

    Returns True on success, False on error.
    """
    marketplace_path = root_dir / ".claude-plugin" / "marketplace.json"

    try:
        marketplace: dict[str, Any] = json.loads(marketplace_path.read_text())
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR: Failed to read marketplace.json: {e}", file=sys.stderr)
        return False

    changes: list[str] = []

    for plugin_entry in marketplace.get("plugins", []):
        name = plugin_entry.get("name")
        old_source = plugin_entry.get("source", "")

        if name in PLUGIN_TO_TIER:
            tier = PLUGIN_TO_TIER[name]
            new_source = f"./plugins/{tier}/{name}"

            if old_source != new_source:
                changes.append(f"  {name}: {old_source} -> {new_source}")
                plugin_entry["source"] = new_source

    if changes:
        if dry_run:
            print("  [DRY-RUN] Would update marketplace.json sources:")
            for change in changes:
                print(change)
        else:
            marketplace_path.write_text(json.dumps(marketplace, indent=2) + "\n")
            print("  Updated marketplace.json sources:")
            for change in changes:
                print(change)
    else:
        print("  No marketplace.json changes needed")

    return True


def update_release_config(root_dir: Path, dry_run: bool = True) -> bool:
    """Update release-please-config.json plugin paths.

    Returns True on success, False on error.
    """
    config_path = root_dir / "release-please-config.json"

    try:
        config: dict[str, Any] = json.loads(config_path.read_text())
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR: Failed to read release-please-config.json: {e}", file=sys.stderr)
        return False

    extra_files = config.get("packages", {}).get(".", {}).get("extra-files", [])
    changes: list[str] = []

    for entry in extra_files:
        if not isinstance(entry, dict):
            continue

        path = entry.get("path", "")

        # Check if this is a plugin.json path
        if path.startswith("plugins/") and "/.claude-plugin/plugin.json" in path:
            # Extract plugin name: plugins/{name}/.claude-plugin/plugin.json
            parts = path.split("/")
            if len(parts) >= 3:
                plugin_name = parts[1]
                if plugin_name in PLUGIN_TO_TIER:
                    tier = PLUGIN_TO_TIER[plugin_name]
                    new_path = f"plugins/{tier}/{plugin_name}/.claude-plugin/plugin.json"
                    if path != new_path:
                        changes.append(f"  {path} -> {new_path}")
                        entry["path"] = new_path

    if changes:
        if dry_run:
            print("  [DRY-RUN] Would update release-please-config.json paths:")
            for change in changes:
                print(change)
        else:
            config_path.write_text(json.dumps(config, indent=2) + "\n")
            print("  Updated release-please-config.json paths:")
            for change in changes:
                print(change)
    else:
        print("  No release-please-config.json changes needed")

    return True


def main() -> int:
    """Main entry point. Returns exit code."""
    # Parse arguments
    dry_run = "--execute" not in sys.argv

    if dry_run:
        print("=" * 60)
        print("DRY RUN MODE - No changes will be made")
        print("Use --execute to apply changes")
        print("=" * 60)

    root_dir = Path(__file__).resolve().parent.parent

    print("\n=== Migration Plan ===")
    print(f"Target structure:")
    for tier, plugins in TIER_MAPPING.items():
        print(f"  {tier}/: {', '.join(plugins)}")

    print("\n=== Step 1: Create tier directories and move plugins ===")
    if not migrate_directories(root_dir, dry_run):
        return 1

    print("\n=== Step 2: Update marketplace.json ===")
    if not update_marketplace(root_dir, dry_run):
        return 1

    print("\n=== Step 3: Update release-please-config.json ===")
    if not update_release_config(root_dir, dry_run):
        return 1

    print("\n=== Migration Complete ===")
    if dry_run:
        print("\nTo apply changes, run:")
        print("  python3 scripts/migrate_plugin_structure.py --execute")
        print("\nAfter migration, update discovery scripts to handle nested structure.")
    else:
        print("\nNext steps:")
        print("  1. Update scripts/validate-plugins.py for nested structure")
        print("  2. Update scripts/update_release_config.py for nested structure")
        print("  3. Run: python3 scripts/validate-plugins.py")
        print("  4. Run: uv run pytest tests/")

    return 0


if __name__ == "__main__":
    sys.exit(main())
