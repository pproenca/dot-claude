# One-shot scaffold (TS/Node)

Generate all of this in the Phase-2 commit. Patterns are distilled from
`openclaw/clawpatch` (verified against source). Replace `tool` with your CLI name.

## `src/errors.ts` — typed error: string `code` + numeric `exitCode`
```ts
export class ToolError extends Error {
  public readonly exitCode: number;
  public readonly code: string;
  public constructor(message: string, exitCode = 1, code = "runtime") {
    super(message);
    this.name = "ToolError";
    this.exitCode = exitCode;
    this.code = code;
  }
}
```
Tests assert on the stable `code` string; the OS sees `exitCode`. Conversion happens
ONLY at the top-level catch (below). Reserved high codes: auth=4, quota=5,
validation=6, lock=7, malformed-model-output=8.

## `src/cli.ts` — flag table, dispatch, output discipline, exit catch
```ts
// Per-command flag whitelist, validated BEFORE any side effect.
const commandFlags = {
  init: new Set(["force"]),
  map: new Set(["dryRun", "provider", "model"]),
  review: new Set(["feature", "limit", "jobs", "since", "provider", "model"]),
  fix: new Set(["finding", "dryRun", "yes", "provider", "model"]),
  // ...
} satisfies Record<string, Set<string>>;

const requiredCommandFlags: Partial<Record<string, string[]>> = {
  fix: ["finding"],
};

const globalFlags = new Set([
  "root", "stateDir", "config", "json", "plain",
  "quiet", "verbose", "debug", "noColor", "noInput",
]);

async function dispatch(ctx: Context, command: string, flags: Flags): Promise<unknown> {
  switch (command) {
    case "init": return initCommand(ctx, flags);
    case "map": return mapCommand(ctx, flags);
    case "review": return reviewCommand(ctx, flags);
    // ...
    default:
      throw new ToolError(`unknown command: ${command}`, 2, "invalid-usage");
  }
}

// stdout is ONLY for results. --json => pretty JSON; markdown if present; else key:value lines.
function writeResult(result: unknown, options: GlobalOptions): void {
  if (options.json) { process.stdout.write(`${JSON.stringify(result, null, 2)}\n`); return; }
  if (result && typeof result === "object" && "markdown" in result && !options.plain) {
    process.stdout.write(String((result as { markdown: unknown }).markdown)); return;
  }
  for (const [k, v] of Object.entries(result as Record<string, unknown>)) {
    if (v === null || typeof v === "object") continue;
    process.stdout.write(`${k}: ${String(v)}\n`);
  }
}

main(process.argv.slice(2)).catch((error: unknown) => {
  if (error instanceof ToolError) {
    process.stderr.write(`error: ${error.message}\n`);
    process.exitCode = error.exitCode;
    return;
  }
  process.stderr.write(`error: ${error instanceof Error ? error.message : String(error)}\n`);
  process.exitCode = 1;
});
```
`validateCommandFlags` rejects unknown flags per command (exit 2 — never silently
ignore). Progress goes to stderr only, gated by `options.quiet`.

