# C3 örneklem çerçevesi — ÖZET (Adım 9a)

> **Tarih:** 24.09.2026. Çerçeve tarihi REF_TARIH = 23.09.2026.
> **Kapsam:** Yalnız çerçeve, meta veri ve belge/kod düzeyinde özellik envanteri. Davranış ölçülmedi: adaptör yazılmadı, test vektörü koşulmadı.
> **Kaynaklar:** Sayılar `CERCEVE.csv`, `SECIM.csv`, `ESIK-DUYARLILIK.csv`, `TARAMA.csv` ve `topla_kayit.json` dosyalarından gelir. Ölçütlerin tam tanımı `KRITERLER-TASLAK.md`'dedir.
> **Ön kayıt kararıyla uyum (ÖK §2A Ö6):**
> - Referans doğrulayıcılar (REF) n'nin **dışında** tutulur.
> - Tedavinin ana kolu composite -04, ikincil kolu ML-DSA-65'tir.
> - Oracle dört değerlidir: accept-classical / accept-hybrid / reject / indeterminate.

---

## 1. Tabaka sayıları (tanımlama → tarama → uygunluk → seçim)

| Aşama | JOSE | SDJWT | COSE | **n (kütüphane)** | REF (n dışı) |
|---|---|---|---|---|---|
| Çerçeve adayı (198) | 109 | 29 | 37 | 175 | 23 |
| Ölçütleri geçen (E2) | 41 | 15 | 17 | **73** | 14 |
| **Seçilen (kota)** | **18** | **8** | **5** | **31** | **3** |
| Yedek | 9 | 6 | 4 | 19 | 2 |

**Nereden geldi?**
- jwt.io'da 37 dil, 110 girdi ve 107 benzersiz depo var.
- GitHub konu ve paket kaydı aramaları gürültü tabanından sonra 386 isabet verdi; bunlar 306 tarama satırına indi.
- Tarama sonunda 91 isabet aday oldu, 215'i elendi:

  | Tarama kararı | Sayı |
  |---|---|
  | ilgisiz | 60 |
  | taban-altı | 46 |
  | uygulama | 33 |
  | yinelenen | 32 |
  | belge | 26 |
  | cüzdan | 9 |
  | mdoc | 5 |
  | ihraççı | 3 |
  | jwt.io ile yinelenen | 1 |

**n aralıkta mı?** Evet. n = 31, 25–40 aralığının içinde.
- Bunu sağlayan eşik değil, kota ve seçim kuralı.
- Kotasız sayım bütün eşik seçeneklerinde aralığın dışında kalıyor: 49–91 hedef.
- Kota uygulanınca n bütün seçeneklerde 30–31 çıkıyor.
- Ayrıntı: `KRITERLER-TASLAK.md` §4.

**E2'de dışlama nedenleri** (bir aday birden çok nedenle dışlanabilir):

| Kod | Neden | Sayı |
|---|---|---|
| K5 | eşik altı | 85 |
| K2 | etkin değil | 56 |
| K1 | simetrik-yalnız | 15 |
| K3 | arşiv/terk | 14 |
| K4 | lisans | 12 |
| K6 | platform | 4 |

Kota dışında kalan uygun adaylar: JOSE'da 14, SDJWT'de 1, COSE'da 8.

## 2. Önerilen nihai liste (E2; n = 31) ve yedekler

**Sütun kısaltmaları:**
- GJ: General JSON çoklu imza
- ML-DSA: RFC 9964 desteği
- Tedavi yolu: §3.2'deki önerilen tedavi sınıfı. "incelenecek" = eklenti API'si olabilir ama kanıtlanmadı.

**Bütün hücreler** `CERCEVE.csv`'de dayanak bağlantısıyla (sabit commit'li satır ya da tarama kaydı) durur.

### 2.1 JOSE (18)

