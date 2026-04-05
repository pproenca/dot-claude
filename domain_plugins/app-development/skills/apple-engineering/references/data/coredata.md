# Core Data

_Framework_

> Source: https://developer.apple.com/documentation/coredata

Persist or cache data on a single device, or sync data to multiple devices with CloudKit.

### Overview

Use Core Data to save your application’s permanent data for offline use, to cache temporary data, and to add undo functionality to your app on a single device. To sync data across multiple devices in a single iCloud account, Core Data automatically mirrors your schema to a CloudKit container.

Through Core Data’s Data Model editor, you define your data’s types and relationships, and generate respective class definitions. Core Data can then manage object instances at runtime to provide the following features.

#### Persistence

Core Data abstracts the details of mapping your objects to a store, making it easy to save data from Swift and Objective-C without administering a database directly.

[image: Flow diagram showing an app saving data to and loading data from a persistent store.]

#### Undo and redo of individual and batched changes

Core Data’s undo manager tracks changes and can roll them back individually, in groups, or all at once, making it easy to add undo and redo support to your app.

[image: Figure showing a shake to undo gesture causing an element to be removed from a list.]

#### Background data tasks

Perform potentially UI-blocking data tasks, like parsing JSON into objects, in the background. You can then cache or store the results to reduce server roundtrips.

[image: Flow diagram showing data from an endpoint populating objects in the background before updating the UI.]

#### View synchronization

Core Data also helps keep your views and data synchronized by providing data sources for table and collection views.

#### Versioning and migration

Core Data includes mechanisms for versioning your data model and migrating user data as your app evolves.
