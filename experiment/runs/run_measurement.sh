#!/usr/bin/env bash
# =====================================================================
#  C3 measurement run (after the pre-registration freeze only).
#  Runs jobs-v1.4.jsonl for every target three times (r1-r3), each run in a fresh container.
#  Before the first run it checks the frozen hashes of the battery, the oracle, the job list and the adapter
#  sources against FREEZE-SHA256SUMS (contract section 4, item 3). Any mismatch stops the run.
#  Usage: bash run_measurement.sh [target ...]      (default: every target in CONTROL-LABELS.csv)
#  Output: outputs/measurement/<target>.<r1|r2|r3>.jsonl, outputs/measurement/run-log.txt
# =====================================================================
set -u
cd "$(dirname "$0")" || exit 1
FROZEN=../../docs/preregistration/FREEZE-SHA256SUMS
if [ ! -f "$FROZEN" ]; then echo "no freeze manifest at $FROZEN: the pre-registration is not frozen"; exit 1; fi
( cd ../.. && sha256sum --quiet -c docs/preregistration/FREEZE-SHA256SUMS ) || { echo "frozen files changed: run aborted"; exit 1; }
T=("$@")
[ ${#T[@]} -eq 0 ] && T=($(tail -n +2 CONTROL-LABELS.csv | cut -d, -f1))
mkdir -p outputs/measurement
LOG=outputs/measurement/run-log.txt
echo "start $(date -u +%FT%TZ) targets=${#T[@]}" >> "$LOG"
for r in r1 r2 r3; do
  for t in "${T[@]}"; do
    s=$(date +%s)
    bash adapters/_tools/kos.sh jobs-v1.4.jsonl "$r" outputs/measurement "$t" >> "$LOG" 2>&1
    echo "$r $t $(( $(date +%s) - s )) s $(wc -l < outputs/measurement/$t.$r.jsonl 2>/dev/null || echo 0) rows" | tee -a "$LOG"
  done
done
echo "end $(date -u +%FT%TZ)" >> "$LOG"
