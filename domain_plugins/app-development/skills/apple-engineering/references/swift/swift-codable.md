# Codable

_Type Alias_

> Source: https://developer.apple.com/documentation/swift/codable

A type that can convert itself into and out of an external representation.

```swift
typealias Codable = Decodable & Encodable
```

### Discussion

`Codable` is a type alias for the `Encodable` and `Decodable` protocols. When you use `Codable` as a type or a generic constraint, it matches any type that conforms to both protocols.
