#!/usr/bin/env bash
# JOSE-084 — installation/build pre-test (Step 9 task 4a). NO signature verification.
export PAKET=python-jose SURUM=3.5.0 EKSTRA=cryptography
exec bash /b/pip.sh
