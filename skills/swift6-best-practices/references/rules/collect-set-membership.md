---
title: Prefer Set for Membership Testing
impact: MEDIUM
impactDescription: O(1) vs O(n) lookup performance
tags: collect, set, contains, lookup
---

## Prefer Set for Membership Testing

Sets provide O(1) membership testing vs O(n) for Array.contains. Use Set when you need fast membership checks.

**Incorrect (Array.contains for membership):**

```swift
let validUserIds = Array(0..<10000)

func isValidUser(_ id: Int) -> Bool {
    return validUserIds.contains(id)  // O(n) - scans entire array
}

// For 10,000 elements, worst case checks all 10,000
// Repeated calls make this extremely slow
```

**Correct (Set for O(1) lookup):**

```swift
let validUserIds = Set(0..<10000)

func isValidUser(_ id: Int) -> Bool {
    return validUserIds.contains(id)  // O(1) - hash lookup
}

// Constant time regardless of set size
// 10 elements or 10 million - same speed

// Common patterns
let allowedDomains: Set<String> = ["example.com", "test.org", "demo.net"]
let visited: Set<URL> = []
let processedIds: Set<UUID> = []

// Building from array when needed
let userList: [User] = fetchUsers()
let userIdSet = Set(userList.map { $0.id })  // One-time O(n) conversion
// Subsequent lookups are O(1)
```

Reference: [Swift Collections - Set](https://developer.apple.com/documentation/swift/set)
