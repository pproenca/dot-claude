# ModelContext

_Class_

> Source: https://developer.apple.com/documentation/swiftdata/modelcontext

An object that enables you to fetch, insert, and delete models, and save any changes to disk.

```swift
class ModelContext
```

### Overview

A model context is central to SwiftData as it’s responsible for managing the entire lifecycle of your persistent models. You use a context to insert new models, track and persist changes to those models, and to delete those models when you no longer need them. A context understands your app’s schema but doesn’t know about any individual models until you tell it to fetch some from the persistent storage or populate it with new models. Afterwards, any changes made to those models exist only in memory until the context implicitly writes them to the persistent storage, or you manually invoke [save()](https://developer.apple.com/documentation/swiftdata/modelcontext/save()). For more information about implicit writes, see [autosaveEnabled](https://developer.apple.com/documentation/swiftdata/modelcontext/autosaveenabled).

If your app’s schema describes relationships between models, you don’t need to manually insert each model into the context when you first create them. Instead, create the graph of related models and insert only the graph’s root model into the context. The context recognizes the hierarchy and automatically handles the insertion of the related models. The same behavior applies even if the graph contains both new and existing models.

A model context depends on a model container for knowledge about your app’s schema and persistent storage. After you attach a container to your app’s window group or view hierarchy, an associated context becomes available in the SwiftUI environment. This context is bound to the main actor and the framework configures the context to implicitly save future model changes. The [Query()](https://developer.apple.com/documentation/swiftdata/query()) macros use the same context to perform their fetches.

```swift
struct LastModifiedView: View {
    @Environment(\.modelContext) private var modelContext

}
```

> **Important:** If you don’t explicitly attach a model container, the environment provides a context bound to an in-memory, schema-less container. Any attempt to insert a model into this context causes the framework to throw an error, and any fetches you run will return empty results.

After you establish access to a model context, use that context’s [insert(_:)](https://developer.apple.com/documentation/swiftdata/modelcontext/insert(_:)) and [delete(_:)](https://developer.apple.com/documentation/swiftdata/modelcontext/delete(_:)) methods to add and remove models. You can also delete several models at once using [delete(model:where:includeSubclasses:)](https://developer.apple.com/documentation/swiftdata/modelcontext/delete(model:where:includesubclasses:)). There isn’t a corresponding method to update a model because the context automatically tracks all changes to its known models. Use the [hasChanges](https://developer.apple.com/documentation/swiftdata/modelcontext/haschanges) property to determine if the context has unsaved changes, and call [rollback()](https://developer.apple.com/documentation/swiftdata/modelcontext/rollback()) to discard any pending inserts and deletes and any restore changed models to their most recent saved state.

Although you fetch models primarily with the `Query()` macro (and its variants), you can use a model context to perform almost identical fetches. For example, use the [fetch(_:)](https://developer.apple.com/documentation/swiftdata/modelcontext/fetch(_:)) and [fetch(_:batchSize:)](https://developer.apple.com/documentation/swiftdata/modelcontext/fetch(_:batchsize:)) methods to retrieve all models of a certain type that match a set of criteria. And use [fetchCount(_:)](https://developer.apple.com/documentation/swiftdata/modelcontext/fetchcount(_:)) to determine the number of models that match some criteria without the overhead of fetching the models themselves. If you need to be able to identify models that match some criteria but don’t require all of the associated data, use [fetchIdentifiers(_:)](https://developer.apple.com/documentation/swiftdata/modelcontext/fetchidentifiers(_:)) and [fetchIdentifiers(_:batchSize:)](https://developer.apple.com/documentation/swiftdata/modelcontext/fetchidentifiers(_:batchsize:)) to retrieve only those models’ persistent identifiers.

A model context posts a [willSave](https://developer.apple.com/documentation/swiftdata/modelcontext/willsave) notification before it attempts a save operation, and a [didSave](https://developer.apple.com/documentation/swiftdata/modelcontext/didsave) notification immediately after that operation succeeds. Subscribe to one, or both, of these notifications if your app needs to be aware of these events. The `didSave` notification provides additional information about any inserted, updated, and deleted models.

```swift
struct LastModifiedView: View {
    @Environment(\.modelContext) private var context
    @State private var lastModified = Date.now
    
    private var didSavePublisher: NotificationCenter.Publisher {
        NotificationCenter.default
            .publisher(for: ModelContext.willSave, object: context)
    }
    
    var body: some View {
        Text(lastModified.formatted(date: .abbreviated, time: .shortened))
            .onReceive(didSavePublisher) { _ in
                lastModified = Date.now
            }
    }
}
```

> **Note:** To avoid receiving unwanted or unexpected notifications, always specify the model context as the `object` parameter when creating a publisher.
