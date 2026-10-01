#!/usr/bin/env bash
# =====================================================================
#  PQ-OID4VC | Adım 4 | Tamarin kural şemaları R1–R5: toplu koşum
# =====================================================================
#  Kullanım (Git Bash):
#     bash model/tamarin/betik/calistir.sh          # bütün varyantlar (ozet.csv baştan yazılır)
#     bash model/tamarin/betik/calistir.sh R3       # yalnız bir kural (o kuralın satırları yenilenir)
#
#  Girdi : betik/varyantlar.tsv (kural, varyant, rol, dosya, bayraklar, G_beklenen[, lemma_beklenen])
#  İyi biçimlilik kuralı (24.09.2026): uyarılı her koşum "gecersiz_wf" olarak kaydedilir.
#  Çıktı : sonuc/ozet.csv   kural,varyant,lemma,sonuc,adim,sure_s,bellek_MiB,merdiven_basamagi
#          sonuc/ham/<kural>__<varyant>__<lemma>__b<basamak>.{txt,meta}   ham Tamarin çıktısı
#          sonuc/ham/<kural>__<varyant>__liste.{txt,meta}                  lemma listesi + iyi biçimlilik
#          sonuc/json/<kural>__<varyant>__<lemma>.json                     bulunan izler (--output-json)
#          sonuc/calistir_log.txt, sonuc/uyarilar.txt
#          ardından betik/degerlendir.py -> sonuc/degerlendirme.csv, datalog_uyum.csv, metrikler.txt
#
#  Kurallar (proje çalışma kuralları, görev tanımı):
#   * Aynı anda tek Tamarin konteyneri: başka bir pq-a02-tamarin konteyneri çalışıyorsa beklenir.
#   * Her çağrı: --rm, --memory=12g --memory-swap=12g, timeout 600 s, ad öneki pq-a04-.
#   * Her lemma ayrı konteynerde koşar (süre ve bellek tepesi lemma başına ölçülür).
#   * Sonlanmama merdiveni (her basamak <= 600 s, 12 GB):
#       1 --prove=<lemma>
#       2 [use_induction]/[reuse] yardımcı lemmaları   -> model düzeyinde, gerekirse elle
#       3 --prove=<lemma> --auto-sources
#       4 tactic / oracle                                -> model düzeyinde, gerekirse elle
#       5 --prove=<lemma> --bound=40                     (sınırlı arama)
#       6 "kapanmadi" etiketi
#     Betik 1 -> 3 -> 5 -> 6 basamaklarını kendiliğinden uygular.
set -u
BASE="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BASE" || exit 1
W=$(cygpath -m "$BASE")
IMG=pq-a02-tamarin:1.12.0
SOLVER=pq-a02-solver:1.0
TO=600
export MSYS_NO_PATHCONV=1
FILTRE="${1:-}"

mkdir -p sonuc/ham sonuc/json
CSV=sonuc/ozet.csv
LOG=sonuc/calistir_log.txt
UYARI=sonuc/uyarilar.txt
HDR="kural,varyant,lemma,sonuc,adim,sure_s,bellek_MiB,merdiven_basamagi"

if [ -z "$FILTRE" ] || [ ! -f "$CSV" ]; then
  echo "$HDR" > "$CSV"; : > "$UYARI"; : > "$LOG"
else
  # yalnız filtrelenen kuralın eski satırlarını sil
  grep -v "^${FILTRE}," "$CSV" > "$CSV.tmp"; mv "$CSV.tmp" "$CSV"
fi

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

log "Başlangıç. Filtre='${FILTRE}'. İmaj: $IMG ($(docker image inspect --format '{{.Id}}' $IMG 2>/dev/null))"
docker run --rm --name pq-a04-surum --memory=2g --memory-swap=2g "$IMG" tamarin-prover --version 2>&1 \
  | grep -E "tamarin-prover [0-9]|Maude version|Git revision" | sed 's/^/    /' | tee -a "$LOG"

N=0
tamarin_run() { # <id> <model_dosyasi> [tamarin argümanları...]
  local id=$1 model=$2; shift 2
  N=$((N+1))
  local bekledi=0
  while [ -n "$(docker ps -q --filter "ancestor=$IMG")" ]; do
    [ $bekledi -eq 0 ] && log "  başka bir Tamarin konteyneri çalışıyor; bekleniyor"
    bekledi=1; sleep 5
  done
  docker run --rm --name "pq-a04-k${N}" --memory=12g --memory-swap=12g \
    -v "$W:/work" "$IMG" sh /work/betik/ic_kosum.sh "sonuc/ham/$id" "$TO" "modeller/$model" "$@" \
    >> "$LOG" 2>&1 < /dev/null
}

