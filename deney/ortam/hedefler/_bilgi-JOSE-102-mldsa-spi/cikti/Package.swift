// swift-tools-version:5.9
import PackageDescription
let package = Package(
  name: "Deneme",
  dependencies: [ .package(url: "https://github.com/vapor/jwt-kit.git", exact: "5.3.0") ],
  targets: [ .executableTarget(name: "Deneme", dependencies: [ .product(name: "JWTKit", package: "jwt-kit") ]) ]
)
