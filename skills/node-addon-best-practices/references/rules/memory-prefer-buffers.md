---
title: Prefer Buffers for Large Data
impact: CRITICAL
impactDescription: String copying of large data doubles memory usage and causes GC pressure
tags: memory, buffers, performance, data-transfer
---

# Prefer Buffers for Large Data

Use `Buffer` or `ArrayBuffer` instead of strings for transferring large binary data between JavaScript and native code. Buffers can share memory without copying, while strings always copy and encode.

## Why This Matters

- **Zero-Copy Possible**: Buffers can directly expose native memory
- **Memory Efficiency**: Avoid doubling memory with copies
- **Performance**: No UTF-8 encoding/decoding overhead
- **Large Data Support**: Handle multi-gigabyte data efficiently

## Understanding the Difference

| Aspect | String | Buffer |
|--------|--------|--------|
| Encoding | UTF-8 converted | Raw bytes |
| Memory | Always copies | Can share |
| Size limit | ~512MB practical | System memory |
| GC pressure | High (copies) | Low (external) |

## Incorrect: Large Data as String

```cpp
// BAD: Copying large data through strings
Napi::Value ReadFile(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    std::string path = info[0].As<Napi::String>().Utf8Value();

    // Read file into native buffer
    FILE* f = fopen(path.c_str(), "rb");
    fseek(f, 0, SEEK_END);
    size_t size = ftell(f);  // Could be 100MB+
    fseek(f, 0, SEEK_SET);

    char* data = new char[size];
    fread(data, 1, size, f);
    fclose(f);

    // BAD: Creating string copies the entire buffer!
    // Memory usage: 100MB (native) + 100MB (V8 heap) = 200MB
    Napi::String result = Napi::String::New(env, data, size);

    delete[] data;  // Native freed, but V8 copy remains

    return result;
    // Total allocation was 200MB for 100MB of data
}
```

```javascript
// JavaScript usage causes memory spike
const content = addon.readFile('large-file.dat');  // 200MB used
// content is now a string - can't avoid the copy
```

## Incorrect: String Round-Trip for Binary

```cpp
// BAD: Binary data through strings corrupts data
Napi::Value ProcessImage(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // BAD: String interpretation corrupts binary data
    std::string imageData = info[0].As<Napi::String>().Utf8Value();
    // Binary 0xFF sequences get corrupted by UTF-8 encoding!

    // Process corrupted data...
    ProcessImageData((uint8_t*)imageData.data(), imageData.size());

    // Return corrupted result as string
    return Napi::String::New(env, imageData);
}
```

## Correct: Buffer Without Copy (External Memory)

```cpp
// GOOD: Zero-copy buffer sharing native memory
Napi::Value ReadFileZeroCopy(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    std::string path = info[0].As<Napi::String>().Utf8Value();

    // Read file
    FILE* f = fopen(path.c_str(), "rb");
    if (!f) {
        throw Napi::Error::New(env, "Failed to open file");
    }

    fseek(f, 0, SEEK_END);
    size_t size = ftell(f);
    fseek(f, 0, SEEK_SET);

    uint8_t* data = new uint8_t[size];
    size_t bytesRead = fread(data, 1, size, f);
    fclose(f);

    // GOOD: Create buffer that wraps existing memory
    // No copy - JavaScript sees the same bytes
    return Napi::Buffer<uint8_t>::New(
        env,
        data,
        bytesRead,
        // Destructor called when Buffer is garbage collected
        [](Napi::Env /*env*/, uint8_t* data) {
            delete[] data;
        }
    );
    // Memory usage: Only ~100MB (shared between native and JS)
}
```

```javascript
// JavaScript usage - efficient
const buffer = addon.readFileZeroCopy('large-file.dat');  // 100MB used
// buffer is a Buffer - direct access to native memory
```

## Correct: ArrayBuffer for Typed Access

```cpp
// GOOD: ArrayBuffer for efficient typed array usage
Napi::Value CreateFloatArray(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    size_t count = info[0].As<Napi::Number>().Uint32Value();

    // Allocate native float array
    size_t byteLength = count * sizeof(float);
    float* data = new float[count];

    // Initialize data
    for (size_t i = 0; i < count; i++) {
        data[i] = static_cast<float>(i) * 0.5f;
    }

    // Create ArrayBuffer wrapping native memory
    Napi::ArrayBuffer arrayBuffer = Napi::ArrayBuffer::New(
        env,
        data,
        byteLength,
        [](Napi::Env /*env*/, void* data) {
            delete[] static_cast<float*>(data);
        }
    );

    // Return as Float32Array for convenient typed access
    return Napi::Float32Array::New(env, count, arrayBuffer, 0);
}
```

