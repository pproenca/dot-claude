---
title: Reserve Capacity for Known Sizes
impact: MEDIUM
impactDescription: Eliminates reallocation overhead
tags: collect, capacity, allocation, performance
---

## Reserve Capacity for Known Sizes

Pre-allocating capacity avoids repeated reallocations during collection growth, reducing memory churn and improving performance.

**Incorrect (Repeated reallocations):**

```swift
var results: [ProcessedItem] = []

for item in largeDataSet {  // 10,000 items
    let processed = process(item)
    results.append(processed)
    // Array may reallocate multiple times:
    // capacity 1 -> 2 -> 4 -> 8 -> 16 -> ... -> 16384
    // Each reallocation copies all existing elements
}
```

**Correct (Reserve capacity upfront):**

```swift
var results: [ProcessedItem] = []
results.reserveCapacity(largeDataSet.count)  // Single allocation

for item in largeDataSet {
    let processed = process(item)
    results.append(processed)  // No reallocation needed
}

// Works for all collection types
var dict: [String: Int] = [:]
dict.reserveCapacity(expectedKeyCount)

var set: Set<String> = []
set.reserveCapacity(expectedElementCount)

// Even better: use map when appropriate
let results = largeDataSet.map { process($0) }  // Sized correctly automatically

// Avoid over-reserving (wastes memory)
var small: [Int] = []
small.reserveCapacity(1_000_000)  // Bad if you only need 100 elements
```

Reference: [Array.reserveCapacity - Apple Developer Documentation](https://developer.apple.com/documentation/swift/array/reservecapacity(_:))
