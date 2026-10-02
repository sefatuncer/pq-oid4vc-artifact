#!/usr/bin/env bash
# =====================================================================
#  PQ-OID4VC | PR §2H item 3 | Ö3 τ-waste cells: R6 / R6h5 Tamarin instances
# =====================================================================
#  Input : ornekler.tsv (fixed before the run with on_kayit.sha256), modeller/R6_*.spthy (byte-identical copy)
#  Output: sonuc/ham/*.{txt,meta}, sonuc/ozet.csv, sonuc/karsilastirma.csv
#  Rules: the same as models/mechanisms/betik/calistir.sh (one container, 12 GB, 600 s, pq-a07-,
#            --derivcheck-timeout=60, ladder 1->3->5->6, well-formedness warning = invalid).
set -u
BASE="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE" || exit 1
W=$(cygpath -m "$BASE")
IMG=pq-a02-tamarin:1.12.0
TO=600
DCT=60
export MSYS_NO_PATHCONV=1
mkdir -p sonuc/ham
CSV=sonuc/ozet.csv
LOG=sonuc/calistir_log.txt
echo "hucre,sablon,bayraklar,lemma,sonuc,adim,sure_s,bellek_MiB,merdiven_basamagi,iyi_bicimlilik" > "$CSV"
: > "$LOG"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
log "Çeviri/beklenti özeti denetimi:"; sha256sum -c on_kayit.sha256 2>&1 | sed 's/^/    /' | tee -a "$LOG"
N=0
tamarin_run() { # <id> <model> [args]
  local id=$1 model=$2; shift 2
  N=$((N+1))
  while [ -n "$(docker ps -q --filter "ancestor=$IMG")" ]; do sleep 5; done
  docker run --rm --name "pq-a07-t${N}-$$" --memory=12g --memory-swap=12g \
    -v "$W:/work" -v "$(cygpath -m "$BASE/../betik"):/betik:ro" "$IMG" \
    sh /betik/ic_kosum.sh "sonuc/ham/$id" "$TO" "modeller/$model" "$@" >> "$LOG" 2>&1 < /dev/null
}
parse() { # <txt> <meta> <lemma>
  local line
  RC=$(sed -nE 's/.*rc=([0-9]+).*/\1/p' "$2"); WALL=$(sed -nE 's/.*wall_s=([0-9.]+).*/\1/p' "$2")
  MEM=$(sed -nE 's/.*mem_peak_MiB=([0-9.NA]+).*/\1/p' "$2")
  line=$(sed -n '/summary of summaries/,$p' "$1" | grep -E "^[[:space:]]+$3 \((all-traces|exists-trace)\):" | head -1)
  STEPS=$(printf '%s' "$line" | sed -nE 's/.*\(([0-9]+) steps\).*/\1/p')
  case "$line" in
    *"falsified - "*) RES=falsified ;; *"verified ("*) RES=verified ;;
    *"analysis incomplete"*) RES=incomplete ;; *) RES=error ;;
  esac
  [ "$RC" = "124" ] && RES=timeout; [ -z "$STEPS" ] && STEPS=NA
}
while IFS=$'\t' read -r hucre sablon bayr lemma bek rol; do
  case "$hucre" in ''|\#*) continue ;; esac
  dfl=""; [ "$bayr" != "-" ] && for fl in ${bayr//,/ }; do dfl="$dfl -D=$fl"; done
  bs=${bayr//,/;}
  tag=$(printf '%s' "${sablon%.spthy}_${bayr}" | tr ',|+' '___')
  for l in executable "$lemma"; do
    if grep -q "^[^,]*,${sablon},${bs},${l}," "$CSV"; then
      grep "^[^,]*,${sablon},${bs},${l}," "$CSV" | head -1 | sed "s/^[^,]*,/${hucre},/" >> "$CSV"; continue
    fi
    for b in 1 3 5; do
      case $b in 1) ex="" ;; 3) ex="--auto-sources" ;; 5) ex="--bound=40" ;; esac
      id="${tag}__${l}__b${b}"
      # shellcheck disable=SC2086
      tamarin_run "$id" "$sablon" --derivcheck-timeout=$DCT --prove="$l" $dfl $ex
      parse "sonuc/ham/$id.txt" "sonuc/ham/$id.meta" "$l"
      wf=temiz
      if ! grep -q "All wellformedness checks were successful" "sonuc/ham/$id.txt" || grep -q "wellformedness check failed" "sonuc/ham/$id.txt"; then
        wf=uyari; RES=gecersiz_wf
      fi
      log "  $hucre $sablon [$bayr] $l basamak=$b -> $RES ($STEPS adım) ${WALL}s ${MEM}MiB"
      if [ "$RES" = "verified" ] || [ "$RES" = "falsified" ] || [ "$RES" = "gecersiz_wf" ]; then break; fi
    done
    [ "$RES" = "verified" ] || [ "$RES" = "falsified" ] || [ "$RES" = "gecersiz_wf" ] || { RES=kapanmadi; b=6; }
    echo "$hucre,$sablon,$bs,$l,$RES,$STEPS,$WALL,$MEM,$b,$wf" >> "$CSV"
  done
done < ornekler.tsv
# comparison (target lemma): expected ornekler.tsv, observed ozet.csv
{
  echo "hucre,sablon,bayraklar,lemma,beklenen,gozlenen,uyum,executable"
  while IFS=$'\t' read -r hucre sablon bayr lemma bek rol; do
    case "$hucre" in ''|\#*) continue ;; esac
    bs=${bayr//,/;}
    g=$(grep "^${hucre},${sablon},${bs},${lemma}," "$CSV" | head -1 | cut -d, -f5)
    ex=$(grep "^${hucre},${sablon},${bs},executable," "$CSV" | head -1 | cut -d, -f5)
    gg=$(case "$g" in verified) echo V ;; falsified) echo F ;; *) echo "$g" ;; esac)
    u=$([ "$gg" = "$bek" ] && echo evet || echo HAYIR)
    echo "$hucre,$sablon,$bs,$lemma,$bek,$gg,$u,$ex"
  done < ornekler.tsv
} > sonuc/karsilastirma.csv
log "Bitti ($N konteyner)."
