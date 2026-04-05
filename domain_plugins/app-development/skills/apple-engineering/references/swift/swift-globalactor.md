# GlobalActor

_Protocol_

> Source: https://developer.apple.com/documentation/swift/globalactor

A type that represents a globally-unique actor that can be used to isolate various declarations anywhere in the program.

```swift
protocol GlobalActor
```

### Overview

A type that conforms to the `GlobalActor` protocol and is marked with the `@globalActor` attribute can be used as a custom attribute. Such types are called global actor types, and can be applied to any declaration to specify that such types are isolated to that global actor type. When using such a declaration from another actor (or from nonisolated code), synchronization is performed through the shared actor instance to ensure mutually-exclusive access to the declaration.

### Custom Actor Executors

A global actor uses a custom executor if it needs to customize its execution semantics, for example, by making sure all of its invocations are run on a specific thread or dispatch queue.

This is done the same way as with normal non-global actors, by declaring a [unownedExecutor](https://developer.apple.com/documentation/swift/actor/unownedexecutor) nonisolated property in the [ActorType](https://developer.apple.com/documentation/swift/globalactor/actortype) underlying this global actor.

It is *not* necessary to override the [sharedUnownedExecutor](https://developer.apple.com/documentation/swift/globalactor/sharedunownedexecutor) static property of the global actor, as its default implementation already delegates to the `shared.unownedExecutor`, which is the most reasonable and correct implementation of this protocol requirement.

You can find out more about custom executors, by referring to the [SerialExecutor](https://developer.apple.com/documentation/swift/serialexecutor) protocol’s documentation.

> **Note:** [SerialExecutor](https://developer.apple.com/documentation/swift/serialexecutor)
