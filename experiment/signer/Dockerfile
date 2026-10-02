# pq-a09-signer — PQ-OID4VC Step 9b: PQ/composite JWS signer and verifier (pqjose)
#
# Base: official Docker Hub python:3.11-slim, pinned by DIGEST (Debian 13 "trixie", Python 3.11.16).
#   * System OpenSSL 3.5.7-1~deb13u2 is READY in the base (ML-DSA-44/65/87 built in): apt is NOT used,
#     so the image can be reproduced from the base digest + PyPI digests only.
#   * Python packages from PyPI pinned by version + SHA-256 (--require-hashes, wheels only).
#   * cryptography 50.0.1 brings its own embedded OpenSSL 4.0.2 -> the library (OpenSSL 4.0.2) and the
#     cross-verifier (system OpenSSL 3.5.7 CLI) are DIFFERENT versions.
# Build:   docker build -t pq-a09-signer:1.0 experiment/signer
FROM python:3.11-slim@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534

LABEL org.opencontainers.image.title="pq-a09-signer" \
      org.opencontainers.image.version="1.0" \
      org.opencontainers.image.description="PQ-OID4VC 9b: ES256/EdDSA/ML-DSA/composite-04 JWS araci"

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=0 \
    PYTHONPATH=/opt/pq \
    TZ=UTC

COPY requirements.txt /opt/pq/requirements.txt
RUN pip install --require-hashes --only-binary=:all: -r /opt/pq/requirements.txt

COPY pqjose /opt/pq/pqjose
COPY servis /opt/pq/servis
COPY testler /opt/pq/testler
COPY dis-vektorler /opt/pq/dis-vektorler

# Version gate: if the versions are not the expected ones, the build FAILS
RUN openssl version | grep -q '^OpenSSL 3\.5\.7 ' \
 && test "$(dpkg-query -W -f='${Version}' openssl)" = "3.5.7-1~deb13u2" \
 && python -c "import cryptography; assert cryptography.__version__ == '50.0.1'" \
 && python -c "from cryptography.hazmat.primitives.asymmetric import mldsa; mldsa.MLDSA65PrivateKey.from_seed_bytes(bytes(32))" \
 && python -m pqjose info \
 && python -m servis.pqdogrula saglik > /dev/null

# PQ primitive verification service (optional): NO authentication -> only the internal Docker network or 127.0.0.1
EXPOSE 8765
WORKDIR /work
CMD ["python", "-m", "pqjose", "info"]
