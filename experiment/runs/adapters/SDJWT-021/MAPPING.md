# SDJWT-021 WalletFramework.SdJwtVc — politika → API eşlemesi (sözleşme 1.0 §2.2, KOSUCU §2)

- **Hedef:** NuGet `WalletFramework.SdJwtVc` **3.1.0** (nuspec commit `2ed7a64b9c44`); doğrulayıcı geçişli `WalletFramework.SdJwtLib` 3.1.0'da. Geçişli IdentityModel: `Microsoft.IdentityModel.Tokens` 8.0.1, `System.IdentityModel.Tokens.Jwt` 7.5.2 (JOSE-001'in 8.23.0'ından farklı). `packages.lock.json` ortamla aynı.
- **İmaj:** `a10-sdjwt-021:1` (`FROM pq-a09-env-dotnet:1.0`). **Çağrı:** `… a10-sdjwt-021:1 adaptor /is/<isler> /c/SDJWT-021.<kosu>.jsonl`.
- **Kaynak:** `Adaptor.cs`, `Ortak.cs` (JOSE-001 ile aynı iskelet).

## 1. Ortak kurallar
`JOSE-087/MAPPING.md` §1 ile aynı (normalleştirme, P2 dahil).

## 2. Genel API ve politika eşlemesi
SdJwtLib'in iki genel doğrulama yolu vardır (yansıma: `evidence/api-tarama.txt`; kaynak: `evidence/kaynak-alintilari.txt`, commit `2ed7a64b9c44`):
1. `Roles.Implementation.Verifier.VerifyPresentation(string presentation, string issuerJwk) → bool` — kaynakta `VerifyJwt` çağrılır ama yöntem **her durumda `false` döndürür** ve `ValidateAudience = true` + `ValidAudience = null` ile her belirteci IDX10208 ile reddeder (`Verifier.cs` tüm dosya). Kabul üretemez → kullanılmadı (deneme 1, `evidence/deneme1-verifypresentation.txt`).
2. **`new SdJwtDoc(serialized).AssertThatJwtSignatureIsValid(string issuerJwk, string expectedIssuer)`** (genel `SdJwtDoc` modeli) — **kullanılan yol.** İçeride `JwtSecurityTokenHandler.ValidateToken` ile `ValidIssuer = expectedIssuer`, **`ValidTypes = {"vc+sd-jwt"}`**, **`ValidAlgorithms = {"ES256"}`** kodda sabittir (`SdJwtDoc.cs` L49–73).

| Politika | Eşleme |
|---|---|
| GEC / P0 / P1 / P2 / VARSAYILAN | `AssertThatJwtSignatureIsValid(jwk_json, iss)` (API yalnız anahtar ve ihraççı alır; alg/typ kümesi kütüphanede sabit) |
| IZIN-A, IZIN-AX, L4, L4-S, L4-Y, L4-YOL | **`ifade-edilemedi`**: API'de alg izin listesi, gerekli küme ya da yol politikası parametresi yok |

- **Anahtar yolu `JWK`** (ihraççı JWK JSON dizesi). **`expectedIssuer`:** güvenilen ihraççı yapılandırması (anahtar ↔ iss): `https://issuer.example`; eski ihraççı anahtarı (kid `GGKBh_lE…`, `anahtarlar/v1.3/roller.json`) için `https://legacy-issuer.example`.
- **Sunum biçimi:** kompakt `jws-cekirdek` vektörleri yürütücü kuralıyla açıklamasız SD-JWT olarak sunulur: `"<jws>~"` (yük ve imza değişmez). OID4VCI toplu yanıtta (VC10) `credentials[0]` değerlendirilir (BATARYA-ESLEME K11). KB-JWT doğrulaması bu API'de yok.
- **x5c:** API x5c almaz; X5C vektörlerinde anahtar manifest kid'iyle JWK olarak verilir (sözleşme §8 m.2'den sapma; hedefte x5c yolu yok).
- `dogrulanan_algoritmalar`: API `void`/`bool` döndürür → `[]`.

## 3. B6 kararları
| Serileştirme / artefakt | Karar |
|---|---|
| sd-jwt-compact; compact `jws-cekirdek` (`"<jws>~"`); oid4vci-toplu-yanit (`credentials[0]`) | desteklenir |
| compact `dpop`, `status-list-token`, `oid4vp-istek` | **B6** (SD-JWT VC değil; API girdisi değil) |
| general, sd-jwt-general, sd-jwt-flattened, dcapi-json-parametre | **B6** (`SdJwtDoc` yalnız `~` ayrımlı kompakt biçimi ayrıştırır) |
| COSE_* | **B6** |

## 4. İstisna → hata_sinifi
`InvalidOperationException("Invalid SD-JWT - Issuer Signed Jwt invalid")` iç istisnasına göre (ShowPII açık; yalnız tanılama):
| İç neden | hata_sinifi |
|---|---|
| IDX10256/IDX10257 `SecurityTokenInvalidTypeException` | `typ` |
| IDX10511/10634/10500/10503 ve başlık alg kütüphanede yok (ES256 dışı) | `alg-desteklenmiyor` |
| IDX10696 | `alg-izin-disi` |
| IDX10500/10503/10501 | `anahtar-bulunamadi` |
| IDX10511/10504 (imza) | `imza-gecersiz` |
| IDX10222/10223 (süre) | `zaman` |
| ayrıştırma (IDX12741/14100, JsonReader, FormatException) | `ayristirma` |
| diğer | `istisna-diger` |
