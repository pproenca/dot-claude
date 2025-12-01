#!/usr/bin/env python3
"""Tests for update_release_config.py script.

TDD: Tests written first to verify sync_marketplace_plugins behavior.
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest

# Load module
SCRIPTS_DIR = os.path.dirname(__file__)
MODULE_PATH = os.path.join(SCRIPTS_DIR, "update_release_config.py")


def load_update_release_config():
    """Load the update_release_config.py module."""
    spec = importlib.util.spec_from_file_location("update_release_config", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["update_release_config"] = module
    spec.loader.exec_module(module)
    return module


class TestSyncMarketplacePlugins(unittest.TestCase):
    """Tests for sync_marketplace_plugins function."""

    def setUp(self):
        """Create temp directory with test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

        # Create marketplace.json
        self.marketplace_dir = os.path.join(self.temp_dir, ".claude-plugin")
        os.makedirs(self.marketplace_dir)
        self.marketplace_path = os.path.join(
            self.marketplace_dir, "marketplace.json"
        )

        # Create plugins directory
        self.plugins_dir = os.path.join(self.temp_dir, "plugins")
        os.makedirs(self.plugins_dir)

        # Create release-please-config.json (required by update_config)
        self.release_config = {
            "packages": {".": {"extra-files": []}}
        }
        release_config_path = os.path.join(
            self.temp_dir, "release-please-config.json"
        )
        with open(release_config_path, "w") as f:
            json.dump(self.release_config, f)

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)
        # Clean up module cache
        if "update_release_config" in sys.modules:
            del sys.modules["update_release_config"]

    def _create_plugin(
        self,
        name: str,
        description: str = "Test plugin",
        version: str = "1.0.0",
        keywords: list[str] | None = None,
        license_: str = "MIT",
    ):
        """Helper to create a plugin with plugin.json."""
        plugin_dir = os.path.join(self.plugins_dir, name, ".claude-plugin")
        os.makedirs(plugin_dir)
        plugin_json = {
            "name": name,
            "version": version,
            "description": description,
            "license": license_,
        }
        if keywords:
            plugin_json["keywords"] = keywords
        with open(os.path.join(plugin_dir, "plugin.json"), "w") as f:
            json.dump(plugin_json, f)

    def _create_marketplace(self, plugins: list[dict]):
        """Helper to create marketplace.json."""
        marketplace = {
            "name": "test-marketplace",
            "owner": {"name": "Test"},
            "plugins": plugins,
            "version": "1.0.0",
        }
        with open(self.marketplace_path, "w") as f:
            json.dump(marketplace, f)

    def test_syncs_description_from_plugin_json(self):
        """Test that description is synced from plugin.json to marketplace."""
        # Create plugin with specific description
        self._create_plugin("test-plugin", description="New description from plugin")

        # Create marketplace with outdated description
        self._create_marketplace([
            {"name": "test-plugin", "source": "./plugins/test-plugin", "description": "Old description"}
        ])

        # Import and run
        update_release_config = load_update_release_config()
        from pathlib import Path

        result = update_release_config.sync_marketplace_plugins(Path(self.temp_dir))
        self.assertTrue(result)

        # Verify description was updated
        with open(self.marketplace_path) as f:
            marketplace = json.load(f)

        plugin_entry = marketplace["plugins"][0]
        self.assertEqual(plugin_entry["description"], "New description from plugin")

    def test_syncs_version_from_plugin_json(self):
        """Test that version is synced from plugin.json to marketplace."""
        self._create_plugin("test-plugin", version="2.5.0")
        self._create_marketplace([
            {"name": "test-plugin", "source": "./plugins/test-plugin"}
        ])

        update_release_config = load_update_release_config()
        from pathlib import Path

        result = update_release_config.sync_marketplace_plugins(Path(self.temp_dir))
        self.assertTrue(result)

        with open(self.marketplace_path) as f:
            marketplace = json.load(f)

        plugin_entry = marketplace["plugins"][0]
        self.assertEqual(plugin_entry["version"], "2.5.0")

    def test_syncs_keywords_from_plugin_json(self):
        """Test that keywords are synced from plugin.json to marketplace."""
        self._create_plugin("test-plugin", keywords=["testing", "automation"])
        self._create_marketplace([
            {"name": "test-plugin", "source": "./plugins/test-plugin"}
        ])

        update_release_config = load_update_release_config()
        from pathlib import Path

        result = update_release_config.sync_marketplace_plugins(Path(self.temp_dir))
        self.assertTrue(result)

        with open(self.marketplace_path) as f:
            marketplace = json.load(f)

        plugin_entry = marketplace["plugins"][0]
        self.assertEqual(plugin_entry["keywords"], ["testing", "automation"])

    def test_syncs_license_from_plugin_json(self):
        """Test that license is synced from plugin.json to marketplace."""
        self._create_plugin("test-plugin", license_="Apache-2.0")
        self._create_marketplace([
            {"name": "test-plugin", "source": "./plugins/test-plugin"}
        ])

        update_release_config = load_update_release_config()
        from pathlib import Path

        result = update_release_config.sync_marketplace_plugins(Path(self.temp_dir))
        self.assertTrue(result)

        with open(self.marketplace_path) as f:
            marketplace = json.load(f)

        plugin_entry = marketplace["plugins"][0]
        self.assertEqual(plugin_entry["license"], "Apache-2.0")

    def test_auto_discovers_new_plugins(self):
        """Test that new plugins in plugins/ are added to marketplace."""
        # Create plugin that's not in marketplace
        self._create_plugin("new-plugin", description="A brand new plugin")

        # Create marketplace without the new plugin
        self._create_marketplace([])

        update_release_config = load_update_release_config()
        from pathlib import Path

        result = update_release_config.sync_marketplace_plugins(Path(self.temp_dir))
        self.assertTrue(result)

        with open(self.marketplace_path) as f:
            marketplace = json.load(f)

        # Should have auto-discovered the new plugin
        self.assertEqual(len(marketplace["plugins"]), 1)
        plugin_entry = marketplace["plugins"][0]
        self.assertEqual(plugin_entry["name"], "new-plugin")
        self.assertEqual(plugin_entry["source"], "./plugins/new-plugin")
        self.assertEqual(plugin_entry["description"], "A brand new plugin")

    def test_preserves_name_and_source(self):
        """Test that name and source fields are preserved, not overwritten."""
        self._create_plugin("test-plugin")
        self._create_marketplace([
            {"name": "test-plugin", "source": "./plugins/test-plugin", "custom_field": "preserved"}
        ])

        update_release_config = load_update_release_config()
        from pathlib import Path

        result = update_release_config.sync_marketplace_plugins(Path(self.temp_dir))
        self.assertTrue(result)

        with open(self.marketplace_path) as f:
            marketplace = json.load(f)

        plugin_entry = marketplace["plugins"][0]
        self.assertEqual(plugin_entry["name"], "test-plugin")
        self.assertEqual(plugin_entry["source"], "./plugins/test-plugin")
        # Custom fields should be preserved
        self.assertEqual(plugin_entry["custom_field"], "preserved")

    def test_sorts_plugins_by_name(self):
        """Test that plugins are sorted alphabetically by name."""
        self._create_plugin("zebra-plugin")
        self._create_plugin("alpha-plugin")
        self._create_plugin("middle-plugin")

        # Create marketplace in non-alphabetical order
        self._create_marketplace([
            {"name": "zebra-plugin", "source": "./plugins/zebra-plugin"},
            {"name": "alpha-plugin", "source": "./plugins/alpha-plugin"},
            {"name": "middle-plugin", "source": "./plugins/middle-plugin"},
        ])

        update_release_config = load_update_release_config()
        from pathlib import Path

        result = update_release_config.sync_marketplace_plugins(Path(self.temp_dir))
        self.assertTrue(result)

        with open(self.marketplace_path) as f:
            marketplace = json.load(f)

        plugin_names = [p["name"] for p in marketplace["plugins"]]
        self.assertEqual(plugin_names, ["alpha-plugin", "middle-plugin", "zebra-plugin"])

    def test_handles_missing_plugin_json(self):
        """Test that plugins without plugin.json are warned but not fatal."""
        # Create plugin directory without plugin.json
        plugin_dir = os.path.join(self.plugins_dir, "incomplete-plugin")
        os.makedirs(plugin_dir)

        # Create a complete plugin
        self._create_plugin("complete-plugin")

        self._create_marketplace([])

        update_release_config = load_update_release_config()
        from pathlib import Path

        # Should succeed, just warn about incomplete plugin
        result = update_release_config.sync_marketplace_plugins(Path(self.temp_dir))
        self.assertTrue(result)

        with open(self.marketplace_path) as f:
            marketplace = json.load(f)

        # Only the complete plugin should be added
        self.assertEqual(len(marketplace["plugins"]), 1)
        self.assertEqual(marketplace["plugins"][0]["name"], "complete-plugin")

    def test_handles_missing_fields_in_plugin_json(self):
        """Test that missing fields in plugin.json don't cause errors."""
        # Create plugin with minimal plugin.json (only name)
        plugin_dir = os.path.join(self.plugins_dir, "minimal-plugin", ".claude-plugin")
        os.makedirs(plugin_dir)
        with open(os.path.join(plugin_dir, "plugin.json"), "w") as f:
            json.dump({"name": "minimal-plugin"}, f)

        self._create_marketplace([])

        update_release_config = load_update_release_config()
        from pathlib import Path

        result = update_release_config.sync_marketplace_plugins(Path(self.temp_dir))
        self.assertTrue(result)

        with open(self.marketplace_path) as f:
            marketplace = json.load(f)

        # Plugin should be added with available fields
        self.assertEqual(len(marketplace["plugins"]), 1)
        self.assertEqual(marketplace["plugins"][0]["name"], "minimal-plugin")
        # Missing fields should not be present (not None or empty)
        self.assertNotIn("description", marketplace["plugins"][0])


