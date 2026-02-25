# AsyncSequence

_Protocol_

> Source: https://developer.apple.com/documentation/swift/asyncsequence

A type that provides asynchronous, sequential, iterated access to its elements.

```swift
protocol AsyncSequence<Element, Failure>
```

### Overview

An `AsyncSequence` resembles the `Sequence` type — offering a list of values you can step through one at a time — and adds asynchronicity. An `AsyncSequence` may have all, some, or none of its values available when you first use it. Instead, you use `await` to receive values as they become available.

As with `Sequence`, you typically iterate through an `AsyncSequence` with a `for await`-`in` loop. However, because the caller must potentially wait for values, you use the `await` keyword. The following example shows how to iterate over `Counter`, a custom `AsyncSequence` that produces `Int` values from `1` up to a `howHigh` value:

```swift
for await number in Counter(howHigh: 10) {
    print(number, terminator: " ")
}
// Prints "1 2 3 4 5 6 7 8 9 10 "
```

An `AsyncSequence` doesn’t generate or contain the values; it just defines how you access them. Along with defining the type of values as an associated type called `Element`, the `AsyncSequence` defines a `makeAsyncIterator()` method. This returns an instance of type `AsyncIterator`. Like the standard `IteratorProtocol`, the `AsyncIteratorProtocol` defines a single `next()` method to produce elements. The difference is that the `AsyncIterator` defines its `next()` method as `async`, which requires a caller to wait for the next value with the `await` keyword.

`AsyncSequence` also defines methods for processing the elements you receive, modeled on the operations provided by the basic `Sequence` in the standard library. There are two categories of methods: those that return a single value, and those that return another `AsyncSequence`.

Single-value methods eliminate the need for a `for await`-`in` loop, and instead let you make a single `await` call. For example, the `contains(_:)` method returns a Boolean value that indicates if a given value exists in the `AsyncSequence`. Given the `Counter` sequence from the previous example, you can test for the existence of a sequence member with a one-line call:

```swift
let found = await Counter(howHigh: 10).contains(5) // true
```

Methods that return another `AsyncSequence` return a type specific to the method’s semantics. For example, the `.map(_:)` method returns a `AsyncMapSequence` (or a `AsyncThrowingMapSequence`, if the closure you provide to the `map(_:)` method can throw an error). These returned sequences don’t eagerly await the next member of the sequence, which allows the caller to decide when to start work. Typically, you’ll iterate over these sequences with `for await`-`in`, like the base `AsyncSequence` you started with. In the following example, the `map(_:)` method transforms each `Int` received from a `Counter` sequence into a `String`:

```swift
let stream = Counter(howHigh: 10)
    .map { $0 % 2 == 0 ? "Even" : "Odd" }
for await s in stream {
    print(s, terminator: " ")
}
// Prints "Odd Even Odd Even Odd Even Odd Even Odd Even "
```
