# a10-jose-102:1 — jwt-kit 5.3.0 (vapor; swift-crypto/BoringSSL). SwiftPM = anonymous git clone from GitHub; Package.resolved pinned.
FROM pq-a09-env-swift:1.0
WORKDIR /opt/a
COPY Package.swift Package.resolved ./
RUN mkdir -p Sources/Adaptor && echo 'print("x")' > Sources/Adaptor/main.swift && swift package resolve && swift build -c release && rm -rf Sources
COPY Sources Sources
RUN swift build -c release && cp .build/release/Adaptor /opt/a/adaptor-bin && echo "5.3.0" > HEDEF_SURUM \
 && cat Sources/Adaptor/*.swift | sha256sum | cut -d' ' -f1 > ADAPTOR_SHA256 \
 && printf '#!/bin/sh\nexec /opt/a/adaptor-bin "$@"\n' > /usr/local/bin/adaptor && chmod +x /usr/local/bin/adaptor
ENV HEDEF_ID=JOSE-102
