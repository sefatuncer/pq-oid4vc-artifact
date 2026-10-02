#!/usr/bin/env bash
# =====================================================================
#  PQ-OID4VC | Step 4 | Tamarin rule schemata R1–R5: batch run
# =====================================================================
#  Usage (Git Bash):
#     bash models/tamarin/betik/calistir.sh          # all variants (ozet.csv is rewritten from the start)
#     bash models/tamarin/betik/calistir.sh R3       # one rule only (the rows of that rule are renewed)
#
#  Input : betik/varyantlar.tsv (kural, varyant, rol, dosya, bayraklar, G_beklenen[, lemma_beklenen])
#  Well-formedness rule (24.09.2026): every run with a warning is recorded as "gecersiz_wf".
#  Output: sonuc/ozet.csv   kural,varyant,lemma,sonuc,adim,sure_s,bellek_MiB,merdiven_basamagi
#          sonuc/ham/<rule>__<variant>__<lemma>__b<step>.{txt,meta}   raw Tamarin output
#          sonuc/ham/<rule>__<variant>__liste.{txt,meta}                  lemma list + well-formedness
#          sonuc/json/<rule>__<variant>__<lemma>.json                     traces found (--output-json)
#          sonuc/calistir_log.txt, sonuc/uyarilar.txt
#          then betik/degerlendir.py -> sonuc/degerlendirme.csv, datalog_uyum.csv, metrikler.txt
#
#  Rules (project working rules, task definition):
#   * One Tamarin container at a time: wait if another pq-a02-tamarin container is running.
#   * Every call: --rm, --memory=12g --memory-swap=12g, timeout 600 s, name prefix pq-a04-.
#   * Every lemma runs in a separate container (duration and memory peak are measured per lemma).
#   * Non-termination ladder (every step <= 600 s, 12 GB):
#       1 --prove=<lemma>
#       2 [use_induction]/[reuse] helper lemmas   -> at model level, by hand if needed
#       3 --prove=<lemma> --auto-sources
#       4 tactic / oracle                                -> at model level, by hand if needed
#       5 --prove=<lemma> --bound=40                     (bounded search)
#       6 label "kapanmadi"
#     The script applies steps 1 -> 3 -> 5 -> 6 by itself.
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
  # delete only the old rows of the filtered rule
  grep -v "^${FILTRE}," "$CSV" > "$CSV.tmp"; mv "$CSV.tmp" "$CSV"
fi

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

log "Başlangıç. Filtre='${FILTRE}'. İmaj: $IMG ($(docker image inspect --format '{{.Id}}' $IMG 2>/dev/null))"
docker run --rm --name pq-a04-surum --memory=2g --memory-swap=2g "$IMG" tamarin-prover --version 2>&1 \
  | grep -E "tamarin-prover [0-9]|Maude version|Git revision" | sed 's/^/    /' | tee -a "$LOG"

N=0
tamarin_run() { # <id> <model_file> [tamarin arguments...]
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

run_lemma() { # <rule> <variant> <file> <dflags> <lemma>
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
    # rule (24.09.2026): a run with a well-formedness warning is invalid
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
