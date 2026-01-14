---
title: Use Handle Scopes in Loops
impact: CRITICAL
impactDescription: Prevents O(n) handle accumulation - loops without scopes leak ~100 bytes per iteration, causing OOM on 1M+ items
tags: memory, handle-scope, gc, loops, node-addon-api
---

# Use Handle Scopes in Loops

Wrap loops that create JavaScript values with `HandleScope` to allow intermediate handles to be garbage collected. Without scopes, handles accumulate and leak memory. Processing 1M items without scopes accumulates ~100MB of leaked handles.

## Why This Matters

- **Memory Efficiency**: Handles are released at scope exit
- **OOM Prevention**: Long loops don't accumulate unbounded handles
- **GC Cooperation**: Allows GC to run between iterations
- **Production Stability**: Prevents memory leaks in long-running servers

## Understanding Handle Scopes

When you create N-API values (strings, numbers, objects), they're protected from garbage collection by an implicit "handle scope." These handles accumulate until the scope closes. In loops, this causes memory buildup.

```
Without HandleScope:        With HandleScope:
Iteration 1: +1 handle      Iteration 1: +1, -1 (scoped)
Iteration 2: +1 handle      Iteration 2: +1, -1 (scoped)
Iteration 3: +1 handle      Iteration 3: +1, -1 (scoped)
...                         ...
Iteration N: N handles!     Iteration N: 1 handle max
```

## Incorrect: Loop Without Handle Scope

```cpp
// PROBLEM: Each iteration creates ~5-10 handles (~100 bytes each)
// 1M iterations = 100MB leaked, causing OOM crash
Napi::Value ProcessLargeArray(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Array input = info[0].As<Napi::Array>();
    uint32_t length = input.Length();

    Napi::Array results = Napi::Array::New(env, length);

    // PROBLEM: Each iteration creates handles that persist
    for (uint32_t i = 0; i < length; i++) {
        // These intermediate values all stay in memory
        Napi::Value item = input.Get(i);
        Napi::Object obj = item.As<Napi::Object>();
        Napi::Value name = obj.Get("name");
        Napi::Value value = obj.Get("value");

        // String operations create more handles
        std::string nameStr = name.As<Napi::String>().Utf8Value();
        std::string processed = ProcessString(nameStr);

        // Creating result object - more handles
        Napi::Object result = Napi::Object::New(env);
        result.Set("name", Napi::String::New(env, processed));
        result.Set("value", value);

        results.Set(i, result);
        // All handles from this iteration persist!
    }
    // If length is 1,000,000, we have millions of leaked handles

    return results;
}
```

**Memory growth example:**
```javascript
// With 1M items, addon consumes gigabytes of memory
const data = new Array(1000000).fill().map((_, i) => ({
    name: `item-${i}`,
    value: i
}));

const result = addon.processLargeArray(data);  // OOM crash!
```

## Incorrect: Scope in Wrong Location

```cpp
// BAD: HandleScope outside loop doesn't help
Napi::Value ProcessLargeArray(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // This scope covers the entire function - doesn't help with loop
    Napi::HandleScope outerScope(env);

    Napi::Array input = info[0].As<Napi::Array>();
    uint32_t length = input.Length();
    Napi::Array results = Napi::Array::New(env, length);

    for (uint32_t i = 0; i < length; i++) {
        // Still accumulating handles per iteration
        Napi::Value item = input.Get(i);
        // ... same problem ...
    }

    return results;
}
```

## Correct: Handle Scope Inside Loop

```cpp
// SOLUTION: Constant O(1) memory regardless of array size
// HandleScope releases all handles at end of each iteration
Napi::Value ProcessLargeArray(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Array input = info[0].As<Napi::Array>();
    uint32_t length = input.Length();

    Napi::Array results = Napi::Array::New(env, length);

    for (uint32_t i = 0; i < length; i++) {
        // Create scope for this iteration
        Napi::HandleScope scope(env);

        // All handles created here are released at scope end
        Napi::Value item = input.Get(i);
        Napi::Object obj = item.As<Napi::Object>();
        Napi::Value name = obj.Get("name");
        Napi::Value value = obj.Get("value");

        std::string nameStr = name.As<Napi::String>().Utf8Value();
        std::string processed = ProcessString(nameStr);

        Napi::Object result = Napi::Object::New(env);
        result.Set("name", Napi::String::New(env, processed));
        result.Set("value", value);

        // Result escapes the scope via Set()
        results.Set(i, result);

        // Scope closes here - intermediate handles released
    }

    return results;
}
```

## Correct: Escapable Handle Scope for Return Values

```cpp
// GOOD: Use EscapableHandleScope when returning values from scope
Napi::Value CreateNestedStructure(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    int depth = info[0].As<Napi::Number>().Int32Value();

    Napi::Object root = Napi::Object::New(env);
    Napi::Object current = root;

    for (int i = 0; i < depth; i++) {
        // Escapable scope allows one value to escape
        Napi::EscapableHandleScope scope(env);

        // Create child object in this scope
        Napi::Object child = Napi::Object::New(env);
        child.Set("level", Napi::Number::New(env, i));
        child.Set("name", Napi::String::New(env, "level-" + std::to_string(i)));

        // Temporary work that can be collected
        for (int j = 0; j < 100; j++) {
            Napi::String temp = Napi::String::New(env, "temp-" + std::to_string(j));
            // temp is released when scope closes
        }

        // Escape the child object to outer scope
        Napi::Object escapedChild = scope.Escape(child).As<Napi::Object>();

        current.Set("child", escapedChild);
        current = escapedChild;
    }

    return root;
}
```

