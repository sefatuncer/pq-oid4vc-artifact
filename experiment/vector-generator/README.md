# pq-a09-credgen — credential and test-vector generator (Step 9b)

> **This is the study's own experiment tool.** It defines **what** the vectors are (construction
> facts, the L level / flag being tested, the specification basis). It does **not** write the
> expected decision (accept/reject; oracle) — as required by the pre-registration, the oracle is
> produced separately as an N-version oracle (`experiment/oracle/`). Target library behaviour is not
> measured here.

**Inputs.** The signer image `pq-a09-signer:1.0` (`experiment/signer/`); the corpus texts
`spec-corpus/metin/` for the self-verification; the pre-registration (`00-on-kayit/ON-KAYIT-TASLAK.md`,
not included) for the battery mapping. **Outputs.** Keys (`anahtarlar/`), vector sets
(`vektorler/v1` … `v1.4`), the battery mapping `BATARYA-ESLEME.md`, sizes and test results
(`sonuclar/`); used by `experiment/oracle/` and `experiment/runs/`.

## Status (last update: 26.09.2026)

| Sub-task | Status |
|---|---|
| `uretec/sdjwt.py` — RFC 9901: disclosure, digest placement, compact/General JSON issuance, KB-JWT, self-verification | ✅ |
| `uretec/statuslist.py`, `uretec/artefakt.py` — Token Status List, OID4VP request object (JAR/DC API), DPoP | ✅ |
| `uretec/anahtar.py` — deterministic keys (39 roles) + test PKI (14 certificates) → `anahtarlar/v1/` | ✅ |
| `uretec/vektorler.py` — test vector set v1 → `vektorler/v1/` (**93 vectors**, 10 families) | ✅ |
| Self-verification `testler/t10_oz_dogrulama.py` | ✅ v1 **471/471** (from inside the image) |
| Image `pq-a09-credgen:1.0` | ✅ `55ac321117b7` (FROM `pq-a09-signer:1.0` = `beeb05a70a97`) — the build that produced v1 |
| **v1.1** (fallback rule A9: `Ed25519`-labelled twins of the control arm) — `uretec/v11.py` → `vektorler/v1.1/` (**100 vectors** = the 93 of v1 byte-identical + 7 twins) | ✅ T10 v1.1 **549/549**; see §5b |
| DPoP size table (A6; claim set + composite upper bound) — `uretec/boyut_dpop.py` → `sonuclar/v1.1_dpop_boyutlari.*` | ✅ see §6 |
| Image `pq-a09-credgen:1.1` | ✅ `bd96803a15cd` (FROM `pq-a09-signer:1.0` = `beeb05a70a97`; v1 generation code unchanged) |
| **v1.2** (gaps of the PR §6.5 mapping: MR4, K5/T7, K10, V+/V−, Ed25519 twins) — `uretec/v12.py` → `vektorler/v1.2/` (**153 vectors** = the 100 of v1.1 byte-identical + 53) | ✅ T10 v1.2 **944/944**; independent reproduction with the image, `diff -r` no difference (157 files); see §5c |
| `BATARYA-ESLEME.md` (PR §6.5 K1–K11, V+/V−, MR1–MR4 × 3 arms) — `uretec/esleme.py` | ✅ independent audit T11 **293/293** |
| Image `pq-a09-credgen:1.2` | ✅ `5984112f66f6` (FROM `pq-a09-signer:1.0` = `beeb05a70a97`; v1/v1.1 generation code unchanged) |
| **v1.3** (Oracle A N-0/N-2: COSE battery + L4c "old issuer") — `uretec/cbor.py`, `uretec/cose.py`, `uretec/v13.py` → `vektorler/v1.3/` (**200 vectors** = the 153 of v1.2 byte-identical + 45 COSE + 2 L4c) and `anahtarlar/v1.3/` | ✅ T10 v1.3 **1440/1440**; independent reproduction with the image, `diff -r` no difference (204 + 6 files); see §5d |
| Validation of the COSE implementation against external vectors — `testler/t12_cose.py` (RFC 9964 Appendix A COSE, -04 Appendix A.2 COSE, corpus lines) | ✅ **138/138**; the -04 ML-DSA-87-ES384 COSE example is internally inconsistent (erratum candidate; §5d) |
| `BATARYA-ESLEME.md` v1.3 (+ §3 COSE K1–K11, V±, MR1–MR4 × 3 arms; §4 L4c) | ✅ T11 **592/592** (the v1.2 mapping against the current PR 293/293; copy `sonuclar/BATARYA-ESLEME_v1.2.md`) |
| Image `pq-a09-credgen:1.3` | ✅ `492b326d64fc` (FROM `pq-a09-signer:1.0` = `beeb05a70a97`; v1/v1.1/v1.2 generation code unchanged) |

## 1. Setup and use

The signer image (`experiment/signer`, `pq-a09-signer:1.0`) is built first; the generator is built
on top of it, with no extra packages.

```bash
docker build -t pq-a09-signer:1.0  experiment/signer
docker build -t pq-a09-credgen:1.0 experiment/vector-generator
# generation (into the output folder: anahtarlar/v1, vektorler/v1, sonuclar/v1_boyutlar.csv)
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-credgen -v "$(cygpath -m "$PWD/experiment/vector-generator"):/work" pq-a09-credgen:1.0
# self-verification (the corpus is mounted read-only)
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-t10 -v "$(cygpath -m "$PWD/experiment/vector-generator"):/work" \
  -v "$(cygpath -m "$PWD/spec-corpus/metin"):/korpus:ro" pq-a09-credgen:1.0 \
  python /opt/vector-generator/testler/t10_oz_dogrulama.py /work /korpus /work/sonuclar
```

Images (last build, 24.09.2026): `pq-a09-signer:1.0` = `beeb05a70a97`, `pq-a09-credgen:1.0` =
`55ac321117b7`. The vector set and T10 were produced from these images (without mounting the
source); the digests equal those of the previous build.
Environment: Python 3.11.16, cryptography 50.0.1 (bundled OpenSSL 4.0.2), system OpenSSL 3.5.7
(Debian 13).

## 2. Determinism and pinning

- **Keys:** `pqjose.keys.derive_key(type, "v1/<role>")` = HKDF-SHA256 (IKM
  `"PQ-OID4VC Adim 9b test vektorleri v1"`, salt `"pqjose/derive/v1"`, info = label|type). ML-DSA:
  32 B seed (RFC 9964 §4); EC: FIPS 186-5-like reduction with extra bits; Ed25519/Ed448: raw seed.
  The components of composite keys are derived **fresh with separate labels** (-04 §6.2: a
  component key is not used in another context).
