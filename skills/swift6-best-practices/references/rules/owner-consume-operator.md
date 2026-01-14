---
title: Use consume to End Variable Lifetime
impact: HIGH
impactDescription: Enables early memory release optimization
tags: owner, consume, lifetime, optimization
---

## Use consume to End Variable Lifetime

The `consume` operator explicitly ends a variable's lifetime, enabling the compiler to free memory earlier and reduce memory pressure.

**Incorrect (Variable lifetime extends unnecessarily):**

```swift
func processBuffer(_ buffer: consuming [UInt8]) {
    let result = transform(buffer)
    // buffer still "alive" even though we're done with it
    // memory not freed until function returns
    expensiveOperation(result)
}
```

**Correct (consume ends lifetime early):**

```swift
func processBuffer(_ buffer: consuming [UInt8]) {
    let result = transform(consume buffer)
    // buffer memory freed immediately after transform
    expensiveOperation(result)  // Less memory pressure during this call
}

// Also useful for explicit transfer
func transferOwnership() {
    var resource = acquireResource()
    let newOwner = consume resource
    // resource is now invalid, newOwner has ownership
    // print(resource)  // Error: used after consume
    useResource(newOwner)
}
```

Reference: [Swift Evolution SE-0366 - consume operator](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0366-move-function.md)
