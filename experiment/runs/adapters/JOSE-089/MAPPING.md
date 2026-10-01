# JOSE-089 json-jwt — politika → API eşlemesi (sözleşme 1.0 §2.2, KOSUCU §2)

- **Hedef:** `json-jwt` 1.17.2 (etiket v1.17.2 → `5fc6faed950f`), `Gemfile.lock` CHECKSUMS `sha256=97e37c1c…` (ortam kaydıyla aynı dosya).
- **İmaj:** `a10-jose-089:1` (`FROM pq-a09-env-ruby:1.0`; Ruby 3.4.11, OpenSSL 3.5.7). Koşum `--network none`.
- **Çağrı:** `docker run --rm --network none -v <v1.3>:/v:ro -v <anahtarlar>:/anahtarlar:ro -v <isler>:/is:ro -v <cikti>:/c a10-jose-089:1 adaptor /is/<isler> /c/JOSE-089.<kosu>.jsonl`
- **Kaynak:** `adaptor.rb`, `ortak.rb` (JOSE-087 ile aynı iskelet).

## 1. Ortak kurallar

`JOSE-087/MAPPING.md` §1 ile aynıdır (A/X; GEC = kütüphanenin yerel desteklediği battery algoritmaları; IZIN-A/AX; L4 ailesi W = {A, X}, R = {X}; tek imzalı nesnede etkin izin listesi = R; anahtar yolu bütün kollarda `JWK`; manifestten yalnız `dogrulama_girdileri`; VARSAYILAN ek politikası; `sonuc_ham` kabul/red/istisna).
- **Politika adı normalleştirme (yürütücü 01.10):** `temel = politika.split('|')[0].split('@')[0]` (`|sdjwtvc=…`, `@-19` ekleri yalnız oracle'ı böler); çıktıya özgün `politika` yazılır. **P2** (P1 + anahtar–alg bağlama) GEC/P0/P1 kümesindedir.

## 2. Politika → API

| Politika | API çağrısı |
|---|---|
| GEC / P0 / P1 (tek imza) | `JSON::JWT.decode(girdi, JSON::JWK.new(jwk), [:ES256, :ES384])` |
| IZIN-A / IZIN-AX | `… [:ES256]` / `… [:ES256, X]` |
| L4 / L4-S / L4-Y (tek imza: kompakt ya da tek imzalı General JSON) | `… [X]` (etkin izin listesi = R) |
| P0 / P1 / L4 / L4-S / L4-Y — **çok imzalı General JSON** | **`ifade-edilemedi`**: kütüphanede çoklu imza kuralı seçeneği yok; `decode_json_serialized` yalnız `signatures.first`'ü doğrular (`lib/json/jws.rb` L199–216, `evidence/api-tarama.txt`). Her imzayı dolaşan döngü özel kod olur (B4, NOTLAR §4) |
| VARSAYILAN | `JSON::JWT.decode(girdi, JSON::JWK.new(jwk))` (algoritma listesi yok → `algorithms.blank?` her alg'ı kabul eder; çok imzalıda yalnız ilk imza) |
| L4-YOL | X5C (SD-JWT) → B6; desteklenen biçimde `ifade-edilemedi` (yol sınıfı API'si yok) |

`girdi`: kompakt için dize; General JSON için `JSON.parse` sonucu Hash (kütüphane Hash girdiyi JSON serileştirme olarak işler, `lib/json/jose.rb` L59–64). Çok imzalı nesnede anahtar ilk imzanın başlığından (`alg_kid`) seçilir.

**dogrulanan_algoritmalar:** kabulde dönen `JSON::JWS` nesnesinin `alg`'ı (General JSON'da ilk imza; kütüphane yalnız onu doğrular).

## 3. B6 kararları (API incelemesiyle)

| Serileştirme | Karar | Dayanak |
|---|---|---|
| compact | desteklenir | `decode_compact_serialized` |
| general | **desteklenir** (yalnız ilk imza doğrulanır) | `decode_json_serialized` (`signatures.first`) |
| sd-jwt-compact, sd-jwt-general, sd-jwt-flattened | **B6** | SD-JWT API'si yok (disclosure/`~` işlenmez) |
| oid4vci-toplu-yanit, dcapi-json-parametre | **B6** | JSON zarf, JWS değil |
| COSE_Sign, COSE_Sign1 | **B6** | COSE API'si yok |

## 4. İstisna → hata_sinifi

| Kütüphane istisnası | hata_sinifi |
|---|---|
| `JSON::JWS::UnexpectedAlgorithm` "Unexpected alg header", alg kütüphanede (ES256/ES384) | `alg-izin-disi` |
| aynı, alg kütüphanede yok (EdDSA, ML-DSA, composite, kayıtsız, none) | `alg-desteklenmiyor` |
| `UnexpectedAlgorithm` "Unknown Signature Algorithm" | `alg-desteklenmiyor` |
| `UnexpectedAlgorithm` (TypeError kaynaklı, anahtar türü ≠ alg) | `alg-anahtar-uyusmazligi` |
| `JSON::JWK::UnknownAlgorithm` "Unknown Key Type" (OKP/AKP JWK) | `alg-desteklenmiyor` |
| `JSON::JWK::Set::KidNotFound` | `anahtar-bulunamadi` |
| `JSON::JWS::VerificationFailed` (anahtar var) / (anahtar seçilemedi) | `imza-gecersiz` / `anahtar-bulunamadi` |
| `JSON::JWT::InvalidFormat` | `ayristirma` |
| diğer | `istisna-diger`; 60 s → `zaman-asimi` |

json-jwt `exp`/`iat` denetlemez (talep doğrulaması uygulamaya bırakılmış); saat ayarı gerekmez.
