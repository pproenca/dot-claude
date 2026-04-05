# NSManagedObject

_Class_

> Source: https://developer.apple.com/documentation/coredata/nsmanagedobject

The base class that all Core Data model objects inherit from.

```swift
nonisolated class NSManagedObject
```

### Overview

A managed object has an associated entity description ([NSEntityDescription](https://developer.apple.com/documentation/coredata/nsentitydescription)) that provides metadata about the object, including the name of the entity that the object represents and the names of its attributes and relationships. A managed object also has an associated managed object context that tracks changes to the object graph.

You can’t use instances of direct subclasses of [NSObject](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class), or any other class that doesn’t inherit from [NSManagedObject](https://developer.apple.com/documentation/coredata/nsmanagedobject), with a managed object context. You may create custom subclasses of [NSManagedObject](https://developer.apple.com/documentation/coredata/nsmanagedobject), although this isn’t always necessary. If you don’t need custom logic, you can create a complete object graph with [NSManagedObject](https://developer.apple.com/documentation/coredata/nsmanagedobject) instances.

If you instantiate a managed object directly, you must call the designated initializer [init(entity:insertInto:)](https://developer.apple.com/documentation/coredata/nsmanagedobject/init(entity:insertinto:)).

#### Data Storage

In some respects, an `NSManagedObject` acts like a dictionary—it’s a generic container object that provides efficient storage for the properties defined by its associated `NSEntityDescription` instance. `NSManagedObject` supports a range of common types for attribute values, including string, date, and number (see [NSAttributeDescription](https://developer.apple.com/documentation/coredata/nsattributedescription) for full details). Therefore, typically you don’t need to define instance variables in subclasses. Sometimes, however, you want to use types that aren’t supported directly, such as colors and C structures. For example, in a graphics application you might want to define a Rectangle entity that has color and bounds attributes that are an instance of `NSColor` and an `NSRect` struct, respectively. For some types you can use a transformable attribute, for others this may require you to create a subclass of `NSManagedObject`.

> **Note:** The default value for [automaticallyNotifiesObservers(forKey:)](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class/automaticallyNotifiesObservers(forKey:)) is `false` for managed properties of a `NSManagedObject`, and `true` for unmanaged properties.

#### Faulting

Managed objects typically represent data held in a persistent store. In some situations a managed object may be a *fault*—an object whose property values haven’t yet been loaded from the external data store. When you access persistent property values, the fault “fires” and the data is retrieved from the store automatically. This can be a comparatively expensive process (potentially requiring a round trip to the persistent store), and you may wish to avoid unnecessarily firing a fault. See [Faulting and Uniquing](https://developer.apple.comhttps://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/CoreData/FaultingandUniquing.html#//apple_ref/doc/uid/TP40001075-CH18) for more details on faults.

You can safely invoke the following methods and properties on a fault without causing it to fire: [isEqual(_:)](https://developer.apple.com/documentation/ObjectiveC/NSObjectProtocol/isEqual(_:)), [hash](https://developer.apple.com/documentation/ObjectiveC/NSObjectProtocol/hash), [superclass](https://developer.apple.com/documentation/ObjectiveC/NSObjectProtocol/superclass), [class](https://developer.apple.com/documentation/ObjectiveC/NSObject-c.protocol/class), [self()](https://developer.apple.com/documentation/ObjectiveC/NSObjectProtocol/self()), [isProxy()](https://developer.apple.com/documentation/ObjectiveC/NSObjectProtocol/isProxy()), [isKind(of:)](https://developer.apple.com/documentation/ObjectiveC/NSObjectProtocol/isKind(of:)), [isMember(of:)](https://developer.apple.com/documentation/ObjectiveC/NSObjectProtocol/isMember(of:)), [conforms(to:)](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class/conforms(to:)), [responds(to:)](https://developer.apple.com/documentation/ObjectiveC/NSObjectProtocol/responds(to:)), [description](https://developer.apple.com/documentation/ObjectiveC/NSObjectProtocol/description), [managedObjectContext](https://developer.apple.com/documentation/coredata/nsmanagedobject/managedobjectcontext), [entity](https://developer.apple.com/documentation/coredata/nsmanagedobject/entity-swift.property), [objectID](https://developer.apple.com/documentation/coredata/nsmanagedobject/objectid), [isInserted](https://developer.apple.com/documentation/coredata/nsmanagedobject/isinserted), [isUpdated](https://developer.apple.com/documentation/coredata/nsmanagedobject/isupdated), [isDeleted](https://developer.apple.com/documentation/coredata/nsmanagedobject/isdeleted), [faultingState](https://developer.apple.com/documentation/coredata/nsmanagedobject/faultingstate), and [isFault](https://developer.apple.com/documentation/coredata/nsmanagedobject/isfault). Because `isEqual` and `hash` don’t cause a fault to fire, managed objects can typically be placed in collections without firing a fault. Note, however, that invoking key-value coding methods on the collection object might in turn result in an invocation of `valueForKey:` on a managed object, which would fire the fault.

Although the `description` property doesn’t cause a fault to fire, if you implement a custom `description` that accesses the object’s persistent properties, this does cause a fault to fire. You are strongly discouraged from overriding `description` in this way.

#### Subclassing Notes

In combination with the entity description in the managed object model, `NSManagedObject` provides a rich set of default behaviors including support for arbitrary properties and value validation. If you decide to subclass `NSManagedObject` to implement custom features, make sure you don’t disrupt Core Data’s behavior.

##### Methods and Properties You Must Not Override

`NSManagedObject` itself customizes many features of `NSObject` so that managed objects can be properly integrated into the Core Data infrastructure. Core Data relies on the `NSManagedObject` implementation of the following methods and properties, which you therefore absolutely must not override: [primitiveValue(forKey:)](https://developer.apple.com/documentation/coredata/nsmanagedobject/primitivevalue(forkey:)), [setPrimitiveValue(_:forKey:)](https://developer.apple.com/documentation/coredata/nsmanagedobject/setprimitivevalue(_:forkey:)), [isEqual(_:)](https://developer.apple.com/documentation/ObjectiveC/NSObjectProtocol/isEqual(_:)), [hash](https://developer.apple.com/documentation/ObjectiveC/NSObjectProtocol/hash), [superclass](https://developer.apple.com/documentation/ObjectiveC/NSObjectProtocol/superclass), [class](https://developer.apple.com/documentation/ObjectiveC/NSObject-c.protocol/class), [self()](https://developer.apple.com/documentation/ObjectiveC/NSObjectProtocol/self()), [isProxy()](https://developer.apple.com/documentation/ObjectiveC/NSObjectProtocol/isProxy()), [isKind(of:)](https://developer.apple.com/documentation/ObjectiveC/NSObjectProtocol/isKind(of:)), [isMember(of:)](https://developer.apple.com/documentation/ObjectiveC/NSObjectProtocol/isMember(of:)), [conforms(to:)](https://developer.apple.com/documentation/ObjectiveC/NSObjectProtocol/conforms(to:)), [responds(to:)](https://developer.apple.com/documentation/ObjectiveC/NSObjectProtocol/responds(to:)), [managedObjectContext](https://developer.apple.com/documentation/coredata/nsmanagedobject/managedobjectcontext), [entity](https://developer.apple.com/documentation/coredata/nsmanagedobject/entity-swift.property), [objectID](https://developer.apple.com/documentation/coredata/nsmanagedobject/objectid), [isInserted](https://developer.apple.com/documentation/coredata/nsmanagedobject/isinserted), [isUpdated](https://developer.apple.com/documentation/coredata/nsmanagedobject/isupdated), [isDeleted](https://developer.apple.com/documentation/coredata/nsmanagedobject/isdeleted), and [isFault](https://developer.apple.com/documentation/coredata/nsmanagedobject/isfault), [alloc](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class/alloc), [allocWithZone:](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class/allocWithZone:), [new](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class/new),  [instancesRespond(to:)](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class/instancesRespond(to:)), [instanceMethod(for:)](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class/instanceMethod(for:)), [method(for:)](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class/method(for:)), [methodSignatureForSelector:](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class/methodSignatureForSelector:), [instanceMethodSignatureForSelector:](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class/instanceMethodSignatureForSelector:), or [isSubclass(of:)](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class/isSubclass(of:)).

##### Methods and Properties You Shouldn’t Override

As with any class, you are strongly discouraged from overriding the key-value observing methods such as [willChangeValue(forKey:)](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class/willChangeValue(forKey:)) and [didChangeValue(forKey:withSetMutation:using:)](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class/didChangeValue(forKey:withSetMutation:using:)). Avoid overriding `description`—if this method fires a fault during a debugging operation, the results may be unpredictable. Also avoid overriding [init(entity:insertInto:)](https://developer.apple.com/documentation/coredata/nsmanagedobject/init(entity:insertinto:)), or `dealloc`. Changing values in the [init(entity:insertInto:)](https://developer.apple.com/documentation/coredata/nsmanagedobject/init(entity:insertinto:)) method won’t be noticed by the context, and if you aren’t careful, those changes may not be saved. Perform most initialization customization in one of the `awake…` methods. If you do override [init(entity:insertInto:)](https://developer.apple.com/documentation/coredata/nsmanagedobject/init(entity:insertinto:)), make sure you adhere to the requirements set out in the method description. See [init(entity:insertInto:)](https://developer.apple.com/documentation/coredata/nsmanagedobject/init(entity:insertinto:)).

Don’t override `dealloc` because [didTurnIntoFault()](https://developer.apple.com/documentation/coredata/nsmanagedobject/didturnintofault()) is usually a better time to clear values—a managed object may not be reclaimed for some time after it has been turned into a fault. Core Data doesn’t guarantee that `dealloc` will be called in all scenarios (such as when the application quits). Therefore, don’t include required side effects (like saving or changes to the file system, user preferences, and so on) in these methods.

In summary, for [init(entity:insertInto:)](https://developer.apple.com/documentation/coredata/nsmanagedobject/init(entity:insertinto:)) and `dealloc`, Core Data reserves exclusive control over the life cycle of the managed object (that is, raw memory management). This is so that the framework can provide features such as uniquing and by consequence, relationship maintenance, as well as much better performance than would be possible otherwise.

##### Additional Override Considerations

The following methods are intended to be fine grained and aren’t suitable for large-scale operations. Don’t fetch or save in these methods. In particular, they shouldn’t have side effects on the managed object context.

- [init(entity:insertInto:)](https://developer.apple.com/documentation/coredata/nsmanagedobject/init(entity:insertinto:))

- [didTurnIntoFault()](https://developer.apple.com/documentation/coredata/nsmanagedobject/didturnintofault())

- [willTurnIntoFault()](https://developer.apple.com/documentation/coredata/nsmanagedobject/willturnintofault())

- `dealloc`


In addition, if you plan to override `awakeFromInsert`, `awakeFromFetch`, and validation methods, first invoke `super.method()`, the superclass’s implementation. Don’t modify relationships in [awakeFromFetch()](https://developer.apple.com/documentation/coredata/nsmanagedobject/awakefromfetch())—see the method description for details.

##### Custom Accessor Methods

Typically, you don’t need to write custom accessor methods for properties that are defined in the entity of a managed object’s corresponding managed object model. If you need to do so, follow the implementation patterns described in Managed Object Accessor Methods in [Core Data Programming Guide](https://developer.apple.comhttps://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/CoreData/index.html#//apple_ref/doc/uid/TP40001075).

Core Data automatically generates accessor methods (and primitive accessor methods) for you. For attributes and to-one relationships, Core Data generates the standard get and set accessor methods; for to-many relationships, Core Data generates the indexed accessor methods as described in [Achieving Basic Key-Value Coding Compliance](https://developer.apple.comhttps://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/KeyValueCoding/AccessorConventions.html#//apple_ref/doc/uid/20002174) in [Key-Value Coding Programming Guide](https://developer.apple.comhttps://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/KeyValueCoding/index.html#//apple_ref/doc/uid/10000107i). You do however need to declare the accessor methods or use Objective-C properties to suppress compiler warnings. For a full discussion, see Managed Object Accessor Methods in [Core Data Programming Guide](https://developer.apple.comhttps://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/CoreData/index.html#//apple_ref/doc/uid/TP40001075).

##### Custom Instance Variables

By default, `NSManagedObject` stores its properties in an internal structure as objects, and in general Core Data is more efficient working with storage under its own control rather than by using custom instance variables.

`NSManagedObject` provides support for a range of common types for attribute values, including string, date, and number (see [NSAttributeDescription](https://developer.apple.com/documentation/coredata/nsattributedescription) for full details). If you want to use types that aren’t supported directly, like colors and C structures, you can either use transformable attributes or create a subclass of `NSManagedObject`.

Sometimes it’s convenient to represent variables as scalars—in drawing applications, for example, where variables represent dimensions and x and y coordinates and are frequently used in calculations. To represent attributes as scalars, you declare instance variables as you do in any other class. You also need to implement suitable accessor methods as described in Managed Object Accessor Methods.

If you define custom instance variables for example to store derived attributes or other transient properties, clean up these variables in [didTurnIntoFault()](https://developer.apple.com/documentation/coredata/nsmanagedobject/didturnintofault()) rather than `dealloc`.

##### Validation Methods

`NSManagedObject` provides consistent hooks for validating property and inter-property values. You typically shouldn’t override [validateValue(_:forKey:)](https://developer.apple.com/documentation/coredata/nsmanagedobject/validatevalue(_:forkey:)). Instead implement methods of the form `validate<Key>:error:`, as defined by the NSKeyValueCoding protocol. If you want to validate inter-property values, you can override [validateForUpdate()](https://developer.apple.com/documentation/coredata/nsmanagedobject/validateforupdate()) and/or related validation methods.

Don’t call `validateValue:forKey:error:` within custom property validation methods—if you do, you create an infinite loop when `validateValue:forKey:error:` is invoked at runtime. If you do implement custom validation methods, don’t call them directly. Instead, call `validateValue:forKey:error:` with the appropriate key. This ensures that any constraints defined in the managed object model are applied.

If you implement custom inter-property validation methods like [validateForUpdate()](https://developer.apple.com/documentation/coredata/nsmanagedobject/validateforupdate()), call the superclass’s implementation first. This ensures that individual property validation methods are also invoked. If there are multiple validation failures in one operation, collect them in an array and add the array—using the key `NSDetailedErrorsKey`—to the userInfo dictionary in the `NSError` object you return. For an example, see Managed Object Validation.
