#!/usr/bin/env bash
# RubyGems hedefi: Gemfile (sürüm sabit) → Gemfile.lock (CHECKSUMS dahil) → bundle install → içe aktarma kontrolü.
# Girdi (kur.sh): PAKET, SURUM, /w/ice_aktar.rb. İmza doğrulama YOK.
set -uo pipefail
source /b/ortak.sh
: "${PAKET:?}"; : "${SURUM:?}"
yaz ekosistem rubygems; yaz paket "$PAKET"; yaz istenen_surum "$SURUM"
yaz arac "$(ruby -v | cut -d' ' -f1-2); bundler $(bundle -v | cut -d' ' -f3); ruby-openssl $(ruby -ropenssl -e 'puts OpenSSL::OPENSSL_LIBRARY_VERSION')"
P=/tmp/p; rm -rf $P; mkdir -p $P; cd $P
printf 'source "https://rubygems.org"\ngem "%s", "= %s"\n' "$PAKET" "${SURUM#v}" > Gemfile
bundle config set --local path vendor/bundle >/dev/null
bundle config set --local lockfile_checksums true >/dev/null
echo "== bundle lock + install ($PAKET = ${SURUM#v})"
if ! bundle lock; then yaz not "bundle lock başarısız"; bitir basarisiz 10; fi
if ! bundle install; then yaz not "bundle install başarısız"; bitir basarisiz 11; fi
cp Gemfile Gemfile.lock "$C/"
yaz kilit_dosyasi "Gemfile.lock (CHECKSUMS dahil)"; yaz kilit_sha256 "$(ozet Gemfile.lock)"
yaz bagimlilik_sayisi "$(sed -n '/^GEM/,/^$/p' Gemfile.lock | grep -c -E '^    [a-z0-9_-]+ \(')"
yaz kurulan_surum "$(bundle exec ruby -e "puts Gem.loaded_specs['$PAKET'].version")"
CS=$(sed -n '/^CHECKSUMS/,/^$/p' Gemfile.lock | grep -E "^  $PAKET \(" | sed 's/.*sha256=/sha256:/')
[ -n "$CS" ] && yaz paket_ozeti "$CS (Gemfile.lock CHECKSUMS)"
yaz lisans_kayit "$(bundle exec ruby -e "puts Gem.loaded_specs['$PAKET'].licenses.join(',')")"
echo "== içe aktarma kontrolü (imza doğrulama YOK)"
if bundle exec ruby /w/ice_aktar.rb > "$C/ice_aktar.txt" 2>&1; then cat "$C/ice_aktar.txt"; bitir basarili 0
else cat "$C/ice_aktar.txt"; yaz not "içe aktarma hatası"; bitir basarisiz 20; fi
