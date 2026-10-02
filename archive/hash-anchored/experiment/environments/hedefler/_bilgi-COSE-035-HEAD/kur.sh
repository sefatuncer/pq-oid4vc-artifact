#!/bin/sh
# BİLGİ (derleme-sonuc.csv dışı): cose-lib çerçeve HEAD commit'i (CERCEVE son_commit_sha) kurulabiliyor mu?
# Amaç: sürüm sabitleme kararına girdi (4.8.2 sürümünde ML-DSA kaynağı yok; HEAD'de var). İmza doğrulama YOK.
export PAKET=web-auth/cose-lib SURUM='4.9.x-dev#1c854bf63c5cd8d872d1e57ec7b891030f4ed314' ANAHTAR='Cose\Algorithm\Signature\MLDSA\MLDSA65' EK_PAKET='spomky-labs/cbor-php:^3.4'
exec sh /b/composer.sh
