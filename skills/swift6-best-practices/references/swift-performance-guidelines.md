# Swift 6 Best Practices

**Version 0.1.0**
Apple Swift Documentation & Swift Evolution
January 2026

> **Note:**
> This document is mainly for agents and LLMs to follow when maintaining,
> generating, or refactoring Swift 6 codebases. Humans
> may also find it useful, but guidance here is optimized for automation
> and consistency by AI-assisted workflows.

---

## Abstract

Comprehensive performance optimization guide for Swift 6 applications, designed for AI agents and LLMs. Contains 48 rules across 8 categories, prioritized by impact from critical (Concurrency & Data-Race Safety, Memory Management) to incremental (Error Handling). Each rule includes detailed explanations, real-world examples comparing incorrect vs. correct implementations, and specific impact metrics to guide automated refactoring and code generation.

---

## Table of Contents

1. [Concurrency & Data-Race Safety](#1-concurrency--data-race-safety) — **CRITICAL**
   - 1.1 [Use @MainActor for UI-Bound Code](#11-use-mainactor-for-ui-bound-code)
   - 1.2 [Conform Types to Sendable](#12-conform-types-to-sendable)
   - 1.3 [Prefer Actors Over Classes with Locks](#13-prefer-actors-over-classes-with-locks)
   - 1.4 [Use nonisolated for Pure Functions](#14-use-nonisolated-for-pure-functions)
   - 1.5 [Handle Closure Isolation Inheritance](#15-handle-closure-isolation-inheritance)
   - 1.6 [Apply @preconcurrency for Legacy Protocols](#16-apply-preconcurrency-for-legacy-protocols)
   - 1.7 [Enable Strict Concurrency Incrementally](#17-enable-strict-concurrency-incrementally)
2. [Memory Management & ARC](#2-memory-management--arc) — **CRITICAL**
   - 2.1 [Use weak self in Escaping Closures](#21-use-weak-self-in-escaping-closures)
   - 2.2 [Prefer unowned When Lifetime is Guaranteed](#22-prefer-unowned-when-lifetime-is-guaranteed)
   - 2.3 [Choose Structs Over Classes for Data](#23-choose-structs-over-classes-for-data)
   - 2.4 [Avoid Strong Self Capture in Long-Lived Closures](#24-avoid-strong-self-capture-in-long-lived-closures)
   - 2.5 [Use autoreleasepool in Tight Loops](#25-use-autoreleasepool-in-tight-loops)
   - 2.6 [Profile Retain Cycles with Instruments](#26-profile-retain-cycles-with-instruments)
3. [Ownership & Noncopyable Types](#3-ownership--noncopyable-types) — **HIGH**
   - 3.1 [Use ~Copyable for Unique Resources](#31-use-copyable-for-unique-resources)
   - 3.2 [Apply consuming for Ownership Transfer](#32-apply-consuming-for-ownership-transfer)
   - 3.3 [Use borrowing for Read-Only Access](#33-use-borrowing-for-read-only-access)
   - 3.4 [Implement deinit for Noncopyable Types](#34-implement-deinit-for-noncopyable-types)
   - 3.5 [Use consume to End Variable Lifetime](#35-use-consume-to-end-variable-lifetime)
4. [Value Types & Copy-on-Write](#4-value-types--copy-on-write) — **MEDIUM-HIGH**
   - 4.1 [Prefer Structs for Simple Data Models](#41-prefer-structs-for-simple-data-models)
   - 4.2 [Implement Copy-on-Write for Large Types](#42-implement-copy-on-write-for-large-types)
   - 4.3 [Use isKnownUniquelyReferenced](#43-use-isknownuniquelyreferenced)
   - 4.4 [Avoid Nested CoW Quadratic Behavior](#44-avoid-nested-cow-quadratic-behavior)
   - 4.5 [Choose Semantics Based on Identity](#45-choose-semantics-based-on-identity)
5. [Collection Performance](#5-collection-performance) — **MEDIUM**
   - 5.1 [Use ContiguousArray for Class Elements](#51-use-contiguousarray-for-class-elements)
   - 5.2 [Prefer Set for Membership Testing](#52-prefer-set-for-membership-testing)
   - 5.3 [Use Dictionary for Key-Value Lookups](#53-use-dictionary-for-key-value-lookups)
   - 5.4 [Reserve Capacity for Known Sizes](#54-reserve-capacity-for-known-sizes)
   - 5.5 [Apply lazy for Chained Transformations](#55-apply-lazy-for-chained-transformations)
   - 5.6 [Consider swift-collections for Specialized Needs](#56-consider-swift-collections-for-specialized-needs)
6. [Async/Await & Structured Concurrency](#6-asyncawait--structured-concurrency) — **MEDIUM**
   - 6.1 [Prefer async let for Fixed Concurrent Operations](#61-prefer-async-let-for-fixed-concurrent-operations)
   - 6.2 [Use TaskGroup with Backpressure](#62-use-taskgroup-with-backpressure)
   - 6.3 [Avoid Spawning Tasks Everywhere](#63-avoid-spawning-tasks-everywhere)
   - 6.4 [Reserve Task.detached for Special Cases](#64-reserve-taskdetached-for-special-cases)
   - 6.5 [Handle Cancellation Properly](#65-handle-cancellation-properly)
   - 6.6 [Replace DispatchGroup with TaskGroup](#66-replace-dispatchgroup-with-taskgroup)
7. [Compiler Optimization](#7-compiler-optimization) — **LOW-MEDIUM**
   - 7.1 [Use @inlinable for Cross-Module Hot Paths](#71-use-inlinable-for-cross-module-hot-paths)
   - 7.2 [Mark Classes final for Devirtualization](#72-mark-classes-final-for-devirtualization)
   - 7.3 [Use @usableFromInline for Internal Helpers](#73-use-usablefrominline-for-internal-helpers)
   - 7.4 [Enable Whole-Module Optimization](#74-enable-whole-module-optimization)
   - 7.5 [Use @frozen for Fixed-Layout Types](#75-use-frozen-for-fixed-layout-types)
   - 7.6 [Avoid Existentials in Hot Paths](#76-avoid-existentials-in-hot-paths)
   - 7.7 [Prefer Concrete Types Over Protocols](#77-prefer-concrete-types-over-protocols)
   - 7.8 [Specialize Generic Functions](#78-specialize-generic-functions)
8. [Error Handling & Type Safety](#8-error-handling--type-safety) — **LOW**
   - 8.1 [Use Typed Throws for Exhaustive Handling](#81-use-typed-throws-for-exhaustive-handling)
   - 8.2 [Prefer Untyped Throws for Evolving Errors](#82-prefer-untyped-throws-for-evolving-errors)
   - 8.3 [Use Typed Throws in Embedded Contexts](#83-use-typed-throws-in-embedded-contexts)
   - 8.4 [Leverage Result for Synchronous Errors](#84-leverage-result-for-synchronous-errors)
   - 8.5 [Avoid Overusing try?](#85-avoid-overusing-try)

---

## 1. Concurrency & Data-Race Safety

**Impact: CRITICAL**

Swift 6 enforces data-race safety at compile time. The compiler performs strict checking to ensure that mutable state is not accessed simultaneously from multiple threads without proper synchronization. This eliminates entire classes of runtime crashes and undefined behavior.

### 1.1 Use @MainActor for UI-Bound Code

All UI updates must occur on the main thread. In Swift 6, annotating types or methods with `@MainActor` ensures the compiler enforces this at compile time.

**Incorrect: UI code without actor isolation**

```swift
class ProfileViewController: UIViewController {
    var userName: String = ""

    func fetchAndDisplayUser() async {
        let user = await userService.fetchUser()
        // Potential data race: accessing userName from background thread
        userName = user.name
        nameLabel.text = userName
    }
}
```

**Correct: @MainActor ensures UI safety**

```swift
@MainActor
class ProfileViewController: UIViewController {
    var userName: String = ""

    func fetchAndDisplayUser() async {
        let user = await userService.fetchUser()
        // Guaranteed to run on main actor
        userName = user.name
        nameLabel.text = userName
    }
}
```

In Swift 6.2 with "approachable concurrency" enabled, new projects default to `@MainActor` isolation, reducing annotation burden.

### 1.2 Conform Types to Sendable

Types passed across isolation boundaries must conform to `Sendable`. This ensures the compiler can verify thread-safe access.

**Incorrect: Non-Sendable type crossing boundaries**

```swift
class UserData {
    var name: String
    var age: Int

    init(name: String, age: Int) {
        self.name = name
        self.age = age
    }
}

func processUser(_ user: UserData) async {
    await Task.detached {
        // Error: UserData is not Sendable
        print(user.name)
    }.value
}
```

**Correct: Use Sendable struct or mark class correctly**

```swift
// Option 1: Use a struct (implicitly Sendable if all properties are)
struct UserData: Sendable {
    let name: String
    let age: Int
}

// Option 2: Final class with immutable properties
final class UserData: Sendable {
    let name: String
    let age: Int

    init(name: String, age: Int) {
        self.name = name
        self.age = age
    }
}

// Option 3: Use @unchecked Sendable with manual synchronization
final class UserData: @unchecked Sendable {
    private let queue = DispatchQueue(label: "userData")
    private var _name: String

    var name: String {
        queue.sync { _name }
    }

    init(name: String, age: Int) {
        self._name = name
        self.age = age
    }
}
```

### 1.3 Prefer Actors Over Classes with Locks

Actors provide built-in isolation without manual synchronization. They eliminate data races by design and produce cleaner code than lock-based approaches.

**Incorrect: Manual synchronization with locks**

```swift
class BankAccount {
    private var balance: Double = 0
    private let lock = NSLock()

    func deposit(_ amount: Double) {
        lock.lock()
        defer { lock.unlock() }
        balance += amount
    }

    func withdraw(_ amount: Double) -> Bool {
        lock.lock()
        defer { lock.unlock() }
        guard balance >= amount else { return false }
        balance -= amount
        return true
    }
}
```

**Correct: Actor with automatic isolation**

```swift
actor BankAccount {
    private var balance: Double = 0

    func deposit(_ amount: Double) {
        balance += amount
    }

    func withdraw(_ amount: Double) -> Bool {
        guard balance >= amount else { return false }
        balance -= amount
        return true
    }
}

// Usage requires await
let account = BankAccount()
await account.deposit(100)
```

Actors eliminate deadlock risks and ensure all access to mutable state is serialized automatically.

### 1.4 Use nonisolated for Pure Functions

Methods that don't access actor state can be marked `nonisolated` to avoid unnecessary async context and improve performance.

**Incorrect: Pure function requires await due to actor isolation**

```swift
actor Calculator {
    private var lastResult: Double = 0

    // Unnecessarily requires await even though it doesn't access state
    func add(_ a: Double, _ b: Double) -> Double {
        return a + b
    }
}
```

**Correct: nonisolated for stateless operations**

```swift
actor Calculator {
    private var lastResult: Double = 0

    nonisolated func add(_ a: Double, _ b: Double) -> Double {
        return a + b
    }

    func addAndStore(_ a: Double, _ b: Double) -> Double {
        lastResult = a + b
        return lastResult
    }
}

// Usage: no await needed for nonisolated
let calc = Calculator()
let sum = calc.add(1, 2)  // Synchronous!
let stored = await calc.addAndStore(3, 4)  // Requires await
```

### 1.5 Handle Closure Isolation Inheritance

Closures inherit isolation from their enclosing context. When frameworks call closures from background threads, explicit handling is required.

**Incorrect: Closure assumes main actor context**

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

**Correct: Explicitly dispatch to main actor**

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

### 1.6 Apply @preconcurrency for Legacy Protocols

When conforming to delegate protocols that assume main actor context, use `@preconcurrency` to bridge the gap.

**Incorrect: Delegate methods without isolation handling**

```swift
@MainActor
class MyViewController: UIViewController, UITableViewDelegate {
    var selectedItems: [Item] = []

    // Warning: Protocol method may be called from any thread
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        selectedItems.append(items[indexPath.row])
    }
}
```

**Correct: @preconcurrency assumes main actor**

```swift
@MainActor
class MyViewController: UIViewController, @preconcurrency UITableViewDelegate {
    var selectedItems: [Item] = []

    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        // @preconcurrency assumes this is called on the main actor
        // Will trap at runtime if called from wrong context
        selectedItems.append(items[indexPath.row])
    }
}
```

### 1.7 Enable Strict Concurrency Incrementally

Migrate to Swift 6 concurrency module-by-module to avoid overwhelming changes.

**Incorrect: Attempting full migration at once**

```swift
// Enabling Swift 6 mode across entire large codebase
// Results in thousands of errors, migration becomes intractable
```

**Correct: Incremental migration strategy**

```swift
// Step 1: Enable warnings in Swift 5 mode per-module
// In build settings: Other Swift Flags = -strict-concurrency=complete

// Step 2: Fix warnings module by module, starting with leaf modules

// Step 3: Once a module is clean, switch it to Swift 6 language mode

// Step 4: Use @preconcurrency imports for dependencies not yet migrated
@preconcurrency import LegacyModule
```

Migration often requires 100+ annotations per large module. Plan accordingly.

---

## 2. Memory Management & ARC

**Impact: CRITICAL**

Automatic Reference Counting introduces overhead on every retain/release. Retain cycles cause memory leaks that accumulate over time, leading to app termination. Proper memory management is essential for app stability and performance.

### 2.1 Use weak self in Escaping Closures

Closures capture references strongly by default. Use `[weak self]` to prevent retain cycles.

**Incorrect: Strong capture creates retain cycle**

```swift
class NetworkManager {
    var onDataReceived: ((Data) -> Void)?

    func startListening() {
        onDataReceived = { data in
            // Strong capture: self -> onDataReceived -> closure -> self
            self.processData(data)
        }
    }

    func processData(_ data: Data) { }
}
```

**Correct: Weak capture breaks the cycle**

```swift
class NetworkManager {
    var onDataReceived: ((Data) -> Void)?

    func startListening() {
        onDataReceived = { [weak self] data in
            guard let self else { return }
            self.processData(data)
        }
    }

    func processData(_ data: Data) { }
}
```

### 2.2 Prefer unowned When Lifetime is Guaranteed

`unowned` has less overhead than `weak` (no side table, no optional unwrapping) when you can guarantee the referenced object outlives the closure.

**Incorrect: Using weak when unowned is safe**

```swift
class Parent {
    var child: Child?

    func setupChild() {
        child = Child()
        child?.onAction = { [weak self] in
            // Child cannot outlive parent, weak adds unnecessary overhead
            self?.handleAction()
        }
    }
}
```

**Correct: unowned for guaranteed lifetime**

```swift
class Parent {
    var child: Child?

    func setupChild() {
        child = Child()
        child?.onAction = { [unowned self] in
            // Parent always exists when child exists
            // No optional, no side table overhead
            self.handleAction()
        }
    }
}
```

**Warning:** Using `unowned` when the object can be deallocated causes a crash. Only use when lifetime is absolutely guaranteed.

### 2.3 Choose Structs Over Classes for Data

Structs avoid ARC overhead entirely. They're stack-allocated (when possible) and have no reference counting.

**Incorrect: Class for simple data**

```swift
class Point {
    var x: Double
    var y: Double

    init(x: Double, y: Double) {
        self.x = x
        self.y = y
    }
}

// Every assignment increments/decrements reference count
let p1 = Point(x: 0, y: 0)
let p2 = p1  // retain
// p1 and p2 share the same instance
```

**Correct: Struct for value semantics**

```swift
struct Point {
    var x: Double
    var y: Double
}

// No reference counting, copied by value
let p1 = Point(x: 0, y: 0)
var p2 = p1  // Copy, no ARC
p2.x = 10    // Only p2 is modified
```

Industry research shows struct-heavy designs can achieve 20% lower peak memory allocations.

### 2.4 Avoid Strong Self Capture in Long-Lived Closures

Closures stored for long periods (timers, observers, notification handlers) are especially prone to retain cycles.

**Incorrect: Timer holds strong reference indefinitely**

```swift
class PollingService {
    var timer: Timer?

    func startPolling() {
        timer = Timer.scheduledTimer(withTimeInterval: 5, repeats: true) { _ in
            // Strong capture: PollingService can never be deallocated
            self.poll()
        }
    }

    func poll() { }
}
```

**Correct: Weak capture allows deallocation**

```swift
class PollingService {
    var timer: Timer?

    func startPolling() {
        timer = Timer.scheduledTimer(withTimeInterval: 5, repeats: true) { [weak self] _ in
            self?.poll()
        }
    }

    func stopPolling() {
        timer?.invalidate()
        timer = nil
    }

    func poll() { }

    deinit {
        stopPolling()
    }
}
```

### 2.5 Use autoreleasepool in Tight Loops

When working with Objective-C objects in tight loops, autoreleasepool prevents memory from accumulating.

**Incorrect: Memory builds up during loop**

```swift
func processImages(_ urls: [URL]) {
    for url in urls {
        // Autoreleased objects accumulate until loop ends
        let image = UIImage(contentsOfFile: url.path)
        processImage(image)
    }
    // All memory released here, could cause memory pressure
}
```

**Correct: autoreleasepool drains each iteration**

```swift
func processImages(_ urls: [URL]) {
    for url in urls {
        autoreleasepool {
            let image = UIImage(contentsOfFile: url.path)
            processImage(image)
        }
        // Memory released immediately
    }
}
```

### 2.6 Profile Retain Cycles with Instruments

Use Instruments' Leaks and Allocations tools to identify retain cycles that static analysis misses.

**Correct: Regular profiling workflow**

```swift
// 1. Run with Leaks instrument
// 2. Exercise app features that create/destroy objects
// 3. Check for objects with unexpected lifetime
// 4. Use Memory Graph Debugger for cycle visualization

// Debug-only retain cycle detection
#if DEBUG
class LeakDetector {
    static var instances: Set<ObjectIdentifier> = []

    static func track(_ object: AnyObject) {
        instances.insert(ObjectIdentifier(object))
    }

    static func assertAllDeallocated() {
        assert(instances.isEmpty, "Potential retain cycle detected")
    }
}
#endif
```

---

## 3. Ownership & Noncopyable Types

**Impact: HIGH**

Swift's ownership system enables zero-copy resource management. Noncopyable types (`~Copyable`) guarantee unique ownership, preventing use-after-free bugs at compile time and enabling efficient resource handling.

### 3.1 Use ~Copyable for Unique Resources

File handles, database connections, and locks should have unique ownership to prevent double-close bugs.

**Incorrect: Copyable resource can be used after transfer**

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

**Correct: ~Copyable prevents copies**

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

### 3.2 Apply consuming for Ownership Transfer

Use `consuming` when a function takes permanent ownership of a value.

**Incorrect: Implicit ownership unclear**

```swift
struct UniqueBuffer: ~Copyable {
    var data: UnsafeMutableBufferPointer<UInt8>

    // Does this function take ownership or just borrow?
    func process(_ buffer: UniqueBuffer) {
        // ...
    }
}
```

**Correct: Explicit consuming ownership**

```swift
struct UniqueBuffer: ~Copyable {
    var data: UnsafeMutableBufferPointer<UInt8>

    deinit {
        data.deallocate()
    }
}

// Ownership is transferred to the function
func process(_ buffer: consuming UniqueBuffer) {
    // buffer is consumed, will be deinitialized after use
    print(buffer.data.count)
}

// Caller cannot use buffer after passing
let buffer = UniqueBuffer(data: .allocate(capacity: 1024))
process(buffer)
// print(buffer.data.count)  // Error: 'buffer' used after consume
```

### 3.3 Use borrowing for Read-Only Access

Use `borrowing` for temporary read access without ownership transfer.

**Incorrect: Unnecessary ownership transfer**

```swift
struct LargeData: ~Copyable {
    var bytes: [UInt8]
}

// Taking ownership when only reading
func checksum(_ data: consuming LargeData) -> UInt32 {
    var sum: UInt32 = 0
    for byte in data.bytes {
        sum = sum &+ UInt32(byte)
    }
    return sum
}
```

**Correct: Borrowing for read-only access**

```swift
struct LargeData: ~Copyable {
    var bytes: [UInt8]
}

// Borrowing: read access, no ownership change
func checksum(_ data: borrowing LargeData) -> UInt32 {
    var sum: UInt32 = 0
    for byte in data.bytes {
        sum = sum &+ UInt32(byte)
    }
    return sum
}

// Caller retains ownership
var data = LargeData(bytes: Array(0..<1000))
let cs = checksum(data)
print(data.bytes.count)  // Still valid
```

### 3.4 Implement deinit for Noncopyable Types

Noncopyable types should clean up resources in `deinit` to ensure cleanup even on error paths.

**Incorrect: Manual cleanup can be missed**

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

**Correct: deinit ensures cleanup**

```swift
struct DatabaseConnection: ~Copyable {
    var handle: OpaquePointer?

    deinit {
        sqlite3_close(handle)
    }

    consuming func close() {
        // Explicit close is now optional but immediate
        sqlite3_close(handle)
        discard self  // Prevent deinit from running
    }
}

func query() throws {
    let conn = DatabaseConnection(handle: openDB())
    try performQuery(conn)
    // deinit called automatically, even on throw
}
```

### 3.5 Use consume to End Variable Lifetime

The `consume` operator explicitly ends a variable's lifetime, enabling optimizations.

**Incorrect: Variable lifetime extends unnecessarily**

```swift
func processBuffer(_ buffer: consuming [UInt8]) {
    let result = transform(buffer)
    // buffer still "alive" even though we're done with it
    // memory not freed until function returns
    expensiveOperation(result)
}
```

**Correct: consume ends lifetime early**

```swift
func processBuffer(_ buffer: consuming [UInt8]) {
    let result = transform(consume buffer)
    // buffer memory freed immediately after transform
    expensiveOperation(result)  // Less memory pressure
}
```

---

## 4. Value Types & Copy-on-Write

**Impact: MEDIUM-HIGH**

Structs provide value semantics but naive implementations copy data on every mutation. Copy-on-write (CoW) gives value semantics with reference-type performance for large data structures.

### 4.1 Prefer Structs for Simple Data Models

Structs are stack-allocated (when possible), have no reference counting, and provide automatic thread safety through value semantics.

**Incorrect: Class for simple data**

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
```

**Correct: Struct for data models**

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
```

### 4.2 Implement Copy-on-Write for Large Types

For structs with large data, wrap storage in a class to enable CoW semantics.

**Incorrect: Struct copies all data on mutation**

```swift
struct LargeBuffer {
    var bytes: [UInt8]  // Already has CoW via Array
    var metadata: [String: Any]  // Also has CoW
    var customData: (UInt64, UInt64, UInt64, UInt64)  // Copied entirely
}

// But for custom storage:
struct Image {
    var width: Int
    var height: Int
    var pixels: UnsafeMutablePointer<UInt32>
    // Copied by value - pointer shared, double-free risk!
}
```

**Correct: CoW wrapper for custom storage**

```swift
struct Image {
    private final class Storage {
        var width: Int
        var height: Int
        var pixels: UnsafeMutablePointer<UInt32>

        init(width: Int, height: Int) {
            self.width = width
            self.height = height
            self.pixels = .allocate(capacity: width * height)
        }

        func copy() -> Storage {
            let new = Storage(width: width, height: height)
            new.pixels.update(from: pixels, count: width * height)
            return new
        }

        deinit {
            pixels.deallocate()
        }
    }

    private var storage: Storage

    var width: Int { storage.width }
    var height: Int { storage.height }

    mutating func setPixel(x: Int, y: Int, color: UInt32) {
        ensureUnique()
        storage.pixels[y * width + x] = color
    }

    private mutating func ensureUnique() {
        if !isKnownUniquelyReferenced(&storage) {
            storage = storage.copy()
        }
    }
}
```

### 4.3 Use isKnownUniquelyReferenced

`isKnownUniquelyReferenced` is the key function for efficient CoW - it checks if copying is necessary.

**Incorrect: Always copy on mutation**

```swift
struct Buffer {
    private class Storage {
        var data: [UInt8]
        init(_ data: [UInt8]) { self.data = data }
    }

    private var storage: Storage

    mutating func append(_ byte: UInt8) {
        // Always copies - defeats CoW purpose
        storage = Storage(storage.data + [byte])
    }
}
```

**Correct: Copy only when shared**

```swift
struct Buffer {
    private final class Storage {
        var data: [UInt8]
        init(_ data: [UInt8]) { self.data = data }
    }

    private var storage: Storage

    mutating func append(_ byte: UInt8) {
        if !isKnownUniquelyReferenced(&storage) {
            storage = Storage(storage.data)
        }
        storage.data.append(byte)
    }
}
```

### 4.4 Avoid Nested CoW Quadratic Behavior

Modifying CoW collections inside loops can cause O(n²) behavior if each iteration triggers a copy.

**Incorrect: Quadratic copying in loop**

```swift
var items = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

for i in items.indices {
    items[i].append(0)  // Each append may copy the entire nested array
}
```

**Correct: Minimize CoW triggers**

```swift
// Option 1: Use inout to maintain unique reference
var items = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

for i in items.indices {
    var inner = items[i]  // Take ownership
    inner.append(0)
    items[i] = inner
}

// Option 2: Build new structure
let items = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
let result = items.map { $0 + [0] }
```

### 4.5 Choose Semantics Based on Identity

Use classes when identity matters (the specific instance), structs when value matters (the data).

**Incorrect: Struct for identity-based entity**

```swift
struct Window {
    var title: String
    var frame: CGRect

    func close() {
        // Which window? Copies don't share identity
    }
}
```

**Correct: Class for identity, struct for data**

```swift
// Identity matters - use class
class Window {
    var title: String
    var frame: CGRect

    func close() {
        // This specific window instance
    }
}

// Value matters - use struct
struct WindowConfiguration {
    var title: String
    var frame: CGRect
}

let config = WindowConfiguration(title: "Settings", frame: .zero)
let window = Window(configuration: config)
```

---

## 5. Collection Performance

**Impact: MEDIUM**

Collection choice significantly affects performance. Using the right collection type for the access pattern can provide 2-10x improvements.

### 5.1 Use ContiguousArray for Class Elements

`ContiguousArray` stores elements in contiguous memory, avoiding NSArray bridging overhead for class types.

**Incorrect: Array with class elements may bridge**

```swift
class Node {
    var value: Int
    var children: [Node] = []

    init(value: Int) { self.value = value }
}

// Array<Node> may use NSArray internally
var nodes: [Node] = []
for i in 0..<1000 {
    nodes.append(Node(value: i))
}
```

**Correct: ContiguousArray guarantees layout**

```swift
class Node {
    var value: Int
    var children: ContiguousArray<Node> = []

    init(value: Int) { self.value = value }
}

// ContiguousArray always uses contiguous storage
var nodes: ContiguousArray<Node> = []
nodes.reserveCapacity(1000)
for i in 0..<1000 {
    nodes.append(Node(value: i))
}
```

Up to 2x performance improvement for reference type elements.

### 5.2 Prefer Set for Membership Testing

Sets provide O(1) membership testing vs O(n) for Array.contains.

**Incorrect: Array.contains for membership**

```swift
let validUserIds = Array(0..<10000)

func isValidUser(_ id: Int) -> Bool {
    return validUserIds.contains(id)  // O(n) - scans entire array
}
```

**Correct: Set for O(1) lookup**

```swift
let validUserIds = Set(0..<10000)

func isValidUser(_ id: Int) -> Bool {
    return validUserIds.contains(id)  // O(1) - hash lookup
}
```

### 5.3 Use Dictionary for Key-Value Lookups

Dictionary provides O(1) access, avoiding linear searches.

**Incorrect: Array of tuples for lookup**

```swift
let userAges: [(name: String, age: Int)] = [
    ("Alice", 30),
    ("Bob", 25),
    ("Charlie", 35)
]

func getAge(for name: String) -> Int? {
    return userAges.first { $0.name == name }?.age  // O(n)
}
```

**Correct: Dictionary for key-based access**

```swift
let userAges: [String: Int] = [
    "Alice": 30,
    "Bob": 25,
    "Charlie": 35
]

func getAge(for name: String) -> Int? {
    return userAges[name]  // O(1)
}
```

### 5.4 Reserve Capacity for Known Sizes

Pre-allocating avoids repeated reallocations during growth.

**Incorrect: Repeated reallocations**

```swift
var results: [ProcessedItem] = []

for item in largeDataSet {  // 10,000 items
    let processed = process(item)
    results.append(processed)  // May reallocate multiple times
}
```

**Correct: Reserve capacity upfront**

```swift
var results: [ProcessedItem] = []
results.reserveCapacity(largeDataSet.count)

for item in largeDataSet {
    let processed = process(item)
    results.append(processed)  // No reallocation needed
}
```

### 5.5 Apply lazy for Chained Transformations

Lazy sequences avoid intermediate array allocations.

**Incorrect: Eager evaluation creates temporaries**

```swift
let numbers = Array(0..<10000)

let result = numbers
    .filter { $0 % 2 == 0 }  // Creates [Int] with 5000 elements
    .map { $0 * 2 }          // Creates [Int] with 5000 elements
    .prefix(10)              // Creates [Int] with 10 elements
```

**Correct: Lazy evaluation avoids allocations**

```swift
let numbers = Array(0..<10000)

let result = numbers.lazy
    .filter { $0 % 2 == 0 }  // LazyFilterSequence - no allocation
    .map { $0 * 2 }          // LazyMapSequence - no allocation
    .prefix(10)              // Stops after 10 elements

// Only when consumed:
let array = Array(result)  // Creates single [Int] with 10 elements
```

### 5.6 Consider swift-collections for Specialized Needs

The swift-collections package provides optimized data structures.

**Use cases for swift-collections:**

```swift
import Collections

// OrderedSet: Set with insertion order preserved
let orderedSet: OrderedSet = [3, 1, 4, 1, 5]  // [3, 1, 4, 5]

// OrderedDictionary: Dictionary with insertion order
let orderedDict: OrderedDictionary = ["b": 2, "a": 1, "c": 3]

// Deque: Double-ended queue with O(1) operations at both ends
var deque: Deque = [1, 2, 3]
deque.prepend(0)     // O(1)
deque.append(4)      // O(1)
deque.popFirst()     // O(1)
deque.popLast()      // O(1)

// TreeDictionary/TreeSet: Persistent collections with structural sharing
// Excellent for immutable data structures with frequent updates
let tree1: TreeDictionary = ["a": 1, "b": 2]
let tree2 = tree1.merging(["c": 3]) { $1 }  // Shares structure with tree1
```

---

## 6. Async/Await & Structured Concurrency

**Impact: MEDIUM**

Structured concurrency ensures tasks have proper lifetimes, automatic cancellation propagation, and controlled resource usage. Misuse leads to resource leaks and performance issues.

### 6.1 Prefer async let for Fixed Concurrent Operations

When running a known number of concurrent operations, `async let` is cleaner than TaskGroup.

**Incorrect: TaskGroup for fixed operations**

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

**Correct: async let for clarity**

```swift
func fetchUserData(id: Int) async throws -> (User, Posts, Friends) {
    async let user = fetchUser(id)
    async let posts = fetchPosts(id)
    async let friends = fetchFriends(id)

    return try await (user, posts, friends)
}
```

### 6.2 Use TaskGroup with Backpressure

Control concurrency to avoid overwhelming resources.

**Incorrect: Unbounded parallelism**

```swift
func processAllImages(_ urls: [URL]) async throws -> [ProcessedImage] {
    try await withThrowingTaskGroup(of: ProcessedImage.self) { group in
        for url in urls {
            group.addTask {
                try await self.downloadAndProcess(url)
            }
        }
        // All 10,000 downloads start simultaneously!
        return try await group.reduce(into: []) { $0.append($1) }
    }
}
```

**Correct: Controlled parallelism with backpressure**

```swift
func processAllImages(_ urls: [URL]) async throws -> [ProcessedImage] {
    try await withThrowingTaskGroup(of: ProcessedImage.self) { group in
        var results: [ProcessedImage] = []
        var iterator = urls.makeIterator()
        let maxConcurrent = 4

        // Start initial batch
        for _ in 0..<min(maxConcurrent, urls.count) {
            if let url = iterator.next() {
                group.addTask { try await self.downloadAndProcess(url) }
            }
        }

        // As each completes, start another
        for try await result in group {
            results.append(result)
            if let url = iterator.next() {
                group.addTask { try await self.downloadAndProcess(url) }
            }
        }

        return results
    }
}
```

### 6.3 Avoid Spawning Tasks Everywhere

Unstructured tasks (`Task { }`) break structured concurrency and complicate resource management.

**Incorrect: Tasks scattered throughout code**

```swift
class DataManager {
    func updateData() {
        Task {
            let data = await fetchData()
            Task {
                await processData(data)
                Task {
                    await saveData(data)
                }
            }
        }
    }
}
```

**Correct: Structured async flow**

```swift
class DataManager {
    func updateData() async {
        let data = await fetchData()
        await processData(data)
        await saveData(data)
    }

    // Single entry point for unstructured context
    func triggerUpdate() {
        Task {
            await updateData()
        }
    }
}
```

### 6.4 Reserve Task.detached for Special Cases

`Task.detached` creates tasks without inheriting actor context or priority. Use only when specifically needed.

**Incorrect: Task.detached by default**

```swift
@MainActor
class ViewController {
    func processInBackground() {
        Task.detached {
            // Loses @MainActor context
            // Have to manually return to main actor
            let result = await self.compute()
            await MainActor.run {
                self.display(result)
            }
        }
    }
}
```

**Correct: Regular Task inherits context**

```swift
@MainActor
class ViewController {
    func processInBackground() {
        Task {
            // Inherits @MainActor
            let result = await compute()
            display(result)  // Already on main actor
        }
    }

    // Task.detached only when you need different priority
    // or want to explicitly escape actor context
    func lowPriorityBackgroundWork() {
        Task.detached(priority: .background) {
            await self.heavyComputation()
        }
    }
}
```

### 6.5 Handle Cancellation Properly

Check for cancellation in long-running tasks to respect structured concurrency.

**Incorrect: Ignoring cancellation**

```swift
func processLargeDataset(_ items: [Item]) async throws -> [Result] {
    var results: [Result] = []
    for item in items {  // 1 million items
        let result = await process(item)
        results.append(result)
    }
    return results
}
```

**Correct: Cooperative cancellation**

```swift
func processLargeDataset(_ items: [Item]) async throws -> [Result] {
    var results: [Result] = []
    for item in items {
        try Task.checkCancellation()  // Throws if cancelled
        let result = await process(item)
        results.append(result)
    }
    return results
}

// Or with cleanup
func processWithCleanup(_ items: [Item]) async throws -> [Result] {
    var results: [Result] = []
    for item in items {
        if Task.isCancelled {
            // Perform cleanup before exiting
            await cleanup(results)
            throw CancellationError()
        }
        results.append(await process(item))
    }
    return results
}
```

### 6.6 Replace DispatchGroup with TaskGroup

TaskGroup provides the same functionality with better cancellation support and type safety.

**Incorrect: DispatchGroup with async code**

```swift
func fetchAllData() async -> [Data] {
    let group = DispatchGroup()
    var results: [Data] = []
    let lock = NSLock()

    for url in urls {
        group.enter()
        Task {
            let data = try? await fetch(url)
            lock.lock()
            if let data { results.append(data) }
            lock.unlock()
            group.leave()
        }
    }

    group.wait()
    return results
}
```

**Correct: TaskGroup is native to async**

```swift
func fetchAllData() async -> [Data] {
    await withTaskGroup(of: Data?.self) { group in
        for url in urls {
            group.addTask {
                try? await fetch(url)
            }
        }

        var results: [Data] = []
        for await data in group {
            if let data { results.append(data) }
        }
        return results
    }
}
```

---

## 7. Compiler Optimization

**Impact: LOW-MEDIUM**

Compiler optimizations can significantly improve performance, especially for library code. However, they often have tradeoffs with binary size and API evolution.

### 7.1 Use @inlinable for Cross-Module Hot Paths

`@inlinable` exposes function implementation, enabling cross-module optimization.

**Incorrect: Internal implementation hidden**

```swift
// In MyLibrary module
public struct Vector {
    public var x, y, z: Double

    public func dot(_ other: Vector) -> Double {
        return x * other.x + y * other.y + z * other.z
    }
}

// In client code - function call overhead for every dot()
```

**Correct: @inlinable enables inlining**

```swift
// In MyLibrary module
public struct Vector {
    public var x, y, z: Double

    @inlinable
    public func dot(_ other: Vector) -> Double {
        return x * other.x + y * other.y + z * other.z
    }
}

// In client code - dot() can be inlined, no function call
```

**Warning:** Changes to `@inlinable` functions require client recompilation for effect.

### 7.2 Mark Classes final for Devirtualization

`final` enables static dispatch instead of virtual dispatch through vtable.

**Incorrect: Open for subclassing unnecessarily**

```swift
class Parser {
    func parse(_ input: String) -> AST {
        // Virtual dispatch: lookup in vtable
        return parseImplementation(input)
    }

    func parseImplementation(_ input: String) -> AST {
        // ...
    }
}
```

**Correct: final enables static dispatch**

```swift
final class Parser {
    func parse(_ input: String) -> AST {
        // Direct function call, no vtable lookup
        return parseImplementation(input)
    }

    func parseImplementation(_ input: String) -> AST {
        // ...
    }
}
```

### 7.3 Use @usableFromInline for Internal Helpers

When `@inlinable` functions call internal helpers, mark those helpers `@usableFromInline`.

**Incorrect: @inlinable can't call internal**

```swift
public struct Buffer {
    @inlinable
    public func process() -> Data {
        // Error: validateInput() is internal
        if validateInput() {
            return transform()
        }
        return Data()
    }

    func validateInput() -> Bool { true }
    func transform() -> Data { Data() }
}
```

**Correct: @usableFromInline exposes for inlining**

```swift
public struct Buffer {
    @inlinable
    public func process() -> Data {
        if validateInput() {
            return transform()
        }
        return Data()
    }

    @usableFromInline
    func validateInput() -> Bool { true }

    @usableFromInline
    func transform() -> Data { Data() }
}
```

### 7.4 Enable Whole-Module Optimization

WMO enables cross-file optimizations within a module.

**Build Settings:**

```
// Debug: Incremental for fast builds
SWIFT_COMPILATION_MODE = singlefile

// Release: WMO for optimized builds
SWIFT_COMPILATION_MODE = wholemodule
SWIFT_OPTIMIZATION_LEVEL = -O
```

Benefits:
- Functions can be inlined across files
- Unused code can be eliminated
- Generics can be specialized

### 7.5 Use @frozen for Fixed-Layout Types

`@frozen` promises the type's layout won't change, enabling more aggressive optimization.

**Incorrect: Library type may change**

```swift
// Library code - caller must handle layout changes
public struct Point {
    public var x: Double
    public var y: Double
}
```

**Correct: @frozen guarantees layout**

```swift
// Library code - layout is fixed forever
@frozen
public struct Point {
    public var x: Double
    public var y: Double
}

// Benefits:
// - Direct field access instead of accessor calls
// - Size known at compile time
// - Can be stack allocated by clients
```

**Warning:** Once `@frozen`, you cannot add/remove/reorder stored properties.

### 7.6 Avoid Existentials in Hot Paths

Existential types (`any Protocol`) require heap allocation and dynamic dispatch.

**Incorrect: Existential in tight loop**

```swift
protocol Processor {
    func process(_ value: Int) -> Int
}

func processAll(_ items: [Int], processor: any Processor) -> [Int] {
    return items.map { processor.process($0) }  // Dynamic dispatch per item
}
```

**Correct: Generic for static dispatch**

```swift
protocol Processor {
    func process(_ value: Int) -> Int
}

func processAll<P: Processor>(_ items: [Int], processor: P) -> [Int] {
    return items.map { processor.process($0) }  // Static dispatch, can inline
}
```

### 7.7 Prefer Concrete Types Over Protocols

When the concrete type is known, use it directly for better optimization.

**Incorrect: Protocol type hides concrete type**

```swift
func computeSum(_ numbers: any Sequence<Int>) -> Int {
    return numbers.reduce(0, +)  // Existential overhead
}
```

**Correct: Concrete type when known**

```swift
func computeSum(_ numbers: [Int]) -> Int {
    return numbers.reduce(0, +)  // Optimized for Array
}

// Or use generics when flexibility needed
func computeSum<S: Sequence>(_ numbers: S) -> Int where S.Element == Int {
    return numbers.reduce(0, +)  // Specializable
}
```

### 7.8 Specialize Generic Functions

Generic functions can be specialized for specific types with `@_specialize`.

**Correct: Hint for specialization**

```swift
@_specialize(where T == Int)
@_specialize(where T == Double)
func sum<T: Numeric>(_ array: [T]) -> T {
    return array.reduce(0, +)
}

// Compiler will generate optimized versions for Int and Double
```

Note: `@_specialize` is not officially supported and may change.

---

## 8. Error Handling & Type Safety

**Impact: LOW**

Swift 6 introduces typed throws, enabling exhaustive error handling without existential overhead. Choose the right approach based on your use case.

### 8.1 Use Typed Throws for Exhaustive Handling

Typed throws allow switch-based error handling with compiler-verified exhaustiveness.

**Incorrect: Untyped throws requires catch-all**

```swift
enum ParseError: Error {
    case invalidSyntax
    case unexpectedEOF
}

func parse(_ input: String) throws -> AST {
    // throws any Error
}

do {
    let ast = try parse(input)
} catch let error as ParseError {
    // Handle known errors
} catch {
    // Must have catch-all for unknown errors
}
```

**Correct: Typed throws for exhaustive handling**

```swift
enum ParseError: Error {
    case invalidSyntax
    case unexpectedEOF
}

func parse(_ input: String) throws(ParseError) -> AST {
    // Only throws ParseError
}

do {
    let ast = try parse(input)
} catch .invalidSyntax {
    // Handle syntax error
} catch .unexpectedEOF {
    // Handle EOF
}
// No catch-all needed - compiler knows all cases handled
```

### 8.2 Prefer Untyped Throws for Evolving Errors

When error cases might change, untyped throws avoids breaking changes.

**Incorrect: Typed throws for evolving API**

```swift
// v1.0
func fetchUser() throws(NetworkError) -> User

// v1.1 - Breaking change! Callers must handle new case
enum NetworkError: Error {
    case noConnection
    case timeout
    case serverError  // Added in v1.1
}
```

**Correct: Untyped throws for API stability**

```swift
// Error type can evolve without breaking callers
func fetchUser() throws -> User

// Or use typed throws with @unknown default
do {
    try fetchUser()
} catch let error as NetworkError {
    switch error {
    case .noConnection: // ...
    case .timeout: // ...
    @unknown default: // Handle future cases
    }
} catch {
    // Other errors
}
```

### 8.3 Use Typed Throws in Embedded Contexts

Typed throws eliminates existential boxing overhead, important for embedded Swift.

**Correct: Typed throws for embedded systems**

```swift
// Embedded Swift - no runtime, minimal overhead
enum GPIOError: Error {
    case invalidPin
    case alreadyInUse
}

func configureGPIO(pin: Int) throws(GPIOError) {
    guard pin >= 0 && pin < 40 else {
        throw .invalidPin
    }
    // ...
}
```

### 8.4 Leverage Result for Synchronous Errors

`Result` is useful for synchronous code that needs explicit error handling.

**Incorrect: Throwing in callback context**

```swift
func validate(_ input: String, completion: (String?, Error?) -> Void) {
    if input.isEmpty {
        completion(nil, ValidationError.empty)
    } else {
        completion(input.uppercased(), nil)
    }
}
```

**Correct: Result for explicit success/failure**

```swift
func validate(_ input: String) -> Result<String, ValidationError> {
    if input.isEmpty {
        return .failure(.empty)
    }
    return .success(input.uppercased())
}

// Usage
switch validate(input) {
case .success(let value):
    print(value)
case .failure(let error):
    handleError(error)
}
```

### 8.5 Avoid Overusing try?

`try?` discards error information, making debugging harder.

**Incorrect: Discarding error information**

```swift
func processFile(_ path: String) {
    guard let data = try? Data(contentsOf: URL(fileURLWithPath: path)) else {
        print("Failed to read file")  // Why did it fail?
        return
    }
    // ...
}
```

**Correct: Preserve error for debugging**

```swift
func processFile(_ path: String) {
    do {
        let data = try Data(contentsOf: URL(fileURLWithPath: path))
        // ...
    } catch {
        print("Failed to read file: \(error)")  // Includes reason
        // Log error for debugging
        logger.error("File read failed", error: error)
    }
}

// try? is OK when error truly doesn't matter
let cachedValue = try? loadFromCache()  // Fallback is acceptable
```

---

## References

1. [Apple Swift Documentation - Adopting Swift 6](https://developer.apple.com/documentation/swift/adoptingswift6)
2. [Swift Evolution Proposals](https://github.com/swiftlang/swift-evolution)
3. [WWDC24 - Explore Swift Performance](https://developer.apple.com/videos/play/wwdc2024/10217/)
4. [WWDC24 - Migrate your app to Swift 6](https://developer.apple.com/videos/play/wwdc2024/10169/)
5. [Swift.org - Enabling Complete Concurrency Checking](https://www.swift.org/documentation/concurrency/)
