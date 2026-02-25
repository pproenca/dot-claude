# Data Frameworks by Need

> Base path: `references/data/`

Map data requirements to the right Apple persistence framework and API. When analyzing requirements, match needs to approaches below, then read the full reference doc from the base path above.

## Choosing a Framework

| Need | Recommended | Reference |
|------|-------------|-----------|
| Modern Swift-native persistence | SwiftData | swiftdata.md |
| Legacy/complex persistence with full control | Core Data | coredata.md |
| Simple key-value settings | UserDefaults | (built-in, no reference) |
| Lightweight file-based data | Codable + JSON/Plist files | swift-codable.md (in swift/) |

## SwiftData

| Need | Topic | Reference |
|------|-------|-----------|
| Get started with SwiftData persistence | Preserving model data across launches | swiftdata-preserving-your-apps-model-data-across-launches.md |
| Create, update, and save model objects | Adding and editing persistent data | swiftdata-adding-and-editing-persistent-data-in-your-app.md |
| Query with predicates, sort descriptors | Filtering and sorting persistent data | swiftdata-filtering-and-sorting-persistent-data.md |
| Sync with a remote server | Maintaining a local copy of server data | swiftdata-maintaining-a-local-copy-of-server-data.md |
| Remove model objects from the store | Deleting persistent data | swiftdata-deleting-persistent-data-from-your-app.md |
| Sync across devices via CloudKit | Syncing model data across devices | swiftdata-syncing-model-data-across-a-persons-devices.md |
| Configure the persistent store | ModelContainer API | swiftdata-modelcontainer.md |
| Manage object lifecycle and saves | ModelContext API | swiftdata-modelcontext.md |
| Evolve schemas between versions | SchemaMigrationPlan | swiftdata-schemamigrationplan.md |
| Define migration steps | MigrationStage | swiftdata-migrationstage.md |

## Core Data

| Need | Topic | Reference |
|------|-------|-----------|
| Initialize Core Data in your app | Setting up a Core Data stack | coredata-setting_up_a_core_data_stack.md |
| Define entities, attributes, relationships | Creating a Core Data model | coredata-creating_a_core_data_model.md |
| Connect data from multiple stores | Linking data between stores | coredata-linking_data_between_two_core_data_stores.md |
| Complex schema migration with mapping models | Heavyweight migration | coredata-heavyweight_migration.md |
| Sync Core Data with CloudKit | Mirroring a store with CloudKit | coredata-mirroring_a_core_data_store_with_cloudkit.md |

### Core Data APIs

| API | Purpose | Reference |
|-----|---------|-----------|
| NSPersistentContainer | Encapsulates the Core Data stack | coredata-nspersistentcontainer.md |
| NSManagedObject | Base class for all Core Data model objects | coredata-nsmanagedobject.md |
| NSManagedObjectContext | Object space for creating, fetching, saving | coredata-nsmanagedobjectcontext.md |
| NSFetchRequest | Describes search criteria for fetching | coredata-nsfetchrequest.md |
| NSPersistentCloudKitContainer | Container with CloudKit mirroring | coredata-nspersistentcloudkitcontainer.md |
| NSEntityDescription | Describes an entity in the model | coredata-nsentitydescription.md |
| NSRelationshipDescription | Describes a relationship between entities | coredata-nsrelationshipdescription.md |
| NSManagedObjectModel | Collection of entity descriptions | coredata-nsmanagedobjectmodel.md |
| NSPersistentStoreCoordinator | Mediates between contexts and stores | coredata-nspersistentstorecoordinator.md |

## Decision Guide

| Scenario | Use | Why |
|----------|-----|-----|
| New app, Swift-only, simple to moderate relationships | SwiftData | Modern, declarative, less boilerplate |
| New app, complex relationships, advanced queries | SwiftData first, Core Data if needed | Start simple, migrate if you hit limits |
| Existing app with Core Data | Keep Core Data | Migration cost rarely justified |
| Need CloudKit sync | SwiftData or NSPersistentCloudKitContainer | Both support CloudKit natively |
| Shared framework between app and extension | Core Data or SwiftData with App Groups | Configure shared container |
| Simple settings/preferences | UserDefaults | No persistence framework needed |
| Read-only bundled data | Codable JSON file | Load once, no persistence needed |
