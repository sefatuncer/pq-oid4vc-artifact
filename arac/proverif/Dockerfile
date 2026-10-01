# Adım 2b — ProVerif 2.05: resmî kaynak arşivinden arayüzsüz (-nointeract) derleme.
# lablgtk/GTK gerekmez; opam depext'in izinsiz paket çekmesi sorunu yok. Kaynak SHA-256: indir/kaynak.sha256
FROM python:3.11-slim@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534 AS build
RUN apt-get update && apt-get install -y --no-install-recommends ocaml-nox ocamlbuild ocaml-findlib make gcc libc6-dev \
 && rm -rf /var/lib/apt/lists/*
COPY indir/proverif2.05.tar.gz /tmp/
RUN cd /tmp && tar -xzf proverif2.05.tar.gz && cd proverif2.05 && ./build -nointeract && ./proverif -help 2>&1 | head -1

FROM python:3.11-slim@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534
COPY --from=build /tmp/proverif2.05/proverif /usr/local/bin/proverif
COPY --from=build /tmp/proverif2.05/cryptoverif.pvl /opt/proverif/
WORKDIR /work
