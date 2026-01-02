# Patterns for Scale (100M+ LOC)

> "With a codebase of 100+ million lines and thousands of engineers, some mistakes and simplifications for one engineer can become costly for many."
> — Google C++ Style Guide

## The Scale Mindset

Every decision you make is multiplied:
- **1000 engineers** will read your code
- **10 years** of maintenance ahead
- **Millions of call sites** if you're writing a library
- **Billions of executions** in production

What seems like a minor convenience becomes a major cost at scale.

## Header File Discipline

### Include What You Use (IWYU)

```cpp
// foo.cc
#include "foo.h"

#include "bar.h"  // WRONG if foo.h already includes bar.h? NO - still include it!

// WHY: bar.h might be removed from foo.h tomorrow
// Then foo.cc breaks, and the person removing it from foo.h
// has to fix every transitive includer
```

### Self-Contained Headers

Every header must compile on its own:

```cpp
// user.h
#ifndef PROJECT_USER_H_
#define PROJECT_USER_H_

#include <string>           // We use std::string
#include "project/types.h"  // We use UserId

class User {
 public:
  explicit User(UserId id);
  const std::string& name() const;
  
 private:
  UserId id_;
  std::string name_;
};

#endif  // PROJECT_USER_H_
```

**Header Guard Format**: `<PROJECT>_<PATH>_<FILE>_H_`

```cpp
// For file: google-awesome-project/src/foo/bar/baz.h
#ifndef GOOGLE_AWESOME_PROJECT_FOO_BAR_BAZ_H_
#define GOOGLE_AWESOME_PROJECT_FOO_BAR_BAZ_H_
...
#endif  // GOOGLE_AWESOME_PROJECT_FOO_BAR_BAZ_H_
```

Test by compiling the header alone:
```bash
g++ -c -fsyntax-only user.h
```

### Include Order

```cpp
// foo.cc
#include "project/foo.h"     // 1. Related header FIRST (catches missing includes)

#include <sys/types.h>       // 2. C system headers
#include <unistd.h>

#include <algorithm>         // 3. C++ standard library
#include <string>
#include <vector>

#include "absl/strings/str_cat.h"  // 4. Other libraries
#include "gtest/gtest.h"

#include "project/bar.h"     // 5. Your project headers
#include "project/util.h"
```

### Forward Declarations: Avoid When Possible

```cpp
// PREFER: Include the header
#include "project/user.h"
void ProcessUser(const User& user);

// AVOID: Forward declaration
class User;  // What if User becomes a typedef? Or changes namespace?
void ProcessUser(const User& user);

// Forward declarations hide dependencies and break tooling
```

### Internal Linkage

Definitions in `.cc` files that don't need external access should have internal linkage:

```cpp
// In .cc file - use unnamed namespace
namespace {

void HelperFunction() { /* ... */ }

constexpr int kLocalConstant = 42;

class InternalHelper { /* ... */ };

}  // namespace

// Or use static for functions/variables (less preferred)
static void AnotherHelper() { /* ... */ }
```

**Never use internal linkage in `.h` files.**

### thread_local Variables

```cpp
// At namespace/class scope: MUST use constinit
constinit thread_local int tls_counter = 0;  // Required!

// Function-local thread_local is OK without constinit
Foo& GetThreadLocalFoo() {
  thread_local Foo foo = ComputeFoo();  // OK
  return foo;
}

// WARNING: thread_local destructors run at thread exit
// Avoid complex destructors that might access other thread_locals
```

## API Design for Scale

### Minimal API Surface

```cpp
// BAD: Exposes everything
class Connection {
 public:
  void SetTimeout(int ms);
  void SetMaxRetries(int n);
  void SetBufferSize(int bytes);
  void SetKeepAlive(bool enabled);
  void SetTcpNoDelay(bool enabled);
  // ... 20 more setters
};

// GOOD: Single configuration point
class Connection {
 public:
  struct Options {
    int timeout_ms = 5000;
    int max_retries = 3;
    int buffer_size = 4096;
    bool keep_alive = true;
    bool tcp_no_delay = false;
  };
  
  static absl::StatusOr<std::unique_ptr<Connection>> Create(
      const Endpoint& endpoint, 
      const Options& options = {});
};
```

### Stable ABIs

```cpp
// Use Pimpl for classes that might change
class Widget {
 public:
  Widget();
  ~Widget();
  
  void DoWork();
  
 private:
  class Impl;
  std::unique_ptr<Impl> impl_;  // Can change without breaking ABI
};

// Use abstract interfaces for polymorphism
class Storage {
 public:
  virtual ~Storage() = default;
  virtual absl::Status Put(Key key, Value value) = 0;
  virtual absl::StatusOr<Value> Get(Key key) = 0;
};

// Factory creates concrete implementation
std::unique_ptr<Storage> CreateStorage(const Config& config);
```

### Avoid Implicit Conversions

