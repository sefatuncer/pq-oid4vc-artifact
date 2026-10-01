# pq-a09-env-rust:1.0 — Rust ortamı, Adım 9 görev 4a (derleme ön testi)
# Taban: resmî Docker Hub imajı (tam sürüm: gcc, make, libssl-dev), özetle sabit. apt/apk KULLANILMAZ.
FROM rust:1.98.1-trixie@sha256:a8a5f0a1e5fe7dfe1d352591e4a1c7dd2c08fd70475cae872cf3458ba0df0546
LABEL pq.adim="a09" pq.gorev="4a" pq.imaj="pq-a09-env-rust:1.0"
# crates.io seyrek (sparse) indeks, anonim.
ENV CARGO_REGISTRIES_CRATES_IO_PROTOCOL=sparse CARGO_TERM_COLOR=never CARGO_NET_RETRY=3
RUN set -eux; echo "SURUM $(rustc --version)"; echo "SURUM $(cargo --version)"; echo "SURUM $(gcc --version | head -1)"; \
    echo "SURUM sistem $(openssl version)"; echo "SURUM pkg-config $(pkg-config --version 2>/dev/null || echo yok)"; \
    echo "SURUM cmake $(cmake --version 2>/dev/null | head -1 || echo yok)"; echo "SURUM clang $(clang --version 2>/dev/null | head -1 || echo yok)"; \
    echo "SURUM libssl-dev başlığı $(test -f /usr/include/openssl/ssl.h && echo var || echo yok)"
