---
title: Use nonisolated for Pure Functions
impact: CRITICAL
impactDescription: Avoids unnecessary async overhead
tags: concur, nonisolated, performance, pure
---

## Use nonisolated for Pure Functions

Methods that don't access actor state can be marked `nonisolated` to avoid unnecessary async context and improve performance. This allows synchronous calls without await.

**Incorrect (Pure function requires await due to actor isolation):**

```swift
actor Calculator {
    private var lastResult: Double = 0

    // Unnecessarily requires await even though it doesn't access state
    func add(_ a: Double, _ b: Double) -> Double {
        return a + b
    }
}

// Caller must use await
let result = await calculator.add(1, 2)
```

**Correct (nonisolated for stateless operations):**

```swift
actor Calculator {
    private var lastResult: Double = 0

    nonisolated func add(_ a: Double, _ b: Double) -> Double {
        return a + b
    }

    func addAndStore(_ a: Double, _ b: Double) -> Double {
        lastResult = a + b
        return lastResult
    }
}

// Usage: no await needed for nonisolated
let calc = Calculator()
let sum = calc.add(1, 2)  // Synchronous!
let stored = await calc.addAndStore(3, 4)  // Requires await
```

Reference: [Swift.org - Enabling Complete Concurrency Checking](https://www.swift.org/documentation/concurrency/)
