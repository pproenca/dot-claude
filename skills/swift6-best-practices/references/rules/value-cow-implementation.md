---
title: Implement Copy-on-Write for Large Types
impact: MEDIUM-HIGH
impactDescription: Value semantics with reference performance
tags: value, cow, copy-on-write, performance
---

## Implement Copy-on-Write for Large Types

For structs with large data, wrap storage in a class to enable CoW semantics. This provides value semantics with reference-type performance.

**Incorrect (Struct copies all data on mutation):**

```swift
struct Image {
    var width: Int
    var height: Int
    var pixels: UnsafeMutablePointer<UInt32>
    // Copied by value - pointer shared, double-free risk!
}
```

**Correct (CoW wrapper for custom storage):**

```swift
struct Image {
    private final class Storage {
        var width: Int
        var height: Int
        var pixels: UnsafeMutablePointer<UInt32>

        init(width: Int, height: Int) {
            self.width = width
            self.height = height
            self.pixels = .allocate(capacity: width * height)
        }

        func copy() -> Storage {
            let new = Storage(width: width, height: height)
            new.pixels.update(from: pixels, count: width * height)
            return new
        }

        deinit {
            pixels.deallocate()
        }
    }

    private var storage: Storage

    var width: Int { storage.width }
    var height: Int { storage.height }

    mutating func setPixel(x: Int, y: Int, color: UInt32) {
        ensureUnique()
        storage.pixels[y * width + x] = color
    }

    private mutating func ensureUnique() {
        if !isKnownUniquelyReferenced(&storage) {
            storage = storage.copy()
        }
    }
}
```

Reference: [Swift Copy-on-Write Optimization](https://medium.com/hash-coding/swift-copy-on-write-optimization-46b1890862dd)
