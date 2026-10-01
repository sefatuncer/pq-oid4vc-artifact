#!/usr/bin/env bash
# BİLGİ (CSV dışı): WalletFramework.SdJwtVc 3.1.0 kurulumunda SD-JWT çekirdek derlemesi (WalletFramework.SdJwtLib) türleri. İmza doğrulama YOK.
export PAKET=WalletFramework.SdJwtVc SURUM=3.1.0 ASM=WalletFramework.SdJwtLib ANAHTAR=""
exec bash /b/nuget.sh
