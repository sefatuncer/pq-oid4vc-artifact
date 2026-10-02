# pq-a09-signer — PQ/composite JWS signer and verifier (`pqjose`, Step 9b)

> **This is the study's own experiment tool.** The signer/verifier used by the C3 experiments and
> the CRQC emulator. It does not measure the behaviour of the target libraries (that work starts
> after the pre-registration freeze).

**Inputs.** External test vectors extracted from the corpus texts (`spec-corpus/metin/RFC9964.txt`,
`JOSECOMP.txt`); the design-stage pilot P4 for the size comparison (`referans/pilot/p4`, not
included). **Outputs.** The image `pq-a09-signer:1.0` (base of the vector generator
`experiment/vector-generator/`), the local PQ verification service (`servis/`), and the acceptance
results in `sonuclar/`.

## Status (last update: 24.09.2026)

| Sub-task | Status |
|---|---|
| 1. Container (`Dockerfile`, `requirements.txt`) | ✅ `pq-a09-signer:1.0` |
| 2. `pqjose` library (JWS compact/flattened/general; ES256, ES384, EdDSA/Ed25519/Ed448, ML-DSA-44/65/87, composite -04 ×6; JWK EC/OKP/AKP; x5c) | ✅ |
| 3a. External test vectors (RFC 9964 Appendix A, composite -04 Appendix A.1) | ✅ T01 **156/156** |
| 3b. OpenSSL cross-verification (both directions) + dilithium-py | ✅ T02 **68/68** (OpenSSL 44/44, dilithium-py 18/18) |
| 3c. Negative tests | ✅ T03 **103/103** (negative 84/84 rejected; positive control 19/19) |
| 3d. Sizes and comparison with P4 | ✅ T04 **29/29** (ML-DSA identical; EC ±2 B) |
| x5c (classical / ML-DSA / mixed chain) | ✅ `pki.py`, `x509.py` (T02-O5, T03-N8) |
| Generator (`experiment/vector-generator`) | ✅ separate README; **v1.1** (fallback rule A9: `Ed25519` twins of the control arm, 100 vectors), the A6 DPoP size table and **v1.2** (PR §6.5 battery completed: MR4, K5/T7, K10, V+/V−; 153 vectors; `BATARYA-ESLEME.md`) are there |
| Extra requirement (9a D-E3/D-E5, TK2 "plug-in"): `servis/` — PQ primitive verification service (local HTTP + CLI) | ✅ T05 **121/121** (t01 69/69, t02 45/45 same result) + T05b integration; see `servis/README.md` |
| Final image build + all tests run from inside the image (`testler/tumunu_calistir.sh`) | ✅ `pq-a09-signer:1.0` = `beeb05a70a97`, `pq-a09-credgen:1.0` = `55ac321117b7` |
| `DECISION-NOTES.md` | ✅ |
| (optional) LAMPS composite X.509 | out of scope (rationale §7); maintainers' decision A1: **not done for now**, labelled as a deviation from HAIP §6.1.1 |

## 1. Setup

```bash
docker build -t pq-a09-signer:1.0 experiment/signer
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-info pq-a09-signer:1.0          # versions
sh experiment/signer/testler/tumunu_calistir.sh                                   # all tests (from inside the image)
```

Last build (24.09.2026): `pq-a09-signer:1.0` image id `beeb05a70a97` (223 MB). All test results were
produced from inside this image, without mounting the source.

| Component | Version / digest | Rationale |
|---|---|---|
| Base image | `python:3.11-slim@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534` (Debian 13 "trixie", Python 3.11.16) | Official image, pinned by digest; OpenSSL 3.5.7 is already in the base, so **apt is not used** → the image can be rebuilt from the base digest + PyPI digests alone |
| System OpenSSL (CLI) | 3.5.7-1~deb13u2 (9 Jun 2026) | ML-DSA-44/65/87 built in; deterministic ML-DSA (`deterministic:1`), context string, key from seed, `-not_before/-not_after`, RFC 6979 (`nonce-type:1`) — cross-verifier and PKI generator |
| cryptography | 50.0.1 (`sha256:51afcfce…497a`), bundled OpenSSL **4.0.2** | `mldsa` module: key from seed + context (ctx) aware sign/verify; ECDSA `deterministic_signing` |
| cffi / pycparser | 2.1.1 / 3.0 (digests in `requirements.txt`) | dependencies of cryptography |
| dilithium-py | 1.4.0 (tests only) | pure-Python FIPS 204 independent of the OpenSSL code base — a third implementation |

