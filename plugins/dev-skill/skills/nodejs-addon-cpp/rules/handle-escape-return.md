---
title: Use EscapableHandleScope for Return Values
impact: HIGH
impactDescription: prevents use-after-free crashes
tags: handle, escapable, return, scope
---

## Use EscapableHandleScope for Return Values

When a helper function creates a value that needs to be returned to the caller, use `EscapableHandleScope` and `Escape()` to promote the value out of the local scope.

**Incorrect (dangling handle):**

```cpp
Napi::Object CreateResult(Napi::Env env, int value) {
  // Regular scope - values destroyed on exit
  Napi::HandleScope scope(env);

  Napi::Object result = Napi::Object::New(env);
  result.Set("value", Napi::Number::New(env, value));

  return result;  // BUG: result's handle is invalid after scope exits!
}

Napi::Value GetResult(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  Napi::Object obj = CreateResult(env, 42);  // Dangling handle!
  obj.Set("extra", Napi::Boolean::New(env, true));  // CRASH or corruption

  return obj;
}
```

**Correct (escaped handle):**

```cpp
Napi::Object CreateResult(Napi::Env env, int value) {
  // Escapable scope - allows one value to survive
  Napi::EscapableHandleScope scope(env);

  Napi::Object result = Napi::Object::New(env);
  result.Set("value", Napi::Number::New(env, value));

  // Escape promotes handle to parent scope
  return scope.Escape(result).As<Napi::Object>();
}

Napi::Value GetResult(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  Napi::Object obj = CreateResult(env, 42);  // Valid handle
  obj.Set("extra", Napi::Boolean::New(env, true));  // Safe

  return obj;
}
```

**Escape only once:**

```cpp
Napi::Value CreateMultiple(Napi::Env env) {
  Napi::EscapableHandleScope scope(env);

  Napi::Object a = Napi::Object::New(env);
  Napi::Object b = Napi::Object::New(env);

  // BUG: Can only escape ONE value per scope
  // scope.Escape(a);
  // scope.Escape(b);  // ERROR: already escaped

  // CORRECT: Put both in a container and escape that
  Napi::Array container = Napi::Array::New(env, 2);
  container[uint32_t(0)] = a;
  container[uint32_t(1)] = b;

  return scope.Escape(container);
}
```

**Factory function pattern:**

```cpp
class WidgetFactory {
 public:
  static Napi::Object Create(Napi::Env env, const Config& config) {
    Napi::EscapableHandleScope scope(env);

    Napi::Object widget = Napi::Object::New(env);

    // Set up widget...
    widget.Set("name", Napi::String::New(env, config.name));
    widget.Set("size", CreateSize(env, config.width, config.height));

    // Note: CreateSize should also use EscapableHandleScope

    return scope.Escape(widget).As<Napi::Object>();
  }

 private:
  static Napi::Object CreateSize(Napi::Env env, int w, int h) {
    Napi::EscapableHandleScope scope(env);

    Napi::Object size = Napi::Object::New(env);
    size.Set("width", Napi::Number::New(env, w));
    size.Set("height", Napi::Number::New(env, h));

    return scope.Escape(size).As<Napi::Object>();
  }
};
```

Reference: [node-addon-api HandleScope](https://github.com/nodejs/node-addon-api/blob/main/doc/handle_scope.md)
