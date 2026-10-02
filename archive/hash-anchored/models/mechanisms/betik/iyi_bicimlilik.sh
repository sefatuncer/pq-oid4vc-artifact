#!/usr/bin/env bash
# =====================================================================
#  PQ-OID4VC | Adım 7 görev 0 | --prove OLMADAN iyi biçimlilik denetimi
# =====================================================================
#  Kullanım (Git Bash):
#     bash model/mechanisms/betik/iyi_bicimlilik.sh <model.spthy> [BAYRAK,BAYRAK,...|-]
#  Çıktı: tek satır: rc, "All wellformedness checks were successful" sayısı, uyarı sayısı,
#         lemma listesi, varsa ayrıştırma hatası.
#  Koşum kuralı: bu betik lemma KANITLAMAZ (tamarin-prover --prove kullanılmaz).
#  Konteyner: pq-a07-wf<pid>, --rm, 4 GB, dış süre sınırı 220 s, iç süre sınırı 170 s.
#  Türetme denetimi (derivation checks) zaman aşımı: DCT ortam değişkeni, öntanımlı 60 s
#  (Tamarin öntanımlısı kısa; büyük modelde "timed out" uyarısı verir — zaman aşımı
#  uyarısı da başarısızlık sayılır, bu yüzden süre uzatılır, denetim kapatılmaz).
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
