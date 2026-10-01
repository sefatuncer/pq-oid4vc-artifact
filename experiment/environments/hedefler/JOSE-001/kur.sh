#!/usr/bin/env bash
# JOSE-001 — kurulum/derleme ön testi (Adım 9 görev 4a). İmza doğrulama YOK.
export PAKET=System.IdentityModel.Tokens.Jwt SURUM=8.23.0 ASM=System.IdentityModel.Tokens.Jwt ANAHTAR=System.IdentityModel.Tokens.Jwt.JwtSecurityTokenHandler
exec bash /b/nuget.sh
