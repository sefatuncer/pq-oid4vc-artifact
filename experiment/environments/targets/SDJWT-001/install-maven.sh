#!/usr/bin/env bash
# SDJWT-001 — installation/build pre-test (Step 9 task 4a). NO signature verification.
export HEDEF_GAV=at.asitplus.wallet:vck-jvm:7.0.1 EK_GAV='' EK_KONTROL='' ANAHTAR=''
exec bash /b/maven.sh
