# SDJWT-025 ssi-sd-jwt (spruceid/ssi): notes

## Library and build

| Item | Value |
|---|---|
| Crate | `ssi-sd-jwt = "=0.6.0"` (environment record SDJWT-025) |
| Commit | `16cd58715aa209f3151560ad59bd6ac65b90fa89`, path `crates/claims/crates/sd-jwt` |
| JOSE crates | `ssi-jws =0.5.0`, `ssi-jwk =0.4.0` with `default-features = false`, features `secp256r1` + `ed25519`; `ssi-jwt =0.6.0` (`default-features = false`); `ssi-claims-core =0.2.0`; `p256` 0.13.2, `ed25519-dalek` 2.2.0 |
| Lock | seeded from `_info-SDJWT-025-feature/output/Cargo.lock`; every version kept. Crates dropped by the resolver because the default features are off: `rsa`, `k256`, `sha3`, `ripemd160`, `pkcs1`, `pkcs8`, `spki`, `der`, `const-oid`, `crypto-bigint`, `num-bigint-dig`, `num-iter`, `pem-rfc7468`, `keccak`, `libm`, `spin`. SHA-256 `e99a55138797eb2d14e51d6417fd1582f0f227c7e830d61355de566e8508a8a9` |
| Image | `a10-sdjwt-025:1` = `sha256:db23d0780327e051717d8147e15f32c5c35f4930135523da410a51ab58958652` |
| `adaptor_sha256` | `0a825968798dd442fb355ee56c7e6b2e5d805cab82a9b26ea6a3eb21a5f44e95` |

Rebuild: `bash build.sh SDJWT-025`. API scan: `bash api_scan.sh SDJWT-025`.

## Treatment arm assignment (proposal)

| Arm | Proposal | Reason |
|---|---|---|
| ML-DSA-65 | **TK3** | Closed algorithm list and closed key-type set in ssi-jwk; an AKP/ML-DSA JWK does not deserialise, a header `alg` of `ML-DSA-65` fails at decoding; 0 ML-DSA matches in the ssi crates. |
| composite | **TK3** | Same; `CMP00` rejected. |

## Control arm

`EdDSA` is supported (`ed25519` feature). There is no `Ed25519` algorithm name. **Control label: `EdDSA`**; the `-ED25519` rows are informative only.

## V± result (`outputs/pre-freeze/SDJWT-025.jsonl`, run label `oncesi`)

| Rows | Observed | Gate expectation | |
|---|---|---|---|
| `VPLUS_ES256` × 4 arms | kabul (ES256) | accept | ok |
| `VMINUS_ES256` × 4 arms | red (`imza-gecersiz`) | reject | ok |
| `VPLUS_EdDSA` (kontrol-EdDSA) | kabul (EdDSA) | accept | ok |
| `VMINUS_EdDSA` (kontrol-EdDSA) | red (`imza-gecersiz`) | reject | ok |
| `VPLUS_EdDSA-ED25519`, `VMINUS_EdDSA-ED25519` | red (`alg-desteklenmiyor`) | | label not supported; EdDSA arm used |
| `VPLUS_ML-DSA-65`, `VMINUS_ML-DSA-65`, `CMP00`, `CMP01` | red (`alg-desteklenmiyor`) | treatment gate | TK1 not shown, arms TK3 |
| 16 `COSE-*` rows | `uygulanamaz` | | B6 |

The V vectors are plain compact JWS and were verified through ssi-jwt (see Decision). **Gate: passed** (control arm `EdDSA`; ES256 8/8, EdDSA 2/2).

## Expressibility

Only `GEC`/`P0`/`P1`/`P2` can be expressed. `IZIN-A`, `IZIN-AX`, the `L4` family and `L4-YOL` are `ifade-edilemedi`, so L1-L4 cannot be reached through the API. Evidence for the "not expressible" rule (contract section 5.5, condition 1 and 3): `evidence/api-scan.txt` (no allow-list hook; 0 matches for allow-list names) and the source lines in MAPPING.md section 1. Condition 2 (two independent attempts) is outside this task.

## Decisions

- **Decision (feature set):** `secp256r1` + `ed25519` with `default-features = false`, as the brief and the environment note K4 state. The environment's info build (`experiment/environments/targets/_info-SDJWT-025-feature`) did not switch default features off, so its lock also contains `rsa` and `k256` (default features `rsa`, `secp256k1`, `eip`, `ripemd-160`). Those only add RS*/PS*/ES256K, none of which is A or X; with the minimal set they verify as `imza-gecersiz` (algorithm not compiled in). ES384 is in neither build.
- **Decision (plain compact JWS through ssi-jwt):** ssi-sd-jwt cannot decode a JWS without `_sd_alg`, so the Python approach (`<jws>~`) would reject every V vector for a reason unrelated to signatures. Plain compact JWS is therefore verified with `ssi_jwt::ToDecodedJwt` on `ssi_jws::JwsStr`: the JWT layer that ssi-sd-jwt itself uses for the issuer JWT, same project, same locked versions, same `VerificationParameters` and the same proof check (`JwsSignature::validate_proof`). Observation for the record: ssi-sd-jwt treats `_sd_alg` as mandatory, unlike RFC 9901.
- **Decision (no allow-list emulation via JWK `alg`):** setting the JWK `alg` member would pin one algorithm per key (ssi-jws lib.rs L680-687) and could imitate `IZIN-A`, but not two-member sets such as `IZIN-AX`, and it is a per-key binding (L3 mechanism), not an allow-list. Following the Python reference for SDJWT-018, allow-list policies are `ifade-edilemedi`; the binding is reported as an L3 candidate for the L-level protocol.
- **Decision (KB-JWT / presentations):** rows whose `artefakt` starts with `vp` are `ifade-edilemedi`; the library offers types and `SdHash::verify` but no KB-JWT verification entry point, and assembling one would be adapter code (B4).
- **Decision (clock):** `VerificationParameters::with_date_time(simdi)`: the API takes a verification time, so `simdi` = 1790003700 is used as the contract asks. Expired tokens are rejected with `zaman` (smoke test J24).

## Smoke test

`evidence/smoke-test.txt`: 32/32 jobs as expected (case list in JOSE-091/NOTES.md).

## Issues

- `ProofValidationError::InvalidSignature` hides the reason of non-signature failures (algorithm/key mismatch, algorithm not compiled in); these rows read `imza-gecersiz`. Only `hata_sinifi` is affected, not `sonuc_ham`.
