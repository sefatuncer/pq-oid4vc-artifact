#!/usr/bin/env bash
# SDJWT-025 — installation/build pre-test (Step 9 task 4a). NO signature verification.
export KRATE=ssi-sd-jwt SURUM=0.6.0 OZELLIK='' VARSAYILAN=true
exec bash /b/cargo.sh
