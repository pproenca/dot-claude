# MXMetricManager

_Class_

> Source: https://developer.apple.com/documentation/metrickit/mxmetricmanager

The shared object that registers you to receive metrics, creates logs for custom metrics, and gives access to past reports.

```swift
class MXMetricManager
```

### Overview

The `MXMetricManager` shared object manages your subscription for receiving on-device daily metrics.

MetricKit starts accumulating reports for your app after calling [shared](https://developer.apple.com/documentation/metrickit/mxmetricmanager/shared) for the first time. To receive the reports, call [add(_:)](https://developer.apple.com/documentation/metrickit/mxmetricmanager/add(_:)) with an object that adopts the [MXMetricManagerSubscriber](https://developer.apple.com/documentation/metrickit/mxmetricmanagersubscriber) protocol. The system then delivers metric reports at most once per day, and diagnostic reports immediately in iOS 15 and later and macOS 12 and later. The reports contain the metrics from the past 24 hours and any previously undelivered daily reports. To pause receiving reports, call [remove(_:)](https://developer.apple.com/documentation/metrickit/mxmetricmanager/remove(_:)).

The calls to add a subscriber and for receiving reports are safe to use in performance-sensitive code, such as app launch.

The snippet below shows a simple class for using MetricKit.

```swift
class AppMetrics: NSObject, MXMetricManagerSubscriber {
    func receiveReports() {
       let shared = MXMetricManager.shared
       shared.add(self)
    }

    func pauseReports() {
       let shared = MXMetricManager.shared
       shared.remove(self)
    }

    // Receive daily metrics.
    func didReceive(_ payloads: [MXMetricPayload]) {
       // Process metrics.
    }

    // Receive diagnostics immediately when available.
    func didReceive(_ payloads: [MXDiagnosticPayload]) {
       // Process diagnostics.
    }
}

```

> **Note:**  MetricKit delivers daily metric reports from iOS 13 or later, and macOS 26 or later.
