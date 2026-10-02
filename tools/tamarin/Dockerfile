# Step 2 — Tamarin 1.12.0 (official binary) + Maude 3.5.1 (official binary)
# SHA-256 values of the binaries: indir/beklenen.sha256 (checked against the GitHub release digests)
FROM python:3.11-slim@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534
COPY indir/tamarin/tamarin-prover /usr/local/bin/tamarin-prover
COPY indir/maude/ /opt/maude/
RUN chmod +x /usr/local/bin/tamarin-prover /opt/maude/maude \
 && ln -s /opt/maude/maude /usr/local/bin/maude
ENV MAUDE_LIB=/opt/maude
WORKDIR /work
