---
title: Prefer async let for Fixed Concurrent Operations
impact: MEDIUM
impactDescription: Cleaner code for known concurrency
tags: async, async-let, concurrent, parallel
---

## Prefer async let for Fixed Concurrent Operations

When running a known number of concurrent operations, `async let` is cleaner and more type-safe than TaskGroup.

**Incorrect (TaskGroup for fixed operations):**

```swift
func fetchUserData(id: Int) async throws -> (User, Posts, Friends) {
    return try await withThrowingTaskGroup(of: Any.self) { group in
        var user: User!
        var posts: Posts!
        var friends: Friends!

        group.addTask { try await self.fetchUser(id) }
        group.addTask { try await self.fetchPosts(id) }
        group.addTask { try await self.fetchFriends(id) }

        for try await result in group {
            switch result {
            case let u as User: user = u
            case let p as Posts: posts = p
            case let f as Friends: friends = f
            default: break
            }
        }

        return (user, posts, friends)
    }
}
```

**Correct (async let for clarity):**

```swift
func fetchUserData(id: Int) async throws -> (User, Posts, Friends) {
    async let user = fetchUser(id)
    async let posts = fetchPosts(id)
    async let friends = fetchFriends(id)

    // All three requests run concurrently
    // Awaited together - if any fails, all are cancelled
    return try await (user, posts, friends)
}

// Benefits:
// - Type-safe: each variable has its correct type
// - Automatic cancellation on error
// - Cleaner, more readable code
// - Compiler ensures all async lets are awaited
```

Reference: [Swift Concurrency - async let](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
