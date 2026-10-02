#!/usr/bin/env bash
# Go module target: get with a pinned version, record go.sum, build and link the smallest program (NO signature verification).
# Input (install.sh): MODUL, SURUM, /w/import_check.go
set -uo pipefail
source /b/common.sh
: "${MODUL:?}"; : "${SURUM:?}"
yaz ekosistem go; yaz paket "$MODUL"; yaz istenen_surum "$SURUM"; yaz arac "$(go version)"
P=/tmp/p; rm -rf $P; mkdir -p $P; cd $P
go mod init pq-a09-ortam/deneme >/dev/null 2>&1
echo "== go get $MODUL@$SURUM"
if ! go get "$MODUL@$SURUM"; then yaz not "go get başarısız"; bitir basarisiz 10; fi
go mod download -json "$MODUL@$SURUM" > "$C/go-mod-download.json" 2>/dev/null || true
python3 - <<'PY' >> "$C/result.tsv"
import json
try:
    d = json.load(open("/w/output/go-mod-download.json"))
    o = d.get("Origin") or {}
    if o.get("Hash"):
        print(f"commit\t{o['Hash']}"); print(f"commit_kaynagi\tGo proxy Origin ({o.get('Ref','')})")
    print(f"kurulan_surum\t{d.get('Version','')}")
except Exception as e:
    print(f"not\tgo mod download -json okunamadı: {e}")
PY
cp /w/import_check.go main.go
if ! go mod tidy; then yaz not "go mod tidy başarısız"; bitir basarisiz 11; fi
cp go.mod go.sum "$C/"
yaz kilit_dosyasi go.sum; yaz kilit_sha256 "$(ozet go.sum)"
yaz bagimlilik_sayisi "$(grep -v '/go.mod ' go.sum | awk '{print $1}' | sort -u | grep -c .)"
yaz paket_ozeti "$(grep "^$MODUL $SURUM " go.sum | grep -v '/go.mod' | awk '{print $3}')"
echo "== derleme ve bağlama"
if ! go build -o /tmp/deneme . ; then yaz not "go build başarısız"; bitir basarisiz 12; fi
if /tmp/deneme > "$C/import_check.txt" 2>&1; then cat "$C/import_check.txt"; bitir basarili 0
else cat "$C/import_check.txt"; yaz not "çalıştırma hatası"; bitir basarisiz 20; fi
