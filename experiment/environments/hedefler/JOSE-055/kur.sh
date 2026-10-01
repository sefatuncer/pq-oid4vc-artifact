#!/usr/bin/env bash
# JOSE-055 — kurulum/derleme ön testi (Adım 9 görev 4a). İmza doğrulama YOK.
export HEDEF_GAV=io.jsonwebtoken:jjwt-api:0.13.0 EK_GAV=io.jsonwebtoken:jjwt-impl:0.13.0\ io.jsonwebtoken:jjwt-jackson:0.13.0 EK_KONTROL=jjwt-impl-0.13.0.jar ANAHTAR=io.jsonwebtoken.Jwts\ io.jsonwebtoken.JwtParserBuilder\ io.jsonwebtoken.impl.DefaultJwtParserBuilder
exec bash /b/maven.sh
