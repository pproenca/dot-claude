# Node.js Native Addons

Patterns for writing safe, performant C++ code that interfaces with Node.js via N-API or Nan.

## The V8 Memory Model

### The Problem

V8's garbage collector can move objects in memory at any time. JavaScript values are represented by "handles" that become invalid:
- When the handle scope ends
- When GC runs
- When you return to the event loop

```cpp
// DANGEROUS: V8 handle used after potential GC
void BadExample(const Nan::FunctionCallbackInfo<v8::Value>& info) {
  v8::Local<v8::String> str = info[0].As<v8::String>();
  
  DoSomeAllocation();  // This might trigger GC!
  
  // str might now point to garbage
  Nan::Utf8String value(str);  // CRASH or corruption
}
```

### The Solution: Extract Early

```cpp
// GOOD: Extract to C++ types immediately
void GoodExample(const Nan::FunctionCallbackInfo<v8::Value>& info) {
  // Validate and extract BEFORE any allocation
  if (info.Length() < 1 || !info[0]->IsString()) {
    return Nan::ThrowTypeError("Expected string argument");
  }
  
  // Convert to C++ string immediately
  Nan::Utf8String str(info[0]);
  std::string cpp_str(*str, str.length());
  
  // Now safe to allocate, call other functions, etc.
  DoSomeAllocation();
  ProcessString(cpp_str);
  
  info.GetReturnValue().Set(Nan::New("success").ToLocalChecked());
}
```

## N-API (Preferred)

N-API is ABI-stable across Node.js versions. Use it for new projects.

### Basic Pattern

```cpp
#include <napi.h>

Napi::Value ProcessData(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  
  // Validate arguments
  if (info.Length() < 1 || !info[0].IsString()) {
    Napi::TypeError::New(env, "Expected string").ThrowAsJavaScriptException();
    return env.Undefined();
  }
  
  // Extract to C++ immediately
  std::string input = info[0].As<Napi::String>().Utf8Value();
  
  // Process (safe to allocate now)
  std::string result = Transform(input);
  
  // Return
  return Napi::String::New(env, result);
}

Napi::Object Init(Napi::Env env, Napi::Object exports) {
  exports.Set("processData", Napi::Function::New(env, ProcessData));
  return exports;
}

NODE_API_MODULE(addon, Init)
```

### Error Handling

```cpp
Napi::Value SafeOperation(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  
  try {
    // Your code that might throw
    auto result = DoWork();
    return Napi::Number::New(env, result);
    
  } catch (const std::exception& e) {
    Napi::Error::New(env, e.what()).ThrowAsJavaScriptException();
    return env.Undefined();
  }
}
```

### ObjectWrap for Classes

```cpp
class MyClass : public Napi::ObjectWrap<MyClass> {
 public:
  static Napi::Object Init(Napi::Env env, Napi::Object exports) {
    Napi::Function func = DefineClass(env, "MyClass", {
      InstanceMethod("getValue", &MyClass::GetValue),
      InstanceMethod("setValue", &MyClass::SetValue),
    });
    
    Napi::FunctionReference* constructor = new Napi::FunctionReference();
    *constructor = Napi::Persistent(func);
    env.SetInstanceData(constructor);
    
    exports.Set("MyClass", func);
    return exports;
  }
  
  explicit MyClass(const Napi::CallbackInfo& info)
      : Napi::ObjectWrap<MyClass>(info) {
    if (info.Length() > 0 && info[0].IsNumber()) {
      value_ = info[0].As<Napi::Number>().Int32Value();
    }
  }
  
 private:
  Napi::Value GetValue(const Napi::CallbackInfo& info) {
    return Napi::Number::New(info.Env(), value_);
  }
  
  void SetValue(const Napi::CallbackInfo& info) {
    if (info.Length() > 0 && info[0].IsNumber()) {
      value_ = info[0].As<Napi::Number>().Int32Value();
    }
  }
  
  int value_ = 0;
};
```

## Nan (Legacy, Still Common)

### Safe Argument Extraction

```cpp
NAN_METHOD(ProcessBuffer) {
  // Validate first
  if (info.Length() < 1) {
    return Nan::ThrowError("Missing argument");
  }
  
  if (!node::Buffer::HasInstance(info[0])) {
    return Nan::ThrowTypeError("Expected Buffer");
  }
  
  // Extract immediately
  char* data = node::Buffer::Data(info[0]);
  size_t length = node::Buffer::Length(info[0]);
  
  // Copy if you need to keep it
  std::vector<char> copy(data, data + length);
  
  // Now safe to do work
  ProcessData(copy.data(), copy.size());
  
  info.GetReturnValue().Set(Nan::True());
}
```

### ObjectWrap Validation

```cpp
NAN_METHOD(InstanceMethod) {
  // ALWAYS validate the unwrap result
  MyClass* obj = Nan::ObjectWrap::Unwrap<MyClass>(info.Holder());
  
  if (obj == nullptr) {
    return Nan::ThrowError("Invalid object");
  }
  
  if (!obj->IsValid()) {
    return Nan::ThrowError("Object has been destroyed");
  }
  
  // Safe to use
  int result = obj->Compute();
  info.GetReturnValue().Set(Nan::New(result));
}
```

### Persistent Handles for Stored References

