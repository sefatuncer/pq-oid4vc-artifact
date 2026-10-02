# pqdogrula — PQ primitive verification service (C3 treatment class TK2 "plug-in")

**Rationale:** Step 9a decision D-E3/D-E5 (pre-registration §2B). In the TK2 class of C3, a thin
plug-in is attached to the **public extension point** of the target library (for example Java
Nimbus `JWSVerifier`, the Go crypto interface, .NET `SecurityKey`/`SignatureProvider`, the PHP
jwt-framework algorithm registry, a custom verifier in JS `jose`); the plug-in asks this service
only for the **cryptographic primitive**. **The policy decision stays in the library** (which alg is
accepted, how many signatures are required, how the key is selected, x5c/crit/typ). The targets
are in 9 language groups and our library is Python, so a language-independent HTTP interface and a
CLI are provided.

(`pqdogrula` = "PQ verify". The API field names and endpoints are Turkish identifiers and are
explained below.)

## 1. What it does / does not do

| Does | Does not |
|---|---|
| `alg` + public key + signed bytes + signature → `{gecerli, bilesenler, hata}` (valid, components, error) | JWS/JWT/SD-JWT parsing, header processing, `kid`/`x5c` resolution, chain verification |
| ML-DSA-44/65/87 (RFC 9964; empty ctx) | alg allow-list, required set, multi-signature semantics (all in the library) |
| composite -04: ML-DSA-44-ES256, ML-DSA-65-ES256, ML-DSA-87-ES384, ML-DSA-44-Ed25519, ML-DSA-65-Ed25519, ML-DSA-87-Ed448 — result per component | classical algs (ES256, EdDSA…): the library's own support is used; the service returns `hata` |
| check `jwk.alg == request alg` for an AKP JWK (RFC 9964 §3: `alg` is MANDATORY in AKP), length/encoding checks | key storage, signing, logging |

The cryptography takes the same path as `pqjose` (cryptography 50.0.1 / bundled OpenSSL 4.0.2;
composite: -04 §4.3, component AND).

## 2. Interface

**Request (JSON):**

| Field | Required | Description |
|---|---|---|
| `alg` | ✔ | one of the 9 values above |
| `jwk` **or** `acik_anahtar` / `acik_anahtar_hex` (public key) | ✔ (one) | `jwk`: AKP (`kty=AKP`, `alg`, `pub`); `priv`, if present, is **ignored**. `acik_anahtar`: base64url raw public key (ML-DSA: FIPS 204 pk; composite: `mldsaPK ‖ tradPK`, -04 §4.1) |
| `imzalama_girdisi` / `_hex` (signing input) | ✔ | the signed bytes. JWS: `ASCII(BASE64URL(protected) '.' BASE64URL(payload))`; COSE: the `Sig_structure` bytes |
| `imza` / `_hex` (signature) | ✔ | raw signature bytes (base64url-decoded for JWS) |

**Response:** `{"gecerli": bool, "alg": str, "bilesenler": {"ml": bool} | {"ml": bool, "trad": bool} | null, "hata": null | str, "servis": "pqdogrula/1"}`.
If `hata` (error) is set, the request or the serialization has a problem and `gecerli=false`
(for example a DER defect in a composite: `"serilestirme: DER: …"`).

**HTTP endpoints:** `GET /v1/saglik` (health: versions, supported algs) · `POST /v1/dogrula`
(verify, single request) · `POST /v1/dogrula/toplu` (batch: `{"istekler": [...]}` →
`{"yanitlar": [...]}`, at most 256). Body limit 4 MiB. **No** authentication; no request log is kept.

**CLI:** `python -m servis.pqdogrula dogrula [--istek FILE]` (stdin if no FILE); exit code `0` =
valid, `1` = invalid, `2` = request error. `python -m servis.pqdogrula saglik`.
`python -m servis.pqdogrula sunucu --host H --port P` (server).

## 3. Running (local only)

> Because there is no authentication, the service is **not exposed to an external network**: either
> on an internal Docker network (recommended) or published only on `127.0.0.1`. DO NOT use
> `-p 8765:8765` (all interfaces).

```bash
# (a) recommended for C3: internal network without outside connectivity; target library containers join the same network
docker network create --internal pq-a09-net
docker run -d --name pq-a09-pqdogrula --network pq-a09-net pq-a09-signer:1.0 \
  python -m servis.pqdogrula sunucu --host 0.0.0.0 --port 8765
#   targets: http://pq-a09-pqdogrula:8765/v1/dogrula
# (b) manual test: publish only on the host's 127.0.0.1
docker run -d --name pq-a09-pqdogrula-yerel -p 127.0.0.1:18765:8765 pq-a09-signer:1.0 \
  python -m servis.pqdogrula sunucu --host 0.0.0.0 --port 8765
# removal
docker rm -f pq-a09-pqdogrula pq-a09-pqdogrula-yerel; docker network rm pq-a09-net
```

## 4. Call examples

- **curl:** `service/examples/curl.sh` (health, single request ×2, batch). The request files were
  produced from the external test vectors: `request_ML-DSA-65.json` (RFC 9964 Appendix A),
  `request_ML-DSA-65-ES256.json` (composite -04 Appendix A.1) (`istek` = request).

```bash
curl -s -X POST -H 'Content-Type: application/json' \
  --data-binary @experiment/signer/service/examples/request_ML-DSA-65-ES256.json http://127.0.0.1:18765/v1/dogrula
# {"gecerli": true, "alg": "ML-DSA-65-ES256", "bilesenler": {"ml": true, "trad": true}, "hata": null, ...}
```

- **Python (standard library only):** `service/examples/client.py` (client) —
  `compact_jws_dogrula(url, jws, jwk)`: extracts the signing input and the signature from the JWS and
  sends them to the service.
- **Other languages (pattern for the plug-ins written in C3):** when the extension point calls
  `verify(alg, key, signingInput, signature)` → `POST /v1/dogrula` with body `{"alg": alg, "jwk":
  <AKP public JWK>, "imzalama_girdisi": b64url(signingInput), "imza": b64url(signature)}` → only the
  `gecerli` field is returned to the library; `bilesenler` and `hata` are written to the measurement
  log.

## 5. Acceptance results

| Test | Result |
|---|---|
| **T05** (`../tests/t05_service.py`, `../results/t05_service.*`) | **121/121**. t01 external vectors (RFC 9964 JOSE + raw COSE, composite -04 JOSE; jwk/hex/b64u key formats; signature/message/component corruptions, trailing bytes): **69/69 same result**; t02 scenarios (the same deterministic keys; pqjose hedged, OpenSSL, dilithium-py, deterministic signatures; composite with pqjose and OpenSSL components; corrupted/truncated): **45/45 same result**. Every case via three paths (HTTP single, HTTP batch, CLI), and `{gecerli, bilesenler}` identical to the library; error paths (unsupported alg, jwk.alg mismatch, broken hex, wrong pub length) and the health endpoint |
| **T05b** integration (`../results/t05b_service_integration.txt`) | call from another container over the internal network `pq-a09-net` (`Internal=true`, published port 0) ✔; host `curl` via `127.0.0.1:18765` ✔ |

## 6. Limitations

- The HTTP round trip adds latency; in C3, **timing** measurements must not be made with this
  service (decision/capability measurement only).
- The service verifies only the PQ/composite primitive; there are no composite X.509 chains (see the
  signer README §7).
- Single-process, threaded `http.server`; not meant for load testing.
