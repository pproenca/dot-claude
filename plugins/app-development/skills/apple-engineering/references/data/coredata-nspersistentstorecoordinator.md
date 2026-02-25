# NSPersistentStoreCoordinator

_Class_

> Source: https://developer.apple.com/documentation/coredata/nspersistentstorecoordinator

An object that enables an app’s contexts and the underlying persistent stores to work together.

```swift
class NSPersistentStoreCoordinator
```

### Overview

A managed object context uses a coordinator to facilitate the persistence of its entities in the coordinator’s registered stores. A context can’t function without a coordinator because it relies on the coordinator’s access to the managed object model. The coordinator presents its registered stores as an aggregate, allowing a context to operate on the union of those stores instead of on each individually. A coordinator performs its work on a private queue and executes that work serially. You can use multiple coordinators if the work requires separate queues.

Use a coordinator to add or remove persistent stores, change the type or location on-disk of those stores, query the metadata of a specific store, defer a store’s migrations, determine whether two objects originate from the same store, and so on.
