# Mirroring a Core Data store with CloudKit

_Article_

> Source: https://developer.apple.com/documentation/coredata/mirroring_a_core_data_store_with_cloudkit

Back user interfaces with a local replica of a CloudKit private database.

### Overview

Use Core Data with CloudKit to give users seamless access to the data in your app across all their devices.

Core Data with CloudKit combines the benefits of local persistence with cloud backup and distribution. Core Data provides powerful object graph management features for developing an app with structured data. CloudKit lets users access their data across every device on their iCloud account, while serving as an always-available backup service.

[image: Flow diagram showing a record syncing between CloudKit and three devices: a laptop, an iPad, and an iPhone.]

#### Determine If Your App Is Eligible for Core Data with CloudKit

Apps adopting Core Data can use Core Data with CloudKit as long as the persistent store is an [NSSQLiteStoreType](https://developer.apple.com/documentation/coredata/nssqlitestoretype) store, and the data model is compatible with CloudKit limitations. For example, CloudKit does not support unique constraints, undefined attributes, or required relationships.

Apps using CloudKit cannot use Core Data with CloudKit with existing CloudKit containers. To fully manage all aspects of data mirroring, Core Data owns the CloudKit schema created from the Core Data model. Existing CloudKit containers aren’t compatible with this schema. If your app already uses CloudKit, you can add Core Data with CloudKit when synchronizing a Core Data store with a new container. For more information about working with multiple stores, see [Manage multiple stores](https://developer.apple.com/documentation/coredata/setting-up-core-data-with-cloudkit#Manage-multiple-stores).

For more information about data model requirements, see [Create a Data Model](https://developer.apple.com/documentation/coredata/creating-a-core-data-model-for-cloudkit#Create-a-Data-Model).

#### Set Up Your Development Environment

You need an [Apple Developer Program](https://developer.apple.comhttps://developer.apple.com/programs/) account to access the CloudKit service and your team’s CloudKit containers during development.

You also need an iCloud account to save records to a CloudKit container. Core Data with CloudKit uses a specific record zone in the CloudKit private database, which is accessible only to the current user.

You can run and test Core Data with CloudKit apps using Simulator. You may also test with multiple physical devices logged into the same iCloud account. Connect all devices to a stable wireless internet connection to avoid network problems that could hinder synchronization.

For more information, see [Create an iCloud Account for Development](https://developer.apple.comhttps://developer.apple.com/library/archive/documentation/DataManagement/Conceptual/CloudKitQuickStart/EnablingiCloudandConfiguringCloudKit/EnablingiCloudandConfiguringCloudKit.html#//apple_ref/doc/uid/TP40014987-CH2-SW7).

#### Configure Core Data with CloudKit

Add Core Data with CloudKit to your project as follows:

1. Set up your Xcode project’s capabilities to enable CloudKit, and modify your Core Data stack setup to use [NSPersistentCloudKitContainer](https://developer.apple.com/documentation/coredata/nspersistentcloudkitcontainer). See [Setting Up Core Data with CloudKit](https://developer.apple.com/documentation/coredata/setting-up-core-data-with-cloudkit).

2. Design your Core Data model, and use it to initialize the CloudKit schema. See [Creating a Core Data Model for CloudKit](https://developer.apple.com/documentation/coredata/creating-a-core-data-model-for-cloudkit).

3. Modify your views to incorporate remote store changes at appropriate times. See [Syncing a Core Data Store with CloudKit](https://developer.apple.com/documentation/coredata/syncing-a-core-data-store-with-cloudkit).


Finally, if you are building custom features or writing a web app, discover how to work with the generated CloudKit schema in [Reading CloudKit Records for Core Data](https://developer.apple.com/documentation/coredata/reading-cloudkit-records-for-core-data).
