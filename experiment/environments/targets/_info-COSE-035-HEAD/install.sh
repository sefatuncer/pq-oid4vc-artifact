#!/bin/sh
# INFORMATION (outside build-results.csv): can the frame HEAD commit of cose-lib (FRAME.csv son_commit_sha) be installed?
# Purpose: input to the version-pinning decision (no ML-DSA source in release 4.8.2; present in HEAD). NO signature verification.
export PAKET=web-auth/cose-lib SURUM='4.9.x-dev#1c854bf63c5cd8d872d1e57ec7b891030f4ed314' ANAHTAR='Cose\Algorithm\Signature\MLDSA\MLDSA65' EK_PAKET='spomky-labs/cbor-php:^3.4'
exec sh /b/composer.sh
