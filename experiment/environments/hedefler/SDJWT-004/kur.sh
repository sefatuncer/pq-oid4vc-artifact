#!/usr/bin/env bash
# SDJWT-004 — kurulum/derleme ön testi (Adım 9 görev 4a). İmza doğrulama YOK.
export HEDEF_GAV=com.authlete:sd-jwt:1.9 EK_GAV='' EK_KONTROL='' ANAHTAR=''
exec bash /b/maven.sh
