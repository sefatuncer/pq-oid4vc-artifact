#!/bin/sh
# =====================================================================
#  PQ-OID4VC | Step 7 | a single Tamarin call inside the container (copy of models/tamarin/betik/ic_kosum.sh)
# =====================================================================
#  Usage (inside the container, /work = models/mechanisms):
#     sh /work/betik/ic_kosum.sh <output_prefix> <timeout_s> <model_relative_path> [tamarin arguments...]
#  Writes: /work/<output_prefix>.txt  (complete Tamarin output)
#          /work/<output_prefix>.meta (rc, wall-clock duration, cgroup memory peak)
#  Memory peak: /sys/fs/cgroup/memory.peak (the whole container; Maude included).
#  Since the container is started for a single call, the peak value belongs to this call.
out=$1; to=$2; f=$3; shift 3
s=$(date +%s.%N)
timeout "$to" tamarin-prover "$@" "/work/$f" > "/work/$out.txt" 2>&1
rc=$?
e=$(date +%s.%N)
peak=$(cat /sys/fs/cgroup/memory.peak 2>/dev/null || echo NA)
python3 -c '
import sys
rc, s, e, p = sys.argv[1:5]
wall = round(float(e) - float(s), 2)
mib = round(int(p) / 1048576, 1) if p.isdigit() else "NA"
print("rc=%s wall_s=%s mem_peak_MiB=%s" % (rc, wall, mib))
' "$rc" "$s" "$e" "$peak" > "/work/$out.meta"
