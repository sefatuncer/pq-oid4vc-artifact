# SDJWT-010 sd-jwt-payload: notes

## Library and build

| Item | Value |
|---|---|
| Crate | `sd-jwt-payload = "=0.5.1"` (environment record SDJWT-010, default feature `sha`) |
| Commit | `c47e52c31545f7ede55ad1259f275f31595e2322` (`.cargo_vcs_info.json`) |
| JOSE layer | `josekit = { version = "=0.8.7", features = ["vendored"] }`, with `openssl` 0.10.75, `openssl-sys` 0.9.111, `openssl-src` 300.5.4+3.5.4: the exact versions of the crate's published `Cargo.lock`. OpenSSL is compiled into the binary (no `libssl` in `ldd`). |
| Lock | seeded from the environment record; all record versions kept; josekit and its deps added, the three openssl crates pinned with `cargo update --precise` to the crate's own lock. SHA-256 `de2ed4ec71f16f2472cee2f2169e2c8658261a15f10f8954aa3fd3ed2fe87cc7` |
| Image | `a10-sdjwt-010:1` = `sha256:fa2db40c0cfadbdae33d787d5171fb9a96e81205e570a5cc26e95b92ed2625da` |
| `adaptor_sha256` | `c83f9447dcc78b930eb0171a4ddff6e0842edfab91df23cd2b4846d5bb4565ae` |

Rebuild: `bash build.sh SDJWT-010`. API scan: `bash api_scan.sh SDJWT-010`.

## Why josekit (contract "item 15" reading)

sd-jwt-payload performs no signature verification: no verifier type, no signature crate in its dependency lock, only a `JwsSigner` trait for issuing. Its README points to `examples/sd_jwt.rs`, which, like the test `sd_jwt_is_verifiable` (tests/api_test.rs L148-155), uses josekit; the manifest declares `josekit = { version = "0.8.4", features = ["vendored"] }` as dev-dependency and the published lock resolves it to 0.8.7. That crate, version and feature are pinned here, so the measured stack is "sd-jwt-payload as documented, with the JOSE layer its own code uses". Every algorithm decision below is therefore a josekit decision; for the delegation analysis (D-E7) this target delegates signature policy to josekit, which does not appear among the targets of the contract's TK table (section 6).

## Treatment arm assignment (proposal)

| Arm | Proposal | Reason |
|---|---|---|
| ML-DSA-65 | **TK3** | No ML-DSA in sd-jwt-payload or josekit 0.8.7 (0 matches); header `ML-DSA-65` has no josekit verifier. josekit's `JwsVerifier` trait is public (jws_algorithm.rs L53), which would be a TK2 route, out of scope since 01.10. |
| composite | **TK3** | Same; `CMP00` rejected. |

## Control arm

josekit `EdDSA` covers Ed25519 and Ed448 keys (eddsa.rs L191-232). There is no `Ed25519` algorithm name. **Control label: `EdDSA`**; the `-ED25519` rows are informative only.

## V± result (`outputs/pre-freeze/SDJWT-010.jsonl`, run label `oncesi`)

| Rows | Observed | Gate expectation | |
|---|---|---|---|
| `VPLUS_ES256` × 4 arms | kabul (ES256) | accept | ok |
| `VMINUS_ES256` × 4 arms | red (`imza-gecersiz`) | reject | ok |
| `VPLUS_EdDSA` (kontrol-EdDSA) | kabul (EdDSA) | accept | ok |
| `VMINUS_EdDSA` (kontrol-EdDSA) | red (`imza-gecersiz`) | reject | ok |
| `VPLUS_EdDSA-ED25519`, `VMINUS_EdDSA-ED25519` | red (`alg-desteklenmiyor`) | | label not supported; EdDSA arm used |
| `VPLUS_ML-DSA-65`, `VMINUS_ML-DSA-65`, `CMP00`, `CMP01` | red (`alg-desteklenmiyor`) | treatment gate | TK1 not shown, arms TK3 |
| 16 `COSE-*` rows | `uygulanamaz` | | B6 |

The V vectors are plain compact JWS; they were checked as SD-JWTs without disclosures (`<jws>~`). **Gate: passed** (control arm `EdDSA`; ES256 8/8, EdDSA 2/2).

## Decisions

- **Decision (JOSE layer):** josekit 0.8.7 with `vendored`, pinned to the crate's own lock (josekit, openssl, openssl-sys, openssl-src). Reason above.
- **Decision (verifier selection):** josekit verifies with one algorithm per verifier. If W ∩ S has one member the verifier is built for it (josekit then refuses other header values); for unrestricted policies the verifier follows the header `alg`; if W ∩ S is empty the row is `red`/`alg-desteklenmiyor` without a call. Same rule as JOSE-091.
- **Decision (KB-JWT / presentations):** rows whose `artefakt` starts with `vp` are `ifade-edilemedi`. The library parses a KB-JWT but offers no way to verify its signature, `sd_hash`, `aud` or `nonce`; writing that check would be adapter code (B4), which the contract excludes from the L level.
- **Decision (JWK unchanged):** the published JWK, including its `kid`, is given to josekit. josekit then also binds the header `kid`: a token without `kid` whose key was found through the `issuer/<alg>` role fallback is refused ("kid header claim is required", `anahtar-bulunamadi`; smoke test J21). This is library behaviour with the published key; it matters for battery vectors that carry no `kid` (for example x5c-based ones).
- **Decision (plain compact JWS):** handed to `SdJwt::parse` as `<jws>~`, as the Python reference does for its SD-JWT target. The library accepts it (`_sd_alg` optional).
- **Decision (claim checks):** none are added. josekit `decode_with_verifier` checks no time claims and the adapter does not call `JwtPayloadValidator`; `zaman` never occurs.

## Smoke test

`evidence/smoke-test.txt`: 32/32 jobs as expected (case list in JOSE-091/NOTES.md), including SD-JWT with a valid disclosure, a tampered SD-JWT, an SD-JWT with an unused disclosure and a `vp` row.

## Issues

- The disclosure step runs only after a successful signature check; disclosure errors are reported as `istisna-diger` (no dedicated class in the closed list).
