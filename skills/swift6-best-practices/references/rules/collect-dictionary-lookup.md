---
title: Use Dictionary for Key-Value Lookups
impact: MEDIUM
impactDescription: O(1) key access performance
tags: collect, dictionary, lookup, key-value
---

## Use Dictionary for Key-Value Lookups

Dictionary provides O(1) access for key-value pairs, avoiding linear searches through arrays of tuples.

**Incorrect (Array of tuples for lookup):**

```swift
let userAges: [(name: String, age: Int)] = [
    ("Alice", 30),
    ("Bob", 25),
    ("Charlie", 35)
]

func getAge(for name: String) -> Int? {
    return userAges.first { $0.name == name }?.age  // O(n)
}

// Scales poorly with data size
// Must scan through all tuples to find match
```

**Correct (Dictionary for key-based access):**

```swift
let userAges: [String: Int] = [
    "Alice": 30,
    "Bob": 25,
    "Charlie": 35
]

func getAge(for name: String) -> Int? {
    return userAges[name]  // O(1)
}

// Common dictionary patterns
var cache: [URL: Data] = [:]
var userSessions: [SessionID: User] = [:]
var configSettings: [String: Any] = [:]

// Building from array
let users: [User] = fetchUsers()
let userById: [UUID: User] = Dictionary(uniqueKeysWithValues: users.map { ($0.id, $0) })

// Handling duplicate keys
let items: [(key: String, value: Int)] = [("a", 1), ("a", 2)]
let dict = Dictionary(items, uniquingKeysWith: { $1 })  // Keep last value
```

Reference: [Swift Collections - Dictionary](https://developer.apple.com/documentation/swift/dictionary)
