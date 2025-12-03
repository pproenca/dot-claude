"""Tests for scripts/fix-plugin-references.py"""

import importlib.util
import json
import tempfile
from pathlib import Path


def _load_module():
    """Load the fix-plugin-references.py script as a module."""
    script_path = Path(__file__).parent.parent / "scripts" / "fix-plugin-references.py"
    spec = importlib.util.spec_from_file_location("fix_plugin_references", script_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fix_plugin_references = _load_module()
get_actual_plugins = fix_plugin_references.get_actual_plugins
check_settings_file = fix_plugin_references.check_settings_file
fix_settings_file = fix_plugin_references.fix_settings_file


def test_get_actual_plugins():
    """Test scanning for actual plugins in project."""
    project_root = Path(__file__).parent.parent
    plugins = get_actual_plugins(project_root)

    # Should find the actual plugins
    assert "core@dot-claude" in plugins
    assert "commit@dot-claude" in plugins
    assert "workflow@dot-claude" in plugins

    # Should not find removed plugins
    assert "super@dot-claude" not in plugins
    assert "dev@dot-claude" not in plugins
    assert "agent@dot-claude" not in plugins


def test_check_settings_file_with_errors():
    """Test detecting plugin reference errors in settings.json."""
    # Create a temp settings file with errors
    settings_data = {
        "enabledPlugins": {
            "core@dot-claude": True,
            "super@dot-claude": True,  # This doesn't exist
            "dev@dot-claude": True,  # This doesn't exist
        },
        "permissions": {
            "allow": [
                "Skill(core:*)",
                "Skill(super:*)",  # This doesn't exist
                "Skill(dev:*)",  # This doesn't exist
            ]
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(settings_data, f)
        temp_path = Path(f.name)

    try:
        # Get actual plugins
        project_root = Path(__file__).parent.parent
        actual_plugins = get_actual_plugins(project_root)

        # Check for errors
        missing_enabled, missing_skills = check_settings_file(temp_path, actual_plugins)

        # Should detect missing plugins
        assert "super@dot-claude" in missing_enabled
        assert "dev@dot-claude" in missing_enabled
        assert "Skill(super:*)" in missing_skills
        assert "Skill(dev:*)" in missing_skills

        # Should not flag existing plugins
        assert "core@dot-claude" not in missing_enabled
        assert "Skill(core:*)" not in missing_skills

    finally:
        temp_path.unlink()


def test_fix_settings_file():
    """Test fixing plugin reference errors."""
    # Create a temp settings file with errors
    settings_data = {
        "enabledPlugins": {
            "core@dot-claude": True,
            "super@dot-claude": True,
        },
        "permissions": {"allow": ["Skill(core:*)", "Skill(super:*)"]},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(settings_data, f)
        temp_path = Path(f.name)

    try:
        # Fix the file
        fix_settings_file(
            temp_path,
            missing_enabled=["super@dot-claude"],
            missing_skills=["Skill(super:*)"],
        )

        # Read back and verify
        with open(temp_path) as f:
            fixed_data = json.load(f)

        # super@dot-claude should be removed
        assert "super@dot-claude" not in fixed_data["enabledPlugins"]
        assert "Skill(super:*)" not in fixed_data["permissions"]["allow"]

        # core@dot-claude should remain
        assert fixed_data["enabledPlugins"]["core@dot-claude"] is True
        assert "Skill(core:*)" in fixed_data["permissions"]["allow"]

    finally:
        temp_path.unlink()


def test_check_settings_no_errors():
    """Test that valid settings pass without errors."""
    # Create a temp settings file without errors
    settings_data = {
        "enabledPlugins": {
            "core@dot-claude": True,
            "commit@dot-claude": True,
        },
        "permissions": {"allow": ["Skill(core:*)", "Skill(commit:*)"]},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(settings_data, f)
        temp_path = Path(f.name)

    try:
        # Get actual plugins
        project_root = Path(__file__).parent.parent
        actual_plugins = get_actual_plugins(project_root)

        # Check for errors
        missing_enabled, missing_skills = check_settings_file(temp_path, actual_plugins)

        # Should have no errors
        assert len(missing_enabled) == 0
        assert len(missing_skills) == 0

    finally:
        temp_path.unlink()
