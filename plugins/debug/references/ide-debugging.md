# IDE Debugging Configuration

## VS Code Debug Configuration

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Node.js App",
            "type": "node",
            "request": "launch",
            "runtimeExecutable": "node",
            "runtimeArgs": ["--inspect-brk", "--enable-source-maps"],
            "program": "${workspaceFolder}/src/index.js",
            "env": {
                "NODE_ENV": "development",
                "DEBUG": "*",
                "NODE_OPTIONS": "--max-old-space-size=4096"
            },
            "sourceMaps": true,
            "resolveSourceMapLocations": [
                "${workspaceFolder}/**",
                "!**/node_modules/**"
            ],
            "skipFiles": [
                "<node_internals>/**",
                "node_modules/**"
            ],
            "console": "integratedTerminal",
            "outputCapture": "std"
        },
        {
            "name": "Debug TypeScript",
            "type": "node",
            "request": "launch",
            "program": "${workspaceFolder}/src/index.ts",
            "preLaunchTask": "tsc: build - tsconfig.json",
            "outFiles": ["${workspaceFolder}/dist/**/*.js"],
            "sourceMaps": true,
            "smartStep": true,
            "internalConsoleOptions": "openOnSessionStart"
        },
        {
            "name": "Debug Jest Tests",
            "type": "node",
            "request": "launch",
            "program": "${workspaceFolder}/node_modules/.bin/jest",
            "args": [
                "--runInBand",
                "--no-cache",
                "--watchAll=false",
                "--detectOpenHandles"
            ],
            "console": "integratedTerminal",
            "internalConsoleOptions": "neverOpen",
            "env": {
                "NODE_ENV": "test"
            }
        },
        {
            "name": "Attach to Process",
            "type": "node",
            "request": "attach",
            "processId": "${command:PickProcess}",
            "protocol": "inspector",
            "restart": true,
            "sourceMaps": true
        }
    ],
    "compounds": [
        {
            "name": "Full Stack Debug",
            "configurations": ["Debug Backend", "Debug Frontend"],
            "stopAll": true
        }
    ]
}
```

## Chrome DevTools Integration

```javascript
// debug-helpers.js
class DebugHelper {
    constructor() {
        this.setupDevTools();
        this.setupConsoleHelpers();
    }

    setupDevTools() {
        if (typeof window !== 'undefined') {
            window.DEBUG = window.DEBUG || {};
            window.DEBUG.store = () => window.__REDUX_STORE__;
            window.DEBUG.router = () => window.__ROUTER__;
            window.DEBUG.components = new Map();

            window.DEBUG.measureRender = (componentName) => {
                performance.mark(`${componentName}-start`);
                return () => {
                    performance.mark(`${componentName}-end`);
                    performance.measure(
                        componentName,
                        `${componentName}-start`,
                        `${componentName}-end`
                    );
                };
            };

            window.DEBUG.heapSnapshot = async () => {
                if ('memory' in performance) {
                    const snapshot = await performance.measureUserAgentSpecificMemory();
                    console.table(snapshot);
                    return snapshot;
                }
            };
        }
    }

    setupConsoleHelpers() {
        const styles = {
            error: 'color: #ff0000; font-weight: bold;',
            warn: 'color: #ff9800; font-weight: bold;',
            info: 'color: #2196f3; font-weight: bold;',
            debug: 'color: #4caf50; font-weight: bold;',
        };

        Object.entries(styles).forEach(([level, style]) => {
            const original = console[level];
            console[level] = function(...args) {
                if (process.env.NODE_ENV === 'development') {
                    const timestamp = new Date().toISOString();
                    original.call(console, `%c[${timestamp}] ${level.toUpperCase()}:`, style, ...args);
                }
            };
        });
    }
}
```

## VS Code Extensions

```json
// .vscode/extensions.json
{
    "recommendations": [
        "ms-vscode.vscode-js-debug",
        "msjsdiag.debugger-for-chrome",
        "ms-vscode.vscode-typescript-tslint-plugin",
        "dbaeumer.vscode-eslint",
        "ms-azuretools.vscode-docker",
        "humao.rest-client",
        "eamodio.gitlens",
        "usernamehw.errorlens",
        "wayou.vscode-todo-highlight",
        "formulahendry.code-runner"
    ]
}
```

## VS Code Tasks

```json
// .vscode/tasks.json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Start Debug Server",
            "type": "npm",
            "script": "debug",
            "problemMatcher": [],
            "presentation": {
                "reveal": "always",
                "panel": "dedicated"
            }
        },
        {
            "label": "Profile Application",
            "type": "shell",
            "command": "node --inspect-brk --cpu-prof --cpu-prof-dir=./profiles ${workspaceFolder}/src/index.js",
            "problemMatcher": []
        },
        {
            "label": "Memory Snapshot",
            "type": "shell",
            "command": "node --inspect --expose-gc ${workspaceFolder}/scripts/heap-snapshot.js",
            "problemMatcher": []
        }
    ]
}
```

## Remote Debugging

```javascript
// remote-debug-server.js
const inspector = require('inspector');
const WebSocket = require('ws');

class RemoteDebugServer {
    constructor(options = {}) {
        this.port = options.port || 9229;
        this.host = options.host || '0.0.0.0';
        this.wsPort = options.wsPort || 9230;
        this.sessions = new Map();
    }

    start() {
        inspector.open(this.port, this.host, true);
        this.wss = new WebSocket.Server({ port: this.wsPort });

        this.wss.on('connection', (ws) => {
            const sessionId = this.generateSessionId();
            this.sessions.set(sessionId, ws);

            ws.on('message', (message) => {
                this.handleDebugCommand(sessionId, message);
            });

            ws.send(JSON.stringify({
                type: 'session',
                sessionId,
                debugUrl: `chrome-devtools://devtools/bundled/inspector.html?ws=${this.host}:${this.port}`
            }));
        });

        console.log(`Remote debug server listening on ws://${this.host}:${this.wsPort}`);
    }
}
```

## Docker Debug Setup

```dockerfile
FROM node:18
RUN apt-get update && apt-get install -y \
    chromium \
    gdb \
    strace \
    tcpdump

EXPOSE 9229 9230
ENV NODE_OPTIONS="--inspect=0.0.0.0:9229"
CMD ["node", "--inspect-brk=0.0.0.0:9229", "index.js"]
```