```javascript
// JavaScript usage - efficient typed array access
const floats = addon.createFloatArray(1000000);
console.log(floats[0], floats[1]);  // 0, 0.5
// Direct memory access, no copying
```

## Pattern: Processing Buffer In-Place

```cpp
// GOOD: Modify buffer data in place
Napi::Value InvertImage(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (!info[0].IsBuffer()) {
        throw Napi::TypeError::New(env, "Expected Buffer");
    }

    Napi::Buffer<uint8_t> buffer = info[0].As<Napi::Buffer<uint8_t>>();
    uint8_t* data = buffer.Data();
    size_t length = buffer.Length();

    // Process in place - no copy needed
    for (size_t i = 0; i < length; i++) {
        data[i] = 255 - data[i];
    }

    // Return same buffer - data modified in place
    return buffer;
}
```

```javascript
// JavaScript usage - modify in place
const imageData = fs.readFileSync('image.raw');
addon.invertImage(imageData);  // Modified in place!
fs.writeFileSync('inverted.raw', imageData);
```

## Pattern: Copy Only When Necessary

```cpp
// GOOD: Use Copy only when you need separate memory
Napi::Value CloneBuffer(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Buffer<uint8_t> input = info[0].As<Napi::Buffer<uint8_t>>();

    // Copy is appropriate here - we need independent memory
    return Napi::Buffer<uint8_t>::Copy(env, input.Data(), input.Length());
}

// Contrast with zero-copy when appropriate
Napi::Value WrapExistingMemory(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Memory owned by this addon - share it, don't copy
    return Napi::Buffer<uint8_t>::New(
        env,
        sharedMemory_,
        sharedMemorySize_,
        // No finalizer - we manage the memory lifecycle
        [](Napi::Env, void*) { /* intentionally empty */ }
    );
}
```

## Pattern: Large Data Transfer with Streaming

```cpp
// GOOD: Stream large data in chunks
class DataStreamer : public Napi::ObjectWrap<DataStreamer> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "DataStreamer", {
            InstanceMethod("nextChunk", &DataStreamer::NextChunk),
            InstanceMethod("hasMore", &DataStreamer::HasMore)
        });
        exports.Set("DataStreamer", func);
        return exports;
    }

    DataStreamer(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<DataStreamer>(info) {
        std::string path = info[0].As<Napi::String>().Utf8Value();
        file_ = fopen(path.c_str(), "rb");
        chunkSize_ = 64 * 1024;  // 64KB chunks
    }

    ~DataStreamer() {
        if (file_) fclose(file_);
    }

    Napi::Value NextChunk(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        if (!file_ || feof(file_)) {
            return env.Null();
        }

        // Allocate chunk
        uint8_t* data = new uint8_t[chunkSize_];
        size_t bytesRead = fread(data, 1, chunkSize_, file_);

        if (bytesRead == 0) {
            delete[] data;
            return env.Null();
        }

        // Return buffer owning chunk memory
        return Napi::Buffer<uint8_t>::New(
            env, data, bytesRead,
            [](Napi::Env, uint8_t* d) { delete[] d; }
        );
    }

    Napi::Value HasMore(const Napi::CallbackInfo& info) {
        return Napi::Boolean::New(info.Env(), file_ && !feof(file_));
    }

private:
    FILE* file_ = nullptr;
    size_t chunkSize_;
};
```

```javascript
// JavaScript usage - memory-efficient streaming
const streamer = new addon.DataStreamer('huge-file.dat');
while (streamer.hasMore()) {
    const chunk = streamer.nextChunk();
    processChunk(chunk);
    // Each chunk can be GC'd before next is allocated
}
```

## Decision Guide: String vs Buffer

```cpp
// Use String when:
// - Data is actual text (UTF-8, UTF-16)
// - Size is small (< 1MB)
// - You need string operations (concatenation, regex)

// Use Buffer when:
// - Data is binary (images, audio, compressed)
// - Size is large (> 1MB)
// - You need byte-level access
// - Zero-copy is beneficial
// - Data will be written to file/network
```

## References

- [N-API Buffer](https://nodejs.org/api/n-api.html#napi_create_buffer)
- [node-addon-api Buffer](https://github.com/nodejs/node-addon-api/blob/main/doc/buffer.md)
- [Node.js Buffer Documentation](https://nodejs.org/api/buffer.html)
