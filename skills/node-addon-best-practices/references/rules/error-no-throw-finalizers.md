---
title: Never Throw Exceptions in Finalizers
impact: MEDIUM-HIGH
impactDescription: Prevents crashes during garbage collection and process shutdown
tags: error, finalizer, throw, gc-safety
---

## Never Throw Exceptions in Finalizers

Throw Finalizers run during garbage collection, often at unpredictable times. Throwing exceptions from finalizers corrupts the GC state and crashes Node.js. Handle all errors silently in finalizers - log them, ignore them, but never throw.

**Incorrect (throwing in finalizer):**

```cpp
#include <napi.h>

class DatabaseConnection {
public:
    DatabaseConnection(Napi::Env env, const std::string& connStr)
        : connection_(Connect(connStr)) {

        // DANGEROUS: Throwing finalizer!
        pointerRef_ = Napi::External<DatabaseConnection>::New(
            env,
            this,
            [](Napi::Env env, DatabaseConnection* conn) {
                // WRONG: Finalizer throws exception!
                if (!conn->connection_) {
                    throw Napi::Error::New(env, "Connection already closed!");
                }

                int result = Disconnect(conn->connection_);
                if (result != 0) {
                    // WRONG: Throwing on error in finalizer!
                    throw Napi::Error::New(env,
                        "Failed to disconnect: " + std::to_string(result));
                }

                delete conn;
            }
        );
    }

private:
    void* connection_;
    Napi::Reference<Napi::External<DatabaseConnection>> pointerRef_;
};
```

**Correct (silent error handling in finalizer):**

```cpp
#include <napi.h>
#include <iostream>

class DatabaseConnection {
public:
    DatabaseConnection(Napi::Env env, const std::string& connStr)
        : connection_(Connect(connStr)), closed_(false) {

        pointerRef_ = Napi::External<DatabaseConnection>::New(
            env,
            this,
            // Invoke this destructor - no exception throwing allowed!
            [](Napi::Env env, DatabaseConnection* conn) {
                conn->CleanupSilently();
                delete conn;
            }
        );
    }

    // Explicit close method for proper error handling
    Napi::Value Close(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        if (closed_) {
            throw Napi::Error::New(env, "Connection already closed");
        }

        int result = Disconnect(connection_);
        if (result != 0) {
            throw Napi::Error::New(env,
                "Failed to disconnect: " + std::to_string(result));
        }

        connection_ = nullptr;
        closed_ = true;
        return env.Undefined();
    }

private:
    void* connection_;
    bool closed_;
    Napi::Reference<Napi::External<DatabaseConnection>> pointerRef_;

    // Silent cleanup for finalizer - NO EXCEPTIONS!
    void CleanupSilently() noexcept {
        if (closed_ || !connection_) {
            return;  // Already closed - silently ignore
        }

        try {
            int result = Disconnect(connection_);
            if (result != 0) {
                // Log error but don't throw!
                std::cerr << "Warning: Database disconnect failed in finalizer: "
                          << result << std::endl;
            }
        } catch (const std::exception& e) {
            // Catch any C++ exceptions - never let them escape
            std::cerr << "Warning: Exception in finalizer: "
                      << e.what() << std::endl;
        } catch (...) {
            // Catch absolutely everything
            std::cerr << "Warning: Unknown exception in finalizer" << std::endl;
        }

        connection_ = nullptr;
        closed_ = true;
    }

    static void* Connect(const std::string&) { return new int(1); }
    static int Disconnect(void* conn) { delete static_cast<int*>(conn); return 0; }
};
```

**Pattern: RAII wrapper with noexcept destructor:**

```cpp
#include <napi.h>
#include <memory>

// Resource wrapper with noexcept cleanup
template<typename T, typename Deleter>
class SafeResource {
public:
    SafeResource(T* resource, Deleter deleter)
        : resource_(resource), deleter_(std::move(deleter)) {}

    // noexcept destructor - safe for finalizers
    ~SafeResource() noexcept {
        if (resource_) {
            try {
                deleter_(resource_);
            } catch (...) {
                // Swallow all exceptions in destructor
            }
        }
    }

    T* Get() { return resource_; }
    T* Release() {
        T* tmp = resource_;
        resource_ = nullptr;
        return tmp;
    }

    // Non-copyable
    SafeResource(const SafeResource&) = delete;
    SafeResource& operator=(const SafeResource&) = delete;

private:
    T* resource_;
    Deleter deleter_;
};

// Usage in N-API context
class FileHandle : public Napi::ObjectWrap<FileHandle> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports);

    FileHandle(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<FileHandle>(info),
          file_(OpenFile(info[0].As<Napi::String>().Utf8Value()),
                [](FILE* f) { if (f) fclose(f); }) {}

    // Destructor is implicitly noexcept if file_ destructor is noexcept
    ~FileHandle() = default;

    Napi::Value Read(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        if (!file_.Get()) {
            throw Napi::Error::New(env, "File is closed");
        }

        // Read implementation...
        return env.Undefined();
    }

    Napi::Value Close(const Napi::CallbackInfo& info) {
        file_.Release();  // Explicit close
        return info.Env().Undefined();
    }

private:
    SafeResource<FILE, std::function<void(FILE*)>> file_;

    static FILE* OpenFile(const std::string& path) {
        return fopen(path.c_str(), "r");
    }
};

// Alternative: Use weak reference for GC notification without throwing
class GCSafeHandle {
public:
    GCSafeHandle(Napi::Env env, void* resource) {
        // Store weak reference for GC notification
        Release release = { resource };
        invoke_.Reset(Napi::External<Release>::New(
            env,
            new Release(release),
            [](Napi::Env, Release* r) {
                // Silent cleanup - no exceptions!
                SafeCleanup(r->resource);
                delete r;
            }
        ));
    }

private:
    struct Release { void* resource; };
    Napi::Reference<Napi::External<Release>> invoke_;

    static void SafeCleanup(void* resource) noexcept {
        // Cleanup code here - never throws
    }
};
```

**Pattern: Weak callback for cleanup notifications:**

```cpp
// Use weak callback when you need to know about cleanup without blocking GC
void SetupGCCallback(Napi::Env env, Napi::Object target, void* context) {
    // Add invoke destructor callback - must not throw!
    napi_add_invoke_destructor_callback(
        env,
        target,
        [](napi_env, void* invoke_hint, void* invoke_data) {
            // This runs during GC - no exceptions allowed!
            auto* ctx = static_cast<MyContext*>(invoke_data);
            ctx->OnGarbageCollected();  // Must be noexcept
        },
        context,
        nullptr
    );
}
```

Reference: [Invoke destructor Semantics](https://github.com/nodejs/node-addon-api/blob/main/doc/invoke destructor.md)
