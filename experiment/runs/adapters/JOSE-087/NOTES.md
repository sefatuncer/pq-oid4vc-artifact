# JOSE-087 ruby-jwt 3.3.0 — adapter notes (01.10.2026)

## 1. Version pinning
- PR item 14: the latest published release. Environment record: `jwt` 3.3.0, tag v3.3.0 → `ccf24892fec8` (not the frame HEAD `9df1393e1972`). The image installs the same `Gemfile.lock` (CHECKSUMS) with `bundle install --frozen`; `HEDEF_SURUM` = `Gem.loaded_specs` (3.3.0).

## 2. TK proposal
| Arm | Proposal | Evidence |
|---|---|---|
| ML-DSA-65 | **TK3** | `lib/jwt/jwa/` only ecdsa/hmac/none/ps/rsa; ML-DSA/composite pattern 0 matches (end of `evidence/api-tarama.txt`). `register_algorithm` / `SigningAlgorithm` is an extension point, but TK2 is out of scope (RUNNER §5) |
| composite | **TK3** | the same |

## 3. V± result (`evidence/vpm-kosu.txt`, `outputs/prefreeze-v1.3/JOSE-087.jsonl`)
- ES256: VPLUS_ES256 `kabul` in 4 arms, VMINUS_ES256 `red/imza-gecersiz` in 4 arms → **passed**.
- EdDSA / Ed25519: VPLUS and VMINUS `red/alg-desteklenmiyor`. Since 3.0 EdDSA is not in the core (README L48, L132–134: separate gem `jwt-eddsa`). The gate was assessed only for the supported alg (ES256).
- ML-DSA-65 and CMP00/CMP01: `red/alg-desteklenmiyor` (consistent with TK3).
- COSE V± rows: `uygulanamaz/bicim-desteklenmiyor` (B6).
- **Gate: passed (ES256 only).**

## 4. Issues and notes for the maintainers
1. **No control arm X:** neither `EdDSA` nor `Ed25519` is supported natively. In the control arm the L1–L4 measurement cannot be made with X = EdDSA (every EdDSA vector `alg-desteklenmiyor`). Option: the `jwt-eddsa` add-on documented by the README (separate package, dependency on the `ed25519` gem) — this changes the dependency set of the environment record; not added. The decision lies with the maintainers.
2. **JWK object + `JWT.decode` incompatibility (3.3.0):** in the first smoke run, when the key finder returned `JWT::JWK.import(jwk)`, even a valid ES256 token was rejected with `VerificationKeyError: Provided JWKs do not support one of the specified algorithms` (Decode passes JWA objects to `validate_jwk_algorithms!`; `jwa.rb` create_verifiers). Fix: the `jwk.verify_key` documented in the README (an OpenSSL key) is returned. This is an adapter fix (before the battery run, on synthetic data).
3. Multi-signature: the library is compact only; General JSON B6 → L4m cannot be measured, Y_i = L4c. Documented mechanism for a per-issuer policy: `algorithms:` + key finder (a per-key allow-list can be set up per call; the notion "same verifier instance" is a stateless `JWT.decode` call in ruby-jwt).
4. No B4 candidate (multi-signature B6).

## 5. Run record
- Synthetic smoke test (not the battery): `evidence/duman-testi.txt` (fixture generator `evidence/sentetik_uret.py`).
- The pre-freeze file of 16→32 rows was run three times: 12:45Z (16 rows, first version), 12:48Z (same image, rerun for the evidence record), 12:55Z (the 32-row file to which the maintainers added the COSE V± rows; after the skeleton change that makes not reading `insa` structural). The last output is valid; only the permitted job file was run.
- **Last run (~13:59Z):** after the maintainers' policy-name normalisation rule (`|sdjwtvc=`, `@-19`; P2) was added, the image was rebuilt and the same 32-row file was rerun; the results did not change, `adaptor_sha256` reflects the current image.
- **Last run (14:05Z):** after the rule L4-YOL → `ifade-edilemedi` was added, the image was rebuilt and the same 32-row file was rerun (V± results unchanged).
