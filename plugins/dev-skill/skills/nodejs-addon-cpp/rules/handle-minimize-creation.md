---
title: Minimize Handle Creation in Hot Paths
impact: MEDIUM-HIGH
impactDescription: reduces GC pressure and improves throughput
tags: handle, allocation, performance, hot-path
---

## Minimize Handle Creation in Hot Paths

Every `Napi::Value` creation allocates a handle. In hot paths, minimize handle creation by reusing values and batching operations.

**Incorrect (excessive handles):**

```cpp
Napi::Value SumProducts(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array items = info[0].As<Napi::Array>();

  double total = 0;
  for (uint32_t i = 0; i < items.Length(); i++) {
    Napi::HandleScope scope(env);
    Napi::Object item = items[i].As<Napi::Object>();

    // Creating string handles on every iteration
    Napi::Value price = item.Get("price");      // "price" → new handle
    Napi::Value quantity = item.Get("quantity"); // "quantity" → new handle

    total += price.As<Napi::Number>().DoubleValue() *
             quantity.As<Napi::Number>().DoubleValue();
  }

  return Napi::Number::New(env, total);
}
```

**Correct (cached property names):**

```cpp
// Module-level cached keys
static Napi::Reference<Napi::String> priceKey;
static Napi::Reference<Napi::String> quantityKey;

Napi::Object Init(Napi::Env env, Napi::Object exports) {
  // Create once at init
  priceKey = Napi::Persistent(Napi::String::New(env, "price"));
  quantityKey = Napi::Persistent(Napi::String::New(env, "quantity"));

  exports.Set("sumProducts",
    Napi::Function::New(env, SumProducts));
  return exports;
}

Napi::Value SumProducts(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array items = info[0].As<Napi::Array>();

  // Get cached keys once
  Napi::String pKey = priceKey.Value();
  Napi::String qKey = quantityKey.Value();

  double total = 0;
  for (uint32_t i = 0; i < items.Length(); i++) {
    Napi::HandleScope scope(env);
    Napi::Object item = items[i].As<Napi::Object>();

    // Reuse cached key handles
    total += item.Get(pKey).As<Napi::Number>().DoubleValue() *
             item.Get(qKey).As<Napi::Number>().DoubleValue();
  }

  return Napi::Number::New(env, total);
}
```

**Even better (use TypedArrays):**

```cpp
// JavaScript preprocessing:
// const prices = new Float64Array(items.map(i => i.price));
// const quantities = new Float64Array(items.map(i => i.quantity));
// addon.sumProductsOptimized(prices, quantities);

Napi::Value SumProductsOptimized(const Napi::CallbackInfo& info) {
  Napi::Float64Array prices = info[0].As<Napi::Float64Array>();
  Napi::Float64Array quantities = info[1].As<Napi::Float64Array>();

  double* p = prices.Data();
  double* q = quantities.Data();
  size_t len = prices.ElementLength();

  double total = 0;
  for (size_t i = 0; i < len; i++) {
    total += p[i] * q[i];  // No handles at all in loop!
  }

  return Napi::Number::New(info.Env(), total);
}
```

**Batch return value creation:**

```cpp
// BAD - creates handles in loop then copies to array
Napi::Value ProcessAll(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  std::vector<Napi::Value> results;

  for (size_t i = 0; i < count; i++) {
    results.push_back(Napi::Number::New(env, Process(i)));
  }

  Napi::Array arr = Napi::Array::New(env, results.size());
  for (size_t i = 0; i < results.size(); i++) {
    arr[i] = results[i];
  }
  return arr;
}

// GOOD - create array first, fill directly
Napi::Value ProcessAll(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  Napi::Array arr = Napi::Array::New(env, count);
  for (size_t i = 0; i < count; i++) {
    arr[i] = Napi::Number::New(env, Process(i));
  }
  return arr;
}
```

Reference: [V8 Handles and Garbage Collection](https://v8.dev/docs/embed#handles-and-garbage-collection)
