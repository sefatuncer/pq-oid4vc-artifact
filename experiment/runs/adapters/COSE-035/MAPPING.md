# COSE-035 web-auth/cose-lib — politika → API eşlemesi (sözleşme 1.0 §2.2, KOSUCU §2)

- **Hedef:** `web-auth/cose-lib` **4.8.2** (`8849e8bf043a`) + `spomky-labs/cbor-php` 3.4.2 (ortam düzeltmesi; cose-lib `suggest`), `composer.lock` ortam kaydıyla aynı.
- **İmaj:** `a10-cose-035:1` (`FROM pq-a09-env-php:1.0`; PHP 8.4.26, OpenSSL 3.5.8). **Çağrı:** `… a10-cose-035:1 adaptor /is/<isler> /c/COSE-035.<kosu>.jsonl`.
- **Kaynak:** `adaptor.php`, `ortak.php` (JOSE-070 ile aynı iskelet).

## 1. Ortak kurallar
`JOSE-087/MAPPING.md` §1 ile aynı (A/X, W/R, tek imzada etkin izin listesi = R, VARSAYILAN, yalnız `dogrulama_girdileri`, politika adı normalleştirme `split('|')[0].split('@')[0]`, P2 ∈ {GEC, P0, P1}). COSE kimlikleri (BATARYA-ESLEME §3): ES256 −7, ES384 −35, EdDSA −8, Ed25519 −19, ML-DSA-65 −49, ML-DSA-65-ES256 −55.

## 2. Belgeli doğrulayıcı = README kalıbı
cose-lib bir ilkel kütüphanesidir. README "Verifying a COSE_Sign1 Signature": *"The library verifies signatures; it does not decide what a message is allowed to say. Checking that `alg` is the one expected for that key, and refusing any `crit` label … are the caller's responsibility"* (`tests/Signature/DocumentedVerifierTest.php` bu kodu koşar). Adaptör kalıbı birebir izler:
`Decoder::create()->decode()` → `CoseHeaders::fromMessage()` → korumalı `alg` (etiket 1) → izin listesi → `crit` (anlaşılan etiketler {1, 2}) → ayrık yük reddi → `Signature1::create(protected, payload)` (COSE_Sign'da `Signature::create(body_protected, sign_protected, payload)`) → `$algorithm->verify((string)$yapi, $key, $sig)`.

| Politika | Yapılandırma |
|---|---|
| GEC / P0 / P1 / P2 / VARSAYILAN | `Manager::create()->add(ES256, ES384, EdDSA, FullySpecified\Ed25519)`; `Manager::has(alg)` izin listesidir |
| IZIN-A / IZIN-AX | Manager = W ∩ yerel (ML-DSA-65/composite eklenemez) |
| L4 / L4-S / L4-Y (COSE_Sign1 ya da tek imzacılı COSE_Sign) | Manager = {X} (etkin izin listesi = R) |
| çok imzacılı COSE_Sign × her politika | **`ifade-edilemedi`**: imzacılar üzerinde kural (P0/P1/R) için belgeli seçenek yok; `CoseSignature::all()` listesini dolaşan döngü çağıranın kodu olur (B4) |
| L4-YOL | **`ifade-edilemedi`**: x5chain yol sınıfı politikası (B2) için belgeli API yok |

- **Anahtar yolu `COSE_Key`:** `dogrulama_girdileri.cose_key_hex[kid]` CBOR ile çözülür → `Key::createFromData()` (kty'ye göre Ec2Key/OkpKey). kid, başlık etiketi 4'ten (korumasız) okunur. Anahtar kısıtı uygulaması (`withKeyRestrictionsEnforced`) varsayılan (kapalı); bataryadaki EC2/OKP anahtarları `alg` (etiket 3) taşımaz.
- Kabulde `dogrulanan_algoritmalar = [{alg: COSE kimliğinin JOSE adı}]`.

## 3. B6 kararları
| Serileştirme | Karar |
|---|---|
| COSE_Sign1, COSE_Sign | desteklenir |
| compact, general, sd-jwt-*, oid4vci-toplu-yanit, dcapi-json-parametre | **B6** (JOSE/SD-JWT API'si yok) |

## 4. Hata → hata_sinifi
| Durum | hata_sinifi |
|---|---|
| CBOR çözülemedi / COSE_Sign1-COSE_Sign değil / korumalı `alg` yok / ayrık yük | `ayristirma` |
| `Manager::has(alg)` yanlış: alg kütüphanede var / yok (−49, −55, kayıtsız) | `alg-izin-disi` / `alg-desteklenmiyor` |
| `crit` dizi değil ya da anlaşılmayan etiket | `crit` |
| kid için COSE_Key yok | `anahtar-bulunamadi` |
| `Key::createFromData` başarısız | `alg-desteklenmiyor` |
| `verify()` istisna (anahtar türü ≠ alg) | `alg-anahtar-uyusmazligi` |
| `verify()` false | `imza-gecersiz` |
| diğer | `istisna-diger` |
