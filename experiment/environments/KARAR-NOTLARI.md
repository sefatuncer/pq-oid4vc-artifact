# Ortam çalışmasından yürütücüye notlar (Adım 9, görev 4a)

> **Tarih:** 25.09.2026. **Yazma alanı:** yalnız `experiment/environments/`.
> **Sınır:** Aşağıdakiler yalnız **kurulum olgusudur**. Hiçbir test vektörü koşulmadı, hiçbir imza doğrulama çağrısı yapılmadı. Bağlama denetimleri tür ya da sembol yüklemeyle sınırlı. Yetenek bayrakları (ör. `MLDsa.IsSupported`, `SubtleCrypto.supports`) çalışma zamanının algoritmayı tanıdığını gösterir; bir hedefin doğru doğruladığını göstermez.
> **Kaynak:** Sayılar betik çıktılarından gelir: `derleme-sonuc.csv` (`betikler/topla_sonuc.py`), `kayit/surum_ozet.csv` (`betikler/surum_ozet.py`), `kayit/surum_dayanak.csv` (`betikler/surum_dayanak.py`), `kayit/surum_commit.csv` (`betikler/etiket_coz.py`).

## 0. Özet

- **34 hedef** (n 31 + REF 3): **33 başarılı, 1 başarısız** (JOSE-104 Swift-JWT), **0 erişilemedi**.
- **Yedek:** JOSE-104 için iki genel yedek adayı derlendi: JOSE-031 guardian ve JOSE-017 jwt-cpp, ikisi de başarılı. **Seçim sizde** (§1 K1). Kesinleşmiş yedek kullanımı: 0.
- **İmajlar:** 12 adet `pq-a09-env-*:1.0` (`IMAJLAR.md`). apt/apk hiç kullanılmadı.
- **Disk:** Docker toplamı 67,30 → 79,95 GB (+12,65 GB; eşik 40 GB).
- **Hedef başına süre:** 3–138 s. Bütün hedefler ~20 dk bütçesinin çok altında kaldı.

## 1. Karar bekleyen maddeler

**K1 — JOSE-104'ün yedeği.** Swift/ObjC grubunda grup-içi yedek yok. Genel yedek (5.3-4-ii) iki aday gösteriyor: JOSE-031 guardian (sıra 1, pop 0,899) ve JOSE-017 jwt-cpp (sıra 2, pop 0,8317). Brif gereği seçim yapılmadı. Öneri JOSE-031'dir (genel sıradaki ilk aday). Ayrıntı: `DEGISIKLIKLER.md` §1.2. Değişiklik `SECIM-DEGISIKLIK.csv`'ye de işlenmeli (çalışmanın yazma alanı dışında).

**K2 — Sürüm sabitleme: `son_surum` mı, `son_commit_sha` mı?**
- Brif `son_surum`'u istedi; KRITERLER §7.6 ise "`son_commit_sha` ile sabitlenir; aynı koda karşılık gelen sürüm varsa o da yazılır" diyor.
- Bu görevde 30 hedef sürümle, 4 hedef commit'le kuruldu. Sürümle kurulan 30 hedefin **21'inde sürüm commit'i çerçeve HEAD'inden farklı** (`kayit/surum_ozet.csv`).
- **TK1'e etkisi (statik kaynak kontrolü, `kayit/surum_dayanak.csv`):**
  - **COSE-035 cose-lib 4.8.2**'de ML-DSA kaynağı yok (`src/Algorithm/Signature/MLDSA` yok). Envanterin "evet" dayanağı çerçeve HEAD'ine (`1c854bf63c5c`) ait.
  - **COSE-034 go-cose v1.3.0** (2024-07) README'sinde envanterin "kısmi" dayanağı yok.
  - JOSE-009, JOSE-001 ve JOSE-102'nin sürümlerinde ML-DSA izi var.
  - Yani D-E3'teki "n içinde ML-DSA'yı yerel destekleyen 4 hedef", sürümle sabitlemede 3'e iner (cose-lib düşer).
- İki HEAD de kurulabiliyor (CSV dışı bilgi koşuları):
  - `_bilgi-COSE-035-HEAD`: 159 sınıf yüklendi, `MLDSA65` dahil.
  - `_bilgi-COSE-034-HEAD`: derlendi.
- Dondurmada hangisi sabitlenecek, karar sizin. Commit seçilirse bu iki hedefin kaydı HEAD koşusuyla değiştirilebilir; 19 hedefte ise yeniden kurulum gerekir.

**K3 — Kotlin çok platformlu hedeflerde çözümleyici (COSE-001, SDJWT-001).** Birincil kayıt Gradle modül meta verisiyle yapıldı. Maven, vck'da `kotlinx-serialization-json` 1.8.0'ı seçti (`-core` 1.11.0 ile karışık); Gradle 1.11.0'ı seçiyor. Öneri: adaptörlerde Gradle ve `verification-metadata.xml` kilidi kullanılsın.

