#!/usr/bin/env bash
# =====================================================================
#  PQ-OID4VC | C3 | adaptör koşumu (KOSUCU.md çağrı biçimi): her hedef kendi imajında, ağsız, salt-okunur girdilerle
#  Kullanım: bash _belge/kos.sh <isler_dosyasi> <kosu_etiketi> <cikti_klasoru> [hedef_id ...]
#    ör.  bash _belge/kos.sh isler_dondurma_oncesi_V.jsonl oncesi kosu/oncesi JOSE-009 JOSE-083
#  Girdiler deney/kosum/ altına göre; çıktı <cikti_klasoru>/<hedef>.jsonl (kosu "oncesi" değilse <hedef>.<kosu>.jsonl)
# =====================================================================
set -eu
cd "$(dirname "$0")/../.."      # deney/kosum
export MSYS_NO_PATHCONV=1
ISLER=$1; KOSU=$2; CIK=$3; shift 3
D=$(cygpath -m "$(cd .. && pwd)" 2>/dev/null || (cd .. && pwd))   # deney
mkdir -p "$CIK"
CM=$(cygpath -m "$(cd "$CIK" && pwd)" 2>/dev/null || (cd "$CIK" && pwd))
for h in "$@"; do
  img="a10-$(echo "$h" | tr 'A-Z' 'a-z'):1"
  ad="$h.jsonl"; [ "$KOSU" = "oncesi" ] || ad="$h.$KOSU.jsonl"
  # Tek ikilide birden çok hedef taşıyan imajlarda (Go, JVM, Kotlin) hedef kimliği ilk bağımsız değişkendir; diğerlerinde de aynı sözleşme.
  t0=$(date +%s)
  docker run --rm --network none --memory=4g -v "$D/uretec/vektorler:/v:ro" -v "$D/uretec/anahtarlar:/anahtarlar:ro" \
    -v "$D/kosum:/is:ro" -v "$CM:/c" "$img" "$h" "/is/$ISLER" "/c/$ad" "$KOSU" || echo "UYARI: $h çıkış kodu $?"
  echo "$h: $(wc -l < "$CIK/$ad") satır, $(( $(date +%s) - t0 )) s"
done
