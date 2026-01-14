---
name: python-best-practices
description: Python 3.11-3.14 performance optimization guidelines from Official Python Docs and Community Best Practices. This skill should be used when writing, reviewing, or refactoring Python code to ensure optimal patterns. Triggers on tasks involving type annotations, asyncio, dataclasses, pattern matching, memory optimization, or performance improvements.
---

# Python 3.11-3.14 Best Practices

## Overview

Comprehensive performance optimization guide for modern Python applications (3.11-3.14), containing 43+ rules across 8 categories. Rules are prioritized by impact to guide automated refactoring and code generation.

## When to Apply

Reference these guidelines when:
- Writing new Python modules, classes, or functions
- Implementing async/await patterns and concurrency
- Reviewing code for type safety and performance issues
- Refactoring existing Python code to modern standards
- Optimizing memory usage and execution speed

## Priority-Ordered Guidelines

Rules are prioritized by impact:

| Priority | Category | Impact |
|----------|----------|--------|
| 1 | Modern Type Annotations | CRITICAL |
| 2 | Async & Concurrency Patterns | CRITICAL |
| 3 | Memory & Performance Optimization | HIGH |
| 4 | Modern Python Idioms (3.11-3.14) | MEDIUM-HIGH |
| 5 | Error Handling & Exceptions | MEDIUM |
| 6 | Data Structures & Classes | MEDIUM |
| 7 | Security & Safety Patterns | LOW-MEDIUM |
| 8 | Tooling & Configuration | LOW |

## Quick Reference

### Critical Patterns (Apply First)

**Modern Type Annotations:**
- Use `int | str` union syntax instead of `Union[int, str]`
- Use `str | None` instead of `Optional[str]`
- Use PEP 695 type parameter syntax (`def func[T](x: T) -> T`)
- Use built-in generics (`list[str]`) instead of `List[str]`
- Use `type` statement for aliases instead of `TypeAlias`

**Async & Concurrency Patterns:**
- Use `asyncio.TaskGroup` for structured concurrency
- Use `asyncio.timeout()` instead of `asyncio.wait_for()`
- Handle task cancellation with `try/except CancelledError`
- Use `asyncio.Queue.shutdown()` for graceful termination
- Avoid blocking calls in async functions

### High-Impact Performance Patterns

- Use `__slots__` for memory-efficient classes with many instances
- Use generators for large datasets instead of list comprehensions
- Cache expensive computations with `functools.cache`
- Use local variable caching in performance-critical loops

### Medium-Impact Modern Idioms

- Use `match`/`case` for complex conditionals
- Use f-string `=` specifier for debugging (`f"{var=}"`)
- Use `tomllib` for TOML parsing (stdlib in 3.11+)

### Error Handling Patterns

- Use `ExceptionGroup` and `except*` for multiple exceptions
- Always chain exceptions with `raise ... from`
- Use context managers for resource cleanup
- Create custom exceptions inheriting from appropriate base
- Use `Self` type for fluent interface methods
- Leverage improved error messages in 3.11+

### Data Structure Patterns

- Use `@dataclass(slots=True)` for memory-efficient dataclasses
- Use `TypedDict` for typed dictionary schemas
- Use `NamedTuple` over plain tuples for clarity
- Prefer `Enum` with `auto()` for enumerated constants
- Use `@dataclass(frozen=True)` for immutable data
- Use `copy.replace()` for dataclass updates (3.13+)
- Use `field(default_factory=...)` for mutable defaults

### Security Patterns

- Never use `eval()`/`exec()`/`pickle` with untrusted data
- Use `secrets` module instead of `random` for cryptographic operations
- Use parameterized queries to prevent SQL injection
- Validate file paths with `Path.is_relative_to()` to prevent traversal
- Store secrets in environment variables, use `pydantic-settings` for validation

### Tooling Patterns

- Use `pyproject.toml` as single configuration source
- Configure ruff for linting and formatting
- Enable strict mode in mypy configuration

## References

Full documentation with code examples is available in:

- `references/python-performance-guidelines.md` - Complete guide with all patterns
- `references/rules/` - Individual rule files organized by category

To look up a specific pattern, grep the rules directory:
```
grep -l "asyncio" references/rules/
grep -l "dataclass" references/rules/
grep -l "typing" references/rules/
```

## Rule Categories in `references/rules/`

- `typing-*` - Modern type annotation patterns
- `async-*` - Async/await and concurrency optimization
- `perf-*` - Memory and performance patterns
- `modern-*` - Python 3.11-3.14 idioms
- `error-*` - Exception handling patterns
- `data-*` - Data structure patterns
- `security-*` - Security and safety patterns
- `tooling-*` - Project configuration patterns