class TestUpdateConfig(unittest.TestCase):
    """Tests for update_config function."""

    def setUp(self):
        """Create temp directory with test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

        # Create marketplace.json
        self.marketplace_dir = os.path.join(self.temp_dir, ".claude-plugin")
        os.makedirs(self.marketplace_dir)
        marketplace = {
            "name": "test-marketplace",
            "version": "1.0.0",
            "metadata": {"version": "1.0.0"},
            "plugins": [],
        }
        with open(os.path.join(self.marketplace_dir, "marketplace.json"), "w") as f:
            json.dump(marketplace, f)

        # Create plugins directory
        self.plugins_dir = os.path.join(self.temp_dir, "plugins")
        os.makedirs(self.plugins_dir)

        # Create release-please-config.json
        self.release_config_path = os.path.join(
            self.temp_dir, "release-please-config.json"
        )
        with open(self.release_config_path, "w") as f:
            json.dump({"packages": {".": {"extra-files": []}}}, f)

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)
        if "update_release_config" in sys.modules:
            del sys.modules["update_release_config"]

    def _create_plugin(self, name: str):
        """Helper to create a plugin with plugin.json."""
        plugin_dir = os.path.join(self.plugins_dir, name, ".claude-plugin")
        os.makedirs(plugin_dir)
        with open(os.path.join(plugin_dir, "plugin.json"), "w") as f:
            json.dump({"name": name, "version": "1.0.0"}, f)

    def test_generates_metadata_version_entry(self):
        """Test that $.metadata.version entry is generated."""
        self._create_plugin("test-plugin")

        update_release_config = load_update_release_config()
        from pathlib import Path

        result = update_release_config.update_config(Path(self.temp_dir))
        self.assertTrue(result)

        with open(self.release_config_path) as f:
            config = json.load(f)

        extra_files = config["packages"]["."]["extra-files"]
        jsonpaths = [e["jsonpath"] for e in extra_files]

        self.assertIn("$.metadata.version", jsonpaths)

    def test_generates_plugin_version_entries_in_marketplace(self):
        """Test that $.plugins[N].version entries are generated for each plugin."""
        self._create_plugin("alpha-plugin")
        self._create_plugin("beta-plugin")
        self._create_plugin("gamma-plugin")

        update_release_config = load_update_release_config()
        from pathlib import Path

        result = update_release_config.update_config(Path(self.temp_dir))
        self.assertTrue(result)

        with open(self.release_config_path) as f:
            config = json.load(f)

        extra_files = config["packages"]["."]["extra-files"]
        marketplace_entries = [
            e for e in extra_files
            if e["path"] == ".claude-plugin/marketplace.json"
        ]
        jsonpaths = [e["jsonpath"] for e in marketplace_entries]

        # Should have: $.metadata.version, $.plugins[0-2].version (no root $.version)
        self.assertNotIn("$.version", jsonpaths)
        self.assertIn("$.metadata.version", jsonpaths)
        self.assertIn("$.plugins[0].version", jsonpaths)
        self.assertIn("$.plugins[1].version", jsonpaths)
        self.assertIn("$.plugins[2].version", jsonpaths)

    def test_plugin_indices_match_sorted_order(self):
        """Test that plugin indices in marketplace match alphabetical order."""
        # Create in non-alphabetical order
        self._create_plugin("zebra")
        self._create_plugin("alpha")

        update_release_config = load_update_release_config()
        from pathlib import Path

        result = update_release_config.update_config(Path(self.temp_dir))
        self.assertTrue(result)

        with open(self.release_config_path) as f:
            config = json.load(f)

        extra_files = config["packages"]["."]["extra-files"]

        # Find plugin.json entries - should be in sorted order
        plugin_json_entries = [
            e for e in extra_files
            if e["path"].startswith("plugins/") and e["path"].endswith("plugin.json")
        ]
        plugin_paths = [e["path"] for e in plugin_json_entries]

        # Should be sorted alphabetically
        self.assertEqual(
            plugin_paths,
            [
                "plugins/alpha/.claude-plugin/plugin.json",
                "plugins/zebra/.claude-plugin/plugin.json",
            ]
        )


if __name__ == "__main__":
    unittest.main()
