---
title: Use Persistent References for Long-Lived Values
impact: HIGH
impactDescription: prevents premature GC of stored values
tags: handle, persistent, reference, prevent-gc
---

## Use Persistent References for Long-Lived Values

Local handles are only valid within the current scope. Use `Napi::Reference` (persistent handles) for values that must survive across multiple function calls.

**Incorrect (local handle stored):**

```cpp
class EventEmitter {
 public:
  void SetCallback(const Napi::CallbackInfo& info) {
    // BUG: Local handle stored as member
    callback_ = info[0].As<Napi::Function>();
    // After this function returns, callback_ is INVALID
  }

  void Emit(const Napi::CallbackInfo& info) {
    // CRASH: callback_ is a dangling handle
    callback_.Call({});
  }

 private:
  Napi::Function callback_;  // Local handle - invalid after function returns!
};
```

**Correct (persistent reference):**

```cpp
class EventEmitter {
 public:
  void SetCallback(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Function fn = info[0].As<Napi::Function>();

    // Create persistent reference with ref count 1
    callback_ = Napi::Persistent(fn);
    callback_.SuppressDestruct();  // Manual control of destructor
  }

  void Emit(const Napi::CallbackInfo& info) {
    if (!callback_.IsEmpty()) {
      Napi::Function fn = callback_.Value();
      fn.Call({});
    }
  }

  void ClearCallback(const Napi::CallbackInfo& info) {
    callback_.Reset();  // Release reference
  }

 private:
  Napi::Reference<Napi::Function> callback_;  // Persistent - survives scopes
};
```

**Reference counting:**

```cpp
class SharedResource {
 public:
  void AddUser(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Object user = info[0].As<Napi::Object>();

    // Create reference with initial ref count 1
    auto ref = Napi::Reference<Napi::Object>::New(user, 1);
    users_.push_back(std::move(ref));
  }

  void IncrementRef(size_t index) {
    if (index < users_.size()) {
      users_[index].Ref();  // Increment ref count
    }
  }

  void DecrementRef(size_t index) {
    if (index < users_.size()) {
      uint32_t count = users_[index].Unref();  // Decrement ref count
      if (count == 0) {
        // Reference is now weak - may be GC'd
      }
    }
  }

 private:
  std::vector<Napi::Reference<Napi::Object>> users_;
};
```

**Weak reference pattern:**

```cpp
class Cache {
 public:
  void Store(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    std::string key = info[0].As<Napi::String>().Utf8Value();
    Napi::Object value = info[1].As<Napi::Object>();

    // Weak reference (ref count 0) - doesn't prevent GC
    auto ref = Napi::Reference<Napi::Object>::New(value, 0);
    cache_[key] = std::move(ref);
  }

  Napi::Value Get(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    std::string key = info[0].As<Napi::String>().Utf8Value();

    auto it = cache_.find(key);
    if (it != cache_.end() && !it->second.IsEmpty()) {
      return it->second.Value();
    }

    return env.Undefined();
  }

 private:
  std::unordered_map<std::string, Napi::Reference<Napi::Object>> cache_;
};
```

Reference: [node-addon-api Reference](https://github.com/nodejs/node-addon-api/blob/main/doc/reference.md)
