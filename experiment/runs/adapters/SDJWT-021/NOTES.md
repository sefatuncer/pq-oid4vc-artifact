# SDJWT-021 WalletFramework.SdJwtVc 3.1.0 — adapter notes (01.10.2026)

## 1. Version pinning
- Latest published release 3.1.0 (two conflicting tags; resolved with the nuspec commit `2ed7a64b9c44` — environment record). Source quotations from the same commit (GitHub, anonymous, temporary image `a10-sdjwt-021-kaynak:1` for reading only; deleted afterwards).

## 2. TK proposal
| Arm | Proposal | Evidence |
|---|---|---|
| ML-DSA-65 | **TK3** | `SdJwtDoc.cs` L61 `ValidAlgorithms = new string[] {"ES256"}`; no ML-DSA in the transitive IdentityModel 8.0.1 (`evidence/api-tarama.txt`) |
| composite | **TK3** | the same |

## 3. V± result (`evidence/vpm-kosu.txt`) — **FAILED**
- VPLUS_ES256 ×4: `red/typ` — inner cause IDX10257 "Type: 'JWT'. Did not match: validationParameters.ValidTypes" (the library accepts only `vc+sd-jwt`; the V vectors have `typ: JWT`).
- VMINUS_ES256 ×4: `red/imza-gecersiz`. EdDSA/Ed25519/ML-DSA-65/CMP: `red/alg-desteklenmiyor`. COSE B6.
- **Correction attempts (2):**
  1. The route `Verifier.VerifyPresentation` (on synthetic data; `evidence/deneme1-verifypresentation.txt`): a valid token was rejected with IDX10208; in the source the method always returns `false` (`evidence/kaynak-alintilari.txt`).
  2. The route `SdJwtDoc.AssertThatJwtSignatureIsValid` (battery V±): V+ was rejected because of the fixed `typ`.
  - The library has no other public verification route; `typ` and alg are hard-coded (`SdJwtDoc.cs` L55–62) → cannot be fixed with the adapter.
- **Result: adapter invalid (V± gate, with justification).** In the synthetic smoke test a token with `typ: vc+sd-jwt` + ES256 is accepted and its corrupted counterpart rejected (`evidence/duman-testi.txt`, SENT_SD_vc_*): the adapter route works; the cause of the rejection is a restriction of the library.

## 4. Notes for the maintainers
1. **The public API of the target also rejects -13 SD-JWT VCs (`typ: dc+sd-jwt`)** (only `vc+sd-jwt`): most VC* vectors of the battery will fail on `typ`. The measurement scope (outside n_eff, or a delegation set via JOSE-001) is the maintainers' decision.
2. **Version difference in the delegation:** IdentityModel 8.0.1/7.5.2 (JOSE-001: 8.23.0).
3. No policy parameter → the IZIN/L4 family is `ifade-edilemedi`. For the evidence rule "not expressible" (contract §5.5): the scan is recorded, the source lines are recorded (`SdJwtDoc.cs` L49–73, `Verifier.cs`); a second independent work attempt is needed.
4. B4 alternative: verifying `SdJwtDoc.IssuerSignedJwt` directly with the IdentityModel `JsonWebTokenHandler` (≈ 10 lines) — this would measure IdentityModel, not WalletFramework.

## 5. Run record
- Pre-freeze file: 13:13Z, ~13:59Z (normalisation) and 14:05Z; V± the same. (The L4-YOL change did not change code for this target; `adaptor_sha256` is the same since the 13:59Z run.)
