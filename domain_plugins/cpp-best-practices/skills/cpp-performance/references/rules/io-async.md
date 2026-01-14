---
title: Use Asynchronous I/O for Non-Blocking Operations
impact: MEDIUM
impactDescription: prevents thread blocking, improves throughput
tags: io, async, non-blocking, coroutines, c++20
---

## Use Asynchronous I/O for Non-Blocking Operations

Blocking I/O wastes thread resources waiting for slow operations. Use asynchronous patterns to overlap computation with I/O and handle many connections efficiently.

**Incorrect (blocking I/O):**

```cpp
// Thread blocks waiting for each operation
void processRequests(const std::vector<std::string>& urls) {
    for (const auto& url : urls) {
        auto response = syncHttpGet(url);  // Blocks thread
        process(response);
    }
}
// Sequential: total time = sum of all request times
```

**Correct (asynchronous with futures):**

```cpp
void processRequests(const std::vector<std::string>& urls) {
    std::vector<std::future<Response>> futures;

    // Start all requests concurrently
    for (const auto& url : urls) {
        futures.push_back(std::async(std::launch::async,
            [&url]() { return httpGet(url); }));
    }

    // Process results as they complete
    for (auto& future : futures) {
        process(future.get());
    }
}
// Parallel: total time ≈ max single request time
```

**C++20 coroutines for async I/O:**

```cpp
#include <coroutine>

// Awaitable task type (simplified)
template<typename T>
struct Task {
    struct promise_type {
        T value_;
        Task get_return_object() { return Task{this}; }
        std::suspend_never initial_suspend() { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }
        void return_value(T v) { value_ = std::move(v); }
        void unhandled_exception() { std::terminate(); }
    };
    // ...
};

// Async file read
Task<std::string> readFileAsync(const std::string& path) {
    auto data = co_await asyncRead(path);  // Non-blocking
    co_return data;
}

// Composing async operations
Task<void> processFiles() {
    auto file1 = readFileAsync("a.txt");
    auto file2 = readFileAsync("b.txt");

    // Both reads happen concurrently
    auto data1 = co_await file1;
    auto data2 = co_await file2;

    process(data1, data2);
}
```

**Boost.Asio for production async I/O:**

```cpp
#include <boost/asio.hpp>

boost::asio::io_context io;
boost::asio::ip::tcp::socket socket(io);

// Async read
boost::asio::async_read(socket, buffer,
    [](const boost::system::error_code& ec, size_t bytes) {
        if (!ec) {
            processData(bytes);
        }
    });

// Run event loop
io.run();
```

**io_uring for Linux high-performance I/O:**

```cpp
// liburing - kernel-level async I/O
#include <liburing.h>

struct io_uring ring;
io_uring_queue_init(256, &ring, 0);

// Submit async read
struct io_uring_sqe* sqe = io_uring_get_sqe(&ring);
io_uring_prep_read(sqe, fd, buffer, size, offset);
io_uring_submit(&ring);

// Get completion
struct io_uring_cqe* cqe;
io_uring_wait_cqe(&ring, &cqe);
// Process result
io_uring_cqe_seen(&ring, cqe);
```

Reference: [Boost.Asio](https://www.boost.org/doc/libs/release/doc/html/boost_asio.html)
