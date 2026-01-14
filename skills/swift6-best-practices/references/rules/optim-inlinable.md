---
title: Use @inlinable for Cross-Module Hot Paths
impact: LOW-MEDIUM
impactDescription: Enables cross-module inlining optimization
tags: optim, inlinable, performance, module
---

## Use @inlinable for Cross-Module Hot Paths

`@inlinable` exposes function implementation, enabling the compiler to inline calls from other modules. Critical for library performance.

**Incorrect (Internal implementation hidden):**

```swift
// In MyLibrary module
public struct Vector {
    public var x, y, z: Double

    public func dot(_ other: Vector) -> Double {
        return x * other.x + y * other.y + z * other.z
    }
}

// In client code - function call overhead for every dot()
// Cannot inline across module boundary
```

**Correct (@inlinable enables inlining):**

```swift
// In MyLibrary module
public struct Vector {
    public var x, y, z: Double

    @inlinable
    public func dot(_ other: Vector) -> Double {
        return x * other.x + y * other.y + z * other.z
    }
}

// In client code - dot() can be inlined
// No function call overhead in tight loops

// Caveats:
// 1. Implementation becomes part of public ABI
// 2. Changes require client recompilation for effect
// 3. Increases client binary size slightly

// Best for:
// - Small, performance-critical functions
// - Stable implementations unlikely to change
// - Library code called in hot paths
```

Reference: [Swift Evolution SE-0193 - Cross-module inlining](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0193-cross-module-inlining-and-specialization.md)
