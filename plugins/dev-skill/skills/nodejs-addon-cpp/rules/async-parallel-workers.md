---
title: Parallelize Independent Operations Across Workers
impact: CRITICAL
impactDescription: N× throughput on multi-core systems
tags: async, parallel, workers, multi-core
---

## Parallelize Independent Operations Across Workers

For operations on independent data chunks, spawn multiple async workers to utilize all CPU cores.

**Incorrect (sequential processing):**

```cpp
class SingleWorker : public Napi::AsyncWorker {
 public:
  SingleWorker(Napi::Function& cb, std::vector<Item>&& items)
      : Napi::AsyncWorker(cb), items_(std::move(items)) {}

  void Execute() override {
    // Process all items on ONE thread
    for (auto& item : items_) {
      results_.push_back(ProcessItem(item));  // Sequential!
    }
  }

  void OnOK() override { /* return results */ }

 private:
  std::vector<Item> items_;
  std::vector<Result> results_;
};
```

**Correct (parallel workers):**

```cpp
#include <atomic>

class ParallelCoordinator {
 public:
  ParallelCoordinator(
    Napi::Env env,
    Napi::Promise::Deferred deferred,
    std::vector<Item>&& items,
    size_t num_workers
  ) : env_(env),
      deferred_(deferred),
      items_(std::move(items)),
      num_workers_(num_workers),
      completed_(0) {
    results_.resize(items_.size());
  }

  void Start() {
    size_t chunk_size = (items_.size() + num_workers_ - 1) / num_workers_;

    for (size_t i = 0; i < num_workers_; i++) {
      size_t start = i * chunk_size;
      size_t end = std::min(start + chunk_size, items_.size());

      if (start < items_.size()) {
        auto* worker = new ChunkWorker(this, start, end);
        worker->Queue();
      }
    }
  }

  void OnChunkComplete(size_t start, size_t end, std::vector<Result>&& chunk_results) {
    // Copy results to correct positions
    for (size_t i = start; i < end; i++) {
      results_[i] = std::move(chunk_results[i - start]);
    }

    // Check if all workers done
    if (++completed_ == num_workers_) {
      // All done - resolve promise on main thread
      deferred_.Resolve(CreateResultArray());
    }
  }

 private:
  class ChunkWorker : public Napi::AsyncWorker {
   public:
    ChunkWorker(ParallelCoordinator* coord, size_t start, size_t end)
        : Napi::AsyncWorker(coord->env_),
          coordinator_(coord),
          start_(start),
          end_(end) {}

    void Execute() override {
      // Process chunk on this thread
      for (size_t i = start_; i < end_; i++) {
        results_.push_back(ProcessItem(coordinator_->items_[i]));
      }
    }

    void OnOK() override {
      coordinator_->OnChunkComplete(start_, end_, std::move(results_));
    }

   private:
    ParallelCoordinator* coordinator_;
    size_t start_, end_;
    std::vector<Result> results_;
  };

  Napi::Env env_;
  Napi::Promise::Deferred deferred_;
  std::vector<Item> items_;
  std::vector<Result> results_;
  size_t num_workers_;
  std::atomic<size_t> completed_;
};

Napi::Value ProcessParallel(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  auto items = ExtractItems(info[0]);

  // Use number of CPU cores
  size_t num_workers = std::thread::hardware_concurrency();

  Napi::Promise::Deferred deferred = Napi::Promise::Deferred::New(env);
  auto* coordinator = new ParallelCoordinator(
    env, deferred, std::move(items), num_workers
  );
  coordinator->Start();

  return deferred.Promise();
}
```

**Simpler approach with thread pool:**

```cpp
#include <thread>
#include <future>

void Execute() override {
  size_t num_threads = std::thread::hardware_concurrency();
  std::vector<std::future<std::vector<Result>>> futures;

  size_t chunk_size = (items_.size() + num_threads - 1) / num_threads;

  for (size_t t = 0; t < num_threads; t++) {
    size_t start = t * chunk_size;
    size_t end = std::min(start + chunk_size, items_.size());

    futures.push_back(std::async(std::launch::async, [this, start, end]() {
      std::vector<Result> chunk_results;
      for (size_t i = start; i < end; i++) {
        chunk_results.push_back(ProcessItem(items_[i]));
      }
      return chunk_results;
    }));
  }

  // Collect results
  for (auto& future : futures) {
    auto chunk = future.get();
    results_.insert(results_.end(), chunk.begin(), chunk.end());
  }
}
```

Reference: [libuv Thread Pool](https://docs.libuv.org/en/v1.x/threadpool.html)
