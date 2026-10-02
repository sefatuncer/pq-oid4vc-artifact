#!/usr/bin/env bash
# JOSE-002 — installation/build pre-test (Step 9 task 4a). NO signature verification.
export PAKET=JWT SURUM=11.1.0 ASM=JWT ANAHTAR=JWT.JwtDecoder
exec bash /b/nuget.sh
