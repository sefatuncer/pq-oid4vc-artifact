# JOSE-087 ruby-jwt — politika → API eşlemesi (sözleşme 1.0 §2.2, KOSUCU §2)

- **Hedef:** `jwt` gem 3.3.0 (etiket v3.3.0 → `ccf24892fec8`), `Gemfile.lock` CHECKSUMS `sha256=44cc34fb…` (ortam kaydıyla aynı dosya, `deney/ortam/hedefler/JOSE-087/cikti/`).
- **İmaj:** `a10-jose-087:1` (`FROM pq-a09-env-ruby:1.0`; Ruby 3.4.11, ruby-openssl → OpenSSL 3.5.7). `bundle install` yalnız imaj yapımında (rubygems.org, anonim); koşum `--network none`.
- **Çağrı:** `docker run --rm --network none -v <v1.3>:/v:ro -v <anahtarlar>:/anahtarlar:ro -v <isler>:/is:ro -v <cikti>:/c a10-jose-087:1 adaptor /is/<isler> /c/JOSE-087.<kosu>.jsonl`
- **Kaynak:** `adaptor.rb` (kütüphaneye özgü), `ortak.rb` (JOSE-089 ile aynı iskelet). `adaptor_sha256` = `sha256(sha256sum adaptor.rb ortak.rb)` imaj yapımında hesaplanır.

## 1. Ortak kurallar (bütün hedeflerimde aynı)

