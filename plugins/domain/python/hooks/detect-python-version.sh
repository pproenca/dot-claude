#!/usr/bin/env bash
# Detect Python version from project files
# Outputs detected version for skill awareness

set -euo pipefail

detect_version() {
    # 1. Check .python-version (uv's pin file)
    if [[ -f ".python-version" ]]; then
        cat ".python-version" | head -1 | tr -d '[:space:]'
        return
    fi

    # 2. Check pyproject.toml for requires-python
    if [[ -f "pyproject.toml" ]]; then
        # Extract version like ">=3.10" or ">=3.12,<4"
        local version
        version=$(grep -oP 'requires-python\s*=\s*"[><=]*\K[0-9]+\.[0-9]+' pyproject.toml 2>/dev/null | head -1)
        if [[ -n "$version" ]]; then
            echo "$version"
            return
        fi
    fi

    # 3. Check .claude/python-version (our stored preference)
    if [[ -f ".claude/python-version" ]]; then
        cat ".claude/python-version" | head -1 | tr -d '[:space:]'
        return
    fi

    # 4. Check setup.py for python_requires (legacy)
    if [[ -f "setup.py" ]]; then
        local version
        version=$(grep -oP 'python_requires\s*=\s*["\x27][><=]*\K[0-9]+\.[0-9]+' setup.py 2>/dev/null | head -1)
        if [[ -n "$version" ]]; then
            echo "$version"
            return
        fi
    fi

    # 5. Not found
    echo "unknown"
}

version=$(detect_version)

if [[ "$version" != "unknown" ]]; then
    echo "Python version: $version"
else
    echo "Python version: not detected (skills should ask user)"
fi
