# NSManagedObjectModel

_Class_

> Source: https://developer.apple.com/documentation/coredata/nsmanagedobjectmodel

A programmatic representation of the `.xcdatamodeld` file describing your objects.

```swift
class NSManagedObjectModel
```

### Overview

The model contains one or more `NSEntityDescription` objects representing the entities in the schema. Each `NSEntityDescription` object has property description objects (instances of subclasses of [NSPropertyDescription](https://developer.apple.com/documentation/coredata/nspropertydescription)) that represent the properties (or fields) of the entity in the schema. The Core Data framework uses this description in several ways:

- Constraining UI creation in Interface Builder

- Validating attribute and relationship values at runtime

- Mapping between your managed objects and a database or file-based schema for object persistence


A managed object model maintains a mapping between each of its entity objects and a corresponding managed object class for use with the persistent storage mechanisms in the Core Data framework. You can determine the entity for a particular managed object with the `entity` method.

You typically create managed object models using the data modeling tool in Xcode, but it’s possible to build a model programmatically if needed.

#### Loading a model file

Managed object model files are typically stored in a project or a framework. To load a model, you provide an URL to the constructor. Note that loading a model doesn’t have the effect of loading all of its entities.

#### Storing fetch requests

Frequently, you need a collection of objects that share features in common. Sometimes you can define those features (property values) in advance; sometimes you need to be able to supply values at runtime. For example, suppose you want to retrieve all movies owned by Pixar, or retrieve all movies that earned more than an amount specified by the user at runtime.

Fetch requests are often predefined in a managed object model as templates. They allow you to predefine named queries and their parameters in the model. Typically they contain variables that need to be substituted at runtime. `NSManagedObjectModel` provides an API to retrieve a stored fetch request by name, and to perform variable substitution—see [fetchRequestTemplate(forName:)](https://developer.apple.com/documentation/coredata/nsmanagedobjectmodel/fetchrequesttemplate(forname:)) and [fetchRequestFromTemplate(withName:substitutionVariables:)](https://developer.apple.com/documentation/coredata/nsmanagedobjectmodel/fetchrequestfromtemplate(withname:substitutionvariables:)).

You typically define fetch request templates using the Data Model editor in Xcode. You can also create fetch request templates programmatically, and associate them with a model using [setFetchRequestTemplate(_:forName:)](https://developer.apple.com/documentation/coredata/nsmanagedobjectmodel/setfetchrequesttemplate(_:forname:)).

#### Supporting multiple configurations for the same model

You may want to specify different sets of entities for the same model to be used in different situations. For example, suppose certain entities should only be available if a user has administrative privileges. To support this requirement, a model may have more than one configuration. Each configuration is named, and has an associated set of entities. The sets may overlap. You establish configurations programmatically using [setEntities(_:forConfigurationName:)](https://developer.apple.com/documentation/coredata/nsmanagedobjectmodel/setentities(_:forconfigurationname:)) or using the Xcode design tool, and retrieve the entities for a given configuration name using [entities(forConfigurationName:)](https://developer.apple.com/documentation/coredata/nsmanagedobjectmodel/entities(forconfigurationname:)).

#### Changing models

Because a model describes the structure of the data in a persistent store, changing any parts of a model that alters the schema renders it incompatible with (and so unable to open) the stores it previously created. If you change your schema, you therefore need to migrate the data in existing stores to new version (see [Core Data Model Versioning and Data Migration Programming Guide](https://developer.apple.comhttps://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/CoreDataVersioning/Articles/Introduction.html#//apple_ref/doc/uid/TP40004399)). For example, if you add a new entity or a new attribute to an existing entity, you *can’t* open old stores; if you add a validation constraint or set a new default value for an attribute, you *can* open old stores.

#### Editing models at runtime

Managed object models are editable until they are used by an object graph manager (a managed object context or a persistent store coordinator). This allows you to create or modify them dynamically until their first use. However, once a model is being used, it *must not* be changed. This is enforced at runtime—when the object manager first fetches data using a model, the whole of that model becomes uneditable. Any attempt to mutate a model or any of its sub-objects after that point throws an exception. If you need to modify a model that’s in use, create a copy, modify the copy, and then discard the objects with the old model.

#### Enumerating entities with fast enumeration

In macOS 10.5 and later and on iOS, `NSManagedObjectModel` supports the [NSFastEnumeration](https://developer.apple.com/documentation/Foundation/NSFastEnumeration) protocol. You can use this to enumerate over a model’s entities, as illustrated in the following example:

```objc
NSManagedObjectModel *aModel = ...;
for (NSEntityDescription *entity in aModel) {
    // entity is each instance of NSEntityDescription in aModel in turn
}
```
