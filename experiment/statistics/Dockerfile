# pq-a09-analiz — PQ-OID4VC Step 9 task 9: C3 (H6) pre-registered statistics scripts (c3istat)
#
# Base: official Docker Hub python:3.11-slim, pinned by DIGEST (the digest used in the project; Python 3.11.16).
#   * apt is NOT USED; the image is reproduced only from the base digest + the PyPI digests.
#   * Python packages from PyPI pinned by version + SHA-256 (--require-hashes, wheels only, --no-deps; full closure).
#   * Runs are made without network (--network none); there are no external requests.
# Build:  docker build -t pq-a09-analiz:1.0 experiment/statistics
# Test:   docker run --rm --name pq-a09-analiz-test --memory=4g --network none -v <results>:/cikti \
#           pq-a09-analiz:1.0 python /opt/c3istat/sentetik-testler/calistir.py --cikti /cikti/test
# Analysis: docker run --rm --name pq-a09-analiz-kosu --memory=4g --network none -v <input-folder>:/girdi:ro \
#           -v <output-folder>:/cikti pq-a09-analiz:1.0 python -m c3istat analiz --girdi /girdi/<file> --cikti /cikti
FROM python:3.11-slim@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534

LABEL org.opencontainers.image.title="pq-a09-analiz" \
      org.opencontainers.image.version="1.0" \
      org.opencontainers.image.description="PQ-OID4VC C3 (H6) istatistik betikleri: T1-T5, Holm, Wilson, Newcombe 10, kosullu kesin OR, kume bootstrap"

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=0 \
    PYTHONIOENCODING=utf-8 \
    PYTHONPATH=/opt/c3istat \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    LC_ALL=C.UTF-8 \
    TZ=UTC

COPY betikler/requirements.txt /opt/c3istat/requirements.txt
RUN pip install --require-hashes --only-binary=:all: --no-deps -r /opt/c3istat/requirements.txt \
 && pip check

COPY betikler/c3istat /opt/c3istat/c3istat
COPY sentetik-testler /opt/c3istat/sentetik-testler

# Version gate: the build FAILS if the versions are not the expected ones
RUN python -c "import sys; assert sys.version_info[:3] == (3, 11, 16), sys.version" \
 && python -c "import numpy, scipy, statsmodels; assert (numpy.__version__, scipy.__version__, statsmodels.__version__) == ('2.4.6', '1.17.1', '0.15.0')" \
 && python -m c3istat surum > /dev/null

WORKDIR /work
CMD ["python", "-m", "c3istat", "surum"]
