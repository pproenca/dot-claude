---
title: Don't Block the Event Loop
impact: LOW
impactDescription: Prevents application freezes and responsiveness issues
tags: pitfall, event-loop, async, blocking, performance
---

# Don't Block the Event Loop

Avoid synchronous I/O or long-running computations in synchronous callbacks. Blocking operations freeze the entire Node.js process, preventing it from handling other requests.

## Why This Matters

- Node.js is single-threaded for JavaScript execution
- Blocking operations halt all concurrent requests
- HTTP requests time out while waiting
- User interfaces become unresponsive

## Incorrect

Synchronous blocking operations in callbacks:

```cpp
#include <napi.h>
#include <fstream>
#include <thread>
#include <chrono>

// BAD: Synchronous file read blocks event loop
Napi::Value ReadFileSyncBad(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    std::string path = info[0].As<Napi::String>().Utf8Value();

    // BLOCKS: Entire Node.js process waits for disk I/O
    std::ifstream file(path);
    std::string content((std::istreambuf_iterator<char>(file)),
                         std::istreambuf_iterator<char>());

    return Napi::String::New(env, content);
}

// BAD: Long computation in sync callback
Napi::Value HeavyComputationBad(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    uint64_t n = info[0].As<Napi::Number>().Int64Value();

    // BLOCKS: 10 second computation freezes everything
    uint64_t result = 0;
    for (uint64_t i = 0; i < n; i++) {
        result += i * i;
    }

    return Napi::Number::New(env, static_cast<double>(result));
}

// BAD: Sleep in sync callback
Napi::Value WaitBad(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    int ms = info[0].As<Napi::Number>().Int32Value();

    // BLOCKS: Thread sleep freezes event loop
    std::this_thread::sleep_for(std::chrono::milliseconds(ms));

    return env.Undefined();
}
```

## Correct

Use AsyncWorker for blocking operations:

```cpp
#include <napi.h>
#include <fstream>
#include <string>
#include <thread>
#include <chrono>

// GOOD: Async file read using AsyncWorker
class ReadFileWorker : public Napi::AsyncWorker {
public:
    ReadFileWorker(const Napi::Env& env,
                   const std::string& path,
                   Napi::Promise::Deferred deferred)
        : Napi::AsyncWorker(env),
          path_(path),
          deferred_(deferred) {}

    void Execute() override {
        // Runs on worker thread - safe to block
        std::ifstream file(path_);
        if (!file.is_open()) {
            SetError("Failed to open file: " + path_);
            return;
        }

        content_ = std::string(
            (std::istreambuf_iterator<char>(file)),
            std::istreambuf_iterator<char>()
        );
    }

    void OnOK() override {
        // Runs on main thread
        deferred_.Resolve(Napi::String::New(Env(), content_));
    }

    void OnError(const Napi::Error& err) override {
        deferred_.Reject(err.Value());
    }

private:
    std::string path_;
    std::string content_;
    Napi::Promise::Deferred deferred_;
};

Napi::Value ReadFileAsync(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    std::string path = info[0].As<Napi::String>().Utf8Value();

    auto deferred = Napi::Promise::Deferred::New(env);
    auto* worker = new ReadFileWorker(env, path, deferred);
    worker->Queue();

    return deferred.Promise();
}

// GOOD: Heavy computation on worker thread
class ComputeWorker : public Napi::AsyncWorker {
public:
    ComputeWorker(const Napi::Env& env,
                  uint64_t n,
                  Napi::Promise::Deferred deferred)
        : Napi::AsyncWorker(env),
          n_(n),
          deferred_(deferred),
          result_(0) {}

    void Execute() override {
        // Heavy computation on worker thread
        for (uint64_t i = 0; i < n_; i++) {
            result_ += i * i;
        }
    }

    void OnOK() override {
        deferred_.Resolve(Napi::Number::New(Env(), static_cast<double>(result_)));
    }

    void OnError(const Napi::Error& err) override {
        deferred_.Reject(err.Value());
    }

private:
    uint64_t n_;
    Napi::Promise::Deferred deferred_;
    uint64_t result_;
};

Napi::Value HeavyComputationAsync(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    uint64_t n = info[0].As<Napi::Number>().Int64Value();

    auto deferred = Napi::Promise::Deferred::New(env);
    auto* worker = new ComputeWorker(env, n, deferred);
    worker->Queue();

    return deferred.Promise();
}
```

## Chunked Processing Pattern

For operations that must be synchronous but can be split:

```cpp
#include <napi.h>

// GOOD: Process in chunks, yielding between chunks
class ChunkedProcessor : public Napi::ObjectWrap<ChunkedProcessor> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "ChunkedProcessor", {
            InstanceMethod("processChunk", &ChunkedProcessor::ProcessChunk),
            InstanceMethod("isComplete", &ChunkedProcessor::IsComplete),
            InstanceMethod("getResult", &ChunkedProcessor::GetResult)
        });
        exports.Set("ChunkedProcessor", func);
        return exports;
    }

    ChunkedProcessor(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<ChunkedProcessor>(info) {

        uint64_t total = info[0].As<Napi::Number>().Int64Value();
        total_ = total;
        current_ = 0;
        result_ = 0;
    }

    Napi::Value ProcessChunk(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        // Process a small chunk (doesn't block long)
        const uint64_t CHUNK_SIZE = 10000;
        uint64_t end = std::min(current_ + CHUNK_SIZE, total_);

        for (uint64_t i = current_; i < end; i++) {
            result_ += i * i;
        }
        current_ = end;

        // Return progress
        return Napi::Number::New(env,
            static_cast<double>(current_) / total_);
    }

    Napi::Value IsComplete(const Napi::CallbackInfo& info) {
        return Napi::Boolean::New(info.Env(), current_ >= total_);
    }

    Napi::Value GetResult(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), static_cast<double>(result_));
    }

private:
    uint64_t total_;
    uint64_t current_;
    uint64_t result_;
};
```

## JavaScript Usage

```javascript
const addon = require('./build/Release/addon');

// Async operations (recommended)
async function processFiles() {
    const content = await addon.readFileAsync('/path/to/large/file.txt');
    const result = await addon.heavyComputationAsync(1000000000);
    return { content, result };
}

// Chunked processing when async isn't possible
function processChunked(total) {
    const processor = new addon.ChunkedProcessor(total);

    return new Promise((resolve) => {
        function tick() {
            const progress = processor.processChunk();

            if (processor.isComplete()) {
                resolve(processor.getResult());
            } else {
                // Yield to event loop between chunks
                setImmediate(tick);
            }
        }
        tick();
    });
}
```

## When Sync is Acceptable

- Startup/initialization (before server listens)
- CLI tools (no concurrent requests)
- Operations completing in <1ms
- Module loading (require-time)

## Detecting Event Loop Blocking

```javascript
// Monitor event loop lag
const start = process.hrtime.bigint();
setImmediate(() => {
    const lag = Number(process.hrtime.bigint() - start) / 1_000_000;
    if (lag > 10) {
        console.warn(`Event loop blocked for ${lag}ms`);
    }
});
```
