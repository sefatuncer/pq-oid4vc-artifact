#!/usr/bin/env bash
# =====================================================================
#  PQ-OID4VC | C3 | pre-freeze adapter conformance run (decision D9)
#  Every adapter image runs the conformance job list on the conformance objects of this folder, never on the battery.
#  The call is the one of adapters/_tools/run.sh (RUNNER.md §2), with the conformance objects mounted at /v.
#  Usage: bash experiment/runs/conformance/run.sh [target ...]   (default: every target of CONTROL-LABELS.csv)
#  Output: experiment/runs/conformance/outputs/<target>.jsonl
# =====================================================================
set -eu
cd "$(dirname "$0")/.."                    # experiment/runs
export MSYS_NO_PATHCONV=1
D=$(cygpath -m "$(cd .. && pwd)" 2>/dev/null || (cd .. && pwd))    # experiment folder
mkdir -p conformance/outputs
O=$(cygpath -m "$(cd conformance/outputs && pwd)" 2>/dev/null || (cd conformance/outputs && pwd))
if [ $# -eq 0 ]; then set -- $(tail -n +2 CONTROL-LABELS.csv | cut -d, -f1); fi
cagri() { if [ -f "adapters/$1/Dockerfile" ]; then echo adaptor; else echo "$1"; fi; }
son() { if [ -f "adapters/$1/Dockerfile" ]; then :; else echo conformance; fi; }
for h in "$@"; do
  img="a10-$(echo "$h" | tr 'A-Z' 'a-z'):1"
  cn="c3conf-$(echo "$h" | tr 'A-Z' 'a-z')-$$"
  rc=0
  timeout "${C3_TARGET_TIMEOUT:-1800}" docker run --rm --name "$cn" --network none --memory=4g \
    -v "$D/runs/conformance/vectors:/v:ro" -v "$D/vector-generator/keys:/anahtarlar:ro" -v "$D/runs:/is:ro" -v "$O:/c" \
    -e KOSU=conformance "$img" $(cagri "$h") /is/conformance/jobs.jsonl "/c/$h.jsonl" $(son "$h") || rc=$?
  if [ "$rc" = 124 ]; then docker kill "$cn" >/dev/null 2>&1 || true; echo "WARNING: $h stopped after ${C3_TARGET_TIMEOUT:-1800} s"
  elif [ "$rc" != 0 ]; then echo "WARNING: $h exit code $rc"; fi
  echo "$h: $(wc -l < "conformance/outputs/$h.jsonl") rows"
done
