#!/bin/sh
# pqdogrula curl examples. The service must be published only on 127.0.0.1 (see service/README.md).
URL=${URL:-http://127.0.0.1:18765}
D=$(dirname "$0")

curl -s "$URL/v1/saglik"; echo
# RFC 9964 Appendix A ML-DSA-65 vector
curl -s -X POST -H 'Content-Type: application/json' --data-binary @"$D/request_ML-DSA-65.json" "$URL/v1/dogrula"; echo
# composite -04 Appendix A.1 ML-DSA-65-ES256 vector
curl -s -X POST -H 'Content-Type: application/json' --data-binary @"$D/request_ML-DSA-65-ES256.json" "$URL/v1/dogrula"; echo
# batch
printf '{"istekler":[%s,%s]}' "$(cat "$D/request_ML-DSA-65.json")" "$(cat "$D/request_ML-DSA-65-ES256.json")" | \
  curl -s -X POST -H 'Content-Type: application/json' --data-binary @- "$URL/v1/dogrula/toplu"; echo
