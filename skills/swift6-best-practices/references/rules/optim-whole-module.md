---
title: Enable Whole-Module Optimization
impact: LOW-MEDIUM
impactDescription: Cross-file optimization within module
tags: optim, wmo, whole-module, build
---

## Enable Whole-Module Optimization

Whole-Module Optimization (WMO) enables cross-file optimizations within a module, including inlining, dead code elimination, and generic specialization.

**Correct (Build settings configuration):**

```swift
// Xcode Build Settings:

// Debug: Incremental for fast builds
// SWIFT_COMPILATION_MODE = singlefile
// SWIFT_OPTIMIZATION_LEVEL = -Onone

// Release: WMO for optimized builds
// SWIFT_COMPILATION_MODE = wholemodule
// SWIFT_OPTIMIZATION_LEVEL = -O

// Or for size optimization:
// SWIFT_OPTIMIZATION_LEVEL = -Osize

// Command line:
// swiftc -O -whole-module-optimization *.swift

// Benefits of WMO:
// 1. Functions can be inlined across files
// 2. Unused internal code eliminated
// 3. Generics specialized for concrete types
// 4. More aggressive devirtualization
// 5. Better escape analysis

// Trade-off:
// - Longer compile times (can't parallelize across files)
// - For development, use incremental compilation
// - For release, WMO is essential

// Example: internal func becomes inlinable across files
// File1.swift
internal func helper() -> Int { 42 }

// File2.swift
public func caller() -> Int {
    helper()  // Can be inlined with WMO
}
```

Reference: [Swift Compiler - Whole Module Optimization](https://github.com/swiftlang/swift/blob/main/docs/OptimizationTips.rst)
