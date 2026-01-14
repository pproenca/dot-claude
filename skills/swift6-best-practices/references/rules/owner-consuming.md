---
title: Apply consuming for Ownership Transfer
impact: HIGH
impactDescription: Explicit ownership semantics, zero-copy transfer
tags: owner, consuming, transfer, ownership
---

## Apply consuming for Ownership Transfer

Use `consuming` when a function takes permanent ownership of a value. This makes ownership transfer explicit and prevents use-after-move bugs.

**Incorrect (Implicit ownership unclear):**

```swift
struct UniqueBuffer: ~Copyable {
    var data: UnsafeMutableBufferPointer<UInt8>

    // Does this function take ownership or just borrow?
    func process(_ buffer: UniqueBuffer) {
        // Unclear semantics
    }
}
```

**Correct (Explicit consuming ownership):**

```swift
struct UniqueBuffer: ~Copyable {
    var data: UnsafeMutableBufferPointer<UInt8>

    deinit {
        data.deallocate()
    }
}

// Ownership is transferred to the function
func process(_ buffer: consuming UniqueBuffer) {
    // buffer is consumed, will be deinitialized after use
    print(buffer.data.count)
}

// Caller cannot use buffer after passing
let buffer = UniqueBuffer(data: .allocate(capacity: 1024))
process(buffer)
// print(buffer.data.count)  // Error: 'buffer' used after consume
```

Reference: [Swift Evolution SE-0377 - Parameter Ownership Modifiers](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0377-parameter-ownership-modifiers.md)
