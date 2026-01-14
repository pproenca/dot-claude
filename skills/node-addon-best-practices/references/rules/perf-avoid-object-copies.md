---
title: Avoid Large Object Copies
impact: MEDIUM
impactDescription: Eliminates O(n) property enumeration overhead for complex objects
tags: perf, objects, copying, memory, structured-data
---

# Avoid Large Object Copies

Don't convert large JavaScript objects property-by-property. Each property access involves N-API overhead. Use TypedArrays, Buffers, or structured binary formats instead.

## Why This Matters

Converting a JavaScript object with N properties requires:
- N calls to get property names
- N calls to get property values
- N type conversions
- Memory allocation for C++ equivalents

This O(n) overhead makes deep object copying prohibitively expensive.

## Incorrect

Getting each property individually from complex objects:

```cpp
#include <napi.h>
#include <vector>
#include <string>
#include <cmath>

struct Point3D {
    double x, y, z;
};

// BAD: Property-by-property extraction
Napi::Value ProcessPoints(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Array pointsArray = info[0].As<Napi::Array>();
    uint32_t numPoints = pointsArray.Length();

    std::vector<Point3D> points;
    points.reserve(numPoints);

    // Expensive: 4 N-API calls per point (Get + 3 properties)
    for (uint32_t i = 0; i < numPoints; i++) {
        Napi::Object ptObj = pointsArray.Get(i).As<Napi::Object>();
        Point3D pt;
        pt.x = ptObj.Get("x").As<Napi::Number>().DoubleValue();
        pt.y = ptObj.Get("y").As<Napi::Number>().DoubleValue();
        pt.z = ptObj.Get("z").As<Napi::Number>().DoubleValue();
        points.push_back(pt);
    }

    // Compute centroid
    double sumX = 0, sumY = 0, sumZ = 0;
    for (const auto& pt : points) {
        sumX += pt.x;
        sumY += pt.y;
        sumZ += pt.z;
    }

    Napi::Object centroid = Napi::Object::New(env);
    centroid.Set("x", sumX / numPoints);
    centroid.Set("y", sumY / numPoints);
    centroid.Set("z", sumZ / numPoints);
    return centroid;
}

// BAD: Deep object graph traversal
Napi::Value ProcessNestedConfig(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Object config = info[0].As<Napi::Object>();

    // Each nested access multiplies N-API calls
    Napi::Object server = config.Get("server").As<Napi::Object>();
    std::string host = server.Get("host").As<Napi::String>().Utf8Value();
    int port = server.Get("port").As<Napi::Number>().Int32Value();

    Napi::Object database = config.Get("database").As<Napi::Object>();
    std::string dbHost = database.Get("host").As<Napi::String>().Utf8Value();
    int dbPort = database.Get("port").As<Napi::Number>().Int32Value();
    std::string dbName = database.Get("name").As<Napi::String>().Utf8Value();

    // ... more property access ...

    return env.Undefined();
}
```

## Correct

Use TypedArray or Buffer with structured layout:

