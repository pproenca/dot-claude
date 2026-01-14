---
title: Choose Structs Over Classes for Data
impact: CRITICAL
impactDescription: Eliminates ARC overhead, 20% lower memory
tags: memory, struct, value-type, arc
---

## Choose Structs Over Classes for Data

Structs avoid ARC overhead entirely. They're stack-allocated (when possible) and have no reference counting. Industry research shows struct-heavy designs can achieve 20% lower peak memory allocations.

**Incorrect (Class for simple data):**

```swift
class Point {
    var x: Double
    var y: Double

    init(x: Double, y: Double) {
        self.x = x
        self.y = y
    }
}

// Every assignment increments/decrements reference count
let p1 = Point(x: 0, y: 0)
let p2 = p1  // retain
// p1 and p2 share the same instance
```

**Correct (Struct for value semantics):**

```swift
struct Point {
    var x: Double
    var y: Double
}

// No reference counting, copied by value
let p1 = Point(x: 0, y: 0)
var p2 = p1  // Copy, no ARC
p2.x = 10    // Only p2 is modified

// Benefits:
// - No ARC overhead
// - Automatic Equatable/Hashable synthesis
// - Thread-safe by default (copies are independent)
// - Memberwise initializer provided
```

Reference: [WWDC24 - Explore Swift Performance](https://developer.apple.com/videos/play/wwdc2024/10217/)
