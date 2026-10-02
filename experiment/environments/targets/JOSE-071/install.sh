#!/bin/sh
# JOSE-071 — installation/build pre-test (Step 9 task 4a). NO signature verification.
export PAKET=lcobucci/jwt SURUM=5.6.0 ANAHTAR=Lcobucci\\JWT\\Validation\\Validator
exec sh /b/composer.sh
