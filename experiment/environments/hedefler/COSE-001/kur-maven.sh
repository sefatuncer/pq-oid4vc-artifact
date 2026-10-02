#!/usr/bin/env bash
# COSE-001 — installation/build pre-test (Step 9 task 4a). NO signature verification.
export HEDEF_GAV=at.asitplus.signum:indispensable-cosef-jvm:3.26.0 EK_GAV='' EK_KONTROL='' ANAHTAR=''
exec bash /b/maven.sh
