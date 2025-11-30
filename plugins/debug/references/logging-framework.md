# Debug Logging Framework

## Advanced Logger with Winston

```javascript
// debug-logger.js
const winston = require('winston');
const { ElasticsearchTransport } = require('winston-elasticsearch');

class DebugLogger {
    constructor(options = {}) {
        this.service = options.service || 'app';
        this.level = process.env.LOG_LEVEL || 'debug';
        this.logger = this.createLogger();
    }

    createLogger() {
        const formats = [
            winston.format.timestamp(),
            winston.format.errors({ stack: true }),
            winston.format.splat(),
            winston.format.json(),
        ];

        if (process.env.NODE_ENV === 'development') {
            formats.push(winston.format.colorize());
            formats.push(winston.format.printf(this.devFormat));
        }

        const transports = [
            new winston.transports.Console({
                level: this.level,
                handleExceptions: true,
                handleRejections: true,
            }),
        ];

        if (process.env.DEBUG_LOG_FILE) {
            transports.push(
                new winston.transports.File({
                    filename: process.env.DEBUG_LOG_FILE,
                    level: 'debug',
                    maxsize: 10485760,
                    maxFiles: 5,
                })
            );
        }

        if (process.env.ELASTICSEARCH_URL) {
            transports.push(
                new ElasticsearchTransport({
                    level: 'info',
                    clientOpts: { node: process.env.ELASTICSEARCH_URL },
                    index: `logs-${this.service}`,
                })
            );
        }

        return winston.createLogger({
            level: this.level,
            format: winston.format.combine(...formats),
            defaultMeta: {
                service: this.service,
                environment: process.env.NODE_ENV,
                hostname: require('os').hostname(),
                pid: process.pid,
            },
            transports,
        });
    }

    devFormat(info) {
        const { timestamp, level, message, ...meta } = info;
        const metaString = Object.keys(meta).length ?
            '\n' + JSON.stringify(meta, null, 2) : '';
        return `${timestamp} [${level}]: ${message}${metaString}`;
    }

    trace(message, meta = {}) {
        const stack = new Error().stack;
        this.logger.debug(message, { ...meta, trace: stack, timestamp: Date.now() });
    }

    timing(label, fn) {
        const start = process.hrtime.bigint();
        const result = fn();
        const end = process.hrtime.bigint();
        const duration = Number(end - start) / 1000000;
        this.logger.debug(`Timing: ${label}`, { duration, unit: 'ms' });
        return result;
    }

    memory() {
        const usage = process.memoryUsage();
        this.logger.debug('Memory usage', {
            rss: `${Math.round(usage.rss / 1024 / 1024)}MB`,
            heapTotal: `${Math.round(usage.heapTotal / 1024 / 1024)}MB`,
            heapUsed: `${Math.round(usage.heapUsed / 1024 / 1024)}MB`,
            external: `${Math.round(usage.external / 1024 / 1024)}MB`,
        });
    }
}
```

## Debug Context Manager

```javascript
class DebugContext {
    constructor() {
        this.contexts = new Map();
    }

    create(id, metadata = {}) {
        const context = {
            id,
            startTime: Date.now(),
            metadata,
            logs: [],
            spans: [],
        };
        this.contexts.set(id, context);
        return context;
    }

    log(contextId, level, message, data = {}) {
        const context = this.contexts.get(contextId);
        if (context) {
            context.logs.push({ timestamp: Date.now(), level, message, data });
        }
    }

    export(contextId) {
        const context = this.contexts.get(contextId);
        if (!context) return null;
        return {
            ...context,
            duration: Date.now() - context.startTime,
            logCount: context.logs.length,
        };
    }
}
```

## Debug Configuration

```javascript
class DebugConfiguration {
    constructor() {
        this.config = {
            levels: { error: 0, warn: 1, info: 2, debug: 3, trace: 4 },
            features: {
                remoteDebugging: process.env.ENABLE_REMOTE_DEBUG === 'true',
                tracing: process.env.ENABLE_TRACING === 'true',
                profiling: process.env.ENABLE_PROFILING === 'true',
                memoryMonitoring: process.env.ENABLE_MEMORY_MONITORING === 'true',
            },
            endpoints: {
                jaeger: process.env.JAEGER_ENDPOINT || 'http://localhost:14268',
                elasticsearch: process.env.ELASTICSEARCH_URL || 'http://localhost:9200',
                sentry: process.env.SENTRY_DSN,
            },
            sampling: {
                traces: parseFloat(process.env.TRACE_SAMPLING_RATE || '0.1'),
                profiles: parseFloat(process.env.PROFILE_SAMPLING_RATE || '0.01'),
                logs: parseFloat(process.env.LOG_SAMPLING_RATE || '1.0'),
            },
        };
    }

    isEnabled(feature) { return this.config.features[feature] || false; }
    getLevel() { return this.config.levels[process.env.DEBUG_LEVEL || 'info'] || 2; }
    shouldSample(type) { return Math.random() < (this.config.sampling[type] || 1.0); }
}
```
