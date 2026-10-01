#!/usr/bin/env bash
# Adım 9 görev 4a — tek hedefin kurulum/derleme ön testini koşar (davranış ölçümü DEĞİL).
# Kullanım: kos.sh <hedef-id> <imaj> [zaman_asimi_s]
# - Kilitler (IS-PLANI §3.4): pq.agir=derleme / pq.agir=tamarin / pq.olcum=1 etiketli konteyner varken başlamaz.
# - Konteyner: --rm, --memory=6g, ad pq-a09-ortam-<id>; yalnız deney/ortam/hedefler/<id> (rw) ve
#   deney/ortam/betikler/konteyner (ro) bağlanır.
set -u
ID="$1"; IMAJ="$2"; ZA="${3:-1500}"
ORTAM_WIN="C:/Users/tuncer/Desktop/Sefa/PQ-OID4VC/deney/ortam"
ORTAM="/c/Users/tuncer/Desktop/Sefa/PQ-OID4VC/deney/ortam"
AD="pq-a09-ortam-$(echo "$ID" | tr '[:upper:]' '[:lower:]')"
LOG="$ORTAM/loglar/$ID.log"
KOSU="$ORTAM/kayit/$ID.kosu.json"
[ -f "$ORTAM/hedefler/$ID/kur.sh" ] || { echo "kur.sh yok: $ID"; exit 2; }
# kilit bekleme (en çok 60 dk)
for i in $(seq 1 120); do
  M=$(docker ps -q --filter label=pq.agir=derleme; docker ps -q --filter label=pq.agir=tamarin; docker ps -q --filter label=pq.olcum=1)
  [ -z "$M" ] && break
  echo "[kos] kilit dolu, bekleniyor ($i): $(echo $M | tr '\n' ' ')"; sleep 30
done
[ -n "${M:-}" ] && { echo "[kos] kilit 60 dk boşalmadı; çıkılıyor"; exit 3; }
docker rm -f "$AD" >/dev/null 2>&1   # yalnız kendi adımızdaki artık konteyner
rm -rf "$ORTAM/hedefler/$ID/cikti"; mkdir -p "$ORTAM/hedefler/$ID/cikti"
IMAJ_ID=$(docker image inspect --format '{{.Id}}' "$IMAJ" 2>/dev/null)
BAS=$(date -u +%s); BAS_ISO=$(date -u +%Y-%m-%dT%H:%M:%SZ)
{
  echo "# hedef=$ID imaj=$IMAJ ($IMAJ_ID) baslangic=$BAS_ISO zaman_asimi=${ZA}s"
  echo "# komut: docker run --rm --name $AD --label pq.agir=derleme --memory=6g --memory-swap=6g -v hedefler/$ID:/w -v betikler/konteyner:/b:ro $IMAJ sh -c '(bash|sh) /w/kur.sh'"
} > "$LOG"
MSYS_NO_PATHCONV=1 timeout --kill-after=30 "$ZA" docker run --rm --name "$AD" \
  --label pq.agir=derleme --label pq.adim=a09-ortam \
  --memory=6g --memory-swap=6g \
  -e HEDEF_ID="$ID" \
  -v "$ORTAM_WIN/hedefler/$ID:/w" -v "$ORTAM_WIN/betikler/konteyner:/b:ro" -w /w \
  "$IMAJ" sh -c 'if command -v bash >/dev/null 2>&1; then exec bash /w/kur.sh; else exec sh /w/kur.sh; fi' >> "$LOG" 2>&1
KOD=$?
if [ $KOD -eq 124 ] || [ $KOD -eq 137 ]; then docker stop -t 5 "$AD" >/dev/null 2>&1; echo "# ZAMAN ASIMI" >> "$LOG"; fi
BIT=$(date -u +%s); SURE=$((BIT-BAS))
echo "# cikis_kodu=$KOD sure_s=$SURE bitis=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LOG"
printf '{"id":"%s","imaj":"%s","imaj_id":"%s","baslangic":"%s","sure_s":%d,"cikis_kodu":%d}\n' \
  "$ID" "$IMAJ" "$IMAJ_ID" "$BAS_ISO" "$SURE" "$KOD" > "$KOSU"
cat "$KOSU" >> "${KOSU%.json}.jsonl"   # bütün denemeler (deneme sayısı ve toplam süre için)
echo "[kos] $ID -> cikis=$KOD sure=${SURE}s log=loglar/$ID.log"
exit $KOD
