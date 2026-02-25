# Distributing binary frameworks as Swift packages

_Article_

> Source: https://developer.apple.com/documentation/xcode/distributing-binary-frameworks-as-swift-packages

Make binaries available to other developers by creating Swift packages that include one or more XCFrameworks.

### Overview

Creating a Swift package to organize and share your code makes source files available to developers who use the Swift package as a package dependency. However, you may need to make your code available as binaries to protect your intellectual property — for example, if you’re developing proprietary, closed-source libraries.

Carefully consider whether you want to distribute your code in binary form because doing so comes with drawbacks. For example, a Swift package that contains a binary is less portable because it can only support platforms that its included binaries support. In addition, binary dependencies are only available for Apple platforms, which limits the audience for your Swift package.

> **Note:** A Swift package can contain a mix of both source files and binaries. This use case is common for packages that contain source code that wraps closed-source binaries.

#### Package binaries as an XCFramework bundle

To distribute code in binary form as a Swift package, create an XCFramework bundle, or *artifact*, that contains the binaries. Then, make the bundle available locally or on a server:

- When you host the binaries on a server, create a ZIP archive with the XCFramework in its root directory and make it available publicly.

- If the XCFramework is available locally and included in the package’s Git repository, you don’t need to create a compressed archive and can reference the XCFramework directly.


To learn more about creating an XCFramework bundle, see [Creating a multiplatform binary framework bundle](https://developer.apple.com/documentation/xcode/creating-a-multi-platform-binary-framework-bundle).

#### Declare a binary target in the package manifest

First, follow the process to create a new Swift package as described in [Creating a standalone Swift package with Xcode](https://developer.apple.com/documentation/xcode/creating-a-standalone-swift-package-with-xcode). Next, declare a *binary target* in your package manifest and make it part of a product, just like a target that contains source files. Ensure that the name of the binary target in the package manifest matches the artifact’s module name.

To declare a remote, or *URL-based*, binary target, use [binaryTarget(name:path:)](https://developer.apple.com/documentation/PackageDescription/Target/binaryTarget(name:path:)). To create the required [checksum](https://developer.apple.com/documentation/PackageDescription/Target/checksum), open the Terminal app, navigate to the root of the package, and run `swift package compute-checksum path/to/MyFramework.zip`. Xcode uses the checksum to verify that the hosted archive file matches the archive you declare in the manifest file. When developers add the package as a binary dependency to their project, and the remote archive’s checksum doesn’t match the checksum in the package manifest, Xcode displays an error.

To declare a local, or *path-based*, binary target, use [package(name:path:)](https://developer.apple.com/documentation/PackageDescription/Package/Dependency/package(name:path:)) and don’t generate a checksum. Instead, include the `.xcframework` bundle in the package’s Git repository.

The following package manifest for the MyLibrary package declares a library product that includes two binary targets: `SomeRemoteBinaryPackage`, a remote, URL-based binary target; and `SomeLocalBinaryPackage`, a local, path-based binary target.

```swift
// swift-tools-version:5.3
import PackageDescription

let package = Package(
    name: "MyLibrary",
    platforms: [
        .macOS(.v10_14), .iOS(.v13), .tvOS(.v13)
    ],
    products: [
        // Products define the executables and libraries a package produces, and make them visible to other packages.
        .library(
            name: "MyLibrary",
            targets: ["MyLibrary", "SomeRemoteBinaryPackage", "SomeLocalBinaryPackage"])
    ],
    dependencies: [
        // Dependencies declare other packages that this package depends on.
    ],
    targets: [
        // Targets are the basic building blocks of a package. A target can define a module or a test suite.
        // Targets can depend on other targets in this package, and on products in packages this package depends on.
        .target(
            name: "MyLibrary"
        ),
        .binaryTarget(
            name: "SomeRemoteBinaryPackage",
            url: "https://url/to/some/remote/xcframework.zip",
            checksum: "The checksum of the ZIP archive that contains the XCFramework."
        ),
        .package(
            name: "SomeLocalBinaryPackage",
            path: "path/to/some.xcframework"
        )
        .testTarget(
            name: "MyLibraryTests",
            dependencies: ["MyLibrary"]),
    ]
)
```
