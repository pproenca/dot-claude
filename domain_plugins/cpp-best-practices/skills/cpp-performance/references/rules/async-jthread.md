---
title: Use jthread Over thread for Automatic Joining
impact: HIGH
impactDescription: eliminates resource leaks, exception-safe
tags: async, jthread, thread, concurrency, c++20, raii
---

## Use jthread Over thread for Automatic Joining

`std::jthread` (C++20) automatically joins on destruction and supports cooperative cancellation via `stop_token`. This eliminates the common bug of forgetting to join or detach threads.

**Incorrect (manual thread management):**

```cpp
void processInBackground() {
    std::thread worker([] {
        // Long-running work
        heavyComputation();
    });

    // If exception thrown here, thread is not joined
    doOtherWork();

    worker.join();  // Easy to forget
}

// Or worse - detached threads that outlive main()
void fireAndForget() {
    std::thread worker(longTask);
    worker.detach();  // Undefined behavior if accesses destroyed data
}
```

**Correct (automatic joining with jthread):**

```cpp
void processInBackground() {
    std::jthread worker([] {
        heavyComputation();
    });

    doOtherWork();
    // worker automatically joined when destroyed
    // Even if exception thrown!
}
```

**Cooperative cancellation:**

```cpp
void cancellableWork() {
    std::jthread worker([](std::stop_token stopToken) {
        while (!stopToken.stop_requested()) {
            processNextItem();
        }
        // Clean shutdown when stop requested
    });

    std::this_thread::sleep_for(std::chrono::seconds(5));
    worker.request_stop();  // Signal worker to stop
    // worker joins automatically after stop
}
```

**Stop callback for cleanup:**

```cpp
void workerWithCleanup(std::stop_token token) {
    // Register cleanup callback
    std::stop_callback callback(token, [] {
        std::cout << "Cleanup triggered\n";
        releaseResources();
    });

    while (!token.stop_requested()) {
        doWork();
    }
}
```

**Multiple jthreads:**

```cpp
void parallelProcess(const std::vector<Task>& tasks) {
    std::vector<std::jthread> workers;
    workers.reserve(tasks.size());

    for (const auto& task : tasks) {
        workers.emplace_back([&task](std::stop_token st) {
            while (!st.stop_requested() && !task.done()) {
                task.processChunk();
            }
        });
    }
    // All workers automatically joined when vector destroyed
}
```

Reference: [std::jthread](https://en.cppreference.com/w/cpp/thread/jthread)
