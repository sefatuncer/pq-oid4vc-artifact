# JOSE-001 Microsoft.IdentityModel.JsonWebTokens — politika → API eşlemesi (sözleşme 1.0 §2.2, KOSUCU §2)

- **Hedef:** `System.IdentityModel.Tokens.Jwt` **8.23.0** paket kümesi (ortam kaydı; nuspec commit `8b16f418b3d5`) → `Microsoft.IdentityModel.JsonWebTokens` / `.Tokens` 8.23.0. `packages.lock.json` ortamla aynı (`dotnet restore --locked-mode`).
- **İmaj:** `a10-jose-001:1` (`FROM pq-a09-env-dotnet:1.0`; .NET 10.0.12, Ubuntu 26.04 OpenSSL 3.5.5, `MLDsa.IsSupported=True`). Telemetri kapalı.
- **Çağrı:** `… a10-jose-001:1 adaptor /is/<isler> /c/JOSE-001.<kosu>.jsonl`. **API taraması:** `adaptor tara '<regex>'` (yansıma; `Ortak.cs` `Tara`).
- **Kaynak:** `Adaptor.cs`, `Ortak.cs` (JOSE-002, SDJWT-021 ile aynı iskelet).

## 1. Ortak kurallar
`JOSE-087/ESLEME.md` §1 ile aynı (A/X, W/R, tek imzada etkin izin listesi = R, anahtar yolu `JWK`, VARSAYILAN, yalnız `dogrulama_girdileri`, politika adı normalleştirme `split('|')[0].split('@')[0]`, P2 ∈ {GEC, P0, P1}, L4-YOL → `ifade-edilemedi`). Vektör başına 60 s (`Task.Wait`).

## 2. Politika → API
`new JsonWebTokenHandler().ValidateTokenAsync(jwt, new TokenValidationParameters { ValidAlgorithms = W_etkin, IssuerSigningKey = new JsonWebKey(jwk_json), ValidateIssuer = false, ValidateAudience = false, RequireExpirationTime = false, ValidateLifetime = true })`

| Politika | `ValidAlgorithms` |
|---|---|
| GEC / P0 / P1 / P2 | {ES256, ES384, ML-DSA-44, ML-DSA-65, ML-DSA-87} (yerel; `SecurityAlgorithms.EcdsaSha256/384`, `MlDsa44/65/87`) |
| IZIN-A / IZIN-AX | {ES256} / {ES256, X} |
| L4 / L4-S / L4-Y (kompakt) | {X} |
| VARSAYILAN | `null` (kütüphane varsayılanı) |
| L4-YOL | `ifade-edilemedi` |

- `RequireExpirationTime = false`: K10 vektörlerinde `exp` yok; varsayılan (true) bunları imzadan bağımsız `IDX10225` ile reddederdi. `ValidateLifetime` açık (gerçek saat; `exp` = 1821536000).
- `IdentityModelEventSource.ShowPII = true` yalnız tanılama içindir: IDX10511 iletisindeki "Exceptions caught" bölümünü (asıl neden, ör. IDX10696) görünür kılar; doğrulama davranışını değiştirmez.
- `dogrulanan_algoritmalar`: kabulde `(result.SecurityToken as JsonWebToken).Alg`.

## 3. B6 kararları
| Serileştirme | Karar | Dayanak |
|---|---|---|
| compact | desteklenir | `JsonWebTokenHandler` |
| general, sd-jwt-*, oid4vci-toplu-yanit, dcapi-json-parametre | **B6** | JWS JSON serileştirme ve SD-JWT API'si yok (yansıma taraması: `kanit/api-tarama.txt`) |
| COSE_* | **B6** | COSE yok |

## 4. İstisna → hata_sinifi
| Kütüphane sonucu (`TokenValidationResult.Exception`, iç iletiler dahil) | hata_sinifi |
|---|---|
| `SecurityTokenInvalidAlgorithmException` / IDX10696, alg kütüphanede var / yok | `alg-izin-disi` / `alg-desteklenmiyor` |
| IDX10634/IDX10652/`NotSupportedException`, alg kütüphanede var / yok | `alg-anahtar-uyusmazligi` / `alg-desteklenmiyor` |
| `SecurityTokenSignatureKeyNotFoundException` | `anahtar-bulunamadi` |
| `SecurityTokenInvalidSignatureException` (IDX10511), başlık alg kütüphanede yok (EdDSA, composite, kayıtsız: "Exceptions caught" boş) | `alg-desteklenmiyor` |
| aynı, alg kütüphanede var | `imza-gecersiz` |
| `SecurityTokenExpired/NotYetValid/NoExpiration/InvalidLifetime` | `zaman` |
| `SecurityTokenMalformedException`, `ArgumentException` | `ayristirma` |
| `SecurityTokenInvalidTypeException` | `typ` |
| diğer | `istisna-diger` |
