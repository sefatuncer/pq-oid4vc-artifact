# pq-a09-signer — PQ-OID4VC Adim 9b: PQ/composite JWS imzalayici ve dogrulayici (pqjose)
#
# Taban: resmi Docker Hub python:3.11-slim, OZET ile sabit (Debian 13 "trixie", Python 3.11.16).
#   * Sistem OpenSSL 3.5.7-1~deb13u2 tabanda HAZIR (ML-DSA-44/65/87 yerlesik): apt KULLANILMAZ,
#     boylece imaj yalniz taban ozeti + PyPI ozetleriyle yeniden uretilebilir.
#   * Python paketleri PyPI'den surum + SHA-256 ile sabit (--require-hashes, yalniz tekerlek).
#   * cryptography 50.0.1 kendi OpenSSL 4.0.2'sini gomulu getirir -> kitaplik (OpenSSL 4.0.2) ile
#     capraz dogrulayici (sistem OpenSSL 3.5.7 CLI) FARKLI surumlerdir.
# Insa:   docker build -t pq-a09-signer:1.0 experiment/signer
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

# Surum kapisi: beklenen surumler degilse insa BASARISIZ olur
RUN openssl version | grep -q '^OpenSSL 3\.5\.7 ' \
 && test "$(dpkg-query -W -f='${Version}' openssl)" = "3.5.7-1~deb13u2" \
 && python -c "import cryptography; assert cryptography.__version__ == '50.0.1'" \
 && python -c "from cryptography.hazmat.primitives.asymmetric import mldsa; mldsa.MLDSA65PrivateKey.from_seed_bytes(bytes(32))" \
 && python -m pqjose info \
 && python -m servis.pqdogrula saglik > /dev/null

# PQ ilkel dogrulama servisi (istege bagli): kimlik dogrulama YOK -> yalniz ic Docker agi ya da 127.0.0.1
EXPOSE 8765
WORKDIR /work
CMD ["python", "-m", "pqjose", "info"]
