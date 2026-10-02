#!/usr/bin/env bash
# JOSE-002 — kurulum/derleme ön testi (Adım 9 görev 4a). İmza doğrulama YOK.
export PAKET=JWT SURUM=11.1.0 ASM=JWT ANAHTAR=JWT.JwtDecoder
exec bash /b/nuget.sh
