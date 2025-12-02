# Production Debugging

## Production Debug Tools

```javascript
// production-debug.js
class ProductionDebugger {
    constructor(options = {}) {
        this.enabled = process.env.PRODUCTION_DEBUG === 'true';
        this.authToken = process.env.DEBUG_AUTH_TOKEN;
        this.allowedIPs = (process.env.DEBUG_ALLOWED_IPS || '').split(',');
    }

    middleware() {
        return (req, res, next) => {
            if (!this.enabled) return next();

            const token = req.headers['x-debug-token'];
            const ip = req.ip || req.connection.remoteAddress;

            if (token !== this.authToken || !this.allowedIPs.includes(ip)) {
                return next();
            }

            res.setHeader('X-Debug-Enabled', 'true');
            req.debugMode = true;
            req.debugContext = new DebugContext().create(req.id);

            const originalConsole = { ...console };
            ['log', 'debug', 'info', 'warn', 'error'].forEach(method => {
                console[method] = (...args) => {
                    req.debugContext.log(req.id, method, args[0], args.slice(1));
                    originalConsole[method](...args);
                };
            });

            res.on('finish', () => {
                Object.assign(console, originalConsole);
                if (req.headers['x-debug-response'] === 'true') {
                    const debugInfo = req.debugContext.export(req.id);
                    res.setHeader('X-Debug-Info', JSON.stringify(debugInfo));
                }
            });

            next();
        };
    }
}
```

## Conditional Breakpoints

```javascript
class ConditionalBreakpoint {
    constructor(condition, callback) {
        this.condition = condition;
        this.callback = callback;
        this.hits = 0;
    }

    check(context) {
        if (this.condition(context)) {
            this.hits++;
            console.debug('Conditional breakpoint hit', {
                condition: this.condition.toString(),
                hits: this.hits,
                context,
            });

            if (this.callback) this.callback(context);

            if (process.env.NODE_ENV === 'production') {
                new PerformanceProfiler().takeHeapSnapshot(`breakpoint-${Date.now()}`);
            } else {
                debugger;
            }
        }
    }
}

// Example usage
const breakpoints = new Map();

breakpoints.set('high-memory', new ConditionalBreakpoint(
    (context) => context.memoryUsage > 500 * 1024 * 1024,
    (context) => {
        console.error('High memory usage detected', context);
        alerting.send('high-memory', context);
    }
));

function checkBreakpoints(context) {
    breakpoints.forEach(breakpoint => breakpoint.check(context));
}
```

## Debug Dashboard

```html
<!-- debug-dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Debug Dashboard</title>
    <style>
        body { font-family: monospace; background: #1e1e1e; color: #d4d4d4; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .metric { background: #252526; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .metric h3 { margin: 0 0 10px 0; color: #569cd6; }
        .log-entry { padding: 5px; border-bottom: 1px solid #3e3e3e; }
        .error { color: #f44747; }
        .warn { color: #ff9800; }
        .info { color: #4fc3f7; }
        .debug { color: #4caf50; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Debug Dashboard</h1>

        <div class="metric">
            <h3>System Metrics</h3>
            <div id="metrics"></div>
        </div>

        <div class="metric">
            <h3>Memory Usage</h3>
            <canvas id="memoryChart"></canvas>
        </div>

        <div class="metric">
            <h3>Request Traces</h3>
            <div id="traces"></div>
        </div>

        <div class="metric">
            <h3>Debug Logs</h3>
            <div id="logs"></div>
        </div>
    </div>

    <script>
        const ws = new WebSocket('ws://localhost:9231/debug');

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            switch (data.type) {
                case 'metrics': updateMetrics(data.payload); break;
                case 'trace': addTrace(data.payload); break;
                case 'log': addLog(data.payload); break;
            }
        };

        function updateMetrics(metrics) {
            document.getElementById('metrics').innerHTML = `
                <div>CPU: ${metrics.cpu.percent}%</div>
                <div>Memory: ${metrics.memory.used}MB / ${metrics.memory.total}MB</div>
                <div>Uptime: ${metrics.uptime}s</div>
            `;
        }

        function addLog(log) {
            const container = document.getElementById('logs');
            const entry = document.createElement('div');
            entry.className = `log-entry ${log.level}`;
            entry.innerHTML = `<span>${log.timestamp}</span> [${log.level.toUpperCase()}] ${log.message}`;
            container.insertBefore(entry, container.firstChild);
            while (container.children.length > 100) container.removeChild(container.lastChild);
        }
    </script>
</body>
</html>
```
