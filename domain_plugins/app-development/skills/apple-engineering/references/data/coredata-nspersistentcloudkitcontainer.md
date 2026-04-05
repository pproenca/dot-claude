# NSPersistentCloudKitContainer

_Class_

> Source: https://developer.apple.com/documentation/coredata/nspersistentcloudkitcontainer

A container that encapsulates the Core Data stack in your app, and mirrors select persistent stores to a CloudKit private database.

```swift
class NSPersistentCloudKitContainer
```

### Overview

[NSPersistentCloudKitContainer](https://developer.apple.com/documentation/coredata/nspersistentcloudkitcontainer) is a subclass of [NSPersistentContainer](https://developer.apple.com/documentation/coredata/nspersistentcontainer) capable of managing both CloudKit-backed and noncloud stores.

By default, [NSPersistentCloudKitContainer](https://developer.apple.com/documentation/coredata/nspersistentcloudkitcontainer) contains a single store description, which Core Data assigns to the first CloudKit container identifier in an app’s entitlements. Use [NSPersistentCloudKitContainerOptions](https://developer.apple.com/documentation/coredata/nspersistentcloudkitcontaineroptions) to customize this behavior or create additional store descriptions with backing by different containers.

For more information about setting up multiple stores, see [Setting Up Core Data with CloudKit](https://developer.apple.com/documentation/coredata/setting-up-core-data-with-cloudkit).
