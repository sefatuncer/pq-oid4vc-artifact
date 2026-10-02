#!/usr/bin/env bash
# SDJWT-021 — installation/build pre-test (Step 9 task 4a). NO signature verification.
export PAKET=WalletFramework.SdJwtVc SURUM=3.1.0 ASM=WalletFramework.SdJwtVc ANAHTAR=''
exec bash /b/nuget.sh
