---
title: Minimize Pointer Chasing in Hot Paths
impact: MEDIUM-HIGH
impactDescription: reduces cache misses in traversals
tags: cache, pointer-chasing, indirection, memory-access, prefetch
---

## Minimize Pointer Chasing in Hot Paths

Each pointer dereference can cause a cache miss. In hot paths, flatten data structures or use indices instead of pointers to improve cache utilization.

**Incorrect (pointer chasing):**

```cpp
struct Node {
    int data;
    Node* next;
    Node* child;
};

// Each access potentially misses cache
int sumTree(Node* root) {
    if (!root) return 0;
    return root->data +
           sumTree(root->next) +   // Cache miss
           sumTree(root->child);   // Cache miss
}

// Linked list traversal
int sumList(Node* head) {
    int sum = 0;
    while (head) {
        sum += head->data;
        head = head->next;  // Cache miss for each node
    }
    return sum;
}
```

**Correct (flatten to vector):**

```cpp
// Flatten tree to vector for processing
struct FlatNode {
    int data;
    int firstChild;  // Index, not pointer
    int nextSibling; // Index, not pointer
};

std::vector<FlatNode> nodes;

int sumTree(const std::vector<FlatNode>& nodes, int root) {
    if (root < 0) return 0;
    return nodes[root].data +
           sumTree(nodes, nodes[root].firstChild) +
           sumTree(nodes, nodes[root].nextSibling);
}

// Even better: level-order storage for sequential access
std::vector<int> treeData;  // Stored level by level
```

**Pool allocation for cache locality:**

```cpp
// Allocate nodes from a pool for locality
class NodePool {
    std::vector<Node> pool_;
    size_t next_ = 0;
public:
    Node* allocate() {
        if (next_ >= pool_.size()) {
            pool_.resize(pool_.size() + 1024);
        }
        return &pool_[next_++];
    }
};

// Nodes allocated sequentially are likely in same cache lines
```

**Prefetch for unavoidable pointer chasing:**

```cpp
int sumListPrefetch(Node* head) {
    int sum = 0;
    while (head) {
        // Prefetch next node while processing current
        if (head->next) {
            __builtin_prefetch(head->next);
        }
        sum += head->data;
        head = head->next;
    }
    return sum;
}
```

**Index-based graph:**

```cpp
struct Graph {
    std::vector<int> edgeData;
    std::vector<int> edgeOffsets;  // CSR format

    // Iterate neighbors without pointer chasing
    void forEachNeighbor(int node, auto&& func) {
        int start = edgeOffsets[node];
        int end = edgeOffsets[node + 1];
        for (int i = start; i < end; ++i) {
            func(edgeData[i]);
        }
    }
};
```

Reference: [What Every Programmer Should Know About Memory](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf)
