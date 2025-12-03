#!/usr/bin/env bash
# Detect Python project context from project files
# Outputs version, framework, and package manager for skill awareness

set -euo pipefail

detect_version() {
    # 1. Check .python-version (uv's pin file)
    if [[ -f ".python-version" ]]; then
        cat ".python-version" | head -1 | tr -d '[:space:]'
        return
    fi

    # 2. Check pyproject.toml for requires-python
    if [[ -f "pyproject.toml" ]]; then
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

detect_framework() {
    local frameworks=""

    # Check pyproject.toml dependencies
    if [[ -f "pyproject.toml" ]]; then
        if grep -qiE '^\s*(fastapi|"fastapi)' pyproject.toml 2>/dev/null; then
            frameworks="${frameworks:+$frameworks,}fastapi"
        fi
        if grep -qiE '^\s*(django|"django)' pyproject.toml 2>/dev/null; then
            frameworks="${frameworks:+$frameworks,}django"
        fi
        if grep -qiE '^\s*(flask|"flask)' pyproject.toml 2>/dev/null; then
            frameworks="${frameworks:+$frameworks,}flask"
        fi
        if grep -qiE '^\s*(starlette|"starlette)' pyproject.toml 2>/dev/null; then
            frameworks="${frameworks:+$frameworks,}starlette"
        fi
    fi

    # Check requirements.txt
    if [[ -f "requirements.txt" ]]; then
        if grep -qiE '^fastapi' requirements.txt 2>/dev/null; then
            [[ ! "$frameworks" =~ fastapi ]] && frameworks="${frameworks:+$frameworks,}fastapi"
        fi
        if grep -qiE '^django' requirements.txt 2>/dev/null; then
            [[ ! "$frameworks" =~ django ]] && frameworks="${frameworks:+$frameworks,}django"
        fi
        if grep -qiE '^flask' requirements.txt 2>/dev/null; then
            [[ ! "$frameworks" =~ flask ]] && frameworks="${frameworks:+$frameworks,}flask"
        fi
    fi

    # Check for framework-specific files
    if [[ -f "manage.py" ]] && grep -q "django" manage.py 2>/dev/null; then
        [[ ! "$frameworks" =~ django ]] && frameworks="${frameworks:+$frameworks,}django"
    fi

    if [[ -z "$frameworks" ]]; then
        echo "none"
    else
        echo "$frameworks"
    fi
}

detect_package_manager() {
    # Check in order of preference
    if [[ -f "uv.lock" ]] || [[ -f ".python-version" && -f "pyproject.toml" ]]; then
        echo "uv"
        return
    fi

    if [[ -f "poetry.lock" ]]; then
        echo "poetry"
        return
    fi

    if [[ -f "Pipfile.lock" ]] || [[ -f "Pipfile" ]]; then
        echo "pipenv"
        return
    fi

    if [[ -f "pdm.lock" ]]; then
        echo "pdm"
        return
    fi

    if [[ -f "requirements.txt" ]]; then
        echo "pip"
        return
    fi

    if [[ -f "pyproject.toml" ]]; then
        # Has pyproject but no lock file - could be pip or uv
        echo "pip"
        return
    fi

    echo "unknown"
}

# Detect all context
version=$(detect_version)
framework=$(detect_framework)
package_manager=$(detect_package_manager)

# Output as human-readable summary
echo "Python context detected:"
echo "  Version: ${version}"
echo "  Framework(s): ${framework}"
echo "  Package manager: ${package_manager}"
