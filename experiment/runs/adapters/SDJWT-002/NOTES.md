# SDJWT-002 selective_disclosure_jwt 1.1.1 — adapter notes (01.10.2026)

## 1. Version pinning
- Latest published release 1.1.1 (tag → `54a187b64095`), the environment's `pubspec.lock`.

## 2. TK proposal
| Arm | Proposal | Evidence |
|---|---|---|
| ML-DSA-65 | **TK3** | `SdJwtSignAlgorithm`: ES256/384/512, ES256K, RS*, HS*, EdDSA; no ML-DSA (`evidence/api-tarama.txt`). The `Verifier` interface is an extension point (TK2 out of scope) |
| composite | **TK3** | the same |

## 3. V± result (`evidence/vpm-kosu.txt`) — **FAILED**
- VPLUS_ES256 ×4, VPLUS_EdDSA, VPLUS_EdDSA-ED25519 and their VMINUS counterparts: `istisna/ayristirma` — `SdJwt.parse` throws a `TypeError` via `Hasher.fromString(null)` for the presentation `"<jws>~"`, because the payload has no `_sd_alg` (`sdjwt.dart` L143–144; `evidence/kaynak-alintilari.txt`). Under RFC 9901 `_sd_alg` is optional; the V vectors are plain JWS, not SD-JWT.
- ML-DSA-65, CMP: `red/alg-desteklenmiyor`. COSE B6.
- There is no way to fix this without changing the payload (`SdJwt._fromParts` is private; `verify()` requires an `SdJwt` object) → **adapter invalid (V± gate, with justification).**

## 4. Notes for the maintainers — IMPORTANT
1. **The result of signature verification is ignored (source observation + synthetic smoke test):** `SdJwtVerifyAction.execute` does not use the `bool` returned by `verifyJwt(...)`; if there is no exception it writes `_isJwsVerified = true` (`verify/sd_jwt_verifier.dart`), while `SDKeyVerifier.verify` catches errors and returns `false` (`models/sdkey.dart`). On synthetic (non-battery) SD-JWTs with `_sd_alg`, **the counterparts with corrupted signatures also returned `isVerified == true`** (`evidence/duman-testi.txt`, `SENT_SD_*_MINUS_*`). This is prior knowledge acquired before the freeze (battery/oracle not used); it is recommended to enter it into the PR deviation/prior-knowledge record. No external notification was made.
2. The header alg is checked only for "is it supported"; verification is done with the alg of the `SdPublicKey` (the alg–key binding is not compared with the header).
3. There are no SD-JWT-format (with `_sd_alg`) V+/V− vectors for V±; for this target (and SDJWT-021) the V± gate is meaningful only with a V± pair in SD-JWT VC form — maintainers' decision.
4. **B4:** implementing the `Verifier` interface with `isAllowedAlgorithm(alg) => W.contains(alg)` and a `verify` that delegates to `SDKeyVerifier` ≈ 6 lines of Dart (not written).

## 5. Run record
- Smoke test `evidence/duman-testi.txt` (including the synthetic `SENT_SD_*`). Pre-freeze file: 13:48Z, ~13:59Z, 14:05Z; V± the same.
