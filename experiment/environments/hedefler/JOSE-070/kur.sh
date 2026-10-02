#!/bin/sh
# JOSE-070 — installation/build pre-test (Step 9 task 4a). NO signature verification.
export PAKET=firebase/php-jwt SURUM=v7.2.0 ANAHTAR=Firebase\\JWT\\JWT
exec sh /b/composer.sh
