# JOSE-070 firebase/php-jwt — politika → API eşlemesi (sözleşme 1.0 §2.2, KOSUCU §2)

- **Hedef:** `firebase/php-jwt` v7.2.0 (`f502cdbf279c`, çerçeve HEAD ile aynı), `composer.lock` ortam kaydıyla aynı.
- **İmaj:** `a10-jose-070:1` (`FROM pq-a09-env-php:1.0`; PHP 8.4.26, OpenSSL 3.5.8, sodium). `composer install` yalnız imaj yapımında.
- **Çağrı:** `docker run --rm --network none -v <v1.3>:/v:ro -v <anahtarlar>:/anahtarlar:ro -v <isler>:/is:ro -v <cikti>:/c a10-jose-070:1 adaptor /is/<isler> /c/JOSE-070.<kosu>.jsonl`
- **Kaynak:** `adaptor.php`, `ortak.php` (JOSE-071 ve COSE-035 ile aynı iskelet).

## 1. Ortak kurallar
`JOSE-087/MAPPING.md` §1 ile aynı (A/X, W/R, tek imzada etkin izin listesi = R, VARSAYILAN, yalnız `dogrulama_girdileri`). Saat: `JWT::$timestamp = simdi` (php-jwt'nin genel statik saat alanı; sözleşme §2.1).
- **Politika adı normalleştirme (yürütücü 01.10):** `temel = politika.split('|')[0].split('@')[0]` (`|sdjwtvc=…`, `@-19` ekleri yalnız oracle'ı böler); çıktıya özgün `politika` yazılır. **P2** (P1 + anahtar–alg bağlama) GEC/P0/P1 kümesindedir.

## 2. Politika mekanizması: anahtar–alg bağlaması
php-jwt'de ayrı bir izin listesi yoktur; algoritma `Key(material, alg)` nesnesine bağlıdır ve `decode` başlık alg'ını anahtarın alg'ıyla karşılaştırır (`JWT.php` L148–158). W bu yüzden **anahtar kümesinin kuruluşuyla** ifade edilir:
- Vektörün JWKS'indeki her JWK için anahtar türünün doğal alg'ı hesaplanır (EC P-256 → ES256, P-384 → ES384, OKP Ed25519 → EdDSA [kontrol-Ed25519 kolunda `Ed25519`], AKP → JWK `alg`).
- Doğal alg ∈ W olan JWK'ler `JWK::parseKey($jwk, $alg)` ile `Key`'e çevrilir → `[kid => Key]` (`anahtar_yolu = JWKS`).
- Başlıkta `kid` yoksa (REQ01/02, TSL01/02, DPoP) seçilen JWK tek `Key` olarak verilir (`anahtar_yolu = JWK` / `jwk-basligi`).

| Politika | Yapılandırma |
|---|---|
| GEC / P0 / P1 | doğal alg ∈ {ES256, ES384, EdDSA} olan bütün anahtarlar |
| IZIN-A / IZIN-AX | doğal alg ∈ {ES256} / {ES256, X} |
| L4 / L4-S / L4-Y (kompakt, tek imza) | doğal alg ∈ {X} (etkin izin listesi = R) |
| VARSAYILAN | GEC ile aynı (php-jwt'de alg her zaman anahtara bağlıdır) |
| L4-YOL | X5C (SD-JWT) → B6; desteklenen biçimde `ifade-edilemedi` (yol sınıfı API'si yok) |

Çağrı: `JWT::decode($jwt, $anahtarlar, $hdr)`; kabulde `dogrulanan_algoritmalar = [{alg: $hdr->alg}]` (php-jwt yalnız `Key` alg'ı başlık alg'ına eşitse doğrular).

## 3. B6 kararları
| Serileştirme | Karar | Dayanak |
|---|---|---|
| compact | desteklenir | `JWT::decode` (`explode('.', $jwt, 4)`, 3 bölüm) |
| general, sd-jwt-* , oid4vci-toplu-yanit, dcapi-json-parametre | **B6** | JSON serileştirme ve SD-JWT API'si yok (`evidence/api-tarama.txt`) |
| COSE_Sign, COSE_Sign1 | **B6** | COSE yok |

## 4. İstisna → hata_sinifi
| Kütüphane istisnası | hata_sinifi |
|---|---|
| `UnexpectedValueException` "Algorithm not supported" | `alg-desteklenmiyor` |
| "Incorrect key for this algorithm" | `alg-anahtar-uyusmazligi` |
| `"kid" invalid` / `"kid" empty` / `InvalidArgumentException` "Key may not be empty", başlık alg ∉ W | `alg-izin-disi` (W, anahtar bağlamasıyla kurulduğu için) |
| aynı, başlık alg ∈ W | `anahtar-bulunamadi`; seçilen anahtar türü `parseKey` ile kurulamadıysa (AKP) `alg-desteklenmiyor` |
| `SignatureInvalidException` | `imza-gecersiz` |
| `ExpiredException`, `BeforeValidException` | `zaman` |
| segment/kodlama/"Payload must be"/"Empty algorithm" iletileri | `ayristirma` |
| `DomainException` (OpenSSL/sodium) ve diğerleri | `istisna-diger` |
