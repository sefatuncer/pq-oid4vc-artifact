# C3 adapters (Rust): one image per target.
#   docker build --build-arg TARGET=JOSE-091 -t a10-jose-091:1 -f Dockerfile .
# Library versions are fixed by <TARGET>/Cargo.toml (`=` pins) and <TARGET>/Cargo.lock
# (built with --locked). Crates are downloaded anonymously from crates.io during the build;
# the adapter itself runs with --network none.
FROM pq-a09-env-rust:1.0 AS build
ARG TARGET
WORKDIR /a
COPY common /a/common
COPY ${TARGET}/Cargo.toml ${TARGET}/Cargo.lock /a/t/
COPY ${TARGET}/src /a/t/src
RUN test -n "${TARGET}" \
 && cd /a/t \
 && cargo build --release --locked \
 && cp target/release/adapter /a/adapter \
 && cargo tree --locked --offline -e normal > /a/deps.txt \
 && sha256sum Cargo.lock > /a/lock.sha256

FROM pq-a09-env-rust:1.0
ARG TARGET
LABEL pq.adim="a10" pq.hedef="${TARGET}" pq.imaj="a10-adapter-rust"
COPY --from=build /a/adapter /a/deps.txt /a/lock.sha256 /a/
COPY --from=build /a/t/Cargo.toml /a/t/Cargo.lock /a/t/src/main.rs /a/src/
COPY --from=build /a/common/adapter_common.rs /a/src/
ENTRYPOINT ["/a/adapter"]
