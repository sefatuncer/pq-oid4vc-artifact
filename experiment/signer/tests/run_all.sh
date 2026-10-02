#!/bin/sh
# Step 9b: runs all tests FROM INSIDE THE IMAGES (without mounting the source); only the output folders and the read-only
# inputs (P4, corpus text) are mounted. Run from the PQ-OID4VC root folder in Git Bash:
#   sh experiment/signer/tests/run_all.sh
set -e
K=$(pwd)
m() { cygpath -m "$1" 2>/dev/null || echo "$1"; }
export MSYS_NO_PATHCONV=1
S=pq-a09-signer:1.0
C=pq-a09-credgen:1.0
OUT_S=$(m "$K/experiment/signer/results")
OUT_U=$(m "$K/experiment/vector-generator")
P4=$(m "$K/referans/pilot/p4")
KORPUS=$(m "$K/spec-corpus/metin")

docker run --rm --name pq-a09-t01 -v "$OUT_S:/out" $S python /opt/pq/tests/t01_external_vectors.py /opt/pq/external-vectors /out
docker run --rm --name pq-a09-t02 -v "$OUT_S:/out" $S python /opt/pq/tests/t02_openssl_cross.py /out
docker run --rm --name pq-a09-t03 -v "$OUT_S:/out" $S python /opt/pq/tests/t03_negative.py /out
docker run --rm --name pq-a09-t04 -v "$OUT_S:/out" -v "$P4:/p4:ro" $S python /opt/pq/tests/t04_sizes.py /p4 /out
docker run --rm --name pq-a09-t05 -v "$OUT_S:/out" $S python /opt/pq/tests/t05_service.py /opt/pq/external-vectors /out
# generator: regenerate the vector set and self-verify it
docker run --rm --name pq-a09-credgen -v "$OUT_U:/work" $C
docker run --rm --name pq-a09-t10 -v "$OUT_U:/work" -v "$KORPUS:/korpus:ro" $C \
  python /opt/vector-generator/tests/t10_self_verification.py /work /korpus /work/results
docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | grep pq-a09