- **Signatures:** ML-DSA deterministic variant (FIPS 204, rnd = 0³², OpenSSL `deterministic:1`);
  ECDSA RFC 6979; EdDSA by nature. Certificates: fixed serial number and validity
  (2026-01-01 … 2036-12-31), deterministic signature.
- **Time:** T0 = 1790000000 (2026-09-21T14:13:20Z); verification time for all vectors `simdi` ("now")
  = T0 + 3700. KB-JWT `iat` = T0 + 3600; DPoP `iat` = simdi − 10.
- **Salt / jti / decoy digest:** derived from HKDF.
- Result: regeneration is **byte-for-byte identical** (T10-C). The keys are additionally stored in
  files and pinned by SHA-256:

| File | SHA-256 |
|---|---|
| `anahtarlar/v1/SHA256SUMS` | `c941feb5ee70de6adbd2f3f9468ae8f9a2d265897db232c34d4dfda8f7ccfc1a` |
| `vektorler/v1/SHA256SUMS` | `90b28b2a25e8469776c44b16bcd3c03cc05fa465aaf3dee4bc6dd5aac467e197` |
| `vektorler/v1/MANIFEST.json` | `a4b559eddc082d71c5340e2f5e92d81f13cb7d5e9a5f7ad4089b524df43a8891` |
| `vektorler/v1/b-uyumlu/vectors.json` | `31a875516d7ce5f2a487a5037f8d696f3b9e2e8b49f409b378bbfddbf2d16cde` |

(These are test keys; there is no data of a real person or organisation. Synthetic PID:
"Erika Mustermann".)

## 3. Keys and test PKI (`anahtarlar/v1/`)

- `acik-jwks.json` (all roles except the CAs; `kid` = RFC 7638 thumbprint), `ozel/<role>.json`
  (private JWK), `roller.json` (role → type, kid, derivation label; certificate information),
  `pki/*.pem|*.der`, `pki/guven-capalari.pem` (trust anchors), `bilesen-yeniden-kullanim-jwks.json`
  (component reuse; CMP12/13 only), `SHA256SUMS`.
- Roles: `issuer/{ES256, ES384, EdDSA, Ed448, ML-DSA-44/65/87, 6 composite}`,
  `status/{ES256, ML-DSA-65, ML-DSA-65-ES256}`, `rp/{ES256, ML-DSA-65, ML-DSA-65-ES256, enc}`,
  `holder/{ES256, ML-DSA-65, ML-DSA-65-ES256}`, `dpop/*`, `ca/*`.
- PKI (HAIP 1.0 §6.1.1: `x5c` = [leaf, intermediate CA]; the root is not placed in `x5c`):

| Certificate | Key | Signed by | Chain class |
|---|---|---|---|
| root-ec / root-ml | P-256 / ML-DSA-65 | itself | trust anchor |
| int-ec / int-ml | P-256 / ML-DSA-65 | root-ec / root-ml | — |
| int-ml-rootec | ML-DSA-65 | **root-ec** | PQ intermediate CA, classical root |
| issuer-ec@int-ec, issuer-ml@int-ml | ES256 / ML-DSA-65 | int-ec / int-ml | all-classical / all-PQ |
| issuer-ec@int-ml | ES256 | int-ml | mixed (classical leaf + PQ intermediate) |
| issuer-ml@int-ec | ML-DSA-65 | int-ec | mixed (PQ leaf + classical intermediate) |
| issuer-ml@int-ml-rootec | ML-DSA-65 | int-ml-rootec | mixed (classical root link) |
| status-ec@int-ec, status-ml@int-ml | ES256 / ML-DSA-65 | — | status list signer |
| rp-ec@int-ec, rp-ml@int-ml | ES256 / ML-DSA-65 | — | RP (SAN: verifier.example) |

- **No composite X.509:** LAMPS composite certificates are not supported in OpenSSL 3.5 → composite
  keys are resolved via `kid`/JWKS (similar to JWT VC Issuer Metadata). This is a **deviation** from
  HAIP's `x5c` requirement in the composite arm (see `experiment/signer/DECISION-NOTES.md`).

## 4. Credential generators

| Artefact | Module | Format and rules |
|---|---|---|
| SD-JWT VC (PID) | `artefakt.issue_vc` | `typ=dc+sd-jwt`; `iss, iat, exp, vct, cnf.jwk, status` in the clear; 10 disclosures (object property, nested object, array element) + 2 decoy digests; `_sd` sorted; `_sd_alg=sha-256` |
| -13 / -19 modes | field `sdjwtvc_surum` | The data format is the same in both versions (`dc+sd-jwt`). Differences: JWS JSON serialization is **optional** in -13 §3.2 and its details are **out of scope** in -19 §2.2; the transitional acceptance of `vc+sd-jwt` exists only in -13 §3.2.1. JSON vectors are labelled `["-13"]`, compact ones `["-13","-19"]` |
| KB-JWT / SD-JWT+KB | `sdjwt.make_kb_jwt`, `artefakt.present` | `typ=kb+jwt`; `iat, aud, nonce, sd_hash`; with the DC API `aud = "origin:https://verifier.example/"` (OID4VP A.4) |
| General JSON SD-JWT | `sdjwt.issue_general` / `present_general` | `disclosures` and `kb_jwt` only in the first unprotected header (RFC 9901 §8.3); `sd_hash` over the temporary compact form with the **first signature** (ambiguity; VP07 contains the second-signature reading) |
| Token Status List | `statuslist.py`, `artefakt.status_token` | `typ=statuslist+jwt`; `sub, iat, exp, ttl, status_list{bits, lst}`; zlib 9; byte-identical with the Appendix C test vectors |
| OID4VP request object | `artefakt.request_compact`, `request_multisigned` | `typ=oauth-authz-req+jwt`; `client_id=x509_hash:<b64u(SHA-256(leaf DER))>` (HAIP §5); DC API `response_mode=dc_api.jwt`, `expected_origins`, DCQL; in the multi-signed form `client_id` only in the protected header of the relevant signature (A.3.2.2); unsigned: `openid4vp-v1-unsigned` |
| DPoP proof | `artefakt.dpop` | `typ=dpop+jwt`, `jwk` (public), `jti, htm, htu, iat` (+ `ath`, `nonce`) |

## 5. Test vector set v1 (`vektorler/v1/`)

Files: `<family>/<id>.jws` (compact JWS), `.sdjwt` (SD-JWT compact, `~`-separated), `.json` (JWS JSON /
SD-JWT JSON / DC API request / batch response). `MANIFEST.json` and `MANIFEST.csv` give for every
vector:

