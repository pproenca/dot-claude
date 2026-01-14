---
title: Prefer Structs for Simple Data Models
impact: MEDIUM-HIGH
impactDescription: No ARC, stack allocation, thread-safe by default
tags: value, struct, model, data
---

## Prefer Structs for Simple Data Models

Structs are stack-allocated (when possible), have no reference counting, and provide automatic thread safety through value semantics.

**Incorrect (Class for simple data):**

```swift
class User {
    var id: UUID
    var name: String
    var email: String

    init(id: UUID, name: String, email: String) {
        self.id = id
        self.name = name
        self.email = email
    }
}

// Requires manual Equatable implementation
// Shared mutable state risks
// ARC overhead on every copy
```

**Correct (Struct for data models):**

```swift
struct User {
    var id: UUID
    var name: String
    var email: String
}

// Benefits:
// - No ARC overhead
// - Automatic Equatable/Hashable synthesis
// - Thread-safe by default (copies are independent)
// - Memberwise initializer provided
// - Codable synthesis works automatically

let user1 = User(id: UUID(), name: "Alice", email: "alice@example.com")
var user2 = user1  // Copy, completely independent
user2.name = "Bob"  // Only user2 is modified
```

Reference: [WWDC24 - Explore Swift Performance](https://developer.apple.com/videos/play/wwdc2024/10217/)
