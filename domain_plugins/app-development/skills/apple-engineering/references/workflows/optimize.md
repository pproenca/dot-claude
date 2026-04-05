# iOS Performance Optimization

You are guiding the user through profiling and optimizing an iOS/iPadOS app's performance. This phase produces a performance audit, optimization plan, and monitoring setup grounded in Apple's performance tools and metrics.

## Hard Rules

These are non-negotiable.

1. **NEVER recommend an optimization without reading the relevant reference doc first.** Open the file. Read it. Then cite it.
2. **ALWAYS quote Apple's documentation** when justifying a recommendation.
3. **ALWAYS work through Apple's 8 key metrics systematically.** Do not skip metrics - assess each one.
4. **EVERY optimization MUST have a measurable target.** No "improve performance" - state the metric and target value.
5. **ALWAYS evaluate tradeoffs.** Optimizing one metric can worsen another. State the tradeoff.
6. **ALWAYS include an XCTest performance test** for every critical metric.
7. **NEVER use soft language.** No "consider," "you might." State what the optimization DOES.
8. **ALWAYS prioritize by user impact.** Fix what users feel first.

## Output Structure

The optimize command produces these files:

```text
engineering/
  performance.md       # Performance audit + optimization plan
  monitoring.md        # MetricKit setup + XCTest performance tests
```

## Setup

1. Read `.codex/app-development.local.md` for project context
2. Read `engineering/requirements.md` if it exists - understand data patterns
3. Read `engineering/persistence.md` if it exists - understand storage approach
4. Read existing `engineering/performance.md` and `engineering/monitoring.md` if they exist
5. Read `SKILL.md` for the reference structure
6. Read design screen specs if they exist:
   - Read all `design/screens/*.md` → identify screens with High density, complex state patterns, or heavy content (images, lists, animations)

If `.codex/app-development.local.md` does not exist and `.claude/app-development.local.md` exists, read and migrate it to `.codex/app-development.local.md`.

If any data model files are missing, note it but proceed — performance optimization can happen before or after data modeling.

## Step 0: Understand the App's Performance Profile

### When design screens exist

If `design/screens/*.md` were found in Setup, pre-populate the performance profile:

"From your design, these screens likely have performance implications:"
- List screens with High density → "data-heavy list, consider prefetch and pagination"
- List screens with complex state or animations → "motion/transitions, monitor frame rate"
- List screens with heavy content (images, media) → "media loading, consider lazy loading and caching"

Then ask for confirmation rather than open-ended questions:
1. **Confirm heaviest work** - "Based on your screens, the heaviest work looks like [inferred]. Is that right, or is there something else?"
2. **What's slow or problematic?** - "What performance issues have you noticed? Slow launches? UI freezes? Battery drain? High memory usage? Or are you optimizing proactively?"
3. **What's the scale?** - "How much data does the app work with? How many concurrent operations? How many network requests per session?"
4. **What's the target?** - "Which devices are you targeting? iPhone SE (low-end) through iPhone 16 Pro? iPad?"

### When no design screens exist

Ask these questions using ask the user directly, skipping any already answered:

1. **What does the app do?** - "Describe the app's main activities. What's the heaviest work it does? (e.g., image processing, network calls, data crunching, animations)"
2. **What's slow or problematic?** - "What performance issues have you noticed? Slow launches? UI freezes? Battery drain? High memory usage? Or are you optimizing proactively?"
3. **What's the scale?** - "How much data does the app work with? How many concurrent operations? How many network requests per session?"
4. **What's the target?** - "Which devices are you targeting? iPhone SE (low-end) through iPhone 16 Pro? iPad?"

## Step 1: Audit the 8 Key Metrics

Read `indexes/performance-by-metric.md`.

For EACH of Apple's 8 key performance metrics, read the relevant reference doc from `references/performance/` and assess the app:

### The 8 Metrics

1. **Battery Usage** - CPU, networking, location subsystems
2. **Launch Time** - Time from icon tap to first frame render
3. **Hang Rate** - App unresponsive for 250+ ms
4. **Memory** - Peak and sustained memory usage
5. **Disk Writes** - NAND wear from write operations
6. **Scrolling** - Frame drops during scroll / animation
7. **Terminations** - System-forced app exits
8. **MXSignposts** - Custom telemetry for app-specific operations

**In the conversation**, present each metric assessment:

```text
### [Metric Name]
**Source**: `[reference-file].md`
**Apple says**: "[Direct quote - key threshold or recommendation]"
**Risk for this app**: [High / Medium / Low / N/A]
**Why**: [Specific reasoning based on the app's characteristics]
**Current tools**: [Which Instruments template / Xcode tool to profile this]
**Optimization opportunities**:
- [Opportunity 1 - specific, actionable]
- [Opportunity 2]
**Measurable target**: [e.g., "Launch time < 400ms on iPhone SE", "Zero hangs > 500ms"]
```

After assessing all 8, ask: "These are the metrics I'd prioritize for [App Name]: [top 3-4]. Does this match what you're experiencing?"

## Step 2: Design Optimization Plan

Based on the audit, create a prioritized optimization plan. Read the FULL reference doc for each optimization strategy before recommending it.

Group optimizations by impact:

### Critical (Directly Affects User Experience)
- Hangs, launch time, scrolling - users feel these immediately

### Important (Affects App Health)
- Memory, terminations - users experience crashes and lost state

