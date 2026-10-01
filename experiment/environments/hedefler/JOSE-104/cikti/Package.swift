// swift-tools-version:5.9
import PackageDescription
let package = Package(
  name: "Deneme",
  dependencies: [ .package(url: "https://github.com/Kitura/Swift-JWT.git", revision: "29fe084d874045d22546612d85fae1e9408c9091") ],
  targets: [ .executableTarget(name: "Deneme", dependencies: [ .product(name: "SwiftJWT", package: "swift-jwt") ]) ]
)
