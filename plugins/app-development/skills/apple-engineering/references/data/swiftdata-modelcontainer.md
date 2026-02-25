# ModelContainer

_Class_

> Source: https://developer.apple.com/documentation/swiftdata/modelcontainer

An object that manages an app’s schema and model storage configuration.

```swift
class ModelContainer
```

### Overview

A model container mediates between its associated model contexts and your app’s underlying persistent storage. The container manages all aspects of that storage and ensures it remains in a consistent and usable state. Whenever you run a fetch or call a context’s [save()](https://developer.apple.com/documentation/swiftdata/modelcontext/save()) method, the container performs the actual read or write of the underlying data using information from the schema you provide. This helps safeguard an app’s resources and ensures those operations happen only in an efficient and coordinated manner. Additionally, if your app’s entitlements include CloudKit, the container automatically handles syncing the persisted storage across devices. For more information about syncing model data, see [Syncing model data across a person’s devices](https://developer.apple.com/documentation/swiftdata/syncing-model-data-across-a-persons-devices).

As your app’s schema evolves, the container performs automatic migrations of the persisted model data so it remains consistent with the app’s model classes. If the aggregate changes between two versions of your schema exceed the capabilities of automatic migrations, provide the container with a [SchemaMigrationPlan](https://developer.apple.com/documentation/swiftdata/schemamigrationplan) to participate in those migrations and help ensure they complete successfully.

By default, a model container makes a number of assumptions about how it configures an app’s persistent storage. If you need to customize this behavior, provide the container with one or more instances of [ModelConfiguration](https://developer.apple.com/documentation/swiftdata/modelconfiguration). For example, you may want use a particular app group container or specify that the storage is ephemeral and should exist only in memory.

An app that uses SwiftData requires at least one model container. You create a container using one of the class’s initializers or the corresponding SwiftUI view modifier. Using the view modifier ensures all windows in the modified window group, or all child views of the modified view, access the same model container. Additionally, the view modifier makes an associated model context available in the SwiftUI environment, which the `Query()` macro depends on.

```swift
@main
struct RecipesApp: App {
    var body: some Scene {
        WindowGroup {
            RecipesList()
        }
        .modelContainer(for: Recipe.self)
    }
}

struct RecipesList: View {
    @Query private var recipes: [Recipe]
    
    var body: some View {
        List(recipes) { RecipeRowView($0) }
    }
} 

```