**K4 — Ön kayda yazılması gereken yapılandırma seçimleri** (hepsi kurulum olgusu):
- JOSE-092 `jsonwebtoken` 11 kripto arka ucu: `aws_lc_rs` ya da `rust_crypto`. İkisi de derleniyor; birincil kayıt `aws_lc_rs` (README örneği).
- SDJWT-025 `ssi-sd-jwt` 0.6.0 özellik kümesi. Kütüphane `ssi-jws`/`ssi-jwk`'ye `default-features=false` ile bağlı; varsayılan kurulumda imza algoritması crate'i yok. `secp256r1` ve `ed25519` açıkken derleniyor (`_bilgi-SDJWT-025-ozellik`).
- COSE-035 için `spomky-labs/cbor-php` (kütüphanenin `suggest` ettiği ek paket).
- pyjwt `[crypto]` ve python-jose `[cryptography]` ekstraları.
- **SDJWT-004 authlete sd-jwt ve SDJWT-010 sd-jwt-payload imza doğrulaması içermiyor:**
  - authlete: POM'da `nimbus-jose-jwt` yalnız `test` kapsamında.
  - sd-jwt-payload: kilitte imza kriptosu crate'i yok.
  - Adaptörün hangi JOSE katmanını kullanacağı ön kayda yazılmalı. Bu, D-E7 devir analizini de etkiler.
- **SDJWT-021 WalletFramework.SdJwtVc:** Genel türler cüzdan/holder odaklı (`SdJwtVcHolderService`). Doğrulayıcı, geçişli bağımlılık `WalletFramework.SdJwtLib` 3.1.0'da (`Roles.Implementation.Verifier`). Adaptörün hedef derlemesi netleşmeli. K7 kapsam sorusu da sizde.