The version gate in the Dockerfile stops the build if the versions are not the expected ones. The
library (OpenSSL 4.0.2) and the cross-verifier (OpenSSL 3.5.7) are **different OpenSSL versions**;
dilithium-py is fully independent.

## 2. Library (`pqjose/`)

| Module | Content |
|---|---|
| `params.py` | alg tables: RFC 7518/9864/9964; composite -04 Table 5 (alg, pre-hash), Table 7 (Label), §4.2 Prefix |
| `der.py` | -04 §4.5: Ecdsa-Sig-Value (strict DER: minimal encoding, single-byte length, trailing bytes rejected), ECPrivateKey (Table 4), X9.62 point |
| `mldsa.py` | ML-DSA: key from seed, hedged signing (cryptography), deterministic signing (OpenSSL CLI), verification |
| `composite.py` | -04 §4.2–4.4: `M' = Prefix ‖ Label ‖ 0x00 ‖ PH(M)`, ML-DSA(ctx=Label) ‖ Trad; component-wise verification (AND) |
| `keys.py` | JWK: EC, OKP, AKP (RFC 9964: `pub`, `priv` = 32 B seed, pub/priv consistency check §7.4), composite AKP (pub = mldsaPK‖tradPK, priv = seed‖tradSK); RFC 7638 thumbprint (AKP: alg, kty, pub); deterministic derivation with HKDF |
| `algs.py` | signing/verification primitives; key–alg binding (8725bis §3.1) |
| `jws.py` | compact / flattened / general serialization; strict parsing (duplicate names, disjoint headers, canonical base64url); **policy-based verification** |
| `x509.py`, `pki.py` | x5c parsing, chain verification with OpenSSL, chain class (all-classical / all-pq / mixed); deterministic test PKI |
| `openssl.py` | OpenSSL CLI wrapper |
| `cli.py` | `python -m pqjose info|keygen|sign|verify|thumbprint` |
| `../servis/pqdogrula.py` | PQ primitive verification service (HTTP + CLI) — for TK2 plug-ins; see `servis/README.md` |

Supported `alg` values: `ES256`, `ES384`, `EdDSA` (RFC 8037, polymorphic), `Ed25519`, `Ed448`
(RFC 9864), `ML-DSA-44/65/87` (RFC 9964), `ML-DSA-44-ES256`, `ML-DSA-65-ES256`, `ML-DSA-87-ES384`,
`ML-DSA-44-Ed25519`, `ML-DSA-65-Ed25519`, `ML-DSA-87-Ed448` (-04 Table 5).

**Verifier policy (`jws.Policy`)** — the default of our verifier:
- `semantics='all'` (**AND**): all present signatures must be valid; `'any'` = the RFC 7515 §7.2
  minimum (P0).
- `required_algs` (**L4**): required algorithm set. AND alone does not catch stripping; stripping is
  rejected only with the expected set (T03 control information).
- `allowed_algs` (L1/L2), `keys` + `kid` + key–alg binding (L3), `trust_anchors` + `attime` (x5c),
  `x5c_pq_only` (reject mixed chains), `require_protected` (alg/crit/x5c/jwk/jku/x5u must be
  protected), `understood_crit`, `allow_embedded_jwk` (DPoP), `expected_typ`.
- Unknown alg, `none`, disallowed alg, not-understood crit → that signature is invalid
  (fail-closed).
- Composite results are reported per component: `imza-gecersiz:bilesen(ml=False,trad=True)` or
  `imza-gecersiz:serilestirme: …` (`imza-gecersiz` = invalid signature, `bilesen` = component,
  `serilestirme` = serialization).

Example:

```python
from pqjose import jws
from pqjose.keys import derive_key
k = derive_key('ML-DSA-65-ES256', 'ornek'); k.kid = k.thumbprint()
tok = jws.sign(b'{"iss":"https://issuer.example"}', jws.Signer(k, {'kid': k.kid}), 'compact', deterministic=True)
r = jws.verify(tok, jws.Policy(keys=[k.public_only()], required_algs=frozenset({'ML-DSA-65-ES256'})))
print(r.valid, r.to_dict())
```

## 3. Verification (acceptance) results — `sonuclar/`

