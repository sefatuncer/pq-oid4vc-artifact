#!/usr/bin/env bash
# JOSE-104 — installation/build pre-test (Step 9 task 4a). No release: frame son_commit_sha. NO signature verification.
export DEPO=https://github.com/Kitura/Swift-JWT.git REVIZYON=29fe084d874045d22546612d85fae1e9408c9091 URUN=SwiftJWT PAKET_KIMLIK=swift-jwt
exec bash /b/swiftpm.sh
