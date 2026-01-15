---
title: Avoid Unnecessary String Copies
impact: HIGH
impactDescription: 2-10× improvement for string-heavy operations
tags: mem, strings, copy-elision, utf8
---

## Avoid Unnecessary String Copies

Creating `std::string` from V8 strings copies the entire buffer. For read-only access, use string views or direct buffer access.

**Incorrect (multiple copies):**

```cpp
Napi::Value ProcessString(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // Copy 1: V8 string → std::string
  std::string input = info[0].As<Napi::String>().Utf8Value();

  // Copy 2: std::string → another std::string (in function)
  std::string result = DoProcessing(input);

  // Copy 3: std::string → V8 string
  return Napi::String::New(env, result);
}

std::string DoProcessing(std::string input) {  // Copy by value!
  return ProcessImpl(input);
}
```

**Correct (minimized copies):**

```cpp
Napi::Value ProcessString(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // Single copy from V8
  std::string input = info[0].As<Napi::String>().Utf8Value();

  // Pass by const reference - no copy
  DoProcessing(input);

  // Return directly
  return Napi::String::New(env, input);
}

void DoProcessing(const std::string& input) {  // No copy!
  ProcessImpl(input);
}
```

**Alternative (direct buffer access for analysis):**

```cpp
Napi::Value AnalyzeString(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::String str = info[0].As<Napi::String>();

  // Get length without copying
  size_t length = str.Utf8Value().size();

  // For simple analysis, use direct N-API calls
  napi_value napi_str = str;
  size_t str_length;
  napi_get_value_string_utf8(env, napi_str, nullptr, 0, &str_length);

  // Only copy if you need the content
  if (NeedToModify(str_length)) {
    std::string content = str.Utf8Value();
    // Modify content
  }

  return Napi::Number::New(env, length);
}
```

**For large strings (external string resource):**

```cpp
// For very large strings, use external string resources
// to share memory with V8 without copying
class ExternalStringResource : public v8::String::ExternalOneByteStringResource {
 public:
  ExternalStringResource(const char* data, size_t length)
      : data_(data), length_(length) {}

  const char* data() const override { return data_; }
  size_t length() const override { return length_; }

 private:
  const char* data_;
  size_t length_;
};
```

**Benefits:**
- Reduced memory bandwidth
- Lower GC pressure
- Better cache utilization

Reference: [V8 String Internals](https://v8.dev/blog/string-processing-in-v8)
