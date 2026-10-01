#!/usr/bin/env bash
# crates.io hedefi: sabit sürüm (=x.y.z) bağımlılıkla ikili derle, Cargo.lock kaydet, bağlama kontrolü.
# Aşama A: yalnız `use krate as _;` ile derleme (kurulum/derleme). Aşama B: /w/main.rs (API tiplerine başvuru).
# Girdi (kur.sh): KRATE, SURUM, [OZELLIK "a,b"], [VARSAYILAN=false]. İmza doğrulama YOK.
set -uo pipefail
source /b/ortak.sh
: "${KRATE:?}"; : "${SURUM:?}"
yaz ekosistem crates.io; yaz paket "$KRATE"; yaz istenen_surum "$SURUM"
[ -n "${OZELLIK:-}" ] && yaz not "özellikler [${OZELLIK}] varsayılan=${VARSAYILAN:-true}"
yaz arac "$(rustc --version | cut -d' ' -f1-2); $(cargo --version | cut -d' ' -f1-2)"
P=/tmp/p; rm -rf $P; mkdir -p $P/src; cd $P
AD=$(echo "$KRATE" | tr '-' '_')
OZ=""; [ -n "${OZELLIK:-}" ] && OZ=", features = [$(echo "$OZELLIK" | sed 's/\([^,]*\)/"\1"/g')]"
VS=""; [ "${VARSAYILAN:-true}" = "false" ] && VS=", default-features = false"
printf '[package]\nname = "ortam-deneme"\nversion = "0.0.0"\nedition = "2021"\npublish = false\n\n[dependencies]\n%s = { version = "=%s"%s%s }\n' "$KRATE" "${SURUM#v}" "$OZ" "$VS" > Cargo.toml
cat Cargo.toml
printf 'use %s as _;\nfn main() { println!("asama A: krate derlendi ve baglandi"); }\n' "$AD" > src/main.rs
echo "== Aşama A: cargo build"
if ! cargo build 2>&1; then yaz not "cargo build (aşama A) başarısız"; bitir basarisiz 10; fi
cp Cargo.toml Cargo.lock "$C/"
yaz kilit_dosyasi Cargo.lock; yaz kilit_sha256 "$(ozet Cargo.lock)"
yaz bagimlilik_sayisi "$(( $(grep -c '^\[\[package\]\]' Cargo.lock) - 1 ))"
CS=$(awk -v n="$KRATE" -v v="${SURUM#v}" '$0=="[[package]]"{a=0} $0=="name = \""n"\""{a=1} a&&$0=="version = \""v"\""{b=1} a&&b&&/^checksum/{gsub(/"/,"",$3);print $3;exit}' Cargo.lock)
[ -n "$CS" ] && yaz paket_ozeti "sha256:$CS (Cargo.lock checksum)"
yaz kurulan_surum "${SURUM#v}"
VCS=$(ls -d /usr/local/cargo/registry/src/*/"$KRATE-${SURUM#v}" 2>/dev/null | head -1)
if [ -n "$VCS" ] && [ -f "$VCS/.cargo_vcs_info.json" ]; then
  cp "$VCS/.cargo_vcs_info.json" "$C/"
  S1=$(grep -o '"sha1": *"[0-9a-f]*"' "$VCS/.cargo_vcs_info.json" | grep -o '[0-9a-f]\{40\}')
  [ -n "$S1" ] && { yaz commit "$S1"; yaz commit_kaynagi ".cargo_vcs_info.json (crate içinde)"; }
fi
[ -n "$VCS" ] && grep -E '^pub (use|mod|struct|enum|trait|fn|type) ' "$VCS/src/lib.rs" 2>/dev/null | head -40 > "$C/lib-pub.txt"
echo "== Aşama B: API tiplerine başvuran program"
cp /w/main.rs src/main.rs
if ! cargo build 2>&1; then yaz not "aşama B derlemesi başarısız (API adları)"; bitir basarisiz 12; fi
if ./target/debug/ortam-deneme > "$C/ice_aktar.txt" 2>&1; then cat "$C/ice_aktar.txt"; bitir basarili 0
else cat "$C/ice_aktar.txt"; yaz not "çalıştırma hatası"; bitir basarisiz 20; fi
