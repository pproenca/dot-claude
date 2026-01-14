---
title: Use Type Erasure for Runtime Flexibility
impact: LOW
impactDescription: combine templates with runtime polymorphism
tags: template, type-erasure, polymorphism, std-function, any
---

## Use Type Erasure for Runtime Flexibility

Type erasure hides template types behind a common interface, combining generic programming with runtime flexibility. Use standard library facilities like `std::function` and `std::any`.

**Problem (templates require compile-time types):**

```cpp
// Can't store different callable types in same container
std::vector<???> callbacks;
callbacks.push_back([](int x) { return x * 2; });
callbacks.push_back(&freeFunction);
callbacks.push_back(std::bind(&Class::method, obj, _1));
```

**Solution (std::function type erasure):**

```cpp
// std::function erases the callable type
std::vector<std::function<int(int)>> callbacks;
callbacks.push_back([](int x) { return x * 2; });
callbacks.push_back(&freeFunction);
callbacks.push_back([&obj](int x) { return obj.method(x); });

for (auto& cb : callbacks) {
    int result = cb(42);  // All callable through same interface
}
```

**std::any for arbitrary types:**

```cpp
std::vector<std::any> values;
values.push_back(42);
values.push_back(std::string("hello"));
values.push_back(Widget{});

// Access with type check
for (const auto& v : values) {
    if (auto* i = std::any_cast<int>(&v)) {
        std::cout << "int: " << *i << '\n';
    } else if (auto* s = std::any_cast<std::string>(&v)) {
        std::cout << "string: " << *s << '\n';
    }
}
```

**Custom type erasure pattern:**

```cpp
// Type-erased drawable
class Drawable {
    struct Concept {
        virtual ~Concept() = default;
        virtual void draw() const = 0;
        virtual std::unique_ptr<Concept> clone() const = 0;
    };

    template<typename T>
    struct Model : Concept {
        T obj_;
        Model(T obj) : obj_(std::move(obj)) {}
        void draw() const override { obj_.draw(); }
        std::unique_ptr<Concept> clone() const override {
            return std::make_unique<Model>(*this);
        }
    };

    std::unique_ptr<Concept> impl_;

public:
    template<typename T>
    Drawable(T obj) : impl_(std::make_unique<Model<T>>(std::move(obj))) {}

    Drawable(const Drawable& other) : impl_(other.impl_->clone()) {}

    void draw() const { impl_->draw(); }
};

// Usage - store any drawable type
std::vector<Drawable> shapes;
shapes.push_back(Circle{});
shapes.push_back(Square{});
shapes.push_back(CustomShape{});
```

**Small buffer optimization for efficiency:**

```cpp
// Avoid allocation for small objects
template<size_t BufferSize = 64>
class SmallFunction {
    std::aligned_storage_t<BufferSize> buffer_;
    // Store small callables in buffer, heap for large ones
};

// std::function typically uses SBO for small lambdas
std::function<int()> small = []{ return 42; };  // No allocation
std::function<int()> large = [big_capture]{ ... };  // May allocate
```

**When to use type erasure:**
- Heterogeneous containers
- Callback registration
- Plugin systems
- Breaking template dependencies

**Costs:**
- Virtual call overhead
- Possible heap allocation
- No inlining

Reference: [Type Erasure](https://www.youtube.com/watch?v=tbUCHifyT24)
