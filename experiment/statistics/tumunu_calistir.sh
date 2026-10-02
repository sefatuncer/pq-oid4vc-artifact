#!/usr/bin/env bash
# pq-a09-analiz (Step 9, task 9): build the image, run the synthetic tests twice (in two fresh containers),
# run the sample synthetic analysis twice, compare the outputs bit for bit, write SHA256SUMS.
#
# Usage (from the repository root or anywhere):  bash experiment/statistics/tumunu_calistir.sh [--insa-yok]
#   --insa-yok: do not build the image, use the existing pq-a09-analiz:1.0
# Runs in Git Bash (Windows) and on Linux. Containers: pq-a09-analiz-*, always --rm, --memory=4g, --network none.
# Never run docker image/system prune or bulk deletion. This script deletes NO image and NO container.
set -euo pipefail

BURASI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAJ="pq-a09-analiz:1.0"
SONUC="$BURASI/sonuclar"
KAYIT="$BURASI/kayit"
mkdir -p "$SONUC" "$KAYIT"

# Windows Git Bash: Windows path for docker -v; turn off MSYS path conversion
yol() { if command -v cygpath >/dev/null 2>&1; then cygpath -w "$1"; else echo "$1"; fi; }
export MSYS_NO_PATHCONV=1
KOS=(docker run --rm --memory=4g --network none)

echo "== 0. Image list at start"
docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | sort > "$KAYIT/docker_images_once.txt"

if [[ "${1:-}" != "--insa-yok" ]]; then
  echo "== 1. Build: $IMAJ (base image pinned by digest; pip --require-hashes)"
  docker build -t "$IMAJ" "$(yol "$BURASI")" 2>&1 | tee "$KAYIT/insa.log" | tail -5
fi
docker image inspect "$IMAJ" --format '{{.Id}}' | tee "$KAYIT/imaj_kimligi.txt"
"${KOS[@]}" --name pq-a09-analiz-surum "$IMAJ" python -m c3istat surum > "$KAYIT/surum.json"

echo "== 2. Synthetic tests: two fresh containers"
for i in 1 2; do
  rm -rf "$SONUC/test$i"; mkdir -p "$SONUC/test$i"
  "${KOS[@]}" --name "pq-a09-analiz-test$i" -v "$(yol "$SONUC/test$i")":/cikti "$IMAJ" \
    python /opt/c3istat/sentetik-testler/calistir.py --cikti /cikti 2>&1 | tee "$SONUC/test$i/konsol.log" | tail -25
done
cmp "$SONUC/test1/test_ozeti.json" "$SONUC/test2/test_ozeti.json" && echo "test summaries byte-identical"

echo "== 3. Sample synthetic input (deterministic generator) and analysis: two fresh containers"
rm -rf "$SONUC/ornek_girdi"; mkdir -p "$SONUC/ornek_girdi"
"${KOS[@]}" --name pq-a09-analiz-uret -v "$(yol "$SONUC/ornek_girdi")":/cikti "$IMAJ" \
  python /opt/c3istat/sentetik-testler/ornek_veri_uret.py /cikti
cmp "$SONUC/ornek_girdi/ornek_n31_sentetik.json" "$BURASI/sentetik-testler/veri/ornek_n31_sentetik.json" \
  && echo "sample input byte-identical to the copy in the repository"
for i in 1 2; do
  rm -rf "$SONUC/ornek_analiz$i"; mkdir -p "$SONUC/ornek_analiz$i"
  "${KOS[@]}" --name "pq-a09-analiz-kosu$i" -v "$(yol "$SONUC/ornek_girdi")":/girdi:ro \
    -v "$(yol "$SONUC/ornek_analiz$i")":/cikti "$IMAJ" \
    python -m c3istat analiz --girdi /girdi/ornek_n31_sentetik.json --cikti /cikti
done
rm -rf "$SONUC/ornek_analiz_csv"; mkdir -p "$SONUC/ornek_analiz_csv"
"${KOS[@]}" --name pq-a09-analiz-kosucsv -v "$(yol "$SONUC/ornek_girdi")":/girdi:ro \
  -v "$(yol "$SONUC/ornek_analiz_csv")":/cikti "$IMAJ" \
  python -m c3istat analiz --girdi /girdi/ornek_n31_sentetik_hedefler.csv \
    --vakalar /girdi/ornek_n31_sentetik_vakalar.csv --cikti /cikti
for f in sonuc.json sonuc.md karsilastirma.json; do
  cmp "$SONUC/ornek_analiz1/$f" "$SONUC/ornek_analiz2/$f" && echo "$f: byte-identical in two containers"
done
( cd "$SONUC" && sha256sum ornek_analiz1/sonuc.json ornek_analiz2/sonuc.json ) | tee "$SONUC/ornek_analiz_sha256.txt"

echo "== 4. SHA256SUMS (files to be frozen)"
( cd "$BURASI" && sha256sum Dockerfile tumunu_calistir.sh SCHEMA.md .dockerignore betikler/requirements.txt \
    betikler/c3istat/*.py sentetik-testler/*.py sentetik-testler/veri/*.json sentetik-testler/veri/*.csv \
    kaynak/NEWCOMBE-SOURCE.md ) > "$BURASI/SHA256SUMS"
cat "$BURASI/SHA256SUMS"

echo "== 5. Image list at end (this script deletes no image)"
docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | sort > "$KAYIT/docker_images_sonra.txt"
diff "$KAYIT/docker_images_once.txt" "$KAYIT/docker_images_sonra.txt" || true
