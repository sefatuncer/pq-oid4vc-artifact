# C3 adaptörü (Node). Kullanım: docker build --build-arg PAKET="jose@6.2.12" -t a10-jose-009:1 -f _node/Dockerfile _node
FROM pq-a09-env-node:1.0
ARG PAKET
WORKDIR /a
RUN npm init -y >/dev/null && npm install --ignore-scripts --no-audit --no-fund ${PAKET} jose@6.2.12 >/dev/null && npm ls --all > /a/npm-ls.txt 2>&1 || true
COPY adaptor.mjs /a/adaptor.mjs
ENTRYPOINT ["node", "--no-warnings", "/a/adaptor.mjs"]
