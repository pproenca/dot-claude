---
title: Use Forward Declarations to Reduce Includes
impact: CRITICAL
impactDescription: 2-10x faster compile times for large projects
tags: compile, forward-declaration, includes, headers, dependencies
---

## Use Forward Declarations to Reduce Includes

Forward declare types instead of including their headers when the full definition isn't needed. This breaks dependency chains and dramatically reduces compile times.

**Incorrect (unnecessary includes):**

```cpp
// widget.h
#include "database.h"    // 500+ lines, includes SQL libraries
#include "network.h"     // 300+ lines, includes socket headers
#include "config.h"      // 200+ lines

class Widget {
    Database* db_;       // Only needs pointer
    Network* net_;       // Only needs pointer
    Config* cfg_;        // Only needs pointer
public:
    void process();
};
```

Every file that includes `widget.h` must also parse 1000+ lines of dependencies.

**Correct (forward declarations):**

```cpp
// widget.h
class Database;  // Forward declaration
class Network;   // Forward declaration
class Config;    // Forward declaration

class Widget {
    Database* db_;
    Network* net_;
    Config* cfg_;
public:
    void process();
};

// widget.cpp - includes only where needed
#include "widget.h"
#include "database.h"
#include "network.h"
#include "config.h"

void Widget::process() {
    db_->query(...);
}
```

**When forward declaration works:**

```cpp
// These only need forward declaration
class Foo;

void process(Foo* ptr);           // Pointer parameter
void process(Foo& ref);           // Reference parameter
Foo* create();                    // Pointer return
std::unique_ptr<Foo> make();      // Smart pointer
class Bar { Foo* member_; };      // Pointer member
```

**When full include is required:**

```cpp
#include "foo.h"  // Required for:

Foo obj;                          // Value (need size)
class Bar : public Foo {};        // Inheritance
void func() { foo.method(); }     // Calling methods
sizeof(Foo);                      // Size information
```

Reference: [C++ Core Guidelines SF.9](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#sf9-avoid-cyclic-dependencies-among-source-files)
