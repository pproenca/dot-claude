---
title: Use AsyncProgressWorker for Progress Updates
impact: HIGH
impactDescription: Enables real-time progress feedback without manual TSFN management
tags: async, progress, worker, streaming
---

## Use AsyncProgressWorker for Progress Updates

For background tasks that need to report progress to JavaScript, use `Napi::AsyncProgressWorker` instead of manually managing a `ThreadSafeFunction`. This class handles the complexity of cross-thread progress reporting with a simple `SendProgress()` API.

**Incorrect (manual TSFN management for progress):**

```cpp
// Overly complex manual implementation
class ManualProgressWorker : public Napi::AsyncWorker {
public:
    ManualProgressWorker(Napi::Env env,
                         Napi::Function complete,
                         Napi::Function progress)
        : Napi::AsyncWorker(complete) {
        // Manual TSFN setup - error prone!
        progressTsfn_ = Napi::ThreadSafeFunction::New(
            env, progress, "progress", 0, 1);
    }

    void Execute() override {
        for (int i = 0; i <= 100; i++) {
            DoChunk();

            // Manual progress reporting - must handle all edge cases
            int percent = i;
            napi_status status = progressTsfn_.BlockingCall(
                [percent](Napi::Env env, Napi::Function cb) {
                    cb.Call({Napi::Number::New(env, percent)});
                });

            if (status != napi_ok) break;
        }
        progressTsfn_.Release();
    }

private:
    Napi::ThreadSafeFunction progressTsfn_;
    void DoChunk() { /* work */ }
};
```

**Correct (using AsyncProgressWorker):**

```cpp
#include <napi.h>

// Simple progress data structure
struct ProgressData {
    int percent;
    std::string message;
};

class FileProcessor : public Napi::AsyncProgressWorker<ProgressData> {
public:
    FileProcessor(Napi::Env env,
                  Napi::Function progress,
                  Napi::Promise::Deferred deferred,
                  std::string filename)
        : Napi::AsyncProgressWorker<ProgressData>(env, progress),
          deferred_(deferred),
          filename_(std::move(filename)),
          bytesProcessed_(0) {}

    void Execute(const ExecutionProgress& progress) override {
        size_t totalSize = GetFileSize(filename_);

        std::ifstream file(filename_, std::ios::binary);
        char buffer[4096];

        while (file.read(buffer, sizeof(buffer)) || file.gcount() > 0) {
            size_t bytesRead = file.gcount();
            ProcessChunk(buffer, bytesRead);
            bytesProcessed_ += bytesRead;

            // Simple progress reporting - just call SendProgress!
            int percent = static_cast<int>((bytesProcessed_ * 100) / totalSize);
            progress.Send(
                new ProgressData{percent, "Processing..."},
                1  // count of items
            );
        }
    }

    // Called on main thread for each progress update
    void OnProgress(const ProgressData* data, size_t count) override {
        Napi::Env env = Env();
        Napi::Object progressObj = Napi::Object::New(env);
        progressObj.Set("percent", Napi::Number::New(env, data->percent));
        progressObj.Set("message", Napi::String::New(env, data->message));

        // Call the progress callback
        Callback().Call({progressObj});
    }

    void OnOK() override {
        deferred_.Resolve(Napi::Number::New(Env(), bytesProcessed_));
    }

    void OnError(const Napi::Error& e) override {
        deferred_.Reject(e.Value());
    }

private:
    Napi::Promise::Deferred deferred_;
    std::string filename_;
    size_t bytesProcessed_;

    size_t GetFileSize(const std::string& path) { return 1000000; }
    void ProcessChunk(const char* data, size_t len) { /* process */ }
};

// JavaScript usage:
// const promise = processFile('/path/to/file', (progress) => {
//     console.log(`${progress.percent}% - ${progress.message}`);
// });

Napi::Value ProcessFile(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    std::string filename = info[0].As<Napi::String>().Utf8Value();
    Napi::Function progressCb = info[1].As<Napi::Function>();

    auto deferred = Napi::Promise::Deferred::New(env);
    auto* worker = new FileProcessor(env, progressCb, deferred, filename);
    worker->Queue();

    return deferred.Promise();
}
```

**Alternative: AsyncProgressQueueWorker for ordered progress:**

```cpp
// Use AsyncProgressQueueWorker when progress order matters
class OrderedProgressWorker : public Napi::AsyncProgressQueueWorker<int> {
public:
    OrderedProgressWorker(Napi::Function& callback)
        : Napi::AsyncProgressQueueWorker<int>(callback) {}

    void Execute(const ExecutionProgress& progress) override {
        for (int i = 0; i < 100; i++) {
            // Progress updates are guaranteed to arrive in order
            progress.Send(&i, 1);
            DoWork();
        }
    }

    void OnProgress(const int* data, size_t count) override {
        Callback().Call({Napi::Number::New(Env(), *data)});
    }

private:
    void DoWork() { /* work */ }
};
```

Reference: [AsyncProgressWorker Documentation](https://github.com/nodejs/node-addon-api/blob/main/doc/async_worker.md#asyncprogressworker)
