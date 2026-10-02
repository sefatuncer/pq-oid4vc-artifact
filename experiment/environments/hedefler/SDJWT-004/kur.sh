#!/usr/bin/env bash
# SDJWT-004 — installation/build pre-test (Step 9 task 4a). NO signature verification.
export HEDEF_GAV=com.authlete:sd-jwt:1.9 EK_GAV='' EK_KONTROL='' ANAHTAR=''
exec bash /b/maven.sh
