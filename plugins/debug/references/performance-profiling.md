# Performance Profiling

## V8 Performance Profiler

```javascript
// performance-profiler.js
const v8Profiler = require('v8-profiler-next');
const fs = require('fs');
const path = require('path');

class PerformanceProfiler {
    constructor(options = {}) {
        this.outputDir = options.outputDir || './profiles';
        this.profiles = new Map();

        if (!fs.existsSync(this.outputDir)) {
            fs.mkdirSync(this.outputDir, { recursive: true });
        }
    }

    startCPUProfile(id, options = {}) {
        const title = options.title || `cpu-profile-${id}`;
        v8Profiler.startProfiling(title, true);
        this.profiles.set(id, { type: 'cpu', title, startTime: Date.now() });
        return id;
    }

    stopCPUProfile(id) {
        const profileInfo = this.profiles.get(id);
        if (!profileInfo || profileInfo.type !== 'cpu') {
            throw new Error(`CPU profile ${id} not found`);
        }

        const profile = v8Profiler.stopProfiling(profileInfo.title);
        const duration = Date.now() - profileInfo.startTime;
        const fileName = `${profileInfo.title}-${Date.now()}.cpuprofile`;
        const filePath = path.join(this.outputDir, fileName);

        profile.export((error, result) => {
            if (!error) {
                fs.writeFileSync(filePath, result);
                console.log(`CPU profile saved to ${filePath}`);
            }
            profile.delete();
        });

        this.profiles.delete(id);
        return { id, duration, filePath };
    }

    takeHeapSnapshot(tag = '') {
        const fileName = `heap-${tag}-${Date.now()}.heapsnapshot`;
        const filePath = path.join(this.outputDir, fileName);
        const snapshot = v8Profiler.takeSnapshot();

        snapshot.export((error, result) => {
            if (!error) {
                fs.writeFileSync(filePath, result);
                console.log(`Heap snapshot saved to ${filePath}`);
            }
            snapshot.delete();
        });

        return filePath;
    }

    measureFunction(fn, name = 'anonymous') {
        const measurements = {
            name,
            executions: 0,
            totalTime: 0,
            minTime: Infinity,
            maxTime: 0,
            avgTime: 0,
        };

        return new Proxy(fn, {
            apply(target, thisArg, args) {
                const start = process.hrtime.bigint();
                try {
                    const result = target.apply(thisArg, args);
                    if (result instanceof Promise) {
                        return result.finally(() => recordExecution(start));
                    }
                    recordExecution(start);
                    return result;
                } catch (error) {
                    recordExecution(start);
                    throw error;
                }
            },
            get(target, prop) {
                if (prop === 'measurements') return measurements;
                return target[prop];
            },
        });

        function recordExecution(start) {
            const duration = Number(process.hrtime.bigint() - start) / 1000000;
            measurements.executions++;
            measurements.totalTime += duration;
            measurements.minTime = Math.min(measurements.minTime, duration);
            measurements.maxTime = Math.max(measurements.maxTime, duration);
            measurements.avgTime = measurements.totalTime / measurements.executions;
            if (duration > 100) {
                console.warn(`Slow function: ${name} took ${duration}ms`);
            }
        }
    }
}
```

## Memory Leak Detector

```javascript
class MemoryLeakDetector {
    constructor() {
        this.snapshots = [];
        this.threshold = 50 * 1024 * 1024; // 50MB
    }

    start(interval = 60000) {
        this.interval = setInterval(() => this.checkMemory(), interval);
    }

    checkMemory() {
        const usage = process.memoryUsage();
        const snapshot = {
            timestamp: Date.now(),
            heapUsed: usage.heapUsed,
            external: usage.external,
            rss: usage.rss,
        };

        this.snapshots.push(snapshot);
        if (this.snapshots.length > 10) this.snapshots.shift();

        if (this.snapshots.length >= 5) {
            const trend = this.calculateTrend();
            if (trend.increasing && trend.delta > this.threshold) {
                console.error('Potential memory leak detected!', { trend, current: snapshot });
                const profiler = new PerformanceProfiler();
                profiler.takeHeapSnapshot('leak-detection');
            }
        }
    }

    calculateTrend() {
        const recent = this.snapshots.slice(-5);
        const first = recent[0];
        const last = recent[recent.length - 1];
        const delta = last.heapUsed - first.heapUsed;
        const increasing = recent.every((s, i) =>
            i === 0 || s.heapUsed > recent[i - 1].heapUsed
        );

        return {
            increasing,
            delta,
            rate: delta / (last.timestamp - first.timestamp) * 1000 * 60,
        };
    }
}
```

## Profiling Middleware

```javascript
class DebugMiddlewareFactory {
    static create(app, config) {
        const middlewares = [];

        if (config.isEnabled('tracing')) {
            middlewares.push(new TracingMiddleware().express());
        }

        if (config.isEnabled('profiling')) {
            middlewares.push(this.profilingMiddleware());
        }

        if (config.isEnabled('memoryMonitoring')) {
            new MemoryLeakDetector().start();
        }

        if (process.env.NODE_ENV === 'development') {
            app.get('/debug/heap', (req, res) => {
                const profiler = new PerformanceProfiler();
                res.json({ heapSnapshot: profiler.takeHeapSnapshot('manual') });
            });

            app.get('/debug/profile', async (req, res) => {
                const profiler = new PerformanceProfiler();
                const id = profiler.startCPUProfile('manual');
                setTimeout(() => res.json(profiler.stopCPUProfile(id)), 10000);
            });

            app.get('/debug/metrics', (req, res) => {
                res.json({
                    memory: process.memoryUsage(),
                    cpu: process.cpuUsage(),
                    uptime: process.uptime(),
                });
            });
        }

        return middlewares;
    }

    static profilingMiddleware() {
        const profiler = new PerformanceProfiler();
        return (req, res, next) => {
            if (Math.random() < 0.01) {
                const id = profiler.startCPUProfile(`request-${Date.now()}`);
                res.on('finish', () => profiler.stopCPUProfile(id));
            }
            next();
        };
    }
}
```
