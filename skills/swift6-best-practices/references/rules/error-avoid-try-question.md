---
title: Avoid Overusing try?
impact: LOW
impactDescription: Preserves error information for debugging
tags: error, try, debugging, information
---

## Avoid Overusing try?

`try?` discards error information, making debugging harder. Use it only when the specific error truly doesn't matter.

**Incorrect (Discarding error information):**

```swift
func processFile(_ path: String) {
    guard let data = try? Data(contentsOf: URL(fileURLWithPath: path)) else {
        print("Failed to read file")  // Why did it fail?
        return
    }
    // Was it: file not found? Permission denied? Disk error?
    // No way to know
}

// Worse: silent failures in production
func loadUserPreferences() -> Preferences {
    if let saved = try? loadFromDisk() {
        return saved
    }
    return .default  // Silently using defaults - user's settings lost?
}
```

**Correct (Preserve error for debugging):**

```swift
func processFile(_ path: String) {
    do {
        let data = try Data(contentsOf: URL(fileURLWithPath: path))
        process(data)
    } catch {
        print("Failed to read file: \(error)")  // Includes specific reason
        logger.error("File read failed", metadata: [
            "path": path,
            "error": "\(error)"
        ])
    }
}

// try? is OK when error truly doesn't matter:

// Optional cache - fallback is fine
let cachedValue = try? loadFromCache()
let value = cachedValue ?? computeValue()

// Best-effort cleanup
try? fileManager.removeItem(at: tempFile)

// User preference with known default
let prefersDark = (try? loadThemePreference()) ?? false

// But log unexpected failures in important operations
func saveDocument() {
    do {
        try persist(document)
    } catch {
        // Don't silently fail - user needs to know!
        showAlert("Save failed: \(error.localizedDescription)")
        logger.error("Document save failed", error: error)
    }
}
```

Reference: [Swift Error Handling](https://docs.swift.org/swift-book/LanguageGuide/ErrorHandling.html)
