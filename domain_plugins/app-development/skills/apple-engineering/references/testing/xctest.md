# XCTest

_Framework_

> Source: https://developer.apple.com/documentation/xctest

Create and run unit tests, performance tests, and UI tests for your Xcode project.

### Overview

Use the XCTest framework to write unit tests for your Xcode projects that integrate seamlessly with Xcode’s testing workflow.

Tests assert that certain conditions are satisfied during code execution, and record test failures (with optional messages) if those conditions aren’t satisfied. Tests can also measure the performance of blocks of code to check for performance regressions. Use XCTest in combination with [XCUIAutomation](https://developer.apple.com/documentation/XCUIAutomation) to interact with an application’s UI and validate user interaction flows. For more information, see [Recording UI automation for testing](https://developer.apple.com/documentation/XCUIAutomation/recording-ui-automation-for-testing).

> **Tip:**  Xcode 16 and later includes Swift Testing, a framework for writing unit tests that takes advantage of the powerful capabilities of the Swift programming language. Consider using Swift Testing for new unit test development and migrating existing tests as described in [Migrating a test from XCTest](https://developer.apple.com/documentation/Testing/MigratingFromXCTest). A test target can contain tests using both Swift Testing and XCTest, however don’t mix API from the two frameworks in the same test. Continue to use XCTest for user interface tests and [Performance Tests](https://developer.apple.com/documentation/xctest/performance-tests).
