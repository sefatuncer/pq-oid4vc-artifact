#!/usr/bin/env bash
# =====================================================================
#  PQ-OID4VC | Step 7 task 0 | well-formedness check WITHOUT --prove
# =====================================================================
#  Usage (Git Bash):
#     bash models/mechanisms/betik/iyi_bicimlilik.sh <model.spthy> [FLAG,FLAG,...|-]
#  Output: one line: rc, number of "All wellformedness checks were successful", number of warnings,
#         lemma list, a parse error if any.
#  Run rule: this script PROVES NO lemma (tamarin-prover --prove is not used).
#  Container: pq-a07-wf<pid>, --rm, 4 GB, outer time limit 220 s, inner time limit 170 s.
#  Timeout of the derivation checks: environment variable DCT, default 60 s
#  (the Tamarin default is short; a large model gives a "timed out" warning — a timeout
#  warning also counts as a failure, so the time is extended and the check is not disabled).
set -u
BASE="$(cd "$(dirname "$0")/.." && pwd)"
W=$(cygpath -m "$BASE")
f=$1; fl=${2:--}
d=""
if [ "$fl" != "-" ]; then for x in ${fl//,/ }; do d="$d -D=$x"; done; fi
export MSYS_NO_PATHCONV=1
out=$(timeout 220 docker run --rm --name "pq-a07-wf$$" --memory=4g --memory-swap=4g \
      -v "$W:/work" pq-a02-tamarin:1.12.0 \
      sh -c "cd /work/modeller && timeout 170 tamarin-prover --derivcheck-timeout=${DCT:-60} $d $f 2>&1" < /dev/null)
rc=$?
ok=$(printf '%s\n' "$out" | grep -c "All wellformedness checks were successful")
bad=$(printf '%s\n' "$out" | grep -c "wellformedness check failed")
err=$(printf '%s\n' "$out" | grep -iE "unexpected|parse error|error:" | head -3 | tr '\n' ' ')
lem=$(printf '%s\n' "$out" | sed -n '/summary of summaries/,$p' \
      | sed -nE 's/^[[:space:]]+([A-Za-z0-9_]+) \((all-traces|exists-trace)\):.*/\1/p' | tr '\n' ' ')
echo "$f [$fl] rc=$rc wf_ok=$ok wf_uyari=$bad lemmalar: $lem${err:+ | HATA: $err}"
