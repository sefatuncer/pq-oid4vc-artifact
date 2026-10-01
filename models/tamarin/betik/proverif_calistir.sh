#!/usr/bin/env bash
# =====================================================================
#  PQ-OID4VC | Adım 5A | ProVerif 2.05 ikinci görüş (R1–R5 alt kümesi)
# =====================================================================
#  Kullanım (Git Bash):  bash models/tamarin/betik/proverif_calistir.sh
#  Girdi : betik/proverif_varyantlar.tsv, modeller/proverif/*.pvt (şablon), betik/pp.awk
#  Çıktı : sonuc/proverif/uretilen/<kural>__<varyant>.pv   önişlenmiş model
#          sonuc/proverif/ham/<kural>__<varyant>.{txt,meta} ProVerif çıktısı; rc, süre, bellek
#          sonuc/proverif/ozet.csv                         sorgu başına ProVerif sonucu
#          sonuc/proverif/karsilastirma.csv, metrikler.txt (betik/proverif_degerlendir.py)
#  Kurallar: --rm, ad öneki pq-a04-, --memory=4g, timeout 600 s; başka bir Tamarin konteyneri
#  çalışıyorsa beklenir (aynı anda tek ağır iş).
set -u
BASE="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BASE" || exit 1
W=$(cygpath -m "$BASE")
IMG=pq-a02-proverif:2.05
TIMG=pq-a02-tamarin:1.12.0
TO=600
export MSYS_NO_PATHCONV=1
OUT=sonuc/proverif
mkdir -p "$OUT/uretilen" "$OUT/ham"
CSV=$OUT/ozet.csv
LOG=$OUT/log.txt
echo "kural,varyant,sira,lemma,tur,proverif_sonuc,sure_s,bellek_MiB" > "$CSV"
: > "$LOG"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

log "Başlangıç. İmaj: $IMG ($(docker image inspect --format '{{.Id}}' $IMG 2>/dev/null))"
docker run --rm --name pq-a04-pv-surum --memory=1g --memory-swap=1g "$IMG" proverif -help 2>&1 < /dev/null | head -1 | tee -a "$LOG"

N=0
while IFS=$'\t' read -r kural varyant sablon bayraklar sorgular; do
  case "$kural" in ''|\#*) continue ;; esac
  N=$((N+1))
  defs=""; [ "$bayraklar" != "-" ] && defs="$bayraklar"
  id="${kural}__${varyant}"
  pv="$OUT/uretilen/$id.pv"
  if ! awk -v DEFS="$defs" -f betik/pp.awk "modeller/proverif/$sablon" > "$pv"; then
    log "$id: önişlemci hatası"; continue
  fi
  while [ -n "$(docker ps -q --filter "ancestor=$TIMG")" ]; do sleep 5; done
  docker run --rm --name "pq-a04-pv$N" --memory=4g --memory-swap=4g -v "$W:/work" "$IMG" \
    sh /work/betik/ic_kosum_pv.sh "$OUT/ham/$id" "$TO" "$pv" < /dev/null >> "$LOG" 2>&1
  meta="$OUT/ham/$id.meta"
  rc=$(sed -nE 's/.*rc=([0-9]+).*/\1/p' "$meta")
  wall=$(sed -nE 's/.*wall_s=([0-9.]+).*/\1/p' "$meta")
  mem=$(sed -nE 's/.*mem_peak_MiB=([0-9.NA]+).*/\1/p' "$meta")
  mapfile -t res < <(grep '^RESULT' "$OUT/ham/$id.txt" | sed -E 's/.* (is true|is false|cannot be proved)\.$/\1/')
  IFS=';' read -r -a sq <<< "$sorgular"
  if [ "${#res[@]}" -ne "${#sq[@]}" ]; then
    log "$id: RESULT sayısı (${#res[@]}) sorgu sayısıyla (${#sq[@]}) uyuşmuyor; rc=$rc"
  fi
  for i in "${!sq[@]}"; do
    lemma="${sq[$i]%%:*}"; tur="${sq[$i]##*:}"
    r="${res[$i]:-yok}"
    case "$r" in
      "is true") r=true ;; "is false") r=false ;; "cannot be proved") r=cannot_be_proved ;;
    esac
    [ "$rc" = "124" ] && r=timeout
    echo "$kural,$varyant,$((i+1)),$lemma,$tur,$r,$wall,$mem" >> "$CSV"
  done
  log "$id (bayraklar: ${defs:-yok}) -> ${res[*]:-sonuç yok} | ${wall}s ${mem}MiB rc=$rc"
done < betik/proverif_varyantlar.tsv

log "ProVerif koşumları bitti ($N model). Karşılaştırma başlıyor."
docker run --rm --name pq-a04-pv-degerlendir --memory=1g --memory-swap=1g -v "$W:/work" -w /work \
  "$IMG" python3 betik/proverif_degerlendir.py 2>&1 < /dev/null | tee -a "$LOG"
log "Bitti."
