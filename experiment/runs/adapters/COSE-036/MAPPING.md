# COSE-036 wolfCOSE — policy → API mapping (contract 1.0 §2.2, RUNNER §2)

- **Target:** wolfCOSE @ `f907071b10127f3ae2dd7719749a91b039ff04a1` (no release → frame `son_commit_sha`; PR item 14), wolfSSL **v5.9.2-stable** (`ac01707f552c`) with the README "Full Build" flags (`--enable-mldsa` included) — the same as the environment record.
- **Measurement configuration:** `make shared` with the documented wolfCOSE build macro **`WOLFCOSE_ENABLE_DEPRECATED_ALGS`** (`docs/Macros.md` L149–157; Makefile `EXTRA_CFLAGS`). Reason: the battery carries ES256 with the RFC 9053 id **−7** and EdDSA with **−8**; the default build rejects these ids with `COSE_BAD_ALG` (`evidence/smoke-default-build.txt`). The code does not change. Needs the maintainers' approval (NOTES §4).
- **Image:** `a10-cose-036:1` (`FROM pq-a09-env-c:1.0`). **Call:** `… a10-cose-036:1 adaptor /is/<isler> /c/COSE-036.<kosu>.jsonl`.
- **Source:** `kopru.c` (libkopru.so; only the public wolfCOSE API), `adaptor.py` (JSON/I-O driver, same process via ctypes; a minimal CBOR reader only for the kid/number of signers).

## 1. Shared rules
The same as `JOSE-087/MAPPING.md` §1 (normalisation, P2, L4-YOL → `ifade-edilemedi`). COSE ids: ES256 −7, ES384 −35, EdDSA −8, Ed25519 −19, ML-DSA-44/65/87 −48/−49/−50, composite −55.

## 2. Policy mechanism: the `alg` pin of the key
wolfCOSE has no allow-list API; the verification path enforces the `alg` field of the key (`WOLFCOSE_KEY.alg` "WOLFCOSE_ALG_*, 0 if unset"; `src/wolfcose_sign1.c` "Honour the key->alg pin on the verify path" L1198–1205) and binds alg to the curve/key type (`wolfCose_AlgCheckCrv`).
- **Key path `COSE_Key`:** `cose_key_hex[kid]` → `wc_CoseKey_PeekInfo` → `wc_CoseKey_Init` + `wc_CoseKey_SetEcc|SetEd25519|SetMlDsa` (wolfCrypt object) → `wc_CoseKey_Decode`.
- **Pin:** GEC/P0/P1/P2/VARSAYILAN → no pin (the value left by Decode; AKP keys carry their own `alg`) = library default. IZIN-A/IZIN-AX/L4 family → if the key's natural alg is in W_effective, that alg is pinned, otherwise the first element of W_effective; if the message alg ≠ pin, the library returns `COSE_BAD_ALG`.

| Policy | Configuration |
|---|---|
| GEC / P0 / P1 / P2 / VARSAYILAN | key without a pin |
| IZIN-A / IZIN-AX | pin ∈ {−7} / {−7, X} |
| L4 / L4-S / L4-Y (COSE_Sign1 or COSE_Sign with a single signer) | pin = X (effective allow-list = R) |
| L4 / L4-S / L4-Y, legacy issuer (payload `iss` = `https://legacy-issuer.example`) | legacy-issuer record of L4c: W = {A, X}, R = ∅, i.e. the allow-list of `IZIN-AX`. The record is selected by the `iss` of the object before the library call (pre-registration §5.13, contract §5.3: "L4c (consecutive)", decision D9) |
| COSE_Sign with several signers × every policy | **`ifade-edilemedi`**: `wc_CoseSign_Verify(key, signerIndex, …)` verifies the signers one by one; for a P0/P1/R rule, a loop over the signers would be the caller's code (B4) |
| L4-YOL | **`ifade-edilemedi`** (no x5chain path-class API) |

Verification: `wc_CoseSign1_Verify(key, msg, …, &hdr, &payload)` / `wc_CoseSign_Verify(key, 0, …)`. On acceptance `dogrulanan_algoritmalar = [{alg: hdr.alg}]` (for COSE_Sign the protected alg of the signer).

## 3. B6 decisions
| Serialization | Decision |
|---|---|
| COSE_Sign1, COSE_Sign | supported |
| compact, general, sd-jwt-*, oid4vci-toplu-yanit, dcapi-json-parametre | **B6** |

## 4. Return code → hata_sinifi (`asama` (stage): 1 PeekInfo, 2 key type/insertion, 3 Decode, 4 Verify)
| Case | hata_sinifi |
|---|---|
| stage < 4 and `UNSUPPORTED`/`COSE_KEY_TYPE`/`BAD_ALG`, or alg not in the library (e.g. AKP + −55) | `alg-desteklenmiyor` |
| −9012 `COSE_SIG_FAIL` | `imza-gecersiz` |
| −9020 `CRYPTO` and alg EdDSA/Ed25519 (wolfCrypt Ed25519 returns a corrupted signature as CRYPTO; synthetic smoke test) | `imza-gecersiz` |
| −9011 `COSE_BAD_ALG` (stage 4): alg not in the library / alg ∉ W / alg ∈ W | `alg-desteklenmiyor` / `alg-izin-disi` / `alg-anahtar-uyusmazligi` |
| −9015 `COSE_KEY_TYPE` | `alg-anahtar-uyusmazligi` |
| −9021 `UNSUPPORTED` | `alg-desteklenmiyor` |
| −9002/−9003/−9004/−9006/−9010 CBOR/tag | `ayristirma` |
| −9014 `COSE_BAD_HDR` (`crit` if crit is present) | `crit` / `ayristirma` |
| other | `istisna-diger` |
