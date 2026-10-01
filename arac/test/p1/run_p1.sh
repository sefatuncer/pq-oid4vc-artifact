#!/bin/sh
# usage: run_p1.sh <label> <timeout_s> <file> [tamarin args...]
label=$1; to=$2; f=$3; shift 3
s=$(date +%s.%N)
timeout $to tamarin-prover --prove "$@" /work/$f > /tmp/out.txt 2>&1
rc=$?
e=$(date +%s.%N)
peak=$(cat /sys/fs/cgroup/memory.peak 2>/dev/null || echo NA)
echo "=== $label rc=$rc wall_s=$(python3 -c "print(round($e-$s,2))") mem_peak_MiB=$(python3 -c "print(round(int('$peak')/1048576,1))" 2>/dev/null || echo $peak)"
sed -n '/summary of summaries/,$p' /tmp/out.txt | grep -E "lemma|verified|falsified|analysis incomplete|processing time|steps" | head -12
[ $rc -eq 124 ] && echo "TIMEOUT after ${to}s" && tail -3 /tmp/out.txt
cp /tmp/out.txt /work/out_$label.txt
