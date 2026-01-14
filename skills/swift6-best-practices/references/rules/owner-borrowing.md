---
title: Use borrowing for Read-Only Access
impact: HIGH
impactDescription: Zero-copy read access without ownership change
tags: owner, borrowing, readonly, access
---

## Use borrowing for Read-Only Access

Use `borrowing` for temporary read access without ownership transfer. This enables zero-copy reads while maintaining ownership at the call site.

**Incorrect (Unnecessary ownership transfer):**

```swift
struct LargeData: ~Copyable {
    var bytes: [UInt8]
}

// Taking ownership when only reading
func checksum(_ data: consuming LargeData) -> UInt32 {
    var sum: UInt32 = 0
    for byte in data.bytes {
        sum = sum &+ UInt32(byte)
    }
    return sum
    // data is consumed - caller loses access unnecessarily
}
```

**Correct (Borrowing for read-only access):**

```swift
struct LargeData: ~Copyable {
    var bytes: [UInt8]
}

// Borrowing: read access, no ownership change
func checksum(_ data: borrowing LargeData) -> UInt32 {
    var sum: UInt32 = 0
    for byte in data.bytes {
        sum = sum &+ UInt32(byte)
    }
    return sum
}

// Caller retains ownership
var data = LargeData(bytes: Array(0..<1000))
let cs = checksum(data)
print(data.bytes.count)  // Still valid - data was only borrowed
```

Reference: [Swift Evolution SE-0377 - Parameter Ownership Modifiers](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0377-parameter-ownership-modifiers.md)
