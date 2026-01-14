---
title: Implement deinit for Noncopyable Types
impact: HIGH
impactDescription: Ensures cleanup even on error paths
tags: owner, deinit, cleanup, resource
---

## Implement deinit for Noncopyable Types

Noncopyable types should clean up resources in `deinit` to ensure cleanup even on error paths where explicit close calls might be skipped.

**Incorrect (Manual cleanup can be missed):**

```swift
struct DatabaseConnection: ~Copyable {
    var handle: OpaquePointer?

    consuming func close() {
        sqlite3_close(handle)
    }
}

func query() throws {
    let conn = DatabaseConnection(handle: openDB())
    try performQuery(conn)  // If this throws...
    conn.close()  // ...this is never called!
}
```

**Correct (deinit ensures cleanup):**

```swift
struct DatabaseConnection: ~Copyable {
    var handle: OpaquePointer?

    deinit {
        sqlite3_close(handle)
    }

    consuming func close() {
        // Explicit close is optional but immediate
        sqlite3_close(handle)
        discard self  // Prevent deinit from running twice
    }
}

func query() throws {
    let conn = DatabaseConnection(handle: openDB())
    try performQuery(conn)
    // deinit called automatically, even on throw
}
```

Reference: [Swift Evolution SE-0390 - Noncopyable Structs and Enums](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0390-noncopyable-structs-and-enums.md)
