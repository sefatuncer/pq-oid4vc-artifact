#!/usr/bin/env bash
# =====================================================================
#  PQ-OID4VC | C3 | yürütücü adaptörlerinin imajlarını kurar (sürümler burada ve derleme dosyalarında sabit)
#  Kullanım: bash _tools/kur.sh [hedef_id]   (run from experiment/runs/adapters)
#  Yardımcı çalışmanın hedefleri kendi klasörlerindeki Dockerfile ile kurulur (<hedef>/Dockerfile → a10-<hedef>:1).
# =====================================================================
set -eu
cd "$(dirname "$0")/.."
export MSYS_NO_PATHCONV=1
H="${1:-}"
k() { [ -z "$H" ] || [ "$H" = "$1" ]; }
im() { echo "a10-$(echo "$1" | tr 'A-Z' 'a-z'):1"; }
for p in "JOSE-083|pyjwt[crypto]==2.15.0" "JOSE-084|python-jose[cryptography]==3.5.0" "SDJWT-018|sd-jwt==0.10.4"; do
  h=${p%%|*}; k "$h" && docker build -q --build-arg PAKET="${p#*|}" -t "$(im "$h")" -f _py/Dockerfile _py
done
for p in "JOSE-009|jose@6.2.12" "JOSE-065|jsonwebtoken@9.0.3" "COSE-014|cose-js@0.9.0" "SDJWT-015|@sd-jwt/core@0.21.0"; do
  h=${p%%|*}; k "$h" && docker build -q --build-arg PAKET="${p#*|}" -t "$(im "$h")" -f _node/Dockerfile _node
done
if k JOSE-033 || k JOSE-034 || k COSE-034; then docker build -q -t a10-go:1 _go; for h in JOSE-033 JOSE-034 COSE-034; do docker tag a10-go:1 "$(im $h)"; done; fi
if k JOSE-052 || k JOSE-055 || k SDJWT-004; then docker build -q -t a10-jvm:1 _jvm; for h in JOSE-052 JOSE-055 SDJWT-004; do docker tag a10-jvm:1 "$(im $h)"; done; fi
if k COSE-001; then (cd _kt && sh derle.sh cose && docker build -q --build-arg T=cose -t a10-cose-001:1 .); fi
if k SDJWT-001; then (cd _kt && sh derle.sh sdjwt && docker build -q --build-arg T=sdjwt -t a10-sdjwt-001:1 .); fi
