# pq-a09-env-c:1.0 — C/C++ environment, Step 9 task 4a (build pre-test)
# Base: official Docker Hub image (based on buildpack-deps: autoconf, automake, libtool, make, libssl-dev, git), pinned by digest.
# apt/apk are NOT used.
FROM gcc:15.3.0-trixie@sha256:ead103e6d03b69232962d467f3520c3f70b6718c69ff71efcc08efe9011fadb6
LABEL pq.adim="a09" pq.gorev="4a" pq.imaj="pq-a09-env-c:1.0"
RUN set -eux; echo "SURUM $(gcc --version | head -1)"; echo "SURUM $(g++ --version | head -1)"; echo "SURUM $(make --version | head -1)"; \
    echo "SURUM $(autoconf --version | head -1)"; echo "SURUM $(automake --version | head -1)"; echo "SURUM $(libtool --version | head -1)"; \
    echo "SURUM pkg-config $(pkg-config --version)"; echo "SURUM sistem $(openssl version)"; echo "SURUM $(git --version)"
