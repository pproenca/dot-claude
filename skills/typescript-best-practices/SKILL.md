---
name: typescript-best-practices
description: TypeScript performance and quality optimization guidelines from official TypeScript Handbook and community best practices. This skill should be used when writing, reviewing, or refactoring TypeScript code to ensure optimal patterns. Triggers on tasks involving type safety, TypeScript configuration, API design, error handling, or performance improvements.
allowed-tools: [Read, Edit, Bash, Glob, Grep, WebSearch, WebFetch]
---

# TypeScript Best Practices

## Overview

Comprehensive quality and performance optimization guide for modern TypeScript (5.x) applications, containing 49 rules across 8 categories. Rules are prioritized by impact to guide automated refactoring and code generation. Applies to both Node.js and browser environments.

## When to Apply

Reference these guidelines when:
- Writing new TypeScript code or libraries
- Implementing type-safe APIs
- Working with complex type hierarchies
- Reviewing code for type safety issues
- Refactoring existing TypeScript codebases
- Optimizing compilation performance

## Priority-Ordered Guidelines

Rules are prioritized by impact:

| Priority | Category | Impact |
|----------|----------|--------|
| 1 | Type Safety | CRITICAL |
| 2 | Performance | CRITICAL |
| 3 | Error Handling | HIGH |
| 4 | API Design | MEDIUM-HIGH |
| 5 | Module Organization | MEDIUM |
| 6 | Code Patterns | MEDIUM |
| 7 | Configuration | LOW-MEDIUM |
| 8 | Testing | LOW |

## Quick Reference

### Critical Patterns (Apply First)

**Type Safety:**
- Enable strict mode - catches 40% of production bugs at compile time
- Never use `any` - prefer `unknown` with proper narrowing
- Use discriminated unions for type-safe state management
- Apply `satisfies` operator for inference + validation

**Performance:**
- Enable incremental compilation - 10x faster subsequent builds
- Use project references for monorepos - rebuild only changed packages
- Avoid barrel file re-exports - prevents 30-70% bundle bloat
- Enable `skipLibCheck` - cuts type-check time by 50%

### High-Impact Patterns

- Use Result/Either pattern - makes errors visible in types
- Apply exhaustive checks with `never` - catches missed cases at compile time
- Type error boundaries - distinguish network vs validation vs auth errors

### Medium-Impact Patterns

**API Design:**
- Use branded types for nominal safety (UserId vs OrderId)
- Prefer generics over `any` - preserves type information
- Design APIs for inference - minimize required annotations

**Module Organization:**
- Prefer named exports - enables better refactoring
- Use `import type` - eliminates runtime import overhead

**Code Patterns:**
- Use utility types (`Partial`, `Pick`, `Omit`) over manual definitions
- Apply const assertions for literal type preservation

### Lower-Impact Patterns

**Configuration:**
- Use `moduleResolution: bundler` for modern projects
- Enable `noUncheckedIndexedAccess` for array safety
- Extend from `@tsconfig/bases` for environment defaults

## References

Full documentation with code examples is available in:

- `references/typescript-best-practices-guidelines.md` - Complete guide with all patterns
- `references/rules/` - Individual rule files organized by category

To look up a specific pattern, grep the rules directory:
```
grep -l "strict" references/rules/
grep -l "generics" references/rules/
grep -l "discriminated" references/rules/
```

## Rule Categories in `references/rules/`

- `safety-*` - Type safety and strict mode patterns
- `perf-*` - Runtime performance optimization
- `compile-*` - Compilation speed and project structure
- `error-*` - Error handling patterns
- `api-*` - API design and function signatures
- `module-*` - Module organization and imports
- `pattern-*` - Code patterns and utility types
- `config-*` - tsconfig.json best practices
- `test-*` - Type testing patterns
