#!/usr/bin/env bash
# BİLGİ (CSV dışı): JOSE-102 ML-DSA SPI türü Linux derlemesinde bağlanıyor mu? — kurulum/derleme ön testi (Adım 9 görev 4a). İmza doğrulama YOK.
export DEPO=https://github.com/vapor/jwt-kit.git SURUM=5.3.0 URUN=JWTKit PAKET_KIMLIK=jwt-kit
exec bash /b/swiftpm.sh
