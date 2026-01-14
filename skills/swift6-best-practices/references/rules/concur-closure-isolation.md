---
title: Handle Closure Isolation Inheritance
impact: CRITICAL
impactDescription: Prevents crashes from wrong-thread access
tags: concur, closure, isolation, callback
---

## Handle Closure Isolation Inheritance

Closures inherit isolation from their enclosing context. When frameworks call closures from background threads, explicit handling is required to avoid runtime crashes.

**Incorrect (Closure assumes main actor context):**

```swift
@MainActor
class DownloadManager {
    var downloadedFiles: [String] = []

    func startDownload(completion: @escaping (String) -> Void) {
        URLSession.shared.dataTask(with: url) { data, _, _ in
            // This closure runs on a background thread!
            // Crash: accessing @MainActor property from background
            self.downloadedFiles.append(filename)
            completion(filename)
        }.resume()
    }
}
```

**Correct (Explicitly dispatch to main actor):**

```swift
@MainActor
class DownloadManager {
    var downloadedFiles: [String] = []

    func startDownload(completion: @escaping (String) -> Void) {
        URLSession.shared.dataTask(with: url) { data, _, _ in
            Task { @MainActor in
                self.downloadedFiles.append(filename)
                completion(filename)
            }
        }.resume()
    }
}

// Or use modern async/await
@MainActor
class DownloadManager {
    var downloadedFiles: [String] = []

    func startDownload() async throws -> String {
        let (data, _) = try await URLSession.shared.data(from: url)
        downloadedFiles.append(filename)
        return filename
    }
}
```

Reference: [SwiftLee - Approachable Concurrency in Swift 6.2](https://www.avanderlee.com/concurrency/approachable-concurrency-in-swift-6-2-a-clear-guide/)
