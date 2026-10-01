# pq-a09-env-dart:1.0 — Dart ortamı ("Diğer" dil grubu: SDJWT-002), Adım 9 görev 4a (derleme ön testi)
# Taban: resmî Docker Hub imajı, özetle sabit. apt/apk KULLANILMAZ.
FROM dart:3.13.4-sdk@sha256:33faf91bc941466a767ce845b4bbb5d578ecd180abe5ee243e9c8c039109d215
LABEL pq.adim="a09" pq.gorev="4a" pq.imaj="pq-a09-env-dart:1.0"
# GİZLİLİK: Dart/pub kullanım analitiği KAPALI (yapılandırma imaja yazılır).
ENV PUB_HOSTED_URL=https://pub.dev
RUN set -eux; dart --disable-analytics; echo "SURUM $(dart --version 2>&1)"; echo "SURUM analitik: $(dart --disable-analytics 2>&1 | head -1)"
