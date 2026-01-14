---
title: Use ContiguousArray for Class Elements
impact: MEDIUM
impactDescription: Up to 2x faster for reference types
tags: collect, contiguousarray, class, performance
---

## Use ContiguousArray for Class Elements

`ContiguousArray` stores elements in contiguous memory, avoiding NSArray bridging overhead for class types. This can provide up to 2x performance improvement.

**Incorrect (Array with class elements may bridge):**

```swift
class Node {
    var value: Int
    var children: [Node] = []

    init(value: Int) { self.value = value }
}

// Array<Node> may use NSArray internally when bridging to Objective-C
var nodes: [Node] = []
for i in 0..<1000 {
    nodes.append(Node(value: i))
}
```

**Correct (ContiguousArray guarantees layout):**

```swift
class Node {
    var value: Int
    var children: ContiguousArray<Node> = []

    init(value: Int) { self.value = value }
}

// ContiguousArray always uses contiguous storage
// No NSArray bridging overhead
var nodes: ContiguousArray<Node> = []
nodes.reserveCapacity(1000)
for i in 0..<1000 {
    nodes.append(Node(value: i))
}

// When to use ContiguousArray:
// - Elements are class types or @objc protocols
// - You don't need to bridge to Objective-C APIs
// - Performance is critical

// When Array is fine:
// - Elements are value types (struct, enum)
// - You need Objective-C interoperability
```

Reference: [ContiguousArray - Apple Developer Documentation](https://developer.apple.com/documentation/swift/contiguousarray)
