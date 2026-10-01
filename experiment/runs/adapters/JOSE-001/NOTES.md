# JOSE-001 Microsoft.IdentityModel 8.23.0 — adaptör notları (01.10.2026)

## 1. Sürüm sabitleme
- Yayımlanmış son sürüm 8.23.0 (2026-09-18; nuspec commit `8b16f418b3d5`; çerçeve HEAD `80995d99c3dd` değil). Ortamın `packages.lock.json`'u (`System.IdentityModel.Tokens.Jwt` 8.23.0 doğrudan; `Microsoft.IdentityModel.JsonWebTokens/Tokens` 8.23.0 geçişli) birebir.

## 2. TK önerisi
| Kol | Öneri | Kanıt |
|---|---|---|
| ML-DSA-65 | **TK1** | Genel API: `SecurityAlgorithms.MlDsa65 = "ML-DSA-65"`, `MlDsaSecurityKey`, `JsonWebAlgorithmsKeyTypes.Akp = "AKP"`, `JsonWebKey.Pub`, `JsonWebKeyConverter.ConvertFromMlDsaSecurityKey` (`evidence/api-tarama.txt`). Çalışma zamanı: .NET 10 `MLDsa` + OpenSSL 3.5.5. V± kapısı ML-DSA kolunda geçti (aşağıda) |
| composite | **TK3** | composite/`ML-DSA-65-ES256` deseni 0 eşleşme; CMP00 `red/alg-desteklenmiyor` |

## 3. V± sonucu (`evidence/vpm-kosu.txt`)
- ES256: VPLUS ×4 `kabul` (`dogrulanan: ES256`), VMINUS ×4 `red/imza-gecersiz`.
- **ML-DSA-65: VPLUS_ML-DSA-65 `kabul` (`dogrulanan: ML-DSA-65`), VMINUS_ML-DSA-65 `red/imza-gecersiz`** → TK1 doğrulandı.
- EdDSA / Ed25519: `red/alg-desteklenmiyor` (IdentityModel'de EdDSA yok).
- CMP00/CMP01: `red/alg-desteklenmiyor` (composite TK3). COSE satırları B6.
- **Kapı: geçti (ES256 + ML-DSA-65).**

## 4. Sorunlar ve yürütücüye notlar
1. **Kontrol kolu X yok:** EdDSA/Ed25519 desteklenmiyor → kontrol kolunda L ölçümü X = EdDSA ile yapılamaz. ML-DSA kolu TK1 olduğu için L2/L4c benzeri izin listesi davranışı tedavi kolunda gözlenebilir.
2. **Devir:** SDJWT-021 IdentityModel'e devreder, ama **farklı sürümle** (Tokens 8.0.1 / System.IdentityModel.Tokens.Jwt 7.5.2; ML-DSA desteği yok).
3. L4c: `IssuerSigningKeys` + `ValidAlgorithms` çağrı başına; ihraççı başına alg kümesi için belgeli tek nesne mekanizması `IssuerSigningKeyResolver`/`AlgorithmValidator` geri çağrılarıdır (özel kod → B4 adayı, ≈ 6 satır; kullanılmadı).
4. Çoklu imza B6 (JWS JSON serileştirme yok); B4 adayı yok.

## 5. Koşu kaydı
- Sentetik duman testi `evidence/duman-testi.txt` (ML-DSA-65 sentetik belirteçleri de kabul/red doğru).
- Dondurma-öncesi dosya: 13:06Z (ilk koşu), ~13:59Z (normalleştirme), 14:05Z (L4-YOL kuralı) — V± sonuçları üçünde aynı; son çıktı güncel imajı gösterir.
