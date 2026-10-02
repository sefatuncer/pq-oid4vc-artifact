// swift-tools-version:5.9
// Adapter for JOSE-102 jwt-kit 5.3.0 — Package.resolved = experiment/environments/hedefler/JOSE-102/cikti (git revisions pinned)
import PackageDescription
let package = Package(
  name: "Adaptor",
  platforms: [.macOS(.v13)],
  dependencies: [ .package(url: "https://github.com/vapor/jwt-kit.git", exact: "5.3.0") ],
  targets: [ .executableTarget(name: "Adaptor", dependencies: [ .product(name: "JWTKit", package: "jwt-kit") ]) ]
)
