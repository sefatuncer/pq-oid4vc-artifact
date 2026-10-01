#!/bin/sh
# Adım 6 | Python betiklerini pq-a02-solver:1.0 konteynerinde koşar (Git Bash). Ad öneki: pq-a06-.
# Bağlar: bu klasör -> /kat (yazılabilir; yalnız ornekler/, sonuc/ yazılır)
#         models/asp -> /asp                          (SALT OKUNUR; tek çekirdek: cekirdek.lp)
#         model/known-answer-tests/nsurum -> /nsurum      (SALT OKUNUR; beklenen değerlerin tek kaynağı)
#         spec-corpus/metin -> /korpus, literatur/metin -> /literatur (SALT OKUNUR; alıntı denetimi)
# Kullanım: ./calistir.sh <betik.py> [argümanlar]
D="$(cd "$(dirname "$0")" && pwd)"
PROJE="$(cd "$D/../../.." && pwd)"
AD="pq-a06-$(basename "$D")-$(date +%s)-$$"
MSYS_NO_PATHCONV=1 docker run --rm --name "$AD" --memory=4g --memory-swap=4g \
  -v "$(cygpath -m "$D")":/kat \
  -v "$(cygpath -m "$PROJE/models/asp")":/asp:ro \
  -v "$(cygpath -m "$PROJE/model/known-answer-tests/nsurum")":/nsurum:ro \
  -v "$(cygpath -m "$PROJE/spec-corpus/metin")":/korpus:ro \
  -v "$(cygpath -m "$PROJE/literatur/metin")":/literatur:ro \
  -w /kat -e PYTHONHASHSEED=0 -e PYTHONIOENCODING=utf-8 pq-a02-solver:1.0 python "$@"