```cpp
#include <napi.h>
#include <cmath>
#include <cstring>

// GOOD: Points as flat Float64Array [x0,y0,z0, x1,y1,z1, ...]
Napi::Value ProcessPointsFlat(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Float64Array pointsData = info[0].As<Napi::Float64Array>();
    double* data = pointsData.Data();
    size_t totalValues = pointsData.ElementLength();
    size_t numPoints = totalValues / 3;

    // Direct memory access - no per-element N-API calls
    double sumX = 0, sumY = 0, sumZ = 0;
    for (size_t i = 0; i < numPoints; i++) {
        size_t offset = i * 3;
        sumX += data[offset];
        sumY += data[offset + 1];
        sumZ += data[offset + 2];
    }

    // Return as TypedArray too
    Napi::Float64Array centroid = Napi::Float64Array::New(env, 3);
    double* result = centroid.Data();
    result[0] = sumX / numPoints;
    result[1] = sumY / numPoints;
    result[2] = sumZ / numPoints;

    return centroid;
}

// GOOD: Struct of Arrays pattern
Napi::Value ProcessPointsSoA(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Three separate arrays - better for SIMD
    Napi::Float64Array xs = info[0].As<Napi::Float64Array>();
    Napi::Float64Array ys = info[1].As<Napi::Float64Array>();
    Napi::Float64Array zs = info[2].As<Napi::Float64Array>();

    double* xData = xs.Data();
    double* yData = ys.Data();
    double* zData = zs.Data();
    size_t numPoints = xs.ElementLength();

    double sumX = 0, sumY = 0, sumZ = 0;
    for (size_t i = 0; i < numPoints; i++) {
        sumX += xData[i];
        sumY += yData[i];
        sumZ += zData[i];
    }

    Napi::Float64Array centroid = Napi::Float64Array::New(env, 3);
    double* result = centroid.Data();
    result[0] = sumX / numPoints;
    result[1] = sumY / numPoints;
    result[2] = sumZ / numPoints;

    return centroid;
}

// GOOD: Binary-packed buffer for complex structures
struct PackedRecord {
    int32_t id;
    float value;
    uint8_t flags;
    uint8_t padding[3];  // Alignment
};

Napi::Value ProcessPackedRecords(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Buffer<uint8_t> buffer = info[0].As<Napi::Buffer<uint8_t>>();
    uint8_t* data = buffer.Data();
    size_t byteLength = buffer.Length();
    size_t numRecords = byteLength / sizeof(PackedRecord);

    // Cast to struct array
    PackedRecord* records = reinterpret_cast<PackedRecord*>(data);

    // Process directly
    float totalValue = 0;
    int activeCount = 0;
    for (size_t i = 0; i < numRecords; i++) {
        totalValue += records[i].value;
        if (records[i].flags & 0x01) {
            activeCount++;
        }
    }

    Napi::Object result = Napi::Object::New(env);
    result.Set("totalValue", totalValue);
    result.Set("activeCount", activeCount);
    result.Set("recordCount", static_cast<uint32_t>(numRecords));
    return result;
}
```

## JavaScript Data Preparation

```javascript
const addon = require('./build/Release/addon');

// Convert array of point objects to flat TypedArray
function pointsToFloat64Array(points) {
    const flat = new Float64Array(points.length * 3);
    for (let i = 0; i < points.length; i++) {
        flat[i * 3] = points[i].x;
        flat[i * 3 + 1] = points[i].y;
        flat[i * 3 + 2] = points[i].z;
    }
    return flat;
}

// Usage
const points = [
    { x: 1, y: 2, z: 3 },
    { x: 4, y: 5, z: 6 },
    { x: 7, y: 8, z: 9 }
];
const flatPoints = pointsToFloat64Array(points);
const centroid = addon.processPointsFlat(flatPoints);

// Struct of Arrays approach
const xs = new Float64Array(points.map(p => p.x));
const ys = new Float64Array(points.map(p => p.y));
const zs = new Float64Array(points.map(p => p.z));
const centroidSoA = addon.processPointsSoA(xs, ys, zs);

// Binary packing for complex structures
function packRecords(records) {
    const buffer = Buffer.alloc(records.length * 12); // sizeof(PackedRecord)
    for (let i = 0; i < records.length; i++) {
        const offset = i * 12;
        buffer.writeInt32LE(records[i].id, offset);
        buffer.writeFloatLE(records[i].value, offset + 4);
        buffer.writeUInt8(records[i].flags, offset + 8);
    }
    return buffer;
}
```

## Data Layout Comparison

| Layout | N-API Calls | Cache Efficiency | Flexibility |
|--------|-------------|------------------|-------------|
| Object array | O(n * props) | Poor | High |
| Flat TypedArray | O(1) | Good | Medium |
| Struct of Arrays | O(arrays) | Excellent | Medium |
| Packed Buffer | O(1) | Excellent | Low |
