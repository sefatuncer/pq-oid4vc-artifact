# JOSE-087 ruby-jwt 3.3.0 — adaptör notları (01.10.2026)

## 1. Sürüm sabitleme
- ÖK madde 14: yayımlanmış son sürüm. Ortam kaydı: `jwt` 3.3.0, etiket v3.3.0 → `ccf24892fec8` (çerçeve HEAD `9df1393e1972` değil). İmaj aynı `Gemfile.lock`'u (CHECKSUMS) `bundle install --frozen` ile kurar; `HEDEF_SURUM` = `Gem.loaded_specs` (3.3.0).

## 2. TK önerisi
| Kol | Öneri | Kanıt |
|---|---|---|
| ML-DSA-65 | **TK3** | `lib/jwt/jwa/` yalnız ecdsa/hmac/none/ps/rsa; ML-DSA/composite deseni 0 eşleşme (`kanit/api-tarama.txt` sonu). `register_algorithm` / `SigningAlgorithm` bir genişleme noktasıdır, ama TK2 kapsam dışı (KOSUCU §5) |
| composite | **TK3** | aynı |

## 3. V± sonucu (`kanit/vpm-kosu.txt`, `kosu/oncesi/JOSE-087.jsonl`)
- ES256: VPLUS_ES256 4 kolda `kabul`, VMINUS_ES256 4 kolda `red/imza-gecersiz` → **geçti**.
- EdDSA / Ed25519: VPLUS ve VMINUS `red/alg-desteklenmiyor`. 3.0'dan beri EdDSA çekirdekte yok (README L48, L132–134: ayrı `jwt-eddsa` gem'i). Kapı yalnız desteklenen alg (ES256) için değerlendirildi.
- ML-DSA-65 ve CMP00/CMP01: `red/alg-desteklenmiyor` (TK3 ile tutarlı).
- COSE V± satırları: `uygulanamaz/bicim-desteklenmiyor` (B6).
- **Kapı: geçti (yalnız ES256).**

## 4. Sorunlar ve yürütücüye notlar
1. **Kontrol kolu X yok:** Ne `EdDSA` ne `Ed25519` yerel olarak destekleniyor. Kontrol kolunda L1–L4 ölçümü X = EdDSA ile yapılamaz (her EdDSA vektörü `alg-desteklenmiyor`). Seçenek: README'nin belgelediği `jwt-eddsa` eklentisi (ayrı paket, `ed25519` gem bağımlılığı) — bu, ortam kaydındaki bağımlılık kümesini değiştirir; eklenmedi. Karar yürütücüde.
2. **JWK nesnesi + `JWT.decode` uyumsuzluğu (3.3.0):** İlk duman koşusunda keyfinder `JWT::JWK.import(jwk)` döndürünce geçerli ES256 belirteci de `VerificationKeyError: Provided JWKs do not support one of the specified algorithms` ile reddedildi (Decode, JWA nesnelerini `validate_jwk_algorithms!`'e geçiriyor; `jwa.rb` create_verifiers). Düzeltme: README'de belgeli `jwk.verify_key` (OpenSSL anahtarı) döndürülür. Bu bir adaptör düzeltmesidir (battery koşusundan önce, sentetik veride).
3. Çoklu imza: kütüphane yalnız kompakt; General JSON B6 → L4m ölçülemez, Y_i = L4c. İhraççı başına politika için belgeli mekanizma: `algorithms:` + keyfinder (anahtar başına izin listesi çağrı başına kurulabilir; "aynı doğrulayıcı örneği" kavramı ruby-jwt'de durumsuz `JWT.decode` çağrısıdır).
4. B4 adayı yok (çoklu imza B6).

## 5. Koşu kaydı
- Sentetik duman testi (batarya değil): `kanit/duman-testi.txt` (fikstür üreteci `kanit/sentetik_uret.py`).
- 16→32 satırlık dondurma-öncesi dosya üç kez koşuldu: 12:45Z (16 satır, ilk sürüm), 12:48Z (aynı imaj, kanıt kaydı için yeniden), 12:55Z (yürütücünün COSE V± satırlarını eklediği 32 satırlık dosya; `insa` okunmamasını yapısal kılan iskelet değişikliğinden sonra). Son çıktı geçerlidir; yalnız izinli iş dosyası koşuldu.
- **Son koşu (~13:59Z):** yürütücünün politika-adı normalleştirme kuralı (`|sdjwtvc=`, `@-19`; P2) eklendikten sonra imaj yeniden yapıldı ve aynı 32 satırlık dosya yeniden koşuldu; sonuçlar değişmedi, `adaptor_sha256` güncel imajı gösterir.
- **Son koşu (14:05Z):** L4-YOL → `ifade-edilemedi` kuralı eklendikten sonra imaj yeniden yapıldı, aynı 32 satırlık dosya yeniden koşuldu (V± sonuçları değişmedi).
