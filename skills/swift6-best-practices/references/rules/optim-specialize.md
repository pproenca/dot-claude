---
title: Specialize Generic Functions
impact: LOW-MEDIUM
impactDescription: Type-specific optimized code paths
tags: optim, specialize, generic, performance
---

## Specialize Generic Functions

Generic functions can be specialized for specific types to generate optimized code paths. The compiler does this automatically within modules, but you can hint for cross-module cases.

**Correct (Specialization hints):**

```swift
// @_specialize hints the compiler to generate specialized versions
// Note: This is not officially stable API

@_specialize(where T == Int)
@_specialize(where T == Double)
@_specialize(where T == Float)
func sum<T: Numeric>(_ array: [T]) -> T {
    return array.reduce(0, +)
}

// Compiler generates:
// - sum<Int>([Int]) -> Int       // Specialized for Int
// - sum<Double>([Double]) -> Double  // Specialized for Double
// - sum<Float>([Float]) -> Float     // Specialized for Float
// - sum<T>([T]) -> T             // Generic fallback

// Without specialization, generic code must:
// - Pass type metadata at runtime
// - Use protocol witness tables for operations
// - Cannot inline type-specific optimizations

// Within a module, WMO handles this automatically:
func internalSum<T: Numeric>(_ array: [T]) -> T {
    array.reduce(0, +)
}

// When called with concrete type, compiler specializes:
let intResult = internalSum([1, 2, 3])  // Specialized to Int
let doubleResult = internalSum([1.0, 2.0])  // Specialized to Double

// Cross-module requires @inlinable or @_specialize
@inlinable
public func publicSum<T: Numeric>(_ array: [T]) -> T {
    array.reduce(0, +)  // Client can specialize
}
```

Reference: [Swift Compiler Optimization Tips](https://github.com/swiftlang/swift/blob/main/docs/OptimizationTips.rst)