| Test | Result | What it shows |
|---|---|---|
| **T01** external vectors (`t01_dis_vektorler.*`) | **156/156** | RFC 9964 Appendix A: 3 JOSE + 3 COSE (raw) ML-DSA vectors; composite -04 Appendix A.1: 6 JOSE vectors (ML-DSA-44/65-ES256, ML-DSA-87-ES384, ML-DSA-44/65-Ed25519, ML-DSA-87-Ed448). All **ACCEPTED by our verifier**; public key from seed, JWK/priv serialization, `kid` (RFC 7638), `M'` byte-identical. **The RFC 9964 JWSs were reproduced byte for byte by our generator (3/3)**; the ML-DSA component of the draft is deterministic (6/6 identical); the 3 composite signatures with EdDSA are **fully byte-identical**; the ECDSA component uses a random k (verifiable only). Independently, the OpenSSL CLI and dilithium-py verified every vector |
| **T02** OpenSSL cross (`t02_openssl_capraz.*`) | **68/68** — OpenSSL **44/44**, dilithium-py **18/18** | ML-DSA ×3: pqjose→OpenSSL, OpenSSL→pqjose (full JWS), key-from-seed equality; classical ×4 both directions; composite ×6: pqjose components in OpenSSL (ML-DSA ctx=Label, ECDSA DER / EdDSA), a composite built from OpenSSL components in pqjose; X.509: OpenSSL's ML-DSA/mixed chains were also verified with cryptography. Deterministic ML-DSA: OpenSSL = dilithium-py (byte-identical) |
| **T03** negative (`t03_negatif.*`) | **103/103** — negative **84/84 rejected**, positive control **19/19 accepted** | corrupted signature (13 algs), corrupted payload/header, wrong alg label (8), composite component corruptions (ML and classical component separately, 6 algs), DER/serialization corruptions, separability (ECDSA component as ES256; ML component as ML-DSA-65), stripped/mixed multi-signatures (EdDSA, ML-DSA-65, composite arms), crit (5), x5c (unprotected, no anchor, mixed chain `x5c_pq_only`, wrong key, EC leaf + ML-DSA alg, broken base64), format (4 parts, duplicate name, non-canonical base64url, non-disjoint headers, `jwk` with private key, typ). **Control information:** P0 (any-valid) and P1 without an expected set (AND) **accept** stripped objects; mixed chains are **accepted** when no chain policy is set |
| **T05** PQ primitive verification service (`t05_servis.*`, `t05b_servis_entegrasyon.txt`) | **121/121** | the service (HTTP single/batch + CLI) gives the same result as the library on the t01 external vectors (69/69) and the t02 scenarios (45/45); integration on an internal Docker network and on 127.0.0.1 |
| **T04** sizes (`t04_boyutlar.*`, `t04_p4_karsilastirma.csv`, `t04_jws_boyutlari.csv`) | **29/29** | the P4 profile (names, 20 B serial number, 30-day UTCTime, BC/KU/SKI/AKI) was copied: **ML-DSA-44/65/87 SPKI, signature, CA and leaf certificate and x5c character count identical to P4**; EC-P256 ±2 B (DER ECDSA 70–72 B) |

Comparison of T04 with P4 (design-stage pilot, OpenSSL 3.5.6):

| alg | SPKI | signature | CA cert. | leaf cert. | x5c (2 certs, b64 chars) |
|---|---|---|---|---|---|
| ML-DSA-44 | 1334 = 1334 | 2420 = 2420 | 4054 = 4054 | 4073 = 4073 | 10840 = 10840 |
| ML-DSA-65 | 1974 = 1974 | 3309 = 3309 | 5583 = 5583 | 5602 = 5602 | 14916 = 14916 |
| ML-DSA-87 | 2614 = 2614 | 4627 = 4627 | 7541 = 7541 | 7560 = 7560 | 20136 = 20136 |
| EC-P256 | 91 = 91 | 72 / 70 | 454 = 454 | 474 / 476 | 1240 / 1244 |

JWS sizes (deterministic; `t04_jws_boyutlari.csv`): composite signature = ML-DSA + DER ECDSA
(ML-DSA-65-ES256: 3309 + 70…72 = **3379–3381 B**, variable), ML-DSA-65-Ed25519 3373 B,
ML-DSA-87-Ed448 4741 B. Public AKP JWK (JSON): ML-DSA-65 2643 B, ML-DSA-65-ES256 2736 B. DPoP
(minimal claims): ML-DSA-65 8128 B, ML-DSA-65-ES256 **8355 B (> nginx 8182)**, ML-DSA-87 11023 B.

Running the tests (from inside the image, results to the mounted folder):

