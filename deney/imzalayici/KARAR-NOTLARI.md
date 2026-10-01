# Adım 9b → yürütücüye notlar (imzalayıcı + üreteç + PQ ilkel doğrulama servisi)

**Tarih:** 24.09.2026 · **Yazan:** imzalayıcı çalışması · **Kapsam:** yalnız bizim araçlarımız; hedef kütüphane ölçümü YOK.
Kanıtlar: `deney/imzalayici/sonuclar/` (T01–T05), `deney/uretec/sonuclar/` (T10), `deney/uretec/vektorler/v1/MANIFEST.json`.

## A. Plana / ön kayda doğrudan etki eden bulgular

| # | Bulgu | Kanıt | Önerilen etki |
|---|---|---|---|
| A1 | **Composite kolu HAIP'e uygun `x5c` taşıyamıyor.** HAIP 1.0 §6.1.1 SD-JWT VC için `x5c` zorunlu; composite X.509 (LAMPS -19) OpenSSL 3.5.7 ve cryptography 50.0.1'de yok. v1'de composite imzalı SD-JWT VC / TSL / istek nesneleri `kid` (JWKS, JWT VC Issuer Metadata benzeri) ile çözülüyor | README §7; VC03/VC06/VC08, TSL03, REQ03 | Ön kayıtta TK ana kolu (composite -04) için anahtar çözümleme yolu açıkça yazılmalı: **(i)** `kid`/JWKS (HAIP sapması olarak etiketli) ya da **(ii)** LAMPS composite sertifika üretimi. (ii) teknik olarak mümkün: LAMPS -19 `M'` yapısı JOSE -04 ile özdeş (boş ctx), Ek E test vektörleri var; kendi DER kurucusu + asgari yol doğrulayıcısı ≈ 6–10 çalışma-saati (tahmin). Ancak hedeflerin composite X.509 desteği düşük olasılık → bu hücre büyük olasılıkla "desteklenmiyor" çıkar |
| A2 | **Composite -04 geriye uyumsuz ve tek `alg`'lı**: klasik yalnız doğrulayıcı hiçbir bileşeni kullanamaz; ECDSA bileşeni ES256 olarak yeniden kullanılamaz (Prefix/Label, M' üzerinde imza) — zayıf ayrılamazlık çalışıyor | T03 N5-ayrılabilirlik (3/3 red); CMP12/CMP13 | Karışık doğrulayıcı nüfusunda geçiş yalnız çoklu imza (senaryo d) ya da ikili ihraçla (b) sağlanır; (a) "bayrak günü" demektir. H1/H2 anlatısında ve senaryo tanımında belirtilmeli |
| A3 | **RFC 9901 §8.1 belirsizliği:** General JSON'da `sd_hash` "the signature" üzerinden; çoklu imzada hangi imza olduğu tanımsız. Bu araç ilk imzayı kullanıyor → KB-JWT yalnız ilk imzayı bağlıyor; **PQ imzası soyulsa da KB-JWT geçerli kalıyor** | VP05/VP06/VP07; T10 sd_hash kontrolleri | Senaryo (d) ve H5 (topla-sahtele) için yeni alt hücre: "KB bağlaması çoklu imzayı korumuyor". Spesifikasyon geri bildirimi adayı (dışa dönük → kullanıcıya sorulmalı) |
| A4 | **AND tek başına soymayı yakalamaz; L4 şart.** Bizim doğrulayıcıda da P0 (any-valid) ve beklenen kümesiz P1 (AND) soyulmuş nesneyi KABUL ediyor; yalnız `required_algs` (L4) reddediyor | T03 kontrol bilgisi (6/6 KABUL); N6 soyma (7/7 red; N6 toplam 16/16 red) | B'nin pilot sınıflandırmasıyla tutarlı; L4 oracle türetmesine (adim-01 kararı) doğrudan girdi |
| A5 | **Ön-özet belirsizliği (-04):** ML-DSA-65-ES256 için Tablo 5 ön-özeti SHA-512 ve Label "…-SHA512"; oysa §7.1.2 IANA açıklaması ve Tablo 5 açıklama sütunu "…P-256 curve and SHA-256" diyor (ECDSA bileşeninin kendi özeti). Uygulayıcı SHA-256 ön-özet kullanırsa birlikte çalışamaz | CMP10 (tutarlı ama yanlış ön-özetli imza) | C3'te uygulayıcı hatası sınıfı olarak kaydedilmeli; WG geri bildirimi adayı (dışa dönük → sor) |
| A6 | **DPoP boyut eşiği talep kümesine bağlı.** P4 "ML-DSA-65 DPoP ≈ 8.192 B (nginx 8.182'nin 10 B üstü)" diyordu. Bizde asgari taleplerle 8.128 B (54 B **altında**), `ath`+`nonce` ile 8.244 B (**üstünde**); ML-DSA-65-ES256 her durumda üstünde (8.355 / 8.472 B); ML-DSA-87 11.023 B; ML-DSA-44 5.805 B (altında) | `uretec/sonuclar/v1_boyutlar.csv`; DPOP01–09 | Dağıtım kısıtı tablosu **talep kümesiyle birlikte** raporlanmalı (token isteği vs. kaynak erişimi `ath`). §7.17'deki "10 B üstünde" ifadesi koşullu hâle getirilmeli |
| A7 | **P4 boyutları birebir yeniden üretildi** (OpenSSL 3.5.7, B: 3.5.6): ML-DSA-44/65/87 SPKI, imza, CA/yaprak sertifika, x5c karakter sayısı eşit; EC ±2 B | T04 29/29 | P4 ölçümleri bağımsız araçla doğrulandı (✓ etiketi için kanıt) |
| A8 | Composite imza boyu **değişken** (DER ECDSA): ML-DSA-65-ES256 3379–3381 B | T04, T01 | Eşik hesaplarında üst sınır (3381 B) kullanılmalı |
| A9 | **Kontrol kolu alg etiketi:** RFC 9864 çok biçimli `EdDSA`'yı kullanımdan kaldırıyor, `Ed25519` tam belirtilmiş ad. v1 kontrol kolu B ile uyum için `EdDSA` kullanıyor; kitaplık `Ed25519`'u da destekliyor | params.py; T02 | Ön kayıtta kontrol kolunun etiketi sabitlenmeli (`EdDSA` önerilir: B uyumu + yaygın destek); istenirse `Ed25519` etiketli ek kontrol vektörleri üretilebilir (tek satır değişiklik) |
| A10 | **Karışık zincirler zincir politikası olmadan geçerli sayılıyor** (OpenSSL yol doğrulaması algoritma sınıfına bakmaz); korumasız `x5c` imzayı bozmadan zincir sınıfını düşürmeye izin veriyor | T03 N8 kontrol bilgisi; X5C03–05, X5C08 | "Karışık x5c" ve "korumasız x5c" bayraklarının ölçümü anlamlı; ASP'deki `X_alt_ca` hücresiyle (adim-04) bağlantılı |
| A11 | **`crit` M-f taşıyıcısı olarak fail-closed**: RFC 7515 §4.1.11 anlaşılmayan crit'i reddetmeyi zorunlu kılıyor → kimlik bilgisi başlığındaki bir M-f işareti eski doğrulayıcıları kırar | CRIT01, T03 N7 | M-f'nin TL/LoTE'de taşınması (plan) doğru; başlık taşıyıcısı yalnız ablasyon varyantı olarak |
| A12 | **-13 / -19 farkı veri biçiminde çok küçük:** ikisi de `dc+sd-jwt`; fark JSON serileştirmenin statüsü (-13 isteğe bağlı, -19 kapsam dışı) ve `vc+sd-jwt` geçişi (yalnız -13) | uretec README §4 | `sdjwtvc_surum` parametresi pratikte senaryo (d) vektörlerini ve VC11'i etkiler; ön kayıtta böyle tanımlanmalı |

## B. Araç düzeyi olgular (kabul)

- Taslak test vektörleri **var ve geçti**: composite -04 Ek A.1 (6 JOSE) + RFC 9964 Ek A (3 JOSE + 3 COSE ham) → T01 156/156. RFC 9964 JWS'leri üreticimizce bayt-bayt yeniden üretildi; taslağın ML-DSA bileşeni belirlenimci, ECDSA bileşeni rastgele k (bayt-aynı üretim yalnız EdDSA'lı composite'lerde mümkün ve sağlandı).
- OpenSSL çapraz doğrulama iki yönlü 44/44; bağımsız saf-Python FIPS 204 (dilithium-py) 18/18.
- Negatif testler: 84/84 reddedildi (bozuk imza, yanlış alg etiketi, composite'in ML-DSA ve ECDSA bileşeni ayrı ayrı, soyulmuş çoklu imza, crit, x5c, biçim).
- Test vektörü seti v1: 93 vektör (T 14, UNK 5, CMP 17, X5C 10, REQ 10, VC 12, VP 7, TSL 3, DPOP 10, CRIT 5); belirlenimci, yeniden üretim bayt-aynı; **oracle kararı içermez**. Kimlik: `vektorler/v1/MANIFEST.json` SHA-256 `a4b559ed…8891`, `vektorler/v1/SHA256SUMS` `90b28b2a…e197`, `anahtarlar/v1/SHA256SUMS` `c941feb5…fc1a` → ön kayıtta dondurulabilir.
- **L5** vektör özelliği değildir (varsayılan yapılandırmayla L3/L4 vektörlerinin koşulmasıyla ölçülür); **L0** L1 etiketli vektörlerde "kısıt yok" durumu olarak ayrışır.
- TK2 "eklenti" için **PQ ilkel doğrulama servisi** hazır (`servis/`; HTTP yalnız iç ağ/127.0.0.1 + CLI): t01 69/69, t02 45/45 kitaplıkla aynı sonuç (T05 121/121). Not: HTTP gecikmesi nedeniyle servis **zamanlama** ölçümlerinde kullanılmamalı.
- Sürümler: taban `python:3.11-slim@sha256:9534e5a8…4534` (Debian 13), sistem OpenSSL 3.5.7, cryptography 50.0.1 (gömülü OpenSSL **4.0.2**, 25 Ağu 2026), dilithium-py 1.4.0. İmajlar: `pq-a09-signer:1.0` = `beeb05a70a97`, `pq-a09-credgen:1.0` = `55ac321117b7`.

## C. Geçerlilik tehdidi notları

- ML-DSA imzaları belirlenimci varyantla üretildi (tekrarlanabilirlik); gerçek dağıtım hedged. Doğrulama davranışına etkisi yok; §7.18'e bir satır.
- Kitaplık ile çapraz doğrulayıcı aynı OpenSSL kod ailesinden (4.0.2 vs 3.5.7); bu yüzden dilithium-py ve taslak/RFC vektörleri (başka uygulamalardan) ayrıca kullanıldı.
- Vektörler JOSE/SD-JWT düzeyinde; COSE/mdoc, JWE, wallet/key attestation v1'de yok.

## D. Süreç notu (şeffaflık)

- Bir kez `docker image prune -f` çalıştırdım (hata). Bu yalnız **etiketsiz** imajları siler; işe başlarken kaydettiğim listede (`kayit/docker_images_once_2026-09-24.txt`) etiketsiz imaj yoktu ve önceden var olan **tüm etiketli imajlar yerinde**, çalışan `pq-a03`/`pq-a04` konteynerleri etkilenmedi. Yine de o arada başka çalışmaların yeniden inşalarından kalan etiketsiz eski katmanlar silinmiş olabilir (toplam 1,27 GB geri kazanıldı). Sonrasında yalnız kendi imajlarımı adla/kimlikle kaldırdım. Kalan kaynaklarım: `pq-a09-signer:1.0`, `pq-a09-credgen:1.0` (etiketli, silinmedi); konteyner ve ağ yok.
- Dışa dönük eylem yapılmadı; paketler yalnız PyPI'den (özetle sabit), taban imaj Docker Hub resmî.

## E. Açık işler / öneriler

1. A1 kararı (composite anahtar çözümleme yolu) ön kayıttan önce verilmeli; istenirse LAMPS composite X.509'u (Ek E vektörleriyle doğrulanmış) v1.1 olarak ekleyebilirim.
2. A3 ve A5 spesifikasyon geri bildirimi adayları — dışa dönük olduğu için kullanıcı kararı.
3. Oracle N-sürüm üretimi için MANIFEST'teki `insa`, `dayanak`, `dogrulama_girdileri` alanları yeterli; iki bağımsız çalışma aynı MANIFEST'ten çalışabilir.

(E.1 kapandı: yürütücü kararı A1 — LAMPS composite X.509 şimdilik yapılmayacak; bkz. F.)

## F. v1.1 (yürütücü kararları A9, A1, A6 — 24.09.2026)

**Yapılan.** `deney/uretec/vektorler/v1.1/` üretildi: v1'in 93 vektörü bayt-aynı (dosyalar, `b-uyumlu/vectors.json` ve manifest girdileri) + `kol = kontrol-EdDSA` olan **7** v1 vektörünün `alg = "Ed25519"` etiketli eşi: `T1K_both_valid-ED25519`, `T2K_second_tampered-ED25519`, `T4K_plus_ML-DSA-65-ED25519`, `T5K_only_EdDSA-ED25519`, `T6_plus_composite-ED25519`, `VC09_GJ_ES256_EdDSA-ED25519`, `DPOP02_EdDSA-ED25519`. Aynı anahtar, aynı yük, aynı yapı; yalnız EdDSA etiketli imzanın korumalı başlığındaki `alg` ve o imza farklı (üretici içi koruma denetimi + T10-E). Manifest: `kol = "kontrol-Ed25519"`; `dayanak` = `RFC9864 §2.2 (Tablo 2: Ed25519)`, `§4.1.1 (JOSE kaydı: Ed25519; "Reference: Section 2.2 of RFC 9864")`, `§4.1.2 (EdDSA: Deprecated)` — üçü de `01-korpus/metin/RFC9864.txt`'ten okunarak doğrulandı.

**v1 dokunulmadı.** Üretim ve testler sırasında `vektorler/v1` ve `anahtarlar/v1` konteynere **salt-okunur** bağlandı. Ağaç özetleri (tüm dosyaların SHA-256 listesinin SHA-256'sı) önce ve sonra aynı: `vektorler/v1` `6b2ac52b…8dcb`, `anahtarlar/v1` `d149c25d…3c96`. Yeni anahtar yok; `anahtarlar/v1` aynen kullanıldı. Üretici, v1.1'den önce v1'i geçici dizinde baştan üretip donmuş v1 ile karşılaştırıyor (fark varsa durur).

**Kimlik (C3 bataryası çapaları):**

| Dosya | SHA-256 |
|---|---|
| `vektorler/v1.1/MANIFEST.json` | `e37ee97e4087829d94ce63109e1466c0cdb8d23c3eab25a84bcf7fee8181e102` |
| `vektorler/v1.1/SHA256SUMS` | `8f4466f2ea13cd84f9a646ca801e89e7ba3a950b4e60d56db215e1962333a40c` |
| `anahtarlar/v1/SHA256SUMS` (kullanılan anahtarlar) | `c941feb5ee70de6adbd2f3f9468ae8f9a2d265897db232c34d4dfda8f7ccfc1a` |

**Doğrulama.** T10 v1.1 **549/549** (`deney/uretec/sonuclar/t10_oz_dogrulama_v1.1.*`); T10 v1 hâlâ 471/471. v1.1 yeniden üretimi `MANIFEST.json` ve `SHA256SUMS` düzeyinde bayt-aynı. Eşlerdeki Ed25519 imzaları OpenSSL CLI ile çapraz doğrulandı (6 geçerli; T2K eşinde tasarım gereği bozuk olan 1 imza geçersiz). `pqjose`, `Ed25519` etiketini kabul ediyor (T eşleri, VC09 eşi, DPoP eşi).

**Yeni gözlem (ölçüm tasarımına girdi).** İzin listeleri **etikete duyarlı**: `pqjose`'de izin listesinde yalnız `EdDSA` varken `Ed25519` etiketli imza, yalnız `Ed25519` varken v1'deki `EdDSA` etiketli imza `alg-izinli-degil` ile reddediliyor. Hedeflerde de aynı davranış olası → yedek kuralla kullanılan etiketin hedef başına kaydı gerekli (A9 ile tutarlı).

**A6 boyut tablosu.** `deney/uretec/sonuclar/v1.1_dpop_boyutlari.{csv,json}` (`uretec/boyut_dpop.py`; rapor tablosu, vektör seti değişmez): 12 alg × {asgari, +ath, +ath+nonce}, composite için imza üst sınırıyla (ML-DSA-65-ES256 3381 B, ML-DSA-44-ES256 2492 B, ML-DSA-87-ES384 4731 B). **ML-DSA-65: asgari 8.128 B (nginx 8.182'nin 54 B altı), +ath 8.198 B (16 B üstü), +ath+nonce 8.244 B.** P4'teki "≈8.192 B, 10 B üstünde" değeri +ath kümesine karşılık geliyor. ML-DSA-65-ES256 (üst sınır) 8.356 / 8.426 / 8.472 B; ML-DSA-87 ≥ 11.023 B; ML-DSA-44 ≤ 5.921 B; Node eşiği (16.348 B) hiçbirinde aşılmıyor.

**README'ler.** `deney/uretec/README.md` §5b (v1.1, yedek kural, A1 ve A6 metinleri, özetler, üretim komutları) ve §6 (talep kümeli DPoP tablosu) eklendi; `deney/imzalayici/README.md` Durum satırları güncellendi.

**Kaynaklar/süreç.** Yalnız `pq-a09-*` adlı `--rm` konteynerler kullanıldı; `prune` ya da toplu silme yapılmadı; Dockerfile yorum düzeltmesi sonrası etiketsiz kalan kendi 1.1 imajım zaten temizlenmişti ("No such image"). İmajlar: `pq-a09-credgen:1.1` = `bd96803a15cd` (FROM `pq-a09-signer:1.0` = `beeb05a70a97`), `pq-a09-credgen:1.0` = `55ac321117b7` (v1'i üreten; korundu). Git kullanılmadı; dışa dönük eylem yok.

## G. v1.2 (ÖK §6.5 eşleme denetiminin eksikleri — 24–25.09.2026)

**Yapılan.** `deney/uretec/vektorler/v1.2/` = v1.1'in 100 vektörü **bayt-aynı** (dosyalar, `b-uyumlu/vectors.json`, manifest girdileri) + **53 yeni vektör** (toplam 153; 157 dosya):
- **MR4** (ÖK §2B m.8, §2C m.4): 24 permütasyon + 9 Ed25519 eşi. İki imzalılar (T1K/P/C, T2K/P/C, VC07/08/09, REQ04) ters; üç imzalılar (T4K/P/C, T6) `ek-once` ve `ters`; ÖK listesine ek olarak T7K/P/C (`kayitsiz-once`, `ters`). Her (korumalı başlık, imza) çifti ve yük bayt-aynı; SD-JWT VC'de `disclosures` yeni ilk korumasız başlıkta (RFC 9901 §8.3; `insa.mr4`).
- **MR4 dışı, tanımlayıcı:** `VP05_GJ_ES256_MLDSA65_kb-SIRA-ters` — KB-JWT değişmez, `sd_hash` artık 2. sıradaki (ES256) imzayı bağlar.
- **K5:** `T7K/T7P/T7C_plus_kayitsiz` (+1 eş) = T1* + `alg:"X-KAYITSIZ-1"` etiketli, 128 B HKDF-belirlenimci rastgele baytlı üçüncü imza. Eşlemede K5'in birincil vektörü T7*, ikincil T4*/T6 (ve ML-DSA kolunda UNK04/UNK05).
- **K10:** her kolda iki yön (6 + 1 eş); imza, başlık alg'ıyla değil gerçek anahtarın kendi algoritmasıyla üretilmiş geçerli imzadır (`insa.k10`); anahtar `dogrulama_girdileri.jwk` (+ `acik-jwks.json`/`kid`) ile, ÖK §2D m.1'e uygun.
- **V+ / V−:** `VPLUS_`/`VMINUS_{ES256, EdDSA, ML-DSA-65}` (6 + 2 eş); composite için CMP00 / CMP01 yeniden kullanıldı.
- **Ed25519 eşleri** (ÖK §2D m.2): EdDSA etiketi taşıyan her yeni kontrol vektörü için (toplam 13). İstisna: `K10K_alg-ES256_anahtar-Ed25519` EdDSA etiketi taşımaz; eşi bayt-aynı olacağından üretilmedi.
- **`deney/uretec/BATARYA-ESLEME.md`** (`uretec/esleme.py`): K1–K11, V+, V−, MR1–MR4 × kontrol / ML-DSA-65 / composite; birincil ve ikincil kimlikler; ÖK §6.5 kararları, MR1–MR3 (§4.20) ve MR4 (§2B m.8) tanımları ÖK metninden **ayrıştırılarak** birebir alıntı. 107 kimlik; v1.2'nin eşlemede geçmeyen yeni kimliği yok.

**Dürüstlük notları (eşlemede de yazılı):**
- **K8 uyarlanmış (D-S1):** "yaprak composite, ara CA klasik" yerine ML-DSA-65 yaprak + klasik ara CA (`X5C04`); composite X.509 kapsam dışı, "HAIP §6.1.1 sapması". K9 da ML-DSA-65 yaprakla (`X5C07`).
- **Uygulanamayan hücreler:** K6/K7 yalnız composite kolunda tanımlı; K8/K9 kol-bağımsız bayrak (zincir yalnız X5C vektörlerinde, klasik ve ML-DSA zincirleriyle; kontrolde EdDSA sertifika zinciri yok).
- **K3** üç kolda ortak dosya (`T3_stripped_to_ES256`); fark yalnız politikada (R = {X}).
- **K11:** `VC10`'daki PQ kopya ML-DSA-65'tir; K11 kararı yalnız klasik kopyaya dayandığı için kontrol ve composite kollarında PQ kopya gerekmez.
- **MR1** T1 ↔ T3 (+ ML-DSA'da VP05 ↔ VP06 tanımlayıcı, REQ04 ↔ REQ05 senaryo c); **MR2** T1 ↔ T7 birincil, T1 ↔ T4 (kontrolde T1 ↔ T6) ikincil; **MR3** VC07/08/09 (aynı dosya, -13 ↔ -19) ve VC01 ↔ VC11.
- REQ04 ve permütasyonu senaryo (c), cüzdan tarafı (IS-PLANI Adım 11).

**Doğrulama.**
- T10 v1.2 **944/944** (`deney/uretec/sonuclar/t10_oz_dogrulama_v1.2.*`); v1 471/471 ve v1.1 549/549 değişmedi. Yeni denetimler (F): v1.1 ⊂ v1.2 bayt-aynı (100/100); MR4 eşlerinde imza içeriği ve geçerlilikler permütasyonla birebir; SD-JWT eşlerinde `pqjose` sonucu kaynakla aynı; VP05 eşinde `sd_hash` 2. imzayı bağlıyor; T7 yapısı; K10 imzaları gerçek anahtarla geçerli ve **OpenSSL CLI ile çapraz doğrulandı**, `pqjose` L3 ile RED; V± `pqjose` ve OpenSSL ile beklendiği gibi; yeni Ed25519 eşleri yalnız etiket/imza farkıyla ve OpenSSL doğrulamalı.
- **Bağımsız yeniden üretim (25.09):** proje dizini tamamen salt-okunurken `pq-a09-credgen:1.2` ile geçici dizine üretim → `diff -r` **fark yok (157 dosya)**; `BATARYA-ESLEME.md` ve `sonuclar/v1.2_boyutlar.csv` bayt-aynı. v1.2 dosyaları imajın içinden üretildi (imaj 20:14:47, manifest 20:14:52).
- **Eşlemenin bağımsız denetimi** `deney/uretec/testler/t11_esleme_denetim.py` (üreteçten ayrı ayrıştırıcı; `sonuclar/t11_esleme_denetim.txt`): **293/293** — ÖK §6.5 içerik ve karar alıntıları birebir, her kol hücresi dolu ya da gerekçeli "—", K8 D-S1 atıflı, MR1–MR4 tanımları birebir, bütün kimlikler manifestte.
- Donmuş dizinler: `vektorler/v1`, `vektorler/v1.1`, `anahtarlar/v1` üretim ve testlerde salt-okunur; ağaç özetleri önce = sonra (`6b2ac52b…8dcb`, `6f4456cd…79e1`, `d149c25d…3c96`).

**Kimlik (çapa 6 için):**

| Dosya | SHA-256 |
|---|---|
| `deney/uretec/vektorler/v1.2/MANIFEST.json` | `bb17aaa76a3d1859b2dd5df54c62e7039948a715e2c4b4628fed82d184c6e738` |
| `deney/uretec/vektorler/v1.2/SHA256SUMS` | `92663b48f477f51e5a4cdd2a6942d97d36b2d9591fa67af451fd33eb14f0b2a3` |
| `deney/uretec/anahtarlar/v1/SHA256SUMS` (değişmedi; yeni anahtar yok) | `c941feb5ee70de6adbd2f3f9468ae8f9a2d265897db232c34d4dfda8f7ccfc1a` |
| `deney/uretec/BATARYA-ESLEME.md` | `d73352179cdf281825d498000b7f9dc6d1df0fe835c8258c6aa2c516e659e3fc` |

**Çapa için not (döngüsellik).** `BATARYA-ESLEME.md` başlığında alıntıladığı ön kayıt dosyasının özeti yazılıdır (`c239d423…8b6e`, 24.09 19:57 sürümü). Değişiklik 6 ön kayda eklenince ÖK dosyasının özeti değişir. Eşleme yeniden üretilirse başlık değişeceği için eşleme özeti de değişir. Öneri: çapada bu dosyayı `c239d423…` sürümüne karşı üretilmiş hâliyle sabitleyin. Değişiklik 6 yalnız ekleme yapıp §6.5/§4.20/§2B'yi değiştirmiyorsa, alıntıların hâlâ birebir olduğu T11 yeni ÖK metnine karşı yeniden koşularak gösterilebilir (T11 başlık özetine bakmaz, satır alıntılarını denetler).

**Araç gözlemleri (hedef ölçümü değil):**
- K10'un kontrol kolunda başlık alg'ı ile gerçek imza aynı uzunlukta (ES256 ve EdDSA 64 B). Anahtar tipine göre dallanan ve alg'ı yok sayan bir doğrulayıcı kabul eder; bu yüzden L3 için keskin bir testtir. ML-DSA ve composite kollarında uzunluklar farklı (ör. `alg=ES256` + 3309 B ML-DSA imzası). Bu kollarda ret uzunluk denetiminde erken gelebilir; gerekçe kodları raporlanırken bu ayrıma dikkat.
- `pqjose` AND semantiğinde T7'nin üçüncü imzası `alg-bilinmiyor` ile düşürülür (fail-closed); any-valid kontrolde üç kolda da KABUL.

**İmajlar ve süreç.**
- `pq-a09-credgen:1.2` = `5984112f66f6` (FROM `pq-a09-signer:1.0` = `beeb05a70a97`). 1.0 (`55ac321117b7`) ve 1.1 (`bd96803a15cd`) korundu. v1 ve v1.1 üretim kodu değişmedi; 1.2 yalnız `uretec/v12.py`, `uretec/esleme.py` ve T10 genişletmesini ekler.
- Oturum limiti 24.09 ~20:14'te kesti. Son komut tamamlanmıştı; 25.09'da yukarıdaki bağımsız yeniden üretim, T10 ve T11 ile doğrulandı.
- Yalnız `pq-a09-*` adlı `--rm` konteynerler kullanıldı. `prune` ya da toplu silme yapılmadı, git kullanılmadı, dışa dönük eylem yok. Konteyner bırakılmadı.

## H. v1.3 (Oracle A N-0 ve N-2: COSE bataryası ve L4c "eski ihraççı" — 26.09.2026)

**Yapılan.** `deney/uretec/vektorler/v1.3/` = v1.2'nin 153 vektörü **bayt-aynı** (dosyalar, `b-uyumlu/vectors.json`, manifest girdileri) + **47 yeni vektör** (toplam 200; 204 dosya). Ekonomi: brifte olmayan aile eklenmedi.
- **COSE (45; RFC 9052).** `uretec/cbor.py` (belirlenimci CBOR, RFC 8949 §4.2.1) ve `uretec/cose.py` (COSE_Sign etiket 98 / COSE_Sign1 etiket 18, Sig_structure, COSE_Key, ayrıştırıcı). Algoritma kimlikleri korpustan birebir, satır numarasıyla (`cose.KAYNAK`; manifest `cose_kimlik_kaynaklari`; tahmin yok): ES256 −7 (RFC9053:248), EdDSA −8 (RFC9053:365), Ed25519 −19 (RFC9864:225, 439), ML-DSA-65 −49 (RFC9964:367), ML-DSA-65-ES256 −55 (JOSECOMP:1268 "TBD (request assignment -55)" → manifestte "talep edilen, KAYITLI DEGIL").
  - Her kolda (EdDSA / ML-DSA-65 / composite): K1 (COSE_Sign ES256 + X), K2 (X bozuk), K4 (yalnız X), K5 (+ kayıtsız tstr alg `X-KAYITSIZ-1`, 128 B HKDF baytı), K10 (iki yön, COSE_Sign1), V+/V− (COSE_Sign1), MR4 (K1 ve K2 imzacı sırası ters). K3 üç kolda ortak tek dosya.
  - Yalnız composite: K6 (COSE_Sign1 geçerli), K7 (ML-DSA ve ECDSA bileşeni ayrı ayrı bozuk).
  - Kol-bağımsız: K8 (korumalı x5chain = ML-DSA-65 yaprak + klasik ara CA; D-S1 uyarlaması), K9 (korumasız x5chain, tam-PQ).
  - Kontrol kolunda EdDSA (−8) etiketi taşıyan 9 vektörün Ed25519 (−19) eşi.
- **L4c (2).** Ayrı kimlikli eski ihraççı: `iss = https://legacy-issuer.example`, anahtar `issuer-eski/ES256` (türetme etiketi `v1.3/issuer-eski/ES256`, kid `GGKBh_lEw5eKZr0XX6kbRRp8H1HYW6hwLhLBagC8MHw`). `L4C-JOSE_eski_ES256` (compact) ve `L4C-COSE_eski_ES256` (COSE_Sign1), yalnız ES256. Göç etmiş ihraççının "yalnız X" ve "yalnız ES256" karşılıkları mevcut vektörlerdir (yeniden üretilseler bayt-aynı olurlardı): JOSE `VPLUS_ML-DSA-65` / `CMP00` / `VPLUS_ES256`, COSE `COSE-VPLUS_ML-DSA-65` / `COSE-K6` / `COSE-VPLUS_ES256`. Vektörlerde karar yok; yalnız `insa.ihracci` (iss, kid, türetme etiketi).
- **`anahtarlar/v1.3/`**: tek yeni anahtar (eski ihraççı), `acik-jwks-l4c.json` (göç etmiş 3 anahtar + eski; `ihraccilar`: iss → kid), `cose-anahtarlar.json` (5 rolün açık COSE_Key'i; EC2 / OKP / AKP), `roller.json`, `SHA256SUMS`. `anahtarlar/v1/` değişmedi.
- **`BATARYA-ESLEME.md` v1.3**: §3 COSE (K1–K11, V±, MR1–MR4 × 3 kol; birincil/ikincil ÖK §2G m.4), §4 L4c (ML-DSA-65 ve composite × 3 satır; dayanak ÖK §2B m.6 L4c cümlesi ve §6.5 K4, ayrıştırılarak alıntı), ÖK §2H m.9, m.10, m.12 alıntıları. 154 kimlik; v1.3'ün eşlemede geçmeyen yeni kimliği yok. v1.2 eşlemesinin kopyası: `deney/uretec/sonuclar/BATARYA-ESLEME_v1.2.md` (`d7335217…`, çapa 7).

**Doğrulama.**
- **T12** (`deney/uretec/testler/t12_cose.py`; `sonuclar/t12_cose.*`) **138/138**: 40 kimliğin korpus satırları; RFC 9964 Ek A.2 COSE (ML-DSA-44/65/87): COSE_Key bayt-aynı yeniden kodlama, AKP COSE parmak izi = kid, Sig_structure = `raw_to_be_signed`, `pqjose` + dilithium-py doğrulaması, **belirlenimci yeniden imzalamayla COSE_Sign1 bayt-aynı**; -04 Ek A.2 COSE (6 composite): M′ bizim kodlamamızla birebir, composite ve bileşenler (OpenSSL CLI, dilithium-py) geçerli, EdDSA'lı örneklerde imzamız bayt-aynı.
- **T10 v1.3** **1440/1440** (`sonuclar/t10_oz_dogrulama_v1.3.*`; yeni G bölümü `testler/t10_cose.py`): v1.2 ⊂ v1.3 bayt-aynı (153/153), çapalar, yeniden üretimde `MANIFEST.json/.csv`, `SHA256SUMS` ve `anahtarlar/v1.3/SHA256SUMS` bayt-aynı; her COSE imzası **üç yolla** (`pqjose`, OpenSSL CLI, ML-DSA için dilithium-py) insa iddiasıyla tutarlı; composite bileşen durumları; K2/K3/K4/K5/V−/K7 bayt ilişkileri; x5chain konumu ve OpenSSL zincir doğrulaması; K10; MR4; Ed25519 eşleri; L4c vektörleri eski anahtarla geçerli, göç etmiş ihraççının ES256 anahtarıyla geçersiz. v1 471/471, v1.1 549/549, v1.2 944/944 değişmedi.
- **T11** v1.3 eşlemesi **592/592** (`sonuclar/t11_esleme_denetim_v1.3.txt`): JOSE bölümü v1.2 denetimlerinin tamamı (K8/K9 §2H m.9 uyarlamasıyla), COSE tablosu (alıntılar, hücreler, kimliklerin COSE ve kola ait olması), L4c (alıntılar birebir; `iss` değerleri vektör dosyalarından), §2H alıntıları. v1.2 eşlemesi güncel ÖK'ye karşı hâlâ **293/293**.
- **Bağımsız yeniden üretim:** `deney/uretec` tamamen salt-okunurken `pq-a09-credgen:1.3` ile geçici dizine üretim → `diff -r` **fark yok** (`vektorler/v1.3` 204 dosya, `anahtarlar/v1.3` 6 dosya); `BATARYA-ESLEME.md` ve `sonuclar/v1.3_boyutlar.csv` bayt-aynı. Resmî çıktılar imajın içinden üretildi (kod bağlanmadan).
- Donmuş dizinler (`vektorler/v1`, `v1.1`, `v1.2`, `anahtarlar/v1`) üretim ve testlerde salt-okunur; ağaç özetleri önce = sonra (`6b2ac52b…8dcb`, `6f4456cd…79e1`, `210c9ec7…af4b`, `d149c25d…3c96`).

**Kimlik (v1.3 çapası için):**

| Dosya | SHA-256 |
|---|---|
| `deney/uretec/vektorler/v1.3/MANIFEST.json` | `a81424470cf2b773c346795aa1b1880aecd841b77254ebb0c077432bc3c5390a` |
| `deney/uretec/vektorler/v1.3/SHA256SUMS` | `a5b678d60ff474f1991168a694f52acb6d1c8a42b9648b4e8e63913042768812` |
| `deney/uretec/anahtarlar/v1/SHA256SUMS` (değişmedi) | `c941feb5ee70de6adbd2f3f9468ae8f9a2d265897db232c34d4dfda8f7ccfc1a` |
| `deney/uretec/anahtarlar/v1.3/SHA256SUMS` | `5d0ccf6bc8cf5de3061ecab1a6c55f8d1165fe10235f366ecd4807b830bb160c` |
| `deney/uretec/BATARYA-ESLEME.md` | `6795ee65f5161b4db90942f7058924061273e5d1eb1546dce444cabb2c7cb982` |
| (alıntılanan) `00-on-kayit/ON-KAYIT-TASLAK.md` | `87932cf00b74063066386b1ade066720c4ac645df3f1e75d895ab9bbc43e3f47` |

**Kararınızı gerektiren noktalar ve dürüstlük notları.**
1. **JOSE eşlemesinde tek değişiklik (K8/K9).** ÖK §2H m.9 "Composite kolunun sonucu değildir" dediği için K8/K9'un composite hücresi artık "—" (v1.2'de `X5C04`/`X5C07` UYARLANMIŞ notuyla birincildi); UYARLANMIŞ/D-S1 notu ML-DSA-65 hücresine taşındı. §2H, §2A–§2G'nin önüne geçtiği için yaptım; istemezseniz bu iki hücre geri alınabilir, vektörler etkilenmez.
2. **COSE_Sign1'e sınırlı hedefler.** K1, K2, K5 ve MR4 COSE_Sign gerektirir. Çoklu imzayı desteklemeyen COSE hedefinde Y_i = L4c (§2B m.6). Bu hedeflerde K1–K5'in nasıl sayılacağı (uygulanamaz mı, "bilinmeyen yapı" mı) ÖK kararı ister; eşleme karar vermez. K3/K4'e COSE_Sign1 karşılıkları yalnız **ikincil** olarak eklendi.
3. **ES256 = −7 "Deprecated".** RFC 9864 §4.2.2 COSE −7 ve −8'i kullanımdan kaldırır; HAIP §7 "COSE algorithm identifier -7 or -9, as applicable" der (HAIP:498). Brif ES256 dediği için yalnız −7 üretildi; ESP256 (−9) eşi yok. Bir COSE hedefi −7'yi reddedip −9'u kabul ederse, EdDSA→Ed25519 yedek kuralının (§2D m.2) ES256→ESP256 karşılığı gerekir; ucuzdur (yalnız A imzacısının etiketi ve imzası), ama ÖK'de tanımlı değildir.
4. **Composite −55 kayıtlı değil.** Hedefler bu değeri büyük olasılıkla tanımaz; gözlenen davranış bilinmeyen-alg davranışıdır (§6.5 son cümlesi).
5. **K11 ve MR3 COSE'da uygulanamaz** (eşlemede gerekçeli): K11 OID4VCI toplu yanıtına (SD-JWT VC) bağlı, imza düzeyi karşılığı L4c-2; MR3 SD-JWT VC -13/-19 boyutudur.
6. **L4c kontrol kolu üretilmedi** (brif: tedavi kolları; L4c "PQ/composite zorunlu" politikasıdır). Gerekirse yeni vektör gerekmeden kurulabilir (eşleme §4 altındaki not).
7. **-04 Ek A.2 COSE ML-DSA-87-ES384 örneği iç tutarsız (erratum adayı).** Gösterilen Sig_structure'ın SHA-512'si, gösterilen M′ içindeki PH ile eşleşmiyor; alg −70…−1, altı örneğin kid'leri, kid'siz, kanonik/ekleme sırası, SHA-512/SHAKE256-64/SHA3-512 denendi, hiçbiri tutmadı. Bileşenler gösterilen M′ üzerinde geçerli; JOSE Ek A.1 eşi T01'de geçerli; aynı anahtar ve başlıkla bizim imzamız iç tutarlı. Diğer 5 composite COSE örneği birebir doğrulandı. JOSE WG'ye bildirim dışa dönük eylemdir; yapılmadı (kullanıcı kararı).
8. **COSE `kid`.** JWK `kid`'inin (RFC 7638 parmak izi) base64url-çözülmüş 32 baytı (bstr). Metin kid bekleyen hedefler için anahtar yolu COSE_Key ya da doğrudan anahtardır (§2D m.1); COSE_Key'ler `anahtarlar/v1.3/cose-anahtarlar.json` ve her vektörün `dogrulama_girdileri.cose_key_hex` alanında.
9. **Kapsam.** COSE vektörleri genel COSE'dur (yük CBOR harita); mdoc MSO/DeviceResponse değildir (ISO 18013-5 kapsam dışı).
10. **Döngüsellik (G'deki not geçerli).** ÖK bu iş sırasında iki kez değişti (`dcc84092…` → `89648731…` → `87932cf0…`). Eşleme başlığı en son sürümü alıntılar; ÖK yeniden değişirse eşleme özeti de değişir. T11 başlık özetine bakmaz, alıntıları güncel ÖK'ye karşı denetler.

**Araç gözlemleri (hedef ölçümü değil).** COSE vektörleri JOSE karşılıklarının %51–74'ü: `COSE-VPLUS_ES256` 174 B (JOSE 341), `COSE-VPLUS_ML-DSA-65` 3.421 B (4.672), composite `COSE-K6` 3.491 B (`CMP00` 4.775), `COSE-K8` 6.295 B (`X5C04` 11.540), `COSE-K9` 14.659 B (`X5C07` 21.564). K7'de ECDSA bileşeni bozulması DER yapısını korur (r'nin son baytı); ret, ayrıştırmada değil imza doğrulamasında gelmelidir.

**İmajlar ve süreç.**
- `pq-a09-credgen:1.3` = `492b326d64fc` (FROM `pq-a09-signer:1.0` = `beeb05a70a97`). 1.0, 1.1 ve 1.2 korundu. v1, v1.1 ve v1.2 üretim kodu değişmedi; 1.3 `cbor.py`, `cose.py`, `v13.py`, `esleme.py` v1.3 bölümlerini ve testler `t10_cose.py`, `t12_cose.py` ile T10/T11 genişletmesini ekler. İmaj listesi önce/sonra: `kayit/docker_images_{once,sonra}_2026-09-26.txt` (tek fark `pq-a09-credgen:1.3`).
- Yalnız `pq-a09-*` adlı `--rm` konteynerler kullanıldı (`pq-a09-credgen`, `-dev13`, `-bagimsiz`, `-ls`). `prune` ya da toplu silme yapılmadı, git kullanılmadı, dışa dönük eylem yok. Konteyner bırakılmadı.
