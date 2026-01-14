---
title: Mark Classes final for Devirtualization
impact: LOW-MEDIUM
impactDescription: Enables static dispatch, removes vtable lookup
tags: optim, final, devirtualization, dispatch
---

## Mark Classes final for Devirtualization

`final` enables static dispatch instead of virtual dispatch through vtable, eliminating method lookup overhead.

**Incorrect (Open for subclassing unnecessarily):**

```swift
class Parser {
    func parse(_ input: String) -> AST {
        // Virtual dispatch: lookup in vtable at runtime
        return parseImplementation(input)
    }

    func parseImplementation(_ input: String) -> AST {
        // Each call goes through vtable indirection
    }
}

// Subclassing possible but not intended
// Compiler cannot optimize to direct calls
```

**Correct (final enables static dispatch):**

```swift
final class Parser {
    func parse(_ input: String) -> AST {
        // Direct function call, no vtable lookup
        return parseImplementation(input)
    }

    func parseImplementation(_ input: String) -> AST {
        // Compiler knows exact implementation
    }
}

// Also works at method level
class BaseClass {
    final func optimizedMethod() {
        // This specific method uses static dispatch
        // Even though class can be subclassed
    }

    func overridableMethod() {
        // This still uses virtual dispatch
    }
}

// Whole-module optimization can infer final
// But explicit final is clearer and works across modules
```

Reference: [WWDC24 - Explore Swift Performance](https://developer.apple.com/videos/play/wwdc2024/10217/)
