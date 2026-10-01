# Adım 3 — ASP sistem modeli (kanıtlanmış soyutlamanın Katman 1'i)

- **Tarih:** 24–25.09.2026 · **Çalışma:** asp (Adım 3) · **Klasör:** `model\asp\` (yalnız bu klasöre yazıldı)
- **Araçlar:** clingo 5.8.2 + z3 5.1.0, imaj `pq-a02-solver:1.0` (konteyner adları `pq-a03-…`; `calistir.sh`). Tamarin koşulmadı.
- **Bağlayıcı girdiler:** ön kayıt §2A (Ö1–Ö12), §2C (D1′: 17 düğüm, birincil yapılandırma), §2D (m.11 `ca_baglama`, `ayni_ad_klasik_ca`), §2F (m.2 çerçeve kuralı); `gozden-gecirme\adim-01.md`, `adim-04.md`, `literatur.md`; Tamarin R1–R7 (`model\tamarin\`).
- **Kanıt kuralı:** Rapordaki her sayı `sorgular/sonuc/`, `z3/sonuc/`, `regresyon/sonuc/`, `ornekleme/` altındaki dosyalardan betikle derlendi (`sorgular/rapor_sayilari.py` → `sorgular/sonuc/rapor_sayilari.json`). Elle verilen hüküm kanıt değildir.

## 0. Özet

| Kabul ölçütü (teknik kapının ASP kısmı) | Sonuç |
|---|---|
| Bütün sorgular çözülür; süreler raporlanır | **52.693 sorgu çözüldü** (10 grup); 80.291 asgari küme. ASP toplam duvar 224,8 s (CPU 2.106,8 s); en uzun tek sorgu 2,01 s (k=3). **D1′ birincil sayımı (Q = 675): duvar 1,95 s, en uzun sorgu 0,088 s** (ölçüt <10 dk) |
| ASP–z3 uyumu %100 | **52.693/52.693 sorgu, 80.291/80.291 asgari küme birebir.** z3 kodlaması bağımsız yazıldı; sonlu k'da farklı yöntem (CEGAR, 4.705 karşı örnek). Ek: üç yönlü rastgele denetim (ASP, z3, Jacobi) **7.000/7.000** (tohum 20260928) |
| Pilot P2 regresyonu | Pilotun kaydı **48/48** yeniden üretildi; yeni çekirdek ve z3 pilotun 82 asgari kümesini **48/48** sorguda birebir verdi; P2b sırası birebir |
| Any-valid-path / anahtar sınıfı; Tamarin datalog 44 hüküm | Sistem çekirdeği **44/44** Tamarin hükmüyle aynı (ASP = z3 = Jacobi 44/44). Naif okuma (yalnız gerçek ebeveyn) yine yalnız `R1 X_alt_ca`'da yanılıyor |
| ≥10 örnekleme dışa aktarımı | §2F gereği **örnek seçilmedi; çerçevenin tamamı** dışa aktarıldı: `ornekleme/cerceve.jsonl` **2.442 satır** (SHA-256 `0a9b10d1…42d87`), `ornekleme/kesif_2x2.jsonl` **8.442 satır** (SHA-256 `c1e810c8…fb2ec`); beklenen hükümler ASP'de hesaplandı (asgari → verified 279/279; bir-eksik → falsified 2.163/2.163) |
| H1/H2/H4/H5 ÖN sonuçları | Tablolandı (§8). **Hepsi "ön"; bilimsel kapıda doğrulanacak** |

**Ek denetimler:** `ca_baglama` sağlık denetimi 675/675 + 675/675; 2×2 ızgarası önceden yazılan 6/6 beklentiyle tuttu (Tamarin R7hx ile aynı yön); R6 pencere sınıfı eşlemesi R6'nın kapsamında 588/588; strateji değerlendirmeleri üç yönlü 648/648, H4 karşılaştırmaları 109/109; optimum sıralarda ASP-DP = Jacobi-DP 36/36.

**Öne çıkan (ön) bulgular:**
1. **Birincil yapılandırmada G4 (ve "tümü") hiçbir PQ kümesiyle sağlanamıyor** (135/135 G4 hücresi UNSAT): imzasız istek HAIP gereği kabul ediliyor (T281), origin'i klasik WebPKI doğruluyor (T282), WRPRC doğrulaması ertelenmiş (faz0, T254) → RP başına kimliği doğrulanmış beklenti taşıyıcısı yok. `wrprc_faz1` OAT'ında G4/tümü P4 hücreleri SAT'a döner (54 hücre).
2. **H1 (ön): destekleniyor.** WebPKI PQ iken çekilen bağlamdaki düğümler (A01, A02, A06, A08, E_JVI, durum belirtecinin içindeki A03/A04 zinciri) asgari kümeden düşebiliyor; aktarılan bağlamda hiçbir düğüm düşmüyor; nominal τ'da klasik taşımayla ikame yok.
3. **H2′ (ön): destekleniyor.** Durum imza anahtarı V2/V3 kipinde hızlı → orta τ arasında A08 kümeden çıkıyor; V1'de hiçbir τ'da çıkmıyor. Yanlışlama (i) (sabit anahtar penceresinde belirteç ömrünün etkisi) 0/32; (ii) 66/180 grupta küme τ ile değişiyor.
4. **H5 (ön): destekleniyor.** Tek kullanım (cüzdan / doğrulayıcı) hiçbir hücrede kümeyi değiştirmiyor; A10'u orta/yavaş τ'da yalnız cnf penceresi (1 gün) düşürüyor. İstisna, paylaşılan durum gerektiren sınır varyantı (küresel tek kullanım + pasif toplayıcı).
5. **H4 (ön): aday var.** Birincil 36 hücredeki farklar uzun ömürlü anahtarlardan, beklenti eksikliğinden ya da Φ3'te yol dışı düğümlerden geliyor; Ö3 yorumuyla sayılmadı (onay bekliyor, NOTLAR N8). Ö3 hücrelerinde 10 aday: G4 (S5'in Φ1/Φ2 kümesinde A11/A12 yok) ve τ kaynaklı israf (cnf 1 g'de A10; V2/V3'te A08).

## 1. Model tanımı

### 1.1 Artefaktlar, kenar-artefaktlar ve karar düğümleri (§2C D1′)

**Sözleşme** (Tamarin R1–R5, pilot P2 ile aynı): `pq(A)` ⇔ A'yı **imzalayan anahtar** PQ (ya da composite). İmzasız artefaktlarda (A06, E_JVI, E_AS) `pq(A)` = nesne düzeyinde PQ bağlama (özet ya da PQ imzalı gösterim); bağlıysa sahteliği bağlandığı artefaktınkine indirgenir (`pq_baglar/2`).

**17 karar düğümü** (`pqd/1`; aynı düğümdeki örnekler birlikte göç eder; `olgular/artefaktlar.lp`). Son sütun, `02-izlenebilirlik\izlenebilirlik.csv`'de o artefakta atanmış T-satırlarıdır (matristen betikle çıkarıldı; parantez içindekiler başka artefakta atanmış ama bu düğümün yorumunu belirleyen satırlar):

| Düğüm | Model örnekleri | İmzalayan anahtar / anlam | W_güven (birincil) | Dayanak |
|---|---|---|---|---|
| a01 | a01_lotl | LOTL imzacısı (OJEU'da sabit) | 5 y | T001–T007 |
| a02 | a02_tl, a02_lote_pid, _cuzdan, _erisim, _kayit | TL imzacıları (LOTL'de listeli, OR T018); LoTE imzacıları (OJEU'da sabit T029) | 5 y | T008–T025, T027–T037 |
| a03 | a03_ca, a08_ca | Sağlayıcı çapa anahtarı (TL/LoTE'de listeli; x5c'de yasak T043); dış kaynak durum CA'sı (T180, T026) | 5 y | T038, T043, T063, T069 |
| a04 | a04_ihr | CA anahtarı (ihraççı, durum ve meta veri imzacı sertifikaları; T160, T161, T084) | 5 y | T039, T041–T042, T044–T047 |
| a05 | a05_meta (+ imzasız varyant) | Meta veri imza anahtarı; imzasız biçim varsayılan (T071, T086) | 1 y | T070–T087, T393–T394 |
| a06 | a06_tip | Type Metadata özet bağlaması (vct#integrity) | — | T090–T099, T101 |
| a07 | a07_kimlik | İhraççı imza anahtarı (kip V1/V2/V3) | 1 y (V1) | T102–T110, T112–T121, T175 |
| a08 | a08_durum | Durum imza anahtarı (kip V1/V2/V3) | 1 y (V1) | T026, T145–T174, T176–T180 |
| a09a | a09c_ornek | WIA'nın bağladığı örnek anahtarı (PoP; T187) | 1 g | T204 |
| a09b | a09a_wia, a09b_ka | Cüzdan sağlayıcı imza anahtarı (WIA ve KA) | 1 y | T199, T203, T204, T208, T399, T400 |
| a10 | a10_kbjwt | Cihaz (cnf) anahtarı; W = kimlik bilgisi geçerliliği | 30 g | T209–T214, T216–T239 |
| a11 | a11_erisim, a11_kayit | Access CA ve WRPRC sağlayıcı anahtarları | 5 y | T088–T089, T240–T247, T249–T267 |
| a12 | a12_istek (+ imzasız varyant) | RP anahtarı (WRPAC ile; kısa ömürlü değil T261) | 1 y | T248, T268–T274, T276–T281, T283–T300 |
| a13 | a13_webpki, a13_lotl_kanal | TLS sunucu kimlik doğrulaması PQ (WebPKI klasikken seçilemez) + OJEU-sabit LOTL indirme kanalı (T002) | 1 y | T275, T282, T302–T309, T311–T313 |
| ecrl | e_crl | Access CA CRL/OCSP imza anahtarı | 5 y | T255, T256 |
| ejvi | e_jvi | JWT VC Issuer Metadata/JWKS: yalnız HTTPS (T309–T311); pq = PQ bağlama | — | T309–T311 |
| eas | e_asmeta | AS meta verisi: yalnız yetenek (M-a; T188, T381); pq = imzalı biçim | — | T188, T381 |

Modelde 36 artefakt atomu var (26 imzalı, 10 imzasız); birincil yapılandırmada 29'u mevcut, 25 karar artefaktı 17 düğüme bağlı. Yardımcılar: OJEU kaynağı (`a00_ojeu`), imzasız varyantlar, adlandırılmış hücre artefaktları (alternatif klasik CA `a03_diger/a04_diger`, `a11_erisim_diger`, ikinci güven çerçevesi `a11_erisim_f2`) ve mekanizma kancaları (`m_d_cfg`, `m_g_oz`, `m_a_alan`).

### 1.2 Kenarlar: any-valid-path (`olgular/kenarlar.lp`)

- `kenar(E,A,B)`: A'yı imzalayan anahtarı B-sınıfı bir artefakt tanıtır (sertifikalar/listeler/cnf ile bağlar). **Doğrulayıcının kabul ettiği her tanıtıcı ayrı bir OR-kenarıdır;** A, kabul edilen herhangi bir tanıtıcısı sahtelenebiliyorsa sahtelenebilir. Dayanak (korpus kimlikleriyle; metinler `01-korpus\metin\` altında doğrulandı): [RFC5280] §6.2 "A system may provide any one of its trusted CAs as the trust anchor for a particular path"; [RFC6840] §5.11 "Validators SHOULD accept any single valid path" (T364) ve §6.2 "any DNSKEY in the zone's signed DNSKEY RRset may be used to authenticate any RRset in the zone"; Tamarin R1 `X_alt_ca` (anahtar sınıfı semantiği).
- 37 kenar olgusu, 24 kenar koşulu. `guven-bagimliligi.dot`'un **28 kenarının 28'i** eşlendi (`dot_kenar/4`; RAPOR ekinde değil, olgu dosyasında).
- OR-kenarı örnekleri: birleşik güven deposunda CA çapası hem PID LoTE'de hem ulusal TL'de (T033, T034); durum imzacısı aynı CA ya da dış kaynak CA (gevşek bağlamada ikisi); JVI alternatif anahtar yolu; alternatif klasik CA (bağlamaya göre); A.3.2.2 ikinci güven çerçevesi.
- **`ca_baglama` (§2D m.11):** alternatif klasik CA'nın kenarı iki koşullu kopyadır: `ca_baglama = yok` **ya da** (`ca_baglama = ad` ∧ `ayni_ad_klasik_ca = var`). `anahtar` bağlamada hiç etkin değildir (Tamarin R7hx ile aynı yapı).

### 1.3 Kanal sınıfları ve taşıma

| Kanal | Ulaştırma kuralı | Örnek |
|---|---|---|
| `aktarilan` | Her zaman (sunan/saldırgan getirir) | kimlik bilgisi, x5c, KB-JWT, istek (DC API), WRPAC |
| `sunan_uc` | Her zaman (kaynak doğrulanacak tarafın kendisi; T284) | `request_uri` |
| `cekilen` | Yalnız taşımanın sunucu kimlik doğrulaması sahtelenebiliyorsa | LOTL, TL/LoTE, durum listesi (çevrimiçi), meta veri, CRL |
| `yalniz_tasima` | Aynı (nesne imzası yok; tek koruma taşıma) | imzasız meta veri, imzasız istek (origin), JVI, özetsiz Type Metadata |
| `sabitlenmis` | Hiçbir zaman | OJEU, bant dışı yapılandırma (M-d) |
| `kimliksiz` | Her zaman (S1 bile değiştirir) | M-a alanı |

Taşımanın sahtelenebilirliği, taşımayı temsil eden artefaktın (`a13_webpki`, `a13_lotl_kanal`) etkin sahteliğidir.

### 1.4 Zaman: pencereler, anahtar kipleri, τ (`olgular/pencereler.lp`)

- **exposure(K)** = `maruziyet(A,0)` (en kötü durum: açık anahtar pencerenin başında gözlenir); **last_accept(K)** = `son_kabul(A,L)`; **W_güven = L − E**. S2, klasik K ile imzalanan artefaktı ancak **τ < W_güven + saat payı** iken sahteleyebilir. Ön kayıt §4.5'teki kural τ < W_güven(K) (katı eşitsizlik); saat payı (300 s; T392) modelin ekidir ve OAT'ta (0, 60, 600 s) hiçbir hücreyi değiştirmiyor.
- **Pencere sınıfları** (Tamarin R6 ile): `uzun_omurlu` ↔ LONG (V1 ya da KEY_REUSE), `donem` ↔ ROTATED (V2: W = 1 g + belirteç/kimlik bilgisi geçerliliği), `belirtec` ↔ PER_TOKEN (V3: W = geçerlilik; kimlik bilgisi başına cnf). V2/V3 anahtarlarını CA'nın düzenlediği kısa ömürlü sertifika bağlar: **kimlik = CA zinciri (R6 `ID_PQ`)**; `anahtar_yeniden_kullanim = var` = R6 `KEY_REUSE`.
- **Belirteç ömrü tek başına belirleyici değildir (Ö1):** yalnız kip onu anahtara bağladığında W'ye girer. TL/LoTE ≤6 ay, WIA <24 sa gibi sabit pencereler W_kabul'dür.
- **τ:** nominal 600 s / 3 g / 26 g; duyarlılık hızlı {1, 10, 60} dk, orta {1, 3, 7, 10} g, yavaş {14, 26, 60} g (§2C 2.3); A5 geniş ızgarası 11 değer: 84 s … 1.000 g ve "∞" (2,1·10⁹ s ≈ 66,5 y ile temsil).
- **k (Ö8):** sınırsız (birincil) = tek senaryo `tum`; S1 = senaryo `bos`; k ∈ {1, 3} = ilgili anahtarların min(k, n) elemanlı bütün altkümeleri (ihlal, kırılan anahtar kümesinde tekdüze arttığı için yeterli). Anahtar kimlikleri: A (imzacı), alt(A) (klasik alternatif anahtarı), `p3_kanal` (P3'ün klasik yapılandırma kanalı).

### 1.5 Faz, çıpa, WebPKI, politika ve parametreler (birincil yapılandırma)

- **Φ (§4.2; Ö10#1):** Φ1 bütün karar artefaktlarında klasik alternatif; Φ2 yalnız yaprak sınıflarda (a05–a12, e_jvi, e_asmeta); Φ3 hiçbirinde. PKI: a01–a04, a13, e_crl.
- **Çıpa (§4.6):** `taze`; `sabit` = TL imza anahtarı bant dışı (R5); `onbellek` = önceki alımın süreli kopyası. Kararlı durumda `onbellek` ≡ `taze` (birincilde 225/225 önbellek hücresi aynı); `onbellek_ufku = ilk_pencere` Q-day'den önce doldurulmuş kopyanın ilk penceresini ayrıca modeller (OAT).
- **Politika (§4.8):** P0–P2 beklenti kullanmaz (bu soyutlamada üçü eşdeğer: kırılan klasik anahtarla tek imza yeter); P3 beklentiyi klasik kanaldan öğrenir (S1'de sağlam; k = 1'de yalnız tek hedefe bakılınca, zamansız G5 ile birlikte değil; NOTLAR N9); P4 PQ-doğrulamalı taşıyıcıdan.

| Parametre | Birincil | Kaynak |
|---|---|---|
| WebPKI | klasik (A13 PQ seçilemez) | §2C 2.3 |
| k | sınırsız | §2C 2.3 |
| iptal_denetimi / cihaz_bagi / rp_auth_fail_open | var / var / yok | §2C 2.3 (T178, T228, T247) |
| wrprc_dogrulama | faz0 | §2C 2.3 (T254) |
| ca_baglama / ayni_ad_klasik_ca | yok / yok | §2D m.11 |
| sdjwtvc_surum | -13 | §2C 2.3 |
| durum_anahtari / ihracci_anahtari / cihaz_anahtari | V1 uzun / V1 uzun / kimlik bilgisi başına | §2C 2.3, Ö1 |
| W_güven: w_kok, w_ca, w_ihracci, w_rp, w_tls, w_wia, w_ka | 5 y, 5 y, 1 y, 1 y, 1 y, 1 g, 1 y | §2C 2.3 |
| kimlik_gecerlilik (cnf), durum_ttl, kbjwt_iat, saat payı | 30 g, 1 g, 10 dk, 5 dk | §2C 2.3; saat payı tabloda yok (T392 "birkaç dakika") |
| Modele özgü (tabloda yok; NOTLAR N13): kimlik_turu pid, guven_deposu birleşik, anahtar_cozumleme x5c, lotl_indirme OJEU-sabit (T002), durum_imzaci aynı CA, durum_baglama sıkı, durum_kanali çekilen, istek_iletimi DC API, imzasız istek/meta kabulü var (T281, T086), tmd_isleme yok (T096), durum_listesi var, tek_kullanim cüzdan (T230), wscd_pq var, diger_ca yok, coklu_cerceve yok, mekanizma kancaları kapalı | temkinli ya da spesifikasyon varsayılanı | NOTLAR N13 |

### 1.6 Hedefler (`olgular/hedefler.lp`)

G1 kimlik bilgisi (+ işlenen Type Metadata); G2 KB-JWT; G3 durum belirteci (durum listesi varsa); G4 istek nesnesi (+ kabul edilen imzasız varyant); politika ihlalleri (`cihaz_bagi = yok` → G2; `iptal_denetimi = yok` → G3; `rp_auth_fail_open = var` → G4). **G5-zamansız (Ö11):** hedef yolundaki göç etmiş varlığın klasik alternatifi açık ve beklentisi yokken ya da imzasız biçimi kabul edilirken ihlal. **G2i (keşifsel):** ihraç tarafı WIA/KA güvencesi.

### 1.7 Beklenti taşıyıcıları ve mekanizma kancaları (`olgular/tasiyicilar.lp`)

`tasi(C,X)` (= `convey/2` kancası): C, X'i imzalayan varlık için "PQ gerekli" beklentisi taşır; karar değişkenidir (asgari kümeye girer). 61 taşıyıcı olgusu: **M-f** (OJEU, LOTL işaretçisi, TL/LoTE kaydı; WRPRC yalnız faz1), **M-e′** (imzalı meta verideki "required"), **M-h** (sertifika eki; kanca: yalnız C bütün kabul yollarına baskınsa ve klasik alternatifin yolundaysa etkili — alternatif CA/JVI yolu baskınlığı bozar), **M-g** (öz-beyan/TOFU; kanca: ilk temas Q-day'den önceyse özgün), **M-d** (bant dışı yapılandırma; kanca), **M-a** (kimliksiz alan; kanca). A3 bileşen kancaları (`mf_kapali(tazelik|tekduzelik|kapsam)`) hazır. Beklenti yalnız K4'ü ve imzasız varyantları kapatır; alternatif tanıtıcı yollarını (başka CA, JVI, ikinci çerçeve) kapatmaz — bunları bağlama parametreleri kapatır. `kenar/3` kimlikleri, Adım 7'nin `beklenti_kapsami ∈ {yaprak_alg, yol_sinifi, anahtar}` denetimini (§2D m.13) kabul edilen yolun kenar sınıfları üzerinden kurmaya hazırdır.

## 2. Çekirdek kurallar (`cekirdek.lp`) ve semantik gerekçesi

Pilot/Tamarin K1–K4'ün genellemesi (S = kırılma senaryosu):

| Kural | ASP | Gerekçe |
|---|---|---|
| K1 (zamanlı) | `basar(S,A) :- kirilir(S,A).` `kirilir` = klasik ∧ senaryoda kırılabilir ∧ τ < W + pay | R1, R4, R6 |
| K2 (any-valid-path) | `basar(S,A) :- kabul_alti(A,B), etkin_sahte(S,B), not sabit_etkin(A).` | R1 X_alt_ca; RFC 5280 §6.2; `sahte(B)` = B-sınıfından kabul edilen keyfi örnek üretilebilir |
| K3 (beklenti) | `beklenir(S,X) :- tasi(C,X), mekanizma_uygun(C,X), p(politika,p4), not etkin_sahte(S,C), ...` (P3: ayrıca `not p3_kirik(S)`) | R2, R3 |
| K4 (zamanlı) | `basar(S,A) :- kirilir_alt(S,A), not beklenir(S,A).` | R2 (birlikte yaşama) |
| İmzasız | bağlanmamışsa her zaman basılır; PQ-bağlıysa sahteliği bağlandığınınki | T071, T090, T309 |
| Kanal | `sahte = basar ∧ ulasir ∧ ¬ozgun`; çekilen/yalnız-taşıma yalnız taşıma sahteyse ulaşır | R3a, H1 |
| Varyant | `etkin_sahte(A)` = sahte(A) ∨ (kabul edilen imzasız biçim ∧ ¬beklenir(A) ∧ sahte(biçim)) | M-b0 (T281) |

Semantik her senaryo için tabakalıdır; bağımlılık grafiği döngüsüzdür (z3 kodlayıcısı döngüde hata verir; Jacobi en çok 8 turda yakınsar). Güvenli kümeler ailesi yukarı kapalıdır (PQ ya da taşıyıcı eklemek saldırı eklemez), bu yüzden `domRec`'in alt küme asgarileri ile z3'ün tek-eleman indirgemesi aynı kümeleri verir.

## 3. Sorgu kataloğu (`sorgular/katalog.py`; §2C ayrımı)

| Grup | Tür | Tanım | Sorgu |
|---|---|---|---|
| birincil | **birincil** | Q = hedef{G1–G4, tümü} × Φ × τ{3} × çıpa{3} × politika{5} | 675 |
| h1 | **2.4 tasarım** | WebPKI{cl, pq} × 8 kanal etiketi varyantı × Q ((cl, birincil) = birincil) | 10.125 |
| h2 | **2.4 tasarım** | {durum, ihraççı} anahtarı × kip{V2, V3} × Q (V1 = birincil) | 2.700 |
| h5 | **2.4 tasarım** | cnf penceresi 1 g × Q (30 g = birincil) | 675 |
| h4 | **2.4 tasarım** | Ö3 adlandırılmış hücreleri + sadakat hücresi | 89 |
| cab | keşifsel | §2D m.11 2×2 × Q (2.700) + `ca_baglama = yok` sağlık denetimi × Q (3 yapılandırma: alternatif CA var × bayrak {yok, var}; alternatif CA yok × bayrak var; 2.025) | 4.725 |
| oat | duyarlılık | birincilden tek parametre sapması (46 sapma) × Q | 31.050 |
| tau | duyarlılık | τ duyarlılık değerleri × Q (τ hariç) | 1.575 |
| a5 | ek (Ö1 kanıt ızgarası) | anahtar kipi × belirteç ömrü × τ geniş; saat payı sınırı | 964 |
| h | adlandırılmış | H0, H3-ön, H5 tek kullanım, R6 KEY_REUSE, M-g/M-h/M-d/M-a kancaları | 115 |
| **Toplam** | | | **52.693** |

Her sorgu: `asgari_kumeler()` (clingo `--heuristic=Domain --enum-mode=domRec`, karar atomları `pqd/1` ve `tasi/2`). Süreler (`sorgular/sonuc/<grup>.json` ozet):

| Grup | Sorgu | SAT | UNSAT | Asgari küme | ASP duvar (s) | ASP en uzun (s) | z3 eşit | z3 duvar (s) | z3 en uzun (s) | CEGAR |
|---|---|---|---|---|---|---|---|---|---|---|
| birincil | 675 | 189 | 486 | 279 | 1,95 | 0,088 | 675/675 | 0,46 | 0,069 | 0 |
| h1 | 10.125 | 3.897 | 6.228 | 7.434 | 32,93 | 0,127 | 10.125/10.125 | 10,70 | 0,194 | 0 |
| h2 | 2.700 | 804 | 1.896 | 1.140 | 9,13 | 0,160 | 2.700/2.700 | 2,48 | 0,091 | 0 |
| h5 | 675 | 189 | 486 | 255 | 2,10 | 0,052 | 675/675 | 0,68 | 0,080 | 0 |
| h4 | 89 | 58 | 31 | 73 | 0,73 | 0,091 | 89/89 | 0,20 | 0,051 | 0 |
| cab | 4.725 | 756 | 3.969 | 1.116 | 16,30 | 0,099 | 4.725/4.725 | 4,14 | 0,199 | 0 |
| oat | 31.050 | 8.604 | 22.446 | 68.142 | 151,85 | 2,007 | 31.050/31.050 | 252,46 | 201,848 | 4.668 |
| tau | 1.575 | 441 | 1.134 | 639 | 5,70 | 0,124 | 1.575/1.575 | 1,70 | 0,155 | 0 |
| a5 | 964 | 964 | 0 | 964 | 3,69 | 0,076 | 964/964 | 0,93 | 0,056 | 0 |
| h | 115 | 89 | 26 | 249 | 0,44 | 0,048 | 115/115 | 1,42 | 1,236 | 37 |

(Paralel 10 süreç; 12 vCPU'lu WSL2 konteyneri. z3'ün en uzun sorgusu `oat|md_kanca_acik|tum|f1|hizli|taze|p4`: bant dışı yapılandırma kancası açıkken taşıyıcı birleşimleri patlıyor, hücrenin **5.888** asgari kümesi var; tek-eleman indirgemesi ve engelleme bu sayıyla doğrusal büyüyor. ASP aynı hücreyi 0,52 s'de sayıyor: topraklama 0,04 s, çözüm 0,48 s.)

## 4. Sonuç tabloları

### 4.1 Birincil yapılandırma (Q = 675)

SAT hücre sayısı (τ × çıpa = 9 hücre üzerinden; `sorgular/sonuc/analiz/birincil.csv`):

| hedef | Φ | P0 | P1 | P2 | P3 | P4 |
|---|---|---|---|---|---|---|
| G1, G2, G3 | Φ1 | 0/9 | 0/9 | 0/9 | 0/9 | 9/9 |
| G1, G2, G3 | Φ2 | 0/9 | 0/9 | 0/9 | 0/9 | 9/9 |
| G1, G2, G3 | Φ3 | 9/9 | 9/9 | 9/9 | 9/9 | 9/9 |
| G4, tümü | Φ1–Φ3 | 0/9 | 0/9 | 0/9 | 0/9 | 0/9 |

Asgari kümeler (düğüm; taze çıpa; τ'nun üç değerinde aynı):

| Hedef | Φ3 (P0–P4) | Φ2, P4 | Φ1, P4 |
|---|---|---|---|
| G1 | {a01, a02, a03, a04, a07} | aynı düğümler + `tasi(a02_lote_pid, a07_kimlik)` ya da {+a05} + `tasi(a02_lote_pid, a05_meta)`, `tasi(a05_meta, a07_kimlik)` | Φ2 kümeleri + 5 PKI taşıyıcısı: `tasi(a00_ojeu, a01_lotl)`, `tasi(a00_ojeu, a02_lote_pid)`, `tasi(a01_lotl, a02_tl)`, `tasi(a02_lote_pid, a03_ca)`, `tasi(a02_lote_pid, a04_ihr)` |
| G2 | G1 ∪ {a10} | G1 kümeleri ∪ {a10} + a10 için taşıyıcı (PID LoTE ya da meta veri): 4 küme | aynı + 5 PKI taşıyıcısı: 4 küme |
| G3 | {a01, a02, a03, a04, a08} | aynı + `tasi(a02_lote_pid, a08_durum)` ya da {+a05} + meta veri yolu | aynı + 5 PKI taşıyıcısı |
| G4, tümü | UNSAT | UNSAT | UNSAT |

- **Çıpa:** `sabit`, 54 hücrede a01'i düşürür (R5): Φ2-P4'te 9, Φ3'te 45. Φ1-P4'te düşürmez (9 hücre), çünkü birlikte yaşamada TL'nin klasik alternatifi ancak LOTL'nin taşıdığı beklentiyle kapanır (`tasi(a01_lotl, a02_tl)`). `onbellek` hücrelerinin **225/225**'i `taze` karşılığıyla aynı (kararlı durum).
- **Politika:** Φ1/Φ2'de P0–P3 UNSAT (beklenti yok ya da P3'ün klasik kanalı S2'de sahte): H3'ün ön sinyali. Φ3'te P0–P4 aynı kümeler.
- **G4 neden UNSAT:** imzasız istek (M-b0) → origin → klasik WebPKI. RP başına kimliği doğrulanmış tek taşıyıcı WRPRC'dir ve yalnız faz1'de etkindir; bant dışı yapılandırma (M-d kancası) da G4'ü açar (OAT). Bu, H1'in G4 yüzü ve M-b0'ın biçimsel izidir (NOTLAR N7).

### 4.2 Stratejiler S0–S8 × M1–M5 (ÖN; `sorgular/stratejiler.py`)

Taslak atama: `sorgular/stratejiler_taslak.json` sürüm 2 (SHA-256 `11b05877…`; karşılaştırmadan önce). M1 = 36 hücre (G1–G4 × Φ × τ; taze); 648 değerlendirme, üç yönlü 648/648.

| Strateji | M1 (cl) | M1 (pq) | M2 düğüm Φ1/Φ2/Φ3 (ağırlıklı), cl | M3 vekil | M4 yapısal | M5 (WSCD) |
|---|---|---|---|---|---|---|
| S0 statüko (HAIP + bant dışı klasik; Ö5) | 0/36 | 0/36 | 0/0/0 | 0 | 0 | hayır |
| S1 kimlik-bilgisi-önce | 0/36 | 0/36 | 1/1/1 | 0 | 1 | hayır |
| S2 ECCG AND, beklentisiz (P1) | 9/36 | 15/36 | 16/16/16 (122) | 2 | 1 | evet |
| S3 composite + bant dışı (M-d) | 36/36 | 36/36 | 16/16/16 (122) | 2 | 0 | evet |
| S4 8725bis yerel, klasik kaynak (P3) | 9/36 | 15/36 | 16/16/16 (122) | 2 | 0 | evet |
| S5 önce kök ve cihaz (P1) | 9/36 | 12/36 | 4/6/16 (110/112/122) | 2 | 1 | evet |
| S5e (keşifsel: S5 + P4 + M-f) | 15/36 | 18/36 | 4/6/16 | 2 | 0 | evet |
| S6 big-bang (P4 + M-f) | 27/36 | 30/36 | 16/16/16 (cl), 17 (pq) | 2 | 0 | evet |
| S7 hesaplanan (P4) | 27/36 | 33/36 | hücre başına 5–6 (pq: 1–7) | — | — | 9/27 hücre (cl); 12/33 (pq) |
| S8 geçici direnç (Anchuri) | 6/36 | 11/36 | 13/13/13 (119) | 2 | 0 | hayır |

- **Önceden kayıtlı sorular (cl):** (1) S5, S7'nin sağladığı her hücreyi sağlıyor mu? **Hayır:** S7 27 hücre, S5 9 hücre sağlıyor; S5'in eksik kaldığı 18 hücre Φ1/Φ2'nin G1–G3 hücreleri. (2) S5 fazladan artefakt istiyor mu? **Evet, 9 hücrede:** Φ3'te S5 16 düğümün hepsini göç ettiriyor, hedef yolunda olmayanlar fazlalık. (3) S1 ve S2 Q-day sonrası kaç hücreyi sağlıyor? **S1: 0; S2: 9.** Beklenen 0 yalnız S1'de tuttu. S2 (P1, beklentisiz) Φ3'ün G1–G3 hücrelerini sağlıyor, çünkü Φ3'te klasik alternatif yok: sınıf düzeyi gün batımı, beklenti kanalı olmadan da yeterli (NOTLAR N6).
- **S3 36/36:** bant dışı (M-d) beklenti sabitlenmiş ve özgün varsayıldığı için; işletim maliyeti (her doğrulayıcıda varlık başına yapılandırma) modelde yok (sınırlılık).
- **S8** (taslak tanımı: V3 ihraççı ve durum anahtarı, kimlik bilgisi başına cnf, uzun ömürlü kimlikler PQ, P4 + M-f): cl'de **yalnız G3'ü orta ve yavaş τ'da** sağlıyor (6 hücre). Durum anahtarının penceresi 1 g TTL < τ. G1'de ihraççı anahtarının V3 penceresi (30 g geçerlilik) ve G2'de cnf penceresi (30 g) nominal τ'lardan uzun; bu yüzden sağlamıyor. WSCD değişimi gerekmez (M5 = hayır).
- M3 ve M4 **yapısal vekillerdir** (bayt ölçümü Adım 12; varlık düzeyi nüfus modeli yok).

### 4.3 ca_baglama 2×2 ve sağlık denetimi (§2D m.11; keşifsel)

Beklentiler koşumdan önce: `sorgular/beklenti_2x2.json` (SHA-256 `c0899c5f…`; tek hücre duman testi önceden koşuldu — NOTLAR N2). Yapılandırma: alternatif klasik CA var (strateji dışı), Q = 675.

| Kombinasyon | Sonuç | Beklenti | Tamarin R7hx |
|---|---|---|---|
| ad / yok | 675/675 hücre birincil ile aynı | korur ✓ | X_namebind_unique = V |
| ad / var | G1–G4 ve tümü: 675/675 UNSAT; birincil asgari kümelerin 279/279'u bu hücrede falsified | atlatılır ✓ | X_namebind_samename = F |
| anahtar / yok | 675/675 birincil ile aynı | korur ✓ | X_keybind_distinct = V |
| anahtar / var | 675/675 birincil ile aynı | korur ✓ | X_keybind_samename = V |
| sağlık: yok, alternatif CA var | bayrak yok ve var: ikisinde de 675/675 UNSAT (birincilin 189 SAT hücresinin hepsi düşer); iki bayrak değeri 675/675 aynı | bayrak etkisiz ✓ | M_no_namebind = F |
| sağlık: yok, birincil (alternatif CA yok) | bayrak var: 675/675 birincil ile aynı | bayrak etkisiz ✓ | — |

(Tamarin sütunu: `model\tamarin\RAPOR.md` R7h/R7hx tablosundaki G1/G5 hükümleri; V = verified (korur), F = falsified (atlatılır). Lemma adları oradan okundu.)

Sadakat hücreleri (Ö3: "model sadakati kanıtı", RFC 6840 §6.2, Kim vd. M2; (2a) sayılmaz; `h4.json` SADAKAT satırları, P4): alternatif klasik CA göç ettirilemiyorsa (`klasik_sabit`) ve `ca_baglama = yok` ise G1 Φ1–Φ3'te UNSAT; `ca_baglama = ad` (farklı adlı CA) ise birincil kümelerle SAT. Alternatif CA aynı düğümle göç ediyorsa (`karar`) G1 Φ2/Φ3'te SAT, Φ1'de UNSAT.

### 4.4 Tamarin R6 pencere sınıfı eşlemesi (A5 G1/G3; `analiz/r6_esleme.csv`)

R6'nın rejimleri sembolik; sayısal okuma: FAST τ ≤ belirteç penceresi; MEDIUM belirteç < τ ≤ dönem penceresi; SLOW τ > dönem penceresi (uzun ömürlü pencerenin altında). A5 ızgarasının 672 G1/G3 hücresinden R6'nın kapsamındaki 588 hücrede (sınıf sayımı: uzun/LONG 196; V2 FAST 140, MEDIUM 4, SLOW 52; V3 aynı) ASP ile R6 koşulu (G3 V ⇔ ID_PQ ∧ ¬KEY_REUSE ∧ ((PER_TOKEN ∧ (MEDIUM ∨ SLOW)) ∨ (ROTATED ∧ SLOW))) **588/588 uyumlu**; kimlik (CA zinciri) karşılaştırılan her hücrede gerekli. Kapsam dışı 84 hücre: 42 `TASIMA_KORUR` (τ > TLS penceresi: çekilen durum belirteci klasik taşımayla da korunur — R6'da taşıma yok), 42 `UZUN_OTESI` (τ > uzun ömürlü pencere). KEY_REUSE adlandırılmış hücrelerinde (`h|R6_reuse_*`: V2/V3 + yeniden kullanım × 3 nominal τ) A08 altı hücrenin altısında gerekli (R6 `M_rot_reuse`: G3 = F, `M_long_key` = V ile aynı yön).

**Sayısal eşleme (fark değil, okuma notu):** §2C birincil değerlerinde (TTL 1 g; V2 penceresi 2 g) nominal "orta" τ = 3 g, V2 için R6'nın **SLOW** sınıfına düşer; bu yüzden ASP'de rotasyonlu durum anahtarı orta ve yavaş nominal rejimde korunur. Kimlik bilgisi (30 g) için ise bütün nominal τ'lar FAST sınıfındadır. MEDIUM yalnız A5'te görünür: TTL 1 sa, τ ∈ {14 sa, 1 g} hücrelerinde V3 korunur, V2 korunmaz (R6 L-D3 ızgarası: `E_rot_medium` = F, `P_tok_medium` = V). Sekiz MEDIUM satırının sekizi uyumlu.

### 4.5 OAT duyarlılığı (Q × 46 sapma; `analiz/oat.json`)

| Sapma | Değişen hücre (/675) | SAT→UNSAT | UNSAT→SAT | Hedefler |
|---|---|---|---|---|
| k1 | 297 | 0 | 108 | G1 81, G2 81, G3 135. Tek kırmayla çekilen artefakt sahtelenemez (imza + taşıma = 2 kırma): G1/G2 kümesi {a03, a04, a07 (+a10)}, a01/a02 düşer; **G3'te ∅ yeter** (durum belirteci çekilen). UNSAT→SAT: G1/G2'de Φ1/Φ2-P3 (36), G3'te Φ1/Φ2-P0…P3 (72) |
| k3 | 9 | 0 | 0 | G1–G3, yalnız sabit çıpa + Φ1 + P4: a01 düşer. LOTL üzerinden TL beklentisini düşürmek 4 kırma ister: {a01_lotl, a13_lotl_kanal, alt(a02_tl), a13_webpki}. Değerlendirme kipinde doğrulandı: k3 kümesine karşı bu dört anahtar birlikte G1'i çiğniyor, dört üçlüsünün hiçbiri çiğnemiyor |
| diger_ca_var (ca_baglama yok) | 189 | 189 | 0 | G1–G3 (sadakat hücresi: alternatif klasik CA yolu) |
| guven_deposu_liste_bagli | 135 | 0 | 0 | G1–G3: a01 düşer (çapa yalnız OJEU-sabit PID LoTE'de; ulusal TL yolu yok) |
| durum_listesi_yok | 135 | 0 | 72 | G3 (iptal süre dolumuyla; durum listesi yolu yok) |
| md_kanca_acik | 108 | 0 | 54 | G1–G3 Φ1/Φ2-P4'te küme ailesi büyür (ör. G2 Φ1: 4 → 448, G1/G3 Φ1: 2 → 128); G4/tümü P4'te UNSAT→SAT (bant dışı beklenti) |
| cihaz_bagi_yok / iptal_denetimi_yok / wscd_pq_yok | 63 / 63 / 63 | 63 / 63 / 63 | 0 | G2 / G3 / G2 (politika ihlali ya da a10 seçilemez) |
| durum_imzaci_farkli_capa | 63 | 0 | 0 | G3: a04'süz asgari küme doğar (durum imzacısını dış kaynak durum CA'sı sertifikalar) |
| onbellek_ufku_ilk_pencere | 63 | 0 | 0 | G1–G3 önbellek hücreleri: a01/a02 düşer (Q-day öncesi doldurulmuş kopya ilk pencerede sahtelenemez) |
| webpki_pq_birlikte | 63 | 0 | 0 | G1–G3 P4: düğüm kümeleri aynı; a01 yerine {a13 + `tasi(a00_ojeu, a13_lotl_kanal)`} alternatif kümesi eklenir. OJEU-sabit LOTL indirme kanalı OJEU'nun taşıdığı beklentiyle PQ'ya kilitlenebilir; genel WebPKI için varlık başına beklenti taşıyıcısı olmadığından `pq_birlikte` klasikle eşdeğer |
| kimlik_turu_qeaa | 54 | 0 | 0 | G1–G3 Φ1/Φ2-P4: düğümler aynı, taşıyıcı PID LoTE yerine ulusal TL (`tasi(a02_tl, …)`) |
| wrprc_faz1 | 54 | 0 | 54 | G4/tümü P4: UNSAT→SAT. G4 kümesi {a02, a11, a12} + WRPRC taşıyıcısı `tasi(a11_kayit, a12_istek)` (Φ3'te bile gerekli: imzasız istek varyantını yalnız bu beklenti kapatır; Φ1'de + 4 LoTE/OJEU taşıyıcısı) |
| tek_kullanim_kuresel_pasif | 42 | 0 | 0 | G2 orta/yavaş: a10 düşer (pasif toplayıcı + küresel tek kullanım: W = iat penceresi 10 dk) |
| mekanizma_kancalari_acik | 36 | 0 | 0 | G1/G2 Φ1/Φ2-P4: M-h alternatifi eklenir (`tasi(a03_ca, a07_kimlik)`) |
| durum_baglama_gevsek | 9 | 0 | 0 | G3 Φ1-P4: dış kaynak durum CA'sı için ek taşıyıcı (`tasi(a02_lote_pid, a08_ca)`) |
| **Etkisiz (0 hücre):** anahtar_yeniden_kullanim, ayni_ad_klasik_ca, ca_baglama ad/anahtar (alternatif CA yokken), cihaz_anahtari_kalici, cnf 180 g / 1 y, coklu_cerceve, durum_ttl 1 sa / 7 g, gun_batimi_iptal, kbjwt_iat 1/60 dk, ma_kanca, rp_auth_fail_open (G4 zaten UNSAT), saat payı 0/60/600, sdjwtvc_s19, tek_kullanim yok/doğrulayıcı, w_ca/w_kok 1 y, w_ihracci 30/180 g, w_ka/w_rp 180 g, w_tls 47 g, wia_anahtari_kalici | | | | |

τ duyarlılığı (Q × τ değeri): yalnız yavaş 60 g (5.184.000 s) 21 hücrede fark verir. Hepsi G2 ve hepsinde yalnız a10 düşüyor (cnf 30 g < τ). Diğer altı τ değeri 0 hücre değiştiriyor.

### 4.6 A1 gereklilik ve optimum sıralar

- **A1:** Birincil çerçevedeki 2.163 bir-eksik kümenin **hepsi** hücrenin hedefini çiğniyor (asgariliğin doğrudan sonucu; değerlendirme kipinde doğrulandı). Taşıyıcı çıkarıldığında G5 de düşer (G1: 144/144, G2: 342/342, G3: 144/144 satır). Düğüm başına satır sayıları `rapor_sayilari.json` → `a1`.
- **Sıralar** (`sorgular/sira.py`; pilot P2b amacı; DP, 36 hücre): ASP-DP = Jacobi-DP **36/36**; 27 hücrede tek en iyi sıra. En iyi sıralar kökten yaprağa (a01 → a02 → a03 → a04 → yaprak; Φ1'de a02–a04 arası serbest, 6 sıra) — Ö3 ve GİRMEYİN #18 gereği bu bir katkı değildir. Pilot P2b sırası (lotl → tl_pid → ca_iss → iss_cert → cred) yeni çekirdekle birebir.

## 5. ASP–z3 uyumu ve üç yönlü denetim

- **Bağımsızlık:** z3 tarafı (`z3/yapi.py`, `z3/z3_kodlama.py`) ASP çekirdeğini okumaz; yalnız zemin olgu dosyalarını okur, koşulları, pencereleri, fazı ve M-h baskınlığını kendi koduyla yorumlar; formülleri bağımlılık grafiği üzerinde bellekli özyinelemeyle kurar. Asgari kümeler: model → tek-eleman indirgeme → üst kümeleri engelleme. Sonlu k: CEGAR (ASP'nin senaryo sayımından farklı yöntem).
- **Sonuç:** 52.693/52.693 sorgu, 80.291/80.291 asgari küme (`z3/sonuc/uyum_*.csv`, `uyum_ozet.json`).
- **Üç yönlü rastgele denetim (ek; tohum 20260928):** 7 sorgu sınıfı (g1, g2, g2i, g3, g4, g5, tümü) × 1.000 yapılandırma (bütün kategorik parametreler, pencere ve τ ızgaraları, kırılma kipi {k sınırsız, S1, rastgele kırık küme}, rastgele PQ/taşıyıcı ataması): ASP = z3 = Jacobi **7.000/7.000** (ihlal ve sahte kümeleri; `z3/sonuc/uclu_rastgele.json`).
- **Yakalanan hata (şeffaflık):** Tamarin örneklerinde karar dışı artefaktlara verilen sabit PQ ataması z3/Jacobi değerlendirme kipinde okunmuyordu (ekosistemde bütün PQ'lanabilir artefaktlar karar değişkeni olduğu için görünmüyordu); düzeltildi, bütün denetimler yeniden koşuldu.

## 6. Regresyon

- **Tamarin datalog (44 hüküm; `regresyon/tamarin_esdegerlik.py`):** R1–R5'in 34 bayrak yapılandırması sistem çekirdeğinin olgu biçimine çevrildi (`regresyon/tamarin_datalog/ornekler/*.lp`; τ = 600 s, pencere sonsuz, Dolev–Yao = aktarılan). **44/44** Tamarin hükmüyle aynı; ASP = z3 = Jacobi 44/44. Naif okuma yalnız `R1 X_alt_ca`'da yanılıyor (any-valid-path gerekliliğinin yeniden gösterimi).
- **Pilot P2 (48 sorgu; `regresyon/p2_regresyon.py`):** Pilotun kendi programı yeniden koşuldu ve kaydı (sayı, asgari kardinalite, ilk ≤6 küme) **48/48** üretildi; pilot topolojisi yeni çekirdeğin olgu biçiminde (`regresyon/p2_ornegi.lp`) koşuldu: yeni çekirdek **48/48**, z3 **48/48**, 82 kümenin hepsi aynı. P2b sırası aynı.
- **Pilottan bilinçli model farkları:** LoTE'ler OJEU'da sabit (T029; pilotta LOTL altındaydı); A09 ikiye bölündü; kanal/taşıma, zaman, politika, varyant ve 17 düğüm eklendi. Bunlar pilot örneğinde nötrlenince sonuçlar birebir.

## 7. Örnekleme dışa aktarımı (teknik kapı; §2F m.2)

- **ASP çalışması örnek seçmedi.** Çerçevenin tamamı: `ornekleme/cerceve.jsonl` (2.442 satır; SHA-256 `0a9b10d169a2898b97a6463fc481385a359744a981c392560ad0355f01942d87`).
  - Katmanlar (hedef × tür): G1 81/546, G2 117/1.071, G3 81/546; **G4 ve tümü boş** (birincilde UNSAT) → dolu katman 6.
  - Her satır: hücre, küme (PQ düğümleri + taşıyıcılar), ASP tahmini (değerlendirme kipinde hesaplandı), tanık (sahte artefaktlar), hedef yolunun alt çizgesi, R1–R7 düz Boole bayrak eşlemesi ve `.spthy` şablon önerisi.
- `ornekleme/kesif_2x2.jsonl` (8.442 satır; SHA-256 `c1e810c8c5f077790e9feb27ab6ddd8c0031ac3019a2d0c1503a4a2e5a3fb2ec`): 2×2'nin SAT hücrelerinde asgari + bir-eksik; her hücrede birincil kümelerin hükmü ("birincil-kume"). **`ca_baglama = ad, ayni_ad_klasik_ca = var` hücresinin 279 "birincil-kume" satırının hepsi falsified** (zorunlu ek örnek bu türden; şablon `R7_mh_x.spthy`, bayraklar CA_PQ, ALT_CA, NAME_BIND, ALT_SAME_NAME).
- Biçim: `ornekleme/SEMA.md`; özet: `ornekleme/disa_aktarim_ozeti.json`.

## 8. ÖN sonuçlar (bilimsel kapıda doğrulanacak)

> Bütün hükümler **ön**dür: ASP modelinin çıktısıdır. Bu sonuçların Tamarin örneklemesi (teknik kapı), soyutlama mutasyonları ve KAT'lar henüz yapılmadı. (2a)/(2b) adaylığı yalnız birincil yapılandırmadan ve 2.4 tasarımlarından sayılır (§2C madde 2, 2.5 "Sayım kuralı"); OAT ve keşifsel farklar kapıyı geçirmez.

| Hipotez | Ön kayıtlı ölçüt | ÖN sonuç | Dayanak |
|---|---|---|---|
| **H1** kanal ikamesi | (i) PQ taşımada en az bir çekilen artefakt için ikame; (ii) klasik taşımada hiçbiri; aktarılanda hiçbiri | **Destek (ön).** (i) WebPKI PQ iken (A13 ile) şu düğümler asgari kümeden düşebiliyor: a01 @G1–G3 (45/45 hücre), a02 @G1–G3 (54/63), durum belirtecinin içindeki a03/a04 @G3 (54/63), a08 @G3 (54/63), a06 @G1 (Type Metadata işlenirken, 54/63), e_jvi @G1 (54/63); a02 @G4 yalnız imzasız istek reddedilen varyantta (45/45). (ii) Nominal τ'da klasik taşımayla ikame yok. Aktarılan bağlamda (a03/a04/a07 @G1–G2, a10 @G2, a11/a12 @G4) ikame 0: yanlışlama koşulu 8 kanal varyantının hiçbirinde oluşmadı. Alt durumlar: çevrimdışı aktarılan durum listesinde a03/a04/a08 @G3 ikamesi 0; LOTL WebPKI'den çekildiğinde a01 ikamesi 36/45. **Sınırlar:** τ > W_güven(TLS) olursa klasik taşıma da korur (A5'te 42 `TASIMA_KORUR` hücresi; nominal ızgarada yok). k = 1'de çekilen artefakt tek kırmayla sahtelenemediği için ikame WebPKI klasikken de görünür (OAT k1) | `analiz/tablolar.md` (h1_md), `analiz/ozet.json` h1; H1 tasarımı 10.125 sorgu |
| **H2′** anahtar penceresi (Ö1) | Destek: ≥1 hedefte ≥2 τ rejimi arasında küme değişir ve pencereyle açıklanır. Yanlışlama: (i) sabit anahtar penceresinde belirteç ömrünün etkisi; (ii) pencerenin hiç etkisiz olması | **Destek (ön).** G3: durum anahtarı V2/V3'te a08 hızlı τ'da 21/21 SAT hücrede gerekli, orta ve yavaş τ'da 33/33 SAT hücrede gereksiz; V1'de her τ'da 21/21 gerekli. (i) 0/32 (A5: V1'de belirteç ömrü kümeyi değiştirmiyor); (ii) 66/180 V2/V3 grubunda küme τ ile değişiyor. İhraççı anahtarı V2/V3'te değişim yok, çünkü pencere (1 g + 30 g geçerlilik) nominal τ'ların hepsinden uzun. R6 ile sayısal eşleme 588/588 | `h2_md`, `r6_esleme.csv` |
| **H4** yayımlanmış sıranın sınırı | ≥1 hücrede S5 yetersiz ya da israflı (+ Tamarin örneği) | **Aday var (ön).** Birincil 36 hücre: yetersiz(düğüm) 12, yetersiz(beklenti) 6, israflı(diğer) 9, ikisi de sağlamaz 9 — Ö3'e göre sayılmaz (uzun ömürlü anahtar / beklenti / yol dışı). **Ö3 hücrelerinde 10 aday:** G4 WRPRC-faz1 imzasız-istek hücreleri (cl ve pq; Φ1/Φ2): S5'in kümesinde a11/a12 yok → yetersiz; cnf 1 g (G2) ve V2/V3 durum anahtarı (G3) orta/yavaş τ'da S5 a10/a08'i gereksiz göç ettiriyor → israflı(τ). Tamarin örneği henüz yok. Sınıflama bir yorumdur ve onay bekliyor (NOTLAR N8) | `sorgular/sonuc/h4_karsilastirma.json` |
| **H5** topla-sahtele | Sahtecilik iz ⇔ τ < kalan geçerlilik; tek kullanım izi engellemez | **Destek (ön).** Tek kullanım {yok, cüzdan, doğrulayıcı} hiçbir hücrede kümeyi değiştirmiyor; a10 cnf 30 g'de her τ'da, cnf 1 g'de yalnız hızlı τ'da gerekli. Yanlışlama sınaması (doğrulayıcıda tek kullanım, paylaşılan durum yok): etkisiz, H5 yanlışlanmadı. Sınır varyantı (pasif toplayıcı + küresel tek kullanım: W = iat 10 dk) orta/yavaş τ'da a10'u düşürür; bu varyant doğrulayıcılar arası paylaşılan durum gerektirdiği için ön kayıt §3.6'nın işlemsel okumasının dışındadır ve sınır koşulu olarak raporlanır | `h5_md`, `h5_tek_kullanim_md` |
| H0 (sağlık) | P0 + birlikte yaşamada iz; τ = ∞'da ∅ | τ = ∞'da "tümü" (Φ1, P0) ∅ ile sağlanıyor; S1'de (kırma yok) "tümü" Φ1–Φ3'te ∅ ile sağlanıyor; S2'de P0 + Φ1/Φ2 UNSAT (iz). Sistem çekirdeği Tamarin'in 44 hükmüyle aynı (§6) | `h.json` H0/H3 satırları |
| H3 (ön sinyal) | Birlikte yaşamada doğrulanmış beklenti olmadan G5 yok | G1+G5 hücreleri: Φ1/Φ2'de P0–P3, S2'de ve k = 1'de UNSAT; P4 SAT; S1'de hepsi ∅ ile SAT. Yalnız G1'e bakıldığında P3 k = 1'de SAT olur (OAT k1): P3'ün klasik kanalı tek başına bir sahtecilik açmaz, ama zamansız G5'i çiğner. G4'te M-b0 (imzasız istek) WRPRC beklentisi olmadan kapanmıyor (faz0 UNSAT, faz1 {a02, a11, a12}). Ö2 gereği M-a/M-b/M-b0 izleri bariz sayılır | `h.json` H3 satırları |

## 9. Sınırlılıklar

1. **Sınıf düzeyi soyutlama:** karar 17 düğümdedir; varlık düzeyi kısmi göç yalnız adlandırılmış hücrelerle (alternatif CA, ikinci çerçeve) temsil edilir. M4 bu yüzden yapısal bir vekildir.
2. **Zaman kararlı durumdur:** en kötü durumda anahtar pencerenin başında gözlenir; Q-day ile ilk pencere arasındaki geçiş yalnız `onbellek_ufku` ile modellenir. Başarı olasılığı < 1 (Häner) ve k'nin makine sayısıyla ilişkisi modellenmez.
3. **P0/P1/P2 bu soyutlamada eşdeğerdir** (7 sonuç grubundaki 10.305 hücre grubunun hepsinde aynı küme ailesi): soyma ve anahtar–alg bağlama farkları uygulama düzeyindedir (C3; NOTLAR N9).
4. **k-bütçesi:** birincil k sınırsızdır. k = 1'de çekilen artefakt iki kırma istediği için sonuçlar belirgin değişir (297 hücre; G3 ∅ ile sağlanır). H1'in "klasik taşımada ikame yok" koşulu k sınırsız varsayımına bağlıdır (NOTLAR N10).
5. **Taşıma tek düğüm:** WebPKI CA zinciri tek anahtara indirgenmiştir (penceresi TLS sunucu sertifikası, 1 y). CA/B Forum indirimi (47 g) yalnız duyarlılıkta; w_tls 47 g + τ ≥ 47 g birleşimi OAT'ta yok (NOTLAR N11).
6. **M-a…M-h yalnız kancadır;** M-f bileşen ablasyonu (A3), M-h'nin reddy/vicente varyantları ve `beklenti_kapsami` Adım 7'nin işidir. M-d (S3) özgün varsayılır; işletim maliyeti modelde yok.
7. **sdjwtvc_surum** biçimsel modelde etkisiz (OAT 0); §2D m.7'deki farklar C3 vektörlerine aittir.
8. **KAT'lar (isteğe bağlı) uygulanmadı:** `literatur\analiz\KAT-SPEC.md` taslakları Adım 6'ya bırakıldı; çekirdek (any-valid-path, beklenti, sürüm/zaman kancaları) KAT-1/KAT-3 örnek dosyalarını olgu olarak almaya hazırdır.
9. **Tek model yazarı:** ASP, z3 ve Jacobi aynı çalışmanın elinden çıktı; bağımsızlık yöntem ve kod düzeyindedir. Gerçek bağımsız doğrulama Tamarin örneklemesidir (NOTLAR N15).

## 10. Adım 5–7 için öneriler

- **Adım 5 (örnekleme):** çerçeve hazır; seçilecek örneklerin ve ad/var ek örneğinin bayrak eşlemesi satırlarda. G4 katmanı birincilde boş (NOTLAR N7): örnekleme `wrprc_faz1` ya da H1 (WebPKI PQ) tasarımlarından keşifsel etiketli bir G4 çerçevesi isterse aynı biçimde üretilebilir.
- **H4 yorumu (NOTLAR N8):** Φ3'teki 9 israflı(diğer) hücrenin (2a) sayılmaması onay bekliyor. (2a)'nın ek koşulu gereği 10 adayın her biri için Tamarin örneği gerekir.
- **R6:** sayısal sınıflar `pencere_sinifi/2` ile dışa aktarılıyor; Tamarin örneklerinde FAST/MEDIUM/SLOW bayrağı satırdaki `R6.tau_pencereden_uzun`'dan türetilmeli.
- **Adım 7:** M-h için baskınlık kancası (`baskin/2`) ve `ortak_ata` varsayımı hazır; `beklenti_kapsami = yol_sinifi` kabul edilen yolun `kenar/3` sınıfları üzerinden eklenebilir. M-e′'nin WebPKI'ye bağımlılığı (imzasız meta veri varyantı) ASP'de görünür: meta veri taşıyıcısı yalnız PQ taşıma ya da imzasız biçimin reddiyle güvenlidir.
- **H4 Tamarin örneği:** en güçlü aday `G2_cnf1g_orta` (israflı; a10) ve `G4_imzasiz_istek_cl_faz1_f1_p4` (yetersiz; a11/a12).

## 11. Durum
(son güncelleme: 25.09.2026, oturum 2)
- [x] İskelet, olgular, çekirdek, sürücü, z3 kodlaması
- [x] §2C uyarlaması (17 düğüm, birincil pencereler, A13, kenar-artefakt düğümleri, PQ-bağlı imzasız artefaktlar)
- [x] §2D uyarlaması (ca_baglama, ayni_ad_klasik_ca, pencere sınıfları, KEY_REUSE)
- [x] 52.693 sorgu; ASP–z3 %100; üç yönlü 7.000/7.000; Tamarin 44/44; P2 48/48
- [x] 2×2 + sağlık 6/6; R6 588/588; stratejiler; H4; A1; sıralar
- [x] Çerçeve dışa aktarımı + SHA-256 + katmanlar; SEMA.md
- [x] Rapor ve notlar (NOTLAR N1–N15; N1'deki `pq_birlikte` ifadesi düzeltildi)
- [x] Son denetim: rapordaki sayılar ve anlatısal iddialar sonuç dosyalarına karşı yeniden kontrol edildi. Düzeltmeler: önbellek karşılaştırması 225/225; T-atıfları matrisin artefakt atamalarına göre; S8, k1/k3, OAT açıklamaları, H1 alt durumları
- [ ] KAT'lar → Adım 6 (bilinçli erteleme)

## 12. Dosyalar

| Yol | İçerik |
|---|---|
| `olgular/*.lp` | artefaktlar, kenarlar, tasiyicilar, pencereler, hedefler, parametreler |
| `cekirdek.lp`, `secim.lp`, `sorgu.lp` | semantik; karar düğümleri ve domRec; sorgu kısıtı |
| `calistir.sh` | konteyner koşucusu (salt okunur bağlar: model/tamarin, referans, veri, 02-izlenebilirlik) |
| `sorgular/` | `ortak.py` (sürücü), `katalog.py`, `kos.py`, `analiz.py`, `stratejiler.py`, `h4.py`, `sira.py`, `rapor_sayilari.py`, `stratejiler_taslak.json`(+`.sha256`), `beklenti_2x2.json`(+`.sha256`), `sonuc/` |
| `z3/` | `yapi.py`, `z3_kodlama.py`, `py_degerlendirici.py`, `capraz_kontrol.py`, `uclu_rastgele.py`, `sonuc/` |
| `regresyon/` | `tamarin_esdegerlik.py`, `p2_regresyon.py`, `p2_ornegi.lp`, `tamarin_datalog/ornekler/`, `sonuc/` |
| `ornekleme/` | `disa_aktar.py`, `cerceve.jsonl`, `kesif_2x2.jsonl`, `SEMA.md`, `disa_aktarim_ozeti.json` |
| `kat/` | boş yer tutucu (KAT'lar Adım 6'ya ertelendi) |

**Yeniden üretim:** `./calistir.sh sorgular/kos.py` → `./calistir.sh z3/capraz_kontrol.py <gruplar>` → `z3/uclu_rastgele.py` → `regresyon/*.py` → `sorgular/analiz.py`, `stratejiler.py`, `h4.py`, `sira.py` → `ornekleme/disa_aktar.py` → `sorgular/rapor_sayilari.py`.
