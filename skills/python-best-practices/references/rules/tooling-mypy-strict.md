---
title: Enable Strict Mypy Mode
impact: LOW
impactDescription: Maximum type safety
tags: tooling, mypy, type-checking, strict
---

## Enable Strict Mypy Mode

Configure mypy in strict mode for maximum type safety.

**Correct (strict mypy configuration):**

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_ignores = true
show_error_codes = true
enable_error_code = ["ignore-without-code", "truthy-bool"]

[[tool.mypy.overrides]]
module = ["tests.*"]
disallow_untyped_defs = false

[[tool.mypy.overrides]]
module = ["third_party.*"]
ignore_missing_imports = true
```

Run with: `mypy .` or `uv run mypy .`

Reference: [mypy configuration](https://mypy.readthedocs.io/en/stable/config_file.html)
