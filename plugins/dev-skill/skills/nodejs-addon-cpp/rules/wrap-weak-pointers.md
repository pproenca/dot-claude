---
title: Use Weak Pointers for Observer Patterns
impact: MEDIUM-HIGH
impactDescription: enables proper cleanup in observer patterns
tags: wrap, weak, observer, prevent-gc
---

## Use Weak Pointers for Observer Patterns

When C++ objects observe JS objects, use weak references to allow JS objects to be garbage collected.

**Incorrect (strong reference prevents GC):**

```cpp
class NativeObserver {
 public:
  void Watch(const Napi::CallbackInfo& info) {
    // Strong reference - target can never be GC'd!
    target_ = Napi::Persistent(info[0].As<Napi::Object>());
  }

 private:
  Napi::Reference<Napi::Object> target_;
};
```

**Correct (weak reference allows GC):**

```cpp
class NativeObserver {
 public:
  void Watch(const Napi::CallbackInfo& info) {
    Napi::Object target = info[0].As<Napi::Object>();
    // Weak reference (ref count = 0)
    target_ = Napi::Reference<Napi::Object>::New(target, 0);
  }

  bool IsTargetAlive() {
    return !target_.IsEmpty();
  }

 private:
  Napi::Reference<Napi::Object> target_;
};
```

Reference: [Weak References in V8](https://v8.dev/features/weak-references)
