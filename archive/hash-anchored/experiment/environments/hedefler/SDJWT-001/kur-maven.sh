#!/usr/bin/env bash
# SDJWT-001 — kurulum/derleme ön testi (Adım 9 görev 4a). İmza doğrulama YOK.
export HEDEF_GAV=at.asitplus.wallet:vck-jvm:7.0.1 EK_GAV='' EK_KONTROL='' ANAHTAR=''
exec bash /b/maven.sh
