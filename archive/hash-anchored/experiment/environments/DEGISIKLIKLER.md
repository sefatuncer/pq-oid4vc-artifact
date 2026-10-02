# Hedef değişiklikleri (KRITERLER-TASLAK §5.4) — Adım 9, görev 4a

> **Kural (§5.4):** Derlenemeyen ya da erişilemeyen hedefin yerine önce aynı dil grubunun yedeği gelir (5.3-4-i); yoksa tabakanın genel yedeği gelir (5.3-4-ii). Davranış sonucu gerekçe olamaz. Bu ön testte davranış ölçülmedi.
> **Durum (25.09.2026):** 34 hedeften 1'i düştü (JOSE-104). Yerine kural **iki** genel yedek adayı gösteriyor. Brif gereği ("kural iki yedeğe izin veriyor" → seçim yapılmaz) **seçim yürütücüye bırakıldı**. İki aday da derlendi.
> **Kesinleşmiş yedek kullanımı: 0. Derlenen aday: 2.**
> Makine okunur kayıt: `kayit/degisiklikler.csv`. Yedek türleri `kayit/hedef_listesi.csv`'de; `betikler/hedef_listesi.py` bunları `topla_kayit.json`'dan türetir.

## 1. Değişiklik tablosu

| # | Düşen hedef | Neden (ön kayıtlı) | Yerine gelen | Kuralın kolu | Yedeğin derleme sonucu | Kanıt |
|---|---|---|---|---|---|---|
| 1 | **JOSE-104** Swift-JWT (Kitura), JOSE, Swift/ObjC; commit `29fe084d8740` (sürüm yok) | **K6 nihai: Linux konteynerinde derlenemedi.** Bağımlılık BlueRSA 1.0.203, OpenSSL 3.x başlıklarıyla derlenmiyor: `cannot find 'EVP_PKEY_size' / 'EVP_CIPHER_iv_length' in scope`. OpenSSL 3'te bu adlar makro takma ad; Swift içe aktaramaz. Kitura/OpenSSL 2.3.1 ile BlueRSA 1.0.203, çözülebilen en son sürümler | **KARAR BEKLİYOR:** aday 1 **JOSE-031** guardian (Elixir), aday 2 **JOSE-017** jwt-cpp (C++) | 5.3-4-ii (genel). Swift/ObjC için grup-içi yedek (5.3-4-i) yok | JOSE-031: **başarılı** (guardian 2.5.0). JOSE-017: **başarılı** (commit `0a503e75084c`) | `loglar/JOSE-104.log`, `loglar/JOSE-104-deneme1.log`, `loglar/JOSE-031.log`, `loglar/JOSE-017.log` |

### 1.1 Neden düzeltilemedi (~20 dk kuralı)

- Harcanan süre ≈ 10 dk: iki koşu ve çözümleme.
- Makul ortam düzeltmesi bulunmadı:
  - Hata bir sistem paketi eksikliği değil, OpenSSL 3 API uyumsuzluğu: BlueRSA, OpenSSL 3'te makroya dönüşen adları çağırıyor.
  - Düzeltme iki yoldan birini gerektirir. Birincisi OpenSSL 1.1/1.0 tabanlı eski bir Linux ortamı; bu, geliştirme dosyaları için büyük olasılıkla OS paket deposu ister ve o depo izinli değil (IS-PLANI §3.3). İkincisi bağımlılık kodunu değiştirmek; bu da brif gereği yasak.
  - Başka Swift taban imajları denenmedi (≈20 dk kuralı ve "boşa emek" talimatı).
- Aynı imajda JOSE-102 jwt-kit (swift-crypto/BoringSSL) sorunsuz derlendi. Sorun Swift ortamında değil, Swift-JWT'nin OpenSSL bağımlılığında.

### 1.2 Seçim için bilgi (karar yürütücünün)

| | JOSE-031 guardian | JOSE-017 jwt-cpp |
|---|---|---|
| Genel yedek sırası (pop_puani) | 1. (0,899) | 2. (0,8317) |
| Dil grubu | Diğer (Elixir) | C/C++ |
| Sürüm / commit | 2.5.0 / etiket `v2.5.0` → `a9c9838b40f8` (çerçeve HEAD `6e86224f9c0a` ile aynı değil) | sürüm yok → çerçeve `son_commit_sha` `0a503e75084c` |
| Doğrulama katmanı (kurulum olgusu) | erlang-jose 1.11.12'ye devrediyor (`JOSE.JWS`); Erlang crypto → OpenSSL 3.5.7 | Başlık-yalnız; sistem OpenSSL 3.5.7'ye bağlanıyor |
| Kaynak | hex.pm (varsayılan liste dışı) | GitHub (anonim git) |
| Lisans | MIT | MIT |

**Öneri (bağlayıcı değil):** JOSE-031. Gerekçe: genel sıradaki ilk aday. Kuralın doğal okuması popülerlik sırasını izler.

**Etki:**
- n = 31 değişmez.
- Swift/ObjC grubunda yalnız JOSE-102 jwt-kit kalır.
- JOSE-031 seçilirse "Diğer" grubuna Elixir eklenir. JOSE-017 seçilirse C/C++ eklenir.
- KRITERLER §5.4 gereği değişiklik `SECIM-DEGISIKLIK.csv`'ye de yazılmalı. O dosya bu çalışmanın yazma alanında değil (`experiment/environments/` dışında).

## 2. Hedef değişikliği olmayan ortam düzeltmeleri

Bunlar kütüphane kodunu değiştirmez; kurulumda belgelenmiş makul düzeltmelerdir.

| Hedef | Düzeltme | Gerekçe | Kanıt |
|---|---|---|---|
| COSE-035 cose-lib 4.8.2 | `spomky-labs/cbor-php` (^3.4 → 3.4.2) birlikte kuruldu | cose-lib'in `suggest` alanı: "Required by the RFC 9052 header reader and cryptographic structures … CoseSign1Tag and its siblings". Paket olmadan 6 COSE mesaj Tag sınıfı yüklenemedi | `hedefler/COSE-035/cikti/composer.lock`, `loglar/COSE-035-deneme3.log` |
| COSE-001, SDJWT-001 (Kotlin çok platformlu) | Birincil kayıt Gradle modül meta verisiyle, kanonik koordinatla. Maven sonucu da saklandı | Maven için `-jvm` yapıtı gerekir. Maven'ın "en yakın kazanır" kuralı vck'da `kotlinx-serialization-json` 1.8.0'ı seçti; Gradle 1.11.0'ı seçiyor | `hedefler/{COSE-001,SDJWT-001}/cikti/` ve `cikti-maven/` |
| REF-003 EUDI doğrulayıcısı | `./gradlew` yerine kurulu Gradle 9.6.1 (sarmalayıcıyla aynı sürüm). JDK 25 imajda; araç zinciri otomatik indirmesi kapalı | services.gradle.org ve foojay JDK indirmesine gerek kalmaz | `imajlar/jvm/Dockerfile`, `loglar/REF-003.log` |
| JOSE-083 pyjwt, JOSE-084 python-jose | `[crypto]` ve `[cryptography]` ekstraları | Asimetrik algoritmalar ve cryptography arka ucu | `hedefler/JOSE-08{3,4}/cikti/requirements.lock` |
| JOSE-092 jsonwebtoken 11 | `aws_lc_rs` özelliği (birincil); `rust_crypto` da derleniyor (bilgi koşusu) | Kütüphane bir arka uç seçilmesini ya da kendi `CryptoProvider`'ınızı istiyor (README) | `hedefler/JOSE-092/`, `hedefler/_bilgi-JOSE-092-rust_crypto/` |
