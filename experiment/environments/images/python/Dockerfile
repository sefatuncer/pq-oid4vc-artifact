# pq-a09-env-python:1.0 — Python environment, Step 9 task 4a (build pre-test)
# Base: official Docker Hub image (full version: contains gcc and git), pinned by digest. apt/apk are NOT used.
FROM python:3.13-trixie@sha256:82c46c08c991d3d3ff10476ac5e386c2c28f27bbd3985a02c5e39fe99ab272eb
LABEL pq.adim="a09" pq.gorev="4a" pq.imaj="pq-a09-env-python:1.0"
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_INPUT=1 PIP_INDEX_URL=https://pypi.org/simple \
    PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
RUN set -eux; echo "SURUM python $(python --version 2>&1)"; echo "SURUM $(pip --version)"; \
    echo "SURUM $(git --version)"; echo "SURUM $(gcc --version | head -1)"; echo "SURUM sistem $(openssl version)"
