#!/usr/bin/env bash
# JOSE-092 — installation/build pre-test (Step 9 task 4a). NO signature verification.
export KRATE=jsonwebtoken SURUM=11.1.0 OZELLIK=aws_lc_rs VARSAYILAN=true
exec bash /b/cargo.sh
