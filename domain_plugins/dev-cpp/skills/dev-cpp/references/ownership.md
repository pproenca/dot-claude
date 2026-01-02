# Ownership and Memory Management

> "Prefer to have single, fixed owners for dynamically allocated objects. Prefer to transfer ownership with smart pointers."
> — Google C++ Style Guide

## The Ownership Mental Model

Every dynamically allocated resource has **exactly one owner** at any point in time. The owner is responsible for:
1. Ensuring the resource is valid while in use
2. Destroying the resource when no longer needed
3. Preventing use-after-free

**If you can't immediately answer "who owns this?", the code is broken.**

## Smart Pointer Decision Tree

```
Do you need dynamic allocation at all?
├── No → Use value semantics (stack allocation)
└── Yes → Continue...

Does ownership need to be shared?
├── No → Use std::unique_ptr
└── Yes → Is the shared object immutable?
    ├── Yes → std::shared_ptr<const T> is acceptable
    └── No → Redesign. Mutable shared ownership is a code smell.
```

**NEVER use std::auto_ptr** - it's deprecated and broken. Use std::unique_ptr.

## std::unique_ptr: The Default Choice

```cpp
// Factory functions return unique_ptr to transfer ownership
std::unique_ptr<Connection> CreateConnection(const Config& config) {
  auto conn = std::make_unique<Connection>();
  if (!conn->Initialize(config)) {
    return nullptr;  // Ownership never transferred, automatically cleaned up
  }
  return conn;  // Caller now owns
}

// Consumer takes ownership by value
void ProcessAndDestroy(std::unique_ptr<Request> request) {
  Process(*request);
  // request destroyed at end of scope
}

// Moving ownership is explicit
auto conn = CreateConnection(config);
processor.TakeConnection(std::move(conn));  // Explicit transfer
// conn is now nullptr, can't accidentally use it
```

### unique_ptr for Class Members

```cpp
class ResourceManager {
 public:
  ResourceManager() : cache_(std::make_unique<Cache>()) {}
  
  // Expose for use, not for ownership
  Cache* cache() { return cache_.get(); }
  const Cache* cache() const { return cache_.get(); }
  
  // Transfer ownership out (rare, be explicit about it)
  std::unique_ptr<Cache> ReleaseCache() { return std::move(cache_); }
  
 private:
  std::unique_ptr<Cache> cache_;  // ResourceManager owns Cache
};
```

## std::shared_ptr: Use Sparingly

**Shared ownership is often a design smell.** Valid uses:
- Immutable shared data: `std::shared_ptr<const Config>`
- Observer patterns with weak references
- Caches where lifetime is genuinely shared

```cpp
// GOOD: Shared immutable configuration
class Application {
 public:
  explicit Application(std::shared_ptr<const Config> config)
      : config_(std::move(config)) {}
      
 private:
  std::shared_ptr<const Config> config_;  // Multiple components share this
};

// Create once, share everywhere
auto config = std::make_shared<const Config>(LoadConfig());
auto app = std::make_unique<Application>(config);
auto logger = std::make_unique<Logger>(config);  // Same config
```

### weak_ptr for Breaking Cycles

```cpp
class Node {
 public:
  void SetParent(std::shared_ptr<Node> parent) {
    parent_ = parent;  // weak_ptr, won't prevent parent destruction
  }
  
  std::shared_ptr<Node> GetParent() const {
    return parent_.lock();  // Returns nullptr if parent destroyed
  }
  
 private:
  std::weak_ptr<Node> parent_;  // Break the ownership cycle
  std::vector<std::shared_ptr<Node>> children_;  // We own children
};
```

## Function Parameter Conventions

```cpp
// Observe only, no ownership implications
void Process(const Foo& foo);           // Prefer for read-only
void Mutate(Foo* foo);                  // Prefer for read-write (nullable)
void MutateRequired(Foo& foo);          // Read-write, must not be null

// Take ownership
void Consume(std::unique_ptr<Foo> foo); // Takes and likely destroys
void Store(std::shared_ptr<Foo> foo);   // Will store the shared_ptr

// Share ownership (must store the shared_ptr)
void AddObserver(std::shared_ptr<Observer> obs);  // Will keep reference

// AVOID: Confusing ownership
void Process(Foo* foo);  // Does this store it? Delete it? Who knows!
```

## RAII: Resource Acquisition Is Initialization

Every resource gets a class that:
1. Acquires in constructor
2. Releases in destructor
3. Deletes copy (or implements correctly)
4. Implements move (or deletes it)

