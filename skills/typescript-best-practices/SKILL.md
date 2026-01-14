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
- Enable strict mode in all projects
- Never use `any` - prefer `unknown` or proper typing
- Use type narrowing with type guards
- Leverage discriminated unions for type-safe branching
- Use `satisfies` operator for type validation
- Avoid type assertions (`as`) - narrow instead

**Performance:**
- Use `const` enums for zero-runtime overhead
- Avoid excessive type complexity (recursive types)
- Use project references for large codebases
- Leverage incremental compilation
- Avoid barrel file re-exports in applications
- Enable `skipLibCheck` for faster builds
- Configure include/exclude properly

### High-Impact Patterns

- Use Result/Either pattern over exceptions
- Type your error boundaries properly
- Use `never` for exhaustive error handling
- Avoid swallowing errors with empty catch blocks

### Medium-Impact Patterns

**API Design:**
- Use function overloads for complex signatures
- Prefer generics over `any` for reusable code
- Use branded types for nominal typing
- Design APIs with inference in mind

**Module Organization:**
- Prefer named exports over default exports
- Use type-only imports where applicable
- Avoid circular dependencies
- Reserve barrel files for library entry points only

**Code Patterns:**
- Use discriminated unions over type assertions
- Leverage exhaustive checks with `never`
- Use utility types (`Partial`, `Pick`, `Omit`, etc.)
- Use template literal types for string patterns

### Lower-Impact Patterns

**Configuration:**
- Use `moduleResolution: bundler` for modern projects
- Enable `noUncheckedIndexedAccess` for array safety
- Configure paths for clean imports
- Enable `exactOptionalPropertyTypes` for stricter optionals
- Extend from `@tsconfig/bases` for environment defaults

**Testing:**
- Use `expectTypeOf` for compile-time type tests
- Mock with proper type narrowing

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
