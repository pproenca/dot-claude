---
title: Use isKnownUniquelyReferenced
impact: MEDIUM-HIGH
impactDescription: Copy only when necessary for CoW
tags: value, cow, unique, reference
---

## Use isKnownUniquelyReferenced

`isKnownUniquelyReferenced` is the key function for efficient CoW - it checks if copying is necessary before mutation.

**Incorrect (Always copy on mutation):**

```swift
struct Buffer {
    private class Storage {
        var data: [UInt8]
        init(_ data: [UInt8]) { self.data = data }
    }

    private var storage: Storage

    mutating func append(_ byte: UInt8) {
        // Always copies - defeats CoW purpose entirely
        storage = Storage(storage.data + [byte])
    }
}
```

**Correct (Copy only when shared):**

```swift
struct Buffer {
    private final class Storage {
        var data: [UInt8]
        init(_ data: [UInt8]) { self.data = data }
    }

    private var storage: Storage

    init(_ data: [UInt8] = []) {
        storage = Storage(data)
    }

    mutating func append(_ byte: UInt8) {
        // Only copy if storage is shared
        if !isKnownUniquelyReferenced(&storage) {
            storage = Storage(storage.data)
        }
        storage.data.append(byte)
    }

    var count: Int { storage.data.count }
}

// Usage
var buffer1 = Buffer([1, 2, 3])
var buffer2 = buffer1  // No copy yet - storage shared
buffer1.append(4)       // Now copies because storage was shared
buffer2.append(5)       // No copy - buffer2 now has unique storage
```

Reference: [isKnownUniquelyReferenced - Apple Developer Documentation](https://developer.apple.com/documentation/swift/isknownuniquelyreferenced(_:))
