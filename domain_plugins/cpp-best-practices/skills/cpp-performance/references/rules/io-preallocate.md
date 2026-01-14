---
title: Preallocate File Space to Avoid Fragmentation
impact: MEDIUM
impactDescription: reduces syscalls, prevents fragmentation, enables sequential writes
tags: io, preallocate, fallocate, file-system, write-performance
---

## Preallocate File Space to Avoid Fragmentation

When writing large files, preallocating space prevents filesystem fragmentation and reduces metadata updates during writes.

**Incorrect (growing file incrementally):**

```cpp
void writeDataIncrementally(const std::string& path,
                           const std::vector<Record>& records) {
    std::ofstream file(path, std::ios::binary);
    for (const auto& record : records) {
        file.write(reinterpret_cast<const char*>(&record), sizeof(record));
        // Each write may trigger filesystem block allocation
        // Causes fragmentation with many small allocations
    }
}
```

**Correct (preallocate then write):**

```cpp
#include <fcntl.h>
#include <unistd.h>

void writeDataPreallocated(const std::string& path,
                          const std::vector<Record>& records) {
    int fd = open(path.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0644);

    // Preallocate the entire file
    size_t totalSize = records.size() * sizeof(Record);
    posix_fallocate(fd, 0, totalSize);  // Allocates contiguous blocks

    // Now write without allocation overhead
    write(fd, records.data(), totalSize);
    close(fd);
}
```

**Using ftruncate for simple preallocation:**

```cpp
void preallocateFile(int fd, size_t size) {
#ifdef __linux__
    // Linux: fallocate is most efficient
    fallocate(fd, 0, 0, size);
#elif defined(__APPLE__)
    // macOS: use F_PREALLOCATE
    fstore_t store = {F_ALLOCATEALL, F_PEOFPOSMODE, 0, (off_t)size, 0};
    fcntl(fd, F_PREALLOCATE, &store);
    ftruncate(fd, size);
#else
    // Portable fallback
    ftruncate(fd, size);
#endif
}
```

**Batch writes with preallocation:**

```cpp
class PreallocatedWriter {
    int fd_;
    size_t position_ = 0;
    size_t capacity_ = 0;

public:
    PreallocatedWriter(const char* path, size_t expectedSize) {
        fd_ = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
        capacity_ = expectedSize;
        posix_fallocate(fd_, 0, capacity_);
    }

    void write(const void* data, size_t size) {
        if (position_ + size > capacity_) {
            // Extend allocation if needed
            capacity_ = (position_ + size) * 2;
            posix_fallocate(fd_, 0, capacity_);
        }
        ::write(fd_, data, size);
        position_ += size;
    }

    ~PreallocatedWriter() {
        ftruncate(fd_, position_);  // Trim to actual size
        close(fd_);
    }
};
```

Reference: [posix_fallocate(3)](https://man7.org/linux/man-pages/man3/posix_fallocate.3.html)
