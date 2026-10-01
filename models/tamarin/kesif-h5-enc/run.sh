#!/bin/sh
# Runs the exploratory encrypted-response variants of the H5 model (Tamarin 1.12.0, 4 GB, 600 s each).
cd "$(dirname "$0")"
W=$(cygpath -m "$(pwd)" 2>/dev/null || pwd)
grep -v '^#' EXPECTED.tsv | while IFS="$(printf '\t')" read -r v flags exp; do
  D=""; [ "$flags" != "(none)" ] && D=$(echo "$flags" | tr ',' '\n' | sed 's/^/-D=/' | tr '\n' ' ')
  MSYS_NO_PATHCONV=1 docker run --rm --name "pq-h5enc-$v" --memory=4g --memory-swap=4g -v "$W:/work" pq-a02-tamarin:1.12.0 \
    sh -c "cd /work && timeout 600 tamarin-prover --derivcheck-timeout=60 $D --prove R6_h5_enc.spthy > $v.txt 2>&1; echo rc=\$? >> $v.txt" < /dev/null
  echo "== $v ($flags) wf=$(grep -c 'All wellformedness checks were successful' $v.txt)"
  sed -n '/summary of summaries/,$p' "$v.txt" | grep -E "verified|falsified|incomplete" | sed 's/^ */   /'
done
