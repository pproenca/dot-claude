---
title: Use @frozen for Fixed-Layout Types
impact: LOW-MEDIUM
impactDescription: Enables direct field access and stack allocation
tags: optim, frozen, layout, library
---

## Use @frozen for Fixed-Layout Types

`@frozen` promises the type's layout won't change, enabling more aggressive optimization. Clients can access fields directly and know the exact size at compile time.

**Incorrect (Library type may change):**

```swift
// Library code - caller must handle layout changes
public struct Point {
    public var x: Double
    public var y: Double
}

// Client code:
// - Can't assume size or layout
// - Must use accessors (potential function call overhead)
// - Can't stack-allocate with known size
```

**Correct (@frozen guarantees layout):**

```swift
// Library code - layout is fixed forever
@frozen
public struct Point {
    public var x: Double
    public var y: Double
}

// Client code benefits:
// - Direct field access instead of accessor calls
// - Size known at compile time (16 bytes)
// - Can be stack allocated by clients
// - Inlined in arrays without indirection

// Use @frozen for:
@frozen
public enum Optional<Wrapped> {  // Standard library does this
    case none
    case some(Wrapped)
}

@frozen
public struct SIMD4<Scalar> {  // Hardware-mapped types
    public var x, y, z, w: Scalar
}

// Never use @frozen for types that might evolve:
// - Don't freeze types with planned additions
// - Don't freeze if you might remove/reorder properties
// - Once frozen, changes are ABI-breaking
```

Reference: [Swift Evolution SE-0260 - Library Evolution](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0260-library-evolution.md)
