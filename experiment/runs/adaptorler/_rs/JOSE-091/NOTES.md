# JOSE-091 frank_jwt: notes

## Library and build

| Item | Value |
|---|---|
| Crate | `frank_jwt = "=3.1.4"` (environment record JOSE-091) |
| Commit | `556a9046563e8fd131aa6174da8c059acde77190` (`.cargo_vcs_info.json`) |
| Crypto | `openssl` 0.10.81 / `openssl-sys` 0.9.117, linked dynamically against the system OpenSSL 3.5.7 of `pq-a09-env-rust:1.0` |
| Lock | `Cargo.lock` seeded from the environment record; every version of the record is kept, only the adapter's own crates were added (sha2 and its deps). SHA-256 `5cd331ce4d2ccab258e425b454955832e7a88a89902bf220b4a0935517d70c61` |
| Image | `a10-jose-091:1` = `sha256:1f98d3f937a97bb5c9894713c06384c18d858db8efd81e64e6dcd2b3a1ca12e1` |
| `adaptor_sha256` | `ab2b318775d0d8a94942726f1d0f8990baaceffa92854c23ec105d4c5aa2507e` |

Rebuild: `bash build.sh JOSE-091`. API scan: `bash api_scan.sh JOSE-091` (output in `evidence/api-scan.txt`).

## Treatment arm assignment (proposal)

| Arm | Proposal | Reason |
|---|---|---|
| ML-DSA-65 | **TK3** | `Algorithm` is a closed enum of HS/RS/ES variants (lib.rs L54-64); 0 matches for ML-DSA in the crate; no registration or verifier hook. V+ `VPLUS_ML-DSA-65` is rejected (`alg-desteklenmiyor`). |
| composite | **TK3** | Same; no composite name; `CMP00` rejected. No target supports composite -04, so the arm is TK3 by rule anyway. |

## Control arm

frank_jwt supports neither `EdDSA` nor `Ed25519` (0 matches in source and README; no OKP key handling). Both control vectors (`VPLUS_EdDSA`, `VPLUS_EdDSA-ED25519`) are rejected with `alg-desteklenmiyor`. **The control arm cannot be measured for this target**: L1-L5 are defined on the control arm (contract section 5), so no behavioural L level and no F_K can be obtained. Only ES256 behaviour is observable.

## V± result (`outputs/pre-freeze/JOSE-091.jsonl`, run label `oncesi`)

| Rows | Observed | Expected by the gate | |
|---|---|---|---|
| `VPLUS_ES256` × 4 arms | kabul (ES256) | accept | ok |
| `VMINUS_ES256` × 4 arms | red (`imza-gecersiz`) | reject | ok |
| `VPLUS_EdDSA` (kontrol-EdDSA) | red (`alg-desteklenmiyor`) | accept | **not met** |
| `VPLUS_EdDSA-ED25519` (kontrol-Ed25519) | red (`alg-desteklenmiyor`) | accept | **not met** |
| `VMINUS_EdDSA`, `VMINUS_EdDSA-ED25519` | red (`alg-desteklenmiyor`) | reject | ok (but not via signature check) |
| `VPLUS_ML-DSA-65`, `VMINUS_ML-DSA-65`, `CMP00`, `CMP01` | red (`alg-desteklenmiyor`) | treatment gate | TK1 not shown, arm stays TK3 |
| 16 `COSE-*` rows | `uygulanamaz` (`bicim-desteklenmiyor`) | | B6 |

**Gate: not passed on the control arm.** The ES256 part is correct (8/8). The failure is the library's missing EdDSA/Ed25519 support, not an adapter error; a correction attempt cannot change it. Suggested handling at study level: record the target as "control algorithm not supported" (outside n_eff with that reason, or descriptive ES256-only rows), rather than "adapter invalid".

## Decisions

- **Decision (algorithm argument):** frank_jwt takes exactly one algorithm per call and does not read the header. W is expressed through that argument: if W ∩ S has one member, the call is pinned to it; if W is unrestricted (`GEC`/`P0`/`P1`/`P2`), the header `alg` selects it when frank_jwt has it; if W ∩ S is empty the row is `red`/`alg-desteklenmiyor` without a call. Reason: this is the only per-call mechanism the API has (README example: `decode(&jwt, &key, Algorithm::RS256, ...)`), and pinning keeps the library's real behaviour visible (it ignores the header `alg`; see smoke test J20).
- **Decision (claim checks):** `ValidationOptions::dangerous()` is used. It disables only the `exp` check, which reads the wall clock and cannot be given `simdi`; the default would also reject every token without `exp`. This mirrors the Python reference (`verify_exp: False`) and keeps runs independent of the run date. `hata_sinifi = zaman` therefore never occurs for this target.
- **Decision (key format):** the JWK is turned into a PEM document with the `openssl` crate frank_jwt already links. The library accepts no JWK.

## Smoke test

`evidence/smoke-test.txt`: 32/32 jobs as expected with self-made keys/tokens (ES256, ES384, Ed25519, placeholder AKP key, legacy issuer, alg-confusion token, kid-less token, expired token, SD-JWT, COSE placeholder, missing file, CRLF job list). Not covered: 60 s timeout and panic paths (runner code shared by all four targets).

## Issues

- The adapter's pre-call rejections (`alg-desteklenmiyor` when no permitted algorithm exists in `Algorithm`) are attributed to the library's algorithm set, not to a library error message.
- `OpenSslError` is mapped to `alg-anahtar-uyusmazligi`; in this code path OpenSSL errors only arise while loading the PEM key for the pinned algorithm.
