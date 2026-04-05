# Adding tags to tests

_Article_

> Source: https://developer.apple.com/documentation/testing/addingtags

Use tags to provide semantic information for organization, filtering, and customizing appearances.

### Overview

A complex package or project may contain hundreds or thousands of tests and suites. Some subset of those tests may share some common facet, such as being *critical* or *flaky*. The testing library includes a type of trait called *tags* that you can add to group and categorize tests.

Tags are different from test suites: test suites impose structure on test functions at the source level, while tags provide semantic information for a test that can be shared with any number of other tests across test suites, source files, and even test targets.

### Add a tag

To add a tag to a test, use the [tags(_:)](https://developer.apple.com/documentation/testing/trait/tags(_:)) trait. This trait takes a sequence of tags as its argument, and those tags are then applied to the corresponding test at runtime. If any tags are applied to a test suite, then all tests in that suite inherit those tags.

The testing library doesn’t assign any semantic meaning to any tags, nor does the presence or absence of tags affect how the testing library runs tests.

Tags themselves are instances of [Tag](https://developer.apple.com/documentation/testing/tag) and expressed as named constants declared as static members of [Tag](https://developer.apple.com/documentation/testing/tag). To declare a named constant tag, use the [Tag()](https://developer.apple.com/documentation/testing/tag()) macro:

```swift
extension Tag {
  @Tag static var legallyRequired: Self
}

@Test("Vendor's license is valid", .tags(.legallyRequired))
func licenseValid() { ... }
```

If two tags with the same name (`legallyRequired` in the above example) are declared in different files, modules, or other contexts, the testing library treats them as equivalent.

If it’s important for a tag to be distinguished from similar tags declared elsewhere in a package or project (or its dependencies), use reverse-DNS naming to create a unique Swift symbol name for your tag:

```swift
extension Tag {
  enum com_example_foodtruck {}
}

extension Tag.com_example_foodtruck {
  @Tag static var extraSpecial: Tag
}

@Test(
  "Extra Special Sauce recipe is secret",
  .tags(.com_example_foodtruck.extraSpecial)
)
func secretSauce() { ... }
```

#### Where tags can be declared

Tags must always be declared as members of [Tag](https://developer.apple.com/documentation/testing/tag) in an extension to that type or in a type nested within [Tag](https://developer.apple.com/documentation/testing/tag). Redeclaring a tag under a second name has no effect and the additional name will not be recognized by the testing library. The following example is unsupported:

```swift
extension Tag {
  @Tag static var legallyRequired: Self // ✅ OK: Declaring a new tag.

  static var requiredByLaw: Self { // ❌ ERROR: This tag name isn't
                                   // recognized at runtime.
    legallyRequired
  }
}
```

If a tag is declared as a named constant outside of an extension to the [Tag](https://developer.apple.com/documentation/testing/tag) type (for example, at the root of a file or in another unrelated type declaration), it cannot be applied to test functions or test suites. The following declarations are unsupported:

```swift
@Tag let needsKetchup: Self // ❌ ERROR: Tags must be declared in an extension
                            // to Tag.
struct Food {
  @Tag var needsMustard: Self // ❌ ERROR: Tags must be declared in an extension
                              // to Tag.
}
```
