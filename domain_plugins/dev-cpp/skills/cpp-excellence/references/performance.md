# Performance Patterns

Patterns for hot paths, livestreaming, and high-throughput systems where every microsecond matters.

## Integer Types for Performance

Choose integer types deliberately:

```cpp
// DEFAULT: Use int for general integers
int count = 0;           // Loop counters, small counts
int result = Compute();  // General computation

// EXACT-WIDTH: When size matters
int64_t large_count = 0;     // Values that may exceed 2^31
int32_t wire_value = 0;      // Network/file format compatibility
int16_t audio_sample = 0;    // Memory-constrained contexts

// UNSIGNED: ONLY for bit patterns, not "non-negative numbers"
uint32_t flags = 0x1234;     // OK - bit pattern
uint8_t byte = buffer[i];    // OK - raw bytes
unsigned int count = 0;      // BAD - use int, assert non-negative

// AVOID: Implementation-defined sizes
short x;       // Use int16_t
long y;        // Use int64_t  
long long z;   // Use int64_t
```

**Why avoid unsigned for counts:**
```cpp
for (unsigned i = n - 1; i >= 0; i--) {  // BUG: infinite loop!
  // When i == 0, i-- wraps to UINT_MAX
}

// Mixing signed/unsigned causes bugs
int a = -1;
unsigned b = 1;
if (a < b) { }  // FALSE! a is converted to huge unsigned
```

## Know Your Costs

| Operation | Approximate Cost |
|-----------|------------------|
| L1 cache hit | 1 ns |
| L2 cache hit | 4 ns |
| L3 cache hit | 12 ns |
| Main memory | 100 ns |
| Branch mispredict | 10-20 ns |
| Virtual function call | 10 ns |
| System call | 1-10 μs |
| Mutex lock (uncontended) | 25 ns |
| Mutex lock (contended) | 10 μs+ |
| Heap allocation | 100 ns - 1 μs |
| Context switch | 1-10 μs |

**Measure before optimizing.** These are approximations—your hardware varies.

## Memory Allocation

### The Problem

```cpp
// HOT PATH: 10 million calls/second
void ProcessFrame(const Frame& frame) {
  std::vector<Point> points;  // ALLOCATION every call!
  ExtractPoints(frame, &points);
  
  std::string metadata = FormatMetadata(frame);  // ALLOCATION!
  
  for (const auto& point : points) {
    ProcessPoint(point, metadata);
  }
}
// Cost: ~200ns of allocations per frame = 2 seconds/10M frames
```

### Pre-allocate and Reuse

```cpp
class FrameProcessor {
 public:
  void ProcessFrame(const Frame& frame) {
    // Reuse existing capacity
    points_.clear();  // Does NOT deallocate
    ExtractPoints(frame, &points_);
    
    // Reuse string buffer
    metadata_.clear();
    FormatMetadataInto(frame, &metadata_);
    
    for (const auto& point : points_) {
      ProcessPoint(point, metadata_);
    }
  }
  
 private:
  std::vector<Point> points_;  // Allocated once
  std::string metadata_;       // Allocated once
};
```

### Object Pools

```cpp
template <typename T>
class ObjectPool {
 public:
  T* Acquire() {
    if (!free_list_.empty()) {
      T* obj = free_list_.back();
      free_list_.pop_back();
      return obj;
    }
    objects_.push_back(std::make_unique<T>());
    return objects_.back().get();
  }
  
  void Release(T* obj) {
    obj->Reset();  // Clear state, keep memory
    free_list_.push_back(obj);
  }
  
 private:
  std::vector<std::unique_ptr<T>> objects_;
  std::vector<T*> free_list_;
};

// Usage
class Connection {
 public:
  void Reset() { /* clear state */ }
};

ObjectPool<Connection> pool;

void HandleRequest() {
  Connection* conn = pool.Acquire();
  // Use conn...
  pool.Release(conn);
}
```

### Arena Allocation

