# pq-a09-env-swift:1.0 — Swift environment (Linux), Step 9 task 4a (build pre-test)
# Base: official Docker Hub image, pinned by digest. apt/apk are NOT used. The Debian 13 base contains the OpenSSL 3.5 development
# files (libssl-dev): the OpenSSL requirement of Kitura/Swift-JWT on Linux is met without an extra package.
FROM swift:6.4.0-trixie@sha256:c90a484cbd45ff768e05bfdb2a73c4cc8978de0d940d8eb2cf68fcede6bad8f8
LABEL pq.adim="a09" pq.gorev="4a" pq.imaj="pq-a09-env-swift:1.0"
RUN set -eux; echo "SURUM $(swift --version 2>&1 | head -1)"; echo "SURUM sistem $(openssl version)"; \
    echo "SURUM pkg-config openssl $(pkg-config --modversion openssl)"; echo "SURUM $(git --version)"
