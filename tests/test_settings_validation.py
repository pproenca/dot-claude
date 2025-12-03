"""Tests for settings.json validation script."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to Python path for imports
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))


def test_validate_settings_script_exists():
    """Test that validate-settings.py script exists and is executable."""
    script_path = Path(__file__).parent.parent / "scripts" / "validate-settings.py"
    assert script_path.exists(), "validate-settings.py script not found"
    assert script_path.stat().st_mode & 0o111, "validate-settings.py not executable"


def test_validate_settings_script_runs():
    """Test that validate-settings.py script runs without errors."""
    script_path = Path(__file__).parent.parent / "scripts" / "validate-settings.py"

    # Run the script (it should complete successfully)
    result = subprocess.run(
        ["uv", "run", "python", str(script_path)],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO_ROOT
    )

    # Should exit with 0 (valid settings found)
    assert result.returncode == 0

    # Should produce output mentioning validation
    assert "Discovering valid skills" in result.stdout
    assert "passed validation" in result.stdout.lower()


def test_valid_settings_json_structure():
    """Test that valid settings.json has correct structure."""
    settings_path = REPO_ROOT / ".claude" / "settings.json"

    if not settings_path.exists():
        pytest.skip("Project settings.json not found")

    with open(settings_path) as f:
        settings = json.load(f)

    # Should have permissions section
    assert "permissions" in settings
    assert isinstance(settings["permissions"], dict)

    # Permissions should have allow, ask, or deny arrays
    for key in ["allow", "ask", "deny"]:
        if key in settings["permissions"]:
            assert isinstance(settings["permissions"][key], list)


def test_invalid_json_syntax_detected():
    """Test that invalid JSON syntax is detected."""
    invalid_json = '{"foo": "bar", }'  # Trailing comma is invalid

    with tempfile.TemporaryDirectory() as tmpdir:
        settings_path = Path(tmpdir) / "settings.json"
        settings_path.write_text(invalid_json)

        with pytest.raises(json.JSONDecodeError):
            json.loads(settings_path.read_text())


def test_permission_patterns_have_valid_format():
    """Test that permission patterns follow expected format."""
    settings_path = REPO_ROOT / ".claude" / "settings.json"

    if not settings_path.exists():
        pytest.skip("Project settings.json not found")

    with open(settings_path) as f:
        settings = json.load(f)

    permissions = settings.get("permissions", {})

    # Check all permission patterns
    for permission_type in ["allow", "ask", "deny"]:
        patterns = permissions.get(permission_type, [])
        for pattern in patterns:
            # Should be a string
            assert isinstance(pattern, str), f"Pattern must be string: {pattern}"
            # Should have basic structure
            assert len(pattern) > 0, "Pattern must not be empty"


def test_script_discovers_skills():
    """Test that script discovers skills from the repository."""
    script_path = REPO_ROOT / "scripts" / "validate-settings.py"

    result = subprocess.run(
        ["uv", "run", "python", str(script_path)],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO_ROOT
    )

    # Should mention discovered skills
    assert "Found" in result.stdout
    assert "skills" in result.stdout
    assert "plugins" in result.stdout


def test_script_validates_multiple_locations():
    """Test that script checks multiple settings.json locations."""
    script_path = REPO_ROOT / "scripts" / "validate-settings.py"

    result = subprocess.run(
        ["uv", "run", "python", str(script_path)],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO_ROOT
    )

    # Should validate at least one location
    assert "Validating" in result.stdout
    # Should show validation results
    assert ("✓ Valid" in result.stdout or "passed validation" in result.stdout.lower())


def test_tier_mapping_exists():
    """Test that tier mapping is defined in the script."""
    script_path = REPO_ROOT / "scripts" / "validate-settings.py"
    script_content = script_path.read_text()

    # Should have TIER_MAPPING defined
    assert "TIER_MAPPING" in script_content
    assert "essential" in script_content
    assert "methodology" in script_content
    assert "domain" in script_content
    assert "specialized" in script_content


def test_known_tools_defined():
    """Test that known tools are defined in the script."""
    script_path = REPO_ROOT / "scripts" / "validate-settings.py"
    script_content = script_path.read_text()

    # Should have KNOWN_TOOLS defined
    assert "KNOWN_TOOLS" in script_content

    # Should include core tools
    assert "Bash" in script_content
    assert "Read" in script_content
    assert "Write" in script_content
    assert "Skill" in script_content


def test_validation_functions_defined():
    """Test that validation functions are defined in the script."""
    script_path = REPO_ROOT / "scripts" / "validate-settings.py"
    script_content = script_path.read_text()

    # Should have key validation functions
    assert "discover_valid_skills" in script_content
    assert "discover_valid_plugins" in script_content
    assert "validate_permission_patterns" in script_content
    assert "detect_permission_conflicts" in script_content
    assert "validate_command_executability" in script_content


@pytest.fixture
def repo_root():
    """Return the repository root directory."""
    return Path(__file__).parent.parent
