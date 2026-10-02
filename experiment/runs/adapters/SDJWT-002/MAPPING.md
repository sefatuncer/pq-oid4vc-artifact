# SDJWT-002 selective_disclosure_jwt (affinidi-sdjwt-dart) — policy → API mapping (contract 1.0 §2.2, RUNNER §2)

- **Target:** pub.dev `selective_disclosure_jwt` **1.1.1** (tag `selective_disclosure_jwt-v1.1.1` → `54a187b64095`), `pubspec.lock` the same as the environment (`dart pub get --enforce-lockfile`; transitive `dart_jsonwebtoken`, `pointycastle`).
- **Image:** `a10-sdjwt-002:1` (`FROM pq-a09-env-dart:1.0`, analytics off; `dart compile exe`). **Call:** `… a10-sdjwt-002:1 adaptor /is/<isler> /c/SDJWT-002.<kosu>.jsonl`.
- **Source:** `bin/adaptor.dart` (skeleton + adapter).

## 1. Shared rules
The same as `JOSE-087/MAPPING.md` §1 (normalisation, P2, L4-YOL → `ifade-edilemedi`).

## 2. Policy → API
Documented route (README "Usage"): `SdJwtHandlerV1().decodeAndVerify(sdJwtToken: s, verifier: SDKeyVerifier(SdPublicKey(jwk_map, SdJwtSignAlgorithm.x)), verifyKeyBinding: kb)` → `SdJwt.isVerified`.
- `SDKeyVerifier.isAllowedAlgorithm(alg)` = `SdJwtSignAlgorithm.isSupported(alg)` (fixed: every alg the library supports); **the signature is verified with the algorithm bound to the `SdPublicKey`** (not with the header alg; `sdkey.dart` SDKeyVerifier). The policy is therefore built with a **key–alg pin**.

| Policy | Configuration |
|---|---|
| GEC / P0 / P1 / P2 / VARSAYILAN | `SdPublicKey(jwk, natural_alg)` (EC P-256 → es256, P-384 → es384, OKP → eddsa) |
| IZIN-A / IZIN-AX | pin = the natural alg if it is in W∩supported, otherwise the first of W∩supported; if W∩supported is empty, no verifier can be built → `red/alg-desteklenmiyor` (the library is not called) |
| L4 / L4-S / L4-Y | the same rule, W_effective = R = {X} |
| L4-YOL | `ifade-edilemedi` |

- `verifyKeyBinding = (artefakt == "sd-jwt-vc+kb")`; there is no API parameter for `kb_aud`/`kb_nonce`.
- A custom implementation of the `Verifier` interface (`isAllowedAlgorithm` = W) is a documented extension point; it was not used because it counts as custom code (B4 candidate, NOTES).
- **Key path `JWK`** (JWK map → `JWTKey.fromJWK`). **x5c:** the API takes no x5c; in the X5C vectors the key is given via the manifest kid.
- **Presentation:** compact `jws-cekirdek` vectors as `"<jws>~"` (maintainers' rule); for the OID4VCI batch response `credentials[0]`.
- `dogrulanan_algoritmalar`: on acceptance the pinned alg (the library verifies the signature with this alg).

## 3. B6 decisions
| Serialization / artefact | Decision |
|---|---|
| sd-jwt-compact; compact `jws-cekirdek` (`"<jws>~"`); oid4vci-toplu-yanit | supported |
| compact `dpop`, `status-list-token`, `oid4vp-istek`; general; sd-jwt-general; sd-jwt-flattened; dcapi-json-parametre; COSE_* | **B6** (`SdJwt.parse` only `~`-separated compact SD-JWT) |

## 4. Result → hata_sinifi
The library swallows the signature error (`sd_jwt_verifier.dart`: exception → `_isJwsVerified = false`); when `isVerified == false`, the class is inferred from the header alg, W and the pin:
| Case | hata_sinifi |
|---|---|
| `isVerified != true`, alg not in the library | `alg-desteklenmiyor` |
| alg ∉ W | `alg-izin-disi` |
| alg ≠ pin | `alg-anahtar-uyusmazligi` |
| otherwise (`kb` if KB was required) | `imza-gecersiz` / `kb` |
| `SdJwt.parse` exception ("Invalid SD-JWT …", `TypeError` when `_sd_alg` is missing) | `ayristirma` (`TypeError` → `sonuc_ham = istisna`) |
| `SdPublicKey` could not be built (AKP) / pin could not be built | `alg-desteklenmiyor` |
| other | `istisna-diger` |
