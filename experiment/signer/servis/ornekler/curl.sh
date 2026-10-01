#!/bin/sh
# pqdogrula curl ornekleri. Servis yalniz 127.0.0.1'e yayinlanmis olmali (bkz. servis/README.md).
URL=${URL:-http://127.0.0.1:18765}
D=$(dirname "$0")

curl -s "$URL/v1/saglik"; echo
# RFC 9964 Ek A ML-DSA-65 vektoru
curl -s -X POST -H 'Content-Type: application/json' --data-binary @"$D/istek_ML-DSA-65.json" "$URL/v1/dogrula"; echo
# composite -04 Ek A.1 ML-DSA-65-ES256 vektoru
curl -s -X POST -H 'Content-Type: application/json' --data-binary @"$D/istek_ML-DSA-65-ES256.json" "$URL/v1/dogrula"; echo
# toplu
printf '{"istekler":[%s,%s]}' "$(cat "$D/istek_ML-DSA-65.json")" "$(cat "$D/istek_ML-DSA-65-ES256.json")" | \
  curl -s -X POST -H 'Content-Type: application/json' --data-binary @- "$URL/v1/dogrula/toplu"; echo
