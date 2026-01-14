---
title: Organize by Feature
impact: MEDIUM
impactDescription: improves code discoverability
tags: module, organization, feature, structure
---

## Organize by Feature

Group related code by feature rather than by type.

**Incorrect (organized by type):**

```
src/
  controllers/
    userController.ts
    orderController.ts
  services/
    userService.ts
    orderService.ts
  models/
    user.ts
    order.ts
```

**Correct (organized by feature):**

```
src/
  users/
    user.controller.ts
    user.service.ts
    user.model.ts
    user.types.ts
    index.ts
  orders/
    order.controller.ts
    order.service.ts
    order.model.ts
    order.types.ts
    index.ts
```

Reference: [Project Structure Best Practices](https://www.typescriptlang.org/docs/handbook/declaration-files/library-structures.html)
