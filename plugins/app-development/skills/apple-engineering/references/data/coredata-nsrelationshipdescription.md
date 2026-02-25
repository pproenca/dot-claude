# NSRelationshipDescription

_Class_

> Source: https://developer.apple.com/documentation/coredata/nsrelationshipdescription

A description of a relationship between two entities.

```swift
class NSRelationshipDescription
```

### Overview

[NSRelationshipDescription](https://developer.apple.com/documentation/coredata/nsrelationshipdescription) provides additional attributes that are specific to modeling a relationship between two entities. For the common attributes of all property types, see [NSPropertyDescription](https://developer.apple.com/documentation/coredata/nspropertydescription).

For example, use this class to define a relationship’s *cardinality* — the number of managed objects the relationship can reference.

- For a to-one relationship, set [maxCount](https://developer.apple.com/documentation/coredata/nsrelationshipdescription/maxcount) to `1`.

- For a to-many relationship, set [maxCount](https://developer.apple.com/documentation/coredata/nsrelationshipdescription/maxcount) to a number greater than `1` to impose an upper limit; otherwise, use `0` to allow an unlimited number of referenced objects.


At runtime, you can modify a relationship description until you associate its owning managed object model with a persistent store coordinator.  If you attempt to modify the model after you associate it, Core Data throws an exception. To modify a model that’s in use, create and modify a copy and then discard any objects that belong to the original model.
