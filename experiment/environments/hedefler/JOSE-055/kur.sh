#!/usr/bin/env bash
# JOSE-055 — installation/build pre-test (Step 9 task 4a). NO signature verification.
export HEDEF_GAV=io.jsonwebtoken:jjwt-api:0.13.0 EK_GAV=io.jsonwebtoken:jjwt-impl:0.13.0\ io.jsonwebtoken:jjwt-jackson:0.13.0 EK_KONTROL=jjwt-impl-0.13.0.jar ANAHTAR=io.jsonwebtoken.Jwts\ io.jsonwebtoken.JwtParserBuilder\ io.jsonwebtoken.impl.DefaultJwtParserBuilder
exec bash /b/maven.sh