```cpp
// Every implicit conversion is a surprise waiting to happen at scale

class FilePath {
 public:
  explicit FilePath(std::string_view path);  // ALWAYS explicit
  
  // explicit operator allows: if (path) but not: bool b = path;
  explicit operator bool() const { return !path_.empty(); }
};
```

## Namespace Hygiene

### Never Pollute Global Namespace

```cpp
// BAD: In a header
using namespace std;  // Every includer now has std:: pollution

// BAD: In a header
using std::string;    // string is now ambiguous for all includers

// GOOD: Fully qualify in headers
void Process(const std::string& data, std::vector<int>* out);

// OK: using in .cc files, inside functions, or in internal namespaces
namespace myproject::internal {
using ::absl::StrCat;  // OK, internal namespace
}
```

### Internal Namespaces

```cpp
// Hide implementation details
namespace myproject {
namespace internal {

// These are not part of the public API
class Helper { };
void InternalFunction();

}  // namespace internal

// Public API
class Widget {
 private:
  internal::Helper helper_;  // Uses internal
};

}  // namespace myproject
```

## Static and Global Variables

### The Problem

```cpp
// BAD: Non-trivial destructor
const std::string kGlobalString = "hello";  // Destructor order is undefined

// BAD: Dynamic initialization order
int g_count = ComputeCount();  // When does this run? Before or after other globals?

// BAD: Thread-unsafe mutable global
std::map<std::string, int> g_cache;  // Race condition
```

### The Solutions

```cpp
// GOOD: constexpr for trivially destructible constants
constexpr std::string_view kGlobalString = "hello";
constexpr int kMaxSize = 1024;
constexpr std::array<int, 3> kValues = {1, 2, 3};

// GOOD: Function-local static for complex constants
const std::string& GlobalString() {
  static const std::string* const str = new std::string("hello");
  return *str;  // Never deleted, but that's fine at shutdown
}

// GOOD: Function-local for lazy initialization
const Config& GlobalConfig() {
  static const Config* const config = new Config(LoadConfig());
  return *config;
}

// For mutable global state: explicit class with thread safety
class GlobalCache {
 public:
  static GlobalCache& Instance() {
    static GlobalCache* cache = new GlobalCache();
    return *cache;
  }
  
  void Put(const Key& key, Value value) {
    absl::MutexLock lock(&mutex_);
    cache_[key] = std::move(value);
  }
  
 private:
  GlobalCache() = default;
  absl::Mutex mutex_;
  absl::flat_hash_map<Key, Value> cache_ ABSL_GUARDED_BY(mutex_);
};
```

## Code Organization

### One Class Per File

```
widget.h          // Widget class declaration
widget.cc         // Widget class definition
widget_test.cc    // Widget tests

// For closely related small classes, grouping is OK
types.h           // Small POD structs
error_codes.h     // Error enums
```

### Logical Grouping

```
project/
├── core/
│   ├── types.h
│   ├── config.h
│   └── config.cc
├── storage/
│   ├── storage.h        // Abstract interface
│   ├── memory_storage.h
│   ├── memory_storage.cc
│   ├── disk_storage.h
│   └── disk_storage.cc
├── network/
│   ├── connection.h
│   └── connection.cc
└── util/
    ├── string_util.h
    └── string_util.cc
```

## Compile Time

At Google scale, compile time is developer productivity.

### Reduce Header Dependencies

```cpp
// BAD: Heavy header in .h
#include <regex>  // Pulls in massive template code

// GOOD: Forward declare, include in .cc
class std::regex;  // If possible, or Pimpl pattern
```

### Prefer Forward Declarations for Pointers/References

```cpp
// In header: forward declare when you only need pointer/reference
class HeavyClass;

class LightClass {
 public:
  void Process(const HeavyClass& heavy);  // Only needs declaration
  
 private:
  HeavyClass* heavy_;  // Only needs declaration
};

// In .cc: include the full definition
#include "heavy_class.h"

void LightClass::Process(const HeavyClass& heavy) {
  heavy.DoWork();  // Now needs full definition
}
```

### Avoid Template Bloat

```cpp
// BAD: Template in header instantiated everywhere
template <typename T>
void HugeFunction(const T& value) {
  // 500 lines of code
  // Instantiated in every translation unit that uses it
}

// GOOD: Non-template implementation in .cc
void HugeFunctionImpl(const void* data, size_t size, TypeInfo info);

template <typename T>
void HugeFunction(const T& value) {
  HugeFunctionImpl(&value, sizeof(T), GetTypeInfo<T>());
}
```

## Breaking Changes

### Deprecation Process

```cpp
// 1. Add deprecation warning
ABSL_DEPRECATED("Use NewFunction instead")
void OldFunction();

// 2. Update all callers (may take months at scale)

// 3. Remove the function
```

### Versioned APIs

```cpp
namespace mylib {
namespace v1 {
class Widget { /* original API */ };
}

namespace v2 {
class Widget { /* new API */ };
}

// Current version alias
using Widget = v2::Widget;
}
```
