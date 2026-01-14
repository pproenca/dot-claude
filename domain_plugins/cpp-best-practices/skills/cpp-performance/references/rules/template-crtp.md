---
title: Use CRTP for Static Polymorphism
impact: LOW
impactDescription: zero-overhead polymorphism, enables inlining
tags: template, crtp, polymorphism, optimization, zero-overhead
---

## Use CRTP for Static Polymorphism

Curiously Recurring Template Pattern (CRTP) provides polymorphism without virtual function overhead. Use when the derived type is known at compile time.

**Incorrect (virtual dispatch overhead):**

```cpp
class Shape {
public:
    virtual double area() const = 0;
    virtual void draw() const = 0;
    virtual ~Shape() = default;
};

class Circle : public Shape {
    double radius_;
public:
    Circle(double r) : radius_(r) {}
    double area() const override { return 3.14159 * radius_ * radius_; }
    void draw() const override { /* ... */ }
};

// Every call goes through vtable - can't inline
void process(const Shape& shape) {
    auto a = shape.area();  // Virtual call
    shape.draw();           // Virtual call
}
```

**Correct (CRTP static polymorphism):**

```cpp
template<typename Derived>
class Shape {
public:
    double area() const {
        return static_cast<const Derived*>(this)->areaImpl();
    }
    void draw() const {
        static_cast<const Derived*>(this)->drawImpl();
    }
};

class Circle : public Shape<Circle> {
    double radius_;
public:
    Circle(double r) : radius_(r) {}
    double areaImpl() const { return 3.14159 * radius_ * radius_; }
    void drawImpl() const { /* ... */ }
};

// Calls are inlined - zero overhead
template<typename T>
void process(const Shape<T>& shape) {
    auto a = shape.area();  // Inlined
    shape.draw();           // Inlined
}
```

**CRTP for mixin functionality:**

```cpp
// Add comparison operators via CRTP
template<typename Derived>
class Comparable {
public:
    bool operator!=(const Derived& other) const {
        return !(*static_cast<const Derived*>(this) == other);
    }
    bool operator<=(const Derived& other) const {
        return !(other < *static_cast<const Derived*>(this));
    }
    bool operator>(const Derived& other) const {
        return other < *static_cast<const Derived*>(this);
    }
    bool operator>=(const Derived& other) const {
        return !(*static_cast<const Derived*>(this) < other);
    }
};

class Point : public Comparable<Point> {
public:
    int x, y;
    bool operator==(const Point& o) const { return x == o.x && y == o.y; }
    bool operator<(const Point& o) const {
        return x < o.x || (x == o.x && y < o.y);
    }
    // Gets !=, <=, >, >= for free
};
```

**CRTP for clone pattern:**

```cpp
template<typename Derived>
class Cloneable {
public:
    std::unique_ptr<Derived> clone() const {
        return std::make_unique<Derived>(*static_cast<const Derived*>(this));
    }
};

class Widget : public Cloneable<Widget> {
    int value_;
public:
    Widget(int v) : value_(v) {}
};

auto w1 = std::make_unique<Widget>(42);
auto w2 = w1->clone();  // Correct type without virtual
```

**When to use virtual functions instead:**
- Runtime type selection (factory patterns)
- Plugin architectures
- Type erasure needed
- Heterogeneous containers

Reference: [CRTP](https://en.wikipedia.org/wiki/Curiously_recurring_template_pattern)
