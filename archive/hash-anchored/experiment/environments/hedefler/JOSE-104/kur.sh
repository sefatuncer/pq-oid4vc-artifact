#!/usr/bin/env bash
# JOSE-104 — kurulum/derleme ön testi (Adım 9 görev 4a). Sürüm yok: CERCEVE son_commit_sha. İmza doğrulama YOK.
export DEPO=https://github.com/Kitura/Swift-JWT.git REVIZYON=29fe084d874045d22546612d85fae1e9408c9091 URUN=SwiftJWT PAKET_KIMLIK=swift-jwt
exec bash /b/swiftpm.sh
