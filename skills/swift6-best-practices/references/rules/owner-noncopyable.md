---
title: Use ~Copyable for Unique Resources
impact: HIGH
impactDescription: Prevents double-free and use-after-free at compile time
tags: owner, noncopyable, resource, unique
---

## Use ~Copyable for Unique Resources

File handles, database connections, and locks should have unique ownership to prevent double-close bugs. Noncopyable types guarantee single ownership at compile time.

**Incorrect (Copyable resource can be used after transfer):**

```swift
struct FileHandle {
    let fd: Int32

    func close() {
        Darwin.close(fd)
    }
}

func processFile() {
    let handle = FileHandle(fd: open("file.txt", O_RDONLY))
    let copy = handle  // Accidental copy
    handle.close()
    copy.close()  // Double close! Undefined behavior
}
```

**Correct (~Copyable prevents copies):**

```swift
struct FileHandle: ~Copyable {
    let fd: Int32

    consuming func close() {
        Darwin.close(fd)
    }

    deinit {
        Darwin.close(fd)
    }
}

func processFile() {
    let handle = FileHandle(fd: open("file.txt", O_RDONLY))
    // let copy = handle  // Error: 'handle' is noncopyable
    handle.close()  // Ownership transferred, handle no longer usable
}
```

Reference: [WWDC24 - Consume noncopyable types in Swift](https://developer.apple.com/videos/play/wwdc2024/10170/)
