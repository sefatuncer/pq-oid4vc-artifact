# pq-a09-env-swift:1.0 — Swift ortamı (Linux), Adım 9 görev 4a (derleme ön testi)
# Taban: resmî Docker Hub imajı, özetle sabit. apt/apk KULLANILMAZ. Debian 13 tabanı OpenSSL 3.5 geliştirme
# dosyalarını (libssl-dev) içerir: Kitura/Swift-JWT'nin Linux'taki OpenSSL gereği ek paket olmadan karşılanır.
FROM swift:6.4.0-trixie@sha256:c90a484cbd45ff768e05bfdb2a73c4cc8978de0d940d8eb2cf68fcede6bad8f8
LABEL pq.adim="a09" pq.gorev="4a" pq.imaj="pq-a09-env-swift:1.0"
RUN set -eux; echo "SURUM $(swift --version 2>&1 | head -1)"; echo "SURUM sistem $(openssl version)"; \
    echo "SURUM pkg-config openssl $(pkg-config --modversion openssl)"; echo "SURUM $(git --version)"
