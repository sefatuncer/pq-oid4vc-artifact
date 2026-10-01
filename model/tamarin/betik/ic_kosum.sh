#!/bin/sh
# =====================================================================
#  PQ-OID4VC | Adım 4 | konteyner içi tek Tamarin çağrısı
# =====================================================================
#  Kullanım (konteyner içinde, /work = model/tamarin):
#     sh /work/betik/ic_kosum.sh <cikti_oneki> <zaman_asimi_s> <model_goreli_yolu> [tamarin argümanları...]
#  Yazar: /work/<cikti_oneki>.txt  (Tamarin'in tam çıktısı)
#         /work/<cikti_oneki>.meta (rc, duvar saati süresi, cgroup bellek tepesi)
#  Bellek tepesi: /sys/fs/cgroup/memory.peak (konteynerin tamamı; Maude dahil).
#  Konteyner tek çağrı için açıldığından tepe değer bu çağrıya aittir.
out=$1; to=$2; f=$3; shift 3
s=$(date +%s.%N)
timeout "$to" tamarin-prover "$@" "/work/$f" > "/work/$out.txt" 2>&1
rc=$?
e=$(date +%s.%N)
peak=$(cat /sys/fs/cgroup/memory.peak 2>/dev/null || echo NA)
python3 -c '
import sys
rc, s, e, p = sys.argv[1:5]
wall = round(float(e) - float(s), 2)
mib = round(int(p) / 1048576, 1) if p.isdigit() else "NA"
print("rc=%s wall_s=%s mem_peak_MiB=%s" % (rc, wall, mib))
' "$rc" "$s" "$e" "$peak" > "/work/$out.meta"
