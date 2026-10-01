#!/usr/bin/env bash
# =====================================================================
#  PQ-OID4VC | Adım 7 | keşif kayıtları (ön kayıt dışı) — yalnız kesif.tsv'deki lemmalar koşulur
# =====================================================================
#  Kurallar: model/mekanizma/betik/calistir.sh ile aynı (tek konteyner, 12 GB, 600 s, pq-a07-,
#            --derivcheck-timeout=60, merdiven 1->3->5->6, iyi biçimlilik uyarısı = geçersiz).
#  Çıktı : sonuc/ham/*.{txt,meta}, sonuc/json/*.json, sonuc/ozet.csv, sonuc/karsilastirma.csv
set -u
BASE="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE" || exit 1
W=$(cygpath -m "$BASE")
IMG=pq-a02-tamarin:1.12.0
TO=600
DCT=60
export MSYS_NO_PATHCONV=1
mkdir -p sonuc/ham sonuc/json
CSV=sonuc/ozet.csv
LOG=sonuc/calistir_log.txt
[ -f "$CSV" ] || echo "kayit,varyant,lemma,sonuc,adim,sure_s,bellek_MiB,merdiven_basamagi,iyi_bicimlilik" > "$CSV"
touch "$LOG"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
log "Keşif özet denetimi:"; grep -v '^#' on_kayit.sha256 | sha256sum -c - 2>&1 | sed 's/^/    /' | tee -a "$LOG"
N=0
tamarin_run() {
  local id=$1 model=$2; shift 2
  N=$((N+1))
  while [ -n "$(docker ps -q --filter "ancestor=$IMG")" ]; do sleep 5; done
  docker run --rm --name "pq-a07-x${N}-$$" --memory=12g --memory-swap=12g \
    -v "$W:/work" -v "$(cygpath -m "$BASE/../betik"):/betik:ro" "$IMG" \
    sh /betik/ic_kosum.sh "sonuc/ham/$id" "$TO" "$model" "$@" >> "$LOG" 2>&1 < /dev/null
}
parse() {
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
{
echo "kayit,varyant,lemma,beklenen,gozlenen,uyum"
} > sonuc/karsilastirma.csv
while IFS=$'\t' read -r kayit varyant dosya bayr lbek; do
  case "$kayit" in ''|\#*) continue ;; esac
  dfl=""; [ "$bayr" != "-" ] && for fl in ${bayr//,/ }; do dfl="$dfl -D=$fl"; done
  for pair in ${lbek//;/ }; do
    l=${pair%%=*}; bek=${pair#*=}
    if ! grep -q "^${kayit},${varyant},${l}," "$CSV"; then
      for b in 1 3 5; do
        case $b in 1) ex="" ;; 3) ex="--auto-sources" ;; 5) ex="--bound=40" ;; esac
        id="${varyant}__${l}__b${b}"
        # shellcheck disable=SC2086
        tamarin_run "$id" "$dosya" --derivcheck-timeout=$DCT --prove="$l" $dfl $ex --output-json="/work/sonuc/json/${varyant}__${l}.json"
        parse "sonuc/ham/$id.txt" "sonuc/ham/$id.meta" "$l"
        wf=temiz
        if ! grep -q "All wellformedness checks were successful" "sonuc/ham/$id.txt" || grep -q "wellformedness check failed" "sonuc/ham/$id.txt"; then
          wf=uyari; RES=gecersiz_wf
        fi
        log "  $varyant $l basamak=$b -> $RES ($STEPS adım) ${WALL}s ${MEM}MiB"
        if [ "$RES" = "verified" ] || [ "$RES" = "falsified" ] || [ "$RES" = "gecersiz_wf" ]; then break; fi
      done
      [ "$RES" = "verified" ] || [ "$RES" = "falsified" ] || [ "$RES" = "gecersiz_wf" ] || { RES=kapanmadi; b=6; }
      echo "$kayit,$varyant,$l,$RES,$STEPS,$WALL,$MEM,$b,$wf" >> "$CSV"
    fi
    g=$(grep "^${kayit},${varyant},${l}," "$CSV" | head -1 | cut -d, -f4)
    gg=$(case "$g" in verified) echo V ;; falsified) echo F ;; *) echo "$g" ;; esac)
    echo "$kayit,$varyant,$l,$bek,$gg,$([ "$gg" = "$bek" ] && echo evet || echo HAYIR)" >> sonuc/karsilastirma.csv
  done
done < kesif.tsv
log "Bitti ($N konteyner)."
