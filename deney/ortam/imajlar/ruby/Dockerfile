# pq-a09-env-ruby:1.0 — Ruby ortamı, Adım 9 görev 4a (derleme ön testi)
# Taban: resmî Docker Hub imajı (tam sürüm: gcc, make, libssl-dev), özetle sabit. apt/apk KULLANILMAZ.
FROM ruby:3.4.11-trixie@sha256:da59b74df06952ff6e99b792ac7713010b8039c5989f0accaf6c97448b31d0ff
LABEL pq.adim="a09" pq.gorev="4a" pq.imaj="pq-a09-env-ruby:1.0"
ENV BUNDLE_SILENCE_ROOT_WARNING=1 BUNDLE_JOBS=4 GEM_HOST=https://rubygems.org
RUN set -eux; echo "SURUM $(ruby -v)"; echo "SURUM gem $(gem -v)"; echo "SURUM $(bundle -v)"; \
    echo "SURUM ruby-openssl $(ruby -ropenssl -e 'puts OpenSSL::OPENSSL_LIBRARY_VERSION')"; echo "SURUM $(gcc --version | head -1)"
