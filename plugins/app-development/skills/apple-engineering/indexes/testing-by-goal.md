# Testing by Goal

> Base path: `references/testing/`

Map testing goals to Swift Testing and XCTest patterns. When planning tests, match your goal to an approach below, then read the full reference doc from the base path above.

## Choosing a Framework

| Scenario | Recommended | Reference |
|----------|-------------|-----------|
| New tests for Swift code | Swift Testing | testing.md |
| Existing XCTest suite | Keep XCTest, migrate incrementally | testing-migratingfromxctest.md |
| UI tests | XCTest (XCUITest) | xctest.md |
| Performance tests | XCTest (XCTMetric) | xctest-performance_tests.md |
| Both in same project | Supported — Swift Testing + XCTest coexist | testing-migratingfromxctest.md |

## Swift Testing

| Goal | Topic | Reference |
|------|-------|-----------|
| Write your first test | Defining tests with @Test | testing-definingtests.md |
| Group tests into logical suites | Organizing tests with @Suite | testing-organizingtests.md |
| Test with multiple input values | Parameterized testing | testing-parameterizedtesting.md |
| Migrate from XCTest to Swift Testing | Migration guide and equivalents | testing-migratingfromxctest.md |
| Categorize and filter tests with tags | Adding tags to tests | testing-addingtags.md |
| Swift Testing framework overview | Framework capabilities and macros | testing.md |

### Swift Testing Quick Reference

| XCTest | Swift Testing | Notes |
|--------|--------------|-------|
| `class FooTests: XCTestCase` | `@Suite struct FooTests` | Structs, not classes |
| `func testBar()` | `@Test func bar()` | No "test" prefix needed |
| `XCTAssertEqual(a, b)` | `#expect(a == b)` | Expression-based |
| `XCTAssertThrowsError` | `#expect(throws:)` | Cleaner error testing |
| `XCTAssertNil(x)` | `#expect(x == nil)` | Standard expressions |
| `XCTUnwrap(x)` | `try #require(x)` | Unwrap or fail |
| `setUpWithError()` | `init()` | Standard initializer |
| `tearDown()` | `deinit` | Standard deinitializer |

## XCTest

| Goal | Topic | Reference |
|------|-------|-----------|
| XCTest framework overview | Classes, assertions, lifecycle | xctest.md |
| Measure performance in tests | Performance tests with XCTMetric | xctest-performance_tests.md |

### Performance Test Patterns

| What to Measure | XCTMetric | Reference |
|----------------|-----------|-----------|
| App launch time | XCTApplicationLaunchMetric | xctest-performance_tests.md |
| Scroll smoothness | XCTOSSignpostMetric.scrollDecelerationMetric | xctest-performance_tests.md |
| Disk write volume | XCTStorageMetric | xctest-performance_tests.md |
| Memory usage | XCTMemoryMetric | xctest-performance_tests.md |
| CPU time | XCTCPUMetric | xctest-performance_tests.md |
| Wall clock time | XCTClockMetric | xctest-performance_tests.md |

## By Testing Goal

### Unit Testing

| Goal | Approach | Reference |
|------|----------|-----------|
| Test a pure function | @Test with #expect | testing-definingtests.md |
| Test with multiple inputs | @Test(arguments:) | testing-parameterizedtesting.md |
| Test error conditions | #expect(throws:) | testing-definingtests.md |
| Test async code | async @Test | testing-definingtests.md |
| Group related tests | @Suite | testing-organizingtests.md |
| Tag tests for filtering | .tags(.critical) | testing-addingtags.md |

### Data Layer Testing

| Goal | Approach | Reference |
|------|----------|-----------|
| Test SwiftData model CRUD | In-memory ModelContainer | swiftdata-modelcontainer.md (in data/) |
| Test Core Data model CRUD | In-memory NSPersistentContainer | coredata-nspersistentcontainer.md (in data/) |
| Test fetch request predicates | Create test data, verify predicate results | testing-parameterizedtesting.md |
| Test migration correctness | Load old store, migrate, verify data | swiftdata-schemamigrationplan.md (in data/) |
| Test CloudKit sync | NSPersistentCloudKitContainer test setup | coredata-nspersistentcloudkitcontainer.md (in data/) |

### Performance Testing

| Goal | Approach | Reference |
|------|----------|-----------|
| Catch launch time regressions | measure(metrics: [XCTApplicationLaunchMetric()]) | xctest-performance_tests.md |
| Catch scroll regressions | measure(metrics: [XCTOSSignpostMetric.scrollDecelerationMetric]) | xctest-performance_tests.md |
| Catch disk write regressions | measure(metrics: [XCTStorageMetric(application:)]) | xctest-performance_tests.md |
| Set performance baselines | Run test 5x, accept baseline in Xcode | xctest-performance_tests.md |