| Konu | Kural |
|---|---|
| Politika adı normalleştirme (yürütücü 01.10) | `temel = politika.split('|')[0].split('@')[0]`; `|sdjwtvc=-13/-19` ve `@-19` ekleri yalnız oracle beklentisini böler, kütüphane yapılandırmasını değiştirmez. Çıktının `politika` alanına iş satırındaki özgün değer yazılır |
| P2 | P1 + anahtar–alg bağlama = kütüphane varsayılanı → GEC/P0/P1 ile aynı küme (W = yerel destek, R = ∅) |
| A, X | A = ES256; X koldan: kontrol-EdDSA → EdDSA, kontrol-Ed25519 → Ed25519, tedavi-ML-DSA-65 → ML-DSA-65, tedavi-composite → ML-DSA-65-ES256 (KOSUCU §1) |
| GEC, GEC@-19, P0, P1 | W = bataryadaki algoritmalardan kütüphanenin **yerel** desteklediği alt küme (YONTEM §2 "desteklenen tüm algoritmalar"), R = ∅ |
| IZIN-A / IZIN-AX | W = {A} / {A, X}, R = ∅ |
| L4, L4-S, L4-Y, L4@-19, L4-YOL | W = {A, X}, R = {X} |
| Tek imzalı nesne (kompakt; tek imzalı General JSON) | Çoklu imza kuralı boş kalır. R ≠ ∅ ise etkin izin listesi R'dir: tek imza R'yi ancak kendisi X ise karşılar ve R ⊆ W. Böylece L4/L4-S/L4-Y kompakt nesnede kütüphanenin **izin listesi** mekanizmasıyla kurulur (L4c "göç etmiş ihraççı" kaydı; sözleşme §5.2). P0/P1 tek imzada GEC'e eşittir |
| Çok imzalı nesne | Kütüphanede belgeli çoklu imza kuralı (en-az-biri / tümü / gerekli küme) yoksa `ifade-edilemedi`; özel döngü yazılmaz (B4) |
| Anahtar yolu (sözleşme §8 m.1) | **Bütün kollarda `JWK`:** başlıktaki `kid` vektörün JWKS'inde (`dogrulama_girdileri.jwks`) aranır; `kid` yoksa manifestteki `alg_kid[alg]`, o da yoksa tek `kid`. Seçilen JWK kütüphanenin belgeli JWK içe aktarma API'siyle anahtara çevrilir. DPoP'ta başlıktaki `jwk` (`jwk-basligi`). x5c, X5C dışı vektörlerde kullanılmaz (§8 m.2) |
| Saat | Kütüphane gerçek saati kullanır (sahte saat API'si yok). V/T/CMP/K10 vektörlerinde `exp` = 1821536000 > gerçek saat; etkilenmez |
| VARSAYILAN (ek, isler.jsonl'de yok) | Sözleşme §5.2 L5 / §5.4 B5 için: yalnız anahtar verilir, izin listesi verilmez. Dondurmadan sonra koşulabilsin diye desteklenir |
| sonuc_ham | `kabul`: kütüphane hata vermedi. `red`: kütüphanenin doğrulama hata sınıfı (`JWT::Error` altı). `istisna`: başka istisna. Adaptör hatası → `adaptor-hatasi` |
| dogrulanan_algoritmalar | Kabulde `JWT.decode`'un döndürdüğü başlığın `alg` değeri (kütüphane yalnız `valid_alg?(alg)` eşleşen doğrulayıcıyı kullanır; `jwa.rb` create_verifiers); redde `[]` |

## 2. Politika → API

| Politika | API çağrısı |
|---|---|
| GEC / P0 / P1 (tek imza) | `JWT.decode(token, nil, true, algorithms: ["ES256","ES384"]) { \|hdr\| JWT::JWK.import(jwk).verify_key }` |
| IZIN-A | `… algorithms: ["ES256"] …` |
| IZIN-AX | `… algorithms: ["ES256", X] …` (X = EdDSA/Ed25519/ML-DSA-65/ML-DSA-65-ES256 kütüphanede `JWA::Unsupported`'a çözülür) |
| L4 / L4-S / L4-Y (kompakt) | `… algorithms: [X] …` (etkin izin listesi = R) |
| L4-YOL | X5C vektörleri SD-JWT biçiminde → önce B6; desteklenen biçimde gelirse `ifade-edilemedi` (x5c yol sınıfı politikası API'si yok; bütün hedeflerimde aynı kural) |
| VARSAYILAN | `JWT.decode(token, nil, true) { … }` (algoritma verilmez; kütüphane "An algorithm must be specified" ile reddeder) |

**Neden `verify_key`:** README "JSON Web Key (JWK)" bölümü `jwk.verify_key`'i belgeler. 3.3.0'da `JWT.decode` + JWK nesnesi birlikte verilince `validate_jwk_algorithms!` JWK'nın JWA'sını JWA **nesneleriyle** karşılaştırıyor ve geçerli ES256 imzasını da `VerificationKeyError` ile reddediyor (ilk sentetik duman koşusu; NOTLAR §4 m.2). `verify_key` yolu ECDSA doğrulayıcısının eğri–alg denetimini (`jwa/ecdsa.rb` `IncorrectAlgorithm`) korur.

## 3. B6 kararları (API incelemesiyle, vektör koşulmadan)

| Serileştirme | Karar | Dayanak |
|---|---|---|
| compact | desteklenir | `JWT.decode`, `EncodedToken` (3 bölüm) |
| general, sd-jwt-flattened | **B6** | JSON serileştirme ayrıştırıcısı yok (`decode.rb` `validate_segment_count!`: yalnız nokta ayrımlı 3 bölüm); 8725bis §3.14 |
| sd-jwt-compact, sd-jwt-general | **B6** | SD-JWT (`~` ayrımlı, disclosure) API'si yok |
| oid4vci-toplu-yanit, dcapi-json-parametre | **B6** | JSON zarf; JWT kütüphanesinin girdisi değil |
| COSE_Sign, COSE_Sign1 | **B6** | COSE API'si yok |

## 4. İstisna → hata_sinifi

| Kütüphane istisnası (mesaj) | hata_sinifi |
|---|---|
| `JWT::UnsupportedKeyType` (OKP/AKP JWK) | `alg-desteklenmiyor` |
| `JWT::IncorrectAlgorithm` "payload algorithm is … verification key was provided" | `alg-anahtar-uyusmazligi` |
| `JWT::IncorrectAlgorithm` "Expected a different algorithm", başlık alg kütüphane listesinde | `alg-izin-disi` |
| aynı, başlık alg kütüphanede yok (EdDSA, ML-DSA-*, composite, none, kayıtsız) | `alg-desteklenmiyor` |
| `JWT::VerificationKeyError` "Algorithm not supported" / "do not support one of the specified" | `alg-desteklenmiyor` / `alg-anahtar-uyusmazligi` |
| `JWT::VerificationError` "Signature verification failed" | `imza-gecersiz` |
| `JWT::SignatureError` "No verification key available", "Could not find public key" | `anahtar-bulunamadi` |
| `JWT::ExpiredSignature`, `ImmatureSignature`, `InvalidIatError` | `zaman` |
| `JWT::InvalidCritError` | `crit` |
| `JWT::MalformedTokenError` (ve `Base64DecodeError`) | `ayristirma` |
| diğer `JWT::Error` / diğer istisna | `istisna-diger` |
| 60 s aşımı (`Timeout`) | `zaman-asimi` |
