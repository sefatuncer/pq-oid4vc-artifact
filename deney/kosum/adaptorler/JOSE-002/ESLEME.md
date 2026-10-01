# JOSE-002 JWT (jwt-dotnet/jwt) — politika → API eşlemesi (sözleşme 1.0 §2.2, KOSUCU §2)

- **Hedef:** NuGet `JWT` **11.1.0** (nuspec commit `5a4a865eaad9`; derleme sürümü 11.0.0.0), `packages.lock.json` ortamla aynı (+ Newtonsoft.Json 13.0.4).
- **İmaj:** `a10-jose-002:1` (`FROM pq-a09-env-dotnet:1.0`). **Çağrı:** `… a10-jose-002:1 adaptor /is/<isler> /c/JOSE-002.<kosu>.jsonl`.
- **Kaynak:** `Adaptor.cs`, `Ortak.cs` (JOSE-001 ile aynı iskelet).

## 1. Ortak kurallar
`JOSE-087/ESLEME.md` §1 ile aynı (normalleştirme, P2, L4-YOL dahil). Saat: `WithDateTimeProvider(SabitSaat(simdi))` (kütüphanenin `IDateTimeProvider` arayüzü).

## 2. Politika mekanizması: anahtara bağlı algoritma nesnesi
JWT.NET'te izin listesi seçeneği ve JWK API'si yoktur. Belgeli kullanım: `JwtBuilder.Create().WithAlgorithm(new ES256Algorithm(ecdsaPublicKey)).MustVerifySignature().Decode(token)`.
- **Anahtar yolu `dogrudan`:** seçilen JWK (EC) adaptörde `ECDsa.Create(ECParameters{Q = x,y})` nesnesine çevrilir (BCL).
- **W:** anahtar türünün doğal alg'ı (P-256 → ES256, P-384 → ES384) W içindeyse o algoritma nesnesi yapılandırılır; değilse algoritma verilmez ve kütüphane `InvalidOperationException` ("Can't decode a token…") ile reddeder.

| Politika | Yapılandırma |
|---|---|
| GEC / P0 / P1 / P2 / VARSAYILAN | doğal alg ∈ {ES256, ES384} |
| IZIN-A / IZIN-AX | doğal alg ∈ {ES256} / {ES256, X} (X'in JWT.NET karşılığı yoksa yalnız ES256) |
| L4 / L4-S / L4-Y (kompakt) | doğal alg ∈ {X} — X ∈ {EdDSA, Ed25519, ML-DSA-65, composite} için hiçbir algoritma kurulamaz |
| L4-YOL | `ifade-edilemedi` |

`dogrulanan_algoritmalar`: kabulde yapılandırılan algoritma nesnesinin `Name`'i (doğrulamayı yapan nesne).

## 3. B6 kararları
| Serileştirme | Karar |
|---|---|
| compact | desteklenir (`JwtDecoder`, 3 bölüm) |
| general, sd-jwt-*, oid4vci-toplu-yanit, dcapi-json-parametre, COSE_* | **B6** (JSON serileştirme/SD-JWT/COSE API'si yok) |

## 4. İstisna → hata_sinifi
| Kütüphane istisnası | hata_sinifi |
|---|---|
| `SignatureVerificationException`, alg kütüphanede var / yok | `imza-gecersiz` (iletide "algorithm" geçerse `alg-anahtar-uyusmazligi`) / `alg-desteklenmiyor` |
| `InvalidOperationException` "Can't decode a token" (algoritma yapılandırılmadı): alg kütüphanede yok / alg ∉ W / alg ∈ W | `alg-desteklenmiyor` / `alg-izin-disi` / `alg-anahtar-uyusmazligi` (`sonuc_ham = red`) |
| `TokenExpiredException`, `TokenNotYetValidException` | `zaman` |
| `InvalidTokenPartsException`, `FormatException`, `ArgumentException` | `ayristirma` |
| `NotSupportedException` | `alg-desteklenmiyor` |
| diğer | `istisna-diger` |
