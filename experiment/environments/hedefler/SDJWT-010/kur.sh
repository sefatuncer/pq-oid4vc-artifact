#!/usr/bin/env bash
# SDJWT-010 — installation/build pre-test (Step 9 task 4a). NO signature verification.
export KRATE=sd-jwt-payload SURUM=0.5.1 OZELLIK='' VARSAYILAN=true
exec bash /b/cargo.sh
