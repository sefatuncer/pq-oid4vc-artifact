# JOSE-070 firebase/php-jwt — policy → API mapping (contract 1.0 §2.2, RUNNER §2)

- **Target:** `firebase/php-jwt` v7.2.0 (`f502cdbf279c`, the same as the frame HEAD), `composer.lock` the same as the environment record.
- **Image:** `a10-jose-070:1` (`FROM pq-a09-env-php:1.0`; PHP 8.4.26, OpenSSL 3.5.8, sodium). `composer install` only when the image is built.
- **Call:** `docker run --rm --network none -v <v1.3>:/v:ro -v <anahtarlar>:/anahtarlar:ro -v <isler>:/is:ro -v <cikti>:/c a10-jose-070:1 adaptor /is/<isler> /c/JOSE-070.<kosu>.jsonl`
- **Source:** `adaptor.php`, `ortak.php` (same skeleton as JOSE-071 and COSE-035).

## 1. Shared rules
The same as `JOSE-087/MAPPING.md` §1 (A/X, W/R, effective allow-list for a single signature = R, VARSAYILAN, only `dogrulama_girdileri`). Clock: `JWT::$timestamp = simdi` (the public static clock field of php-jwt; contract §2.1).
- **Policy name normalisation (maintainers 01.10):** `temel = politika.split('|')[0].split('@')[0]` (the suffixes `|sdjwtvc=…`, `@-19` only split the oracle); the original `politika` is written to the output. **P2** (P1 + key–alg binding) is in the GEC/P0/P1 set.

## 2. Policy mechanism: key–alg binding
php-jwt has no separate allow-list; the algorithm is bound to the object `Key(material, alg)`, and `decode` compares the header alg with the alg of the key (`JWT.php` L148–158). W is therefore expressed **by the construction of the key set**:
- For every JWK in the vector's JWKS the natural alg of the key type is computed (EC P-256 → ES256, P-384 → ES384, OKP Ed25519 → EdDSA [`Ed25519` in the kontrol-Ed25519 arm], AKP → the JWK `alg`).
- The JWKs whose natural alg ∈ W are converted into a `Key` with `JWK::parseKey($jwk, $alg)` → `[kid => Key]` (`anahtar_yolu = JWKS`).
- If the header has no `kid` (REQ01/02, TSL01/02, DPoP), the selected JWK is given as a single `Key` (`anahtar_yolu = JWK` / `jwk-basligi`).

| Policy | Configuration |
|---|---|
| GEC / P0 / P1 | all keys whose natural alg ∈ {ES256, ES384, EdDSA} |
| IZIN-A / IZIN-AX | natural alg ∈ {ES256} / {ES256, X} |
| L4 / L4-S / L4-Y (compact, single signature) | natural alg ∈ {X} (effective allow-list = R) |
| VARSAYILAN | the same as GEC (in php-jwt the alg is always bound to the key) |
| L4-YOL | X5C (SD-JWT) → B6; in a supported format `ifade-edilemedi` (no path-class API) |

Call: `JWT::decode($jwt, $anahtarlar, $hdr)`; on acceptance `dogrulanan_algoritmalar = [{alg: $hdr->alg}]` (php-jwt verifies only if the `Key` alg equals the header alg).

## 3. B6 decisions
| Serialization | Decision | Basis |
|---|---|---|
| compact | supported | `JWT::decode` (`explode('.', $jwt, 4)`, 3 parts) |
| general, sd-jwt-* , oid4vci-toplu-yanit, dcapi-json-parametre | **B6** | no JSON serialization and no SD-JWT API (`evidence/api-tarama.txt`) |
| COSE_Sign, COSE_Sign1 | **B6** | no COSE |

## 4. Exception → hata_sinifi
| Library exception | hata_sinifi |
|---|---|
| `UnexpectedValueException` "Algorithm not supported" | `alg-desteklenmiyor` |
| "Incorrect key for this algorithm" | `alg-anahtar-uyusmazligi` |
| `"kid" invalid` / `"kid" empty` / `InvalidArgumentException` "Key may not be empty", header alg ∉ W | `alg-izin-disi` (because W is built with the key binding) |
| the same, header alg ∈ W | `anahtar-bulunamadi`; `alg-desteklenmiyor` if the selected key type could not be built with `parseKey` (AKP) |
| `SignatureInvalidException` | `imza-gecersiz` |
| `ExpiredException`, `BeforeValidException` | `zaman` |
| segment/encoding/"Payload must be"/"Empty algorithm" messages | `ayristirma` |
| `DomainException` (OpenSSL/sodium) and others | `istisna-diger` |
