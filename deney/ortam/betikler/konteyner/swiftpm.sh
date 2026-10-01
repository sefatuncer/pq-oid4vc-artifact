#!/usr/bin/env bash
# SwiftPM hedefi: yürütülebilir paket (bağımlılık: DEPO @ exact SURUM ya da REVIZYON), Package.resolved kaydet,
# derle ve bağla; /w/main.swift yalnız modülü içe aktarır ve tür adlarına başvurur. İmza doğrulama YOK.
set -uo pipefail
source /b/ortak.sh
: "${DEPO:?}"; : "${URUN:?}"; : "${PAKET_KIMLIK:?}"
yaz ekosistem swiftpm; yaz paket "$DEPO"; yaz istenen_surum "${SURUM:-git:${REVIZYON:-?}}"
yaz arac "$(swift --version 2>&1 | head -1 | sed 's/ (.*//')"
P=/tmp/p; rm -rf $P; mkdir -p $P/Sources/Deneme; cd $P
if [ -n "${SURUM:-}" ]; then GEREK="exact: \"$SURUM\""; else GEREK="revision: \"$REVIZYON\""; fi
cat > Package.swift <<X
// swift-tools-version:5.9
import PackageDescription
let package = Package(
  name: "Deneme",
  dependencies: [ .package(url: "$DEPO", $GEREK) ],
  targets: [ .executableTarget(name: "Deneme", dependencies: [ .product(name: "$URUN", package: "$PAKET_KIMLIK") ]) ]
)
X
cp /w/main.swift Sources/Deneme/main.swift
echo "== swift package resolve"
if ! swift package resolve; then yaz sonuc erisilemedi; yaz not "SwiftPM çözümleme (git) başarısız"; bitir basarisiz 30; fi
cp Package.swift Package.resolved "$C/"
yaz kilit_dosyasi "Package.resolved (git revizyonları)"; yaz kilit_sha256 "$(ozet Package.resolved)"
yaz bagimlilik_sayisi "$(grep -c '"identity"' Package.resolved)"
REV=$(awk -v k="\"$PAKET_KIMLIK\"" 'index($0,"\"identity\" : " k){a=1} a&&/^[[:space:]]*}/{exit} a&&/"revision"/{gsub(/[",]/,"",$3);print $3;exit}' Package.resolved)
[ -n "$REV" ] && { yaz commit "$REV"; yaz commit_kaynagi "Package.resolved revision"; yaz paket_ozeti "git:$REV (SwiftPM revizyonu)"; }
VER=$(awk -v k="\"$PAKET_KIMLIK\"" 'index($0,"\"identity\" : " k){a=1} a&&/^[[:space:]]*}/{exit} a&&/"version"/{gsub(/[",]/,"",$3);print $3;exit}' Package.resolved)
yaz kurulan_surum "${VER:-git:${REV:0:12}}"
[ -f /w/ek.sh ] && . /w/ek.sh
echo "== swift build"
if ! swift build -c debug 2>&1; then yaz not "swift build başarısız"; bitir basarisiz 12; fi
if ./.build/debug/Deneme > "$C/ice_aktar.txt" 2>&1; then cat "$C/ice_aktar.txt"; bitir basarili 0
else cat "$C/ice_aktar.txt"; yaz not "çalıştırma hatası"; bitir basarisiz 20; fi