`id, dosya, sha256, bayt, aile, artefakt, serilestirme, aciklama, kol` (kontrol-EdDSA /
tedavi-ML-DSA-65 / tedavi-composite / klasik-taban / ortak), `senaryo` (§7.5 a–d, M-b0),
`sdjwtvc_surum`, `sinanan{basamak, plan_bayraklari, ek_etiketler}`, `dayanak` (MANIFEST id +
section), `insa` (**construction facts**: the alg of each signature, the key role, how it was built —
"gecerli" (valid), "bozuk: bayt 5, bit 0" (corrupted: byte 5, bit 0), …; x5c chain and its class),
`dogrulama_girdileri` (verification inputs: JWKS, kids, trust anchors, `simdi`, `kb_aud/kb_nonce`),
`b_pilot_esi`, `dcapi_protokol`. Field meanings: `docs/DATA-DICTIONARY.md` §4.

> The `insa` fields are **not** an accept/reject verdict; they state how the vector was produced.
> The oracle uses them, together with the specification clauses, as input.

| Family | Count | Content | Mainly tested |
|---|---|---|---|
| **T** | 14 | T1–T6 of the design-stage pilot P3 with **real** signatures: T1/T2 × {K: ES256+EdDSA, P: ES256+ML-DSA-65, C: ES256+ML-DSA-65-ES256}; T3 (stripped, common to all arms); T4 × 3 arms (+ a valid extra signature); T5 × 3 (single alg only); T6 (ES256+EdDSA+composite). Payload and headers as in the pilot (`{"alg":…}`), the T2 corruption as in the pilot `s[5]^=1` | L1, L2, L4; unknown-composite-alg |
| **UNK** | 5 | unregistered `ML-DSA-66`, unregistered composite name `ML-DSA-65-P256`, lower case `ml-dsa-65`, General JSON + unregistered composite, General JSON + `alg:none` | L1; unknown-composite-alg |
| **CMP** | 17 | ML-DSA-65-ES256 reference + component corruptions (ML / ECDSA / DER length / raw r‖s / non-minimal DER / trailing bytes / truncated / different messages / reversed order), imitations of implementer errors (ML component with empty ctx; SHA-256 pre-hash; M' without 0x00), separability (ECDSA component as ES256; ML component as ML-DSA-65), ML-DSA-65-Ed25519 component corruptions | L4 (AND inside the composite), L3 (key reuse) |
| **X5C** | 10 | all-classical, all-PQ, 3 mixed chains (classical leaf + PQ intermediate; PQ leaf + classical intermediate; PQ intermediate + classical root), root inside x5c, unprotected x5c, unprotected x5c chain substitution (same signature), x5c both protected and unprotected, x5c + a kid pointing to another key | L3; mixed-x5c, unprotected-x5c |
| **REQ** | 10 | signed ES256 / ML-DSA-65 (x509_hash), composite (pre-registered client), multi-signed (A.3.2.2) + PQ stripped / classical stripped / PQ corrupted, **M-b0** unsigned (no client_id / client_id kept), `alg:none` | L1, L3, L4; scenario c, M-b0 |
| **VC** | 12 | ES256 x5c, ML-DSA-65 x5c, composite kid, ML-DSA-44/87 kid, ML-DSA-65-Ed25519 kid, General JSON ×3 (scenario d; including control EdDSA), double issuance (scenario b), `typ=vc+sd-jwt`, `alg:none` | L1, L3, L4 |
| **VP** | 7 | SD-JWT+KB: ES256/ES256, ML-DSA-65/ES256 (PQ issuer + classical device key), ML-DSA-65/ML-DSA-65, composite/composite; General JSON + KB; **PQ signature stripped but KB valid**; second-signature reading of sd_hash | L1, L3, L4; sd_hash ambiguity |
| **TSL** | 3 | ES256 x5c, ML-DSA-65 x5c, composite kid | L1, L3 |
| **DPOP** | 10 | minimal claims for 7 algs + 2 (`ath`+`nonce`) + `jwk` with a private key | L1; size threshold |
| **CRIT** | 5 | not-understood `x-pq-beklenti` (candidate M-f carrier), unprotected crit, crit=["alg"], crit=[], listed parameter missing | L1; crit |

Coverage (number of vectors): L1 51, L2 6, L3 32, L4 34. **L0** needs no separate vector (L0 if
there is no constraint on the L1-labelled vectors); **L5** is measured by running the L3/L4 vectors
with the default configuration (not a vector property). Plan flags (§7.17): unknown-composite-alg 4,
mixed-x5c 4, unprotected-x5c 3; "number of lines needed to express with custom code" is a
measurement output, not a vector.

**B-compatible file:** `vektorler/v1/b-uyumlu/vectors.json` — the same structure as
`p3_node.mjs`/`p3_py.py` of the design-stage pilot P3 (`pub1` = ES256, `pub2` = EdDSA,
`vectors.T1…T6`), additionally `pub_mldsa65`, `pub_composite`. T4–T6 are now real PQ/composite
signatures instead of random bytes.

## 5b. Test vector set v1.1 (`vektorler/v1.1/`) — C3 battery

**Definition.** v1.1 = the 93 vectors of v1 (files, `b-uyumlu/vectors.json` and manifest entries
**byte-identical**) + an `alg = "Ed25519"`-labelled twin of **every** v1 vector with
`kol = kontrol-EdDSA` (7 twins). v1 is frozen: `vektorler/v1/` and `anahtarlar/v1/` were not changed
(mounted read-only during generation; tree digests identical before/after). No new keys;
**`anahtarlar/v1` is used as is**.

| v1 control vector | v1.1 twin | What changes |
|---|---|---|
| `T1K_both_valid` | `T1K_both_valid-ED25519` | header of signature #1 `{"alg":"Ed25519"}` + that signature |
| `T2K_second_tampered` | `T2K_second_tampered-ED25519` | the same; then the v1 corruption (`s[5]^=1`) |
| `T4K_plus_ML-DSA-65` | `T4K_plus_ML-DSA-65-ED25519` | signature #1 |
| `T5K_only_EdDSA` | `T5K_only_EdDSA-ED25519` | signature #0 |
| `T6_plus_composite` | `T6_plus_composite-ED25519` | signature #1 |
| `VC09_GJ_ES256_EdDSA` | `VC09_GJ_ES256_EdDSA-ED25519` | signature #1 (same salts/disclosures; ES256 signature byte-identical) |
| `DPOP02_EdDSA` | `DPOP02_EdDSA-ED25519` | the single signature (same `jti`, `iat`, `jwk`); 378 → 380 B |

Twins: the same key (`issuer/EdDSA`, `dpop/EdDSA` = Ed25519), the same payload, the same structure;
**only** the `alg` in the protected header of the `EdDSA`-labelled signature and the signature that
depends on it differ (Ed25519 is deterministic). This is checked independently by a guard inside
the generator and by T10-E. Manifest: `kol = "kontrol-Ed25519"`, `dayanak` +=
`RFC9864 §2.2 (Tablo 2: Ed25519)`, `RFC9864 §4.1.1 (JOSE kaydı: Ed25519)`,
`RFC9864 §4.1.2 (EdDSA: Deprecated)` (sections verified in `spec-corpus/metin/RFC9864.txt`),
`insa.v1_esi`, `insa.etiket_degisikligi`.

**Fallback rule (A9).** The primary label of the control arm is `EdDSA` (pre-registration
§3.7/§6.5, pilot compatibility). If a target does not support `EdDSA` but **documentedly** supports
`Ed25519` from RFC 9864, the control arm of that target is run with the `-ED25519`-suffixed vectors
and the label used is **recorded per target**.

**Decision A1 (key path).** In the L-level measurements of C3 the verification key is given in
**all arms** through the target's documented API (JWK/JWKS or a direct key); the **same path** is
used across arms. `x5c`/chain behaviour is measured **only on the X5C vectors**, with classical and
ML-DSA chains. Composite X.509 is outside v1/v1.1; this is labelled as a **deviation from HAIP
§6.1.1**. LAMPS composite X.509 will **not be done** for now.

**Decision A6 (size report).** DPoP sizes are reported **together with the claim set** (minimal /
+ath / +ath+nonce); for the composite signature size the **upper bound** is used (ML-DSA-65-ES256:
3309 + 72 = **3381 B**; ML-DSA-44-ES256 2492 B; ML-DSA-87-ES384 4731 B). Table: §6 and
`sonuclar/v1.1_dpop_boyutlari.{csv,json}`.

**Identity (to be anchored in the pre-registration as the C3 battery):**

| File | SHA-256 |
|---|---|
| `vektorler/v1.1/MANIFEST.json` | `e37ee97e4087829d94ce63109e1466c0cdb8d23c3eab25a84bcf7fee8181e102` |
| `vektorler/v1.1/SHA256SUMS` | `8f4466f2ea13cd84f9a646ca801e89e7ba3a950b4e60d56db215e1962333a40c` |
| `anahtarlar/v1/SHA256SUMS` (keys used; same as v1) | `c941feb5ee70de6adbd2f3f9468ae8f9a2d265897db232c34d4dfda8f7ccfc1a` |

The v1.1 manifest also carries the v1 anchors (`v1_capalari`: v1 `MANIFEST.json` `a4b559ed…8891`, v1
`SHA256SUMS` `90b28b2a…e197`) and the field `anahtar_sha256sums`.

**Generation and verification:**

```bash
docker build -t pq-a09-credgen:1.1 experiment/vector-generator
K="$(cygpath -m "$PWD/experiment/vector-generator")"
RO="-v $K/vektorler/v1:/work/vektorler/v1:ro -v $K/anahtarlar/v1:/work/anahtarlar/v1:ro"   # v1 read-only
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-credgen -v "$K:/work" $RO pq-a09-credgen:1.1          # v1.1
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-t10 -v "$K:/work" $RO -v "$(cygpath -m "$PWD/spec-corpus/metin"):/korpus:ro" \
  pq-a09-credgen:1.1 python /opt/vector-generator/testler/t10_oz_dogrulama.py /work /korpus /work/sonuclar v1.1
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-boyut -v "$K:/work" $RO pq-a09-credgen:1.1 python -m uretec.boyut_dpop /work
```

The generator first regenerates v1 from scratch in a temporary folder and compares it with the
frozen v1 (`SHA256SUMS` of `vektorler/v1` and `anahtarlar/v1`); if there is a difference, v1.1 is not
generated.

**T10 v1.1 (`sonuclar/t10_oz_dogrulama_v1.1.*`) — 549/549:** the A–D checks of v1 on all 100
vectors; additionally **E**: the 93 vectors of v1 are byte-identical in v1.1 and their manifest
entries are the same; `b-uyumlu` the same; the v1 anchors and the key digest are correct; every
control-EdDSA vector has exactly one twin; every twin differs from v1 only in the EdDSA→Ed25519
header and that signature; the Ed25519 signatures of the twins were **cross-verified with the
OpenSSL CLI** (6 valid, 1 corrupted in the T2K twin); `pqjose` **accepts** the `Ed25519` label (T twins
with `allowed = required`, the VC09 twin with ES256 x5c + Ed25519 kid, the DPoP twin with an embedded
jwk); allow-lists are **label-sensitive**: with only `EdDSA` in the list an `Ed25519` signature, and
with only `Ed25519` in the list the v1 `EdDSA` signature, is rejected with `alg-izinli-degil`
(alg not allowed) — the reason why the label must also be recorded separately for the targets.

## 5c. Test vector set v1.2 (`vektorler/v1.2/`) — completing the PR §6.5 battery

**Why.** The maintainers' mapping audit against PR §6.5 found these gaps in v1.1: a third signature
with an unregistered label for K5 in the control and composite arms, K10, a clean V−, MR4
(permutation of the signature order). No target had been measured.

**Definition.** v1.2 = the 100 vectors of v1.1 (files, `b-uyumlu/vectors.json`, manifest entries
**byte-identical**) + 53 new vectors. `vektorler/v1/`, `vektorler/v1.1/` and `anahtarlar/v1/` were
mounted **read-only** throughout generation and testing; the tree digests are the same before and
after. No new keys. The generator first regenerates v1.1 (and v1 inside it) from scratch in a
temporary folder and compares them with the frozen versions; it stops on any difference.

| Group | Count | Content |
|---|---|---|
| MR4 (PR §2B item 8, §2C item 4) | 24 (+9 Ed25519 twins) | Id `<id>-SIRA-<short-name>` (`sıra` = order). Two-signature objects reversed: T1K/P/C, T2K/P/C, VC07/08/09, REQ04. Three-signature objects two permutations: T4K/P/C and T6 → `ek-once` ([extra, ES256, X]) and `ters` (reversed); T7K/P/C → `kayitsiz-once` (unregistered first) and `ters` (an addition to the PR list; the primary K5 vectors are multi-signed). The protected header and signature bytes of every signature and the payload are **byte-identical**; only the order changes. For SD-JWT VC, `disclosures` are always in the **new** first unprotected header (RFC 9901 §8.3; `insa.mr4.ifsalar_yeni_ilk_basliga_tasindi`) |
| Outside MR4, descriptive | 1 | `VP05_GJ_ES256_MLDSA65_kb-SIRA-ters`: the KB-JWT is unchanged; `sd_hash` now binds the signature in position 2 (ES256), not the first one (RFC 9901 §8.1 ambiguity; PR §2D item 4) |
| K5 (T7) | 3 (+1) | `T7K/T7P/T7C_plus_kayitsiz` = T1* (first two signatures byte-identical) + a third signature labelled `alg: "X-KAYITSIZ-1"`; random, deterministic bytes (HKDF `v1.2/T7<arm>/kayitsiz-imza`, 128 B). The primary K5 vectors; T4*/T6 are secondary |
| K10 | 6 (+1) | Two directions per arm: control `alg=EdDSA` + ES256 key, `alg=ES256` + Ed25519 key; ML-DSA `alg=ML-DSA-65` + ES256, `alg=ES256` + ML-DSA-65 (AKP); composite `alg=ML-DSA-65-ES256` + pure ML-DSA-65, `alg=ML-DSA-65` + composite. The signature is a valid signature produced **with the real key's own algorithm**, not with the header alg (`insa.k10`). The key is given via `dogrulama_girdileri.jwk` (JWK) and via `acik-jwks.json` + `kid` (PR §2D item 1). The `alg=ES256` + Ed25519 direction carries no EdDSA label, so it has no twin (it would be byte-identical) |
| V+ / V− | 6 (+2) | `VPLUS_/VMINUS_{ES256, EdDSA, ML-DSA-65}`: single-signature compact JWS (`{"alg","kid","typ":"JWT"}`), V− with a bit flipped in a middle byte. For composite, `CMP00` (V+) and `CMP01` (V−) are reused. `VPLUS/VMINUS_ES256` are common to the three arms (PR §4.15: a single valid classical signature) |
| Ed25519 twins (PR §2D item 2) | 13 | the `-ED25519` twin of every new control vector that carries an EdDSA label |

**Mapping.** `BATARYA-ESLEME.md` (`uretec/esleme.py`): rows K1–K11, V+, V−, MR1–MR4; columns control
/ ML-DSA-65 / composite; each cell gives primary and secondary ids, and the PR §6.5 oracle decision
is quoted **by parsing the PR text** (the vectors contain no decisions). Cells that do not apply are
justified (K6/K7 composite only; K8/K9 arm-independent flags); K8 is adapted with an ML-DSA leaf
(`X5C04`) instead of a composite leaf (D-S1). 107 ids are used; no new v1.2 id is missing from the
mapping. Independent audit `testler/t11_esleme_denetim.py` (separate parser): **293/293**.

**Identity (for the C3 battery anchor):**

| File | SHA-256 |
|---|---|
| `vektorler/v1.2/MANIFEST.json` | `bb17aaa76a3d1859b2dd5df54c62e7039948a715e2c4b4628fed82d184c6e738` |
| `vektorler/v1.2/SHA256SUMS` | `92663b48f477f51e5a4cdd2a6942d97d36b2d9591fa67af451fd33eb14f0b2a3` |
| `anahtarlar/v1/SHA256SUMS` (unchanged) | `c941feb5ee70de6adbd2f3f9468ae8f9a2d265897db232c34d4dfda8f7ccfc1a` |
| `BATARYA-ESLEME.md` | `d73352179cdf281825d498000b7f9dc6d1df0fe835c8258c6aa2c516e659e3fc` |
| (quoted) `00-on-kayit/ON-KAYIT-TASLAK.md` | `c239d42367d81ddca1c83f35219b578c592e6b7968f689964f591f4d5b698b6e` |

The v1.2 manifest carries `v1_1_capalari` (v1.1 `MANIFEST.json` `e37ee97e…e102`, `SHA256SUMS`
`8f4466f2…a40c`), `v1_capalari` and `anahtar_sha256sums`.

**Generation and verification:**

```bash
docker build -t pq-a09-credgen:1.2 experiment/vector-generator
K="$(cygpath -m "$PWD/experiment/vector-generator")"
RO="-v $K/vektorler/v1:/work/vektorler/v1:ro -v $K/vektorler/v1.1:/work/vektorler/v1.1:ro -v $K/anahtarlar/v1:/work/anahtarlar/v1:ro"
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-credgen -v "$K:/work" $RO pq-a09-credgen:1.2                      # v1.2
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-esleme -v "$K:/work" $RO -v "$(cygpath -m "$PWD/00-on-kayit"):/onkayit:ro" \
  pq-a09-credgen:1.2 python -m uretec.esleme /work /onkayit/ON-KAYIT-TASLAK.md                                         # mapping
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-t10 -v "$K:/work" $RO -v "$(cygpath -m "$PWD/spec-corpus/metin"):/korpus:ro" \
  pq-a09-credgen:1.2 python /opt/vector-generator/testler/t10_oz_dogrulama.py /work /korpus /work/sonuclar v1.2                 # T10
```

**T10 v1.2 (`sonuclar/t10_oz_dogrulama_v1.2.*`) — 944/944** (v1 471/471 and v1.1 549/549 unchanged).
The A–D checks on 153 vectors; additionally **F**: the 100 vectors of v1.1 are byte-identical in v1.2
and their manifest entries are the same; the anchors are correct; in the MR4 twins the payload and
every (protected header, signature) pair are preserved, the signature validities are carried over
exactly by the permutation, in SD-JWT VCs the disclosures are in the new first header and the
`pqjose` result equals the source; in the VP05 twin `sd_hash` now binds the signature in position 2;
in T7 the first two signatures are byte-identical with T1*, the third signature has the unregistered
label + HKDF bytes, `pqjose` AND → `alg-bilinmiyor` (alg unknown); in K10 the signature is valid
with the real key, **cross-verified with the OpenSSL CLI**, `pqjose` L3 → REJECT; V+ / V− as
expected with `pqjose` and OpenSSL; in the new Ed25519 twins only the label and that signature
differ, verified with OpenSSL; every new control vector with an EdDSA label has its twin.

**Independent reproduction (25.09.2026):** with the project folder fully read-only, regeneration
into a temporary folder with `pq-a09-credgen:1.2` → `diff -r` **no difference (157 files)**;
`BATARYA-ESLEME.md` and `sonuclar/v1.2_boyutlar.csv` byte-identical.

## 5d. Test vector set v1.3 (`vektorler/v1.3/`) — COSE and the L4c "old issuer"

**Why.** Oracle A found two gaps (N-0, N-2): 5 of the n = 31 targets are COSE targets, yet v1.2 has
no COSE vector; and there is no separately identified "old issuer" for the per-issuer policy of L4c
(PR §2B item 6). The user approved the COSE set; PR §2H item 12. No target was measured.

**Definition.** v1.3 = the 153 vectors of v1.2 (files, `b-uyumlu/vectors.json`, manifest entries
**byte-identical**) + 47 new vectors. `vektorler/v1/`, `v1.1/`, `v1.2/` and `anahtarlar/v1/` were
mounted **read-only** throughout generation and testing; the tree digests are the same before and
after. The generator first regenerates v1.2 (and v1.1 and v1 inside it) from scratch in a temporary
folder and compares it with the frozen version; it stops on any difference. Economy: no family
outside the brief was added.

**COSE (RFC 9052; `uretec/cbor.py` deterministic CBOR, `uretec/cose.py`).** COSE_Sign (tag 98;
K1–K5, MR4) and COSE_Sign1 (tag 18; K6–K10, V±). Payload: deterministic CBOR map
`{"iss","vct","given_name"}`; protected header `{1: alg}`; `kid` (label 4) in the unprotected header
= the 32 base64url-decoded bytes of the JWK `kid`; empty `external_aad`; ECDSA signature r‖s
(RFC 9053 §2.1); composite signature per -04 (M′ = Prefix‖Label‖0x00‖PH(ToBeSigned), ML-DSA
ctx = Label, ECDSA component DER). **Algorithm identifiers are taken verbatim from the corpus** (line
numbers in `KAYNAK` of `uretec/cose.py` and in the manifest field `cose_kimlik_kaynaklari`; T12 and
T10-G re-check them against the corpus lines):

| Label | COSE | Source |
|---|---|---|
| ES256 | −7 | RFC9053:248; RFC 9864 §4.2.2 "Deprecated" (RFC9864:467); HAIP §7 "-7 or -9, as applicable" (HAIP:498) |
| EdDSA | −8 | RFC9053:365; RFC 9864 §4.2.2 "Deprecated" (RFC9864:491) |
| Ed25519 | −19 | RFC9864:225, 439 |
| ML-DSA-65 | −49 | RFC9964:367 (AKP kty 7: RFC9964:405; pub −1: 427) |
| ML-DSA-65-ES256 | −55 | JOSECOMP:1268 "TBD (request assignment -55)" → **requested, not registered** (`kayit_durumu` in the manifest) |

| Group | Count | Content |
|---|---|---|
| K1 / K2 / K4 | 3 + 3 + 3 | Per arm (X = EdDSA / ML-DSA-65 / composite): K1 COSE_Sign ES256 + X, both valid; K2 with a bit flipped in byte 5 of the X signature; K4 X only (its single signer byte-identical with the second COSE_Signature of K1) |
| K3 | 1 | `COSE-K3_X_soyuldu` (X stripped): only the ES256 signer; one file common to the three arms (byte-identical with the first signer of K1K/K1P/K1C) |
| K5 | 3 | K1 + a third signer: unregistered tstr alg `"X-KAYITSIZ-1"`, empty unprotected header, 128 B of HKDF bytes (`v1.3/COSE-K5<arm>/kayitsiz-imza`) |
| K6 / K7 | 1 + 2 | Valid composite COSE_Sign1; K7 with the ML-DSA component (byte 1654) and the ECDSA component (last byte of r; DER still valid) corrupted separately |
| K8 / K9 | 1 + 1 | ML-DSA-65 COSE_Sign1; K8 **protected** x5chain (RFC 9360, label 33) = [ML-DSA-65 leaf, classical intermediate CA] (mixed; D-S1 adaptation), K9 **unprotected** x5chain (all-PQ). The trust anchor is outside the x5chain |
| K10 | 6 | Two directions per arm, COSE_Sign1 (the same pairs as JOSE K10); the signature is valid with the real key's algorithm (`insa.k10`) |
| V+ / V− | 6 | `COSE-VPLUS_/VMINUS_{ES256, EdDSA, ML-DSA-65}` COSE_Sign1; V− with a bit flipped in a middle byte. For composite, K6 (V+) and K7-ML (V−) are reused |
| MR4 | 6 | K1 and K2 (three arms) with the COSE_Sign signer order reversed (`-SIRA-ters`); every COSE_Signature carried over byte-identical |
| Ed25519 twins | 9 | The Ed25519 (−19) twin of every control vector with the EdDSA (−8) label (fallback rule A9) |
| **L4c** | 2 | `L4C-JOSE_eski_ES256` (compact, `{"alg","kid","typ":"JWT"}`) and `L4C-COSE_eski_ES256` (COSE_Sign1): **old issuer** (`eski` = old) `iss = https://legacy-issuer.example`, key `issuer-eski/ES256` (derivation label `v1.3/issuer-eski/ES256`, kid `GGKBh_lE…MHw`), ES256 only. The counterparts of the migrated issuer are existing vectors: X only → `VPLUS_ML-DSA-65` / `CMP00` / `COSE-VPLUS_ML-DSA-65` / `COSE-K6`; ES256 only → `VPLUS_ES256` / `COSE-VPLUS_ES256` |

K11 does not apply to COSE (double issuance depends on the OID4VCI/SD-JWT VC format; its
signature-level counterpart is L4c-2). MR3 does not apply to COSE (no SD-JWT VC -13/-19 dimension).
The vectors **contain no** accept/reject expectation; for L4c there are only the `insa.ihracci`
facts (iss, kid, derivation label).

**Keys (`anahtarlar/v1.3/`):** `ozel/issuer-eski__ES256.json` (the only new key), `acik-jwks.json`,
`acik-jwks-l4c.json` (the 3 keys of the migrated issuer + the old issuer; `ihraccilar`: iss → kid),
`cose-anahtarlar.json` (public COSE_Keys of 5 roles, deterministic CBOR hex; EC2 / OKP / AKP),
`roller.json`, `SHA256SUMS`. `anahtarlar/v1/` unchanged.

**Mapping.** `BATARYA-ESLEME.md` v1.3: §1–§2 JOSE/SD-JWT (as in v1.2; the only difference is that the
control and composite cells of K8/K9 are "—" per PR §2H item 9: "not a result of the composite
arm"), §3 COSE (K1–K11, V±, MR1–MR4 × 3 arms; primary/secondary PR §2G item 4), §4 L4c (two treatment
arms × 3 rows; quotes of PR §2B item 6 and §6.5 K4), §5 honesty notes. 154 ids; no new v1.3 id is
missing from the mapping. T11: **592/592**. Copy of the v1.2 mapping:
`sonuclar/BATARYA-ESLEME_v1.2.md` (`d7335217…`).

**Identity (for the C3 battery anchor):**

| File | SHA-256 |
|---|---|
| `vektorler/v1.3/MANIFEST.json` | `a81424470cf2b773c346795aa1b1880aecd841b77254ebb0c077432bc3c5390a` |
| `vektorler/v1.3/SHA256SUMS` | `a5b678d60ff474f1991168a694f52acb6d1c8a42b9648b4e8e63913042768812` |
| `anahtarlar/v1/SHA256SUMS` (unchanged) | `c941feb5ee70de6adbd2f3f9468ae8f9a2d265897db232c34d4dfda8f7ccfc1a` |
| `anahtarlar/v1.3/SHA256SUMS` | `5d0ccf6bc8cf5de3061ecab1a6c55f8d1165fe10235f366ecd4807b830bb160c` |
| `BATARYA-ESLEME.md` | `6795ee65f5161b4db90942f7058924061273e5d1eb1546dce444cabb2c7cb982` |
| (quoted) `00-on-kayit/ON-KAYIT-TASLAK.md` | `87932cf00b74063066386b1ade066720c4ac645df3f1e75d895ab9bbc43e3f47` |

The v1.3 manifest carries `v1_2_capalari` (v1.2 `MANIFEST.json` `bb17aaa7…e738`, `SHA256SUMS`
`92663b48…b2a3`), `v1_1_capalari`, `v1_capalari` and the `anahtar_sha256sums` of the two key folders.

**Generation and verification:**

```bash
docker build -t pq-a09-credgen:1.3 experiment/vector-generator
K="$(cygpath -m "$PWD/experiment/vector-generator")"
RO="-v $K/vektorler/v1:/work/vektorler/v1:ro -v $K/vektorler/v1.1:/work/vektorler/v1.1:ro -v $K/vektorler/v1.2:/work/vektorler/v1.2:ro -v $K/anahtarlar/v1:/work/anahtarlar/v1:ro"
DIS="-v $(cygpath -m "$PWD/spec-corpus/metin"):/korpus:ro -v $(cygpath -m "$PWD/00-on-kayit"):/onkayit:ro"
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-credgen -v "$K:/work" $RO pq-a09-credgen:1.3                        # v1.3
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-esleme -v "$K:/work" $RO $DIS \
  pq-a09-credgen:1.3 python -m uretec.esleme /work /onkayit/ON-KAYIT-TASLAK.md                                         # mapping
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-t10 -v "$K:/work" $RO $DIS pq-a09-credgen:1.3 sh -c 'cd /opt/vector-generator/testler &&
  python t10_oz_dogrulama.py /work /korpus /work/sonuclar v1.3 &&
  python t11_esleme_denetim.py /onkayit/ON-KAYIT-TASLAK.md /work/BATARYA-ESLEME.md /work/vektorler/v1.3/MANIFEST.json &&
  python t12_cose.py /korpus /opt/pq/dis-vektorler /work/sonuclar'                                                     # T10, T11, T12
```

**T12 (`sonuclar/t12_cose.*`) — 138/138:** (A) the 40 identifiers in `KAYNAK` (algorithms, headers,
labels, key parameters) occur verbatim in the corpus line; (B) RFC 9964 Appendix A.2 COSE
(ML-DSA-44/65/87): the COSE_Key is decoded and re-encoded byte-identically in insertion order, the
AKP COSE thumbprint = kid, Sig_structure = `raw_to_be_signed`, the signature is verified with `pqjose`
and dilithium-py, and **deterministic re-signing reproduces the COSE_Sign1 byte for byte**; (C) -04
Appendix A.2 COSE (6 composites): key from seed, **M′ identical** with our protected header +
Sig_structure encoding, the composite signature and its components (OpenSSL CLI, dilithium-py) are
verified; in the examples with EdDSA our signature is byte-identical. **Exception:** in the
ML-DSA-87-ES384 example the SHA-512 of the shown Sig_structure does not match the PH inside the shown
M′ (the components are valid over the shown M′; alg/kid/order/digest variants were tried) → the
example cannot be verified as a COSE_Sign1, an **erratum candidate**; with the same key and header our
signature is internally consistent.

**T10 v1.3 (`sonuclar/t10_oz_dogrulama_v1.3.*`) — 1440/1440** (v1 471/471, v1.1 549/549, v1.2
944/944 unchanged). A–D on the 153 JOSE vectors and on L4C-JOSE; in C, the v1.3 `MANIFEST.json/.csv`,
`SHA256SUMS` and `anahtarlar/v1.3/SHA256SUMS` are byte-identical on regeneration; additionally **G**
(`testler/t10_cose.py`): the 153 vectors of v1.2 are byte-identical and their manifest entries are
the same; the anchors are correct; the identifier sources are on the corpus lines; the old-issuer key
is re-derived from its label and differs from the v1 keys; COSE_Key = JWK; for every COSE vector the
tag/structure, outer and inner CBOR deterministic, payload, alg label in the protected header, kid;
**every signature via three paths** (`pqjose`, OpenSSL CLI, dilithium-py for ML-DSA) consistent with
the construction claim; composite component states; the byte relations between K2/K3/K4/K5/V−/K7;
x5chain position, OpenSSL chain validity, class and leaf key; K10 header/key mismatch; in MR4 every
COSE_Signature carried over byte-identical; in the Ed25519 twins only −8→−19 and that signature
differ; in L4c the old-issuer vectors are valid with the old key and invalid with the ES256 key of
the migrated issuer.

**Independent reproduction (26.09.2026):** with `experiment/vector-generator` fully read-only,
generation into a temporary folder with `pq-a09-credgen:1.3` → `diff -r` **no difference**
(`vektorler/v1.3` 204 files, `anahtarlar/v1.3` 6 files); `BATARYA-ESLEME.md` and
`sonuclar/v1.3_boyutlar.csv` byte-identical.

**Sizes (COSE / JOSE):** because there is no base64url payload, the COSE vectors are 51–74 % of their
JOSE counterparts: `COSE-VPLUS_ES256` 174 B (JOSE 341), `COSE-VPLUS_ML-DSA-65` 3,421 B (4,672),
`COSE-K6` composite 3,491 B (`CMP00` 4,775), `COSE-K1P` 3,533 B (`T1P` 4,781), `COSE-K8` 6,295 B
(`X5C04` 11,540), `COSE-K9` 14,659 B (`X5C07` 21,564). All values in `sonuclar/v1.3_boyutlar.csv`.

## 5e. Test vector set v1.4 (`vektorler/v1.4/`) — ES384 control arm

v1.4 = v1.3 (byte-identical) + ES384 counterparts of the control-arm (EdDSA) vectors, for targets that
support neither EdDSA nor Ed25519 (pre-registration amendment 10; label order EdDSA, then Ed25519, then
ES384). 230 vectors, 30 of them with `kol` = `kontrol-ES384`. Generator `uretec/v14.py` (its docstring
describes the construction); independent check `testler/t14_es384.py` → `sonuclar/t14_es384.txt`
(**341/341**). The merged oracle for v1.4 is `experiment/oracle/birlesik/turet_v14.py`.

## 6. Sizes (`sonuclar/v1_boyutlar.csv`, `sonuclar/v1.1_boyutlar.csv`, `sonuclar/v1.1_dpop_boyutlari.*`)

DPoP by claim set (A6; `bytes / upper bound`; nginx 1.31.6 default header value threshold 8,182 B,
Node 24.15 16,348 B — pilot P4):

| alg | minimal | +ath | +ath+nonce |
|---|---|---|---|
| ES256 / EdDSA / Ed25519 | 440 / 378 / 380 | 510 / 448 / 450 | 556 / 494 / 496 |
| ML-DSA-44 | 5,805 | 5,875 | 5,921 |
| ML-DSA-65 | 8,128 | **8,198** (> nginx, +16 B) | **8,244** |
| ML-DSA-87 | **11,023** | **11,093** | **11,139** |
| ML-DSA-44-ES256 (upper bound) | 6,032 | 6,102 | 6,148 |
| ML-DSA-65-ES256 (upper bound) | **8,356** | **8,426** | **8,472** |
| ML-DSA-87-ES384 (upper bound) | **11,350** | **11,420** | **11,466** |
| ML-DSA-65-Ed25519 | **8,292** | **8,362** | **8,408** |

Bold: above the nginx threshold. ML-DSA-65 is 54 B below it with the minimal set and 16 B above it
once `ath` is added (the "≈8,192 B, 10 B above" value of pilot P4 corresponds to this set). Composite
and ML-DSA-87 are above it with every set; none exceeds the Node threshold.

Other artefacts:

| Artefact | Bytes |
|---|---|
| SD-JWT VC ES256 + x5c (classical) | 3,838 |
| SD-JWT VC ML-DSA-65 + x5c (all-PQ) | 26,409 |
| SD-JWT VC ML-DSA-65-ES256 (kid) | 6,537 |
| SD-JWT+KB: ML-DSA-65 issuer + ML-DSA-65 KB | 33,983 |
| Status List Token ML-DSA-65 + x5c | 24,719 |
| OID4VP request ML-DSA-65 + x5c / multi-signed ES256+ML-DSA-65 | 25,619 / 27,797 |

(The DPoP sizes in the vector files are measured with the actual signature size, for example DPOP06
ML-DSA-65-ES256 8,355 B; reports use the upper-bound table above — A6.)

## 7. Self-verification (T10; `sonuclar/t10_oz_dogrulama.*`) — 471/471

- **A.** TSL Appendix C (1/2/4/8 bits): decoding equal and **encoding byte-identical** (zlib 9);
  RFC 9901 §4.2.3 digest example.
- **B.** SHA-256 of the 93 vector files against the manifest; `SHA256SUMS` (96 + 71 files).
- **C.** Regeneration into a temporary folder → `vektorler/v1` and `anahtarlar/v1` byte-for-byte
  identical.
- **D.** The `insa` claims of every vector: number of signatures and alg labels; the cryptographic
  state of "valid/corrupted" signatures; CMP component states (ml/trad/serialization) and the
  consistency of the implementer-error imitations with their own deviating M'/ctx; in the
  separability vectors, that the component is genuine over M'; validity of the x5c chains with
  OpenSSL and their class (all-classical/all-PQ/mixed); `client_id` = x509_hash(leaf); TSL status
  values; DPoP `jwk`; validity of the KB-JWT with the cnf key and that `sd_hash` covers the claimed
  signature.

## 8. Limitations

- Composite X.509 (LAMPS -19) was not produced → no `x5c` in the composite arm; labelled as a
  **deviation from HAIP §6.1.1**. Maintainers' decision A1: in the L-level measurements the key is
  given in all arms through the target's documented API (JWK/JWKS or a direct key); chain behaviour is
  measured only on the X5C vectors (classical and ML-DSA chains); LAMPS composite X.509 will not be
  done for now.
- The `-ED25519` twins of v1.1 cover only the control arm (fallback rule A9); the labels of the
  other arms do not change.
- ML-DSA signatures were produced with the **deterministic** variant (for reproducibility); real
  deployments use the hedged variant. There is no difference for verification.
- The v1–v1.2 vectors are at the JOSE/SD-JWT level; v1.3 adds COSE_Sign/COSE_Sign1 (§5d). There are no
  mdoc (ISO/IEC 18013-5 MSO/DeviceResponse), JWE (response encryption), wallet attestation or key
  attestation vectors. In COSE, ES256 was produced only with −7 (no ESP256 −9; §5d).
- DCQL and `client_metadata` were kept minimal in the OID4VP requests; the full OID4VP flow
  (response, `request_uri` retrieval, `wallet_nonce`) is not produced.
- Apart from `vc+sd-jwt`, the -13/-19 data format is the same, so both modes share the same file; the
  distinction is in the manifest label `sdjwtvc_surum`.

## Generated files and Turkish names in this folder

`BATARYA-ESLEME.md` ("battery mapping") and `sonuclar/BATARYA-ESLEME_v1.2.md` are generated by
`uretec/esleme.py`. They are kept in Turkish and unchanged: T11 and both oracles parse them, and the
SHA-256 of the file is pinned in `experiment/oracle/oracle-A/karar_uret.py` and in the
pre-registration. Their structure: §1–§2 JOSE/SD-JWT cases K1–K11, V+/V− and metamorphic relations
MR1–MR4 per arm (control / ML-DSA-65 / composite), each cell with primary and secondary vector ids and
the quoted PR decision; §3 COSE; §4 L4c (two issuers); §5 honesty notes; §6 audit.

`uretec` generator · `anahtar` key · `anahtarlar` keys · `ozel` private · `acik-jwks` public JWKS ·
`roller` roles · `guven-capalari` trust anchors · `bilesen-yeniden-kullanim` component reuse ·
`vektorler` vectors · `b-uyumlu` compatible with pilot P3 · `artefakt` artefact · `boyut_dpop` DPoP
sizes · `esleme` mapping · `uret` generate · `testler` tests · `t10_oz_dogrulama` self-verification ·
`t11_esleme_denetim` mapping audit · `t12_cose` COSE external vectors · `sonuclar` results ·
`boyutlar` sizes · `eski` old · `kayitsiz` unregistered · `SIRA-ters` order reversed · `simdi` now.
