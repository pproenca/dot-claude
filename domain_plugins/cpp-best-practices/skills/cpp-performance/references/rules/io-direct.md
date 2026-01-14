---
title: Use Direct I/O for Large Sequential Transfers
impact: MEDIUM
impactDescription: bypasses page cache, reduces memory pressure, predictable latency
tags: io, direct-io, o_direct, bypass-cache, database
---

## Use Direct I/O for Large Sequential Transfers

Direct I/O bypasses the OS page cache, which is beneficial when you manage your own caching or when sequential access would pollute the cache.

**Incorrect (polluting page cache):**

```cpp
void copyLargeFile(const char* src, const char* dst) {
    std::ifstream in(src, std::ios::binary);
    std::ofstream out(dst, std::ios::binary);

    char buffer[1024 * 1024];  // 1MB buffer
    while (in.read(buffer, sizeof(buffer))) {
        out.write(buffer, in.gcount());
    }
    // Problem: Both files now in page cache
    // Evicts useful cached data from memory
}
```

**Correct (direct I/O bypassing cache):**

```cpp
#include <fcntl.h>
#include <unistd.h>

void copyLargeFileDirect(const char* src, const char* dst) {
    int in_fd = open(src, O_RDONLY | O_DIRECT);
    int out_fd = open(dst, O_WRONLY | O_CREAT | O_TRUNC | O_DIRECT, 0644);

    // Buffer must be aligned for O_DIRECT
    constexpr size_t BLOCK_SIZE = 512 * 1024;  // 512KB
    void* buffer = aligned_alloc(4096, BLOCK_SIZE);

    ssize_t bytes;
    while ((bytes = read(in_fd, buffer, BLOCK_SIZE)) > 0) {
        write(out_fd, buffer, bytes);
    }

    free(buffer);
    close(in_fd);
    close(out_fd);
}
```

**Aligned buffer allocation:**

```cpp
// C++17 aligned allocation
template<size_t Alignment>
class AlignedBuffer {
    void* data_;
    size_t size_;
public:
    AlignedBuffer(size_t size)
        : data_(std::aligned_alloc(Alignment, size)), size_(size) {
        if (!data_) throw std::bad_alloc();
    }
    ~AlignedBuffer() { std::free(data_); }

    char* data() { return static_cast<char*>(data_); }
    size_t size() const { return size_; }
};

// Usage for O_DIRECT (typically 4KB alignment)
AlignedBuffer<4096> buffer(512 * 1024);
```

**When to use direct I/O:**

```cpp
// Database-style buffered I/O with own cache
class DatabaseFile {
    int fd_;
    std::unordered_map<size_t, Page> pageCache_;

public:
    DatabaseFile(const char* path)
        : fd_(open(path, O_RDWR | O_DIRECT)) {}

    Page& getPage(size_t pageNum) {
        auto it = pageCache_.find(pageNum);
        if (it != pageCache_.end()) return it->second;

        // Read page directly into our cache
        Page& page = pageCache_[pageNum];
        pread(fd_, page.data(), PAGE_SIZE, pageNum * PAGE_SIZE);
        return page;
    }
};
```

**When NOT to use direct I/O:**
- Small random reads (page cache helps)
- Frequently accessed data (caching benefits)
- When you don't control buffer alignment

Reference: [O_DIRECT and Raw I/O](https://man7.org/linux/man-pages/man2/open.2.html)
