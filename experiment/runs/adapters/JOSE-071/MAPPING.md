# JOSE-071 lcobucci/jwt — policy → API mapping (contract 1.0 §2.2, RUNNER §2)

- **Target:** `lcobucci/jwt` 5.6.0 (`bb3e9f21e419`; not the frame HEAD `2bead08a8cc2`) + `psr/clock` 1.0.0; `composer.lock` the same as the environment record. (`SECIM.csv` JOSE-071 = packagist `lcobucci/jwt`.)
- **Image:** `a10-jose-071:1` (`FROM pq-a09-env-php:1.0`). **Call:** `… a10-jose-071:1 adaptor /is/<isler> /c/JOSE-071.<kosu>.jsonl`.
- **Source:** `adaptor.php`, `ortak.php` (same skeleton as JOSE-070).

## 1. Shared rules
The same as `JOSE-087/MAPPING.md` §1. Clock: a PSR-20 `ClockInterface` that returns `simdi`, passed into `LooseValidAt(saat)` and `SignedWithUntilDate(..., saat)` (a 3-line anonymous class in the adapter).
- **Policy name normalisation (maintainers 01.10):** `temel = politika.split('|')[0].split('@')[0]` (the suffixes `|sdjwtvc=…`, `@-19` only split the oracle); the original `politika` is written to the output. **P2** (P1 + key–alg binding) is in the GEC/P0/P1 set.

## 2. Policy → API
lcobucci/jwt has no JWK parser and no global allow-list. Documented verification: `Validator::assert($token, ...Constraint)`; the signature constraint `SignedWith(Signer, Key)` compares the header `alg` with `Signer::algorithmId()` and then verifies the signature (`Validation/Constraint/SignedWith.php`). For several (signer, key) pairs `SignedWithOneInSet(SignedWithUntilDate…)`.

| Policy | Constraints |
|---|---|
| GEC / P0 / P1 / VARSAYILAN | `SignedWithOneInSet` (ES256, ES384, EdDSA signers × the selected key) + `LooseValidAt(simdi)` |
| IZIN-A / IZIN-AX | (Signer, key) for every alg in W; an alg without a signer in the library (ML-DSA-65, composite, the label `Ed25519`) cannot be added |
| L4 / L4-S / L4-Y (compact) | effective allow-list R = {X}; if X has no signer, the constraint set stays empty and the library throws `NoConstraintsGiven` (→ `red/alg-desteklenmiyor`) |
| L4-YOL | X5C (SD-JWT) → B6; in a supported format `ifade-edilemedi` (no path-class API) |

- **Key path (`dogrudan`):** the selected JWK is converted in the adapter into the form the library expects: EC → SubjectPublicKeyInfo PEM (RFC 5480 prefix + 04‖x‖y), OKP Ed25519 → raw 32 bytes (`Eddsa` expects sodium), `InMemory::plainText`. The same path in all arms.
- On acceptance `dogrulanan_algoritmalar = [{alg: $token->headers()->get('alg')}]` (SignedWith verifies only with the matching signer).

## 3. B6 decisions
| Serialization | Decision |
|---|---|
| compact | supported (`Token\Parser::parse`) |
| general, sd-jwt-*, oid4vci-toplu-yanit, dcapi-json-parametre, COSE_* | **B6** (no JSON serialization/SD-JWT/COSE API) |

## 4. Exception → hata_sinifi
| Library exception | hata_sinifi |
|---|---|
| "Token signature mismatch" inside `RequiredConstraintsViolated` | `imza-gecersiz` |
| only "Token signer mismatch": alg not in the library / alg ∉ W / alg ∈ W | `alg-desteklenmiyor` / `alg-izin-disi` / `alg-anahtar-uyusmazligi` |
| "issued in the future", "cannot be used yet", "is expired" | `zaman` |
| `NoConstraintsGiven` (no signer for any alg of W) | `alg-desteklenmiyor` |
| `Signer\InvalidKeyProvided`, `Ecdsa\ConversionFailed` | `alg-anahtar-uyusmazligi` |
| `InvalidTokenStructure`, `CannotDecodeContent`, `UnsupportedHeaderFound` | `ayristirma` |
| other | `istisna-diger` |

`hata_ozeti`: the fixed introductory sentences of the library are shortened (to "ihlaller:" (violations) and "imza kumesi:" (signature set)); the texts of the violations are kept.
