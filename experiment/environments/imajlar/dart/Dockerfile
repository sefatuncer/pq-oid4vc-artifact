# pq-a09-env-dart:1.0 — Dart environment (language group "Other": SDJWT-002), Step 9 task 4a (build pre-test)
# Base: official Docker Hub image, pinned by digest. apt/apk are NOT used.
FROM dart:3.13.4-sdk@sha256:33faf91bc941466a767ce845b4bbb5d578ecd180abe5ee243e9c8c039109d215
LABEL pq.adim="a09" pq.gorev="4a" pq.imaj="pq-a09-env-dart:1.0"
# PRIVACY: Dart/pub usage analytics OFF (the configuration is written into the image).
ENV PUB_HOSTED_URL=https://pub.dev
RUN set -eux; dart --disable-analytics; echo "SURUM $(dart --version 2>&1)"; echo "SURUM analitik: $(dart --disable-analytics 2>&1 | head -1)"
