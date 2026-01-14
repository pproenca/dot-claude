---
title: Use Type-Tagged Objects
impact: CRITICAL
impactDescription: Prevents 100% of type confusion vulnerabilities (CVE-severity security bugs in native addons)
tags: napi, type-safety, type-tags, security, node-addon-api
---

# Use Type-Tagged Objects

Apply `napi_type_tag_object()` to mark wrapped native objects with unique identifiers. Always verify the type tag before casting to prevent memory corruption from malicious or accidental type confusion. Type confusion is a common CVE-severity vulnerability in native code.

## Why This Matters

- **Security**: Prevents type confusion attacks from JavaScript
- **Safety**: Catches accidental wrong-type passing
- **Debugging**: Clear error messages when types mismatch
- **Reliability**: Eliminates undefined behavior from bad casts

## Understanding Type Tags

Type tags are 128-bit UUIDs that uniquely identify your native object types. N-API stores these tags internally and can verify them before allowing access to native data.

```cpp
// Type tag structure - 128-bit UUID
typedef struct {
    uint64_t lower;
    uint64_t upper;
} napi_type_tag;
```

## Incorrect: Unsafe Static Cast

```cpp
// PROBLEM: Attacker can pass any JS object, causing memory corruption
// This pattern has led to CVEs in production addons
#include <napi.h>

class Database : public Napi::ObjectWrap<Database> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "Database", {
            InstanceMethod("query", &Database::Query)
        });
        exports.Set("Database", func);
        return exports;
    }

    Database(const Napi::CallbackInfo& info) : Napi::ObjectWrap<Database>(info) {
        connectionString_ = info[0].As<Napi::String>().Utf8Value();
    }

    Napi::Value Query(const Napi::CallbackInfo& info) {
        return Napi::String::New(info.Env(), "result");
    }

private:
    std::string connectionString_;
};

// BAD: Function accepts any object and blindly casts
Napi::Value ExecuteQuery(const Napi::CallbackInfo& info) {
    // DANGEROUS: No verification that this is actually a Database!
    // If user passes a different object type, this corrupts memory
    Database* db = Napi::ObjectWrap<Database>::Unwrap(info[0].As<Napi::Object>());

    // This accesses connectionString_ which may not exist
    // Leading to crashes, memory corruption, or security vulnerabilities
    return db->Query(info);
}
```

**Attack scenario:**
```javascript
const addon = require('./addon');

// Attacker creates fake "Database" object
const fakeDb = {
    __proto__: addon.Database.prototype,
    maliciousData: new ArrayBuffer(1024)
};

// Without type tags, addon blindly trusts and casts, causing corruption
addon.executeQuery(fakeDb);  // CRASH or security vulnerability!
```

## Correct: Type-Tagged Objects (Raw N-API)

