# JOSE-102 jwt-kit — policy → API mapping (contract 1.0 §2.2, RUNNER §2)

- **Target:** vapor/jwt-kit **5.3.0** (`b5f82fb9dc23`; not the frame HEAD `0c74d3201bff`) + swift-crypto 4.5.2, swift-asn1 1.7.3, swift-certificates 1.21.0, swift-log 1.15.1 — `Package.resolved` the same as the environment.
- **Image:** `a10-jose-102:1` (`FROM pq-a09-env-swift:1.0`; Swift 6.4, Linux). **Call:** `… a10-jose-102:1 adaptor /is/<isler> /c/JOSE-102.<kosu>.jsonl`.
- **Source:** `Sources/Adaptor/Adaptor.swift`, `Package.swift`.

## 1. Shared rules
The same as `JOSE-087/MAPPING.md` §1 (normalisation, P2, L4-YOL → `ifade-edilemedi`). Clock: `exp.verifyNotExpired(currentDate: simdi)` inside the payload type `Yuk: JWTPayload` (the documented payload verification pattern of jwt-kit). The job file is read CRLF-safely.

## 2. Policy mechanism: key object registered in the collection
jwt-kit has no allow-list. `JWTKeyCollection.verify` selects the signer by kid (the default if there is no kid) and **verifies the signature with the algorithm of the registered key object; the header `alg` is not compared with the signer** (`JWTSigner.swift` verify, `evidence/api-scan.txt`). The policy is therefore built by **which key object is registered**:
- Key path **`dogrudan`** (in all arms): EC → `ES256PublicKey/ES384PublicKey(parameters: (x, y))`, OKP → `EdDSA.PublicKey(x:curve: .ed25519)`, AKP → `MLDSA65PublicKey/MLDSA87PublicKey(rawRepresentation:)` (`@_spi(PostQuantum) import JWTKit`; README section "MLDSA").
- If the natural alg of the key is in W_effective, `keys.add(ecdsa:|eddsa:|mldsa:, kid:)`; otherwise the collection stays empty → the library gives `JWTError.noKeyProvided`.

| Policy | Registration |
|---|---|
| GEC / P0 / P1 / P2 / VARSAYILAN | the key is always registered (if the natural alg exists in the library) |
| IZIN-A / IZIN-AX | natural alg ∈ {ES256} / {ES256, X} |
| L4 / L4-S / L4-Y (compact) | natural alg ∈ {X} |
| L4-YOL | `ifade-edilemedi` |

`dogrulanan_algoritmalar`: on acceptance the algorithm of the registered key (the library verifies with it).

## 3. B6 decisions
| Serialization | Decision |
|---|---|
| compact | supported (`DefaultJWTParser`, 3 parts) |
| general, sd-jwt-*, oid4vci-toplu-yanit, dcapi-json-parametre, COSE_* | **B6** (no JWS JSON/SD-JWT/COSE API) |

## 4. Error → hata_sinifi
| Library error | hata_sinifi |
|---|---|
| `JWTError.signatureVerificationFailed` | `imza-gecersiz` |
| `.claimVerificationFailure` (exp) | `zaman` |
| `.malformedToken`, `.invalidHeaderField` | `ayristirma` |
| `.noKeyProvided`, `.unknownKID`: header alg not in the library / alg ∉ W / otherwise | `alg-desteklenmiyor` / `alg-izin-disi` / `anahtar-bulunamadi` |
| the key object could not be built, or the key type does not exist in the library (composite) | `alg-desteklenmiyor` |
| other | `istisna-diger` |
