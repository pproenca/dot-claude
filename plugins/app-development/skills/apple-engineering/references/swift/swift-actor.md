# Actor

_Protocol_

> Source: https://developer.apple.com/documentation/swift/actor

Common protocol to which all actors conform.

```swift
protocol Actor : AnyObject, Sendable
```

### Overview

The `Actor` protocol generalizes over all `actor` types. Actor types implicitly conform to this protocol.

#### Actors and SerialExecutors

By default, actors execute tasks on a shared global concurrency thread pool. This pool is shared by all default actors and tasks, unless an actor or task specified a more specific executor requirement.

It is possible to configure an actor to use a specific [SerialExecutor](https://developer.apple.com/documentation/swift/serialexecutor), as well as impact the scheduling of default tasks and actors by using a [TaskExecutor](https://developer.apple.com/documentation/swift/taskexecutor).

> **Note:** [SerialExecutor](https://developer.apple.com/documentation/swift/serialexecutor)

> **Note:** [TaskExecutor](https://developer.apple.com/documentation/swift/taskexecutor)
