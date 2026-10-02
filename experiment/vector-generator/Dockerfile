# pq-a09-credgen — PQ-OID4VC Step 9b: generator of SD-JWT VC / KB-JWT / TSL / OID4VP request / DPoP and test vectors
#
# Base: local pq-a09-signer:1.0 (experiment/signer; python:3.11-slim@sha256:9534e5a8...; OpenSSL 3.5.7;
#        cryptography 50.0.1). Since it is a local image it is referenced by tag, not by digest; the id of the image
#        used is recorded in the README. NO additional packages.
# Versions: 1.0 = the build that produced v1; 1.1 = + generator/v11.py (v1.1) and boyut_dpop.py;
#           1.2 = + generator/v12.py (v1.2) and esleme.py (BATTERY-MAPPING.md).
#           1.3 = + generator/cbor.py, cose.py (COSE_Sign/COSE_Sign1), v13.py (v1.3: COSE + L4c old issuer),
#                 the v1.3 sections of esleme.py, tests t10_cose.py and t12_cose.py. The generation code of v1, v1.1, v1.2 did not change.
# Build:   docker build -t pq-a09-credgen:1.3 experiment/vector-generator
# Generation (v1.3; the frozen v1, v1.1, v1.2 and keys/v1 are mounted read-only):
#   docker run --rm --name pq-a09-credgen -v <root>:/work -v <root>/vectors/v1:/work/vectors/v1:ro
#     -v <root>/vectors/v1.1:/work/vectors/v1.1:ro -v <root>/vectors/v1.2:/work/vectors/v1.2:ro
#     -v <root>/keys/v1:/work/keys/v1:ro pq-a09-credgen:1.3
# Mapping: ... -v <project>/00-on-kayit:/onkayit:ro pq-a09-credgen:1.3 python -m generator.esleme /work /onkayit/ON-KAYIT-TASLAK.md
# Earlier sets: python -m generator.uret /work (v1), python -m generator.v11 /work (v1.1), python -m generator.v12 /work (v1.2)
# Layout inside the image: /opt/vector-generator/{generator,tests} (renamed 03.10.2026; the images built before
# that date have /opt/uretec/uretec and /opt/uretec/testler, see docs/PATHS.md).
FROM pq-a09-signer:1.0

LABEL org.opencontainers.image.title="pq-a09-credgen" \
      org.opencontainers.image.version="1.3" \
      org.opencontainers.image.description="PQ-OID4VC 9b: kimlik bilgisi ve test vektoru ureteci (v1, v1.1, v1.2, v1.3)"

COPY generator /opt/vector-generator/generator
COPY tests /opt/vector-generator/tests
ENV PYTHONPATH=/opt/pq:/opt/vector-generator

RUN python -c "import generator, generator.vektorler, generator.uret, generator.v11, generator.boyut_dpop, generator.v12, generator.esleme, generator.cbor, generator.cose, generator.v13, generator.v14; print('generator', generator.__version__)"

WORKDIR /work
CMD ["python", "-m", "generator.v13", "/work"]