```cpp
class FileHandle {
 public:
  explicit FileHandle(const char* path) 
      : fd_(open(path, O_RDONLY)) {
    if (fd_ < 0) {
      throw std::system_error(errno, std::generic_category());
    }
  }
  
  ~FileHandle() {
    if (fd_ >= 0) {
      close(fd_);
    }
  }
  
  // Non-copyable
  FileHandle(const FileHandle&) = delete;
  FileHandle& operator=(const FileHandle&) = delete;
  
  // Movable
  FileHandle(FileHandle&& other) noexcept : fd_(other.fd_) {
    other.fd_ = -1;
  }
  
  FileHandle& operator=(FileHandle&& other) noexcept {
    if (this != &other) {
      if (fd_ >= 0) close(fd_);
      fd_ = other.fd_;
      other.fd_ = -1;
    }
    return *this;
  }
  
  int fd() const { return fd_; }
  
 private:
  int fd_;
};
```

## Common Ownership Patterns

### Factory with Fallible Construction

```cpp
class Connection {
 public:
  // Factory - the only way to create
  static std::unique_ptr<Connection> Create(const Endpoint& endpoint) {
    auto conn = std::unique_ptr<Connection>(new Connection());
    if (!conn->Connect(endpoint)) {
      return nullptr;
    }
    return conn;
  }
  
  // Public interface
  bool Send(std::string_view data);
  
 private:
  Connection() = default;  // Private, forces factory use
  bool Connect(const Endpoint& endpoint);
  
  int socket_fd_ = -1;
};

// Usage
auto conn = Connection::Create(endpoint);
if (!conn) {
  LOG(ERROR) << "Connection failed";
  return;
}
conn->Send("hello");
```

### Pimpl with unique_ptr

```cpp
// widget.h - Public interface, stable ABI
class Widget {
 public:
  Widget();
  ~Widget();  // Must be declared, defined in .cc
  
  Widget(Widget&&) noexcept;
  Widget& operator=(Widget&&) noexcept;
  
  void DoWork();
  
 private:
  class Impl;  // Forward declaration
  std::unique_ptr<Impl> impl_;
};

// widget.cc - Implementation details hidden
class Widget::Impl {
 public:
  void DoWork() { /* complex implementation */ }
 private:
  // Heavy dependencies only in .cc
  HugeLibrary lib_;
  std::vector<ComplexType> data_;
};

Widget::Widget() : impl_(std::make_unique<Impl>()) {}
Widget::~Widget() = default;  // unique_ptr needs complete type
Widget::Widget(Widget&&) noexcept = default;
Widget& Widget::operator=(Widget&&) noexcept = default;

void Widget::DoWork() { impl_->DoWork(); }
```

### Object Pool

```cpp
template <typename T>
class ObjectPool {
 public:
  std::unique_ptr<T, std::function<void(T*)>> Acquire() {
    std::lock_guard<std::mutex> lock(mutex_);
    
    if (pool_.empty()) {
      return {new T(), [this](T* obj) { this->Release(obj); }};
    }
    
    T* obj = pool_.back().release();
    pool_.pop_back();
    return {obj, [this](T* obj) { this->Release(obj); }};
  }
  
 private:
  void Release(T* obj) {
    std::lock_guard<std::mutex> lock(mutex_);
    pool_.push_back(std::unique_ptr<T>(obj));
  }
  
  std::mutex mutex_;
  std::vector<std::unique_ptr<T>> pool_;
};
```

## Anti-Patterns

```cpp
// BAD: Raw new/delete
Foo* foo = new Foo();
// ... 100 lines later, did we delete?
delete foo;  // Hope we didn't forget, hope no exception was thrown

// BAD: std::auto_ptr (BANNED)
std::auto_ptr<Foo> p;  // NEVER - deprecated, use unique_ptr

// BAD: Shared ownership of mutable state
std::shared_ptr<std::vector<int>> shared_data;  // Race condition waiting to happen

// BAD: Storing raw pointer with unclear ownership
class Manager {
  std::vector<Foo*> items_;  // Who deletes these? When?
};

// BAD: Returning raw pointer from factory
Foo* CreateFoo();  // Caller must remember to delete

// BAD: Optional ownership
void Process(Foo* foo, bool take_ownership);  // Recipe for bugs
```

**Note on Performance**: The performance costs of ownership transfer are often overestimated. Moving a unique_ptr is just copying a pointer. Don't avoid smart pointers for "performance" without measuring.

## Testing Ownership

If you're unsure about ownership in existing code, add this:

```cpp
class OwnershipTracker {
 public:
  OwnershipTracker() { ++live_count; }
  ~OwnershipTracker() { --live_count; }
  
  static int live_count;
};

// In tests
TEST(OwnershipTest, NoLeaks) {
  OwnershipTracker::live_count = 0;
  {
    auto thing = CreateThing();
    ProcessThing(std::move(thing));
  }
  EXPECT_EQ(0, OwnershipTracker::live_count);
}
```
