# NSEntityDescription

_Class_

> Source: https://developer.apple.com/documentation/coredata/nsentitydescription

A description of a Core Data entity.

```swift
class NSEntityDescription
```

### Overview

Entities are to managed objects what `Class` is to `id`, or — to use a database analogy — what tables are to rows. An instance specifies the entity’s name, its attributes and relationships (as instances of [NSAttributeDescription](https://developer.apple.com/documentation/coredata/nsattributedescription) and [NSRelationshipDescription](https://developer.apple.com/documentation/coredata/nsrelationshipdescription)) and the class that represents it. Instances of that class correspond to entries in the associated persistent store. As a minimum, an entity description requires:

- A name.

- The class name of the corresponding managed object.


If you don’t specify a class name, the framework uses [NSManagedObject](https://developer.apple.com/documentation/coredata/nsmanagedobject).

You define entities in a managed object model (an instance of [NSManagedObjectModel](https://developer.apple.com/documentation/coredata/nsmanagedobjectmodel)) using Xcode’s data modeling tool. Core Data uses `NSEntityDescription` to map entries in the persistent store to managed objects in your app. It’s unlikely you’ll interact with entity descriptions directly unless you’re specifically working with models. `NSEntityDescription` provides a user dictionary for you to store any related, app-specific information.

#### Editing entity descriptions

Entity descriptions are editable until an object graph manager uses them, which allows you to create or modify descriptions dynamically. However, once you associate the description’s managed object model with a persistent store coordinator, you can no longer modify it. The framework enforces this rule at runtime; any attempt to mutate the model, or any of its child objects, after you associate it with a persistent store coordinator results in an exception. If you need to modify a model that’s in use, create a copy of that model, modify it, and then discard the stale model.

If you want to create an entity hierarchy, consider the relevant API. You can only set an entity’s [subentities](https://developer.apple.com/documentation/coredata/nsentitydescription/subentities), not an entity’s super-entity. To set an entity’s super-entity, set an array of subentities on the super entity that includes the desired entity; the entity hierarchy is built top-down.

#### Using entity descriptions in dictionaries

The `copy` method of `NSEntityDescription` returns an entity such that:

```objc
[[entity copy] isEqual:entity] == NO
```

Since [NSDictionary](https://developer.apple.com/documentation/Foundation/NSDictionary) copies its keys and requires that keys both conform to the [NSCopying](https://developer.apple.com/documentation/Foundation/NSCopying) protocol and have a property that `copy` returns an object for where the source and the copy are equal, don’t use entities as keys in a dictionary. Instead, use either the entity’s name as the key or use an [NSMapTable](https://developer.apple.com/documentation/Foundation/NSMapTable) with retain callbacks.

#### Fast enumeration

`NSEntityDescription` implements the [NSFastEnumeration](https://developer.apple.com/documentation/Foundation/NSFastEnumeration) protocol. Use this to enumerate over an entity’s properties, as the following example illustrates.

```objc
NSEntityDescription *anEntity = ...;
for (NSPropertyDescription *property in anEntity) {
    // property is each instance of NSPropertyDescription in anEntity in turn
}
```
