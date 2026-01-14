---
title: Apply lazy for Chained Transformations
impact: MEDIUM
impactDescription: Eliminates intermediate allocations
tags: collect, lazy, sequence, transformation
---

## Apply lazy for Chained Transformations

Lazy sequences avoid intermediate array allocations when chaining operations. Computations happen only when elements are accessed.

**Incorrect (Eager evaluation creates temporaries):**

```swift
let numbers = Array(0..<10000)

let result = numbers
    .filter { $0 % 2 == 0 }  // Creates [Int] with 5000 elements
    .map { $0 * 2 }          // Creates [Int] with 5000 elements
    .prefix(10)              // Creates ArraySlice with 10 elements

// Three intermediate allocations for 10 final elements
```

**Correct (Lazy evaluation avoids allocations):**

```swift
let numbers = Array(0..<10000)

let result = numbers.lazy
    .filter { $0 % 2 == 0 }  // LazyFilterSequence - no allocation
    .map { $0 * 2 }          // LazyMapSequence - no allocation
    .prefix(10)              // LazyPrefixSequence - no allocation

// Only when consumed:
let array = Array(result)  // Creates single [Int] with 10 elements
// Only processes 20 elements (10 even numbers), not all 10,000

// Good use cases
let firstMatch = hugelist.lazy.filter(predicate).first
let topN = items.lazy.sorted().prefix(10)
let transformed = data.lazy.compactMap(transform).first

// Avoid lazy when:
// - You need the full result anyway (map all elements)
// - Random access is required (lazy can't skip ahead efficiently)
// - The source collection is small
```

Reference: [LazySequenceProtocol - Apple Developer Documentation](https://developer.apple.com/documentation/swift/lazysequenceprotocol)
