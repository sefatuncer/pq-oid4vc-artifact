#!/usr/bin/env bash
# JOSE-001 — installation/build pre-test (Step 9 task 4a). NO signature verification.
export PAKET=System.IdentityModel.Tokens.Jwt SURUM=8.23.0 ASM=System.IdentityModel.Tokens.Jwt ANAHTAR=System.IdentityModel.Tokens.Jwt.JwtSecurityTokenHandler
exec bash /b/nuget.sh
