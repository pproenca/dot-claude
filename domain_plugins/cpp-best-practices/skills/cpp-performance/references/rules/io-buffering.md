---
title: Use Buffered I/O and Batch Operations
impact: MEDIUM
impactDescription: 10-100x faster than unbuffered single operations
tags: io, buffering, batch, performance, streams
---

## Use Buffered I/O and Batch Operations

System calls are expensive. Buffer data and batch I/O operations to minimize syscall overhead and maximize throughput.

**Incorrect (unbuffered, single operations):**

```cpp
// Single character at a time - extremely slow
void writeChars(const std::string& data) {
    for (char c : data) {
        write(fd, &c, 1);  // Syscall per character!
    }
}

// Flushing after every line
void writeLines(std::ofstream& out, const std::vector<std::string>& lines) {
    for (const auto& line : lines) {
        out << line << '\n' << std::flush;  // Flush per line!
    }
}
```

**Correct (buffered, batched):**

```cpp
// Write entire buffer at once
void writeChars(const std::string& data) {
    write(fd, data.data(), data.size());  // Single syscall
}

// Let stream handle buffering
void writeLines(std::ofstream& out, const std::vector<std::string>& lines) {
    for (const auto& line : lines) {
        out << line << '\n';  // Buffered internally
    }
    // Flush once at end or let destructor handle it
}
```

**Larger buffer for bulk operations:**

```cpp
// Increase stream buffer size
std::ofstream out("large_file.txt");
std::vector<char> buffer(1024 * 1024);  // 1MB buffer
out.rdbuf()->pubsetbuf(buffer.data(), buffer.size());

// Now writes are batched in 1MB chunks
for (int i = 0; i < 1000000; ++i) {
    out << "line " << i << '\n';
}
```

**Disable sync with stdio for performance:**

```cpp
int main() {
    // Disable synchronization for faster I/O
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(nullptr);

    // Now iostream is faster but can't mix with printf/scanf
    std::string line;
    while (std::getline(std::cin, line)) {
        std::cout << process(line) << '\n';
    }
}
```

**Memory-mapped I/O for random access:**

```cpp
#include <sys/mman.h>
#include <fcntl.h>

class MappedFile {
    void* data_;
    size_t size_;
public:
    MappedFile(const char* path) {
        int fd = open(path, O_RDONLY);
        struct stat st;
        fstat(fd, &st);
        size_ = st.st_size;
        data_ = mmap(nullptr, size_, PROT_READ, MAP_PRIVATE, fd, 0);
        close(fd);
    }
    ~MappedFile() { munmap(data_, size_); }

    std::string_view view() const {
        return {static_cast<char*>(data_), size_};
    }
};
```

Reference: [I/O Performance](https://www.gnu.org/software/libc/manual/html_node/Stream-Buffering.html)
