#!/usr/bin/env bash
# JOSE-102 — installation/build pre-test (Step 9 task 4a). NO signature verification.
export DEPO=https://github.com/vapor/jwt-kit.git SURUM=5.3.0 URUN=JWTKit PAKET_KIMLIK=jwt-kit
exec bash /b/swiftpm.sh