| id | Hedef | Dil | Paket | ★ | Aylık indirme | GJ | ML-DSA | Tedavi yolu (öneri) |
|---|---|---|---|---|---|---|---|---|
| JOSE-065 | auth0/node-jsonwebtoken | JS/TS | npm `jsonwebtoken` | 18.193 | 204,6 M | hayır | hayır | T3 (incelenecek) |
| JOSE-009 | panva/jose *(pilot)* | JS/TS | npm `jose` | 7.799 | 472,0 M | evet (any, belgeli) | **evet** | ML-DSA: T1; composite: T3 |
| JOSE-083 | jpadilla/pyjwt | Python | `pyjwt` | 5.703 | 523,0 M | hayır | hayır | T2 (`register_algorithm`) |
| JOSE-084 | mpdavis/python-jose | Python | `python-jose` | 1.759 | 30,7 M | hayır | hayır | T3 |
| JOSE-055 | jwtk/jjwt | JVM | `jjwt-api` | 11.137 | — | hayır | hayır | T2 (`parserBuilder.sig().add`) |
| JOSE-052 | auth0/java-jwt | JVM | `java-jwt` | 6.236 | — | hayır | hayır | incelenecek |
| JOSE-033 | golang-jwt/jwt | Go | `jwt/v5` | 9.225 | — | hayır | hayır | incelenecek |
| JOSE-034 | dvsekhvalnov/jose2go | Go | `jose2go` | 186 | — | hayır | hayır | T2 (`RegisterJws`) |
| JOSE-001 | Microsoft IdentityModel | .NET | `System.IdentityModel.Tokens.Jwt` | 1.154 | — | hayır | **evet** | ML-DSA: T1; composite: incelenecek |
| JOSE-002 | jwt-dotnet/jwt (JWT.NET) | .NET | `JWT` | 2.190 | — | hayır | hayır | incelenecek |
| JOSE-070 | firebase/php-jwt | PHP | `firebase/php-jwt` | 9.809 | 14,2 M | hayır | hayır | T3 |
| JOSE-071 | lcobucci/jwt | PHP | `lcobucci/jwt` | 7.478 | 9,8 M | hayır | hayır | incelenecek |
| JOSE-087 | jwt/ruby-jwt | Ruby | `jwt` | 3.687 | — | hayır | hayır | incelenecek |
| JOSE-089 | nov/json-jwt | Ruby | `json-jwt` | 297 | — | evet (yalnız ilk imza) | hayır | incelenecek |
| JOSE-092 | Keats/jsonwebtoken | Rust | `jsonwebtoken` | 2.093 | 16,9 M | hayır | hayır | T3 |
| JOSE-091 | GildedHonour/rust-jwt | Rust | `frank_jwt` | 251 | 8,9 k | hayır | hayır | T3 |
| JOSE-104 | Kitura/Swift-JWT | Swift | SwiftPM | 602 | — | hayır | hayır | T3 |
| JOSE-102 | vapor/jwt-kit | Swift | SwiftPM | 282 | — | hayır | kısmi (65/87; macOS 26+) | Linux'ta T3 olası |

**JOSE yedekleri.** Önce dil grubu içindeki yedek gelir; sonra genel yedek.
- JS/TS: jsrsasign
- Python: authlib/joserfc *(pilot; GJ evet: "tümü")*
- JVM: Nimbus JOSE+JWT *(GJ evet: "uygulamaya bırakılmış")*
- Go: lestrrat-go/jwx *(ML-DSA evet, composite evet)*
- .NET: jose-jwt
- PHP: web-token/jwt-framework *(ML-DSA evet)*
- Rust: biscuit
- Genel yedek: guardian (Elixir), jwt-cpp (C++)

### 2.2 SDJWT (8)

