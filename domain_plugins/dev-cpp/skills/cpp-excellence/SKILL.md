---
name: cpp-excellence
description: "Production-grade C++ engineering patterns from Google C++ Style Guide (100M+ LOC scale). Provides strict naming conventions, ownership semantics with smart pointers, defensive coding patterns, and scale-aware API design. Use when: (1) Writing new C++ code that must be maintainable, (2) Reviewing C++ for style compliance, (3) Designing C++ APIs or libraries, (4) Building Node.js native addons with N-API/V8, (5) Optimizing C++ hot paths for performance, (6) Questions about Google C++ style or modern C++ best practices."
---

# C++ Engineering Excellence

Battle-tested patterns from production systems at Google-scale. Focus: **non-automatable wisdom** that clang-format cannot fix.

**Core Philosophy**: Optimize for the reader, not the writer. Code is read 10x more than written.

## Quick Reference: Naming

| Entity | Convention | Example |
|--------|------------|---------|
| Types (class, struct, enum, typedef, concept) | `PascalCase` | `UrlTableTester`, `Hashable` |
| Variables, parameters | `snake_case` | `table_name`, `num_entries` |
| Class data members | `snake_case_` | `cached_value_`, `num_entries_` |
| Struct data members | `snake_case` | `num_entries` (no underscore) |
| Constants (`constexpr`, `static const`) | `kPascalCase` | `kMaxBufferSize` |
| Functions | `PascalCase` | `ComputeHash()`, `ValidateInput()` |
| Accessors/mutators | Match member | `num_entries()`, `set_num_entries()` |
| Namespaces | `snake_case` | `video::encoding::h264` |
| Macros (avoid) | `SCREAMING_SNAKE` | `MYPROJ_UNLIKELY()` |
| Enumerators | `kEnumName` | `kErrorOutOfMemory` |
| Template type params | `PascalCase` | `typename ValueType` |
| Template non-type params | `snake_case` or `kName` | `int buffer_size`, `size_t kMaxSize` |

**→ Edge cases and rationale: [references/naming.md](references/naming.md)**

## Critical Policies (Hard Rules)

### Exceptions: BANNED
```cpp
throw std::runtime_error("error");  // NEVER at Google
// Use StatusOr, factory patterns, or CHECK macros instead
```

### RTTI: AVOID
```cpp
if (typeid(*data) == typeid(D1)) { }  // BAD
// Use virtual dispatch or visitor pattern
```

### std::auto_ptr: BANNED
```cpp
std::auto_ptr<Foo> p;  // NEVER - use std::unique_ptr
```

### Copy/Move: Declare Explicitly
```cpp
class Copyable {
 public:
  Copyable(const Copyable&) = default;
  Copyable& operator=(const Copyable&) = default;
};

class MoveOnly {
 public:
  MoveOnly(MoveOnly&&) = default;
  MoveOnly& operator=(MoveOnly&&) = default;
  MoveOnly(const MoveOnly&) = delete;
  MoveOnly& operator=(const MoveOnly&) = delete;
};
```

### Integer Types
```cpp
int count = 0;           // Default for most integers
int64_t big = 0;         // When value may exceed 2^31
uint32_t flags = 0x1234; // ONLY for bit patterns, never "non-negative"
```

## Decision Trees

### Writing New Code
```
1. Apply naming table above
2. Decide ownership for each resource → see references/ownership.md
3. Choose error strategy (StatusOr, factory, CHECK) → see references/defensive.md
4. Headers: include what you use, never transitive
```

### Smart Pointer Selection
```
Need dynamic allocation?
├── No → Use value semantics (stack)
└── Yes → Ownership shared?
    ├── No → std::unique_ptr
    └── Yes → Object immutable?
        ├── Yes → std::shared_ptr<const T>
        └── No → Redesign (mutable shared = code smell)
```

### Function Parameter Types
```cpp
void Process(const Foo& foo);           // Read-only, non-null
void Mutate(Foo* foo);                  // Read-write, nullable
void MutateRequired(Foo& foo);          // Read-write, non-null
void Consume(std::unique_ptr<Foo> foo); // Takes ownership
void Store(std::shared_ptr<Foo> foo);   // Shares ownership (stores it)
```

### Error Handling (No Exceptions)
```cpp
// Simple success/failure
bool ParseConfig(const std::string& path, Config* out);

// Value + error info
absl::StatusOr<Config> ParseConfig(const std::string& path);

// Fallible construction: use factory
static std::unique_ptr<Connection> Create(const Endpoint& ep);
```

## Essential Patterns

### Ownership Must Be Explicit
```cpp
// GOOD: Compiler-verified
std::unique_ptr<Foo> CreateFoo();           // Factory transfers ownership
void ConsumeFoo(std::unique_ptr<Foo> foo);  // Takes ownership
void ObserveFoo(const Foo& foo);            // Borrows, never stores

// BAD: Ownership mystery
Foo* CreateFoo();        // Who deletes?
void Process(Foo* foo);  // Will this store/delete it?
```

### Initialization at Declaration
```cpp
// GOOD
const int count = ComputeCount();
std::vector<int> values = {1, 2, 3};

// BAD - window of undefined state
int count;
count = ComputeCount();
```

### Explicit Constructors
```cpp
// ALWAYS explicit for single-argument constructors
explicit Duration(int64_t milliseconds);
explicit FilePath(std::string_view path);
```

### Header Guards
```cpp
// Format: PROJECT_PATH_FILE_H_
#ifndef GOOGLE_AWESOME_PROJECT_FOO_BAR_BAZ_H_
#define GOOGLE_AWESOME_PROJECT_FOO_BAR_BAZ_H_
// ...
#endif  // GOOGLE_AWESOME_PROJECT_FOO_BAR_BAZ_H_
```

## Anti-Patterns to Reject

```cpp
// REJECT: using namespace in headers
using namespace std;

// REJECT: Non-explicit single-arg constructors
Foo(int x);  // Missing explicit

// REJECT: Raw new/delete
auto* p = new Foo();  // Use make_unique

// REJECT: Output params for simple returns
void GetValue(int* out);  // Just return int

// REJECT: Mutable global state
static std::map<string, int> g_cache;

// REJECT: Throwing exceptions
throw std::exception();

// REJECT: RTTI for dispatch
dynamic_cast<Derived*>(base);

// REJECT: Transitive includes
// foo.cc uses bar.h symbols but doesn't include it
// (relies on foo.h including bar.h)
```

## Reference Files

| Topic | File | When to Read |
|-------|------|--------------|
| Naming deep dive | [references/naming.md](references/naming.md) | Edge cases, abbreviations, file naming, STL-like entities |
| Ownership & memory | [references/ownership.md](references/ownership.md) | Smart pointers, RAII, factory patterns, Pimpl |
| Defensive coding | [references/defensive.md](references/defensive.md) | Const correctness, copy/move, error handling, StatusOr |
| Scale patterns | [references/scale.md](references/scale.md) | Header hygiene, API design, namespaces, static variables |
| Performance | [references/performance.md](references/performance.md) | Hot paths, allocation, cache, integer types, lock-free |
| Node.js addons | [references/node-addons.md](references/node-addons.md) | V8/N-API, prevent GC disasters, libuv integration |

## Meta-Rules

1. **Names tell you what something IS** without looking up declarations
2. **Ownership is always explicit** - reader knows who deletes what
3. **Const by default** - mutability is the exception
4. **Fail at compile time** - make wrong usage a compiler error
5. **No clever** - absence of prohibition is not permission
