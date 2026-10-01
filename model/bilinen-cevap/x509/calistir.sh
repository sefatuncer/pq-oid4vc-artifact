#!/bin/sh
# Adım 6 | Python betiklerini pq-a02-solver:1.0 konteynerinde koşar (Git Bash). Ad öneki: pq-a06-.
# Bağlar: bu klasör -> /kat (yazılabilir; yalnız ornekler/, sonuc/ yazılır)
#         model/asp -> /asp                          (SALT OKUNUR; tek çekirdek: cekirdek.lp)
#         model/bilinen-cevap/nsurum -> /nsurum      (SALT OKUNUR; beklenen değerlerin tek kaynağı)
#         01-korpus/metin -> /korpus, literatur/metin -> /literatur (SALT OKUNUR; alıntı denetimi)
# Kullanım: ./calistir.sh <betik.py> [argümanlar]
D="$(cd "$(dirname "$0")" && pwd)"
PROJE="$(cd "$D/../../.." && pwd)"
AD="pq-a06-$(basename "$D")-$(date +%s)-$$"
MSYS_NO_PATHCONV=1 docker run --rm --name "$AD" --memory=4g --memory-swap=4g \
  -v "$(cygpath -m "$D")":/kat \
  -v "$(cygpath -m "$PROJE/model/asp")":/asp:ro \
  -v "$(cygpath -m "$PROJE/model/bilinen-cevap/nsurum")":/nsurum:ro \
  -v "$(cygpath -m "$PROJE/01-korpus/metin")":/korpus:ro \
  -v "$(cygpath -m "$PROJE/literatur/metin")":/literatur:ro \
  -w /kat -e PYTHONHASHSEED=0 -e PYTHONIOENCODING=utf-8 pq-a02-solver:1.0 python "$@"