### Monitoring (Prevents Future Regression)
- Battery, disk writes, MXSignposts - track to catch regressions

**In the conversation**, present each optimization:

```text
### [Optimization Name]
**Metric**: [which of the 8 metrics this improves]
**Source**: `[reference-file].md`
**Apple says**: "[Direct quote]"
**What to do**: [Specific, actionable steps - not vague advice]
**Expected improvement**: [Quantified where possible]
**Tradeoff**: [What gets worse, or "None"]
**How to verify**: [Instruments template, XCTest metric, or manual test]
```

### Save to `engineering/performance.md`

```markdown
# Performance Plan: [App Name]

## Metric Assessment

| Metric | Risk | Target | Current Tool |
|--------|------|--------|-------------|
| Battery Usage | [H/M/L] | [target] | Energy Gauge |
| Launch Time | [H/M/L] | [target] | App Launch template |
| Hang Rate | [H/M/L] | [target] | Time Profiler |
| Memory | [H/M/L] | [target] | Allocations / Leaks |
| Disk Writes | [H/M/L] | [target] | File Activity |
| Scrolling | [H/M/L] | [target] | Core Animation |
| Terminations | [H/M/L] | [target] | Organizer |
| MXSignposts | [H/M/L] | [target] | Custom |

## Optimization Plan

### Priority 1: [Optimization Name]
**Metric**: [metric]
**Action**: [specific steps]
**Target**: [measurable goal]
**Verify**: [how to confirm improvement]

### Priority 2: [Optimization Name]
...

## Instruments Profiling Checklist

For each optimization, profile with the appropriate template:

- [ ] **Time Profile** - CPU usage, identify hot functions
- [ ] **Allocations** - Memory lifecycle, peak usage
- [ ] **Leaks** - Heap memory leaks
- [ ] **File Activity** - Disk write patterns
- [ ] **App Launch** - Launch time breakdown (5-second window)
- [ ] **Core Animation** - Frame rate, GPU usage
- [ ] **System Trace** - Thread scheduling, blocking
- [ ] **Network** - Request timing, payload sizes

## Data Layer Optimizations

[If engineering/persistence.md exists, include data-specific optimizations:]
- **Fetch performance**: [batch sizes, prefetching, predicate optimization]
- **Write batching**: [how writes are batched to reduce disk I/O]
- **Index strategy**: [which properties are indexed and why]
- **Fault handling**: [how object faulting is managed]
```

## Step 3: Define Monitoring Plan

Design the monitoring setup to track metrics in production and catch regressions in CI.

Read the MetricKit references from `references/performance/`.

### Save to `engineering/monitoring.md`

```markdown
# Monitoring Plan: [App Name]

## MetricKit Integration

### Setup
```swift
// AppMetrics.swift
class AppMetrics: MXMetricManagerSubscriber {
    init() {
        MXMetricManager.shared.add(self)
    }

    func didReceive(_ payloads: [MXMetricPayload]) {
        // Process daily metrics
    }

    func didReceive(_ payloads: [MXDiagnosticPayload]) {
        // Process instant diagnostics (hangs, crashes)
    }
}
```

### Tracked Metrics
| Metric | Threshold | Alert Condition |
|--------|-----------|----------------|
| [metric] | [value] | [when to alert] |

### Custom MXSignposts
| Signpost | Category | Measures |
|----------|----------|----------|
| [name] | [category] | [what operation] |

## XCTest Performance Tests

### Launch Time
```swift
func testLaunchPerformance() throws {
    measure(metrics: [XCTApplicationLaunchMetric()]) {
        XCUIApplication().launch()
    }
}
```

### Scroll Performance
```swift
func testScrollPerformance() throws {
    let app = XCUIApplication()
    app.launch()
    let list = app.collectionViews.firstMatch

    let options = XCTMeasureOptions()
    options.invocationOptions = [.manuallyStop]

    measure(metrics: [XCTOSSignpostMetric.scrollDecelerationMetric],
            options: options) {
        list.swipeUp(velocity: .fast)
        stopMeasuring()
        list.swipeDown(velocity: .fast)
    }
}
```

### Disk Writes
```swift
func testDiskWrites() throws {
    let app = XCUIApplication()
    let options = XCTMeasureOptions()
    options.invocationOptions = [.manuallyStart]

    measure(metrics: [XCTStorageMetric(application: app)],
            options: options) {
        app.launch()
        startMeasuring()
        // Trigger the operation that writes data
    }
}
```

### [App-Specific Performance Tests]
[Custom tests for critical operations identified in the audit]

## CI Integration

### Performance Baselines
| Test | Baseline | Max Deviation |
|------|----------|---------------|
| Launch time | [value] | [%] |
| Scroll hitch rate | [value] | [%] |
| [custom] | [value] | [%] |

### Regression Detection
- XCTest performance tests run on every PR
- Baselines stored in `.xcresult` bundles
- Failures block merge if deviation exceeds threshold
```

## Completion

Present a summary:

> "Performance plan complete for [App Name]. Here's what we defined:"

- **Metrics assessed**: All 8 - [top risks highlighted]
- **Optimizations**: [count] prioritized actions
- **Monitoring**: MetricKit + [count] XCTest performance tests
- **CI**: Performance baselines for regression detection

Files created:
- `engineering/performance.md` - Metric assessment and optimization plan
- `engineering/monitoring.md` - MetricKit setup and XCTest performance tests
