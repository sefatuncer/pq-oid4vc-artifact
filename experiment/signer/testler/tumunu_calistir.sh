#!/bin/sh
# Step 9b: runs all tests FROM INSIDE THE IMAGES (without mounting the source); only the output folders and the read-only
# inputs (P4, corpus text) are mounted. Run from the PQ-OID4VC root folder in Git Bash:
#   sh experiment/signer/testler/tumunu_calistir.sh
set -e
K=$(pwd)
m() { cygpath -m "$1" 2>/dev/null || echo "$1"; }
export MSYS_NO_PATHCONV=1
S=pq-a09-signer:1.0
C=pq-a09-credgen:1.0
OUT_S=$(m "$K/experiment/signer/sonuclar")
OUT_U=$(m "$K/experiment/vector-generator")
P4=$(m "$K/referans/pilot/p4")
KORPUS=$(m "$K/spec-corpus/metin")

docker run --rm --name pq-a09-t01 -v "$OUT_S:/out" $S python /opt/pq/testler/t01_dis_vektorler.py /opt/pq/dis-vektorler /out
docker run --rm --name pq-a09-t02 -v "$OUT_S:/out" $S python /opt/pq/testler/t02_openssl_capraz.py /out
docker run --rm --name pq-a09-t03 -v "$OUT_S:/out" $S python /opt/pq/testler/t03_negatif.py /out
docker run --rm --name pq-a09-t04 -v "$OUT_S:/out" -v "$P4:/p4:ro" $S python /opt/pq/testler/t04_boyutlar.py /p4 /out
docker run --rm --name pq-a09-t05 -v "$OUT_S:/out" $S python /opt/pq/testler/t05_servis.py /opt/pq/dis-vektorler /out
# uretec: regenerate the vector set and self-verify it
docker run --rm --name pq-a09-credgen -v "$OUT_U:/work" $C
docker run --rm --name pq-a09-t10 -v "$OUT_U:/work" -v "$KORPUS:/korpus:ro" $C \
  python /opt/vector-generator/testler/t10_oz_dogrulama.py /work /korpus /work/sonuclar
docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | grep pq-a09
