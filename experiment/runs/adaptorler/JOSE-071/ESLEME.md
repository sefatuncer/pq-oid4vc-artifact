# JOSE-071 lcobucci/jwt — politika → API eşlemesi (sözleşme 1.0 §2.2, KOSUCU §2)

- **Hedef:** `lcobucci/jwt` 5.6.0 (`bb3e9f21e419`; çerçeve HEAD `2bead08a8cc2` değil) + `psr/clock` 1.0.0; `composer.lock` ortam kaydıyla aynı. (`SECIM.csv` JOSE-071 = packagist `lcobucci/jwt`.)
- **İmaj:** `a10-jose-071:1` (`FROM pq-a09-env-php:1.0`). **Çağrı:** `… a10-jose-071:1 adaptor /is/<isler> /c/JOSE-071.<kosu>.jsonl`.
- **Kaynak:** `adaptor.php`, `ortak.php` (JOSE-070 ile aynı iskelet).

## 1. Ortak kurallar
`JOSE-087/ESLEME.md` §1 ile aynı. Saat: `LooseValidAt(saat)` ve `SignedWithUntilDate(..., saat)` içine `simdi` döndüren PSR-20 `ClockInterface` (adaptörde 3 satırlık anonim sınıf).
- **Politika adı normalleştirme (yürütücü 01.10):** `temel = politika.split('|')[0].split('@')[0]` (`|sdjwtvc=…`, `@-19` ekleri yalnız oracle'ı böler); çıktıya özgün `politika` yazılır. **P2** (P1 + anahtar–alg bağlama) GEC/P0/P1 kümesindedir.

## 2. Politika → API
lcobucci/jwt'de JWK ayrıştırıcısı ve global izin listesi yoktur. Belgeli doğrulama: `Validator::assert($token, ...Constraint)`; imza kısıtı `SignedWith(Signer, Key)` başlık `alg`'ını `Signer::algorithmId()` ile karşılaştırır, sonra imzayı doğrular (`Validation/Constraint/SignedWith.php`). Birden çok (imzalayıcı, anahtar) çifti için `SignedWithOneInSet(SignedWithUntilDate…)`.

| Politika | Kısıtlar |
|---|---|
| GEC / P0 / P1 / VARSAYILAN | `SignedWithOneInSet` (ES256, ES384, EdDSA imzalayıcıları × seçilen anahtar) + `LooseValidAt(simdi)` |
| IZIN-A / IZIN-AX | W'deki her alg için (Signer, anahtar); kütüphanede imzalayıcısı olmayan alg (ML-DSA-65, composite, `Ed25519` etiketi) eklenemez |
| L4 / L4-S / L4-Y (kompakt) | etkin izin listesi R = {X}; X'in imzalayıcısı yoksa kısıt kümesi boş kalır ve kütüphane `NoConstraintsGiven` atar (→ `red/alg-desteklenmiyor`) |
| L4-YOL | X5C (SD-JWT) → B6; desteklenen biçimde `ifade-edilemedi` (yol sınıfı API'si yok) |

- **Anahtar yolu (`dogrudan`):** seçilen JWK adaptörde kütüphanenin beklediği biçime çevrilir: EC → SubjectPublicKeyInfo PEM (RFC 5480 öneki + 04‖x‖y), OKP Ed25519 → ham 32 bayt (`Eddsa` sodium bekler), `InMemory::plainText`. Bütün kollarda aynı yol.
- Kabulde `dogrulanan_algoritmalar = [{alg: $token->headers()->get('alg')}]` (SignedWith yalnız eşleşen imzalayıcıyla doğrular).

## 3. B6 kararları
| Serileştirme | Karar |
|---|---|
| compact | desteklenir (`Token\Parser::parse`) |
| general, sd-jwt-*, oid4vci-toplu-yanit, dcapi-json-parametre, COSE_* | **B6** (JSON serileştirme/SD-JWT/COSE API'si yok) |

## 4. İstisna → hata_sinifi
| Kütüphane istisnası | hata_sinifi |
|---|---|
| `RequiredConstraintsViolated` içinde "Token signature mismatch" | `imza-gecersiz` |
| yalnız "Token signer mismatch": alg kütüphanede yok / alg ∉ W / alg ∈ W | `alg-desteklenmiyor` / `alg-izin-disi` / `alg-anahtar-uyusmazligi` |
| "issued in the future", "cannot be used yet", "is expired" | `zaman` |
| `NoConstraintsGiven` (W'nin hiçbir alg'ı için imzalayıcı yok) | `alg-desteklenmiyor` |
| `Signer\InvalidKeyProvided`, `Ecdsa\ConversionFailed` | `alg-anahtar-uyusmazligi` |
| `InvalidTokenStructure`, `CannotDecodeContent`, `UnsupportedHeaderFound` | `ayristirma` |
| diğer | `istisna-diger` |

`hata_ozeti`: kütüphanenin sabit giriş cümleleri kısaltılır ("ihlaller:", "imza kumesi:"), ihlal metinleri korunur.
