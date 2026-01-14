---
title: Use @usableFromInline for Internal Helpers
impact: LOW-MEDIUM
impactDescription: Enables inlining of internal dependencies
tags: optim, usablefrominline, inlinable, internal
---

## Use @usableFromInline for Internal Helpers

When `@inlinable` functions call internal helpers, mark those helpers `@usableFromInline` to enable inlining without making them fully public.

**Incorrect (@inlinable can't call internal):**

```swift
public struct Buffer {
    @inlinable
    public func process() -> Data {
        // Error: validateInput() is internal, not visible to clients
        if validateInput() {
            return transform()
        }
        return Data()
    }

    func validateInput() -> Bool { true }  // Internal
    func transform() -> Data { Data() }     // Internal
}
```

**Correct (@usableFromInline exposes for inlining):**

```swift
public struct Buffer {
    @inlinable
    public func process() -> Data {
        if validateInput() {
            return transform()
        }
        return Data()
    }

    @usableFromInline
    func validateInput() -> Bool { true }

    @usableFromInline
    func transform() -> Data { Data() }
}

// @usableFromInline means:
// - Still internal access level (not part of public API)
// - But visible to clients for inlining purposes
// - Implementation becomes part of ABI like @inlinable

// For stored properties in @frozen structs:
@frozen
public struct Point {
    @usableFromInline
    var _x: Double  // Visible for inlining

    public var x: Double {
        @inlinable get { _x }
        @inlinable set { _x = newValue }
    }
}
```

Reference: [Swift Evolution SE-0193 - Cross-module inlining](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0193-cross-module-inlining-and-specialization.md)
