# pq-a09-env-node:1.0 — JS/TS environment (Node LTS), Step 9 task 4a (build pre-test)
# Base: official Docker Hub image, pinned by digest. apt/apk are NOT used (work plan §3.3).
FROM node:24.21.0-trixie@sha256:be40f6a87b9b22215ddb20da0a2320a5c6d583fe3ee3b0024d9fa4f05b40c8fd
LABEL pq.adim="a09" pq.gorev="4a" pq.imaj="pq-a09-env-node:1.0"
# Only the official npm registry (anonymous); update notification, funding and audit requests off.
ENV NPM_CONFIG_REGISTRY=https://registry.npmjs.org/ \
    NPM_CONFIG_UPDATE_NOTIFIER=false NPM_CONFIG_FUND=false NPM_CONFIG_AUDIT=false \
    NPM_CONFIG_LOGLEVEL=warn
RUN set -eux; node --version; npm --version; node -p "'node-openssl ' + process.versions.openssl"; openssl version; \
    git --version; python3 --version; gcc --version | head -1
