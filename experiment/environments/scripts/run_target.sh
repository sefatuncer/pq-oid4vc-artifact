#!/usr/bin/env bash
# Step 9 task 4a — runs the installation/build pre-test of a single target (NOT a behaviour measurement).
# Usage: run_target.sh <target-id> <image> [timeout_s]
# - Locks (work plan §3.4): does not start while a container labelled pq.agir=derleme / pq.agir=tamarin / pq.olcum=1 exists.
# - Container: --rm, --memory=6g, name pq-a09-ortam-<id>; only experiment/environments/targets/<id> (rw) and
#   experiment/environments/scripts/container (ro) are mounted.
set -u
ID="$1"; IMAJ="$2"; ZA="${3:-1500}"
ORTAM="$(cd "$(dirname "$0")/.." && pwd)"                      # experiment/environments
ORTAM_WIN="$(cygpath -m "$ORTAM" 2>/dev/null || echo "$ORTAM")"   # Windows form for docker -v under Git Bash
AD="pq-a09-ortam-$(echo "$ID" | tr '[:upper:]' '[:lower:]')"
LOG="$ORTAM/logs/$ID.log"
KOSU="$ORTAM/records/$ID.run.json"
[ -f "$ORTAM/targets/$ID/install.sh" ] || { echo "install.sh yok: $ID"; exit 2; }
# lock wait (at most 60 min)
for i in $(seq 1 120); do
  M=$(docker ps -q --filter label=pq.agir=derleme; docker ps -q --filter label=pq.agir=tamarin; docker ps -q --filter label=pq.olcum=1)
  [ -z "$M" ] && break
  echo "[kos] kilit dolu, bekleniyor ($i): $(echo $M | tr '\n' ' ')"; sleep 30
done
[ -n "${M:-}" ] && { echo "[kos] kilit 60 dk boşalmadı; çıkılıyor"; exit 3; }
docker rm -f "$AD" >/dev/null 2>&1   # only a leftover container with our own name
rm -rf "$ORTAM/targets/$ID/output"; mkdir -p "$ORTAM/targets/$ID/output"
IMAJ_ID=$(docker image inspect --format '{{.Id}}' "$IMAJ" 2>/dev/null)
BAS=$(date -u +%s); BAS_ISO=$(date -u +%Y-%m-%dT%H:%M:%SZ)
{
  echo "# hedef=$ID imaj=$IMAJ ($IMAJ_ID) baslangic=$BAS_ISO zaman_asimi=${ZA}s"
  echo "# komut: docker run --rm --name $AD --label pq.agir=derleme --memory=6g --memory-swap=6g -v targets/$ID:/w -v scripts/container:/b:ro $IMAJ sh -c '(bash|sh) /w/install.sh'"
} > "$LOG"
MSYS_NO_PATHCONV=1 timeout --kill-after=30 "$ZA" docker run --rm --name "$AD" \
  --label pq.agir=derleme --label pq.adim=a09-ortam \
  --memory=6g --memory-swap=6g \
  -e HEDEF_ID="$ID" \
  -v "$ORTAM_WIN/targets/$ID:/w" -v "$ORTAM_WIN/scripts/container:/b:ro" -w /w \
  "$IMAJ" sh -c 'if command -v bash >/dev/null 2>&1; then exec bash /w/install.sh; else exec sh /w/install.sh; fi' >> "$LOG" 2>&1
KOD=$?
if [ $KOD -eq 124 ] || [ $KOD -eq 137 ]; then docker stop -t 5 "$AD" >/dev/null 2>&1; echo "# ZAMAN ASIMI" >> "$LOG"; fi
BIT=$(date -u +%s); SURE=$((BIT-BAS))
echo "# cikis_kodu=$KOD sure_s=$SURE bitis=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LOG"
printf '{"id":"%s","imaj":"%s","imaj_id":"%s","baslangic":"%s","sure_s":%d,"cikis_kodu":%d}\n' \
  "$ID" "$IMAJ" "$IMAJ_ID" "$BAS_ISO" "$SURE" "$KOD" > "$KOSU"
cat "$KOSU" >> "${KOSU%.json}.jsonl"   # all attempts (for the number of attempts and the total time)
echo "[kos] $ID -> cikis=$KOD sure=${SURE}s log=logs/$ID.log"
exit $KOD
