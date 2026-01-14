---
title: Use Memory-Mapped Files for Large File Access
impact: MEDIUM
impactDescription: avoids copying, enables random access, leverages OS page cache
tags: io, mmap, memory-mapping, large-files, random-access
---

## Use Memory-Mapped Files for Large File Access

Memory-mapped files allow treating file contents as memory, eliminating explicit read/write calls and leveraging the OS page cache for efficient large file access.

**Incorrect (explicit reading into buffer):**

```cpp
std::vector<char> readLargeFile(const std::string& path) {
    std::ifstream file(path, std::ios::binary | std::ios::ate);
    auto size = file.tellg();
    file.seekg(0);

    std::vector<char> buffer(size);
    file.read(buffer.data(), size);  // Copies entire file
    return buffer;  // Another copy on return
}

// Random access requires seeking
char getByteAt(std::ifstream& file, size_t offset) {
    file.seekg(offset);
    char c;
    file.read(&c, 1);  // Expensive for random access
    return c;
}
```

**Correct (memory-mapped file):**

```cpp
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>

class MappedFile {
    void* data_ = nullptr;
    size_t size_ = 0;
    int fd_ = -1;

public:
    MappedFile(const char* path) {
        fd_ = open(path, O_RDONLY);
        if (fd_ < 0) return;

        struct stat st;
        fstat(fd_, &st);
        size_ = st.st_size;

        data_ = mmap(nullptr, size_, PROT_READ, MAP_PRIVATE, fd_, 0);
    }

    ~MappedFile() {
        if (data_ != MAP_FAILED) munmap(data_, size_);
        if (fd_ >= 0) close(fd_);
    }

    const char* data() const { return static_cast<const char*>(data_); }
    size_t size() const { return size_; }

    // Random access is now O(1)
    char operator[](size_t i) const { return data()[i]; }
};
```

**Cross-platform with std::span (C++20):**

```cpp
#ifdef _WIN32
#include <windows.h>
class MappedFile {
    HANDLE file_, mapping_;
    void* data_;
    size_t size_;
public:
    MappedFile(const wchar_t* path) {
        file_ = CreateFileW(path, GENERIC_READ, FILE_SHARE_READ,
                           nullptr, OPEN_EXISTING, 0, nullptr);
        size_ = GetFileSize(file_, nullptr);
        mapping_ = CreateFileMappingW(file_, nullptr, PAGE_READONLY, 0, 0, nullptr);
        data_ = MapViewOfFile(mapping_, FILE_MAP_READ, 0, 0, 0);
    }
    std::span<const char> data() const {
        return {static_cast<const char*>(data_), size_};
    }
};
#endif
```

**Best practices:**
- Use `MAP_POPULATE` for sequential access (prefetch pages)
- Use `madvise(MADV_RANDOM)` for random access patterns
- Don't map huge files entirely - map regions as needed

Reference: [mmap(2) man page](https://man7.org/linux/man-pages/man2/mmap.2.html)
