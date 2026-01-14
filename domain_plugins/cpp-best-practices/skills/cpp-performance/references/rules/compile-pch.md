---
title: Use Precompiled Headers for Stable Dependencies
impact: HIGH
impactDescription: 30-70% faster incremental builds
tags: compile, precompiled-headers, pch, build-time, includes
---

## Use Precompiled Headers for Stable Dependencies

Precompiled headers (PCH) cache parsed headers that rarely change. Include stable dependencies (STL, third-party libraries) in PCH to avoid re-parsing them for every file.

**Incorrect (re-parsing STL in every file):**

```cpp
// Every .cpp file includes these
#include <vector>
#include <string>
#include <map>
#include <algorithm>
#include <memory>
#include <iostream>
// Each file re-parses ~50,000 lines of STL headers
```

**Correct (precompiled header):**

```cpp
// pch.h - precompiled header
#pragma once

// Standard library (stable)
#include <vector>
#include <string>
#include <map>
#include <unordered_map>
#include <algorithm>
#include <memory>
#include <functional>
#include <iostream>
#include <sstream>

// Third-party libraries (stable)
#include <boost/asio.hpp>
#include <nlohmann/json.hpp>

// DO NOT include project headers that change frequently

// pch.cpp - force compilation
#include "pch.h"
```

**CMake configuration:**

```cmake
# CMakeLists.txt
target_precompile_headers(myapp PRIVATE
    <vector>
    <string>
    <memory>
    <algorithm>
    "third_party/json.hpp"
)

# Or use a PCH file
target_precompile_headers(myapp PRIVATE pch.h)
```

**What to include in PCH:**
- Standard library headers
- Stable third-party headers
- System headers

**What NOT to include:**
- Project headers that change often
- Headers with macros that affect other code
- Rarely-used large headers

**Measure impact:**

```bash
# Without PCH
time make -j8 clean all  # 45s

# With PCH
time make -j8 clean all  # 18s (60% faster)
```

Reference: [CMake Precompile Headers](https://cmake.org/cmake/help/latest/command/target_precompile_headers.html)
