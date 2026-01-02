# Defensive Coding Patterns

> "Avoid surprising or dangerous constructs. C++ has features that are more surprising or dangerous than one might think at a glance."
> — Google C++ Style Guide

## Const Correctness

### The Rule: Const by Default

```cpp
// Function parameters
void Process(const std::string& input);        // Read-only access
void Modify(std::string* output);              // Will modify (pointer = mutable)
void Transform(const Request& req, Response* resp);

// Methods
class DataStore {
 public:
  int size() const;                            // Doesn't modify state
  const std::string& name() const;             // Returns const reference
  bool Contains(const Key& key) const;         // Query method
  
  void Add(const Item& item);                  // Modifies state
  void Clear();                                // Modifies state
};

// Variables
const int count = ComputeCount();              // Won't change
const auto& config = GetConfig();              // Won't modify config
```

### Why Const Matters

1. **Documentation**: Reader knows this won't be modified
2. **Thread safety**: Const methods are safe to call concurrently
3. **Compiler verification**: Catches accidental modifications
4. **Optimization**: Compiler can make assumptions

### Const Placement

```cpp
const int* ptr;        // Pointer to const int (can't modify *ptr)
int* const ptr;        // Const pointer to int (can't modify ptr)
const int* const ptr;  // Const pointer to const int

// Read right-to-left: "ptr is a const pointer to a const int"

// Prefer const on the left for simple cases (more readable)
const std::string& name();

// Some prefer consistency: const always follows what it modifies
std::string const& name();  // Also valid, less common
```

## Initialization

### Initialize at Declaration

```cpp
// GOOD: Initialize immediately
const int count = ComputeCount();
std::string name = GetName();
std::vector<int> values = {1, 2, 3};
auto result = Process(input);

// BAD: Delayed initialization
int count;
if (condition) {
  count = GetA();
} else {
  count = GetB();
}

// GOOD: Use ternary for simple cases
const int count = condition ? GetA() : GetB();

// GOOD: Use immediately-invoked lambda for complex cases
const int count = [&]() {
  if (complex_condition) {
    return ComputeA();
  } else if (other_condition) {
    return ComputeB();
  }
  return default_value;
}();
```

### Member Initializer Lists

```cpp
class HttpClient {
 public:
  // GOOD: Initialize in member initializer list
  explicit HttpClient(const Config& config)
      : timeout_(config.timeout()),
        max_retries_(config.max_retries()),
        base_url_(config.base_url()),
        pool_(std::make_unique<ConnectionPool>()) {}
  
  // BAD: Assignment in constructor body
  explicit HttpClient(const Config& config) {
    timeout_ = config.timeout();        // Wasteful: default-construct then assign
    max_retries_ = config.max_retries();
    base_url_ = config.base_url();
  }
  
 private:
  int timeout_;
  int max_retries_;
  std::string base_url_;
  std::unique_ptr<ConnectionPool> pool_;
};
```

### In-Class Member Initializers

```cpp
class Counter {
 public:
  void Increment() { ++count_; }
  int count() const { return count_; }
  
 private:
  int count_ = 0;          // Default value at declaration
  bool is_enabled_ = true;
  std::string name_ = "default";
};
```

## Error Handling (Without Exceptions)

Google style forbids exceptions. Use these patterns instead:

### Return Values for Expected Failures

```cpp
// Simple bool for success/failure
bool ParseConfig(const std::string& path, Config* out);

// StatusOr for value + error info
absl::StatusOr<Config> ParseConfig(const std::string& path);

// Usage
auto config_or = ParseConfig(path);
if (!config_or.ok()) {
  LOG(ERROR) << "Failed to parse: " << config_or.status();
  return;
}
const Config& config = *config_or;
```

### absl::Status Patterns

