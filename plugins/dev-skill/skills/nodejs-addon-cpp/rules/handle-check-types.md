---
title: Always Check Value Types Before Conversion
impact: HIGH
impactDescription: prevents crashes from type mismatches
tags: handle, types, validation, safety
---

## Always Check Value Types Before Conversion

Calling `.As<T>()` on a value of the wrong type causes undefined behavior or crashes. Always validate types first.

**Incorrect (no validation):**

```cpp
Napi::Value ProcessData(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // CRASH if info[0] is not a number
  int32_t count = info[0].As<Napi::Number>().Int32Value();

  // CRASH if info[1] is not a string
  std::string name = info[1].As<Napi::String>().Utf8Value();

  // CRASH if info[2] is not an array
  Napi::Array items = info[2].As<Napi::Array>();
}
```

**Correct (validated types):**

```cpp
Napi::Value ProcessData(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // Validate argument count
  if (info.Length() < 3) {
    Napi::TypeError::New(env, "Expected 3 arguments")
      .ThrowAsJavaScriptException();
    return env.Undefined();
  }

  // Validate and convert each argument
  if (!info[0].IsNumber()) {
    Napi::TypeError::New(env, "First argument must be a number")
      .ThrowAsJavaScriptException();
    return env.Undefined();
  }
  int32_t count = info[0].As<Napi::Number>().Int32Value();

  if (!info[1].IsString()) {
    Napi::TypeError::New(env, "Second argument must be a string")
      .ThrowAsJavaScriptException();
    return env.Undefined();
  }
  std::string name = info[1].As<Napi::String>().Utf8Value();

  if (!info[2].IsArray()) {
    Napi::TypeError::New(env, "Third argument must be an array")
      .ThrowAsJavaScriptException();
    return env.Undefined();
  }
  Napi::Array items = info[2].As<Napi::Array>();

  // Now safe to process
  return DoProcess(env, count, name, items);
}
```

**Type checking helper:**

```cpp
template<typename T>
std::optional<T> SafeCast(const Napi::Value& value);

template<>
std::optional<int32_t> SafeCast(const Napi::Value& value) {
  if (!value.IsNumber()) return std::nullopt;
  return value.As<Napi::Number>().Int32Value();
}

template<>
std::optional<std::string> SafeCast(const Napi::Value& value) {
  if (!value.IsString()) return std::nullopt;
  return value.As<Napi::String>().Utf8Value();
}

template<>
std::optional<Napi::Array> SafeCast(const Napi::Value& value) {
  if (!value.IsArray()) return std::nullopt;
  return value.As<Napi::Array>();
}

// Usage
Napi::Value ProcessData(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  auto count = SafeCast<int32_t>(info[0]);
  auto name = SafeCast<std::string>(info[1]);
  auto items = SafeCast<Napi::Array>(info[2]);

  if (!count || !name || !items) {
    Napi::TypeError::New(env, "Invalid argument types")
      .ThrowAsJavaScriptException();
    return env.Undefined();
  }

  return DoProcess(env, *count, *name, *items);
}
```

**Check for null/undefined:**

```cpp
Napi::Value ProcessOptional(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // Handle optional arguments
  std::string name = "default";
  if (info.Length() > 0 && !info[0].IsNull() && !info[0].IsUndefined()) {
    if (!info[0].IsString()) {
      Napi::TypeError::New(env, "Name must be a string if provided")
        .ThrowAsJavaScriptException();
      return env.Undefined();
    }
    name = info[0].As<Napi::String>().Utf8Value();
  }

  return Process(env, name);
}
```

Reference: [node-addon-api Type Checking](https://github.com/nodejs/node-addon-api/blob/main/doc/value.md)
