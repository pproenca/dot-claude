# MXSignpostMetric

_Class_

> Source: https://developer.apple.com/documentation/metrickit/mxsignpostmetric

An object representing a custom metric.

```swift
class MXSignpostMetric
```

### Overview

A custom metric is an event type with a developer-defined name and category. You can add custom metrics to daily reports to capture information specific to your app.

Custom metrics are a type of signpost saved to custom OS logs created using [makeLogHandle(category:)](https://developer.apple.com/documentation/metrickit/mxmetricmanager/makeloghandle(category:)). The daily report contains information about the number and duration of custom events, as well as the power and performance impact of those events. Only custom metric events logged using MetricKit utility functions capture additional power and performance data.

> **Note:**  The system limits the number of custom signpost metrics saved to the log in order to reduce on-device memory overhead. Limit use of custom metrics to critical sections of code.
