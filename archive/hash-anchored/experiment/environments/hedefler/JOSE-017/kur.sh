#!/usr/bin/env bash
# JOSE-017 — jwt-cpp (YEDEK ADAYI; JOSE-104'ün yerine genel yedek 5.3-4-ii). Kaynak, commit sabit (sürüm yok).
# Başlık-yalnız kütüphane: en küçük C++ programı derlenir ve sistem OpenSSL'ine bağlanır. İmza doğrulama YOK.
set -uo pipefail
source /b/ortak.sh
DEPO=https://github.com/Thalhammer/jwt-cpp; SHA=0a503e75084cfdb48cc2186e6b961444eb819007
yaz ekosistem "kaynak (git), başlık-yalnız"; yaz paket jwt-cpp; yaz istenen_surum "git:$SHA"
yaz arac "$(g++ --version | head -1); sistem $(openssl version | cut -d' ' -f1-2)"
mkdir -p /tmp/src && cd /tmp/src
if ! { git_anonim init -q . && git_anonim remote add origin "$DEPO.git" && git_anonim fetch -q --depth 1 origin "$SHA" && git_anonim checkout -q FETCH_HEAD; }; then
  yaz sonuc erisilemedi; yaz not "anonim git fetch başarısız"; bitir basarisiz 30; fi
HEAD=$(git rev-parse HEAD); yaz commit "$HEAD"; yaz commit_kaynagi "git checkout (CERCEVE son_commit_sha)"
yaz paket_ozeti "git-tree:$(git rev-parse 'HEAD^{tree}')"; yaz kurulan_surum "git:${HEAD:0:12}"
yaz kilit_dosyasi "yok (başlık-yalnız; bağımlılık: sistem OpenSSL + gömülü picojson)"; yaz kilit_sha256 "$(git rev-parse 'HEAD^{tree}')"
yaz lisans_kayit MIT
cat > /tmp/baglanti.cpp <<'CPP'
// Bağlama kontrolü: doğrulayıcı türü decltype ile (DEĞERLENDİRİLMEDEN) alınır; hiçbir işlev ÇAĞRILMAZ.
#include <jwt-cpp/jwt.h>
#include <iostream>
#include <typeinfo>
int main() {
  using dogrulayici_t = decltype(jwt::verify());
  std::cout << "jwt-cpp baglandi; tip " << typeid(dogrulayici_t).name() << "\n";
  std::cout << "tip " << typeid(jwt::algorithm::es256).name() << "\n";
  return 0;
}
CPP
cp /tmp/baglanti.cpp "$C/"
if ! g++ -std=c++17 -I include /tmp/baglanti.cpp -lssl -lcrypto -o /tmp/baglanti; then yaz not "derleme başarısız"; bitir basarisiz 12; fi
if /tmp/baglanti > "$C/ice_aktar.txt" 2>&1; then cat "$C/ice_aktar.txt"; bitir basarili 0; else cat "$C/ice_aktar.txt"; bitir basarisiz 20; fi