```cpp
absl::Status ValidateInput(const Request& request) {
  if (request.name().empty()) {
    return absl::InvalidArgumentError("name cannot be empty");
  }
  if (request.count() < 0) {
    return absl::InvalidArgumentError("count must be non-negative");
  }
  return absl::OkStatus();
}

absl::StatusOr<Response> ProcessRequest(const Request& request) {
  // Validate first
  if (auto status = ValidateInput(request); !status.ok()) {
    return status;
  }
  
  // Do work
  Response response;
  response.set_result(Compute(request));
  return response;
}

// Macro for early return (if using abseil)
ASSIGN_OR_RETURN(auto config, LoadConfig(path));
RETURN_IF_ERROR(ValidateConfig(config));
```

### Fallible Construction: Factory Pattern

```cpp
class Connection {
 public:
  // Factory returns nullptr on failure
  static std::unique_ptr<Connection> Create(const Endpoint& endpoint) {
    auto conn = std::unique_ptr<Connection>(new Connection());
    if (!conn->Initialize(endpoint)) {
      return nullptr;
    }
    return conn;
  }
  
  // Or return StatusOr for error details
  static absl::StatusOr<std::unique_ptr<Connection>> Create(
      const Endpoint& endpoint) {
    auto conn = std::unique_ptr<Connection>(new Connection());
    if (auto status = conn->Initialize(endpoint); !status.ok()) {
      return status;
    }
    return conn;
  }
  
 private:
  Connection() = default;  // Private constructor
  absl::Status Initialize(const Endpoint& endpoint);
};
```

## Copy and Move Semantics

### The Rule: Declare All Four Explicitly

Every class's public API must make clear whether it's copyable, move-only, or neither:

```cpp
// COPYABLE: Explicitly declare copy operations
class Copyable {
 public:
  Copyable(const Copyable& other) = default;
  Copyable& operator=(const Copyable& other) = default;
  
  // Move operations implicitly suppressed, or declare explicitly for efficiency
  Copyable(Copyable&& other) = default;
  Copyable& operator=(Copyable&& other) = default;
};

// MOVE-ONLY: Explicitly declare move, delete copy
class MoveOnly {
 public:
  MoveOnly(MoveOnly&& other) = default;
  MoveOnly& operator=(MoveOnly&& other) = default;
  
  // Explicitly delete copy
  MoveOnly(const MoveOnly&) = delete;
  MoveOnly& operator=(const MoveOnly&) = delete;
};

// NEITHER: Delete copy (move implicitly deleted)
class NotCopyableOrMovable {
 public:
  NotCopyableOrMovable(const NotCopyableOrMovable&) = delete;
  NotCopyableOrMovable& operator=(const NotCopyableOrMovable&) = delete;
  
  // Move also deleted (can spell out explicitly for clarity)
  NotCopyableOrMovable(NotCopyableOrMovable&&) = delete;
  NotCopyableOrMovable& operator=(NotCopyableOrMovable&&) = delete;
};
```

### Why This Matters

```cpp
// BAD: Implicit behavior is unclear
class Widget {
 public:
  Widget();
  // Is this copyable? Movable? Reader must check all members
 private:
  std::unique_ptr<Impl> impl_;  // Makes class move-only implicitly
};

// GOOD: Explicit intent
class Widget {
 public:
  Widget();
  ~Widget();
  
  Widget(Widget&&) noexcept;
  Widget& operator=(Widget&&) noexcept;
  
  Widget(const Widget&) = delete;
  Widget& operator=(const Widget&) = delete;
  
 private:
  std::unique_ptr<Impl> impl_;
};
```

### Exception: Obvious Cases

Declarations can be omitted only if copyability is obvious:
- Structs with no private section (copyability determined by members)
- Interface-only base classes

## Explicit Keyword

### Single-Argument Constructors

```cpp
// ALWAYS explicit for single-argument constructors
class Duration {
 public:
  explicit Duration(int64_t milliseconds);
};

class FilePath {
 public:
  explicit FilePath(std::string_view path);
};

// WHY: Prevents subtle bugs
void Wait(Duration d);

// Without explicit:
Wait(5);  // Compiles! But is this 5ms? 5s? 5 hours?

// With explicit:
Wait(Duration(5));  // Clear: 5 of whatever Duration's unit is
```

### Conversion Operators