| id | Hedef | Dil | Paket | ★ | Aylık indirme | GJ | ML-DSA | Tedavi yolu (öneri) |
|---|---|---|---|---|---|---|---|---|
| SDJWT-025 | spruceid/ssi | Rust | `ssi-sd-jwt` | 264 | 17,3 k | belirsiz | hayır | incelenecek |
| SDJWT-015 | identity-common-ts *(pilot; sd-jwt-js'nin halefi)* | TS | `@sd-jwt/core` | 7 | 100,4 k | evet (belgesiz; kodda "tümü") | belirsiz | T2 (doğrulayıcı geri çağrısı) |
| SDJWT-018 | OWF-Labs sd-jwt-python | Python | `sd-jwt` | 20 | 22,5 k | evet | belirsiz | T1-dolaylı (jwcrypto) |
| SDJWT-001 | a-sit-plus/vck | Kotlin | `vck` | 73 | — | belirsiz | hayır | incelenecek |
| SDJWT-010 | iotaledger/sd-jwt-payload | Rust | `sd-jwt-payload` | 9 | 1,3 k | belirsiz | belirsiz | incelenecek (kripto-bağımsız) |
| SDJWT-021 | OWF-Labs wallet-framework-dotnet | .NET | `WalletFramework.SdJwtVc` | 32 | — | hayır | hayır | T3 (ES256 kodda sabit) |
| SDJWT-004 | authlete/sd-jwt | Java | `com.authlete:sd-jwt` | 37 | — | belirsiz | hayır | incelenecek |
| SDJWT-002 | affinidi selective_disclosure_jwt | Dart | pub | 5 | 5,0 k | belirsiz | hayır | incelenecek |

**SDJWT yedekleri:**
- eudi-lib-jvm-sdjwt-kt (GJ evet ama yalnız ilk imza)
- OWF-Labs sd-jwt-rust (çoklu imzayı açıkça reddeder)
- affinidi-sd-jwt
- HeroSD-JWT (ML-DSA kısmi: alg adları RFC 9964'e uymuyor)
- sd-jwt-vc-dm
- eudi-lib-sdjwt-swift

**Not:** EUDI referans kütüphanesi eudi-lib-jvm-sdjwt-kt popülerlik sırası yüzünden yedekte kaldı (★25; vck ★73, authlete ★37). Yine de REF'teki EUDI doğrulayıcısı üzerinden ölçüme girer, çünkü doğrulayıcı `eudi-lib-jvm-sdjwt-kt 0.20.1` ve Nimbus kullanıyor.

### 2.3 COSE (5)

| id | Hedef | Dil | ★ | COSE_Sign (çoklu imzacı) | Semantik | ML-DSA | Tedavi yolu (öneri) |
|---|---|---|---|---|---|---|---|
| COSE-001 | a-sit-plus/signum (`indispensable-cosef`) | Kotlin | 197 | hayır (yalnız Sign1) | — | hayır | T3 |
| COSE-034 | veraison/go-cose | Go | 66 | evet (API deneysel) | **all** (belgeli) | kısmi | T2 (Signer/Verifier arayüzü) |
| COSE-035 | web-auth/cose-lib | PHP | 19 (5,0 M/ay) | evet | uygulamaya bırakılmış (belgeli) | **evet** (PHP 8.4 + OpenSSL 3.5) | T1 |
| COSE-036 | wolfSSL/wolfCOSE | C | 76 | evet | uygulamaya bırakılmış (imzacı dizini başına) | **evet** | T1 (GPL-3.0) |
| COSE-014 | erdtman/cose-js | JS | 28 | evet (yalnız kid'e eşleşen tek imza) | belirsiz | hayır | T3 |

**COSE yedekleri:** coset (ML-DSA yalnız tanımlayıcı; geri çağrı → T2), dark-bio crypto-rs (composite, özel COSE kimliğiyle), t_cose (COSE_Sign için 2.x sürümü gerekir), ldclabs/cose.

### 2.4 REF — referans doğrulayıcılar (n dışı, 3 + 2 yedek)

| id | Doğrulayıcı | Yığın ve bağımlılık (kanıt) |
|---|---|---|
| REF-003 | EUDI verifier endpoint | Kotlin. `eudi-lib-jvm-sdjwt-kt 0.20.1` + Nimbus (`gradle/libs.versions.toml` L17, L41–45) |
| REF-010 | ACA-Py `oid4vc` eklentisi | Python. `cryptography<51` (`oid4vc/pyproject.toml` L35) |
| REF-011 | Credo `@credo-ts/openid4vc` | TS. `@openid4vc/*` 0.5.6 (identity-common-ts) |

**Yedekler:**
- walt.id verifier-api
- irmago (Yivi): ihraççı imzasını jwx v4.4+ ile doğruluyor ve ML-DSA'yı kapsıyor. Emülatörde **PQ kolu olan tek doğrulayıcı adayı**.

### 2.5 Pilot kütüphanelerinin durumu

| Kütüphane | Durum |
|---|---|
| jose | seçildi |
| @sd-jwt/core | seçildi (yeni depo: identity-common-ts) |
| joserfc | yedek |
| jwcrypto | uygun ama kota dışı (Python'da pyjwt ile python-jose önde) |
| Authlib | dışlandı (K3: `authlib.jose` kullanımdan kaldırıldı) |

Öneri: pilotlar zorla eklenmesin. "n + pilotlar" duyarlılık analizi olarak raporlansın.

## 3. PQ destek manzarası ve kontrol–tedavi tasarımına etkisi

### 3.1 Bulgular

Kaynak: `destek_kanitlari.csv`'deki 349 kanıt satırı. Bunların 160'ı otomatik olumsuz kanıttır: 0 eşleşmeli desen taraması, sabit commit'le.

| Destek | n = 31 içinde | Tüm çerçevede (incelenenler) |
|---|---|---|
| **Composite (JOSE/COSE, -04)** | **0** | Yalnız jwx (yedek; `jwx-go/compsig` eklentisi deneysel, taslak sürümü belirtilmemiş). Kısmi: dark-bio (özel COSE kimliği, -04 tanımlayıcısı değil) |
| **ML-DSA (RFC 9964), yerel** | **4**: jose, IdentityModel, cose-lib, wolfCOSE | **8**: + jwcrypto, jwx, jwt-framework, irmago |
| ML-DSA kısmi | 2: jwt-kit (yalnız 65/87, macOS 26+), go-cose (yalnız arayüzle) | 5: + coset (yalnız kimlik), HeroSD-JWT (alg adları uyumsuz), dark-bio |
| ML-DSA belirsiz (kripto-bağımsız ya da devredilmiş) | 3: @sd-jwt/core, sd-jwt-python, sd-jwt-payload | — |

**Ek gözlemler:**
- **jwt.io verisi güncel değil.** jwt.io yalnız `panva/jose`'yi ML-DSA destekli gösteriyor. Oysa kaynak kodda en az 7 kütüphane daha ML-DSA taşıyor.
- **Ortam koşulları.** ML-DSA'nın çalışması çoğu hedefte çalışma zamanına bağlı:

  | Hedef | Gereken ortam |
  |---|---|
  | IdentityModel | .NET MLDsa |
  | cose-lib | PHP 8.4 + OpenSSL 3.5 |
  | jwcrypto | pyca `mldsa` |
  | jwx | Go 1.27 ya da eklenti |
  | jwt-kit | macOS 26+ |

  Tedavi kolunun uygulanabilirliği Linux konteynerinde bu koşullar sağlanınca kesinleşir.

### 3.2 Tasarıma etkisi (öneri)

1. **Ana kol (composite -04) yerel olarak hiçbir n hedefinde uygulanamıyor.** Bu yüzden tedavi, hedef başına üç sınıftan biriyle kurulmalı (`KRITERLER-TASLAK.md` §5.5):
   - **T1-yerel:** Kütüphane PQ algoritmasını kendisi doğrular.
     - ML-DSA-65 kolu için n içinde 4 hedef var (jose, IdentityModel, cose-lib, wolfCOSE); jwt-kit koşullu.
     - Composite kolu için n içinde yok; yalnız jwx (yedek).
   - **T2-eklenti:** Kendi composite -04 / ML-DSA-65 doğrulayıcımız, kütüphanenin **kamuya açık** algoritma kaydı ya da geri çağrı API'siyle takılır.
     - Kanıtlı yollar: PyJWT (`register_algorithm`), jjwt (`sig().add`), jose2go (`RegisterJws`), go-cose (Signer/Verifier arayüzü), @sd-jwt/core (doğrulayıcı geri çağrısı).
     - Yedeklerde: jose-jwt (`RegisterJws`), coset (geri çağrı).
     - Politika katmanı kütüphanenin kalır. Böylece L0–L5 ölçümü geçerli olur.
   - **T3-bilinmeyen-alg:** Kütüphane PQ imzasını doğrulayamaz. Kendi imzalayıcımızla üretilen composite/ML-DSA imzası sunulur ve kütüphanenin "bilinmeyen alg" davranışı ölçülür (metamorfik ilişki M2).
     - Oracle çıktısı yalnız accept-classical, reject ya da indeterminate olabilir; accept-hybrid mümkün değildir.
     - Bu da PQ'ya özgü bir başarısızlık biçimidir: "PQ zorunlu" politikası ifade edilemediği için ya fail-open (klasiğe düşme) ya da fail-closed (tümden ret) olur.
2. **McNemar ve "PQ'ya özgü açık" ayrımı.**
   - Kontrol kolu (EdDSA ikinci imza) ile tedavi arasındaki eşleştirilmiş karşılaştırma yalnız T1 + T2 alt kümesinde anlamlı.
   - T3, "yetenek yokluğu" kategorisi olarak ayrı raporlanmalı. Aksi hâlde McNemar farkı ile "algoritmayı hiç tanımama" birbirine karışır.
3. **n'nin tedavi sınıflarına dağılımı (öneri, ölçüm öncesi dondurulacak):**

   | Kol | T1 | T2 (kanıtlı) | incelenecek | T3 |
   |---|---|---|---|---|
   | ML-DSA-65 | 4 (+ jwt-kit koşullu, + sd-jwt-python dolaylı) | 5 | 9 | kalan |
   | composite -04 | 0 | ≈5 | 9 | kalan |

   "İncelenecek" 9 hedef: java-jwt, golang-jwt, JWT.NET, lcobucci, ruby-jwt, json-jwt, IdentityModel, spruceid/ssi, vck/authlete/affinidi grubu. Bunların eklenti API'si adaptör yazımı sırasında **API incelemesiyle** (davranış ölçümü olmadan) T2 ya da T3'e atanır.
4. **İmzalayıcı gereksinimi.** Composite -04 için kendi JOSE/COSE imzalayıcımız zorunludur (Sürüm 3 §9.2: "composite -04 JOSE için kendi imzalayıcımız"). ML-DSA-65 için OpenSSL 3.5 / liboqs yeterlidir.

### 3.3 Çoklu imza ve politika envanteri (n = 31)

- **General JSON çoklu imza:** evet 4 (jose, json-jwt, @sd-jwt/core, sd-jwt-python), hayır 17 (kompakt-yalnız), belirsiz 6, COSE'da uygulanamaz 4.
  - **Sonuç:** Stres yapılandırması (d), yani General JSON, JOSE tabakasında yalnız birkaç hedefte doğrudan sınanabilir.
  - Hedeflerin çoğu kompakt-yalnızdır. Bunlarda L4'ün ifade biçimi "ihraççı başına zorunlu PQ/composite alg"dir (bkz. §6-P2).
- **Çoklu imza semantiğinin belgelenme durumu:**
  - Belgeli: any 1 (jose), all 1 (go-cose), uygulamaya bırakılmış 2 (cose-lib, wolfCOSE).
  - **Belirsiz: 10.**
  - Kod okumasına göre (ölçülmedi) birkaç kütüphane General JSON'da **yalnız ilk imzaya** bakıyor: json-jwt, eudi-lib-jvm-sdjwt-kt, sd-jwt-python'daki kompakt dönüşüm, cose-js (kid eşleşmesi).
- **Algoritma izin listesi:** çağrı başına 23, belirsiz 6, yok 1 (cose-js), genel/sabit 1 (WalletFramework: ES256 kodda sabit).
- **Anahtar–alg bağlama:** evet 18, hayır 3 (golang-jwt: Keyfunc'a bırakılmış; cose-lib: "caller's responsibility"; cose-js), belirsiz 10.

## 4. Kütüphaneler arası bağımlılıklar (bağımsızlık varsayımı için)

Doğrulamayı başka bir hedefe devreden birimler:

| Birim | Devrettiği hedef |
|---|---|
| sd-jwt-python | jwcrypto |
| eudi-lib-jvm-sdjwt-kt ve EUDI doğrulayıcısı | Nimbus |
| irmago | jwx |
| WalletFramework.SdJwtVc | Microsoft IdentityModel (`JwtSecurityTokenHandler`) |
| Credo | identity-common-ts (`@openid4vc/*`) |

n içinde doğrudan devir kümesi: **WalletFramework → IdentityModel**. sd-jwt-python'un bağımlısı jwcrypto n dışında.

## 5. Riskler

| # | Risk | Etki | Önlem |
|---|---|---|---|
| R1 | **Referans depo değişimi.** sd-jwt-js ve oid4vc-ts Eylül 2026'da arşivlendi, identity-common-ts'e taşındı. Pilotun dayanağı olan commit `c7cf23dbc1b8` eski depoda | Pilot ile C3 arasında sürüm kopukluğu | Yeni depoda commit sabitlensin; pilot vektörleri yeni sürümde yeniden koşulsun (ölçüm aşamasında) |
| R2 | **Linux derlemesi** (K6 nihai). Swift hedefleri (Swift-JWT, jwt-kit); ML-DSA ortamları (.NET MLDsa, PHP 8.4 + OpenSSL 3.5, wolfSSL ML-DSA derlemesi, Go 1.27) | Hedef ya da tedavi kolu kaybı | Değiştirme kuralı (§5.4); ilk iş olarak derleme ön testi |
| R3 | **Belgesiz semantik.** Çoklu imza semantiği 10 hedefte belirsiz | "İfade edilemez" hükmü tartışmalı olur | Kanıt kuralı: iki bağımsız deneme + satır referansı; aksi hâlde "belirsiz" |
| R4 | **"Yalnız ilk imza" deseni** (kod okuması) | İmza sırası permütasyonuyla kabul değişebilir | Metamorfik ilişki olarak imza sırası permütasyonu eklensin |
| R5 | **Composite -04'ün yerel desteği yok** ve taslak oynak | Ana kolda accept-hybrid gözlemi yalnız T1 (jwx) ve T2'de mümkün | Tedavi sınıfı ön kayda; jwx-go/compsig'in taslak sürümü -04 ile karşılaştırılsın (bilinen-cevap vektörü) |
| R6 | **Bağımsızlık ihlali** (§4) | Binom testinin varsayımı zayıflar | Devir kümeleri ön kayda; kümeleri tek birim sayan duyarlılık analizi |
| R7 | **Popülerlik ölçüsü ekosistemden ekosisteme değişiyor.** Dil kotası düşük popülerlikli hedefleri içeri alıyor (frank_jwt 8,9 k/ay; Swift-JWT) | Temsil gücü | Tabaka içi yüzdelik ve kural önceden kayıtlı; alternatif kural (kotasız E5) duyarlılık olarak raporlansın |
| R8 | **Etkinlik sınırına yakın hedefler:** Swift-JWT (2024-11-18), python-jose (2025-05-28), frank_jwt (2025-07-12) | Bakım riski | Dondurma anında K2 yeniden hesaplanır; düşen hedef yedekle değişir |
| R9 | **Kapsam boşluğu.** jwt.io dışındaki JOSE kütüphaneleri; PyPI'de arama API'si yok; npm'de COSE anahtar sözcüğü eksik kalabilir | Dış geçerlilik | Sınırlılık bölümü; isteğe bağlı J4 taraması |
| R10 | **Lisans.** wolfCOSE GPL-3.0 | Artefaktın dağıtımı | Ayrı konteyner ve lisans notu |
| R11 | **Anlık görüntü kayması.** Arama ve kayıt API'leri zamanla değişir | Tekrarlanabilirlik | `onbellek/` ve girdi dosyalarının SHA-256'ları ön kayda |
| R12 | **Gizlilik olayı** (kapatıldı). Silinmiş bir Bitbucket deposunun anonim klonu Git Credential Manager'ı tetikledi | — | Süreç **girdi almadan** sonlandırıldı. Sonraki bütün git çağrıları kimlik yardımcıları ve istemler kapalı çalıştı (`credential.helper=`, `GCM_INTERACTIVE=never`). Hiçbir kimlik bilgisi ya da kişisel veri gönderilmedi |

## 6. Ön kayda girecek maddeler

Tam liste `KRITERLER-TASLAK.md` §7'dedir. Özetle:
1. Çerçeve kaynakları ve sorgular: jwt.io commit `60b70f7d8d20`; `onbellek/` ve girdi dosyalarının SHA-256'ları.
2. K1–K8, E2 eşikleri ve istisnaları, lisans kuralı, tek-depo istisnası.
3. Popülerlik puanı; kotalar (18/8/5; n = 31); REF 3 (n dışı); seçim, yedek ve Linux-değiştirme kuralları.
4. Sürüm sabitleme: `son_commit_sha`; tarihsel taban bu noktadan geriye doğru.
5. Binom eşikleri: n = 31'de ≥21 / ≤10 (p = 0,035). n = 30'a düşerse ≥20 / ≤10.
6. Tedavi sınıfı ataması (T1/T2/T3), dondurulmuş hâliyle.
7. L4'ün işlemselleştirilmesi (aşağıda P2).
8. Metamorfik ilişkilere imza sırası permütasyonunun eklenmesi (R4).
9. Bağımlılık kümeleri ve duyarlılık analizi (R6).
10. Pilotların ele alınışı: zorla eklenmez; "n + pilotlar" duyarlılığı.

## 7. Plana öneriler

| No | Öneri |
|---|---|
| P1 | **E2 + kota 18/8/5 (n = 31), REF n dışı** kabul edilsin. Eşik seçimi n'yi değiştirmiyor, yalnız uygun havuzu belirliyor |
| P2 | **L4 iki biçimde tanımlansın.** Kompakt-yalnız 17 hedefte L4 = "ihraççı/anahtar başına gerekli PQ (composite) algoritması; yoksa ret". Çoklu imzalı hedeflerde L4 = "gerekli kümedeki her alg mevcut ve geçerli". Tanımlanmazsa L4 hedeflerin yarısından fazlasında "uygulanamaz" çıkar ve H6'nın paydası küçülür |
| P3 | **T3 ayrı kategori olsun.** Tedavi sınıfları ön kayda girsin; McNemar yalnız T1 + T2'de, T3 "yetenek yokluğu" (fail-open/fail-closed) olarak raporlansın |
| P4 | **Linux derleme ön testi (K6) ölçümden önce ayrı bir adım olarak yapılsın** (≤4 çalışma-saati/hedef). Konteyner imajları ML-DSA ortamlarıyla sabitlensin: OpenSSL 3.5, .NET MLDsa, PHP 8.4, Go 1.27 |
| P5 | **Adaptör yazımı sırasında "incelenecek" 9 hedefin eklenti API'si belgelenip tedavi sınıfı dondurulsun.** Bu API incelemesidir, davranış ölçümü değildir |
| P6 | **Cüzdan tarafı istek nesnesi doğrulaması** (OID4VP A.3.2.2, G4 hedefi) için isteğe bağlı küçük bir ek çerçeve kurulsun (n dışı): eudi-lib-jvm-openid4vp-kt, eudi-lib-ios-openid4vp-swift, Multipaz. Bunlar şimdi "cüzdan" kararıyla dışarıda |
| P7 | **Emülatör için irmago** (ML-DSA doğrulayan tek REF adayı) yedek sırasında öne alınabilir. Ancak bu, kuralın (G önce) değişmesi demektir; yürütücü kararı gerekir |
| P8 | **R1 gereği pilot vektörleri identity-common-ts'in sabitlenmiş sürümünde yeniden koşulsun** (ölçüm aşamasında) |

## 8. Dosyalar ve yeniden üretim

| Dosya | İçerik |
|---|---|
| `CERCEVE.csv` | 198 aday. Kimlik, meta veri, 8 destek sütunu ve her birinin dayanağı, ölçüt sonucu (E2), dışlama nedeni |
| `SECIM.csv` | E1–E5 için ölçüt sonuçları ve kararlar; popülerlik puanları |
| `ESIK-DUYARLILIK.csv` | Eşik seçenekleri × tabaka: uygun ve seçilen sayıları, sayım n'si |
| `TARAMA.csv` | 306 tarama satırı: kaynak, sorgu, karar, gerekçe |
| `topla_kayit.json` | Koşum kaydı |
| `KRITERLER-TASLAK.md` | Ölçütler, eşikler, kotalar, seçim kuralı, dışlama nedenleri, ön kayıt sabitleri |
| `OZET.md` | Bu belge |
| `topla.py` | Toplama betiği. `python topla.py --cevrimdisi` yalnız önbellekten aynı çıktıları üretir. `--desen-tara` kanıt ipucu taraması yapar (sığ klon, anonim git) |
| `tarama_kararlari.csv` | Elle verilmiş girdi |
| `jwtio_esleme.csv` | Elle verilmiş girdi |
| `elle_bayraklar.csv` | Elle verilmiş girdi |
| `destek_kanitlari.csv` | Elle verilmiş girdi; 349 kanıt |
| `onbellek/` | HTTP yanıtları (kişisel veri alanları ayıklanmış), git HEAD kayıtları, desen taraması çıktıları |

**Sınır:** `destek_*` hücreleri **envanterdir**. Belge ya da kod satırına dayanırlar ama L0–L5 sonucu değildirler. H6'nın kanıtı, ön kayıttan sonra adaptör testleriyle üretilecek.