## Correct: Raw N-API Handle Scopes

```cpp
// GOOD: Raw N-API with handle scope in loop
static napi_value ProcessArray(napi_env env, napi_callback_info info) {
    napi_status status;
    size_t argc = 1;
    napi_value argv[1];
    napi_get_cb_info(env, info, &argc, argv, NULL, NULL);

    uint32_t length;
    napi_get_array_length(env, argv[0], &length);

    napi_value results;
    napi_create_array_with_length(env, length, &results);

    for (uint32_t i = 0; i < length; i++) {
        // Open handle scope for this iteration
        napi_handle_scope scope;
        status = napi_open_handle_scope(env, &scope);
        if (status != napi_ok) break;

        // Work within scope
        napi_value item;
        napi_get_element(env, argv[0], i, &item);

        napi_value name_val;
        napi_get_named_property(env, item, "name", &name_val);

        char name[256];
        size_t name_len;
        napi_get_value_string_utf8(env, name_val, name, sizeof(name), &name_len);

        // Create result
        napi_value result;
        napi_create_object(env, &result);

        napi_value processed_name;
        napi_create_string_utf8(env, name, name_len, &processed_name);
        napi_set_named_property(env, result, "processed", processed_name);

        // Add to results array (escapes scope implicitly)
        napi_set_element(env, results, i, result);

        // Close scope - releases intermediate handles
        napi_close_handle_scope(env, scope);
    }

    return results;
}
```

## Pattern: Batched Processing with Scopes

```cpp
// GOOD: Batch processing with periodic scope cleanup
Napi::Value ProcessMassiveArray(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Array input = info[0].As<Napi::Array>();
    uint32_t length = input.Length();

    Napi::Array results = Napi::Array::New(env, length);

    const uint32_t BATCH_SIZE = 1000;

    for (uint32_t batch = 0; batch < length; batch += BATCH_SIZE) {
        // Scope per batch for very large arrays
        Napi::HandleScope batchScope(env);

        uint32_t batchEnd = std::min(batch + BATCH_SIZE, length);

        for (uint32_t i = batch; i < batchEnd; i++) {
            // Inner scope for fine-grained cleanup
            Napi::HandleScope itemScope(env);

            Napi::Value item = input.Get(i);
            Napi::Object result = ProcessItem(env, item);
            results.Set(i, result);
        }
    }

    return results;
}
```

## Pattern: Recursive Function with Scopes

```cpp
// GOOD: Handle scope in recursive calls
Napi::Value TraverseTree(Napi::Env env, Napi::Object node, int depth) {
    Napi::HandleScope scope(env);

    Napi::Object result = Napi::Object::New(env);

    if (node.Has("value")) {
        result.Set("value", node.Get("value"));
    }

    if (node.Has("children") && node.Get("children").IsArray()) {
        Napi::Array children = node.Get("children").As<Napi::Array>();
        Napi::Array processedChildren = Napi::Array::New(env, children.Length());

        for (uint32_t i = 0; i < children.Length(); i++) {
            Napi::HandleScope childScope(env);

            Napi::Object child = children.Get(i).As<Napi::Object>();
            // Recursive call - each level has its own scope
            Napi::Value processed = TraverseTree(env, child, depth + 1);
            processedChildren.Set(i, processed);
        }

        result.Set("children", processedChildren);
    }

    return result;
}
```

**When to use:** Always use HandleScope inside any loop that creates N-API values, especially when processing arrays, iterating data structures, or any unbounded iteration.

**When NOT to use:** Handle scopes add ~10ns overhead per scope. Skip for loops under 10 iterations or when no N-API values are created in the loop body.

## When NOT to Use Handle Scopes

```cpp
// Handle scopes are UNNECESSARY for:

// 1. Simple functions without loops
Napi::Value SimpleAdd(const Napi::CallbackInfo& info) {
    // No loop, no scope needed
    double a = info[0].As<Napi::Number>().DoubleValue();
    double b = info[1].As<Napi::Number>().DoubleValue();
    return Napi::Number::New(info.Env(), a + b);
}

// 2. Very short loops (< 10 iterations)
Napi::Value ProcessSmallArray(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Array input = info[0].As<Napi::Array>();

    // Only 3-5 items - overhead not worth it
    if (input.Length() < 10) {
        // Process without scope
    }
}
```

## References

- [N-API Handle Scope](https://nodejs.org/api/n-api.html#napi_open_handle_scope)
- [node-addon-api HandleScope](https://github.com/nodejs/node-addon-api/blob/main/doc/handle_scope.md)
- [V8 Handle Documentation](https://v8.dev/docs/embed#handles-and-garbage-collection)