```cpp
class Arena {
 public:
  explicit Arena(size_t block_size = 64 * 1024)
      : block_size_(block_size) {}
  
  void* Allocate(size_t size, size_t alignment = alignof(max_align_t)) {
    size_t space = current_block_end_ - current_ptr_;
    void* aligned = current_ptr_;
    
    if (std::align(alignment, size, aligned, space)) {
      current_ptr_ = static_cast<char*>(aligned) + size;
      return aligned;
    }
    
    // Need new block
    AllocateBlock(std::max(size, block_size_));
    return Allocate(size, alignment);
  }
  
  template <typename T, typename... Args>
  T* Create(Args&&... args) {
    void* mem = Allocate(sizeof(T), alignof(T));
    return new (mem) T(std::forward<Args>(args)...);
  }
  
  void Reset() {
    // Keep blocks, reset pointer
    if (!blocks_.empty()) {
      current_ptr_ = blocks_.front().get();
      current_block_end_ = current_ptr_ + block_size_;
    }
  }
  
 private:
  void AllocateBlock(size_t size) {
    blocks_.push_back(std::unique_ptr<char[]>(new char[size]));
    current_ptr_ = blocks_.back().get();
    current_block_end_ = current_ptr_ + size;
  }
  
  size_t block_size_;
  std::vector<std::unique_ptr<char[]>> blocks_;
  char* current_ptr_ = nullptr;
  char* current_block_end_ = nullptr;
};
```

## Cache Efficiency

### Data Layout

```cpp
// BAD: Array of Structs (AoS) - poor cache utilization for single-field access
struct Particle {
  float x, y, z;
  float vx, vy, vz;
  float mass;
  int id;
};
std::vector<Particle> particles;

void UpdatePositions(float dt) {
  for (auto& p : particles) {
    p.x += p.vx * dt;  // Loads entire Particle, uses 3 fields
    p.y += p.vy * dt;
    p.z += p.vz * dt;
  }
}

// GOOD: Struct of Arrays (SoA) - cache-friendly for vectorized operations
struct Particles {
  std::vector<float> x, y, z;
  std::vector<float> vx, vy, vz;
  std::vector<float> mass;
  std::vector<int> id;
};

void UpdatePositions(Particles& p, float dt) {
  for (size_t i = 0; i < p.x.size(); i++) {
    p.x[i] += p.vx[i] * dt;  // Sequential memory access
    p.y[i] += p.vy[i] * dt;
    p.z[i] += p.vz[i] * dt;
  }
}
```

### Hot/Cold Splitting

```cpp
// BAD: Hot and cold data mixed
struct Request {
  // Hot (used every request)
  int type;
  int priority;
  
  // Cold (used rarely)
  std::string debug_info;
  std::vector<std::string> trace;
  std::chrono::time_point<std::chrono::system_clock> created_at;
};

// GOOD: Split hot and cold
struct RequestHot {
  int type;
  int priority;
  RequestCold* cold;  // Pointer to cold data when needed
};

struct RequestCold {
  std::string debug_info;
  std::vector<std::string> trace;
  std::chrono::time_point<std::chrono::system_clock> created_at;
};
```

### Prefetching

```cpp
void ProcessArray(const int* data, size_t n) {
  for (size_t i = 0; i < n; i++) {
    // Prefetch 8 elements ahead
    if (i + 8 < n) {
      __builtin_prefetch(&data[i + 8], 0, 3);
    }
    ProcessElement(data[i]);
  }
}
```

## Branch Prediction

### Likely/Unlikely Hints

```cpp
#define LIKELY(x)   __builtin_expect(!!(x), 1)
#define UNLIKELY(x) __builtin_expect(!!(x), 0)

int ProcessPacket(const Packet& packet) {
  if (UNLIKELY(packet.is_corrupted())) {
    return HandleCorruption(packet);  // Rare path
  }
  
  if (LIKELY(packet.type() == PacketType::kData)) {
    return ProcessData(packet);  // Common path
  }
  
  return ProcessControlPacket(packet);
}
```

### Branchless Code

```cpp
// BRANCHY
int Max(int a, int b) {
  if (a > b) return a;
  return b;
}

// BRANCHLESS
int Max(int a, int b) {
  return a ^ ((a ^ b) & -(a < b));
}

// Or use std::max which the compiler may optimize

// BRANCHY
int Clamp(int value, int min, int max) {
  if (value < min) return min;
  if (value > max) return max;
  return value;
}

// BRANCHLESS
int Clamp(int value, int min, int max) {
  value = value < min ? min : value;
  value = value > max ? max : value;
  return value;
}
```

### Sort Data for Predictable Branches

```cpp
// If you must branch, make it predictable
void ProcessMixedPackets(std::vector<Packet>& packets) {
  // Sort so all Type A comes before Type B
  std::partition(packets.begin(), packets.end(), 
                 [](const Packet& p) { return p.type == TypeA; });
  
  // Now branches are predictable
  for (const auto& packet : packets) {
    if (packet.type == TypeA) {
      ProcessTypeA(packet);
    } else {
      ProcessTypeB(packet);
    }
  }
}
```

