# JOSE-001 Microsoft.IdentityModel 8.23.0 — adapter notes (01.10.2026)

## 1. Version pinning
- Latest published release 8.23.0 (2026-09-18; nuspec commit `8b16f418b3d5`; not the frame HEAD `80995d99c3dd`). The environment's `packages.lock.json` (`System.IdentityModel.Tokens.Jwt` 8.23.0 direct; `Microsoft.IdentityModel.JsonWebTokens/Tokens` 8.23.0 transitive) exactly.

## 2. TK proposal
| Arm | Proposal | Evidence |
|---|---|---|
| ML-DSA-65 | **TK1** | Public API: `SecurityAlgorithms.MlDsa65 = "ML-DSA-65"`, `MlDsaSecurityKey`, `JsonWebAlgorithmsKeyTypes.Akp = "AKP"`, `JsonWebKey.Pub`, `JsonWebKeyConverter.ConvertFromMlDsaSecurityKey` (`evidence/api-scan.txt`). Runtime: .NET 10 `MLDsa` + OpenSSL 3.5.5. The V± gate passed in the ML-DSA arm (below) |
| composite | **TK3** | composite/`ML-DSA-65-ES256` pattern 0 matches; CMP00 `red/alg-desteklenmiyor` |

## 3. V± result (`evidence/vpm-run.txt`)
- ES256: VPLUS ×4 `kabul` (`dogrulanan: ES256`), VMINUS ×4 `red/imza-gecersiz`.
- **ML-DSA-65: VPLUS_ML-DSA-65 `kabul` (`dogrulanan: ML-DSA-65`), VMINUS_ML-DSA-65 `red/imza-gecersiz`** → TK1 confirmed.
- EdDSA / Ed25519: `red/alg-desteklenmiyor` (IdentityModel has no EdDSA).
- CMP00/CMP01: `red/alg-desteklenmiyor` (composite TK3). COSE rows B6.
- **Gate: passed (ES256 + ML-DSA-65).**

## 4. Issues and notes for the maintainers
1. **No control arm X:** EdDSA/Ed25519 not supported → in the control arm the L measurement cannot be made with X = EdDSA. Since the ML-DSA arm is TK1, allow-list behaviour similar to L2/L4c can be observed in the treatment arm.
2. **Delegation:** SDJWT-021 delegates to IdentityModel, but **with a different version** (Tokens 8.0.1 / System.IdentityModel.Tokens.Jwt 7.5.2; no ML-DSA support).
3. L4c: `IssuerSigningKeys` + `ValidAlgorithms` per call; the only documented single-object mechanism for a per-issuer alg set is the callbacks `IssuerSigningKeyResolver`/`AlgorithmValidator` (custom code → B4 candidate, ≈ 6 lines; not used).
4. Multi-signature B6 (no JWS JSON serialization); no B4 candidate.

## 5. Run record
- Synthetic smoke test `evidence/smoke-test.txt` (synthetic ML-DSA-65 tokens are also accepted/rejected correctly).
- Pre-freeze file: 13:06Z (first run), ~13:59Z (normalisation), 14:05Z (L4-YOL rule) — V± results the same in all three; the last output reflects the current image.
