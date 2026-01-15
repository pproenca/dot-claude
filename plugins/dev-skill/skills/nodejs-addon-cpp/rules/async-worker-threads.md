---
title: Use AsyncWorker for CPU-Intensive Tasks
impact: CRITICAL
impactDescription: prevents event loop blocking, enables true parallelism
tags: async, worker, threading, cpu-bound
---

## Use AsyncWorker for CPU-Intensive Tasks

Synchronous C++ code blocks the Node.js event loop. Use `Napi::AsyncWorker` to offload CPU-intensive work to background threads.

**Incorrect (blocks event loop):**

```cpp
Napi::Value ProcessLargeDataset(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Buffer<uint8_t> data = info[0].As<Napi::Buffer<uint8_t>>();

  // This blocks the event loop for seconds!
  std::vector<uint8_t> result = HeavyComputation(
    data.Data(),
    data.ByteLength()
  );

  return Napi::Buffer<uint8_t>::Copy(env, result.data(), result.size());
}
```

**Correct (async worker):**

```cpp
class ComputationWorker : public Napi::AsyncWorker {
 public:
  ComputationWorker(
    Napi::Function& callback,
    std::vector<uint8_t>&& input_data
  ) : Napi::AsyncWorker(callback),
      input_data_(std::move(input_data)) {}

  // Runs on background thread - doesn't block event loop
  void Execute() override {
    result_ = HeavyComputation(input_data_.data(), input_data_.size());
  }

  // Runs on main thread after Execute completes
  void OnOK() override {
    Napi::Env env = Env();
    Callback().Call({
      env.Null(),
      Napi::Buffer<uint8_t>::Copy(env, result_.data(), result_.size())
    });
  }

  void OnError(const Napi::Error& error) override {
    Callback().Call({error.Value()});
  }

 private:
  std::vector<uint8_t> input_data_;
  std::vector<uint8_t> result_;
};

Napi::Value ProcessLargeDatasetAsync(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Buffer<uint8_t> data = info[0].As<Napi::Buffer<uint8_t>>();
  Napi::Function callback = info[1].As<Napi::Function>();

  // Copy input data since buffer may be GC'd during async operation
  std::vector<uint8_t> input_copy(data.Data(), data.Data() + data.ByteLength());

  // Queue work on libuv thread pool
  ComputationWorker* worker = new ComputationWorker(callback, std::move(input_copy));
  worker->Queue();

  return env.Undefined();
}
```

**Promise-based version:**

```cpp
class ComputationWorker : public Napi::AsyncWorker {
 public:
  ComputationWorker(
    Napi::Env env,
    Napi::Promise::Deferred deferred,
    std::vector<uint8_t>&& input_data
  ) : Napi::AsyncWorker(env),
      deferred_(deferred),
      input_data_(std::move(input_data)) {}

  void Execute() override {
    result_ = HeavyComputation(input_data_.data(), input_data_.size());
  }

  void OnOK() override {
    Napi::Env env = Env();
    deferred_.Resolve(
      Napi::Buffer<uint8_t>::Copy(env, result_.data(), result_.size())
    );
  }

  void OnError(const Napi::Error& error) override {
    deferred_.Reject(error.Value());
  }

 private:
  Napi::Promise::Deferred deferred_;
  std::vector<uint8_t> input_data_;
  std::vector<uint8_t> result_;
};

Napi::Value ProcessLargeDatasetPromise(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Buffer<uint8_t> data = info[0].As<Napi::Buffer<uint8_t>>();

  Napi::Promise::Deferred deferred = Napi::Promise::Deferred::New(env);
  std::vector<uint8_t> input_copy(data.Data(), data.Data() + data.ByteLength());

  ComputationWorker* worker = new ComputationWorker(env, deferred, std::move(input_copy));
  worker->Queue();

  return deferred.Promise();
}
```

**When NOT to use this pattern:**
- Operations completing in <1ms (async overhead exceeds benefit)
- When you need synchronous result for initialization

Reference: [N-API AsyncWorker](https://nodejs.org/api/n-api.html#asynchronous-operations)
