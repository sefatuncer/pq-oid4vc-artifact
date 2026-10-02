# pq-a09-env-go:1.0 — Go environment, Step 9 task 4a (build pre-test)
# Base: official Docker Hub image, pinned by digest. apt/apk are NOT used.
FROM golang:1.27.1-trixie@sha256:433790e515d27dc6003e847e644cc0af956985cf315c1c58a3b73ee2dd305183
LABEL pq.adim="a09" pq.gorev="4a" pq.imaj="pq-a09-env-go:1.0"
# Modules only via the Go proxy + sum.golang.org (anonymous); the toolchain is not downloaded automatically (GOTOOLCHAIN=local).
ENV GOPROXY=https://proxy.golang.org,direct GOSUMDB=sum.golang.org GOTOOLCHAIN=local GOFLAGS=-mod=mod
RUN set -eux; echo "SURUM $(go version)"; echo "SURUM $(git --version)"; echo "SURUM sistem $(openssl version)"; \
    echo "SURUM stdlib crypto/mldsa: $(test -d /usr/local/go/src/crypto/mldsa && echo var || echo yok)"
