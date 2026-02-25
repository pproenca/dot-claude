# Performance by Metric

> Base path: `references/performance/`

Map performance concerns to Apple's 8 key metrics, tools, and optimization strategies. When analyzing performance, identify the relevant metric below, then read the full reference doc from the base path above.

## Apple's 8 Key Performance Metrics

| # | Metric | Threshold | Primary Tool | Reference |
|---|--------|-----------|-------------|-----------|
| 1 | Battery Usage | Varies by subsystem | Energy Gauge (Xcode) | xcode-analyzing-the-performance-of-your-shipping-app.md |
| 2 | Launch Time | < 400ms warm, < 2s cold | App Launch template | xcode-reducing-your-app-s-launch-time.md |
| 3 | Hang Rate | 0 hangs > 250ms | Time Profiler | xcode-improving-app-responsiveness.md |
| 4 | Memory | Under system limit | Allocations / Leaks | xcode-gathering-information-about-memory-use.md |
| 5 | Disk Writes | < 1GB / 24hrs | File Activity template | xcode-reducing-disk-writes.md |
| 6 | Scrolling | 0 hitches, 60/120 fps | Core Animation template | xcode-analyzing-responsiveness-issues-in-your-shipping-app.md |
| 7 | Terminations | 0 system-forced exits | Xcode Organizer | xcode-analyzing-the-performance-of-your-shipping-app.md |
| 8 | MXSignposts | App-defined targets | Custom signposts | metrickit-mxsignpostmetric.md |

## By Concern

### App feels slow to open

| Concern | Metric | Reference |
|---------|--------|-----------|
| Cold launch takes too long | Launch Time | xcode-reducing-your-app-s-launch-time.md |
| Warm launch slow | Launch Time | xcode-reducing-your-app-s-launch-time.md |
| First frame delayed | Launch Time | xcode-reducing-your-app-s-launch-time.md |

### App freezes or stutters

| Concern | Metric | Reference |
|---------|--------|-----------|
| UI unresponsive during interaction | Hang Rate | xcode-improving-app-responsiveness.md |
| Scrolling stutters / drops frames | Scrolling | xcode-analyzing-responsiveness-issues-in-your-shipping-app.md |
| Animation hitches | Scrolling | xcode-analyzing-responsiveness-issues-in-your-shipping-app.md |
| Main thread blocked | Hang Rate | xcode-improving-app-responsiveness.md |

### App crashes or gets killed

| Concern | Metric | Reference |
|---------|--------|-----------|
| System kills app in background | Terminations | xcode-analyzing-the-performance-of-your-shipping-app.md |
| Out of memory crash | Memory | xcode-gathering-information-about-memory-use.md |
| Watchdog timeout on launch | Launch Time | xcode-reducing-your-app-s-launch-time.md |

### App drains battery

| Concern | Metric | Reference |
|---------|--------|-----------|
| High CPU usage | Battery | xcode-analyzing-the-performance-of-your-shipping-app.md |
| Excessive network requests | Battery | xcode-analyzing-the-performance-of-your-shipping-app.md |
| Continuous location tracking | Battery | xcode-analyzing-the-performance-of-your-shipping-app.md |
| Excessive disk writes | Disk Writes | xcode-reducing-disk-writes.md |

### Memory issues

| Concern | Metric | Reference |
|---------|--------|-----------|
| Memory grows over time (leak) | Memory | xcode-gathering-information-about-memory-use.md |
| High peak memory | Memory | xcode-gathering-information-about-memory-use.md |
| Retain cycles | Memory | xcode-diagnosing-memory-thread-and-crash-issues-early.md |
| Thread safety / data races | Memory | xcode-diagnosing-memory-thread-and-crash-issues-early.md |

## MetricKit — Production Monitoring

| API | Purpose | Reference |
|-----|---------|-----------|
| MetricKit framework | On-device performance telemetry | metrickit.md |
| MXMetricManager | Subscribe to metric and diagnostic payloads | metrickit-mxmetricmanager.md |
| MXMetricPayload | Daily aggregate metrics (launch time, memory, etc.) | metrickit-mxmetricpayload.md |
| MXDiagnosticPayload | Instant diagnostics (hangs, crashes — iOS 15+) | metrickit-mxdiagnosticpayload.md |
| MXSignpostMetric | Custom telemetry for app-specific operations | metrickit-mxsignpostmetric.md |

## Instruments Templates Cheat Sheet

| Template | Measures | When to Use |
|----------|----------|-------------|
| Time Profiler | CPU usage, hot call stacks | Hangs, high CPU, slow operations |
| Allocations | Object lifecycle, peak memory | Memory growth, high usage |
| Leaks | Heap memory leaks | Suspected retain cycles |
| VM Tracker | Virtual memory over time | Memory pressure analysis |
| File Activity | File system access patterns | Excessive disk writes |
| App Launch | Launch time breakdown (5s window) | Slow app startup |
| Core Animation | Frame rate, GPU usage | Scroll hitches, animation jank |
| System Trace | Thread scheduling, blocking | Deadlocks, priority inversion |
| Network | Request timing, payload sizes | Slow network, excess requests |
| Energy Log | CPU/network/location energy | Battery drain analysis |

## XCTest Performance Metrics

| Metric Class | Measures | Reference |
|-------------|----------|-----------|
| XCTApplicationLaunchMetric | App launch time | xctest-performance_tests.md (in testing/) |
| XCTOSSignpostMetric.scrollDecelerationMetric | Scroll performance | xctest-performance_tests.md (in testing/) |
| XCTStorageMetric | Disk write volume | xctest-performance_tests.md (in testing/) |
| XCTMemoryMetric | Peak physical memory | xctest-performance_tests.md (in testing/) |
| XCTCPUMetric | CPU time and instructions | xctest-performance_tests.md (in testing/) |
| XCTClockMetric | Wall clock time | xctest-performance_tests.md (in testing/) |
