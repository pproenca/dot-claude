# Advanced Packaging Patterns

## Table of Contents
- [Pattern 11: Including Data Files](#pattern-11-including-data-files)
- [Pattern 12: Namespace Packages](#pattern-12-namespace-packages)
- [Pattern 13: C Extensions](#pattern-13-c-extensions)
- [Pattern 14: Semantic Versioning](#pattern-14-semantic-versioning)
- [Pattern 15: Git-Based Versioning](#pattern-15-git-based-versioning)
- [Pattern 19: Multi-Architecture Wheels](#pattern-19-multi-architecture-wheels)
- [Pattern 20: Private Package Index](#pattern-20-private-package-index)

## Pattern 11: Including Data Files

```toml
[tool.setuptools.package-data]
my_package = [
    "data/*.json",
    "templates/*.html",
    "static/css/*.css",
    "py.typed",
]
```

**Accessing data files:**
```python
# src/my_package/loader.py
from importlib.resources import files
import json

def load_config():
    config_file = files("my_package").joinpath("data/config.json")
    with config_file.open() as f:
        return json.load(f)

# Python 3.9+
from importlib.resources import files

data = files("my_package").joinpath("data/file.txt").read_text()
```

## Pattern 12: Namespace Packages

**For large projects split across multiple repositories:**

```
# Package 1: company-core
company/
└── core/
    ├── __init__.py
    └── models.py

# Package 2: company-api
company/
└── api/
    ├── __init__.py
    └── routes.py
```

**Do NOT include __init__.py in the namespace directory (company/):**

```toml
# company-core/pyproject.toml
[project]
name = "company-core"

[tool.setuptools.packages.find]
where = ["."]
include = ["company.core*"]

# company-api/pyproject.toml
[project]
name = "company-api"

[tool.setuptools.packages.find]
where = ["."]
include = ["company.api*"]
```

**Usage:**
```python
# Both packages can be imported under same namespace
from company.core import models
from company.api import routes
```

## Pattern 13: C Extensions

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel", "Cython>=0.29"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
ext-modules = [
    {name = "my_package.fast_module", sources = ["src/fast_module.c"]},
]
```

**Or with setup.py:**
```python
# setup.py
from setuptools import setup, Extension

setup(
    ext_modules=[
        Extension(
            "my_package.fast_module",
            sources=["src/fast_module.c"],
            include_dirs=["src/include"],
        )
    ]
)
```

## Pattern 14: Semantic Versioning

```python
# src/my_package/__init__.py
__version__ = "1.2.3"

# Semantic versioning: MAJOR.MINOR.PATCH
# MAJOR: Breaking changes
# MINOR: New features (backward compatible)
# PATCH: Bug fixes
```

**Version constraints in dependencies:**
```toml
dependencies = [
    "requests>=2.28.0,<3.0.0",  # Compatible range
    "click~=8.1.0",              # Compatible release (~= 8.1.0 means >=8.1.0,<8.2.0)
    "pydantic>=2.0",             # Minimum version
    "numpy==1.24.3",             # Exact version (avoid if possible)
]
```

## Pattern 15: Git-Based Versioning

```toml
[build-system]
requires = ["setuptools>=61.0", "setuptools-scm>=8.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my-package"
dynamic = ["version"]

[tool.setuptools_scm]
write_to = "src/my_package/_version.py"
version_scheme = "post-release"
local_scheme = "dirty-tag"
```

**Creates versions like:**
- `1.0.0` (from git tag)
- `1.0.1.dev3+g1234567` (3 commits after tag)

## Pattern 19: Multi-Architecture Wheels

```yaml
# .github/workflows/wheels.yml
name: Build wheels

on: [push, pull_request]

jobs:
  build_wheels:
    name: Build wheels on ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]

    steps:
      - uses: actions/checkout@v3

      - name: Build wheels
        uses: pypa/cibuildwheel@v2.16.2

      - uses: actions/upload-artifact@v3
        with:
          path: ./wheelhouse/*.whl
```

## Pattern 20: Private Package Index

```bash
# Install from private index
pip install my-package --index-url https://private.pypi.org/simple/

# Or add to pip.conf
[global]
index-url = https://private.pypi.org/simple/
extra-index-url = https://pypi.org/simple/

# Upload to private index
twine upload --repository-url https://private.pypi.org/ dist/*
```
