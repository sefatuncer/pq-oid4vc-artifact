#!/usr/bin/env bash
# JOSE-083 — installation/build pre-test (Step 9 task 4a). NO signature verification.
export PAKET=pyjwt SURUM=2.15.0 EKSTRA=crypto
exec bash /b/pip.sh
