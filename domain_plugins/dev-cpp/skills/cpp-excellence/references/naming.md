# Naming Conventions Deep Dive

> "The most important consistency rules are those that govern naming. The style of a name immediately informs us what sort of thing the named entity is: a type, a variable, a function, a constant, a macro, etc., without requiring us to search for the declaration."
> — Google C++ Style Guide

## Why Naming Matters at Scale

In a 100M+ LOC codebase with thousands of engineers:
- Pattern-matching is how developers navigate instantly
- Consistent naming eliminates entire categories of "what is this?" questions
- Wrong naming creates friction multiplied by every reader, forever

## Complete Naming Reference

### Types: `PascalCase`

All type names follow the same convention—classes, structs, type aliases, enums:

```cpp
// Classes and structs
class UrlTable { };
class UrlTableTester { };
struct UrlTableProperties { };

// Type aliases
using PropertiesMap = std::unordered_map<std::string, Property>;
typedef std::vector<std::string> StringVector;  // Legacy, prefer using

// Enums
enum class UrlTableError { kSuccess, kNotFound, kPermissionDenied };
enum HttpMethod { kGet, kPost, kPut, kDelete };
```

### Variables: `snake_case`

Local variables and function parameters:

```cpp
void ProcessRequest(const HttpRequest& http_request) {
  std::string table_name = http_request.table();
  int num_entries = 0;
  bool is_valid = ValidateName(table_name);
  
  for (const auto& entry : entries) {
    ProcessEntry(entry);
  }
}
```

### Class Data Members: `snake_case_` (trailing underscore)

```cpp
class TableInfo {
 public:
  int num_entries() const { return num_entries_; }
  void set_num_entries(int num_entries) { num_entries_ = num_entries; }
  
  const std::string& table_name() const { return table_name_; }
  
 private:
  int num_entries_;
  std::string table_name_;
  std::unique_ptr<Pool> pool_;
};
```

**Why the trailing underscore?**
- Instantly distinguishes members from locals/parameters
- Prevents shadowing bugs: `void SetName(std::string name) { name_ = name; }`
- Makes member access obvious in method bodies

### Struct Data Members: `snake_case` (NO underscore)

Structs are for passive data with no invariants:

```cpp
struct UrlTableProperties {
  std::string name;
  int num_entries;
  bool is_cached;
};

// Usage is direct field access
UrlTableProperties props;
props.name = "users";
props.num_entries = 100;
```

**Why no underscore for structs?**
- Structs are passive data carriers, not encapsulated objects
- Direct field access is expected, no accessor methods
- Trailing underscore would add noise without benefit

### Constants: `kPascalCase`

Constants with static storage duration (lives for program lifetime):

```cpp
// Namespace scope
constexpr int kMaxBufferSize = 1024 * 1024;
constexpr char kDefaultPath[] = "/var/data";
const std::string_view kErrorMessage = "Operation failed";

// Class scope
class HttpClient {
 public:
  static constexpr int kDefaultTimeout = 30;
  static constexpr int kMaxRetries = 3;
  
 private:
  static const std::string kUserAgent;
};

// This convention is OPTIONAL for locals
void Process() {
  const int kLocalMax = 100;  // OK
  const int local_max = 100;  // Also OK for locals
}
```

### Functions: `PascalCase`

```cpp
// Regular functions
void ComputeHash();
bool ValidateInput(const Request& request);
std::string FormatMessage(std::string_view format, Args... args);

// Accessors match member name (lowercase)
class MyClass {
 public:
  int count() const { return count_; }           // Accessor
  void set_count(int count) { count_ = count; }  // Mutator
  
  void IncrementCount();   // Non-accessor method: PascalCase
  void ProcessData();      // Non-accessor method: PascalCase
  
 private:
  int count_;
};
```

**Very short inline functions MAY use lowercase:**
```cpp
inline int size() const { return size_; }  // OK
inline bool empty() const { return size_ == 0; }  // OK
```

### Namespaces: `snake_case`

Based on project structure and path:

```cpp
namespace google_awesome_project {
namespace video {
namespace encoding {
namespace h264 {

// Nested namespaces (C++17)
namespace myproject::internal::util {

}  // namespace myproject::internal::util
```

### Enumerators: `kEnumName` (preferred)

```cpp
// Preferred: constant style
enum class UrlTableError {
  kSuccess,
  kNotFound,
  kPermissionDenied,
  kConnectionTimeout,
};

// Alternative (for compatibility): MACRO style
enum LegacyError {
  ERROR_SUCCESS,
  ERROR_NOT_FOUND,
  ERROR_PERMISSION_DENIED,
};
```