## Lock-Free Patterns

### SPSC Queue (Single Producer, Single Consumer)

```cpp
template <typename T, size_t Capacity>
class SPSCQueue {
 public:
  bool Push(const T& value) {
    size_t write = write_.load(std::memory_order_relaxed);
    size_t next = (write + 1) % Capacity;
    
    if (next == read_.load(std::memory_order_acquire)) {
      return false;  // Full
    }
    
    buffer_[write] = value;
    write_.store(next, std::memory_order_release);
    return true;
  }
  
  bool Pop(T* value) {
    size_t read = read_.load(std::memory_order_relaxed);
    
    if (read == write_.load(std::memory_order_acquire)) {
      return false;  // Empty
    }
    
    *value = buffer_[read];
    read_.store((read + 1) % Capacity, std::memory_order_release);
    return true;
  }
  
 private:
  std::array<T, Capacity> buffer_;
  std::atomic<size_t> read_{0};
  std::atomic<size_t> write_{0};
};
```

### Avoiding False Sharing

```cpp
// BAD: Counters on same cache line
struct Counters {
  std::atomic<int64_t> reads{0};
  std::atomic<int64_t> writes{0};  // Same cache line, false sharing!
};

// GOOD: Pad to separate cache lines
struct alignas(64) PaddedCounter {
  std::atomic<int64_t> value{0};
  char padding[64 - sizeof(std::atomic<int64_t>)];
};

struct Counters {
  PaddedCounter reads;
  PaddedCounter writes;  // Different cache lines
};
```

## String Operations

### Avoid Copies

```cpp
// BAD: Copies everywhere
void ProcessLog(std::string log) {  // Copy 1
  std::string prefix = log.substr(0, 10);  // Copy 2
  std::string body = log.substr(10);  // Copy 3
  DoWork(prefix, body);  // Possible copies 4, 5
}

// GOOD: Views all the way
void ProcessLog(std::string_view log) {  // No copy
  std::string_view prefix = log.substr(0, 10);  // No copy
  std::string_view body = log.substr(10);  // No copy
  DoWork(prefix, body);  // No copies
}
```

### Small String Optimization

```cpp
// std::string has SSO: strings <= ~15 chars don't allocate
void ProcessSmall() {
  std::string s = "hello";  // No allocation! SSO kicks in
  
  // For larger strings, consider flat_hash_map<string_view, ...>
  // if you can guarantee the string outlives the map
}
```

### Pre-sized Buffers

```cpp
std::string BuildMessage(const Data& data) {
  std::string result;
  result.reserve(1024);  // Estimate size upfront
  
  absl::StrAppend(&result, "Header: ", data.header());
  absl::StrAppend(&result, "\nBody: ", data.body());
  // ... append more
  
  return result;  // Single allocation
}
```

## Inlining

### Force Inlining Hot Paths

```cpp
// Header-only for inlining
inline int FastHash(uint32_t x) __attribute__((always_inline));
inline int FastHash(uint32_t x) {
  x ^= x >> 16;
  x *= 0x85ebca6b;
  x ^= x >> 13;
  x *= 0xc2b2ae35;
  x ^= x >> 16;
  return x;
}
```

### Prevent Inlining Cold Paths

```cpp
void HandleError(const Error& e) __attribute__((noinline));
void HandleError(const Error& e) {
  // Error handling code - keep out of hot path instruction cache
  LogError(e);
  UpdateMetrics(e);
  NotifyMonitoring(e);
}

void ProcessPacket(const Packet& p) {
  if (UNLIKELY(p.HasError())) {
    HandleError(p.error());  // Not inlined, keeps ProcessPacket small
    return;
  }
  // Hot path stays compact
  DoWork(p);
}
```

## Measurement

```cpp
#include <chrono>

class Timer {
 public:
  Timer() : start_(std::chrono::high_resolution_clock::now()) {}
  
  double ElapsedMicros() const {
    auto now = std::chrono::high_resolution_clock::now();
    return std::chrono::duration<double, std::micro>(now - start_).count();
  }
  
 private:
  std::chrono::time_point<std::chrono::high_resolution_clock> start_;
};

// Usage
void Benchmark() {
  Timer t;
  for (int i = 0; i < 1000000; i++) {
    DoWork();
  }
  double us = t.ElapsedMicros();
  LOG(INFO) << "Per-op: " << (us / 1000000) << " μs";
}
```

**Always benchmark with optimizations enabled (`-O2` or `-O3`).**