```cpp
class SafeBool {
 public:
  // BAD: Allows arithmetic on bool result
  operator bool() const { return is_valid_; }
  
  // GOOD: Must explicitly convert
  explicit operator bool() const { return is_valid_; }
  
 private:
  bool is_valid_;
};

// Usage
SafeBool sb;
if (sb) { }        // OK: explicit conversion in boolean context
bool b = sb;       // Error with explicit: must use static_cast
bool b = static_cast<bool>(sb);  // OK: explicit conversion
```

## Assertions and Invariants

### Debug-Only Checks

```cpp
#include <cassert>

void ProcessBuffer(const char* data, size_t size) {
  assert(data != nullptr);  // Programmer error if nullptr
  assert(size > 0);         // Programmer error if empty
  
  // In release builds, assertions are removed
  DoWork(data, size);
}
```

### Production Checks

```cpp
void ProcessBuffer(const char* data, size_t size) {
  // CHECK always runs, crashes with message
  CHECK(data != nullptr) << "data must not be null";
  CHECK_GT(size, 0) << "size must be positive";
  
  // DCHECK only in debug builds
  DCHECK(IsAligned(data, 8)) << "data should be 8-byte aligned";
}
```

### Documenting Invariants

```cpp
class CircularBuffer {
 public:
  void Push(int value) {
    // INVARIANT: size_ <= capacity_
    DCHECK_LE(size_, capacity_);
    
    if (size_ == capacity_) {
      // Overwrite oldest
      data_[head_] = value;
      head_ = (head_ + 1) % capacity_;
    } else {
      data_[(head_ + size_) % capacity_] = value;
      ++size_;
    }
    
    // INVARIANT: Still holds
    DCHECK_LE(size_, capacity_);
  }
};
```

## Null Safety

### Prefer References Over Pointers

```cpp
// GOOD: Reference means non-null
void Process(const Request& request);

// When nullable, use pointer + document
// @param request The request to process. May be null for default behavior.
void Process(const Request* request);

// BEST: Use std::optional for optional values
void Process(std::optional<Request> request);
```

### Validate Pointers at Boundaries

```cpp
absl::StatusOr<Response> HandleRequest(const Request* request) {
  // Validate at API boundary
  if (request == nullptr) {
    return absl::InvalidArgumentError("request must not be null");
  }
  
  // After validation, can use references internally
  return ProcessValidatedRequest(*request);
}
```

## Preventing Common Bugs

### Range Checking

```cpp
class Array {
 public:
  int& operator[](size_t index) {
    DCHECK_LT(index, size_) << "Index out of bounds";
    return data_[index];
  }
  
  // Safe access with bounds checking in release
  int& at(size_t index) {
    if (index >= size_) {
      throw std::out_of_range("Index out of bounds");
      // Or: LOG(FATAL) << "Index " << index << " out of bounds";
    }
    return data_[index];
  }
};
```

### Integer Overflow

```cpp
// Use safe arithmetic when overflow is possible
#include <absl/numeric/int128.h>

bool SafeAdd(int64_t a, int64_t b, int64_t* result) {
  if (b > 0 && a > INT64_MAX - b) return false;  // Overflow
  if (b < 0 && a < INT64_MIN - b) return false;  // Underflow
  *result = a + b;
  return true;
}

// Or use saturating arithmetic
int64_t SaturatingAdd(int64_t a, int64_t b) {
  if (b > 0 && a > INT64_MAX - b) return INT64_MAX;
  if (b < 0 && a < INT64_MIN - b) return INT64_MIN;
  return a + b;
}
```

### Thread Safety Annotations

```cpp
class Counter {
 public:
  void Increment() ABSL_LOCKS_EXCLUDED(mutex_) {
    absl::MutexLock lock(&mutex_);
    ++count_;
  }
  
  int count() const ABSL_LOCKS_EXCLUDED(mutex_) {
    absl::MutexLock lock(&mutex_);
    return count_;
  }
  
 private:
  mutable absl::Mutex mutex_;
  int count_ ABSL_GUARDED_BY(mutex_) = 0;
};
```
