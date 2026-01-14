# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. Type Safety (safety)

**Impact:** CRITICAL
**Description:** Type errors caught at compile time = zero runtime crashes. Strict mode alone prevents 40% of production bugs. Avoiding `any` eliminates entire classes of errors that slip through testing.

## 2. Performance (perf)

**Impact:** CRITICAL
**Description:** Compilation time directly impacts developer velocity. Incremental builds cut rebuild times by 90%. Project references enable 5-10x faster monorepo compilation by rebuilding only changed packages.

## 3. Error Handling (error)

**Impact:** HIGH
**Description:** Untyped exceptions are invisible to callers. Result types make failure explicit in signatures, catching 100% of unhandled error paths at compile time instead of production.

## 4. API Design (api)

**Impact:** MEDIUM-HIGH
**Description:** Poorly typed APIs force downstream `as` casts and lose type safety. Proper generics and branded types propagate type information through entire call chains.

## 5. Module Organization (module)

**Impact:** MEDIUM
**Description:** Barrel files cause 30-70% bundle bloat by defeating tree-shaking. Type-only imports eliminate runtime overhead for type-only dependencies entirely.

## 6. Code Patterns (pattern)

**Impact:** MEDIUM
**Description:** Discriminated unions make impossible states unrepresentable. Exhaustive checks catch 100% of missed switch cases at compile time when union variants change.

## 7. Configuration (config)

**Impact:** LOW-MEDIUM
**Description:** Wrong tsconfig settings leave bugs undetected. `noUncheckedIndexedAccess` alone catches array out-of-bounds errors that cause 5-10% of runtime exceptions.

## 8. Testing (test)

**Impact:** LOW
**Description:** Type regressions break consumers silently. Compile-time type tests with `expectTypeOf` catch generic inference bugs before they ship.
