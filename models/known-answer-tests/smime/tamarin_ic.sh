#!/bin/sh
# Step 6 | a single Tamarin call inside the container (the same measurement format as ic_kosum.sh of the Tamarin work).
# Usage (inside the container): sh /kat/tamarin_ic.sh <output_prefix> <timeout_s> <model_path> [tamarin arguments...]
# Writes: <output_prefix>.txt (complete Tamarin output), <output_prefix>.meta (rc, wall time, cgroup memory peak)
out=$1; to=$2; f=$3; shift 3
s=$(date +%s.%N)
timeout "$to" tamarin-prover "$@" "$f" > "$out.txt" 2>&1
rc=$?
e=$(date +%s.%N)
peak=$(cat /sys/fs/cgroup/memory.peak 2>/dev/null || echo NA)
python3 -c '
import sys
rc, s, e, p = sys.argv[1:5]
wall = round(float(e) - float(s), 2)
mib = round(int(p) / 1048576, 1) if p.isdigit() else "NA"
print("rc=%s wall_s=%s mem_peak_MiB=%s" % (rc, wall, mib))
' "$rc" "$s" "$e" "$peak" > "$out.meta"
