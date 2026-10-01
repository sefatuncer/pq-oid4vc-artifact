#!/usr/bin/env bash
# =====================================================================
#  PQ-OID4VC | Adım 7 | mekanizma kanıt koşumları (çapa 8 = 2d16592'den sonra)
# =====================================================================
#  Kullanım (Git Bash):
#     bash model/mechanisms/betik/calistir.sh            # bütün koşulacak satırlar (kaldığı yerden sürer)
#     bash model/mechanisms/betik/calistir.sh <varyant>  # tek satır
#  Girdi : on_kayit_varyantlar.tsv (çapa 8; DEĞİŞTİRİLMEZ). Koşulan roller:
#          mekanizma, kosul, tasiyici, ablasyon, 3b, 3a. 5A-kapsandi / indirgendi / betimsel koşulmaz.
#  Çıktı : sonuc/ham/<varyant>__<lemma>__b<basamak>.{txt,meta}  tam Tamarin çıktısı, süre, bellek
#          sonuc/ham/<varyant>__liste.{txt,meta}                iyi biçimlilik + lemma listesi
#          sonuc/json/<varyant>__<lemma>.json                   bulunan izler (yalnız rapor içi iz özeti;
#                                                               G09 öykünücü dışa aktarımı DEĞİL)
#          sonuc/ozet.csv, sonuc/calistir_log.txt
#  Kurallar:
#   * Tek Tamarin konteyneri; başka bir pq-a02-tamarin konteyneri varsa beklenir.
#   * --rm, --memory=12g --memory-swap=12g, timeout 600 s, ad öneki pq-a07-.
#   * --derivcheck-timeout=60 (ÖK §2H madde 2); iyi biçimlilik uyarılı koşum geçersizdir.
#   * Sonlanmama merdiveni: 1 --prove, 3 --auto-sources, 5 --bound=40, 6 "kapanmadi"
#     (2 ve 4 model düzeyindedir; modeller çapadadır, DEĞİŞTİRİLMEZ).
#   * Kaldığı yerden sürme: ozet.csv'de satırı olan (varyant, lemma) yeniden koşulmaz.
set -u
BASE="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BASE" || exit 1
W=$(cygpath -m "$BASE")
IMG=pq-a02-tamarin:1.12.0
TO=600
DCT=60
export MSYS_NO_PATHCONV=1
FILTRE="${1:-}"
mkdir -p sonuc/ham sonuc/json
CSV=sonuc/ozet.csv
LOG=sonuc/calistir_log.txt
HDR="kural,varyant,lemma,sonuc,adim,sure_s,bellek_MiB,merdiven_basamagi,iyi_bicimlilik"
[ -f "$CSV" ] || echo "$HDR" > "$CSV"
touch "$LOG"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

log "Başlangıç. Filtre='${FILTRE}'. İmaj: $IMG ($(docker image inspect --format '{{.Id}}' $IMG 2>/dev/null))"
log "Çapa denetimi (SHA256-ON-KAYIT.txt):"
grep -v '^#' SHA256-ON-KAYIT.txt | sha256sum -c - 2>&1 | sed 's/^/    /' | tee -a "$LOG"

N=0
tamarin_run() { # <id> <model> [tamarin argümanları...]
  local id=$1 model=$2; shift 2
  N=$((N+1))
  local bekledi=0
  while [ -n "$(docker ps -q --filter "ancestor=$IMG")" ]; do
    [ $bekledi -eq 0 ] && log "  başka bir Tamarin konteyneri çalışıyor; bekleniyor"
    bekledi=1; sleep 5
  done
  docker run --rm --name "pq-a07-k${N}-$$" --memory=12g --memory-swap=12g \
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
  local k=$1 v=$2 f=$3 dfl=$4 l=$5 b extra id wf
  if grep -q "^[^,]*,${v},${l}," "$CSV"; then return; fi
  for b in 1 3 5; do
    case $b in
      1) extra="" ;;
      3) extra="--auto-sources" ;;
      5) extra="--bound=40" ;;
    esac
    id="${v}__${l}__b${b}"
    # shellcheck disable=SC2086
    tamarin_run "$id" "$f" --derivcheck-timeout=$DCT --prove="$l" $dfl $extra \
      --output-json="/work/sonuc/json/${v}__${l}.json"
    parse "sonuc/ham/$id.txt" "sonuc/ham/$id.meta" "$l"
    wf=0
    grep -q "All wellformedness checks were successful" "sonuc/ham/$id.txt" || wf=1
    grep -q "wellformedness check failed" "sonuc/ham/$id.txt" && wf=1
    [ $wf -eq 1 ] && RES=gecersiz_wf
    log "  $v $l basamak=$b -> $RES ($STEPS adım) ${WALL}s ${MEM}MiB rc=$RC"
    if [ "$RES" = "gecersiz_wf" ]; then
      echo "$k,$v,$l,$RES,$STEPS,$WALL,$MEM,$b,uyari" >> "$CSV"; return
    fi
    if [ "$RES" = "verified" ] || [ "$RES" = "falsified" ]; then
      echo "$k,$v,$l,$RES,$STEPS,$WALL,$MEM,$b,temiz" >> "$CSV"; return
    fi
  done
  log "  $v $l -> KAPANMADI (basamak 6)"
  echo "$k,$v,$l,kapanmadi,$STEPS,$WALL,$MEM,6,temiz" >> "$CSV"
}

while IFS=$'\t' read -r kural varyant rol dosya bayraklar gbek lbek; do
  case "$kural" in ''|\#*) continue ;; esac
  case "$rol" in mekanizma|kosul|tasiyici|ablasyon|3b|3a) ;; *) continue ;; esac
  [ -n "$FILTRE" ] && [ "$varyant" != "$FILTRE" ] && continue
  dflags=""
  if [ "$bayraklar" != "-" ]; then
    for fl in ${bayraklar//,/ }; do dflags="$dflags -D=$fl"; done
  fi
  kural_ad=$(printf '%s' "$kural" | tr ',' ';')
  lid="${varyant}__liste"
  if [ ! -f "sonuc/ham/$lid.txt" ]; then
    log "== $varyant ($rol) $dosya bayraklar:${dflags:- yok}"
    # shellcheck disable=SC2086
    tamarin_run "$lid" "$dosya" --derivcheck-timeout=$DCT $dflags
  fi
  if ! grep -q "All wellformedness checks were successful" "sonuc/ham/$lid.txt"; then
    log "  UYARI: $varyant iyi biçimlilik denetimi başarısız"
  fi
  lemmalar=$(sed -n '/summary of summaries/,$p' "sonuc/ham/$lid.txt" \
             | sed -nE 's/^[[:space:]]+([A-Za-z0-9_]+) \((all-traces|exists-trace)\):.*/\1/p')
  if [ -z "$lemmalar" ]; then log "  HATA: $varyant lemma listesi alınamadı"; continue; fi
  for l in $lemmalar; do run_lemma "$kural_ad" "$varyant" "$dosya" "$dflags" "$l"; done
done < on_kayit_varyantlar.tsv
log "Bitti ($N konteyner)."
