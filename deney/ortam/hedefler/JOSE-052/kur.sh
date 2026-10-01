#!/usr/bin/env bash
# JOSE-052 — kurulum/derleme ön testi (Adım 9 görev 4a). İmza doğrulama YOK.
export HEDEF_GAV=com.auth0:java-jwt:4.6.1 EK_GAV='' EK_KONTROL='' ANAHTAR=com.auth0.jwt.JWT\ com.auth0.jwt.JWTVerifier\ com.auth0.jwt.algorithms.Algorithm
exec bash /b/maven.sh
