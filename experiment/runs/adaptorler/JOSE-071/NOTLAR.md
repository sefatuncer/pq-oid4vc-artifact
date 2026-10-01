# JOSE-071 lcobucci/jwt 5.6.0 — adaptör notları (01.10.2026)

## 1. Sürüm sabitleme
- Yayımlanmış son sürüm 5.6.0 (`bb3e9f21e419`). Paket kimliği `SECIM.csv`/`CERCEVE.csv`: `lcobucci/jwt` (packagist; jwt.io adı "jwt").

## 2. TK önerisi
| Kol | Öneri | Kanıt |
|---|---|---|
| ML-DSA-65 | **TK3** | `src/Signer`: Ecdsa (Sha256/384/512), Eddsa, Rsa, Hmac, Blake2b; ML-DSA/JWK 0 eşleşme (`kanit/api-tarama.txt`). `Signer` arayüzü genişleme noktasıdır ama TK2 kapsam dışı |
| composite | **TK3** | aynı |

## 3. V± sonucu (`kanit/vpm-kosu.txt`)
- ES256 ×4 kabul / VMINUS ×4 `red/imza-gecersiz`; EdDSA kabul / VMINUS_EdDSA `red/imza-gecersiz`; `Ed25519` etiketi `alg-desteklenmiyor` (kontrol kolu EdDSA); ML-DSA-65 ve CMP `alg-desteklenmiyor`; COSE B6.
- **Kapı: geçti (ES256 + EdDSA).**

## 4. Notlar
1. JWK API'si yok → anahtar adaptörde PEM/ham bayta çevrilir (`dogrudan`). Bu dönüşüm doğrulama değildir.
2. L2/L3 mekanizması: çağrı başına (Signer, Key) kısıt kümesi; alg bağlaması imzalayıcı seçimiyle açık (SignedWith başlık alg = algorithmId denetimi).
3. Çoklu imza B6; B4 adayı yok.
4. `RequiredConstraintsViolated` iletisi 200 karakteri aştığı için `hata_ozeti` kısaltıldı (yalnız biçim; sınıflama tam iletiyle yapılır).

## 5. Koşu kaydı
- Dondurma-öncesi dosya dört kez koşuldu (12:56–12:58Z); ilk koşu kapıyı geçti, sonraki üçü yalnız `hata_ozeti` biçim düzeltmeleri içindi (sınıflar değişmedi). Son çıktı geçerlidir.
- **Son koşu (~13:59Z):** yürütücünün politika-adı normalleştirme kuralı (`|sdjwtvc=`, `@-19`; P2) eklendikten sonra imaj yeniden yapıldı ve aynı 32 satırlık dosya yeniden koşuldu; sonuçlar değişmedi, `adaptor_sha256` güncel imajı gösterir.
- **Son koşu (14:05Z):** L4-YOL → `ifade-edilemedi` kuralı eklendikten sonra imaj yeniden yapıldı, aynı 32 satırlık dosya yeniden koşuldu (V± sonuçları değişmedi).
