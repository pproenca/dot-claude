---
title: Use Path Aliases
impact: MEDIUM
impactDescription: eliminates ../../../ import chains
tags: module, paths, aliases, tsconfig
---

## Use Path Aliases

Configure path aliases for cleaner imports in large projects.

**Incorrect (relative import hell):**

```typescript
import { User } from '../../../models/user';
import { formatDate } from '../../../../utils/date';
import { API_URL } from '../../../../../config';
```

**Correct (path aliases):**

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@models/*": ["src/models/*"],
      "@utils/*": ["src/utils/*"]
    }
  }
}

// Now imports are clean
import { User } from '@models/user';
import { formatDate } from '@utils/date';
import { API_URL } from '@/config';
```

Reference: [TypeScript Path Mapping](https://www.typescriptlang.org/tsconfig#paths)
