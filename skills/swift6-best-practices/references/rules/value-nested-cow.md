---
title: Avoid Nested CoW Quadratic Behavior
impact: MEDIUM-HIGH
impactDescription: Prevents O(n^2) copying in loops
tags: value, cow, quadratic, nested
---

## Avoid Nested CoW Quadratic Behavior

Modifying CoW collections inside loops can cause O(n^2) behavior if each iteration triggers a copy.

**Incorrect (Quadratic copying in loop):**

```swift
var items = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

for i in items.indices {
    items[i].append(0)  // Each append may trigger copy due to shared reference
}
// With many iterations, this becomes O(n^2)
```

**Correct (Minimize CoW triggers):**

```swift
// Option 1: Use inout to maintain unique reference
var items = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

for i in items.indices {
    var inner = items[i]  // Take ownership temporarily
    inner.append(0)       // Mutate local copy
    items[i] = inner      // Put back
}

// Option 2: Build new structure (often cleaner)
let items = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
let result = items.map { $0 + [0] }

// Option 3: Use withUnsafeMutableBufferPointer for in-place mutation
var items = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
items.withContiguousMutableStorageIfAvailable { buffer in
    for i in buffer.indices {
        buffer[i].append(0)
    }
}
```

Reference: [Understanding Swift Copy-on-Write Mechanisms](https://medium.com/@lucianoalmeida1/understanding-swift-copy-on-write-mechanisms-52ac31d68f2f)