### Concepts: `PascalCase` (like types)

```cpp
template <typename T>
concept Hashable = requires(T a) {
  { std::hash<T>{}(a) } -> std::convertible_to<std::size_t>;
};

template <typename T>
concept Serializable = requires(T a, std::ostream& os) {
  { os << a } -> std::same_as<std::ostream&>;
};
```

### Template Parameters

```cpp
// Type parameters: PascalCase (like types)
template <typename ValueType, typename Allocator>
class Container { };

// Non-type parameters: follow variable or constant rules
template <int buffer_size>  // snake_case like variable
class FixedBuffer { };

template <size_t kMaxSize>  // kPascalCase for compile-time constant
class BoundedQueue { };
```

### Macros: `SCREAMING_SNAKE_CASE` with project prefix

**Avoid macros when possible.** When necessary:

```cpp
#define MYPROJECT_DISALLOW_COPY(TypeName) \
  TypeName(const TypeName&) = delete;     \
  TypeName& operator=(const TypeName&) = delete

#define MYPROJECT_UNLIKELY(x) __builtin_expect(!!(x), 0)
#define MYPROJECT_LIKELY(x)   __builtin_expect(!!(x), 1)

// NEVER without prefix in headers
#define MAX_SIZE 1024  // BAD: Will collide with other code
```

## File Naming

```
url_table.h           // Class declaration
url_table.cc          // Class definition  
url_table_test.cc     // Unit tests
url_table_benchmark.cc // Benchmarks

http_request.h
http_request.cc

// All lowercase, underscores between words
// Match the primary class name, converted to snake_case
```

## Descriptive Names vs Abbreviations

**Be descriptive. Avoid abbreviations.**

```cpp
// GOOD
int num_errors;
int num_completed_connections;
std::string table_name;

// BAD
int nerr;
int n_comp_conns;
std::string tbl_nm;
```

**Universally known abbreviations ARE acceptable:**
```cpp
int i, j, k;  // Loop counters
T* p;         // Pointer in template code
int n;        // Count in well-scoped context
```

**Domain-standard abbreviations are OK:**
```cpp
// These are standard in their domains
HttpRequest http_req;  // HTTP is universal
DnsResolver resolver;  // DNS is universal
RpcClient client;      // RPC is universal
```

## Edge Cases and Decisions

### STL-like entities follow STL conventions
```cpp
// If it looks like STL, follow STL naming
template <typename T>
class sparse_hash_map {  // lowercase like std::unordered_map
  using value_type = T;  // lowercase like STL
  using iterator = ...;
  
  iterator begin();
  iterator end();
  size_t size() const;
};
```

### Type aliases for templates
```cpp
using PropertiesMap = std::unordered_map<std::string, Property>;
using StringVector = std::vector<std::string>;
using Callback = std::function<void(int)>;
```

### Boolean variables
```cpp
bool is_valid;       // Use is_, has_, can_, should_ prefixes
bool has_permission;
bool can_proceed;
bool should_retry;

bool IsValid();      // Boolean-returning functions same pattern
bool HasPermission();
```

### Private helper functions
```cpp
class Processor {
 private:
  void ProcessInternal();        // Still PascalCase
  void ValidateInputHelper();    // Still PascalCase
  static int ComputeHashImpl();  // Still PascalCase
};
```

## Common Mistakes

```cpp
// WRONG: Struct members with underscore
struct Point {
  int x_;  // NO - structs don't use trailing underscore
  int y_;
};

// WRONG: Constants without k prefix
constexpr int MaxSize = 1024;  // Should be kMaxSize

// WRONG: Functions in snake_case
void process_data();  // Should be ProcessData()

// WRONG: Types in snake_case
class url_table { };  // Should be UrlTable

// WRONG: Abbreviations
int numConn;  // Should be num_connections or num_conns if domain-standard
```

## Naming Aliases (using declarations)

```cpp
// In .cc files or function scope: use short names
namespace fbz = ::foo::bar::baz;
using ::foo::bar::SomeType;

// In headers: must be internal namespace or part of API
namespace mylib {
namespace internal {
namespace sidetable = ::pipeline_diagnostics::sidetable;  // OK, internal
}
}

// NEVER at namespace scope in headers
namespace mylib {
using ::std::string;  // BAD: Pollutes every includer
}
```
