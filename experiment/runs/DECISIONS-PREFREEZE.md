# Pre-freeze decisions for the library measurement (C3)

Date: 2026-10-01. These decisions were taken after the adapter validity runs and before the
pre-registration is frozen. They are referenced from the frozen pre-registration and apply to all
measurement runs.

## Validity gate

The gate checks that an adapter drives its library correctly: a valid object is accepted and an object
with a corrupted signature is rejected, per algorithm. It is not part of the measurement.

| Source | Content |
|---|---|
| `outputs/prefreeze-v1.3/*.jsonl`, `outputs/prefreeze-v1.3/GATE-SUMMARY.csv` | JWS/COSE-level gate, 31 targets (`adapters/_tools/gate_summary.py`) |
| `vpm-sdjwt/` | SD-JWT-format gate vectors (16) and their generator; added because the JWS-level pair is not a well-formed SD-JWT VC for libraries that require `_sd_alg` or a specific `typ` |
| `outputs/prefreeze-sdjwt/*.jsonl`, `outputs/prefreeze-sdjwt/GATE-SUMMARY-SDJWT.csv` | SD-JWT-format gate, 8 SD-JWT targets |

JWS/COSE-level gate, targets passing per algorithm: ES256 29, EdDSA 16, Ed25519 7, ES384 24, ML-DSA-65 6, composite ML-DSA-65-ES256 0 (`outputs/prefreeze-v1.4/`).

## Decisions

**D1. SD-JWT targets are gated with SD-JWT-format vectors.**
- SDJWT-021 accepts only the legacy `typ` value `vc+sd-jwt` and only ES256. It passes the gate in that form and is measured as is. Battery objects with `dc+sd-jwt` are expected to be rejected by this library, which is its documented behaviour.
- SDJWT-002 accepts valid objects and also objects with a corrupted issuer signature (ES256 and EdDSA). The library computes the signature check but does not use its result (source and evidence in `adapters/SDJWT-002/evidence/`). The adapter is valid. The target is measured as is. Its outcomes are flagged `integrity-failure`, and every analysis is also reported without it.

**D2. ML-DSA behind a non-public interface.**
- JOSE-102 (jwt-kit 5.3.0) verifies ML-DSA-65 only through `@_spi(PostQuantum)`, which is not public API.
- Primary analysis: TK3. Sensitivity analysis: TK1.

**D3. COSE algorithm identifiers in wolfCOSE.**
- The default wolfCOSE build rejects ES256 (−7) and EdDSA (−8).
- The library documents the build flag `WOLFCOSE_ENABLE_DEPRECATED_ALGS`, which enables them. The target therefore supports −7 through a documented configuration and is measured with that build.
- The default-build behaviour is reported descriptively. The rule for targets that support only −9 does not apply.

**D4. Control-arm label order and battery v1.4 (pre-registration amendment 10).**
- The control arm measures policy expressibility with a second classical algorithm, separately from PQ support. At the JWS/COSE-level gate, 15 targets support neither EdDSA nor Ed25519.
- Label order becomes EdDSA, then Ed25519, then **ES384**: a second classical algorithm of the same family, signed with the battery's deterministic `issuer/ES384` key.
- Battery v1.4 = v1.3 (byte-identical) + 30 ES384 counterparts of the control-arm vectors. Every EdDSA signature is re-made with ES384, recorded corruptions are reproduced, and the K10 alg/key mismatch meaning is kept. The DPoP proof has no counterpart. Generator: `../vector-generator/generator/v14.py`. Independent check: `../vector-generator/tests/t14_es384.py` (341/341, `../vector-generator/results/t14_es384.txt`).
- Oracle v1.4: each kontrol-EdDSA row is copied to the kontrol-ES384 arm with the counterpart vector, which gives 357 rows (`../oracle/merged/derive_v14.py`, `decisions_v14.tsv`). Jobs: `jobs-v1.4.jsonl` (2,202 rows) and `jobs-prefreeze-v1.4.jsonl`.
- v1.4 is mounted at `/v/v1.3` for the adapters. It is a byte-identical superset, so no adapter reads a different file for a v1.3 vector.
- Result (`CONTROL-LABELS.csv`, from the gate on v1.4): EdDSA 17, ES384 13, none 1. SDJWT-021 verifies only ES256, so it cannot express a two-algorithm required set. It is excluded from the primary H6 analysis and counted as Y = 0 in a sensitivity analysis. SDJWT-002 keeps the label EdDSA and the D1 flag.
- Effect on the H6 sample: n_eff for the primary analysis is 30 before any undetermined targets are removed.

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
- `adapters/_tools/run.sh` handles both.

**D8. Outcome of the independent second attempts of the evidence rule (2026-10-03).**
- The rule of pre-registration section 5.14 needs a second, independent attempt for every target whose L4 configuration, which determines Y, is recorded as not expressible. The attempts were made before the freeze in a separate session without access to the adapters (`evidence-rule/`, summary `analysis/evidence-rule.csv`), so that an adapter could still be corrected.
- Rule used to reconcile the attempts, the same as for every other adapter: L4 counts as expressible when the library itself enforces the policy that the caller configures, for example an allow-list or the key that selects the required signer. A check that the caller writes inside a callback, while the library enforces no algorithm policy, is custom code: the level is not raised (section 5.13), Y = 0 and B4 records the lines.
- COSE-034, COSE-001 and SDJWT-025: both attempts find L4 not expressible; the evidence rule is satisfied.
- JOSE-089: the form follows the pre-registered rule, L4m, because the library accepts General JSON objects with several signatures. It verifies only the first signature and has no multi-signature rule, so both attempts agree and the evidence rule is satisfied.
- SDJWT-018 and SDJWT-001: the second attempt reaches the L4c decisions only with about 8 lines of caller code in the documented key or verification callbacks. This is custom code, so Y = 0 with B4.
- COSE-014: the second attempt shows that the library expresses L4 for R = {X} through its documented signer selection (`cose.sign.verify` checks the signer whose kid equals the kid of the verifier key). The first attempt had missed this. The adapter now uses this configuration under L4.
- The same review found two defects of the COSE-014 adapter that the validity gate could not show, because the gate uses single-signature objects with the default issuer key: the kid was passed as text, so no signer of a COSE_Sign message could be found, and the kid was read only from the protected header, while the battery places it in the unprotected header. Both were corrected. A synthetic test with objects outside the battery, built with the issuer keys of the key set, gives 13 of 13 expected decisions (previously 2 of 13).
