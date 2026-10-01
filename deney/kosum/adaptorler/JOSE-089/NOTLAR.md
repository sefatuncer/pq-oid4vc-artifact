# JOSE-089 json-jwt 1.17.2 — adaptör notları (01.10.2026)

## 1. Sürüm sabitleme
- Yayımlanmış son sürüm 1.17.2 (etiket v1.17.2 → `5fc6faed950f`; çerçeve HEAD `fa5ef904013b` değil). Ortamdaki `Gemfile.lock` (21 bağımlılık, CHECKSUMS) birebir kullanıldı.

## 2. TK önerisi
| Kol | Öneri | Kanıt |
|---|---|---|
| ML-DSA-65 | **TK3** | `jws.rb` yalnız HS/RS/PS/ES; ML-DSA/EdDSA/OKP deseni 0 eşleşme (`kanit/api-tarama.txt`) |
| composite | **TK3** | aynı |

## 3. V± sonucu (`kanit/vpm-kosu.txt`)
- ES256: VPLUS `kabul` (4 kol), VMINUS `red/imza-gecersiz` → **geçti**.
- EdDSA/Ed25519: desteklenmiyor (`red/alg-desteklenmiyor`); ML-DSA-65 ve CMP00/01: `red/alg-desteklenmiyor`.
- **Kapı: geçti (yalnız ES256).**

## 4. Sorunlar ve yürütücüye notlar
1. **Kontrol kolu X yok** (EdDSA da Ed25519 da desteklenmiyor) → kontrol kolunda L ölçümü X = EdDSA ile yapılamaz.
2. **General JSON yalnız ilk imza:** `JSON::JWT.decode(Hash)` → `JWS.decode_json_serialized` yalnız `input[:signatures].first`'ü doğrular (`lib/json/jws.rb` L199–216, satırlar `kanit/api-tarama.txt` sonunda). Çoklu imza kuralı (P0/P1/R) için seçenek yok → çok imzalı General JSON'da P0/P1/L4/L4-S/L4-Y `ifade-edilemedi`. Bu, B5 (semantik sınıf) için "ilk-imza" davranışının **varsayılan yapılandırma** satırlarıyla (ek `VARSAYILAN` politikası) gözlenmesini gerektirir; `isler.jsonl`'de VARSAYILAN satırı yok.
3. **B4 (özel kod alternatifi):** her imzayı ayrı kompakt JWS olarak `JSON::JWS.decode_compact_serialized` ile doğrulayıp R/P0/P1 kuralını uygulayan döngü ≈ 12 satır Ruby (boş satır/yorum hariç; yazılmadı, sözleşme §1 gereği L düzeyini yükseltmez).
4. json-jwt talep (`exp`/`iat`) denetlemez.

## 5. Koşu kaydı
- Sentetik duman testi: `kanit/duman-testi.txt`.
- Dondurma-öncesi dosya iki kez koşuldu: 12:48Z (16 satır) ve 12:55Z (32 satır, COSE satırları eklendikten ve `insa`-okumama değişikliğinden sonra). Son çıktı geçerlidir.
- **Son koşu (~13:59Z):** yürütücünün politika-adı normalleştirme kuralı (`|sdjwtvc=`, `@-19`; P2) eklendikten sonra imaj yeniden yapıldı ve aynı 32 satırlık dosya yeniden koşuldu; sonuçlar değişmedi, `adaptor_sha256` güncel imajı gösterir.
- **Son koşu (14:05Z):** L4-YOL → `ifade-edilemedi` kuralı eklendikten sonra imaj yeniden yapıldı, aynı 32 satırlık dosya yeniden koşuldu (V± sonuçları değişmedi).
