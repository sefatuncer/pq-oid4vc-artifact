# JOSE-070 firebase/php-jwt 7.2.0 — adaptör notları (01.10.2026)

## 1. Sürüm sabitleme
- Yayımlanmış son sürüm v7.2.0 = çerçeve `son_commit_sha` `f502cdbf279c` (composer.lock `dist.reference`). Ortam `composer.lock`'u birebir; `HEDEF_SURUM` lock'tan.

## 2. TK önerisi
| Kol | Öneri | Kanıt |
|---|---|---|
| ML-DSA-65 | **TK3** | `JWT::$supported_algs` (`JWT.php` L57–69): ES384, ES256, ES256K, HS*, RS*, PS256, EdDSA; ML-DSA/composite/AKP 0 eşleşme (`evidence/api-tarama.txt`) |
| composite | **TK3** | aynı |

## 3. V± sonucu (`evidence/vpm-kosu.txt`)
- ES256: VPLUS `kabul` ×4, VMINUS `red/imza-gecersiz` ×4.
- EdDSA (kontrol-EdDSA): VPLUS_EdDSA `kabul`, VMINUS_EdDSA `red/imza-gecersiz`.
- `Ed25519` etiketi (kontrol-Ed25519): `red/alg-desteklenmiyor` → kontrol kolu `EdDSA` ile koşulur (sözleşme §8 m.4).
- ML-DSA-65, CMP00/01: `red/alg-desteklenmiyor`. COSE satırları B6.
- **Kapı: geçti (ES256 + EdDSA).**

## 4. Notlar
1. Politika mekanizması yalnız anahtar–alg bağlamasıdır (ESLEME §2). İzin dışı alg'lı belirteçte kütüphane `"kid" invalid` döndürür; adaptör bunu `alg-izin-disi` diye sınıflar (gerekçe ESLEME §4).
2. L3: bağlama belgeli ve açık (`Key` alg'ı ≠ başlık alg'ı → "Incorrect key for this algorithm").
3. L4c: aynı `JWT::decode` çağrısına `[kid => Key]` dizisi verilir; ihraççı başına (kid başına) farklı alg bağlaması aynı dizide kurulabilir (L4c için belgeli mekanizma adayı).
4. Çoklu imza B6 → L4m yok; B4 adayı yok.

## 5. Koşu kaydı
- Sentetik duman testi `evidence/duman-testi.txt`. İlk duman koşusunda yalnız seçilen anahtar verildiğinde izin dışı her durumda "Key may not be empty" alınıyordu; anahtar kümesi vektör JWKS'inden kurulacak biçimde düzeltildi (battery koşusundan önce).
- Dondurma-öncesi dosya bir kez koşuldu (12:54Z, 32 satır).
- **Son koşu (~13:59Z):** yürütücünün politika-adı normalleştirme kuralı (`|sdjwtvc=`, `@-19`; P2) eklendikten sonra imaj yeniden yapıldı ve aynı 32 satırlık dosya yeniden koşuldu; sonuçlar değişmedi, `adaptor_sha256` güncel imajı gösterir.
- **Son koşu (14:05Z):** L4-YOL → `ifade-edilemedi` kuralı eklendikten sonra imaj yeniden yapıldı, aynı 32 satırlık dosya yeniden koşuldu (V± sonuçları değişmedi).
