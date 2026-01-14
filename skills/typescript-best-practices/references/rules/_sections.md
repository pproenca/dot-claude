# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. Type Safety (safety)

**Impact:** CRITICAL
**Description:** Type safety is TypeScript's core value proposition. Proper typing catches bugs at compile time, enables better IDE support, and serves as documentation. Strict mode and avoiding `any` eliminate entire classes of runtime errors.

## 2. Performance (perf)

**Impact:** CRITICAL
**Description:** TypeScript compilation performance affects developer productivity. Runtime performance depends on avoiding unnecessary abstractions. Proper project structure and incremental compilation are essential for large codebases.

## 3. Error Handling (error)

**Impact:** HIGH
**Description:** Proper error handling in TypeScript goes beyond try/catch. Result types, typed errors, and exhaustive handling patterns make error states explicit and prevent silent failures.

## 4. API Design (api)

**Impact:** MEDIUM-HIGH
**Description:** Well-designed TypeScript APIs leverage the type system for better developer experience. Function overloads, generics, and branded types create self-documenting, type-safe interfaces.

## 5. Module Organization (module)

**Impact:** MEDIUM
**Description:** Module structure affects both compilation speed and code maintainability. Proper import/export patterns, avoiding barrel files in libraries, and type-only imports reduce bundle size and improve tree-shaking.

## 6. Code Patterns (pattern)

**Impact:** MEDIUM
**Description:** TypeScript enables powerful patterns like discriminated unions, exhaustive checks, and utility types. These patterns make impossible states unrepresentable and code more maintainable.

## 7. Configuration (config)

**Impact:** LOW-MEDIUM
**Description:** tsconfig.json settings dramatically affect type safety and developer experience. Modern projects should use strict mode, proper module resolution, and target settings for their environment.

## 8. Testing (test)

**Impact:** LOW
**Description:** Type-level testing ensures your types behave as expected. Compile-time type tests catch type regressions, while proper mocking patterns maintain type safety in unit tests.
