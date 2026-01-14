---
title: Batch Small Operations
impact: MEDIUM
impactDescription: 10-50x throughput improvement by reducing N-API call overhead
tags: perf, batching, throughput, call-overhead, arrays
---

# Batch Small Operations

Process data in batches rather than making repeated N-API calls for each element. Each N-API call has overhead; batching amortizes this cost across many operations.

## Why This Matters

Each N-API function call involves:
- Parameter validation
- Handle scope management
- Potential JavaScript engine interaction
- Function call overhead

For 1000 elements, batching converts 1000+ N-API calls into 1-2 calls.

## Incorrect

Calling N-API repeatedly in a loop:

```cpp
#include <napi.h>
#include <cmath>

// BAD: N-API call for every array element
Napi::Value TransformArray(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Array input = info[0].As<Napi::Array>();
    uint32_t length = input.Length();

    Napi::Array output = Napi::Array::New(env, length);

    // Expensive: Each iteration makes multiple N-API calls
    for (uint32_t i = 0; i < length; i++) {
        // N-API call: Get element from input
        Napi::Value elem = input.Get(i);
        // N-API call: Convert to number
        double val = elem.As<Napi::Number>().DoubleValue();

        // Actual computation (trivial)
        double result = std::sqrt(val) * 2.0;

        // N-API call: Create new number
        Napi::Number newNum = Napi::Number::New(env, result);
        // N-API call: Set in output array
        output.Set(i, newNum);
    }

    return output;
}

// BAD: Building result object property by property
Napi::Value ComputeStatistics(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Array data = info[0].As<Napi::Array>();
    uint32_t length = data.Length();

    double sum = 0, min = 0, max = 0;

    // Multiple N-API calls per element
    for (uint32_t i = 0; i < length; i++) {
        double val = data.Get(i).As<Napi::Number>().DoubleValue();
        sum += val;
        if (i == 0 || val < min) min = val;
        if (i == 0 || val > max) max = val;
    }

    Napi::Object result = Napi::Object::New(env);
    result.Set("sum", sum);
    result.Set("min", min);
    result.Set("max", max);
    result.Set("mean", sum / length);
    return result;
}
```

## Correct

Process entire array in single native call with TypedArrays:

```cpp
#include <napi.h>
#include <cmath>
#include <algorithm>

// GOOD: Single call processes entire array via TypedArray
Napi::Value TransformTypedArray(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Get direct pointer - no per-element N-API calls
    Napi::Float64Array input = info[0].As<Napi::Float64Array>();
    double* inputData = input.Data();
    size_t length = input.ElementLength();

    // Create output TypedArray
    Napi::Float64Array output = Napi::Float64Array::New(env, length);
    double* outputData = output.Data();

    // Pure C++ loop - no N-API overhead
    for (size_t i = 0; i < length; i++) {
        outputData[i] = std::sqrt(inputData[i]) * 2.0;
    }

    return output;
}

// GOOD: Batch statistics computation
Napi::Value ComputeStatisticsBatched(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Float64Array data = info[0].As<Napi::Float64Array>();
    double* ptr = data.Data();
    size_t length = data.ElementLength();

    if (length == 0) {
        Napi::Object result = Napi::Object::New(env);
        result.Set("sum", 0.0);
        result.Set("min", 0.0);
        result.Set("max", 0.0);
        result.Set("mean", 0.0);
        return result;
    }

    // Pure C++ computation - no N-API calls in loop
    double sum = 0.0;
    double min = ptr[0];
    double max = ptr[0];

    for (size_t i = 0; i < length; i++) {
        double val = ptr[i];
        sum += val;
        if (val < min) min = val;
        if (val > max) max = val;
    }

    // Single batch of N-API calls to create result
    Napi::Object result = Napi::Object::New(env);
    result.Set("sum", sum);
    result.Set("min", min);
    result.Set("max", max);
    result.Set("mean", sum / static_cast<double>(length));
    return result;
}
```

## Batch Processing Multiple Arrays

```cpp
#include <napi.h>
#include <cmath>

// GOOD: Process multiple arrays in single call
Napi::Value BatchVectorOperations(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Accept array of TypedArrays
    Napi::Array vectors = info[0].As<Napi::Array>();
    uint32_t numVectors = vectors.Length();

    // Pre-allocate result array
    Napi::Float64Array magnitudes = Napi::Float64Array::New(env, numVectors);
    double* magData = magnitudes.Data();

    // Process all vectors in single call
    for (uint32_t v = 0; v < numVectors; v++) {
        Napi::Float64Array vec = vectors.Get(v).As<Napi::Float64Array>();
        double* vecData = vec.Data();
        size_t dims = vec.ElementLength();

        double sumSquares = 0.0;
        for (size_t i = 0; i < dims; i++) {
            sumSquares += vecData[i] * vecData[i];
        }
        magData[v] = std::sqrt(sumSquares);
    }

    return magnitudes;
}

// GOOD: Batch matrix operations
Napi::Value BatchMatrixMultiply(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Matrices as flat TypedArrays with dimensions
    Napi::Float64Array matA = info[0].As<Napi::Float64Array>();
    Napi::Float64Array matB = info[1].As<Napi::Float64Array>();
    uint32_t rowsA = info[2].As<Napi::Number>().Uint32Value();
    uint32_t colsA = info[3].As<Napi::Number>().Uint32Value();
    uint32_t colsB = info[4].As<Napi::Number>().Uint32Value();

    double* a = matA.Data();
    double* b = matB.Data();

    // Allocate result
    Napi::Float64Array result = Napi::Float64Array::New(env, rowsA * colsB);
    double* c = result.Data();

    // Pure C++ matrix multiplication
    for (uint32_t i = 0; i < rowsA; i++) {
        for (uint32_t j = 0; j < colsB; j++) {
            double sum = 0.0;
            for (uint32_t k = 0; k < colsA; k++) {
                sum += a[i * colsA + k] * b[k * colsB + j];
            }
            c[i * colsB + j] = sum;
        }
    }

    return result;
}
```

## JavaScript Usage

```javascript
const addon = require('./build/Release/addon');

// Batch processing with TypedArrays
const input = new Float64Array([1, 4, 9, 16, 25, 36, 49, 64, 81, 100]);
const transformed = addon.transformTypedArray(input);
// Result: Float64Array [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

// Batch statistics
const data = new Float64Array(10000);
for (let i = 0; i < data.length; i++) {
    data[i] = Math.random() * 100;
}
const stats = addon.computeStatisticsBatched(data);
// Result: { sum: ..., min: ..., max: ..., mean: ... }

// Batch vector operations
const vectors = [
    new Float64Array([3, 4]),      // magnitude: 5
    new Float64Array([1, 1, 1]),   // magnitude: sqrt(3)
    new Float64Array([0, 5, 12])   // magnitude: 13
];
const magnitudes = addon.batchVectorOperations(vectors);
```

## Performance Comparison

| Approach | 10K elements | N-API Calls |
|----------|--------------|-------------|
| Per-element | ~50ms | 40,000+ |
| Batched TypedArray | ~1ms | ~5 |
