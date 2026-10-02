#!/usr/bin/env bash
# SDJWT-002 — affinidi selective_disclosure_jwt (pub.dev). Adım 9 görev 4a. İmza doğrulama YOK.
# pubspec.lock (sha256) kaydedilir; paket kitaplığı içe aktarılır, doğrulayıcı sınıf adlarına tür değişmezi olarak başvurulur.
set -uo pipefail
source /b/ortak.sh
PAKET=selective_disclosure_jwt; SURUM=1.1.1
yaz ekosistem pub.dev; yaz paket $PAKET; yaz istenen_surum $SURUM; yaz arac "$(dart --version 2>&1 | cut -d'(' -f1)"
dart --disable-analytics >/dev/null 2>&1
P=/tmp/p; mkdir -p $P/bin; cd $P
printf 'name: ortam_deneme\npublish_to: none\nenvironment:\n  sdk: ^3.0.0\ndependencies:\n  %s: %s\n' $PAKET $SURUM > pubspec.yaml
echo "== dart pub get"
if ! dart pub get; then yaz not "dart pub get başarısız"; bitir basarisiz 10; fi
cp pubspec.yaml pubspec.lock "$C/"
yaz kilit_dosyasi "pubspec.lock (sha256)"; yaz kilit_sha256 "$(ozet pubspec.lock)"
yaz bagimlilik_sayisi "$(grep -c '^  [a-z_0-9]*:$' pubspec.lock)"
SHA=$(awk -v p="  $PAKET:" '$0==p{a=1} a&&/sha256:/{gsub(/"/,"",$2);print $2;exit}' pubspec.lock)
[ -n "$SHA" ] && yaz paket_ozeti "sha256:$SHA (pubspec.lock)"
yaz kurulan_surum "$(awk -v p="  $PAKET:" '$0==p{a=1} a&&/version:/{gsub(/"/,"",$2);print $2;exit}' pubspec.lock)"
KOK=$(ls -d /root/.pub-cache/hosted/pub.dev/$PAKET-$SURUM 2>/dev/null | head -1)
SINIF=$(grep -rhoE '^(abstract )?(final |base |interface )?class [A-Z][A-Za-z0-9]*Verif[A-Za-z0-9]*' "$KOK/lib" 2>/dev/null | awk '{print $NF}' | sort -u | head -3 | tr '\n' ' ')
echo "doğrulayıcı sınıf adları (kaynak taraması): $SINIF"
# Deneme 1: KbVerifyAction ve SdJwtVerifierInput ana kitaplıktan dışa aktarılmıyor; yalnız dışa aktarılan SDKeyVerifier kullanılır
SINIF="SDKeyVerifier"
{ echo "import 'package:$PAKET/$PAKET.dart';"; echo "void main() {"; echo "  print('paket $PAKET ice aktarildi');"
  for s in $SINIF; do echo "  print('tip \${$s}');"; done; echo "}"; } > bin/main.dart
cp bin/main.dart "$C/"
if dart run bin/main.dart > "$C/ice_aktar.txt" 2>&1; then cat "$C/ice_aktar.txt"; bitir basarili 0; fi
echo "tür başvurulu program derlenmedi; yalnız içe aktarma denenir"; cat "$C/ice_aktar.txt"
printf "import 'package:%s/%s.dart' as p;\nvoid main() { print('paket %s ice aktarildi (tur basvurusu yok)'); }\n" $PAKET $PAKET $PAKET > bin/main.dart
yaz not "doğrulayıcı sınıf adları ana kitaplıktan dışa aktarılmıyor olabilir; yalnız içe aktarma"
if dart run bin/main.dart > "$C/ice_aktar.txt" 2>&1; then cat "$C/ice_aktar.txt"; bitir basarili 0; else cat "$C/ice_aktar.txt"; bitir basarisiz 20; fi
