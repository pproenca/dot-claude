---
title: Prefer Concrete Types Over Protocols
impact: LOW-MEDIUM
impactDescription: Enables maximum optimization
tags: optim, concrete, protocol, types
---

## Prefer Concrete Types Over Protocols

When the concrete type is known, use it directly for better optimization. The compiler can inline, specialize, and eliminate abstractions.

**Incorrect (Protocol type hides concrete type):**

```swift
func computeSum(_ numbers: any Sequence<Int>) -> Int {
    return numbers.reduce(0, +)
    // Existential overhead
    // Cannot specialize for Array
}

func process(_ data: any Collection<UInt8>) {
    // Must handle any collection type generically
    // Even if caller always passes Data
}
```

**Correct (Concrete type when known):**

```swift
func computeSum(_ numbers: [Int]) -> Int {
    return numbers.reduce(0, +)
    // Optimized specifically for Array
    // Direct memory access
}

// Or use generics when flexibility is needed
func computeSum<S: Sequence>(_ numbers: S) -> Int where S.Element == Int {
    return numbers.reduce(0, +)
    // Specializable for each concrete type
}

// Overload for common concrete types
func process(_ data: Data) {
    // Optimized for Data
}

func process(_ data: [UInt8]) {
    // Optimized for Array
}

func process<C: Collection>(_ data: C) where C.Element == UInt8 {
    // Fallback for other collections
}
```

Reference: [WWDC24 - Explore Swift Performance](https://developer.apple.com/videos/play/wwdc2024/10217/)
