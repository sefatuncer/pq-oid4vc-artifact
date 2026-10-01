#!/usr/bin/env bash
# =====================================================================
#  PQ-OID4VC | Adım 5B soyutlama örneklemesi (ÖK §4.18) | örnek koşumu
# =====================================================================
#  Kullanım (Git Bash):  bash model/sampling/teknik-kapi/betik/calistir.sh [satir_id]
#  Girdi : ceviri_plani.tsv (cevir.py çıktısı; on_ceviri.sha256 ile koşumdan önce sabitlendi)
#  Çıktı : ham/<satir_id>__<lemma>__b<basamak>.{txt,meta}   Tamarin'in tam çıktısı, süre ve bellek
#          ham/<satir_id>__liste.{txt,meta}                   iyi biçimlilik ve lemma listesi
#          json/<satir_id>__<lemma>.json                      izler (--output-json)
#          tamarin_ham.csv, calistir_log.txt
#  Kurallar:
#   * Tek Tamarin konteyneri: başka bir pq-a02-tamarin konteyneri çalışıyorsa beklenir.
#   * Her çağrı: --rm, --memory=12g --memory-swap=12g, timeout 600 s, ad öneki pq-a5b-.
#   * --derivcheck-timeout=60 (öntanımlı süre büyük modellerde zaman aşımı uyarısı verir).
#   * İyi biçimlilik uyarılı koşum geçersizdir ("gecersiz_wf").
#   * Sonlanmama merdiveni (models/tamarin/betik/calistir.sh ile aynı): 1 --prove, 3 --auto-sources,
#     5 --bound=40, 6 "kapanmadi". 2. ve 4. basamak model düzeyindedir (çeviri değiştirilmez).
#   * ASP tahmini bu betikte OKUNMAZ; karşılaştırma karsilastir.py ile koşumdan sonra yapılır.
set -u
BASE="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BASE" || exit 1
W=$(cygpath -m "$BASE")
IMG=pq-a02-tamarin:1.12.0
TO=600
DCT=60
export MSYS_NO_PATHCONV=1
FILTRE="${1:-}"
mkdir -p ham json
CSV=tamarin_ham.csv
LOG=calistir_log.txt
HDR="satir_id,lemma,sonuc,adim,sure_s,bellek_MiB,merdiven_basamagi,iyi_bicimlilik"
if [ -z "$FILTRE" ] || [ ! -f "$CSV" ]; then
  echo "$HDR" > "$CSV"; : > "$LOG"
else
  grep -v "^${FILTRE}," "$CSV" > "$CSV.tmp"; mv "$CSV.tmp" "$CSV"
fi
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

log "Başlangıç. Filtre='${FILTRE}'. İmaj: $IMG ($(docker image inspect --format '{{.Id}}' $IMG 2>/dev/null))"
log "Çeviri özeti (on_ceviri.sha256) denetimi:"
sha256sum -c on_ceviri.sha256 2>&1 | sed 's/^/    /' | tee -a "$LOG"

N=0
tamarin_run() { # <id> <model> [tamarin argümanları...]
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
  for b in 1 3 5; do
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
    grep -q "All wellformedness checks were successful" "ham/$id.txt" || wf=1
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
  log "== $sid ($gorev) hedef=$hedef tur=$tur model=$dosya lemma=$lemma"
  tamarin_run "${sid}__liste" "$dosya" --derivcheck-timeout=$DCT
  if ! grep -q "All wellformedness checks were successful" "ham/${sid}__liste.txt"; then
    log "  UYARI: iyi biçimlilik denetimi başarısız"
  fi
  run_lemma "$sid" "$dosya" executable
  run_lemma "$sid" "$dosya" "$lemma"
done < ceviri_plani.tsv
log "Bitti ($N konteyner)."
