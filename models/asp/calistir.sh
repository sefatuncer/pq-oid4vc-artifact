#!/bin/sh
# PQ-OID4VC Step 3 — runs the scripts in the pq-a02-solver:1.0 container (Git Bash).
# Usage: ./calistir.sh <script.py> [arguments]   (working folder: models/asp -> /work, writable)
# Read-only mounts: models/tamarin -> /tamarin, referans -> /referans, data -> /veri,
#                     traceability -> /izlenebilirlik  (read only; writes go only to /work)
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
