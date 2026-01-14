---
title: Minimize Data Marshaling Overhead
impact: MEDIUM
impactDescription: Each V8-C++ boundary crossing costs ~1-5 microseconds - batching reduces 1000 calls to 1 (1000x speedup)
tags: perf, marshaling, v8, performance, data-transfer, node-addon-api
---

# Minimize Data Marshaling Overhead

Converting JavaScript values to C++ equivalents and back has significant overhead (~1-5 microseconds per value). The cost of marshaling often exceeds the performance gains from using native code. Only use C++ when the computational work justifies the conversion cost.

## Why This Matters

Every V8-to-C++ conversion involves:
- Type checking and validation
- Memory allocation for C++ types
- Data copying across the boundary
- Reverse conversion for return values

For small operations, this overhead dominates execution time.

## Incorrect

```cpp
// PROBLEM: Each Get() + As() costs ~2-3 microseconds
// Processing 1000 users = 6+ seconds of marshaling overhead alone
#include <napi.h>
#include <vector>
#include <string>

// BAD: Converts entire object graph to C++ types
Napi::Value ProcessUserData(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Object user = info[0].As<Napi::Object>();

    // Expensive: Each property access involves marshaling
    std::string name = user.Get("name").As<Napi::String>().Utf8Value();
    std::string email = user.Get("email").As<Napi::String>().Utf8Value();
    int32_t age = user.Get("age").As<Napi::Number>().Int32Value();

    Napi::Array friends = user.Get("friends").As<Napi::Array>();
    std::vector<std::string> friendNames;

    // Very expensive: Loop with repeated marshaling
    for (uint32_t i = 0; i < friends.Length(); i++) {
        Napi::Object friendObj = friends.Get(i).As<Napi::Object>();
        friendNames.push_back(
            friendObj.Get("name").As<Napi::String>().Utf8Value()
        );
    }

    // Simple operation that doesn't justify the conversion cost
    bool isAdult = age >= 18;
    size_t friendCount = friendNames.size();

    Napi::Object result = Napi::Object::New(env);
    result.Set("isAdult", Napi::Boolean::New(env, isAdult));
    result.Set("friendCount", Napi::Number::New(env, friendCount));
    return result;
}
```

## Correct

```cpp
// SOLUTION: Use Buffer for bulk data - direct memory access, no per-element marshaling
// 1M floats via Buffer: ~0ms marshaling vs ~5 seconds for array Get() calls
#include <napi.h>
#include <cstring>
#include <cmath>

// GOOD: Accept pre-marshaled data via Buffer for heavy computation
Napi::Value ProcessSignalData(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Data arrives as Buffer - no conversion needed
    Napi::Buffer<float> inputBuffer = info[0].As<Napi::Buffer<float>>();
    float* data = inputBuffer.Data();
    size_t length = inputBuffer.Length();

    // Heavy computation that justifies native code
    double sum = 0.0;
    double sumSquares = 0.0;
    float minVal = data[0];
    float maxVal = data[0];

    for (size_t i = 0; i < length; i++) {
        float val = data[i];
        sum += val;
        sumSquares += val * val;
        if (val < minVal) minVal = val;
        if (val > maxVal) maxVal = val;
    }

    double mean = sum / length;
    double variance = (sumSquares / length) - (mean * mean);
    double stddev = std::sqrt(variance);

    // Return only computed results
    Napi::Object result = Napi::Object::New(env);
    result.Set("mean", Napi::Number::New(env, mean));
    result.Set("stddev", Napi::Number::New(env, stddev));
    result.Set("min", Napi::Number::New(env, minVal));
    result.Set("max", Napi::Number::New(env, maxVal));
    return result;
}

// GOOD: For simple property access, let JavaScript handle it
// This belongs in JavaScript, not C++:
// function processUserData(user) {
//     return {
//         isAdult: user.age >= 18,
//         friendCount: user.friends.length
//     };
// }
```

## Decision Framework

Use native code when:
- Processing large arrays of numeric data (>1000 elements)
- Performing CPU-intensive algorithms (crypto, compression, image processing)
- Interfacing with system libraries that have no JS equivalent
- Operations that would take >1ms in pure JavaScript

Keep in JavaScript when:
- Simple object property access
- String manipulation
- Small array operations
- Logic that primarily involves V8 heap objects

**When to use:** Use native code for CPU-bound operations on large datasets (>1000 elements), crypto, compression, or image processing. Pass data via Buffer/TypedArray.

**When NOT to use:** For simple object property access, string manipulation, or small arrays (<100 elements), the marshaling cost exceeds any native performance gain. Keep these in JavaScript.

## Measuring Marshaling Cost

```cpp
#include <napi.h>
#include <chrono>

// Helper to measure marshaling overhead
Napi::Value BenchmarkMarshaling(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Array input = info[0].As<Napi::Array>();
    uint32_t iterations = info[1].As<Napi::Number>().Uint32Value();

    auto start = std::chrono::high_resolution_clock::now();

    double total = 0.0;
    for (uint32_t iter = 0; iter < iterations; iter++) {
        for (uint32_t i = 0; i < input.Length(); i++) {
            // Each Get() and As() involves marshaling
            total += input.Get(i).As<Napi::Number>().DoubleValue();
        }
    }

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(
        end - start
    ).count();

    Napi::Object result = Napi::Object::New(env);
    result.Set("total", Napi::Number::New(env, total));
    result.Set("microseconds", Napi::Number::New(env, static_cast<double>(duration)));
    return result;
}
```
