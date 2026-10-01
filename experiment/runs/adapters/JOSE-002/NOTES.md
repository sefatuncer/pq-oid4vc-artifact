# JOSE-002 JWT.NET 11.1.0 — adaptör notları (01.10.2026)

## 1. Sürüm sabitleme
- Yayımlanmış son sürüm 11.1.0 (2026-07-06; etiketler tarih biçiminde, nuspec commit `5a4a865eaad9`; çerçeve HEAD `034f1fe9faef` değil).

## 2. TK önerisi
| Kol | Öneri | Kanıt |
|---|---|---|
| ML-DSA-65 | **TK3** | `JwtAlgorithmName`: HS256/384/512, RS256…RS4096, ES256/384/512, None; EdDSA/ML-DSA/JWK 0 eşleşme (`evidence/api-tarama.txt`). `IAlgorithmFactory` genişleme noktası (TK2 kapsam dışı) |
| composite | **TK3** | aynı |

## 3. V± sonucu (`evidence/vpm-kosu.txt`)
- ES256: VPLUS ×4 `kabul`, VMINUS ×4 `red/imza-gecersiz`. EdDSA/Ed25519, ML-DSA-65, CMP: `red/alg-desteklenmiyor`. COSE B6.
- **Kapı: geçti (yalnız ES256).**

## 4. Sorunlar ve yürütücüye notlar
1. **Kontrol kolu X yok** (EdDSA/Ed25519 yok).
2. JWT.NET doğrulamayı yapılandırılan algoritma nesnesiyle yapar; başlık alg'ının nesne adıyla karşılaştırılıp karşılaştırılmadığı API'de belgeli değil (L3 davranışı dondurma sonrası K10 ile ölçülecek; burada test edilmedi).
3. Birden çok alg'lı W için belgeli yol `WithAlgorithmFactory(IAlgorithmFactory)` (ör. `ECDSAAlgorithmFactory`); başlığa göre alg seçen fabrika anahtar–alg bağlamasını gevşettiği için kullanılmadı; W tek anahtar türüne indirgenir (ESLEME §2).
4. Çoklu imza B6; B4 adayı yok.

## 5. Koşu kaydı
- Duman testi `evidence/duman-testi.txt`. İlk duman sürümünde `e.ToString()` (yığın izi "JWT.Algorithms" içeriyor) yanlış `alg-anahtar-uyusmazligi` veriyordu → `e.Message`'a geçildi (battery koşusundan önce).
- Dondurma-öncesi dosya: 13:08Z, ~13:59Z, 14:05Z; V± sonuçları aynı.
