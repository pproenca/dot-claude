---
title: Choose Efficient String Encoding
impact: HIGH
impactDescription: 2-5× faster string conversion
tags: conv, strings, encoding, utf8, utf16
---

## Choose Efficient String Encoding

V8 stores strings in either Latin-1 (one-byte) or UTF-16. Choose the conversion that matches your needs to avoid unnecessary transcoding.

**Incorrect (always UTF-8):**

```cpp
Napi::Value ProcessString(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::String str = info[0].As<Napi::String>();

  // Always converts to UTF-8, even for ASCII strings
  std::string utf8 = str.Utf8Value();

  // Process...

  return Napi::String::New(env, result);  // Converts back from UTF-8
}
```

**Correct (choose based on content):**

```cpp
Napi::Value ProcessString(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::String str = info[0].As<Napi::String>();

  // Check if string is one-byte (ASCII/Latin-1)
  napi_value napi_str = str;
  napi_valuetype type;
  napi_typeof(env, napi_str, &type);

  // For ASCII-only processing, use Latin-1 (no transcoding for ASCII)
  if (IsAsciiOnly()) {
    std::u16string utf16 = str.Utf16Value();
    // Process as wide chars...
  } else {
    std::string utf8 = str.Utf8Value();
    // Process as UTF-8...
  }

  return result;
}
```

**For known ASCII content:**

```cpp
// When you know content is ASCII, use direct buffer access
Napi::Value ProcessAscii(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::String str = info[0].As<Napi::String>();

  // Get length first
  size_t length;
  napi_get_value_string_latin1(env, str, nullptr, 0, &length);

  // Allocate and copy
  std::string ascii(length, '\0');
  napi_get_value_string_latin1(env, str, &ascii[0], length + 1, nullptr);

  // Process ASCII string
  ProcessAsciiImpl(ascii);

  return Napi::String::New(env, ascii);
}
```

**Return strings efficiently:**

```cpp
// For small strings, New() is fine
return Napi::String::New(env, small_result);

// For large strings created from raw data
extern "C" char* large_data;
size_t large_length;

// Use external string when data is already in memory
// (advanced - requires custom string resource)
```

**Avoid repeated conversions:**

```cpp
// BAD - converts string twice
void ProcessTwice(const Napi::CallbackInfo& info) {
  Napi::String str = info[0].As<Napi::String>();

  std::string a = str.Utf8Value();  // Convert
  DoSomething(a);

  std::string b = str.Utf8Value();  // Convert AGAIN
  DoSomethingElse(b);
}

// GOOD - convert once
void ProcessOnce(const Napi::CallbackInfo& info) {
  Napi::String str = info[0].As<Napi::String>();

  std::string converted = str.Utf8Value();  // Convert once
  DoSomething(converted);
  DoSomethingElse(converted);
}
```

Reference: [V8 String Types](https://v8.dev/blog/string)