```cpp
class Observer : public Nan::ObjectWrap {
 public:
  void SetCallback(v8::Local<v8::Function> callback) {
    // Store in Persistent to prevent GC
    callback_.Reset(callback);
  }
  
  void Notify(int value) {
    Nan::HandleScope scope;
    
    if (callback_.IsEmpty()) {
      return;
    }
    
    v8::Local<v8::Function> cb = Nan::New(callback_);
    v8::Local<v8::Value> argv[] = { Nan::New(value) };
    Nan::MakeCallback(Nan::GetCurrentContext()->Global(), cb, 1, argv);
  }
  
  ~Observer() {
    callback_.Reset();  // Release the persistent handle
  }
  
 private:
  Nan::Persistent<v8::Function> callback_;
};
```

## Async Operations

### N-API AsyncWorker

```cpp
class ComputeWorker : public Napi::AsyncWorker {
 public:
  ComputeWorker(Napi::Function& callback, int input)
      : Napi::AsyncWorker(callback), input_(input) {}
  
  void Execute() override {
    // Runs on worker thread - NO V8 ACCESS HERE
    // This method CANNOT touch any Napi:: types
    result_ = ExpensiveComputation(input_);
  }
  
  void OnOK() override {
    // Back on main thread - safe to use Napi::
    Napi::HandleScope scope(Env());
    Callback().Call({Env().Null(), Napi::Number::New(Env(), result_)});
  }
  
  void OnError(const Napi::Error& e) override {
    Napi::HandleScope scope(Env());
    Callback().Call({e.Value(), Env().Undefined()});
  }
  
 private:
  int input_;
  int result_;
};

Napi::Value StartCompute(const Napi::CallbackInfo& info) {
  int input = info[0].As<Napi::Number>().Int32Value();
  Napi::Function callback = info[1].As<Napi::Function>();
  
  auto* worker = new ComputeWorker(callback, input);
  worker->Queue();
  
  return info.Env().Undefined();
}
```

### Promise-Based Async

```cpp
Napi::Value AsyncCompute(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  
  int input = info[0].As<Napi::Number>().Int32Value();
  
  auto deferred = Napi::Promise::Deferred::New(env);
  
  // Store what we need in a shared_ptr (C++ types only!)
  auto data = std::make_shared<int>(input);
  auto result = std::make_shared<int>(0);
  
  auto worker = new Napi::AsyncWorker(env);
  // ... setup worker with deferred.Resolve/Reject ...
  
  return deferred.Promise();
}
```

## Memory Management Patterns

### Safe Buffer Creation

```cpp
// Creating a Buffer that copies data
Napi::Value CreateBuffer(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  
  std::vector<uint8_t> data = GenerateData();
  
  // Napi::Buffer::Copy creates a copy (safe)
  return Napi::Buffer<uint8_t>::Copy(env, data.data(), data.size());
}

// Creating a Buffer with custom cleanup
Napi::Value CreateBufferWithCleanup(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  
  // Allocated data that the Buffer will own
  uint8_t* data = new uint8_t[1024];
  FillData(data, 1024);
  
  return Napi::Buffer<uint8_t>::New(
    env, data, 1024,
    [](Napi::Env, uint8_t* data) { delete[] data; }  // Cleanup
  );
}
```

### Reference Counting with C++ Objects

```cpp
class NativeResource : public Napi::ObjectWrap<NativeResource> {
 public:
  static Napi::Object Init(Napi::Env env, Napi::Object exports);
  
  explicit NativeResource(const Napi::CallbackInfo& info)
      : Napi::ObjectWrap<NativeResource>(info),
        resource_(CreateExpensiveResource()) {}
  
  ~NativeResource() {
    // Clean up C++ resources when JS object is GC'd
    DestroyResource(resource_);
  }
  
  // Explicit cleanup for deterministic destruction
  Napi::Value Close(const Napi::CallbackInfo& info) {
    if (resource_) {
      DestroyResource(resource_);
      resource_ = nullptr;
    }
    return info.Env().Undefined();
  }
  
 private:
  ExpensiveResource* resource_;
};
```

## Common Pitfalls

### 1. Using V8 Types in Worker Threads

```cpp
// WRONG: V8 types in Execute()
void Execute() override {
  Napi::String str;  // CRASH: no V8 on this thread
}

// RIGHT: Only C++ types in Execute()
void Execute() override {
  std::string str = "hello";  // Pure C++
}
```

### 2. Forgetting HandleScope

```cpp
// WRONG: Local handles leak
void ProcessMany() {
  for (int i = 0; i < 1000000; i++) {
    Nan::New<v8::Integer>(i);  // Handles accumulate!
  }
}

// RIGHT: Scope handles in loops
void ProcessMany() {
  for (int i = 0; i < 1000000; i++) {
    Nan::HandleScope scope;  // Handles cleaned up each iteration
    Nan::New<v8::Integer>(i);
  }
}
```

### 3. Storing Local Handles

```cpp
// WRONG: Local handle becomes invalid
class Bad {
  v8::Local<v8::Object> cached_;  // Will become garbage
};

// RIGHT: Use Persistent for stored references
class Good {
  Nan::Persistent<v8::Object> cached_;
};
```

### 4. Unchecked Casts

```cpp
// WRONG: Assumes type without checking
auto str = info[0].As<Napi::String>();  // Crash if not a string

// RIGHT: Validate first
if (!info[0].IsString()) {
  Napi::TypeError::New(env, "Expected string").ThrowAsJavaScriptException();
  return env.Undefined();
}
auto str = info[0].As<Napi::String>();
```