```cpp
// SOLUTION: Type tags provide 100% protection against type confusion
// Only objects tagged by your addon pass verification
#define NAPI_VERSION 8
#include <node_api.h>
#include <string.h>
#include <stdlib.h>

// Unique type tag for Database objects
static const napi_type_tag database_type_tag = {
    0xdb01234567890abc, 0xfedcba9876543210
};

typedef struct {
    char connection_string[256];
    int is_connected;
} Database;

static void DatabaseFinalize(napi_env env, void* data, void* hint) {
    Database* db = (Database*)data;
    free(db);
}

static napi_value CreateDatabase(napi_env env, napi_callback_info info) {
    napi_status status;
    size_t argc = 1;
    napi_value argv[1];

    status = napi_get_cb_info(env, info, &argc, argv, NULL, NULL);
    if (status != napi_ok) return NULL;

    // Allocate native data
    Database* db = (Database*)malloc(sizeof(Database));
    if (!db) {
        napi_throw_error(env, NULL, "Failed to allocate Database");
        return NULL;
    }

    // Get connection string
    status = napi_get_value_string_utf8(env, argv[0],
        db->connection_string, sizeof(db->connection_string), NULL);
    if (status != napi_ok) {
        free(db);
        napi_throw_type_error(env, NULL, "Connection string required");
        return NULL;
    }
    db->is_connected = 1;

    // Create wrapped object
    napi_value wrapper;
    status = napi_create_object(env, &wrapper);
    if (status != napi_ok) {
        free(db);
        return NULL;
    }

    // Wrap the native data
    status = napi_wrap(env, wrapper, db, DatabaseFinalize, NULL, NULL);
    if (status != napi_ok) {
        free(db);
        return NULL;
    }

    // CRITICAL: Apply type tag for safe verification later
    status = napi_type_tag_object(env, wrapper, &database_type_tag);
    if (status != napi_ok) {
        napi_throw_error(env, NULL, "Failed to tag object");
        return NULL;
    }

    return wrapper;
}

static napi_value ExecuteQuery(napi_env env, napi_callback_info info) {
    napi_status status;
    size_t argc = 2;
    napi_value argv[2];

    status = napi_get_cb_info(env, info, &argc, argv, NULL, NULL);
    if (status != napi_ok) return NULL;

    // CRITICAL: Verify type tag before unwrapping
    bool is_database;
    status = napi_check_object_type_tag(env, argv[0], &database_type_tag, &is_database);
    if (status != napi_ok) {
        napi_throw_error(env, NULL, "Failed to check type tag");
        return NULL;
    }

    if (!is_database) {
        napi_throw_type_error(env, NULL,
            "First argument must be a Database object created by this addon");
        return NULL;
    }

    // Safe to unwrap - type verified
    Database* db;
    status = napi_unwrap(env, argv[0], (void**)&db);
    if (status != napi_ok) {
        napi_throw_error(env, NULL, "Failed to unwrap Database");
        return NULL;
    }

    // Now safely access Database fields
    char result[512];
    snprintf(result, sizeof(result), "Query executed on: %s", db->connection_string);

    napi_value js_result;
    napi_create_string_utf8(env, result, NAPI_AUTO_LENGTH, &js_result);
    return js_result;
}
```

## Correct: Type-Tagged Objects (node-addon-api)

```cpp
// GOOD: node-addon-api with type tags
#define NAPI_VERSION 8
#include <napi.h>

class Database : public Napi::ObjectWrap<Database> {
public:
    // Unique type tag for this class
    static inline const napi_type_tag typeTag_ = {
        0xdb01234567890abc, 0xfedcba9876543210
    };

    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "Database", {
            InstanceMethod<&Database::Query>("query"),
            InstanceMethod<&Database::Close>("close"),
            InstanceAccessor<&Database::GetConnected>("connected")
        });

        constructor_ = Napi::Persistent(func);
        constructor_.SuppressDestruct();

        exports.Set("Database", func);
        return exports;
    }

    Database(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<Database>(info), isConnected_(true) {
        Napi::Env env = info.Env();

        if (info.Length() < 1 || !info[0].IsString()) {
            throw Napi::TypeError::New(env, "Connection string required");
        }

        connectionString_ = info[0].As<Napi::String>().Utf8Value();

        // Apply type tag to this instance
        info.This().As<Napi::Object>().TypeTag(&typeTag_);
    }

    // Safe static unwrap with type verification
    static Database* Unwrap(Napi::Env env, Napi::Value value) {
        if (!value.IsObject()) {
            throw Napi::TypeError::New(env, "Expected Database object");
        }

        Napi::Object obj = value.As<Napi::Object>();

        // Verify type tag before unwrapping
        if (!obj.CheckTypeTag(&typeTag_)) {
            throw Napi::TypeError::New(env,
                "Invalid Database object - may be from a different addon");
        }

        return Napi::ObjectWrap<Database>::Unwrap(obj);
    }

    const std::string& GetConnectionString() const { return connectionString_; }
    bool IsConnected() const { return isConnected_; }

private:
    Napi::Value Query(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        if (!isConnected_) {
            throw Napi::Error::New(env, "Database is closed");
        }

        std::string sql = info[0].As<Napi::String>().Utf8Value();
        return Napi::String::New(env, "Result for: " + sql);
    }

    Napi::Value Close(const Napi::CallbackInfo& info) {
        isConnected_ = false;
        return info.Env().Undefined();
    }

    Napi::Value GetConnected(const Napi::CallbackInfo& info) {
        return Napi::Boolean::New(info.Env(), isConnected_);
    }

    static Napi::FunctionReference constructor_;
    std::string connectionString_;
    bool isConnected_;
};

Napi::FunctionReference Database::constructor_;

// Safe function that accepts Database from any source
Napi::Value ExecuteQuery(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Type-safe unwrap with verification
    Database* db = Database::Unwrap(env, info[0]);

    std::string query = info[1].As<Napi::String>().Utf8Value();

    return Napi::String::New(env,
        "Executing '" + query + "' on " + db->GetConnectionString());
}

Napi::Object Init(Napi::Env env, Napi::Object exports) {
    Database::Init(env, exports);
    exports.Set("executeQuery", Napi::Function::New(env, ExecuteQuery));
    return exports;
}

NODE_API_MODULE(database, Init)
```

