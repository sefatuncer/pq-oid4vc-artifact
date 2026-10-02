# pq-a09-env-php:1.0 — PHP 8.4 + Composer environment, Step 9 task 4a (build pre-test)
# Bases: official Docker Hub images, pinned by digest. apt/apk are NOT used.
# The Alpine 3.24 base brings OpenSSL 3.5.x (the ML-DSA condition of cose-lib: PHP 8.4 + OpenSSL 3.5; inventory).
# The Composer binary is copied from the official composer image; BusyBox `unzip` is used for unzipping.
FROM composer:2.10.3@sha256:9715c7f69044da2a212a5fbde29ee7da24e364d426560ae6367b060236f847d7 AS composer
FROM php:8.4-cli-alpine3.24@sha256:de082dce8399ed408c47a303ac7f126de659088b403d791cefc81a7b707ea0c1
LABEL pq.adim="a09" pq.gorev="4a" pq.imaj="pq-a09-env-php:1.0"
COPY --from=composer /usr/bin/composer /usr/bin/composer
ENV COMPOSER_ALLOW_SUPERUSER=1 COMPOSER_NO_INTERACTION=1 COMPOSER_NO_AUDIT=1 COMPOSER_CACHE_DIR=/tmp/composer-cache
RUN set -eux; echo "SURUM $(php -v | head -1)"; echo "SURUM $(composer --version 2>/dev/null)"; \
    echo "SURUM php-openssl $(php -r 'echo OPENSSL_VERSION_TEXT;')"; echo "SURUM alpine $(cat /etc/alpine-release)"; \
    echo "SURUM modüller $(php -m | grep -v '^\[' | tr '\n' ' ')"
