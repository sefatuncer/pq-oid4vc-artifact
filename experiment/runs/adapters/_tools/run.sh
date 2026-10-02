#!/usr/bin/env bash
# =====================================================================
#  PQ-OID4VC | C3 | adapter run (call format of RUNNER.md): every target in its own image, without network, with read-only inputs
#  Usage: bash _tools/run.sh <job_file> <run_label> <output_folder> [hedef_id ...]
#    e.g. bash _tools/run.sh jobs-prefreeze-v1.3.jsonl oncesi outputs/prefreeze-v1.3 JOSE-009 JOSE-083
#  Inputs relative to experiment/runs/; output <output_folder>/<hedef>.jsonl (<hedef>.<kosu>.jsonl if the run label is not "oncesi")
# =====================================================================
set -eu
cd "$(dirname "$0")/../.."      # experiment/runs
export MSYS_NO_PATHCONV=1
ISLER=$1; KOSU=$2; CIK=$3; shift 3
D=$(cygpath -m "$(cd .. && pwd)" 2>/dev/null || (cd .. && pwd))   # experiment folder
mkdir -p "$CIK"
CM=$(cygpath -m "$(cd "$CIK" && pwd)" 2>/dev/null || (cd "$CIK" && pwd))
# Two calling conventions: adapters with their own folder and Dockerfile take "adaptor <jobs> <out>" (run label from
# KOSU or the output file name); the shared adapters (_py, _node, _go, _jvm, _kt, _rs) take "<target> <jobs> <out> <run>".
ADIR=$(cd "$(dirname "$0")/.." && pwd)
cagri() { if [ -f "$ADIR/$1/Dockerfile" ]; then echo adaptor; else echo "$1"; fi; }
son() { if [ -f "$ADIR/$1/Dockerfile" ]; then :; else echo "$KOSU"; fi; }
for h in "$@"; do
  img="a10-$(echo "$h" | tr 'A-Z' 'a-z'):1"
  ad="$h.jsonl"; [ "$KOSU" = "oncesi" ] || ad="$h.$KOSU.jsonl"
  # In images that carry several targets in one binary (Go, JVM, Kotlin) the target id is the first argument; the others follow the same contract.
  t0=$(date +%s)
  # EXTRA_MOUNT (optional): an additional vector folder, e.g. "<abs path>/vpm-sdjwt/vectors:/v/vpm-sdjwt:ro"
  # Battery v1.4 is a byte-identical superset of v1.3 and is mounted at /v/v1.3 (adapters read /v/v1.3/MANIFEST.json).
  # BATTERY=v1.3 keeps the original v1.3 folder.
  # Limit per target and run (adapter contract section 4): C3_TARGET_TIMEOUT seconds, default 1800. On expiry the
  # container is stopped; rows it did not write are missing in this run, so the cell becomes unstable.
  cn="c3-$(echo "$h" | tr 'A-Z' 'a-z')-$KOSU-$$"
  rc=0
  timeout "${C3_TARGET_TIMEOUT:-1800}" docker run --rm --name "$cn" --network none --memory=4g -v "$D/vector-generator/vectors:/v:ro"     -v "$D/vector-generator/vectors/${BATTERY:-v1.4}:/v/v1.3:ro" ${EXTRA_MOUNT:+-v "$EXTRA_MOUNT"} -v "$D/vector-generator/keys:/anahtarlar:ro" \
    -v "$D/runs:/is:ro" -v "$CM:/c" -e KOSU="$KOSU" "$img" $(cagri "$h") "/is/$ISLER" "/c/$ad" $(son "$h") || rc=$?
  if [ "$rc" = 124 ]; then docker kill "$cn" >/dev/null 2>&1 || true; echo "WARNING: $h stopped after ${C3_TARGET_TIMEOUT:-1800} s"
  elif [ "$rc" != 0 ]; then echo "WARNING: $h exit code $rc"; fi
  echo "$h: $(wc -l < "$CIK/$ad") satır, $(( $(date +%s) - t0 )) s"
done
