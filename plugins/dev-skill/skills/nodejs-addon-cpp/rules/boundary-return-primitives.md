---
title: Return Primitives Over Objects When Possible
impact: HIGH
impactDescription: 2-5× faster returns
tags: boundary, primitives, return-values, allocation
---

## Return Primitives Over Objects When Possible

Returning JS objects requires heap allocation and handle creation. Primitives (numbers, booleans) are returned inline without allocation.

**Incorrect (object return for simple result):**

```cpp
Napi::Value GetStats(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // Heap allocation for every call
  Napi::Object result = Napi::Object::New(env);
  result.Set("count", Napi::Number::New(env, count_));
  result.Set("total", Napi::Number::New(env, total_));
  result.Set("average", Napi::Number::New(env, total_ / count_));
  return result;
}
```

**Correct (primitive returns, batch object creation):**

```cpp
// Separate getters for individual values
Napi::Value GetCount(const Napi::CallbackInfo& info) {
  return Napi::Number::New(info.Env(), count_);
}

Napi::Value GetTotal(const Napi::CallbackInfo& info) {
  return Napi::Number::New(info.Env(), total_);
}

Napi::Value GetAverage(const Napi::CallbackInfo& info) {
  return Napi::Number::New(info.Env(), total_ / count_);
}

// Object version only when caller needs multiple values
Napi::Value GetStats(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Object result = Napi::Object::New(env);
  result.Set("count", Napi::Number::New(env, count_));
  result.Set("total", Napi::Number::New(env, total_));
  result.Set("average", Napi::Number::New(env, total_ / count_));
  return result;
}
```

**Alternative (return TypedArray for multiple numbers):**

```cpp
// For fixed-layout numeric results
Napi::Value GetStatsArray(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // Create ArrayBuffer once, reuse across calls
  Napi::Float64Array result = Napi::Float64Array::New(env, 3);
  double* data = result.Data();
  data[0] = count_;
  data[1] = total_;
  data[2] = total_ / count_;
  return result;
}
```

```javascript
// JS side - destructure array
const [count, total, average] = addon.getStatsArray();
```

**When NOT to use this pattern:**
- When the return structure is complex or variable
- When the caller always needs all values together

Reference: [V8 Value Representation](https://v8.dev/blog/pointer-compression)
