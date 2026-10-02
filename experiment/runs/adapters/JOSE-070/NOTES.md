# JOSE-070 firebase/php-jwt 7.2.0 — adapter notes (01.10.2026)

## 1. Version pinning
- Latest published release v7.2.0 = frame `son_commit_sha` `f502cdbf279c` (composer.lock `dist.reference`). The environment's `composer.lock` exactly; `HEDEF_SURUM` from the lock.

## 2. TK proposal
| Arm | Proposal | Evidence |
|---|---|---|
| ML-DSA-65 | **TK3** | `JWT::$supported_algs` (`JWT.php` L57–69): ES384, ES256, ES256K, HS*, RS*, PS256, EdDSA; ML-DSA/composite/AKP 0 matches (`evidence/api-tarama.txt`) |
| composite | **TK3** | the same |

## 3. V± result (`evidence/vpm-kosu.txt`)
- ES256: VPLUS `kabul` ×4, VMINUS `red/imza-gecersiz` ×4.
- EdDSA (kontrol-EdDSA): VPLUS_EdDSA `kabul`, VMINUS_EdDSA `red/imza-gecersiz`.
- Label `Ed25519` (kontrol-Ed25519): `red/alg-desteklenmiyor` → the control arm is run with `EdDSA` (contract §8 item 4).
- ML-DSA-65, CMP00/01: `red/alg-desteklenmiyor`. COSE rows B6.
- **Gate: passed (ES256 + EdDSA).**

## 4. Notes
1. The policy mechanism is only the key–alg binding (MAPPING §2). For a token with a non-permitted alg the library returns `"kid" invalid`; the adapter classifies this as `alg-izin-disi` (reason in MAPPING §4).
2. L3: the binding is documented and explicit (`Key` alg ≠ header alg → "Incorrect key for this algorithm").
3. L4c: an array `[kid => Key]` is given to the same `JWT::decode` call; a different alg binding per issuer (per kid) can be set up in the same array (a candidate documented mechanism for L4c).
4. Multi-signature B6 → no L4m; no B4 candidate.

## 5. Run record
- Synthetic smoke test `evidence/duman-testi.txt`. In the first smoke run, when only the selected key was given, "Key may not be empty" came in every non-permitted case; this was corrected so that the key set is built from the vector JWKS (before the battery run).
- The pre-freeze file was run once (12:54Z, 32 rows).
- **Last run (~13:59Z):** after the maintainers' policy-name normalisation rule (`|sdjwtvc=`, `@-19`; P2) was added, the image was rebuilt and the same 32-row file was rerun; the results did not change, `adaptor_sha256` reflects the current image.
- **Last run (14:05Z):** after the rule L4-YOL → `ifade-edilemedi` was added, the image was rebuilt and the same 32-row file was rerun (V± results unchanged).