RES=""; STEPS=""; WALL=""; MEM=""; RC=""
parse() { # <txt> <meta> <lemma>
  local line
  RC=$(sed -nE 's/.*rc=([0-9]+).*/\1/p' "$2")
  WALL=$(sed -nE 's/.*wall_s=([0-9.]+).*/\1/p' "$2")
  MEM=$(sed -nE 's/.*mem_peak_MiB=([0-9.NA]+).*/\1/p' "$2")
  line=$(sed -n '/summary of summaries/,$p' "$1" | grep -E "^[[:space:]]+$3 \((all-traces|exists-trace)\):" | head -1)
  STEPS=$(printf '%s' "$line" | sed -nE 's/.*\(([0-9]+) steps\).*/\1/p')
  case "$line" in
    *"falsified - found trace"*)    RES=falsified ;;
    *"falsified - no trace found"*) RES=falsified ;;
    *"verified ("*)                 RES=verified ;;
    *"analysis incomplete"*)        RES=incomplete ;;
    *)                              RES=error ;;
  esac
  [ "$RC" = "124" ] && RES=timeout
  [ -z "$STEPS" ] && STEPS=NA
}

run_lemma() { # <kural> <varyant> <dosya> <dflags> <lemma>
  local k=$1 v=$2 f=$3 dfl=$4 l=$5 b extra id
  for b in 1 3 5; do
    case $b in
      1) extra="" ;;
      3) extra="--auto-sources" ;;
      5) extra="--bound=40" ;;
    esac
    id="${k}__${v}__${l}__b${b}"
    # shellcheck disable=SC2086
    tamarin_run "$id" "$f" --prove="$l" $dfl $extra --output-json="/work/sonuc/json/${k}__${v}__${l}.json"
    parse "sonuc/ham/$id.txt" "sonuc/ham/$id.meta" "$l"
    # kural (24.09.2026): iyi biçimlilik uyarılı koşum geçersizdir
    if grep -q "wellformedness check failed" "sonuc/ham/$id.txt"; then
      RES=gecersiz_wf
      echo "$k $v $l: WELLFORMEDNESS UYARISI (koşum geçersiz)" >> "$UYARI"
    fi
    log "  $k $v $l basamak=$b -> $RES ($STEPS adım) ${WALL}s ${MEM}MiB rc=$RC"
    if [ "$RES" = "gecersiz_wf" ]; then
      echo "$k,$v,$l,$RES,$STEPS,$WALL,$MEM,$b" >> "$CSV"
      return
    fi
    if [ "$RES" = "verified" ] || [ "$RES" = "falsified" ]; then
      echo "$k,$v,$l,$RES,$STEPS,$WALL,$MEM,$b" >> "$CSV"
      return
    fi
  done
  log "  $k $v $l -> KAPANMADI (basamak 6)"
  echo "$k,$v,$l,kapanmadi,$STEPS,$WALL,$MEM,6" >> "$CSV"
}

while IFS=$'\t' read -r kural varyant rol dosya bayraklar gbek lbek; do
  case "$kural" in ''|\#*) continue ;; esac
  [ -n "$FILTRE" ] && [ "$kural" != "$FILTRE" ] && continue
  dflags=""
  if [ "$bayraklar" != "-" ]; then
    for fl in ${bayraklar//,/ }; do dflags="$dflags -D=$fl"; done
  fi
  log "== $kural $varyant ($rol) bayraklar:${dflags:- yok} G_beklenen=$gbek"
  lid="${kural}__${varyant}__liste"
  # shellcheck disable=SC2086
  tamarin_run "$lid" "$dosya" $dflags
  if grep -q "wellformedness check failed" "sonuc/ham/$lid.txt"; then
    echo "$kural $varyant: WELLFORMEDNESS UYARISI" >> "$UYARI"
    log "  UYARI: iyi biçimlilik denetimi başarısız"
  fi
  lemmalar=$(sed -n '/summary of summaries/,$p' "sonuc/ham/$lid.txt" \
             | sed -nE 's/^[[:space:]]+([A-Za-z0-9_]+) \((all-traces|exists-trace)\):.*/\1/p')
  if [ -z "$lemmalar" ]; then
    log "  HATA: lemma listesi alınamadı (ayrıştırma hatası?)"; echo "$kural $varyant: lemma listesi yok" >> "$UYARI"
    continue
  fi
  for l in $lemmalar; do run_lemma "$kural" "$varyant" "$dosya" "$dflags" "$l"; done
done < betik/varyantlar.tsv

log "Tamarin koşumları bitti ($N konteyner). Değerlendirme (clingo, $SOLVER) başlıyor."
docker run --rm --name pq-a04-degerlendir --memory=2g --memory-swap=2g -v "$W:/work" -w /work \
  "$SOLVER" python betik/degerlendir.py 2>&1 | tee -a "$LOG"
log "Bitti."
