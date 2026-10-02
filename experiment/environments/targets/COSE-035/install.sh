#!/bin/sh
# COSE-035 — installation/build pre-test (Step 9 task 4a). NO signature verification.
# Environment fix: spomky-labs/cbor-php (>=3.4.0; "RFC 9052 header reader and
# cryptographic structures ... CoseSign1Tag and its siblings"), which cose-lib `suggest`s, is installed with it. The library code does not change.
export PAKET=web-auth/cose-lib SURUM=4.8.2 ANAHTAR='' EK_PAKET='spomky-labs/cbor-php:^3.4'
exec sh /b/composer.sh
