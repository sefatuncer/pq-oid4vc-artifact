# C3 adaptörü (Python). Kullanım: docker build --build-arg PAKET="pyjwt[crypto]==2.15.0" -t a10-jose-083:1 -f _py/Dockerfile _py
FROM pq-a09-env-python:1.0
ARG PAKET
RUN python -m venv /e && /e/bin/pip install --no-cache-dir ${PAKET} && /e/bin/pip freeze > /a_freeze.txt
COPY adaptor.py /a/adaptor.py
ENTRYPOINT ["/e/bin/python", "/a/adaptor.py"]
