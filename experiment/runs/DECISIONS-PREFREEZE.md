# Pre-freeze decisions for the library measurement (C3)

Date: 2026-10-01. These decisions were taken after the adapter validity runs and before the
pre-registration is frozen. They are referenced from the frozen pre-registration and apply to all
measurement runs.

## Validity gate

The gate checks that an adapter drives its library correctly: a valid object is accepted and an object
with a corrupted signature is rejected, per algorithm. It is not part of the measurement.

| Source | Content |
|---|---|
| `kosu/oncesi/*.jsonl`, `kosu/oncesi/GATE-SUMMARY.csv` | JWS/COSE-level gate, 31 targets (`adaptorler/_belge/gate_summary.py`) |
| `vpm-sdjwt/` | SD-JWT-format gate vectors (16) and their generator; added because the JWS-level pair is not a well-formed SD-JWT VC for libraries that require `_sd_alg` or a specific `typ` |
| `kosu/oncesi-sdjwt/*.jsonl`, `kosu/oncesi-sdjwt/GATE-SUMMARY-SDJWT.csv` | SD-JWT-format gate, 8 SD-JWT targets |

JWS/COSE-level gate, targets passing per algorithm: ES256 29, EdDSA 16, Ed25519 7, ML-DSA-65 6, composite ML-DSA-65-ES256 0.

## Decisions

**D1. SD-JWT targets are gated with SD-JWT-format vectors.**
- SDJWT-021 accepts only the legacy `typ` value `vc+sd-jwt` and only ES256. It passes the gate in that form and is measured as is. Battery objects with `dc+sd-jwt` are expected to be rejected by this library, which is its documented behaviour.
- SDJWT-002 accepts valid objects and also objects with a corrupted issuer signature (ES256 and EdDSA). The library computes the signature check but does not use its result (source and evidence in `adaptorler/SDJWT-002/kanit/`). The adapter is valid. The target is measured as is. Its outcomes are flagged `integrity-failure`, and every analysis is also reported without it.

**D2. ML-DSA behind a non-public interface.**
- JOSE-102 (jwt-kit 5.3.0) verifies ML-DSA-65 only through `@_spi(PostQuantum)`, which is not public API.
- Primary analysis: TK3. Sensitivity analysis: TK1.

**D3. COSE algorithm identifiers in wolfCOSE.**
- The default wolfCOSE build rejects ES256 (−7) and EdDSA (−8).
- The library documents the build flag `WOLFCOSE_ENABLE_DEPRECATED_ALGS`, which enables them. The target therefore supports −7 through a documented configuration and is measured with that build.
- The default-build behaviour is reported descriptively. The rule for targets that support only −9 does not apply.

**D4. Control arm without the control algorithm.**
- Targets that support neither EdDSA nor Ed25519 cannot be measured in the control arm. Their control-arm level is `undetermined`, and paired control–treatment analyses exclude them under the effective-sample-size rule.
- Affected targets at the JWS/COSE-level gate (15): COSE-001, COSE-014, JOSE-001, JOSE-002, JOSE-034, JOSE-052, JOSE-065, JOSE-084, JOSE-087, JOSE-089, JOSE-091, SDJWT-001, SDJWT-002, SDJWT-004, SDJWT-021.
- SDJWT-002 handles EdDSA at the SD-JWT gate but without signature integrity (D1), so it stays in this list.

**D5. Documented caller patterns count as the library's verification path.**
- COSE-035 (cose-lib): the algorithm and `crit` checks are in the caller pattern given in the README.
- SDJWT-010 (sd-jwt-payload): signature verification goes through josekit, as in the crate's own example and tests.
- SDJWT-015 (@sd-jwt/core): the library is crypto-agnostic. The verifier callback answers only whether a signature is valid under a key; the algorithm policy stays in the library option `allowedIssuerAlgorithms`.
- SDJWT-025 (ssi-sd-jwt): plain compact JWS objects are verified with ssi-jwt from the same project and the same locked versions.

**D6. Policy-name suffixes.**
- `|sdjwtvc=…` and `@-19` split only the expected outcome. They do not change the library configuration.
- `P2` uses the library default, the same as GEC/P0/P1.
- `L4-YOL` is `ifade-edilemedi` for every target: no target exposes a path-class policy.

**D7. Calling conventions.**
- Adapters with their own folder and Dockerfile take `adaptor <jobs> <out>`.
- The shared adapters (`_py`, `_node`, `_go`, `_jvm`, `_kt`, `_rs`) take `<target> <jobs> <out> <run>`.
- `adaptorler/_belge/kos.sh` handles both.
