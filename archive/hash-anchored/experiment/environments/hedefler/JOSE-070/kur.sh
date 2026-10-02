#!/bin/sh
# JOSE-070 — kurulum/derleme ön testi (Adım 9 görev 4a). İmza doğrulama YOK.
export PAKET=firebase/php-jwt SURUM=v7.2.0 ANAHTAR=Firebase\\JWT\\JWT
exec sh /b/composer.sh