## Multiple Type Tags for Inheritance

```cpp
// GOOD: Different type tags for different classes
class BaseConnection {
public:
    static inline const napi_type_tag typeTag_ = {
        0x1111111111111111, 0xaaaaaaaaaaaaaaaa
    };
};

class MySQLConnection : public BaseConnection {
public:
    static inline const napi_type_tag typeTag_ = {
        0x2222222222222222, 0xbbbbbbbbbbbbbbbb
    };
};

class PostgresConnection : public BaseConnection {
public:
    static inline const napi_type_tag typeTag_ = {
        0x3333333333333333, 0xcccccccccccccccc
    };
};

// Function that accepts any connection type
Napi::Value CloseConnection(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Object obj = info[0].As<Napi::Object>();

    if (obj.CheckTypeTag(&MySQLConnection::typeTag_)) {
        auto* conn = Napi::ObjectWrap<MySQLWrapper>::Unwrap(obj);
        conn->Close();
    } else if (obj.CheckTypeTag(&PostgresConnection::typeTag_)) {
        auto* conn = Napi::ObjectWrap<PostgresWrapper>::Unwrap(obj);
        conn->Close();
    } else {
        throw Napi::TypeError::New(env, "Unknown connection type");
    }

    return env.Undefined();
}
```

## Generating Unique Type Tags

```cpp
// Generate type tags using UUIDs
// Use a UUID generator to create unique values

// Option 1: Use random UUIDs (recommended for production)
// uuidgen or similar tools
static const napi_type_tag my_type = {
    0x550e8400e29b41d4,  // First 64 bits of UUID
    0xa716446655440000   // Last 64 bits of UUID
};

// Option 2: Use domain-specific identifiers
// Combine package name hash + type name hash
static const napi_type_tag database_type = {
    0x6d79706b67000000 | ('D' << 8) | 'B',  // "mypkg" + "DB"
    0x0001000000000000   // version 1
};
```

**When to use:** Always use type tags for any addon that exposes wrapped native objects to JavaScript. This is especially critical for addons that handle sensitive operations (database connections, file handles, crypto).

**When NOT to use:** Type tags are unnecessary for addons that only export pure functions without wrapped objects, or for internal helper objects never exposed to user code.

## References

- [N-API Object Type Tag](https://nodejs.org/api/n-api.html#napi_type_tag_object)
- [N-API Check Object Type Tag](https://nodejs.org/api/n-api.html#napi_check_object_type_tag)
- [CWE-843: Type Confusion](https://cwe.mitre.org/data/definitions/843.html)
