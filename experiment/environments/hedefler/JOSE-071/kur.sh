#!/bin/sh
# JOSE-071 — kurulum/derleme ön testi (Adım 9 görev 4a). İmza doğrulama YOK.
export PAKET=lcobucci/jwt SURUM=5.6.0 ANAHTAR=Lcobucci\\JWT\\Validation\\Validator
exec sh /b/composer.sh
