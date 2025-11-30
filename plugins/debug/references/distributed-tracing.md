# Distributed Tracing

## OpenTelemetry Setup

```javascript
// tracing.js
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');
const { JaegerExporter } = require('@opentelemetry/exporter-jaeger');
const { BatchSpanProcessor } = require('@opentelemetry/sdk-trace-base');

class TracingSystem {
    constructor(serviceName) {
        this.serviceName = serviceName;
        this.sdk = null;
    }

    initialize() {
        const jaegerExporter = new JaegerExporter({
            endpoint: process.env.JAEGER_ENDPOINT || 'http://localhost:14268/api/traces',
        });

        const resource = Resource.default().merge(
            new Resource({
                [SemanticResourceAttributes.SERVICE_NAME]: this.serviceName,
                [SemanticResourceAttributes.SERVICE_VERSION]: process.env.SERVICE_VERSION || '1.0.0',
                [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV || 'development',
            })
        );

        this.sdk = new NodeSDK({
            resource,
            spanProcessor: new BatchSpanProcessor(jaegerExporter),
            instrumentations: [
                getNodeAutoInstrumentations({
                    '@opentelemetry/instrumentation-fs': { enabled: false },
                    '@opentelemetry/instrumentation-http': {
                        requestHook: (span, request) => {
                            span.setAttribute('http.request.body', JSON.stringify(request.body));
                        },
                    },
                    '@opentelemetry/instrumentation-express': {
                        requestHook: (span, req) => {
                            span.setAttribute('user.id', req.user?.id);
                            span.setAttribute('session.id', req.session?.id);
                        },
                    },
                }),
            ],
        });

        this.sdk.start();

        process.on('SIGTERM', () => {
            this.sdk.shutdown()
                .then(() => console.log('Tracing terminated'))
                .catch((error) => console.error('Error terminating tracing', error))
                .finally(() => process.exit(0));
        });
    }

    createSpan(name, fn, attributes = {}) {
        const tracer = trace.getTracer(this.serviceName);
        return tracer.startActiveSpan(name, async (span) => {
            try {
                Object.entries(attributes).forEach(([key, value]) => {
                    span.setAttribute(key, value);
                });
                const result = await fn(span);
                span.setStatus({ code: SpanStatusCode.OK });
                return result;
            } catch (error) {
                span.recordException(error);
                span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
                throw error;
            } finally {
                span.end();
            }
        });
    }
}
```

## Tracing Middleware

```javascript
class TracingMiddleware {
    constructor() {
        this.tracer = trace.getTracer('http-middleware');
    }

    express() {
        return (req, res, next) => {
            const span = this.tracer.startSpan(`${req.method} ${req.path}`, {
                kind: SpanKind.SERVER,
                attributes: {
                    'http.method': req.method,
                    'http.url': req.url,
                    'http.target': req.path,
                    'http.host': req.hostname,
                    'http.scheme': req.protocol,
                    'http.user_agent': req.get('user-agent'),
                },
            });

            req.span = span;
            req.traceId = span.spanContext().traceId;
            res.setHeader('X-Trace-Id', req.traceId);

            const originalEnd = res.end;
            res.end = function(...args) {
                span.setAttribute('http.status_code', res.statusCode);
                if (res.statusCode >= 400) {
                    span.setStatus({ code: SpanStatusCode.ERROR, message: `HTTP ${res.statusCode}` });
                }
                span.end();
                originalEnd.apply(res, args);
            };

            next();
        };
    }
}
```

## Source Map Configuration

```javascript
// webpack.config.js
module.exports = {
    mode: 'production',
    devtool: 'hidden-source-map',

    output: {
        filename: '[name].[contenthash].js',
        sourceMapFilename: 'sourcemaps/[name].[contenthash].js.map',
    },

    plugins: [
        new SentryWebpackPlugin({
            authToken: process.env.SENTRY_AUTH_TOKEN,
            org: 'your-org',
            project: 'your-project',
            include: './dist',
            ignore: ['node_modules'],
            urlPrefix: '~/',
            release: process.env.RELEASE_VERSION,
            deleteAfterCompile: true,
        }),
    ],
};

// Runtime source map support
require('source-map-support').install({
    environment: 'node',
    handleUncaughtExceptions: false,
});
```
