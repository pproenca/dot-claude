---
title: Use Binary I/O for Structured Data
impact: MEDIUM
impactDescription: 5-10x faster than text parsing
tags: io, binary, serialization, performance, files
---

## Use Binary I/O for Structured Data

Text formats require parsing and formatting overhead. For internal data storage, binary I/O is much faster and more compact.

**Incorrect (text format - slow parsing):**

```cpp
struct Record {
    int id;
    double value;
    std::string name;
};

void saveRecordsText(const std::vector<Record>& records, const std::string& path) {
    std::ofstream file(path);
    for (const auto& r : records) {
        file << r.id << ',' << r.value << ',' << r.name << '\n';
    }
}

std::vector<Record> loadRecordsText(const std::string& path) {
    std::vector<Record> records;
    std::ifstream file(path);
    std::string line;
    while (std::getline(file, line)) {
        // Parse each field - slow and error-prone
        Record r;
        std::sscanf(line.c_str(), "%d,%lf,", &r.id, &r.value);
        // ... parse name
        records.push_back(r);
    }
    return records;
}
```

**Correct (binary format - fast):**

```cpp
// For POD types with fixed-size strings
struct RecordBinary {
    int32_t id;
    double value;
    char name[64];  // Fixed size for binary I/O
};

void saveRecordsBinary(const std::vector<RecordBinary>& records,
                       const std::string& path) {
    std::ofstream file(path, std::ios::binary);
    uint64_t count = records.size();
    file.write(reinterpret_cast<const char*>(&count), sizeof(count));
    file.write(reinterpret_cast<const char*>(records.data()),
               records.size() * sizeof(RecordBinary));
}

std::vector<RecordBinary> loadRecordsBinary(const std::string& path) {
    std::ifstream file(path, std::ios::binary);
    uint64_t count;
    file.read(reinterpret_cast<char*>(&count), sizeof(count));
    std::vector<RecordBinary> records(count);
    file.read(reinterpret_cast<char*>(records.data()),
              count * sizeof(RecordBinary));
    return records;
}
```

**Memory-mapped binary for large files:**

```cpp
class MappedRecords {
    void* data_;
    size_t size_;
    size_t count_;
public:
    MappedRecords(const char* path) {
        int fd = open(path, O_RDONLY);
        struct stat st;
        fstat(fd, &st);
        size_ = st.st_size;
        data_ = mmap(nullptr, size_, PROT_READ, MAP_PRIVATE, fd, 0);
        close(fd);
        count_ = *reinterpret_cast<uint64_t*>(data_);
    }

    const RecordBinary& operator[](size_t i) const {
        auto base = static_cast<char*>(data_) + sizeof(uint64_t);
        return reinterpret_cast<const RecordBinary*>(base)[i];
    }

    ~MappedRecords() { munmap(data_, size_); }
};
```

**Consider serialization libraries for complex types:**

```cpp
// Protocol Buffers, FlatBuffers, Cap'n Proto
// More portable, versioned, but still binary

// FlatBuffers example - zero-copy access
auto monster = GetMonster(buffer);
auto name = monster->name()->str();
auto hp = monster->hp();
```

**When to use text formats:**
- Human-readable configuration
- Interoperability with other languages
- Debugging and logging
- External API communication

Reference: [FlatBuffers](https://google.github.io/flatbuffers/)
