# SwiftData

_Framework_

> Source: https://developer.apple.com/documentation/swiftdata

Write your model code declaratively to add managed persistence and efficient model fetching.

### Overview

Combining Core Data’s proven persistence technology and Swift’s modern concurrency features, SwiftData enables you to add persistence to your app quickly, with minimal code and no external dependencies. Using modern language features like macros, SwiftData enables you to write code that is fast, efficient, and safe, enabling you to describe the entire model layer (or object graph) for your app. The framework handles storing the underlying model data, and optionally, syncing that data across multiple devices.

SwiftData has uses beyond persisting locally created content. For example, an app that fetches data from a remote web service might use SwiftData to implement a lightweight caching mechanism and provide limited offline functionality.

[image: A white Swift logo containing ones and zeros on a blueprint-style background.]

SwiftData is unintrusive by design and supplements your app’s existing model classes. Attach the [Model()](https://developer.apple.com/documentation/swiftdata/model()) macro to any model class to make it persistable. Customize the behavior of that model’s properties with the [Attribute(_:originalName:hashModifier:)](https://developer.apple.com/documentation/swiftdata/attribute(_:originalname:hashmodifier:)) and [Relationship(_:deleteRule:minimumModelCount:maximumModelCount:originalName:inverse:hashModifier:)](https://developer.apple.com/documentation/swiftdata/relationship(_:deleterule:minimummodelcount:maximummodelcount:originalname:inverse:hashmodifier:)) macros. Use the [ModelContext](https://developer.apple.com/documentation/swiftdata/modelcontext) class to insert, update, and delete instances of that model, and to write unsaved changes to disk.

To display models in a SwiftUI view, use the [Query()](https://developer.apple.com/documentation/swiftdata/query()) macro and specify a predicate or fetch descriptor. SwiftData performs the fetch when the view appears, and tells SwiftUI about any subsequent changes to the fetched models so the view can update accordingly. You can access the model context in any SwiftUI view using the [modelContext](https://developer.apple.com/documentation/SwiftUI/EnvironmentValues/modelContext) environment value, and specify a particular model container or context for a view with the [modelContainer(_:)](https://developer.apple.com/documentation/SwiftUI/View/modelContainer(_:)) and [modelContext(_:)](https://developer.apple.com/documentation/SwiftUI/View/modelContext(_:)) view modifiers.
