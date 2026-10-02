# JOSE-031 guardian 2.5.0 — adapter notes (01.10.2026)

## 1. Version pinning
- Latest published release 2.5.0 (tag → `a9c9838b40f8`; not the frame HEAD `6e86224f9c0a`). PR item 13: in the sample in place of JOSE-104.

## 2. TK proposal
| Arm | Proposal | Evidence |
|---|---|---|
| ML-DSA-65 | **TK3** | erlang-jose 1.11.12 `jose_jws.erl` from_map: Ed25519/Ed448/EdDSA, ES*, HS*, Poly1305, PS*, RS*, none; ML-DSA/AKP 0 matches (`evidence/api-scan.txt`) |
| composite | **TK3** | the same |

## 3. V± result (`evidence/vpm-run.txt`)
- ES256 ×4 `kabul` / VMINUS ×4 `red/imza-gecersiz`; EdDSA `kabul` / VMINUS `red`; label `Ed25519` `kabul` / VMINUS `red` (erlang-jose recognises both labels → control arm `EdDSA`, contract §8 item 4).
- ML-DSA-65, CMP00/01: `red/alg-desteklenmiyor` (the AKP JWK cannot be built). COSE B6.
- **Gate: passed (ES256 + EdDSA + Ed25519).**

## 4. Notes
1. Guardian merges the error causes into `:invalid_token`; the `hata_sinifi` distinction is an inference of the adapter (MAPPING §4). The decision (accept/reject) is the library's.
2. L2: `allowed_algos` is a per-call option (documented). L3: `JOSE.JWT.verify_strict` verifies the signature according to the match of key type and alg (the behaviour will be measured with K10 after the freeze).
3. L4c: the Guardian `SecretFetcher` behaviour (`fetch_verifying_secret(mod, headers, opts)`) allows selecting the issuer key from the header (documented extension; the per-issuer alg set per call with `allowed_algos`).
4. Multi-signature B6; no B4 candidate. `dogrulanan_algoritmalar` empty (Guardian does not show it).

## 5. Run record
- Smoke test `evidence/smoke-test.txt`. Pre-freeze file: 13:15Z, ~13:59Z, 14:05Z; V± the same.
