#!/bin/sh
# Step 6 | runs the Python scripts in the pq-a02-solver:1.0 container (Git Bash). Name prefix: pq-a06-.
# Mounts: this folder -> /kat (writable; only ornekler/ and sonuc/ are written)
#         models/asp -> /asp                          (READ ONLY; single core: cekirdek.lp)
#         models/known-answer-tests/nsurum -> /nsurum      (READ ONLY; single source of the expected values)
#         spec-corpus/metin -> /korpus, literatur/metin -> /literatur (READ ONLY; quotation check)
# Usage: ./calistir.sh <script.py> [arguments]
D="$(cd "$(dirname "$0")" && pwd)"
PROJE="$(cd "$D/../../.." && pwd)"
AD="pq-a06-$(basename "$D")-$(date +%s)-$$"
MSYS_NO_PATHCONV=1 docker run --rm --name "$AD" --memory=4g --memory-swap=4g \
  -v "$(cygpath -m "$D")":/kat \
  -v "$(cygpath -m "$PROJE/models/asp")":/asp:ro \
  -v "$(cygpath -m "$PROJE/model/known-answer-tests/nsurum")":/nsurum:ro \
  -v "$(cygpath -m "$PROJE/spec-corpus/metin")":/korpus:ro \
  -v "$(cygpath -m "$PROJE/literatur/metin")":/literatur:ro \
  -w /kat -e PYTHONHASHSEED=0 -e PYTHONIOENCODING=utf-8 pq-a02-solver:1.0 python "$@"
