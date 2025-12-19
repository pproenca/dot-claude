# Complex Test Plan

**Goal:** Test parallel execution grouping with realistic file dependencies

**Architecture:** Multiple tasks with overlapping and independent files

---

### Task 1: Create user model

**Files:**
- Create: `src/models/user.ts`
- Modify: `src/models/index.ts`

**TDD Instructions (MANDATORY):**

1. Create user model with id, email, name fields
2. Export from index

---

### Task 2: Create auth service

**Files:**
- Create: `src/services/auth.ts`
- Modify: `src/models/user.ts`

**TDD Instructions (MANDATORY):**

1. Create auth service using user model
2. Implement login/logout methods

---

### Task 3: Create product model

**Files:**
- Create: `src/models/product.ts`
- Modify: `src/models/index.ts`

**TDD Instructions (MANDATORY):**

1. Create product model (independent of user)

---

### Task 4: Create cart service

**Files:**
- Create: `src/services/cart.ts`
- Modify: `src/models/product.ts`

**TDD Instructions (MANDATORY):**

1. Create cart service using product model

---

### Task 5: Create API routes

**Files:**
- Create: `src/routes/api.ts`
- Modify: `src/services/auth.ts`
- Modify: `src/services/cart.ts`

**TDD Instructions (MANDATORY):**

1. Create API routes using both services

---

### Task 6: Add logging utility

**Files:**
- Create: `src/utils/logger.ts`

**TDD Instructions (MANDATORY):**

1. Create standalone logging utility (no dependencies)

---

### Task 7: Add config loader

**Files:**
- Create: `src/utils/config.ts`

**TDD Instructions (MANDATORY):**

1. Create standalone config loader (no dependencies)

---

### Task 8: Integration tests

**Files:**
- Create: `tests/integration/api.test.ts`
- Test: `src/routes/api.ts`

**TDD Instructions (MANDATORY):**

1. Write integration tests for API routes
