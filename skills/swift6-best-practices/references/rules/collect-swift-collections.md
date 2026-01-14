---
title: Consider swift-collections for Specialized Needs
impact: MEDIUM
impactDescription: Optimized data structures for specific patterns
tags: collect, swift-collections, deque, ordered
---

## Consider swift-collections for Specialized Needs

The swift-collections package provides optimized data structures beyond the standard library for specific access patterns.

**Correct (Use specialized collections):**

```swift
import Collections

// OrderedSet: Set with insertion order preserved
let orderedSet: OrderedSet = [3, 1, 4, 1, 5]  // [3, 1, 4, 5]
// Maintains uniqueness like Set, but preserves order
// O(1) contains, O(1) append, ordered iteration

// OrderedDictionary: Dictionary with insertion order
var orderedDict: OrderedDictionary = ["b": 2, "a": 1]
orderedDict["c"] = 3
// Iterates in order: [("b", 2), ("a", 1), ("c", 3)]

// Deque: Double-ended queue
var deque: Deque = [1, 2, 3]
deque.prepend(0)     // O(1) - unlike Array's O(n)
deque.append(4)      // O(1)
deque.popFirst()     // O(1) - unlike Array's O(n)
deque.popLast()      // O(1)
// Great for queues and sliding windows

// TreeDictionary/TreeSet: Persistent collections
// Excellent for immutable data with frequent updates
let tree1: TreeDictionary = ["a": 1, "b": 2]
let tree2 = tree1.merging(["c": 3]) { $1 }
// tree1 and tree2 share structure - memory efficient

// Heap: Priority queue
var heap = Heap<Task>()  // Using comparable
heap.insert(task)
let highest = heap.popMax()  // O(log n)

// Add dependency:
// .package(url: "https://github.com/apple/swift-collections.git", from: "1.0.0")
```

Reference: [GitHub - apple/swift-collections](https://github.com/apple/swift-collections)
