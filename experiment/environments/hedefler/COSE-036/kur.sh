#!/usr/bin/env bash
# COSE-036 — wolfCOSE (kaynak, commit sabit; GPL-3.0: yalnız ölçülür, dağıtılmaz). Adım 9 görev 4a. İmza doğrulama YOK.
# wolfSSL v5.9.2-stable, README'deki "Full Build (All Algorithms)" bayraklarıyla (--enable-mldsa dahil) derlenir.
# COSE hedefi: yürütücü talimatıyla ek ortam uğraşı yapılmaz (başarısızsa kaydedilir).
set -uo pipefail
source /b/ortak.sh
DEPO=https://github.com/wolfssl/wolfcose; SHA=f907071b10127f3ae2dd7719749a91b039ff04a1
WDEPO=https://github.com/wolfSSL/wolfssl; WETIKET=v5.9.2-stable; WSHA=ac01707f552c611fbd135cc723b2682b3e7f80f2
WBAYRAK="--enable-ecc --enable-ed25519 --enable-ed448 --enable-curve25519 --enable-aesgcm --enable-aesccm --enable-sha384 --enable-sha512 --enable-keygen --enable-rsapss --enable-chacha --enable-poly1305 --enable-mldsa --enable-lms --enable-hkdf --enable-aeskeywrap"
yaz ekosistem "kaynak (git) + make"; yaz paket wolfcose; yaz istenen_surum "git:$SHA"
yaz arac "$(gcc --version | head -1); wolfSSL $WETIKET"
getir() { mkdir -p "$2" && cd "$2" && git_anonim init -q . && git_anonim remote add origin "$1.git" && git_anonim fetch -q --depth 1 origin "$3" && git_anonim checkout -q FETCH_HEAD; }
if ! getir "$WDEPO" /tmp/wolfssl "$WSHA"; then yaz sonuc erisilemedi; yaz not "wolfSSL fetch başarısız"; bitir basarisiz 30; fi
[ "$(git rev-parse HEAD)" = "$WSHA" ] || { yaz not "wolfSSL commit uyuşmuyor"; bitir basarisiz 31; }
echo "== wolfSSL $WETIKET: autogen + configure ($WBAYRAK)"
if ! { ./autogen.sh >/dev/null && ./configure --prefix=/usr/local $WBAYRAK >/tmp/wconf.log 2>&1 && make -j8 >/tmp/wmake.log 2>&1 && make install >/dev/null; }; then
  tail -30 /tmp/wconf.log /tmp/wmake.log; yaz not "wolfSSL derlemesi başarısız"; bitir basarisiz 10; fi
ldconfig 2>/dev/null || true
grep -E "define (HAVE_DILITHIUM|WOLFSSL_HAVE_MLDSA|WOLFSSL_WC_DILITHIUM|HAVE_ED25519|HAVE_ECC)\b" /usr/local/include/wolfssl/options.h | tee "$C/wolfssl-options-secim.txt"
yaz not "wolfSSL $WETIKET ($WSHA) bayrakları: $WBAYRAK"
if ! getir "$DEPO" /tmp/wolfcose "$SHA"; then yaz sonuc erisilemedi; yaz not "wolfCOSE fetch başarısız"; bitir basarisiz 30; fi
HEAD=$(git rev-parse HEAD); yaz commit "$HEAD"; yaz commit_kaynagi "git checkout (CERCEVE son_commit_sha)"
yaz paket_ozeti "git-tree:$(git rev-parse 'HEAD^{tree}')"; yaz kurulan_surum "git:${HEAD:0:12}"
sed -n '75,95p' include/wolfcose/settings.h > "$C/settings-h-L75-95.txt" 2>/dev/null
echo "== wolfCOSE make (libwolfcose.a)"
if ! make -j8 all 2>&1 | tail -20; then :; fi
[ -f libwolfcose.a ] || { yaz not "wolfCOSE make başarısız"; bitir basarisiz 12; }
yaz kilit_dosyasi "yok (kaynak; wolfSSL etiket+commit ve wolfCOSE commit sabit)"; yaz kilit_sha256 "$(ozet libwolfcose.a) (libwolfcose.a; yeniden üretilebilirlik iddia edilmez)"
yaz lisans_kayit "$(head -3 LICENSE | tr '\n' ' ' | cut -c1-60)"
# Yalnız imza (COSE_Sign1 / COSE_Sign) doğrulama adları; wolfcose.h'de bildirilenler (deneme 1: EAT/MAC adları seçilmişti — çalışma hatası)
FN=$(grep -ohE '\bwc_CoseSign1?_Verify[A-Za-z0-9_]*[[:space:]]*\(' include/wolfcose/wolfcose.h | tr -d ' (' | sort -u | head -4)
echo "doğrulama işlev adları (başlık): $FN"
{ echo '#include <stdio.h>'; echo '#include <wolfcose/wolfcose.h>'; echo 'int main(void) {'
  echo '  puts("wolfcose baglandi (islevler CAGRILMAZ; yalniz adres)");'
  for f in $FN; do echo "  printf(\"sembol $f %s\n\", (void*)&$f ? \"var\" : \"yok\");"; done; echo '  return 0; }'; } > /tmp/baglanti.c
cp /tmp/baglanti.c "$C/"
if ! gcc -std=gnu11 -DHAVE_ANONYMOUS_INLINE_AGGREGATES=1 -I include -I/usr/local/include /tmp/baglanti.c libwolfcose.a -L/usr/local/lib -lwolfssl -lm -o /tmp/baglanti; then
  yaz not "bağlama programı derlenemedi"; bitir basarisiz 13; fi
if LD_LIBRARY_PATH=/usr/local/lib /tmp/baglanti > "$C/ice_aktar.txt" 2>&1; then cat "$C/ice_aktar.txt"; bitir basarili 0
else cat "$C/ice_aktar.txt"; bitir basarisiz 20; fi