**K5 — Varsayılan izinli liste dışı kaynaklar.** Hepsi anonim ve kimliksiz; yalnız indirme yapıldı. Onay ya da kayıt gerekiyorsa lütfen bildirin:
- MCR (`mcr.microsoft.com`, .NET SDK imajı; .NET'in resmî imaj kaydı).
- Gradle Plugin Portal ve `maven.waltid.dev` (REF-003; `waltid-mdoc-credentials-jvm` 0.11.0 Maven Central'da yok).
- pub.dev (SDJWT-002).
- hex.pm ve builds.hex.pm (JOSE-031 adayı).
- crates.io API'sine anonim User-Agent'la meta veri sorgusu.
- apt/apk hiç kullanılmadı (§13 soru 5 açık kalabilir).

**K6 — n içi yeni devir adayları (D-E7 duyarlılığı için):**
- **SDJWT-001 vck 7.0.1 → Signum 3.24.0** (`indispensable-josef/cosef`, `supreme` 0.15.0). COSE-001, Signum 3.26.0.
- **SDJWT-021 WalletFramework → IdentityModel 7.5.2/8.0.1 + jose-jwt 5.0.0.** Bilinen devir; ama JOSE-001'in sabit sürümü (8.23.0) ile **aynı kod değil**.
- REF-011 Credo 0.7.1 → `@sd-jwt/core` 0.21.0 (SDJWT-015 ile aynı sürüm).
- REF-003 EUDI → eudi-lib-jvm-sdjwt-kt 0.20.1 + Nimbus 10.9 (Nimbus'ın yedek sürümü 10.10).
- JOSE-031 adayı → erlang-jose 1.11.12.

## 2. Tedavi kolu (TK1/TK2/TK3) ve L4 biçimi (L4m/L4c) açısından kurulum olguları

| Hedef | Kurulum olgusu | İlgisi |
|---|---|---|
| JOSE-009 jose 6.2.12 | Sürümde ML-DSA izi var. Node 24.21.0 WebCrypto, ML-DSA-44/65/87'yi tanıyor (`SubtleCrypto.supports`; Node "deneysel" uyarısı veriyor). `generalVerify` sembolü var | TK1 (ML-DSA) için ortam koşulu sağlanıyor; L4m sembol düzeyinde mevcut |
| JOSE-001 IdentityModel 8.23.0 | .NET 10.0.12 + OpenSSL 3.5.5: `MLDsa`, `CompositeMLDsa` ve `SlhDsa` için `IsSupported=True`. IdentityModel'in `CompositeMLDsa`'yı kullanıp kullanmadığı incelenmedi | TK1 (ML-DSA) ortam koşulu sağlanıyor. Composite için "incelenecek" (JOSE composite -04 ile ilişkisi doğrulanmadı) |
| COSE-035 cose-lib | 4.8.2'de ML-DSA yok; HEAD'de var. HEAD'in kapısı PHP ≥ 8.4 + OpenSSL 3.5; imajda PHP 8.4.26 + OpenSSL 3.5.8 (`isSupported()` çağrılmadı) | TK1, K2 kararına bağlı |
| COSE-036 wolfCOSE | ML-DSA **derleme bayrağına bağlı**: wolfSSL `--enable-mldsa` ve "v5.9.1-stable'dan yeni" koşulu. v5.9.2-stable ile `WOLFSSL_HAVE_MLDSA` tanımlı. `wc_CoseSign1_Verify` ve `wc_CoseSign_Verify` bağlandı | TK1 yalnız bu yapılandırmada; bayrak kümesi ön kayda yazılmalı. COSE_Sign sembolü var (L4m için) |
| JOSE-102 jwt-kit 5.3.0 | ML-DSA kaynakları Linux'ta derleniyor (CryptoExtras / swift-crypto 4.5.2); `@_spi(PostQuantum)` arkasında. `MLDSA` türü bağlandı (`_bilgi-JOSE-102-mldsa-spi`) | Envanterdeki "macOS 26+ → Linux'ta T3 olası" notu yeniden değerlendirilmeli. Çalışma zamanı sınanmadı |
| COSE-034 go-cose | Go 1.27.1 stdlib'de `crypto/mldsa` var. `NewVerifier`, `Sign1Message` ve `SignMessage` bağlandı | TK2 (Signer/Verifier arayüzü) için ortam hazır; v1.3.0'da ML-DSA dayanağı yok (K2) |
| JOSE-083 pyjwt | `PyJWS.register_algorithm` sembolü var | TK2 dayanağıyla tutarlı |
| JOSE-034 jose2go | `RegisterJws` sembolü var | TK2 dayanağıyla tutarlı |
| JOSE-033 golang-jwt | `RegisterSigningMethod` sembolü var | TK2 adayı (envanterde "incelenecek") |
| JOSE-092 jsonwebtoken 11 | README'ye göre arka uç seçilmezse "kendi `CryptoProvider`'ınızı sağlayın" | TK2 yolu olabilir (incelenecek; envanterde T3) |
| SDJWT-015 @sd-jwt/core 0.21.0 | `GeneralJSON` ve `SDJwtGeneralJSONInstance` dışa aktarılıyor | L4m sembol düzeyinde mevcut |
| SDJWT-018 sd-jwt-python 0.10.4 | jwcrypto sabitlenmemiş; bu kurulumda 1.6.1. cryptography 50.0.1'de (gömülü OpenSSL 4.0.2) `mldsa` modülü var | TK1-dolaylı, jwcrypto sürümüne ve kilide bağlı |
| REF-010 ACA-Py oid4vc | Kilit cryptography 43.0.3'ü sabitliyor (OpenSSL 3.3.2; `mldsa` modülü yok) | Emülatörün PQ kolu için değil (irmago kararıyla tutarlı) |
| REF-003 EUDI | JDK 25 JCA'da ML-DSA-44/65/87 imza adları kayıtlı (JEP 497). Doğrulayıcı eudi-lib-jvm-sdjwt-kt + Nimbus 10.9 kullanıyor | Doğrulayıcı zincirinin ML-DSA kullanımı sınanmadı |

## 3. Lisans notları

- **COSE-036 wolfCOSE: GPL-3.0** (LICENSE başlığı). **wolfSSL v5.9.2-stable: GPLv3** (LICENSING; belirli yazılımlar için GPLv2 istisnası).
  - İkisi de yalnız ölçülür, kodları dağıtılmaz (D-E11).
  - `experiment/environments/` içinde üçüncü taraf kaynak kodu yok. Yalnız kendi betiklerimiz, kilit dosyaları ve meta veriler (POM, nuspec, `.cargo_vcs_info.json`) var.
- JOSE-002 JWT.NET: CC0-1.0. JOSE-104 Swift-JWT: Apache-2.0. Adaylar guardian ve jwt-cpp: MIT.
- Diğer hedefler envanterdeki lisanslarla uyumlu: MIT / Apache-2.0 / BSD-3-Clause / MPL-2.0 (go-cose). Kayıt defterinin bildirdiği lisans `hedefler/<id>/cikti/sonuc.tsv` içinde `lisans_kayit` alanında.

## 4. Sınırlılıklar

- **§5.4'ün "en küçük doğrulama çağrısı" kısmı yapılmadı** (brif gereği; V+/V− adaptörlerle ayrıca yapılacak). K6 nihai testi yalnız derleme/bağlama yarısıyla tamamlandı. JOSE-104 derleme aşamasında düştüğü için bu eksiklik o hedefin sonucunu etkilemez.
- Bağlama denetiminin derinliği dile göre değişiyor:
  - JVM: bütün sınıflar ilklendirilmeden yüklendi.
  - .NET: `GetTypes`.
  - PHP: sınıf haritası.
  - JS/Python/Ruby: içe aktarma ve sembol varlığı.
  - Go/Rust/Swift/C/Dart: derleme ve tür/sembol başvurusu.
  - Hiçbiri doğrulama yolunun çalıştığını göstermez.
- Kilit dosyaları bu koşunun çözümlemesidir. Geçişli sürümler zamanla kayabilir, bu yüzden dondurmada bu kilitler kullanılmalı.
- Yeniden üretilebilir yapı iddia edilmez (REF-003 bootJar, `libwolfcose.a`). Sabit olanlar kaynak commit'leri ve bağımlılık özetleri. Yine de gözlem: REF-003'ün `verification-metadata.xml`'i ve `libwolfcose.a` tekrar koşularda aynı çıktı.
- npm kurulumları `--ignore-scripts` ile yapıldı; kurulum betikleri çalıştırılmadı.
- Hedef başına süre (`sure_s`) yalnız son denemenin konteyner süresidir. İmaj yapımı ve taban imaj çekme süresi hariç. Deneme sayısı ve toplam süre `not` sütununda.
- CSV dışı bilgi koşuları (`hedefler/_bilgi-*`) karar girdisidir, sonuç sayılarına girmez.

## 5. Süreç notları

- **Çalışma hataları (düzeltildi; ilgili hedefler yeniden koşuldu, deneme sayıları CSV'de):**
  - Python `write_text` CRLF yazdı.
  - Alpine'de `bash` yok (çıkış 127).
  - PHP denetim betiğinde ters eğik çizgi kayboldu.
  - REF-003'te MANIFEST satır katlaması.
  - .NET çapa türü aslında ad alanıydı.
  - wolfCOSE'da koşullu sembol seçildi.
  - Dart'ta dışa aktarılmayan tür seçildi.
  - SwiftPM sürüm ayrıştırması hatalıydı.
  - Hiçbiri hedef sonucunu değiştirmedi. Değişen tek sonuç JOSE-104'tür ve o da gerçek bir derleme hatası.
- **Gizlilik:**
  - Telemetri kapatıldı: .NET (`DOTNET_CLI_TELEMETRY_OPTOUT=1`), Dart analitiği, npm (audit/fund/update-notifier), Composer audit, NuGetAudit.
  - Hiçbir kayıt defterinde oturum açılmadı; token ya da e-posta kullanılmadı.
  - Bütün git çağrıları `GIT_TERMINAL_PROMPT=0`, `GCM_INTERACTIVE=never` ve `-c credential.helper=` ile yapıldı. Kimlik istemi çıkmadı.
  - Dışa dönük eylem yapılmadı.
- **Docker:**
  - `prune` ya da toplu silme yapılmadı.
  - Konteynerler `pq-a09-ortam-*` adıyla, `--rm`, `--memory=6g` ve `pq.agir=derleme` kilit etiketiyle, aynı anda tek konteyner olarak koştu.
  - Çekilen 14 taban imaj silinmedi (kural: çalışma yalnız `pq-a09-env-*` imajlarını silebilir). Liste `IMAJLAR.md` ve `_docker/yeni_imajlar_*.txt`'de.
  - İmaj yapımları build cache'e küçük girdiler ekledi. Kimliğe göre temizlik size ait (§3.4 madde 6).
- **COSE notu (yürütücü talimatı):** Oracle A, C3 bataryasında (v1.2) COSE vektörü olmadığını buldu. Beş COSE hedefinin (COSE-001, -014, -034, -035, -036) kurulumu yapıldı; ölçüm kapsamları ayrıca karara bağlanacak. Talimattan sonra COSE için ek ortam uğraşı yapılmadı; COSE-036 standart yolla derlendi. COSE-035'teki cbor-php düzeltmesi ve HEAD bilgi koşuları talimattan önce yapılmıştı.
- **Kişisel veri taraması (Adım 15 için):**
  - Kullanıcının e-postası `experiment/environments/` içinde hiçbir dosyada yok (tarandı).
  - Kilit ve rapor dosyalarında üçüncü taraf paket yazarlarının kayıt defterlerindeki genel e-postaları var: `composer.lock`, `pip-report.json`, `poetry-report.json`, REF-010 `pyproject.toml`.
  - Windows kullanıcı adı yalnız `betikler/kos.sh` içindeki yerel bağlama yolunda geçiyor (IS-PLANI §3.4 örneğiyle aynı).
