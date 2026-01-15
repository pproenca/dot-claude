---
title: Implement Proper Destructor Cleanup
impact: MEDIUM-HIGH
impactDescription: prevents resource leaks when objects are garbage collected
tags: wrap, destructor, cleanup, prevent-leaks
---

## Implement Proper Destructor Cleanup

ObjectWrap instances are destroyed when their JS wrapper is garbage collected. Implement proper cleanup in the destructor.

**Incorrect (resources leak):**

```cpp
class FileHandle : public Napi::ObjectWrap<FileHandle> {
 public:
  FileHandle(const Napi::CallbackInfo& info)
      : Napi::ObjectWrap<FileHandle>(info) {
    fd_ = open(path, O_RDONLY);
  }
  // No destructor - file descriptor leaks!

 private:
  int fd_;
};
```

**Correct (cleanup in destructor):**

```cpp
class FileHandle : public Napi::ObjectWrap<FileHandle> {
 public:
  FileHandle(const Napi::CallbackInfo& info)
      : Napi::ObjectWrap<FileHandle>(info) {
    fd_ = open(path, O_RDONLY);
  }

  ~FileHandle() {
    if (fd_ >= 0) {
      close(fd_);
      fd_ = -1;
    }
  }

  void Close(const Napi::CallbackInfo& info) {
    if (fd_ >= 0) {
      close(fd_);
      fd_ = -1;
    }
  }

 private:
  int fd_ = -1;
};
```

Reference: [ObjectWrap Documentation](https://github.com/nodejs/node-addon-api/blob/main/doc/object_wrap.md)
