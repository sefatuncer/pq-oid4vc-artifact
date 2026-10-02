#!/bin/sh
# COSE-035 — kurulum/derleme ön testi (Adım 9 görev 4a). İmza doğrulama YOK.
# Ortam düzeltmesi: cose-lib'in `suggest` ettiği spomky-labs/cbor-php (>=3.4.0; "RFC 9052 header reader and
# cryptographic structures ... CoseSign1Tag and its siblings") birlikte kurulur. Kütüphane kodu değişmez.
export PAKET=web-auth/cose-lib SURUM=4.8.2 ANAHTAR='' EK_PAKET='spomky-labs/cbor-php:^3.4'
exec sh /b/composer.sh
