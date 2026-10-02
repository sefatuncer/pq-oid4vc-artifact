# a10-sdjwt-002:1 — selective_disclosure_jwt 1.1.1 (affinidi-sdjwt-dart); pubspec.lock = experiment/environments/hedefler/SDJWT-002/cikti
# pub.dev anonymous; Dart analytics off. Runs with --network none.
FROM pq-a09-env-dart:1.0
WORKDIR /opt/a
COPY pubspec.yaml pubspec.lock ./
RUN dart --disable-analytics >/dev/null 2>&1; dart pub get --enforce-lockfile
COPY bin bin
RUN dart compile exe bin/adaptor.dart -o /opt/a/adaptor-bin && echo "1.1.1" > HEDEF_SURUM \
 && cat bin/*.dart | sha256sum | cut -d' ' -f1 > ADAPTOR_SHA256 \
 && printf '#!/bin/sh\nexec /opt/a/adaptor-bin "$@"\n' > /usr/local/bin/adaptor && chmod +x /usr/local/bin/adaptor
ENV HEDEF_ID=SDJWT-002
