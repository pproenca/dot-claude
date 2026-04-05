# MetricKit

_Framework_

> Source: https://developer.apple.com/documentation/metrickit

Aggregate and analyze per-device reports on exception and crash diagnostics and on power and performance metrics.

### Overview

With MetricKit, you can receive on-device app diagnostics and power and performance metrics the system captures. The system delivers metric reports about the previous 24 hours to a registered app at most once per day, and delivers diagnostic reports immediately in iOS 15 and later and macOS 12 and later. This framework supports diagnostics for crashes, hangs, energy, and disk writes for apps running in visionOS but doesn’t report metrics for apps running in visionOS. This includes apps built for visionOS or compatible iPhone and iPad apps running in visionOS.

Use the data in the reports to help improve the performance of your iOS app, macOS app, or Mac app built with Mac Catalyst. The framework includes the following:

- A manager class and a subscriber protocol

- Payload classes for reported data

- Classes for each category of metrics and diagnostics

- Classes for measurement units, such as bars of cellular connectivity

- Classes for representing accumulated data, such as histograms

- A class for capturing stack traces in diagnostics

