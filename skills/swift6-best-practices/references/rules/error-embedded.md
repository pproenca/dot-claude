---
title: Use Typed Throws in Embedded Contexts
impact: LOW
impactDescription: Eliminates existential overhead for errors
tags: error, embedded, performance, typed
---

## Use Typed Throws in Embedded Contexts

Typed throws eliminates existential boxing overhead for error types, which is important for embedded Swift and performance-critical code paths.

**Correct (Typed throws for embedded systems):**

```swift
// Embedded Swift - no runtime, minimal overhead
enum GPIOError: Error {
    case invalidPin
    case alreadyInUse
    case permissionDenied
}

// Typed throws avoids any Error existential
func configureGPIO(pin: Int) throws(GPIOError) {
    guard pin >= 0 && pin < 40 else {
        throw .invalidPin
    }
    guard !usedPins.contains(pin) else {
        throw .alreadyInUse
    }
    // Configure hardware...
}

// Memory layout comparison:
// Untyped throws:
//   [Existential Container] -> [Type Metadata] -> [Error Value]
//   Requires runtime, heap allocation possible
//
// Typed throws:
//   [Error Value]
//   Direct storage, no metadata, no allocation

// Performance-critical contexts
@inlinable
public func parseNumber(_ s: String) throws(ParseError) -> Int {
    // Hot path - avoid existential overhead
    guard let value = Int(s) else {
        throw .invalidFormat
    }
    return value
}

// Generic typed throws propagation
func map<T, E: Error>(
    _ transform: (Element) throws(E) -> T
) throws(E) -> [T] {
    // Error type flows through without boxing
}
```

Reference: [Swift.org - Embedded Swift](https://www.swift.org/blog/embedded-swift-examples/)
