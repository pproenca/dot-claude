# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. Modern Type Annotations (typing)

**Impact:** CRITICAL
**Description:** Modern Python 3.11-3.14 type annotation patterns for type safety and code clarity using PEP 695 syntax.

## 2. Async & Concurrency Patterns (async)

**Impact:** CRITICAL
**Description:** Asyncio best practices for concurrent Python applications using TaskGroup, proper cancellation, and structured concurrency.

## 3. Memory & Performance Optimization (perf)

**Impact:** HIGH
**Description:** Memory-efficient patterns including __slots__, generators, and caching strategies for high-performance Python.

## 4. Modern Python Idioms (modern)

**Impact:** MEDIUM-HIGH
**Description:** New language features in Python 3.11-3.14 including pattern matching, f-string improvements, and stdlib additions.

## 5. Error Handling & Exceptions (error)

**Impact:** MEDIUM
**Description:** Exception handling patterns including exception groups, proper chaining, and context managers.

## 6. Data Structures & Classes (data)

**Impact:** MEDIUM
**Description:** Modern data structure patterns using dataclasses, TypedDict, NamedTuple, and Enum best practices.

## 7. Security & Safety Patterns (security)

**Impact:** LOW-MEDIUM
**Description:** Security best practices including avoiding eval/exec, safe deserialization, and input validation.

## 8. Tooling & Configuration (tooling)

**Impact:** LOW
**Description:** Modern Python project configuration with pyproject.toml, uv, ruff, and mypy integration.
