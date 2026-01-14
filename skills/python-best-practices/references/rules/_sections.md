# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. Modern Type Annotations (typing)

**Impact:** CRITICAL
**Description:** Modern type syntax reduces annotation boilerplate by 50% and eliminates 5+ import statements per file. Catches 3-5 type errors per 1000 LoC at development time with mypy/pyright.

## 2. Async & Concurrency Patterns (async)

**Impact:** CRITICAL
**Description:** Prevents event loop blocking that causes 100% CPU lockups and missed deadlines. TaskGroup eliminates manual task cleanup code and guarantees proper exception propagation.

## 3. Memory & Performance Optimization (perf)

**Impact:** HIGH
**Description:** __slots__ reduces memory by 30-50% per instance (150 bytes to 40 bytes). Generators process 10GB+ files with constant memory instead of loading entire datasets.

## 4. Modern Python Idioms (modern)

**Impact:** MEDIUM-HIGH
**Description:** Pattern matching replaces 10-20 line if/elif chains with 5-8 line match statements. F-string debug specifier saves 50% typing in debug statements.

## 5. Error Handling & Exceptions (error)

**Impact:** MEDIUM
**Description:** Exception groups capture all concurrent errors instead of losing all but the first. Proper chaining preserves full tracebacks for debugging.

## 6. Data Structures & Classes (data)

**Impact:** MEDIUM
**Description:** @dataclass(slots=True) combines 30-50% memory savings with zero-boilerplate class definitions. TypedDict adds type checking to dictionary schemas without runtime overhead.

## 7. Security & Safety Patterns (security)

**Impact:** LOW-MEDIUM
**Description:** Prevents code injection (eval/exec), arbitrary code execution (pickle), and SQL injection. Each vulnerability class affects ~15% of Python applications.

## 8. Tooling & Configuration (tooling)

**Impact:** LOW
**Description:** Modern Python project configuration with pyproject.toml, uv, ruff, and mypy integration.
