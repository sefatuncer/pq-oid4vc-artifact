#!/usr/bin/env bash
# COSE-001 — kurulum/derleme ön testi (Adım 9 görev 4a). İmza doğrulama YOK.
export HEDEF_GAV=at.asitplus.signum:indispensable-cosef-jvm:3.26.0 EK_GAV='' EK_KONTROL='' ANAHTAR=''
exec bash /b/maven.sh
