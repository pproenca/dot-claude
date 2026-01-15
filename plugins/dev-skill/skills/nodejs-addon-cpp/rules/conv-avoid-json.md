---
title: Avoid JSON Serialization for Structured Data
impact: MEDIUM-HIGH
impactDescription: 5-20× faster than JSON.parse/stringify roundtrip
tags: conv, json, serialization, performance
---

## Avoid JSON Serialization for Structured Data

Don't serialize to JSON in C++ and parse in JS (or vice versa). Use direct object construction or binary protocols.

**Incorrect (JSON roundtrip):**

```cpp
Napi::Value GetData(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // Build JSON string in C++
  std::string json = "{\"items\":[";
  for (size_t i = 0; i < items.size(); i++) {
    if (i > 0) json += ",";
    json += "{\"id\":" + std::to_string(items[i].id) +
            ",\"name\":\"" + EscapeJson(items[i].name) +
            "\",\"value\":" + std::to_string(items[i].value) + "}";
  }
  json += "]}";

  // Return string - JS will need to JSON.parse()
  return Napi::String::New(env, json);
}
```

```javascript
// JavaScript
const result = JSON.parse(addon.getData());  // Expensive parse!
```

**Correct (direct object construction):**

```cpp
Napi::Value GetData(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  Napi::Object result = Napi::Object::New(env);
  Napi::Array itemsArray = Napi::Array::New(env, items.size());

  for (size_t i = 0; i < items.size(); i++) {
    Napi::Object item = Napi::Object::New(env);
    item.Set("id", Napi::Number::New(env, items[i].id));
    item.Set("name", Napi::String::New(env, items[i].name));
    item.Set("value", Napi::Number::New(env, items[i].value));
    itemsArray[i] = item;
  }

  result.Set("items", itemsArray);
  return result;
}
```

```javascript
// JavaScript - no parsing needed
const result = addon.getData();
console.log(result.items[0].name);
```

**For very large datasets - binary protocol:**

```cpp
// Pack data into binary format
Napi::Value GetDataBinary(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // Calculate total size
  size_t size = 4;  // item count
  for (const auto& item : items) {
    size += 4 + 4 + 2 + item.name.size();  // id + value + name_len + name
  }

  Napi::Buffer<uint8_t> buffer = Napi::Buffer<uint8_t>::New(env, size);
  uint8_t* ptr = buffer.Data();

  // Write count
  *reinterpret_cast<uint32_t*>(ptr) = items.size();
  ptr += 4;

  // Write items
  for (const auto& item : items) {
    *reinterpret_cast<int32_t*>(ptr) = item.id;
    ptr += 4;
    *reinterpret_cast<float*>(ptr) = item.value;
    ptr += 4;
    *reinterpret_cast<uint16_t*>(ptr) = item.name.size();
    ptr += 2;
    memcpy(ptr, item.name.data(), item.name.size());
    ptr += item.name.size();
  }

  return buffer;
}
```

```javascript
// JavaScript - fast binary parsing
function parseData(buffer) {
  const view = new DataView(buffer.buffer);
  let offset = 0;

  const count = view.getUint32(offset, true);
  offset += 4;

  const items = [];
  for (let i = 0; i < count; i++) {
    const id = view.getInt32(offset, true);
    offset += 4;
    const value = view.getFloat32(offset, true);
    offset += 4;
    const nameLen = view.getUint16(offset, true);
    offset += 2;
    const name = buffer.toString('utf8', offset, offset + nameLen);
    offset += nameLen;

    items.push({ id, name, value });
  }

  return { items };
}
```

**When JSON might be acceptable:**
- Debugging or logging
- Interop with JSON-based APIs
- Small, infrequent data transfers

Reference: [V8 JSON Performance](https://v8.dev/blog/cost-of-javascript-2019)