## `src/provider.ts` — the adapter interface + boundary parse + one mock
```ts
import { z } from "zod";

export type ProviderOptions = {
  model: string | null;
  reasoningEffort: string | null;
  skipGitRepoCheck: boolean;
};

export type Provider = {
  name: string;
  check(root: string): Promise<string>;                                  // verify CLI present/authed
  map(root: string, prompt: string, o: ProviderOptions): Promise<MapOutput>;
  review(root: string, prompt: string, o: ProviderOptions): Promise<ReviewOutput>;
  fix(root: string, prompt: string, o: ProviderOptions): Promise<FixPlanOutput>;     // the ONLY mutating method
  revalidate(root: string, prompt: string, o: ProviderOptions): Promise<RevalidateOutput>;
};

// THE single boundary. All model output is `unknown` until it passes here.
export function parseOrThrow<T>(schema: z.ZodType<T>, input: unknown, label: string): T {
  const result = schema.safeParse(input);
  if (result.success) return result.data;
  throw new ToolError(`${label}: ${formatZodError(result.error)}`, 8, "malformed-output");
}

// Generate a strict JSON schema from a zod type to constrain the model.
export function providerJsonSchema(schema: z.ZodType): object {
  const json = z.toJSONSchema(schema, { io: "input", unrepresentable: "any" }) as Record<string, unknown>;
  return forceStrict(json); // additionalProperties:false + required = all keys, recursively
}

export function providerByName(name: string): Provider {
  switch (name) {
    case "codex": return codexProvider;
    case "mock": return mockProvider;
    default: throw new ToolError(`unsupported provider: ${name}`, 2, "unsupported-provider");
  }
}
```
Each real provider runs **read-only by default**; only `fix` opts into a
workspace-write sandbox. Detect auth/quota from output and throw `4`/`5`. The `mock`
provider reacts to fixture markers (e.g. a `TODO_BUG` comment) so the whole pipeline
is testable with no network.

For list output (e.g. review findings), partition instead of all-or-nothing: validate
the container, then `safeParse` each item, keep valid ones, record dropped ones — a
fundamentally wrong container still throws `malformed-output` (8).

## `src/fs.ts` — atomic write, validated read
```ts
export async function writeJson(path: string, value: unknown): Promise<void> {
  await ensureDir(dirname(path));
  const tmp = `${path}.tmp-${process.pid}-${Date.now()}-${randomUUID()}`;
  await writeFile(tmp, `${JSON.stringify(value, null, 2)}\n`, "utf8");
  await rename(tmp, path);                       // atomic
}

export async function readJson<T>(path: string, schema: z.ZodType<T>): Promise<T> {
  const raw = await readFile(path, "utf8");
  let parsed: unknown;
  try { parsed = JSON.parse(raw); }
  catch { throw new ToolError(`corrupt state: ${path}`, 1, "malformed-state"); } // wrap! (clawpatch gap)
  const r = schema.safeParse(parsed);
  if (!r.success) throw new ToolError(`invalid state: ${path}`, 1, "malformed-state");
  return r.data;
}
```
> Note: clawpatch uses bare `JSON.parse` + `schema.parse` here, so corrupt state
> surfaces as an untyped exit 1. The wrapped version above is the improvement to ship.

## `src/state.ts` — one file per record, dir layout, lock
```ts
export function statePaths(stateDir: string) {
  return {
    stateDir,
    config: join(stateDir, "config.json"),
    project: join(stateDir, "project.json"),
    features: join(stateDir, "features"),  // <id>.json each
    findings: join(stateDir, "findings"),
    runs: join(stateDir, "runs"),
    patches: join(stateDir, "patches"),
    locks: join(stateDir, "locks"),        // <id>.json lock files
  };
}

// Exclusive-create lock; EEXIST => lock-conflict (7).
export async function claim(lockPath: string, runId: string): Promise<void> {
  try {
    const fd = await open(lockPath, "wx");
    await fd.writeFile(JSON.stringify({ lockedByRunId: runId, lockedAt: new Date().toISOString(), pid: process.pid }));
    await fd.close();
  } catch (e) {
    if ((e as NodeJS.ErrnoException).code === "EEXIST") throw new ToolError(`feature locked`, 7, "lock-conflict");
    throw e;
  }
}
```

## `src/types.ts` — records as zod, with `schemaVersion`
```ts
export const findingRecordSchema = z.object({
  schemaVersion: z.literal(1),
  findingId: z.string(),
  category: z.enum(["bug", "security", "performance", "test-gap", "maintainability"]),
  severity: z.enum(["critical", "high", "medium", "low"]),
  confidence: z.enum(["high", "medium", "low"]),
  evidence: z.array(z.object({ path: z.string(), startLine: z.number().nullable(), quote: z.string().nullable() })),
  status: z.enum(["open", "false-positive", "fixed", "wont-fix", "uncertain"]),
  signature: z.string(),
  createdAt: z.string(),
  updatedAt: z.string(),
});
export type FindingRecord = z.infer<typeof findingRecordSchema>;
```

