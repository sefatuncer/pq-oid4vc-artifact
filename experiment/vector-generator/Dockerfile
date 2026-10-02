# pq-a09-credgen — PQ-OID4VC Step 9b: generator of SD-JWT VC / KB-JWT / TSL / OID4VP request / DPoP and test vectors
#
# Base: local pq-a09-signer:1.0 (experiment/signer; python:3.11-slim@sha256:9534e5a8...; OpenSSL 3.5.7;
#        cryptography 50.0.1). Since it is a local image it is referenced by tag, not by digest; the id of the image
#        used is recorded in the README. NO additional packages.
# Versions: 1.0 = the build that produced v1; 1.1 = + uretec/v11.py (v1.1) and boyut_dpop.py;
#           1.2 = + uretec/v12.py (v1.2) and esleme.py (BATARYA-ESLEME.md).
#           1.3 = + uretec/cbor.py, cose.py (COSE_Sign/COSE_Sign1), v13.py (v1.3: COSE + L4c old issuer),
#                 the v1.3 sections of esleme.py, tests t10_cose.py and t12_cose.py. The generation code of v1, v1.1, v1.2 did not change.
# Build:   docker build -t pq-a09-credgen:1.3 experiment/vector-generator
# Generation (v1.3; the frozen v1, v1.1, v1.2 and anahtarlar/v1 are mounted read-only):
#   docker run --rm --name pq-a09-credgen -v <kok>:/work -v <kok>/vektorler/v1:/work/vektorler/v1:ro
#     -v <kok>/vektorler/v1.1:/work/vektorler/v1.1:ro -v <kok>/vektorler/v1.2:/work/vektorler/v1.2:ro
#     -v <kok>/anahtarlar/v1:/work/anahtarlar/v1:ro pq-a09-credgen:1.3
# Mapping: ... -v <project>/00-on-kayit:/onkayit:ro pq-a09-credgen:1.3 python -m uretec.esleme /work /onkayit/ON-KAYIT-TASLAK.md
# Earlier sets: python -m uretec.uret /work (v1), python -m uretec.v11 /work (v1.1), python -m uretec.v12 /work (v1.2)
FROM pq-a09-signer:1.0

LABEL org.opencontainers.image.title="pq-a09-credgen" \
      org.opencontainers.image.version="1.3" \
      org.opencontainers.image.description="PQ-OID4VC 9b: kimlik bilgisi ve test vektoru ureteci (v1, v1.1, v1.2, v1.3)"

COPY uretec /opt/vector-generator/uretec
COPY testler /opt/vector-generator/testler
ENV PYTHONPATH=/opt/pq:/opt/uretec

RUN python -c "import uretec, uretec.vektorler, uretec.uret, uretec.v11, uretec.boyut_dpop, uretec.v12, uretec.esleme, uretec.cbor, uretec.cose, uretec.v13; print('uretec', uretec.__version__)"

WORKDIR /work
CMD ["python", "-m", "uretec.v13", "/work"]
