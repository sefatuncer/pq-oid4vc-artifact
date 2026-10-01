#!/usr/bin/env bash
# =====================================================================
#  Smoke test of the Rust adapter images with self-made keys and tokens (not the battery).
#  Usage: bash smoke/run_smoke.sh <work_dir> [TARGET ...]
#    <work_dir> receives the generated keys/tokens/jobs and the raw outputs; it should be a
#    temporary folder outside this tree. The report goes to <TARGET>/evidence/smoke-test.txt.
#  Python with `cryptography` is taken from the a10-jose-083:1 image (pyjwt[crypto] venv),
#  started with --network none and only this folder and <work_dir> mounted.
# =====================================================================
set -u
cd "$(dirname "$0")/.."
export MSYS_NO_PATHCONV=1
W=${1:?work dir}; shift
TARGETS=("$@"); [ ${#TARGETS[@]} -eq 0 ] && TARGETS=(JOSE-091 JOSE-092 SDJWT-010 SDJWT-025)
mkdir -p "$W/out"
WM=$(cygpath -m "$(cd "$W" && pwd)" 2>/dev/null || (cd "$W" && pwd))
SM=$(cygpath -m "$(pwd)/smoke" 2>/dev/null || echo "$(pwd)/smoke")
PY="docker run --rm --network none --memory=4g -v $SM:/s:ro -v $WM:/w --entrypoint /e/bin/python a10-jose-083:1"
$PY /s/make_smoke.py /w
for t in "${TARGETS[@]}"; do
  img="a10-$(echo "$t" | tr 'A-Z' 'a-z'):1"
  docker run --rm --network none --memory=4g -v "$WM/v:/v:ro" -v "$WM/anahtarlar:/anahtarlar:ro" \
    -v "$WM/is:/is:ro" -v "$WM/out:/c" "$img" "$t" /is/jobs_smoke.jsonl "/c/$t.jsonl" smoke
  {
    echo "# $t smoke test (self-made keys and tokens; not the battery)"
    echo "# image: $img ($(docker image inspect --format '{{.Id}}' "$img"))"
    echo "# data:  smoke/make_smoke.py (deterministic keys from fixed labels; job list written with CRLF)"
    echo "# run:   docker run --rm --network none --memory=4g -v <w>/v:/v:ro -v <w>/anahtarlar:/anahtarlar:ro -v <w>/is:/is:ro -v <w>/out:/c $img $t /is/jobs_smoke.jsonl /c/$t.jsonl smoke"
    echo "# check: python smoke/check_smoke.py expected.json out/$t.jsonl $t"
    echo
    $PY /s/check_smoke.py /w/expected.json "/w/out/$t.jsonl" "$t"
    echo "exit=$?"
  } > "$t/evidence/smoke-test.txt" 2>&1
  echo "$t: $(tail -3 "$t/evidence/smoke-test.txt" | head -1)"
done
