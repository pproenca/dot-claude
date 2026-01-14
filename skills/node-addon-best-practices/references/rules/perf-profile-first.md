---
title: Profile Before Optimizing
impact: MEDIUM
impactDescription: Prevents wasted effort on optimizations that provide no benefit
tags: perf, profiling, benchmarking, measurement, optimization
---

# Profile Before Optimizing

Benchmark your addon against pure JavaScript before assuming C++ will be faster. The overhead of crossing the N-API boundary can exceed the gains from native code for many operations.

## Why This Matters

Native code is NOT always faster because:
- N-API call overhead: ~100-500ns per crossing
- Data marshaling: O(n) for arrays/strings
- V8 is highly optimized for JS-native patterns
- JIT compilation optimizes hot paths

Profile to find where native code actually helps.

## Incorrect

Assuming native implementation is always faster:

```cpp
#include <napi.h>
#include <string>
#include <algorithm>

// BAD: Assumed to be faster, but probably isn't
Napi::Value ToUpperCase(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // String marshaling cost
    std::string input = info[0].As<Napi::String>().Utf8Value();

    // Trivial operation
    std::transform(input.begin(), input.end(), input.begin(), ::toupper);

    // String marshaling cost again
    return Napi::String::New(env, input);
}

// BAD: Simple math that V8 handles efficiently
Napi::Value AddNumbers(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    double a = info[0].As<Napi::Number>().DoubleValue();
    double b = info[1].As<Napi::Number>().DoubleValue();

    return Napi::Number::New(env, a + b);
}
```

## Correct

Measure and compare before committing to native:

```cpp
#include <napi.h>
#include <chrono>
#include <cmath>
#include <vector>

// GOOD: Benchmark harness for accurate measurement
Napi::Value BenchmarkNative(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Float64Array data = info[0].As<Napi::Float64Array>();
    uint32_t iterations = info[1].As<Napi::Number>().Uint32Value();

    double* ptr = data.Data();
    size_t length = data.ElementLength();

    auto start = std::chrono::high_resolution_clock::now();

    double result = 0.0;
    for (uint32_t iter = 0; iter < iterations; iter++) {
        for (size_t i = 0; i < length; i++) {
            result += std::sin(ptr[i]) * std::cos(ptr[i]);
        }
    }

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(
        end - start
    ).count();

    Napi::Object response = Napi::Object::New(env);
    response.Set("result", result);
    response.Set("microseconds", static_cast<double>(duration));
    response.Set("opsPerSecond",
        (iterations * length * 1000000.0) / duration);
    return response;
}

// GOOD: Include marshaling cost in benchmark
Napi::Value BenchmarkWithMarshaling(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // This measures total cost including marshaling
    Napi::Array input = info[0].As<Napi::Array>();
    uint32_t iterations = info[1].As<Napi::Number>().Uint32Value();

    auto start = std::chrono::high_resolution_clock::now();

    double result = 0.0;
    for (uint32_t iter = 0; iter < iterations; iter++) {
        uint32_t length = input.Length();
        for (uint32_t i = 0; i < length; i++) {
            double val = input.Get(i).As<Napi::Number>().DoubleValue();
            result += std::sin(val) * std::cos(val);
        }
    }

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(
        end - start
    ).count();

    Napi::Object response = Napi::Object::New(env);
    response.Set("result", result);
    response.Set("microseconds", static_cast<double>(duration));
    return response;
}
```

## JavaScript Benchmark Comparison

```javascript
const addon = require('./build/Release/addon');

// Benchmark utility
function benchmark(name, fn, iterations = 1000) {
    // Warmup
    for (let i = 0; i < 100; i++) fn();

    const start = process.hrtime.bigint();
    for (let i = 0; i < iterations; i++) {
        fn();
    }
    const end = process.hrtime.bigint();

    const ms = Number(end - start) / 1_000_000;
    console.log(`${name}: ${ms.toFixed(2)}ms for ${iterations} iterations`);
    return ms;
}

// Compare JS vs Native for string operations
const testString = 'hello world '.repeat(100);

benchmark('JS toUpperCase', () => {
    testString.toUpperCase();
});

benchmark('Native toUpperCase', () => {
    addon.toUpperCase(testString);
});

// Compare for numeric operations
const data = new Float64Array(10000);
for (let i = 0; i < data.length; i++) {
    data[i] = Math.random() * Math.PI;
}

// Pure JS implementation
function jsCompute(arr) {
    let result = 0;
    for (let i = 0; i < arr.length; i++) {
        result += Math.sin(arr[i]) * Math.cos(arr[i]);
    }
    return result;
}

benchmark('JS sin*cos', () => {
    jsCompute(data);
});

// Native with TypedArray (low marshaling)
const nativeResult = addon.benchmarkNative(data, 1);
console.log(`Native sin*cos: ${nativeResult.microseconds}us`);

// Native with Array (high marshaling)
const arrayData = Array.from(data);
const marshaledResult = addon.benchmarkWithMarshaling(arrayData, 1);
console.log(`Native with marshaling: ${marshaledResult.microseconds}us`);

// Call overhead benchmark
function measureCallOverhead() {
    const iterations = 100000;

    // Measure N-API call overhead
    const start = process.hrtime.bigint();
    for (let i = 0; i < iterations; i++) {
        addon.addNumbers(1, 2);  // Trivial operation
    }
    const end = process.hrtime.bigint();

    const nsPerCall = Number(end - start) / iterations;
    console.log(`N-API call overhead: ~${nsPerCall.toFixed(0)}ns per call`);
}

measureCallOverhead();
```

## When Native Code Wins

```javascript
// Native wins for:
// 1. Large array processing with TypedArrays
// 2. CPU-intensive algorithms (crypto, compression)
// 3. System library bindings (no JS equivalent)

// Native loses for:
// 1. Small data operations
// 2. Frequent small calls
// 3. String-heavy operations
// 4. Object property access

// Decision checklist
function shouldUseNative(operation) {
    const criteria = {
        dataSize: 'Is data size > 1000 elements?',
        cpuIntensive: 'Is computation > 1ms in pure JS?',
        systemBinding: 'Does it require system libraries?',
        frequentCalls: 'Will it be called > 1000x/second with small data?',
        stringHeavy: 'Is it primarily string manipulation?'
    };

    // Native if: (dataSize || cpuIntensive || systemBinding)
    //            && !frequentCalls && !stringHeavy
}
```

## Profiling Tools

| Tool | Use For |
|------|---------|
| `process.hrtime.bigint()` | Micro-benchmarks |
| `perf_hooks` | Detailed timing |
| `--prof` flag | V8 profiler |
| Clinic.js | Node.js profiling |
| Instruments (macOS) | Native profiling |
| perf (Linux) | System profiling |

## Sample Output Analysis

```
Operation              JS Time    Native Time   Winner
----------------------------------------------------------
String uppercase       2.1ms      8.5ms         JS (4x faster)
Array sum (1K)         0.3ms      0.4ms         JS (1.3x faster)
Array sum (100K)       12ms       3ms           Native (4x faster)
Matrix multiply        250ms      45ms          Native (5x faster)
JSON parse             15ms       18ms          JS (1.2x faster)
Image resize           800ms      120ms         Native (6x faster)
```

Always measure your specific use case - generalizations don't apply uniformly.
