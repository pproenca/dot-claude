# Swift by Topic

> Base path: `references/swift/`

Map Swift language features relevant to data modeling, performance, and debugging. When working with Swift patterns, find the relevant topic below, then read the full reference doc from the base path above.

## Concurrency & Threading

| Topic | Purpose | Reference |
|-------|---------|-----------|
| Swift 6 strict concurrency | Complete data-race safety, migration guide | swift-adoptingswift6.md |
| Sendable protocol | Mark types as safe to share across concurrency domains | swift-sendable.md |
| Actor | Reference type with serialized access to mutable state | swift-actor.md |
| GlobalActor | Apply actor isolation to declarations across files | swift-globalactor.md |
| MainActor | Ensure code runs on the main thread (UI updates) | swift-mainactor.md |
| TaskGroup | Structured concurrency for parallel work | swift-taskgroup.md |
| AsyncSequence | Asynchronous iteration over values over time | swift-asyncsequence.md |
| AsyncStream | Bridge callback/delegate APIs to async/await | swift-asyncstream.md |

### Concurrency Decision Guide

| Scenario | Use | Reference |
|----------|-----|-----------|
| Protect mutable state from data races | Actor | swift-actor.md |
| Ensure UI updates happen on main thread | @MainActor | swift-mainactor.md |
| Pass data between concurrency domains | Sendable | swift-sendable.md |
| Run multiple async tasks in parallel | TaskGroup | swift-taskgroup.md |
| Convert delegate callbacks to async/await | AsyncStream | swift-asyncstream.md |
| Iterate over values arriving over time | AsyncSequence | swift-asyncsequence.md |
| Migrate to Swift 6 complete checking | Adopting Swift 6 guide | swift-adoptingswift6.md |

## Data Serialization

| Topic | Purpose | Reference |
|-------|---------|-----------|
| Codable | Encode/decode to JSON, Plist, and custom formats | swift-codable.md |
| Swift standard library | Arrays, dictionaries, sets, optionals, value types | swift.md |

## Swift Packages

| Topic | Purpose | Reference |
|-------|---------|-----------|
| Swift packages overview | Create, manage, and distribute packages | xcode-swift-packages.md |
| Create a standalone package | Step-by-step package creation with Xcode | xcode-creating-a-standalone-swift-package-with-xcode.md |
| Bundle resources with packages | Include assets, data files, storyboards | xcode-bundling-resources-with-a-swift-package.md |
| Distribute binary frameworks | XCFramework distribution via SPM | xcode-distributing-binary-frameworks-as-swift-packages.md |
| Organize code with local packages | Modularize an app into local packages | xcode-organizing-your-code-with-local-packages.md |
| Identify binary dependencies | Detect and manage binary dependencies | xcode-identifying-binary-dependencies.md |

### Package Decision Guide

| Scenario | Approach | Reference |
|----------|----------|-----------|
| Modularize a monolithic app | Local packages for feature modules | xcode-organizing-your-code-with-local-packages.md |
| Share code between app and extension | Swift package with shared target | xcode-creating-a-standalone-swift-package-with-xcode.md |
| Distribute a closed-source SDK | XCFramework via SPM | xcode-distributing-binary-frameworks-as-swift-packages.md |
| Include non-code assets in a package | Bundle resources | xcode-bundling-resources-with-a-swift-package.md |

## By Engineering Need

### Data Modeling

| Need | Swift Feature | Reference |
|------|--------------|-----------|
| Define model types | struct (value type) or class (reference type) | swift.md |
| Serialize to/from JSON | Codable protocol | swift-codable.md |
| Thread-safe model access | Actor or Sendable | swift-actor.md, swift-sendable.md |
| Async data loading | async/await with TaskGroup | swift-taskgroup.md |

### Performance

| Need | Swift Feature | Reference |
|------|--------------|-----------|
| Avoid data races (Swift 6) | Strict concurrency checking | swift-adoptingswift6.md |
| Parallelize expensive work | TaskGroup | swift-taskgroup.md |
| Stream data efficiently | AsyncSequence / AsyncStream | swift-asyncsequence.md, swift-asyncstream.md |
| Isolate UI work to main thread | @MainActor | swift-mainactor.md |

### Debugging

| Need | Swift Feature | Reference |
|------|--------------|-----------|
| Diagnose concurrency issues | Swift 6 strict checking + Thread Sanitizer | swift-adoptingswift6.md |
| Understand actor isolation errors | Actor, GlobalActor concepts | swift-actor.md, swift-globalactor.md |
| Debug Sendable conformance | Sendable protocol requirements | swift-sendable.md |
