#!/usr/bin/env bash
# pq-a09-analiz (Step 9, task 9): build the image, run the synthetic tests twice (in two fresh containers),
# run the sample synthetic analysis twice, compare the outputs bit for bit, write SHA256SUMS.
#
# Usage (from the repository root or anywhere):  bash experiment/statistics/run_all.sh [--insa-yok]
#   --insa-yok: do not build the image, use the existing pq-a09-analiz:1.0
# Runs in Git Bash (Windows) and on Linux. Containers: pq-a09-analiz-*, always --rm, --memory=4g, --network none.
# Never run docker image/system prune or bulk deletion. This script deletes NO image and NO container.
set -euo pipefail

BURASI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAJ="pq-a09-analiz:1.0"
SONUC="$BURASI/results"
KAYIT="$BURASI/records"
mkdir -p "$SONUC" "$KAYIT"

# Windows Git Bash: Windows path for docker -v; turn off MSYS path conversion
yol() { if command -v cygpath >/dev/null 2>&1; then cygpath -w "$1"; else echo "$1"; fi; }
export MSYS_NO_PATHCONV=1
KOS=(docker run --rm --memory=4g --network none)

echo "== 0. Image list at start (images of this study and its base image only)"
docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | grep -E '^(pq-|python:)' | sort > "$KAYIT/docker_images_before.txt" || true

if [[ "${1:-}" != "--insa-yok" ]]; then
  echo "== 1. Build: $IMAJ (base image pinned by digest; pip --require-hashes)"
  docker build -t "$IMAJ" "$(yol "$BURASI")" 2>&1 | tee "$KAYIT/build.log" | tail -5
fi
docker image inspect "$IMAJ" --format '{{.Id}}' | tee "$KAYIT/image_id.txt"
"${KOS[@]}" --name pq-a09-analiz-surum "$IMAJ" python -m c3istat surum > "$KAYIT/versions.json"

echo "== 2. Synthetic tests: two fresh containers"
for i in 1 2; do
  rm -rf "$SONUC/test$i"; mkdir -p "$SONUC/test$i"
  "${KOS[@]}" --name "pq-a09-analiz-test$i" -v "$(yol "$SONUC/test$i")":/cikti "$IMAJ" \
    python /opt/c3istat/synthetic-tests/run_tests.py --cikti /cikti 2>&1 | tee "$SONUC/test$i/console.log" | tail -25
done
cmp "$SONUC/test1/test_summary.json" "$SONUC/test2/test_summary.json" && echo "test summaries byte-identical"

echo "== 3. Sample synthetic input (deterministic generator) and analysis: two fresh containers"
rm -rf "$SONUC/sample_input"; mkdir -p "$SONUC/sample_input"
"${KOS[@]}" --name pq-a09-analiz-uret -v "$(yol "$SONUC/sample_input")":/cikti "$IMAJ" \
  python /opt/c3istat/synthetic-tests/make_sample_data.py /cikti
cmp "$SONUC/sample_input/sample_n31_synthetic.json" "$BURASI/synthetic-tests/data/sample_n31_synthetic.json" \
  && echo "sample input byte-identical to the copy in the repository"
for i in 1 2; do
  rm -rf "$SONUC/sample_analysis$i"; mkdir -p "$SONUC/sample_analysis$i"
  "${KOS[@]}" --name "pq-a09-analiz-kosu$i" -v "$(yol "$SONUC/sample_input")":/girdi:ro \
    -v "$(yol "$SONUC/sample_analysis$i")":/cikti "$IMAJ" \
    python -m c3istat analiz --girdi /girdi/sample_n31_synthetic.json --cikti /cikti
done
rm -rf "$SONUC/sample_analysis_csv"; mkdir -p "$SONUC/sample_analysis_csv"
"${KOS[@]}" --name pq-a09-analiz-kosucsv -v "$(yol "$SONUC/sample_input")":/girdi:ro \
  -v "$(yol "$SONUC/sample_analysis_csv")":/cikti "$IMAJ" \
  python -m c3istat analiz --girdi /girdi/sample_n31_synthetic_targets.csv \
    --vakalar /girdi/sample_n31_synthetic_cases.csv --cikti /cikti
for f in sonuc.json sonuc.md karsilastirma.json; do
  cmp "$SONUC/sample_analysis1/$f" "$SONUC/sample_analysis2/$f" && echo "$f: byte-identical in two containers"
done
( cd "$SONUC" && sha256sum sample_analysis1/sonuc.json sample_analysis2/sonuc.json ) | tee "$SONUC/sample_analysis_sha256.txt"

echo "== 4. SHA256SUMS (files to be frozen)"
( cd "$BURASI" && sha256sum Dockerfile run_all.sh SCHEMA.md .dockerignore scripts/requirements.txt \
    scripts/c3istat/*.py synthetic-tests/*.py synthetic-tests/data/*.json synthetic-tests/data/*.csv \
    sources/NEWCOMBE-SOURCE.md ) > "$BURASI/SHA256SUMS"
cat "$BURASI/SHA256SUMS"

echo "== 5. Image list at end (this script deletes no image)"
docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | grep -E '^(pq-|python:)' | sort > "$KAYIT/docker_images_after.txt" || true
diff "$KAYIT/docker_images_before.txt" "$KAYIT/docker_images_after.txt" || true
