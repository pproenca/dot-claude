#!/bin/bash
set -euo pipefail

# Detect Python version from project configuration
# Priority: .python-version > pyproject.toml > .claude/python-version > setup.py

detect_python_version() {
    local version=""

    # 1. Check .python-version (uv's pin file)
    if [[ -f ".python-version" ]]; then
        version=$(cat ".python-version" | tr -d '[:space:]')
        if [[ -n "$version" ]]; then
            echo "Python version: $version (from .python-version)"
            return 0
        fi
    fi

    # 2. Check pyproject.toml requires-python
    if [[ -f "pyproject.toml" ]]; then
        version=$(grep -E "^requires-python\s*=" pyproject.toml 2>/dev/null | \
            sed -E 's/.*">=([0-9]+\.[0-9]+).*/\1/' | \
            head -1 | tr -d '[:space:]')
        if [[ -n "$version" && "$version" != *"requires"* ]]; then
            echo "Python version: $version (from pyproject.toml)"
            return 0
        fi
    fi

    # 3. Check .claude/python-version (stored preference)
    if [[ -f ".claude/python-version" ]]; then
        version=$(cat ".claude/python-version" | tr -d '[:space:]')
        if [[ -n "$version" ]]; then
            echo "Python version: $version (from .claude/python-version)"
            return 0
        fi
    fi

    # 4. Check setup.py python_requires (legacy)
    if [[ -f "setup.py" ]]; then
        version=$(grep -E "python_requires\s*=" setup.py 2>/dev/null | \
            sed -E "s/.*['\"]>=([0-9]+\.[0-9]+).*/\1/" | \
            head -1 | tr -d '[:space:]')
        if [[ -n "$version" && "$version" != *"python_requires"* ]]; then
            echo "Python version: $version (from setup.py)"
            return 0
        fi
    fi

    # No version found
    echo "Python version: unknown"
    echo "Tip: Skills should prompt user for Python version and store in .claude/python-version"
    return 0
}

# Run detection
detect_python_version
