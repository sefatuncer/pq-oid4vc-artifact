#!/usr/bin/env bash
# JOSE-091 — installation/build pre-test (Step 9 task 4a). NO signature verification.
export KRATE=frank_jwt SURUM=3.1.4 OZELLIK='' VARSAYILAN=true
exec bash /b/cargo.sh
