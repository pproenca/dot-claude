---
title: Use DefineClass for Object-Oriented APIs
impact: MEDIUM
impactDescription: cleaner API with proper prototype chain
tags: napi, class, define, oop
---

## Use DefineClass for Object-Oriented APIs

Use `Napi::ObjectWrap` with `DefineClass` to create proper JavaScript classes with methods and properties.

**Incorrect (manual object setup):**

```cpp
Napi::Value CreateCounter(const Napi::CallbackInfo& info) {
  Napi::Object obj = Napi::Object::New(info.Env());
  // Manually adding methods - no prototype, no instanceof
  obj.Set("increment", Napi::Function::New(info.Env(), Increment));
  return obj;
}
```

**Correct (DefineClass):**

```cpp
class Counter : public Napi::ObjectWrap<Counter> {
 public:
  static Napi::Object Init(Napi::Env env, Napi::Object exports) {
    Napi::Function func = DefineClass(env, "Counter", {
      InstanceMethod("increment", &Counter::Increment),
      InstanceAccessor("value", &Counter::GetValue, nullptr),
    });

    exports.Set("Counter", func);
    return exports;
  }

  Counter(const Napi::CallbackInfo& info)
      : Napi::ObjectWrap<Counter>(info), value_(0) {}

 private:
  Napi::Value Increment(const Napi::CallbackInfo& info) {
    return Napi::Number::New(info.Env(), ++value_);
  }

  Napi::Value GetValue(const Napi::CallbackInfo& info) {
    return Napi::Number::New(info.Env(), value_);
  }

  int value_;
};
```

Reference: [ObjectWrap](https://github.com/nodejs/node-addon-api/blob/main/doc/object_wrap.md)