```bash
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-test -v "$(cygpath -m "$PWD/experiment/signer/sonuclar"):/out" \
  -v "$(cygpath -m "$PWD/referans/pilot/p4"):/p4:ro" pq-a09-signer:1.0 sh -c \
  'python /opt/pq/testler/t01_dis_vektorler.py /opt/pq/dis-vektorler /out && python /opt/pq/testler/t02_openssl_capraz.py /out \
   && python /opt/pq/testler/t03_negatif.py /out && python /opt/pq/testler/t04_boyutlar.py /p4 /out'
```

The external vectors are extracted from the corpus text (`spec-corpus/metin/RFC9964.txt`,
`JOSECOMP.txt`; their SHA-256 values are in `dis-vektorler/00-OZET.json`) by
`testler/dis_vektorler.py`.

## 4. x5c

- `x5c` is standard base64 DER (RFC 7515 §4.1.6). Chain verification uses the system OpenSSL
  (`openssl verify -x509_strict -attime`).
- Chain class: leaf key + the signature of every certificate in x5c; all PQ → `tam-pq` (all-PQ),
  all classical → `tam-klasik` (all-classical), otherwise → `karisik` (mixed). `x5c_pq_only` rejects
  a mixed/classical link.
- Deterministic PKI with `pki.py`: classical (P-256) and ML-DSA-65 chains, mixed chains (classical
  leaf + ML-DSA intermediate CA; ML-DSA leaf + classical intermediate CA; ML-DSA intermediate CA +
  classical root). PKI of the test vectors: `experiment/vector-generator/anahtarlar/v1/pki/`.

## 5. Command line

```bash
python -m pqjose keygen --alg ML-DSA-65 --label issuer --private > k.json
python -m pqjose sign --key k.json --payload yuk.json --serialization compact --deterministic > t.jws
python -m pqjose verify --jws t.jws --keys jwks.json --required ML-DSA-65 --semantics all
python -m pqjose verify --jws t.jws --anchors root-ml.pem --attime 1790003700 --pq-only-chain
```

## 6. Determinism

Keys are derived from a label with HKDF-SHA256 (`keys.derive_key`); with `deterministic=True`,
ML-DSA (FIPS 204 deterministic variant; OpenSSL CLI), ECDSA (RFC 6979) and EdDSA signatures repeat
byte for byte. The default ML-DSA signature (`deterministic=False`) is hedged (cryptography).

## 7. Limitations

- **Composite X.509 (draft-ietf-lamps-pq-composite-sigs-19): out of scope.** OpenSSL 3.5.7 and
  cryptography 50.0.1 cannot produce or verify composite certificates. In LAMPS -19 the `M'`
  structure is identical to JOSE -04 (`Prefix‖Label‖len(ctx)‖ctx‖PH(M)`, empty ctx) and Appendix E
  has test vectors, so signature-level production is possible with `pqjose.composite`, but chain
  verification would need our own path validator. Not done in v1; composite keys are resolved via
  `kid`/JWKS (a deviation from the HAIP `x5c` requirement; recorded in the notes).
- COSE: `pqjose` has no COSE layer; T01 verifies only the **raw** fields (signing input / signature /
  public key) of the RFC 9964 COSE vectors. The COSE_Sign/COSE_Sign1 structure (deterministic
  CBOR, Sig_structure, COSE_Key) was added to the generator in v1.3:
  `experiment/vector-generator/uretec/cbor.py`, `cose.py`; it is verified against the RFC 9964
  Appendix A COSE_Sign1 and the -04 Appendix A.2 composite COSE examples by
  `experiment/vector-generator/testler/t12_cose.py` (138/138; the -04 ML-DSA-87-ES384 COSE example is
  internally inconsistent, an erratum candidate — decision notes H).
- Detached/unencoded payload (RFC 7797 `b64:false`) is not supported.
- x5c verification leaves path building to OpenSSL; no CRL/OCSP.
- dilithium-py is a test dependency only; it is not used on the library path.

## Turkish names in this folder

`servis` service · `pqdogrula` PQ verify · `testler` tests · `tumunu_calistir` run all ·
`dis-vektorler` external vectors · `dis_vektorler` extract external vectors · `sonuclar` results ·
`kayit` records (Docker image lists before/after) · `t01_dis_vektorler` external vectors ·
`t02_openssl_capraz` OpenSSL cross-verification · `t03_negatif` negative tests · `t04_boyutlar`
sizes · `t05_servis` service · `ortak` common · `ornek` example · `yuk` payload.
