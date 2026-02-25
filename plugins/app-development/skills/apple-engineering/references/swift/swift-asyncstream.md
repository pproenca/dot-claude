# AsyncStream

_Structure_

> Source: https://developer.apple.com/documentation/swift/asyncstream

An asynchronous sequence generated from a closure that calls a continuation to produce new elements.

```swift
struct AsyncStream<Element>
```

### Overview

`AsyncStream` conforms to `AsyncSequence`, providing a convenient way to create an asynchronous sequence without manually implementing an asynchronous iterator. In particular, an asynchronous stream is well-suited to adapt callback- or delegation-based APIs to participate with `async`-`await`.

You initialize an `AsyncStream` with a closure that receives an `AsyncStream.Continuation`. Produce elements in this closure, then provide them to the stream by calling the continuation’s `yield(_:)` method. When there are no further elements to produce, call the continuation’s `finish()` method. This causes the sequence iterator to produce a `nil`, which terminates the sequence. The continuation conforms to `Sendable`, which permits calling it from concurrent contexts external to the iteration of the `AsyncStream`.

An arbitrary source of elements can produce elements faster than they are consumed by a caller iterating over them. Because of this, `AsyncStream` defines a buffering behavior, allowing the stream to buffer a specific number of oldest or newest elements. By default, the buffer limit is `Int.max`, which means the value is unbounded.

#### Adapting Existing Code to Use Streams

To adapt existing callback code to use `async`-`await`, use the callbacks to provide values to the stream, by using the continuation’s `yield(_:)` method.

Consider a hypothetical `QuakeMonitor` type that provides callers with `Quake` instances every time it detects an earthquake. To receive callbacks, callers set a custom closure as the value of the monitor’s `quakeHandler` property, which the monitor calls back as necessary.

```swift
class QuakeMonitor {
    var quakeHandler: ((Quake) -> Void)?

    func startMonitoring() {…}
    func stopMonitoring() {…}
}
```

To adapt this to use `async`-`await`, extend the `QuakeMonitor` to add a `quakes` property, of type `AsyncStream<Quake>`. In the getter for this property, return an `AsyncStream`, whose `build` closure – called at runtime to create the stream – uses the continuation to perform the following steps:

1. Creates a `QuakeMonitor` instance.

2. Sets the monitor’s `quakeHandler` property to a closure that receives each `Quake` instance and forwards it to the stream by calling the continuation’s `yield(_:)` method.

3. Sets the continuation’s `onTermination` property to a closure that calls `stopMonitoring()` on the monitor.

4. Calls `startMonitoring` on the `QuakeMonitor`.


```swift
extension QuakeMonitor {

    static var quakes: AsyncStream<Quake> {
        AsyncStream { continuation in
            let monitor = QuakeMonitor()
            monitor.quakeHandler = { quake in
                continuation.yield(quake)
            }
            continuation.onTermination = { @Sendable _ in
                 monitor.stopMonitoring()
            }
            monitor.startMonitoring()
        }
    }
}
```

Because the stream is an `AsyncSequence`, the call point can use the `for`-`await`-`in` syntax to process each `Quake` instance as the stream produces it:

```swift
for await quake in QuakeMonitor.quakes {
    print("Quake: \(quake.date)")
}
print("Stream finished.")
```
