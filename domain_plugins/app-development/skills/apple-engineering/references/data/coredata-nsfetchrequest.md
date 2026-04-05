# NSFetchRequest

_Class_

> Source: https://developer.apple.com/documentation/coredata/nsfetchrequest

A description of search criteria used to retrieve data from a persistent store.

```swift
class NSFetchRequest<ResultType> where ResultType : NSFetchRequestResult
```

### Overview

An instance of [NSFetchRequest](https://developer.apple.com/documentation/coredata/nsfetchrequest) collects the criteria needed to select and optionally to sort a group of [NSManagedObject](https://developer.apple.comhttps://developer.apple.com/library/archive/releasenotes/Cocoa/CoreDataReleaseNotes/index.html#//apple_ref/doc/uid/TP40006503-SW6) managed objects held in an [NSPersistentStore](https://developer.apple.com/documentation/coredata/nspersistentstore) persistent store. A fetch request contains an [NSEntityDescription](https://developer.apple.com/documentation/coredata/nsentitydescription) or an entity name that specifies which entity to search. It frequently also contains:

- An [NSPredicate](https://developer.apple.com/documentation/Foundation/NSPredicate) predicate that specifies which properties to filter by and the constraints on selection, such as, `“last name begins with a ‘J’”`. If you don’t specify a predicate, then the system fetches all instances of the entity that you specified, subject to other constraints. For more information, see [fetch(_:)](https://developer.apple.com/documentation/coredata/nsmanagedobjectcontext/fetch(_:)-38ys1).

- An array of [NSSortDescriptor](https://developer.apple.com/documentation/Foundation/NSSortDescriptor) sort descriptors that specify how to order the returned objects, such as ascending by last name and then by first name.


You can also specify other aspects of a fetch request:

**[fetchLimit](https://developer.apple.com/documentation/coredata/nsfetchrequest/fetchlimit)**
  The maximum number of objects that a request returns

**[fetchOffset](https://developer.apple.com/documentation/coredata/nsfetchrequest/fetchoffset)**
  The number of objects to skip

**[affectedStores](https://developer.apple.com/documentation/coredata/nsfetchrequest/affectedstores)**
  Which data stores the request accesses

**[resultType](https://developer.apple.com/documentation/coredata/nsfetchrequest/resulttype)**
  Whether the fetch returns managed objects, object IDs, dictionaries, or a count

**[includesPropertyValues](https://developer.apple.com/documentation/coredata/nsfetchrequest/includespropertyvalues) and**
  Whether objects are fully populated with their properties

**[returnsObjectsAsFaults](https://developer.apple.com/documentation/coredata/nsfetchrequest/returnsobjectsasfaults)**
  Whether the objects are faults

**[includesSubentities](https://developer.apple.com/documentation/coredata/nsfetchrequest/includessubentities)**
  Whether the fetch includes subentities of the fetched entity

**[propertiesToFetch](https://developer.apple.com/documentation/coredata/nsfetchrequest/propertiestofetch)**
  Which properties to fetch

**[includesPendingChanges](https://developer.apple.com/documentation/coredata/nsfetchrequest/includespendingchanges)**
  Whether to include unsaved changes

Use [execute()](https://developer.apple.com/documentation/coredata/nsfetchrequest/execute()) to perform the fetch directly on the managed object context that’s associated with the current queue. Or use one of the [NSManagedObjectContext](https://developer.apple.com/documentation/coredata/nsmanagedobjectcontext) methods such as [perform(_:)](https://developer.apple.com/documentation/coredata/nsmanagedobjectcontext/perform(_:)) to execute the fetch.

> **Note:**  When you execute an instance of [NSFetchRequest](https://developer.apple.com/documentation/coredata/nsfetchrequest), it always accesses the underlying persistent stores to retrieve the latest results.

In [SwiftUI](https://developer.apple.com/documentation/SwiftUI), you can use a [FetchRequest](https://developer.apple.com/documentation/SwiftUI/FetchRequest) property wrapper to execute the fetch and assign the results to a property. First, create the request:

```swift
let request: NSFetchRequest = {
    // Create a fetch request.
    let request = ShoppingItem.fetchRequest()
    
    // Limit the maximum number of items that the request returns.
    request.fetchLimit = 100
            
    // Filter the request results, such as to only return unchecked items.
    request.predicate = NSPredicate(format: "isChecked = false")
    
    // Sort the fetched results, such as ascending by name.
    request.sortDescriptors = [NSSortDescriptor(keyPath: \ShoppingItem.name, ascending: true)]

    return request
}()
```

Then use a [FetchRequest](https://developer.apple.com/documentation/SwiftUI/FetchRequest) property wrapper with the request to declare a property that receives the objects that the fetch returns:

```swift
// Use a `FetchRequest` property wrapper to fetch the managed objects
// and assign the result.
@FetchRequest(fetchRequest: request) private var items: FetchedResults<ShoppingItem>
```

> **Tip:**  If you don’t need to specify multiple properties of the fetch, you can avoid creating the fetch request separately and declare it in the property wrapper instead. See [FetchRequest](https://developer.apple.com/documentation/SwiftUI/FetchRequest) for more information.

You often predefine fetch requests in an [NSManagedObjectModel](https://developer.apple.com/documentation/coredata/nsmanagedobjectmodel) managed object model to provide an API to retrieve a stored fetch request by name. Stored fetch requests can include placeholders for variable substitution, and serve as templates for later completion. Fetch request templates allow you to predefine queries with variables to substitute at runtime.
