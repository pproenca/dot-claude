# NSManagedObjectContext

_Class_

> Source: https://developer.apple.com/documentation/coredata/nsmanagedobjectcontext

An object space to manipulate and track changes to managed objects.

```swift
nonisolated class NSManagedObjectContext
```

### Overview

A context consists of a group of related model objects that represent an internally consistent view of one or more persistent stores. Changes to managed objects remain in memory in the associated context until Core Data saves that context to one or more persistent stores. A single managed object instance exists in one and only one context, but multiple copies of an object can exist in different contexts. Therefore, an object is unique to a particular context.

#### Life cycle management

The context is a powerful object with a central role in the life cycle of managed objects, with responsibilities from life cycle management (including faulting) to validation, inverse relationship handling, and undo/redo. Through a context you can retrieve or “fetch” objects from a persistent store, make changes to those objects, and then either discard the changes or—again through the context—commit them back to the persistent store. The context is responsible for watching for changes in its objects and maintains an undo manager so you can have finer-grained control over undo and redo. You can insert new objects and delete ones you have fetched, and commit these modifications to the persistent store.

All objects fetched from an external store are registered in a context together with a global identifier (an instance of `NSManagedObjectID`) that’s used to uniquely identify each object to the external store.

#### Parent store

Managed object contexts have a parent store from which they retrieve data representing managed objects and through which they commit changes to managed objects.

Prior to OS X v10.7 and iOS v5.0, the parent store is always a persistent store coordinator. In macOS 10.7 and later and iOS v5.0 and later, the parent store may be another managed object context. Ultimately the root of a context’s ancestry must be a persistent store coordinator. The coordinator provides the managed object model and dispatches requests to the various persistent stores containing the data.

If a context’s parent store is another managed object context, fetch and save operations are mediated by the parent context instead of a coordinator. This pattern has a number of usage scenarios, including:

- Performing background operations on a second thread or queue.

- Managing discardable edits, such as in an inspector window or view.


As the first scenario implies, a parent context can service requests from children on different threads. You cannot, therefore, use parent contexts created with the thread confinement type (see [Concurrency](https://developer.apple.com/documentation/coredata/nsmanagedobjectcontext#Concurrency)).

When you save changes in a context, the changes are only committed “one store up.” If you save a child context, changes are pushed to its parent. Changes are not saved to the persistent store until the root context is saved. (A root managed object context is one whose parent context is `nil`.) In addition, a parent does not pull changes from children before it saves. You must save a child context if you want ultimately to commit the changes.

#### Notifications

A context posts notifications at various points—see [NSManagedObjectContextObjectsDidChange](https://developer.apple.com/documentation/Foundation/NSNotification/Name-swift.struct/NSManagedObjectContextObjectsDidChange) for example. Typically, you should register to receive these notifications only from known contexts:

Several system frameworks use Core Data internally. If you register to receive these notifications from all contexts (by passing `nil` as the object parameter to a method such as [addObserver(_:selector:name:object:)](https://developer.apple.com/documentation/Foundation/NotificationCenter/addObserver(_:selector:name:object:))), then you may receive unexpected notifications that are difficult to handle.

#### Concurrency

Core Data uses thread (or serialized queue) confinement to protect managed objects and managed object contexts (see [Core Data Programming Guide](https://developer.apple.comhttps://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/CoreData/index.html#//apple_ref/doc/uid/TP40001075)). A consequence of this is that a context assumes the default owner is the thread or queue that creates it. Don’t, therefore, initialize a context on one thread then pass it to another. Instead, pass a reference to a persistent store coordinator and have the receiving thread or queue create a new context using that. If you use [Operation](https://developer.apple.com/documentation/Foundation/Operation), you must create the context in [main()](https://developer.apple.com/documentation/Foundation/Operation/main()) (for a serial queue) or [start()](https://developer.apple.com/documentation/Foundation/Operation/start()) (for a concurrent queue).

When you create a context you specify the concurrency type with which you’ll use it. When you create a managed object context, you have two options for its thread (queue) association:

- Private: The context creates and manages a private queue.

- Main: The context associates with the main queue and is dependent on the application’s event loop; otherwise, it’s similar to a private context. Use this type for contexts that update view controllers and other user interface elements.


You use contexts using the queue-based concurrency types in conjunction with [perform(_:)](https://developer.apple.com/documentation/coredata/nsmanagedobjectcontext/perform(_:)) and [performAndWait(_:)](https://developer.apple.com/documentation/coredata/nsmanagedobjectcontext/performandwait(_:)-ypye). You group “standard” messages to send to the context within a block to pass to one of these methods. There are two exceptions:

- Setter methods on queue-based managed object contexts are thread-safe. You can invoke these methods directly on any thread.

- If your code executes on the main thread, you can invoke methods on the main queue style contexts directly instead of using the block based API.


[perform(_:)](https://developer.apple.com/documentation/coredata/nsmanagedobjectcontext/perform(_:)) and [performAndWait(_:)](https://developer.apple.com/documentation/coredata/nsmanagedobjectcontext/performandwait(_:)-ypye) ensure the block operations execute on the correct queue for the context. The [perform(_:)](https://developer.apple.com/documentation/coredata/nsmanagedobjectcontext/perform(_:)) method returns immediately and the context executes the block methods on its own thread. With the [performAndWait(_:)](https://developer.apple.com/documentation/coredata/nsmanagedobjectcontext/performandwait(_:)-ypye) method, the context still executes the block methods on its own thread, but the method doesn’t return until the block completes.

It’s important to appreciate that blocks execute as a distinct body of work. As soon as your block ends, anyone else can enqueue another block, undo changes, reset the context, and so on. Thus blocks may be quite large, and typically end by invoking [save()](https://developer.apple.com/documentation/coredata/nsmanagedobjectcontext/save()).

You can also perform other operations, such as:

#### Subclassing notes

You are strongly discouraged from subclassing `NSManagedObjectContext`. The change tracking and undo management mechanisms are highly optimized and hence intricate and delicate. Interposing your own additional logic that might impact [processPendingChanges()](https://developer.apple.com/documentation/coredata/nsmanagedobjectcontext/processpendingchanges()) can have unforeseen consequences. In situations such as store migration, Core Data will create instances of `NSManagedObjectContext` for its own use. Under these circumstances, you cannot rely on any features of your custom subclass. Any `NSManagedObject` subclass must always be fully compatible with `NSManagedObjectContext` (that is, it cannot rely on features of a subclass of `NSManagedObjectContext`).
