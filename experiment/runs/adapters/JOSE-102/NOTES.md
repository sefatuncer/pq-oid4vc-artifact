# JOSE-102 jwt-kit 5.3.0 — adapter notes (01.10.2026)

## 1. Version pinning
- Latest published release 5.3.0 (`b5f82fb9dc23`), the environment's `Package.resolved` (git revisions pinned).

## 2. TK proposal
| Arm | Proposal | Evidence |
|---|---|---|
| ML-DSA-65 | **TK1** | `Sources/JWTKit/MLDSA/*` (`MLDSA65PublicKey`, `JWTKeyCollection.add(mldsa:)`), README L276–297 (documented; behind the `@_spi(PostQuantum)` flag). `@available(macOS 26)` does not restrict Linux; swift-crypto CryptoExtras MLDSA worked on Linux. V± passed in the ML-DSA arm |
| composite | **TK3** | no composite pattern; CMP00 `red/alg-desteklenmiyor` |

## 3. V± result (`evidence/vpm-run.txt`)
- ES256 ×4 `kabul` / VMINUS ×4 `red/imza-gecersiz`; EdDSA `kabul` / VMINUS `red`; VPLUS_EdDSA-ED25519 (header `Ed25519`) `kabul` / VMINUS `red`.
- **ML-DSA-65: VPLUS `kabul` (`dogrulanan: ML-DSA-65`), VMINUS `red/imza-gecersiz`.**
- CMP00/01: `red/alg-desteklenmiyor`. COSE B6.
- **Gate: passed (ES256 + EdDSA + ML-DSA-65).** Control label `EdDSA` (the label `Ed25519` is not documented; the library accepted because it verifies with the EdDSA key without looking at the header label).

## 4. Notes for the maintainers
1. **SPI decision:** the ML-DSA API is behind `@_spi(PostQuantum)` (a "breaking changes" warning); documented in the README. Counting it as TK1 requires the maintainers' approval of the interpretation "documented public API" (the inventory note "macOS 26+" does not apply on Linux — consistent with the environment record).
2. **The header alg is not compared (source observation):** `JWTSigner.verify` verifies the signature only with the registered algorithm (`evidence/api-scan.txt`, JWTSigner.swift). The alg–key mismatch cases (K10) and label sensitivity will therefore be interesting; not measured here.
3. W can be built only with the set of registered keys (MAPPING §2) — a single signer per kid; a per-issuer policy (L4c) is expressed through the collection setup.
4. Multi-signature B6; no B4 candidate. The Swift driver has no 60 s limit per vector (async calls in sequence).

## 5. Run record
- Smoke test `evidence/smoke-test.txt`. In the first version the job file was read with `split("\n")`; with CRLF line endings (in Swift `"\r\n"` is a single Character) it looked like a single line and crashed → `components(separatedBy: .newlines)` (found on synthetic data before the battery run).
- Pre-freeze file: 13:57Z, ~13:59Z, 14:05Z; V± the same.
