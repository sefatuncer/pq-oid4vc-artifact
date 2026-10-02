#!/usr/bin/env bash
# =====================================================================
#  PQ-OID4VC | Step 5B abstraction sampling (PR §4.18) | instance run
# =====================================================================
#  Usage (Git Bash):  bash models/sampling/teknik-kapi/betik/calistir.sh [satir_id]
#  Input : ceviri_plani.tsv (output of cevir.py; fixed before the run with on_ceviri.sha256)
#  Output: ham/<satir_id>__<lemma>__b<step>.{txt,meta}   complete Tamarin output, duration and memory
#          ham/<satir_id>__liste.{txt,meta}                   well-formedness and lemma list
#          json/<satir_id>__<lemma>.json                      traces (--output-json)
#          tamarin_ham.csv, calistir_log.txt
#  Rules:
#   * One Tamarin container: wait if another pq-a02-tamarin container is running.
#   * Every call: --rm, --memory=12g --memory-swap=12g, timeout 600 s, name prefix pq-a5b-.
#   * --derivcheck-timeout=60 (the default time gives a timeout warning on large models).
#   * A run with a well-formedness warning is invalid ("gecersiz_wf").
#   * Non-termination ladder (the same as models/tamarin/betik/calistir.sh): 1 --prove, 3 --auto-sources,
#     5 --bound=40, 6 "kapanmadi". Steps 2 and 4 are at model level (the translation is not changed).
#   * The ASP prediction is NOT READ in this script; the comparison is made with karsilastir.py after the run.
#   * Correction (01.10.2026): a run killed at the memory limit (rc=137) or by the timeout has no summary, so it was
#     recorded as "gecersiz_wf" and the ladder stopped. Well-formedness is checked by the separate __liste run of
#     each model. Such a run is now recorded as "bellek" / "timeout" and the ladder continues, as pre-registered.
#   * Targeted rerun: ADIMLAR="3 5" bash betik/calistir.sh <satir_id> <lemma>  (replaces only that row)
set -u
BASE="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BASE" || exit 1
W=$(cygpath -m "$BASE")
IMG=pq-a02-tamarin:1.12.0
TO=600
DCT=60
export MSYS_NO_PATHCONV=1
FILTRE="${1:-}"
LEMMA_FILTRE="${2:-}"
ADIMLAR="${ADIMLAR:-1 3 5}"
mkdir -p ham json
CSV=tamarin_ham.csv
LOG=calistir_log.txt
HDR="satir_id,lemma,sonuc,adim,sure_s,bellek_MiB,merdiven_basamagi,iyi_bicimlilik"
if [ -z "$FILTRE" ] || [ ! -f "$CSV" ]; then
  echo "$HDR" > "$CSV"; : > "$LOG"
else
  grep -v "^${FILTRE},${LEMMA_FILTRE}" "$CSV" > "$CSV.tmp"; mv "$CSV.tmp" "$CSV"
fi
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

log "Başlangıç. Filtre='${FILTRE}'. İmaj: $IMG ($(docker image inspect --format '{{.Id}}' $IMG 2>/dev/null))"
log "Çeviri özeti (on_ceviri.sha256) denetimi:"
sha256sum -c on_ceviri.sha256 2>&1 | sed 's/^/    /' | tee -a "$LOG"

N=0
tamarin_run() { # <id> <model> [tamarin arguments...]
  local id=$1 model=$2; shift 2
  N=$((N+1))
  local bekledi=0
  while [ -n "$(docker ps -q --filter "ancestor=$IMG")" ]; do
    [ $bekledi -eq 0 ] && log "  başka bir Tamarin konteyneri çalışıyor; bekleniyor"
    bekledi=1; sleep 5
  done
  docker run --rm --name "pq-a5b-k${N}-$$" --memory=12g --memory-swap=12g \
    -v "$W:/work" "$IMG" sh /work/betik/ic_kosum.sh "ham/$id" "$TO" "$model" "$@" \
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

run_lemma() { # <satir_id> <model> <lemma>
  local sid=$1 f=$2 l=$3 b extra id wf
  for b in $ADIMLAR; do
    case $b in
      1) extra="" ;;
      3) extra="--auto-sources" ;;
      5) extra="--bound=40" ;;
    esac
    id="${sid}__${l}__b${b}"
    # shellcheck disable=SC2086
    tamarin_run "$id" "$f" --derivcheck-timeout=$DCT --prove="$l" $extra --output-json="/work/json/${sid}__${l}.json"
    parse "ham/$id.txt" "ham/$id.meta" "$l"
    wf=0
    if [ "$RC" = "137" ] || [ "$RES" = "timeout" ]; then
      [ "$RC" = "137" ] && RES=bellek
    else
      grep -q "All wellformedness checks were successful" "ham/$id.txt" || wf=1
    fi
    grep -q "wellformedness check failed" "ham/$id.txt" && wf=1
    if [ $wf -eq 1 ]; then RES=gecersiz_wf; fi
    log "  $sid $l basamak=$b -> $RES ($STEPS adım) ${WALL}s ${MEM}MiB rc=$RC"
    if [ "$RES" = "gecersiz_wf" ]; then
      echo "$sid,$l,$RES,$STEPS,$WALL,$MEM,$b,uyari" >> "$CSV"; return
    fi
    if [ "$RES" = "verified" ] || [ "$RES" = "falsified" ]; then
      echo "$sid,$l,$RES,$STEPS,$WALL,$MEM,$b,temiz" >> "$CSV"; return
    fi
  done
  log "  $sid $l -> KAPANMADI (basamak 6)"
  echo "$sid,$l,kapanmadi,$STEPS,$WALL,$MEM,6,temiz" >> "$CSV"
}

while IFS=$'\t' read -r sid gorev hedef tur hucre lemma dosya _rest; do
  case "$sid" in satir_id|'') continue ;; esac
  [ -n "$FILTRE" ] && [ "$sid" != "$FILTRE" ] && continue
  if [ -n "$LEMMA_FILTRE" ]; then
    log "== $sid lemma=$LEMMA_FILTRE basamaklar=$ADIMLAR (targeted rerun)"
    grep -q "All wellformedness checks were successful" "ham/${sid}__liste.txt" || log "  UYARI: iyi biçimlilik denetimi başarısız"
    run_lemma "$sid" "$dosya" "$LEMMA_FILTRE"
    continue
  fi
  log "== $sid ($gorev) hedef=$hedef tur=$tur model=$dosya lemma=$lemma"
  tamarin_run "${sid}__liste" "$dosya" --derivcheck-timeout=$DCT
  if ! grep -q "All wellformedness checks were successful" "ham/${sid}__liste.txt"; then
    log "  UYARI: iyi biçimlilik denetimi başarısız"
  fi
  run_lemma "$sid" "$dosya" executable
  run_lemma "$sid" "$dosya" "$lemma"
done < ceviri_plani.tsv
log "Bitti ($N konteyner)."
