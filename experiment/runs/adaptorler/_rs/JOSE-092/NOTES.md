# JOSE-092 jsonwebtoken: notes

## Library and build

| Item | Value |
|---|---|
| Crate | `jsonwebtoken = { version = "=11.1.0", features = ["aws_lc_rs"] }` (environment record JOSE-092; default `use_pem` kept) |
| Commit | `4c0ae752e9acc108c8e2c4c8ed8128dc66014210` (`.cargo_vcs_info.json`) |
| Crypto | `aws-lc-rs` 1.18.1 / `aws-lc-sys` 0.45.0 (built from source in the image) |
| Lock | seeded from the environment record; all record versions kept, only sha2 and its deps added. SHA-256 `7f0ee828e4f18b027b6c67df7c90ce1fc3da879e76e89a6df3862d52a45ee06b` |
| Image | `a10-jose-092:1` = `sha256:d5f78319e708036d43ec14532271a60bfb9b8f37a053ba42ba2509db16942d9e` |
| `adaptor_sha256` | `ab8889e821375dd81ce25755b935ba066f2e4418d700c2dfe8565b3056120c7b` |

Rebuild: `bash build.sh JOSE-092`. API scan: `bash api_scan.sh JOSE-092`.

## Treatment arm assignment (proposal)

| Arm | Proposal | Reason |
|---|---|---|
| ML-DSA-65 | **TK3** | Closed `Algorithm` enum (`algorithms.rs` L75-90); a header `alg` of `ML-DSA-65` fails at header parsing; `DecodingKey::from_jwk` rejects AKP keys (`UnsupportedAlgorithm`); 0 ML-DSA matches in the crate. `CryptoProvider` swaps backends for existing names only, so even a plug-in (TK2, out of scope since 01.10) would need a library change. |
| composite | **TK3** | Same reasons; `CMP00` rejected. |

## Control arm

`EdDSA` is supported (aws-lc-rs Ed25519 verifier, `crypto/aws_lc/eddsa.rs`). The RFC 9864 label `Ed25519` is not (unknown variant). **Control label: `EdDSA`** (`kontrol_etiketi = EdDSA`); the `-ED25519` rows are informative only.

## V± result (`outputs/pre-freeze/JOSE-092.jsonl`, run label `oncesi`)

| Rows | Observed | Gate expectation | |
|---|---|---|---|
| `VPLUS_ES256` × 4 arms | kabul (ES256) | accept | ok |
| `VMINUS_ES256` × 4 arms | red (`imza-gecersiz`) | reject | ok |
| `VPLUS_EdDSA` (kontrol-EdDSA) | kabul (EdDSA) | accept | ok |
| `VMINUS_EdDSA` (kontrol-EdDSA) | red (`imza-gecersiz`) | reject | ok |
| `VPLUS_EdDSA-ED25519`, `VMINUS_EdDSA-ED25519` (kontrol-Ed25519) | red (`alg-desteklenmiyor`) | | label not supported; EdDSA arm used |
| `VPLUS_ML-DSA-65`, `VMINUS_ML-DSA-65`, `CMP00`, `CMP01` | red (`alg-desteklenmiyor`) | treatment gate | TK1 not shown, arms TK3 |
| 16 `COSE-*` rows | `uygulanamaz` | | B6 |

**Gate: passed** (control arm with `EdDSA`; ES256 8/8, EdDSA 2/2).

## Decisions

- **Decision (allow-list per key family):** `Validation::algorithms` = W ∩ family(resolved key). The library rejects any mixed-family list outright (`decoding.rs` L346-353), so passing W literally would turn `GEC` and `IZIN-AX` (control arm) into "reject everything", which no deployment of this library can configure. The projection never widens W; it only drops algorithms the key cannot verify anyway. For `GEC` it equals `Validation::new_for_family(key.family())`.
- **Decision (claim checks):** `validate_exp`, `validate_nbf`, `validate_aud` off and `required_spec_claims` empty. jsonwebtoken reads the wall clock (`get_current_timestamp`) and has no time parameter, requires `exp` by default and rejects any token carrying `aud` unless an audience is set. Signature policy is what is measured; this mirrors the Python reference (`verify_exp/iat/nbf/aud: False`).
- **Decision (backend):** `aws_lc_rs` only, as recorded in the environment; `rust_crypto` was not built.

## Smoke test

`evidence/smoke-test.txt`: 32/32 jobs as expected (self-made keys/tokens; see JOSE-091/NOTES.md for the case list). Notable observed behaviour: an ES384 token is refused under `IZIN-A` with `InvalidAlgorithm`; a token whose header says `EdDSA` but whose `kid` points to a P-256 key is refused with `InvalidAlgorithm` (J19/J20).

## Issues

- None open. Ed25519 label rows are rejected at header parsing; recorded as `alg-desteklenmiyor`.
