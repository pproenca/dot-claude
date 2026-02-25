# TaskGroup

_Structure_

> Source: https://developer.apple.com/documentation/swift/taskgroup

A group that contains dynamically created child tasks.

```swift
@frozen struct TaskGroup<ChildTaskResult> where ChildTaskResult : Sendable
```

### Overview

To create a task group, call the `withTaskGroup(of:returning:body:)` method.

Don’t use a task group from outside the task where you created it. In most cases, the Swift type system prevents a task group from escaping like that because adding a child task to a task group is a mutating operation, and mutation operations can’t be performed from a concurrent execution context like a child task.

## Structured Concurrency

Structured concurrency is a way to organize your program, and tasks, in such a way that tasks don’t outlive the scope in which they are created. Within a structured task hierarchy, no child task remains running longer than its parent task. This guarantee simplifies reasoning about resource usage, and is a powerful mechanism that you can use to write well-behaved concurrent programs.

A task group is the primary way to create structured concurrency tasks in Swift. Another way of creating structured tasks is an `async let` declaration.

Structured concurrency tasks are often called “child tasks” because of their relationship with their parent task. A child task inherits the parent’s priority, task-local values, and is structured in the sense that its lifetime never exceeds the lifetime of the parent task.

A task group *always* waits for all child tasks to complete before it’s destroyed. Specifically, `with...TaskGroup` APIs don’t return until all the child tasks created in the group’s scope have completed running.

Structured concurrency APIs (including task groups and `async let`), *always* waits for the completion of tasks contained within their scope before returning. Specifically, this means that even if you await a single task result and return it from a `withTaskGroup` function body, the group automatically waits for all the remaining tasks before returning:

```swift
func takeFirst(actions: [@Sendable () -> Int]) async -> Int? {
    await withTaskGroup { group in
        for action in actions {
            group.addTask { action() }
        }

        return await group.next() // return the first action to complete
    } // the group will ALWAYS await the completion of all the actions (!)
}
```

In the above example, even though the code returns the first collected integer from all actions added to the task group, the task group *always*, automatically, waits for the completion of all the resulting tasks.

You can use `group.cancelAll()` to signal cancellation to the remaining in-progress tasks, however this doesn’t interrupt their execution automatically. Rather, the child tasks need to cooperatively react to the cancellation, and return early if that’s possible.

To create unstructured concurrency tasks, you can use `Task.init`, `Task.detached` or `Task.immediate`.

## Task Group Cancellation

You can cancel a task group and all of its child tasks by calling the `cancelAll()` method on the task group, or by canceling the task in which the group is running.

If you call `addTask(name:priority:operation:)` to create a new task in a canceled group, that task is immediately canceled after creation. Alternatively, you can call `addTaskUnlessCancelled(name:priority:operation:)`, which doesn’t create the task if the group has already been canceled. Choosing between these two functions lets you control how to react to cancellation within a group: some child tasks need to run regardless of cancellation, but other tasks are better not even being created when you know they can’t produce useful results.

In nonthrowing task groups the tasks you add to a group with this method are nonthrowing, those tasks can’t respond to cancellation by throwing `CancellationError`. The tasks must handle cancellation in some other way, such as returning the work completed so far, returning an empty result, or returning `nil`. For tasks that need to handle cancellation by throwing an error, use the `withThrowingTaskGroup(of:returning:body:)` method instead.

#### Task execution order

Tasks added to a task group execute concurrently, and may be scheduled in any order.

#### Cancellation behavior

A task group becomes canceled in one of the following ways:

- When [cancelAll()](https://developer.apple.com/documentation/swift/taskgroup/cancelall()) is invoked on it.

- When the [Task](https://developer.apple.com/documentation/swift/task) running this task group is canceled.


Because a `TaskGroup` is a structured concurrency primitive, cancellation is automatically propagated through all of its child-tasks (and their child tasks).

A canceled task group can still keep adding tasks, however they will start being immediately canceled, and might respond accordingly. To avoid adding new tasks to an already canceled task group, use `addTaskUnlessCancelled(name:priority:body:)` rather than the plain `addTask(name:priority:body:)` which adds tasks unconditionally.

For information about the language-level concurrency model that `TaskGroup` is part of, see [Concurrency](https://developer.apple.comhttps://docs.swift.org/swift-book/LanguageGuide/Concurrency.html) in [The Swift Programming Language](https://developer.apple.comhttps://docs.swift.org/swift-book/).

> **Note:** [ThrowingTaskGroup](https://developer.apple.com/documentation/swift/throwingtaskgroup)

> **Note:** [DiscardingTaskGroup](https://developer.apple.com/documentation/swift/discardingtaskgroup)

> **Note:** [ThrowingDiscardingTaskGroup](https://developer.apple.com/documentation/swift/throwingdiscardingtaskgroup)