## `src/plugins/types.ts` — the breadth interface (mapper/adapter example)
```ts
export type FeatureMapper = {
  name: string;
  map(root: string, ctx: MapperContext): Promise<FeatureSeed[]>;  // returns raw "what I found"
};
```
Register in one array; run in parallel; dedupe by a stable key. A separate enrichment
step turns seeds into persisted records. Adding a language/framework = one new file +
one array entry — the core never changes.
```ts
const mappers: FeatureMapper[] = [
  { name: "node", map: nodeSeeds },
  { name: "go", map: goSeeds },
  // new breadth here
];
const seeds = dedupeSeeds((await Promise.all(mappers.map((m) => m.map(root, ctx)))).flat());
```

## Config files
**`package.json`**
```json
{
  "type": "module",
  "bin": { "tool": "dist/cli.js" },
  "files": ["dist", "README.md", "LICENSE"],
  "engines": { "node": ">=22" },
  "packageManager": "pnpm@11.1.2",
  "scripts": {
    "build": "tsc -p tsconfig.build.json",
    "prepack": "pnpm -s build",
    "typecheck": "tsc -p tsconfig.json --noEmit",
    "lint": "oxlint . --config oxlint.json",
    "format": "oxfmt --write .",
    "format:check": "oxfmt --check .",
    "test": "vitest run",
    "pack:smoke": "node scripts/package-smoke.mjs"
  },
  "dependencies": { "zod": "^4.4.3" },
  "devDependencies": { "oxlint": "^1", "oxfmt": "^0.50", "typescript": "^6", "vitest": "^4", "@types/node": "^25" }
}
```
**`tsconfig.json`** (every strictness flag on)
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "noPropertyAccessFromIndexSignature": true,
    "module": "NodeNext", "moduleResolution": "NodeNext", "target": "ES2024",
    "declaration": true, "skipLibCheck": true, "outDir": "dist"
  }
}
```
**`oxlint.json`**: `{ "categories": { "correctness": "error", "suspicious": "error" }, "ignorePatterns": ["dist/**", ".tool/**"] }`
**`.oxfmtrc.json`**: `{ "tabWidth": 2, "useTabs": false }`
**`.gitignore`**: `node_modules/`, `dist/`, `coverage/`, and your state runtime dirs (`.tool/runs/`, `.tool/findings/`, `.tool/patches/`, `.tool/locks/`).

## `.github/workflows/ci.yml` — the gate
```yaml
name: CI
on: { pull_request: {}, push: { branches: [main] } }
permissions: { contents: read }
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with: { version: 11.1.2 }
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm typecheck
      - run: pnpm lint
      - run: pnpm format:check
      - run: pnpm test
      - run: pnpm build
      - run: pnpm pack:smoke
```

## Test pattern (vitest, fixture + mock provider, assert on `code`)
```ts
it("flags a TODO_BUG via the mock provider", async () => {
  const root = await mkdtemp(join(tmpdir(), "tool-"));
  await writeFixture(root, "src/index.ts", "// TODO_BUG: off-by-one\nexport const x = 1;\n");
  process.env["TOOL_PROVIDER"] = "mock";
  const ctx = await makeContext(testOptions(root));
  await initCommand(ctx, {});
  await mapCommand(ctx, {});
  const reviewed = await reviewCommand(ctx, { limit: "1" });
  expect(reviewed).toMatchObject({ findings: 1 });
});

it("refuses fix on a dirty worktree", async () => {
  await expect(fixCommand(ctx, { finding })).rejects.toMatchObject({ code: "dirty-worktree" });
});
```
No snapshots. One focused `it` per behavior. New mapper/feature = new `it` with the
minimal fixture that triggers it, asserting the exact output.
