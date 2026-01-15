---
title: Optimize Object Serialization for Large Data
impact: HIGH
impactDescription: 3-10× faster for complex object graphs
tags: conv, serialization, objects, structured-clone
---

## Optimize Object Serialization for Large Data

For complex objects crossing the JS/C++ boundary, use structured serialization or custom binary formats instead of property-by-property conversion.

**Incorrect (property-by-property conversion):**

```cpp
Napi::Value SerializeObjects(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array objects = info[0].As<Napi::Array>();

  std::vector<MyStruct> result;
  for (uint32_t i = 0; i < objects.Length(); i++) {
    Napi::Object obj = objects[i].As<Napi::Object>();

    MyStruct item;
    // Each Get() is a hash lookup + type conversion
    item.id = obj.Get("id").As<Napi::Number>().Int32Value();
    item.name = obj.Get("name").As<Napi::String>().Utf8Value();
    item.x = obj.Get("x").As<Napi::Number>().DoubleValue();
    item.y = obj.Get("y").As<Napi::Number>().DoubleValue();
    item.z = obj.Get("z").As<Napi::Number>().DoubleValue();
    // ... more properties

    result.push_back(item);
  }

  return ProcessStructs(result);
}
```

**Correct (TypedArray for numeric fields):**

```cpp
// JavaScript side - prepare data in TypedArrays
// const ids = new Int32Array(objects.map(o => o.id));
// const positions = new Float64Array(objects.flatMap(o => [o.x, o.y, o.z]));
// addon.processOptimized(ids, positions, names);

Napi::Value ProcessOptimized(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // Direct memory access for numeric data
  Napi::Int32Array ids = info[0].As<Napi::Int32Array>();
  Napi::Float64Array positions = info[1].As<Napi::Float64Array>();
  Napi::Array names = info[2].As<Napi::Array>();

  int32_t* id_ptr = ids.Data();
  double* pos_ptr = positions.Data();
  size_t count = ids.ElementLength();

  std::vector<MyStruct> result(count);
  for (size_t i = 0; i < count; i++) {
    result[i].id = id_ptr[i];
    result[i].x = pos_ptr[i * 3];
    result[i].y = pos_ptr[i * 3 + 1];
    result[i].z = pos_ptr[i * 3 + 2];
    // Only string needs JS access
    result[i].name = names[i].As<Napi::String>().Utf8Value();
  }

  return ProcessStructs(result);
}
```

**Alternative (binary protocol):**

```cpp
// Define binary format
struct PackedData {
  int32_t id;
  float x, y, z;
  uint16_t name_length;
  // followed by name_length bytes of name
};

Napi::Value ProcessBinary(const Napi::CallbackInfo& info) {
  Napi::Buffer<uint8_t> buffer = info[0].As<Napi::Buffer<uint8_t>>();
  uint8_t* data = buffer.Data();
  size_t length = buffer.Length();

  std::vector<MyStruct> result;
  size_t offset = 0;

  while (offset < length) {
    PackedData* packed = reinterpret_cast<PackedData*>(data + offset);
    offset += sizeof(PackedData);

    MyStruct item;
    item.id = packed->id;
    item.x = packed->x;
    item.y = packed->y;
    item.z = packed->z;
    item.name = std::string(
      reinterpret_cast<char*>(data + offset),
      packed->name_length
    );
    offset += packed->name_length;

    result.push_back(std::move(item));
  }

  return ProcessStructs(result);
}
```

```javascript
// JavaScript helper to pack objects
function packObjects(objects) {
  const parts = [];
  for (const obj of objects) {
    const nameBytes = Buffer.from(obj.name);
    const header = Buffer.alloc(18);  // 4 + 4*3 + 2
    header.writeInt32LE(obj.id, 0);
    header.writeFloatLE(obj.x, 4);
    header.writeFloatLE(obj.y, 8);
    header.writeFloatLE(obj.z, 12);
    header.writeUInt16LE(nameBytes.length, 16);
    parts.push(header, nameBytes);
  }
  return Buffer.concat(parts);
}
```

Reference: [MessagePack](https://msgpack.org/) for a standard binary serialization format.
