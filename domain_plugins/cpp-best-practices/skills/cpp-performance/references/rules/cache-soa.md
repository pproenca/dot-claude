---
title: Use Structure of Arrays for Hot Data
impact: MEDIUM-HIGH
impactDescription: 2-4x faster for selective field access
tags: cache, soa, aos, data-layout, vectorization, simd
---

## Use Structure of Arrays for Hot Data

When processing only some fields of many objects, Structure of Arrays (SoA) layout keeps hot data together, improving cache utilization and enabling SIMD vectorization.

**Incorrect (Array of Structures - AoS):**

```cpp
// Traditional OOP layout
struct Particle {
    float x, y, z;        // Position (hot)
    float vx, vy, vz;     // Velocity (hot)
    int id;               // ID (cold)
    std::string name;     // Name (cold)
    // ... more cold fields
};

std::vector<Particle> particles(10000);

// Processing positions loads entire struct into cache
void updatePositions(std::vector<Particle>& p, float dt) {
    for (auto& particle : p) {
        particle.x += particle.vx * dt;  // Cache line contains cold data
        particle.y += particle.vy * dt;
        particle.z += particle.vz * dt;
    }
}
```

**Correct (Structure of Arrays - SoA):**

```cpp
struct Particles {
    // Hot data together
    std::vector<float> x, y, z;
    std::vector<float> vx, vy, vz;
    // Cold data separate
    std::vector<int> id;
    std::vector<std::string> name;

    size_t size() const { return x.size(); }
};

// Processing positions only loads position and velocity data
void updatePositions(Particles& p, float dt) {
    const size_t n = p.size();
    for (size_t i = 0; i < n; ++i) {
        p.x[i] += p.vx[i] * dt;  // Only hot data in cache
        p.y[i] += p.vy[i] * dt;
        p.z[i] += p.vz[i] * dt;
    }
}
```

**SIMD-friendly version:**

```cpp
// SoA enables auto-vectorization
void updatePositionsSIMD(Particles& p, float dt) {
    const size_t n = p.size();
    float* __restrict px = p.x.data();
    float* __restrict py = p.y.data();
    float* __restrict pz = p.z.data();
    const float* __restrict vx = p.vx.data();
    const float* __restrict vy = p.vy.data();
    const float* __restrict vz = p.vz.data();

    #pragma omp simd
    for (size_t i = 0; i < n; ++i) {
        px[i] += vx[i] * dt;
        py[i] += vy[i] * dt;
        pz[i] += vz[i] * dt;
    }
}
```

**Hybrid approach for related fields:**

```cpp
// Group related hot fields together
struct Vec3 { float x, y, z; };

struct Particles {
    std::vector<Vec3> position;  // Often accessed together
    std::vector<Vec3> velocity;
    // Cold data
    std::vector<int> id;
};
```

**When to use AoS:**
- Accessing all fields of each object
- Object identity is important
- Few objects or cold paths

Reference: [Data-Oriented Design](https://www.dataorienteddesign.com/dodbook/)
