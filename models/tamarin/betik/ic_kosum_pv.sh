#!/bin/sh
# =====================================================================
#  PQ-OID4VC | Step 5A | a single ProVerif call inside the container
# =====================================================================
#  Usage (inside the container, /work = models/tamarin):
#     sh /work/betik/ic_kosum_pv.sh <output_prefix> <timeout_s> <pv_relative_path>
#  Writes: /work/<output_prefix>.txt (ProVerif output), /work/<output_prefix>.meta (rc, duration, cgroup memory peak)
out=$1; to=$2; f=$3
s=$(date +%s.%N)
timeout "$to" proverif "/work/$f" > "/work/$out.txt" 2>&1
rc=$?
e=$(date +%s.%N)
peak=$(cat /sys/fs/cgroup/memory.peak 2>/dev/null || echo NA)
python3 -c '
import sys
rc, s, e, p = sys.argv[1:5]
wall = round(float(e) - float(s), 3)
mib = round(int(p) / 1048576, 1) if p.isdigit() else "NA"
print("rc=%s wall_s=%s mem_peak_MiB=%s" % (rc, wall, mib))
' "$rc" "$s" "$e" "$peak" > "/work/$out.meta"
