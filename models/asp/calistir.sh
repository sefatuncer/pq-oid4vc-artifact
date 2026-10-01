#!/bin/sh
# PQ-OID4VC Adım 3 — betikleri pq-a02-solver:1.0 konteynerinde koşar (Git Bash).
# Kullanım: ./calistir.sh <betik.py> [argümanlar]   (çalışma dizini: models/asp -> /work, yazılabilir)
# Salt okunur bağlar: models/tamarin -> /tamarin, referans -> /referans, veri -> /veri,
#                     02-izlenebilirlik -> /izlenebilirlik  (yalnız okunur; yazma yalnız /work'e)
D="$(cd "$(dirname "$0")" && pwd)"
PROJE="$(cd "$D/../.." && pwd)"
AD="pq-a03-$(date +%s)-$$"
MSYS_NO_PATHCONV=1 docker run --rm --name "$AD" \
  -v "$(cygpath -m "$D")":/work \
  -v "$(cygpath -m "$PROJE/models/tamarin")":/tamarin:ro \
  -v "$(cygpath -m "$PROJE/referans")":/referans:ro \
  -v "$(cygpath -m "$PROJE/veri")":/veri:ro \
  -v "$(cygpath -m "$PROJE/traceability")":/izlenebilirlik:ro \
  -w /work -e PYTHONPATH=/work -e PYTHONHASHSEED=0 pq-a02-solver:1.0 python "$@"
