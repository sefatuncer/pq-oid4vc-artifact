# KAT eşlemesi (Adım 6): üç ekosistem, tek çekirdek

> **Durum:** Hazırlık belgesi. Okuma kuralları ve eşleme, hiçbir KAT hücresi koşulmadan yazıldı ve SHA-256 ile sabitlendi (`SHA256SUMS`, "hazırlık" bölümü; ADIM06-RAPOR §1). Sonradan yapılan her değişiklik "sonuç görüldükten sonra" etiketiyle raporlanır.
> **Beklenen değerler:** yalnız `nsurum/kat_nsurum.tsv` (`ilk_ajan`; çapa 8, ÖK §2H.1). Bu belge beklenen değer içermez ve tanımlamaz.
> **Kaynaklar:** `literatur/analiz/KAT-SPEC.md` (şartname), `model/asp/cekirdek.lp` (tek çekirdek), ÖK §4.19, IS-PLANI Adım 6.

## 0. İlke

1. **Tek çekirdek.** Her KAT hücresi yalnız `model/asp/cekirdek.lp` ile bu klasördeki örnek dosyalarıyla koşulur.
   - `olgular/*.lp`, `secim.lp`, `sorgu.lp` yüklenmez.
   - KAT-SPEC'in önerdiği `kat_core.lp` ve `hon_decision.lp` **kullanılmaz** (IS-PLANI 6.1).
   - Çekirdeğin SHA-256'sı her koşucuda önce ve sonra alınır: `a32372a7…0b38` (commit `45cbd0f`).
2. **Örnek dosyasının içeriği.** Her KAT'ın taban dosyasında (`dnssec/kat1_dnssec.lp`, `x509/kat2_x509.lp`, `smime/kat3a_smime.lp`, `smime/kat3b_auth.lp`) iki şey vardır:
   - ekosistem olguları, çekirdeğin sözlüğüyle;
   - küçük ekosistem türetme kuralları: bir hücrenin sabitlerinden (`ornekler/*.lp`) o ekosistemin durumunu çıkarırlar.

   Çekirdek kuralı yoktur. Bu, Adım 3'teki `olgular/pencereler.lp`'nin (ekosistem kuralı) rolüyle aynıdır.
3. **Okuma kuralı.** Çekirdeğin çıktısı `ihlal(S,G)` atomlarıdır. Her KAT'ın hücre değerine dönüşümü aşağıdaki sabit kurallarla yapılır (§2.5, §3.4, §4.4, §4.5).
   - Karar ve sınıflama hücrelerinde okuma kuralı, çekirdeğin hesapladığı güvenlik yüklemini hücrenin kanıt durumuyla birleştirir.
   - Hangi parçanın çekirdekte hesaplandığı §5'te tek tabloda gösterilir.
4. **Yedek test yok.** Üç eşleme de kuruldu; S/MIME dahil (§4). Yedek bilinen-cevap testi seçilmedi (ÖK §2C madde 1).

### 0.1 Çekirdek semantiği (kısa)

| Kural | Anlam |
|---|---|
| K1 | Klasik imzacı anahtar, τ < W + pay iken kırılır; artefakt üretilebilir. |
| K2 (any-valid-path) | A'nın imzacısını tanıtan **herhangi** bir kabul edilen artefakt sahtelenebilirse A üretilebilir (sabit/çapa ise hayır). |
| K3/K4 | PQ imzacılı A'nın klasik alternatifi kabul ediliyorsa (`klasik_alt`), alternatif anahtar kırılabilir. Kimliği doğrulanmış bir beklenti (`tasi` + P4, taşıyıcı sahtelenemiyor) bunu kapatır. |
| M-f kancası | `mf_kapali(tazelik)` ve `mf_kapali(tekduzelik)` birlikteyse taşıyıcının eski sürümü geri oynatılır (`geri_alinir`) ve beklenti düşer. |
| Kanal | Çekilen artefakt yalnız taşıması sahtelenebiliyorsa ulaştırılır; aktarılan her zaman; sabitlenmiş hiçbir zaman. |
| G5 (zamansız) | Hedef yolundaki göç etmiş (PQ) varlığın klasik alternatifi açık ve kimliği doğrulanmış beklentisi yoksa ihlal; kırılma gerekmez. |

### 0.2 Ortak sözlük: KAT-SPEC §1.1 → çekirdek

| KAT-SPEC (`kat_core.lp`) | Çekirdek (`cekirdek.lp` girdisi) |
|---|---|
| `key_class(K,cl)` | imzacısı klasik: `not pq(A)` |
| `key_class(K,pq)`, `comp` | `pq(A)` (composite'in PQ bileşeni kırılmaz; bu yüzden PQ gibi) |
| aynı artefaktta klasik ve PQ `slot` | `pq(A)` + `klasik_alt(A)` (∃-yol: herhangi biri yeter) |
| `intro`/`validates` | `kenar(E,X,I)` (OR-kenarı) |
| `anchor(K)`, `anchored(K,X)` | `sabit(X)` |
| `exposure`, `qday`, `tau`, `now` | `pencere(A, now − max(T0,qday))`, `p_sayi(tau,τ)`, `saat_payi = 0`. Çekirdek τ < W; KAT-SPEC τ ≤ W. Eşitlik sınırında hücre yok. |
| `signal_*` + `pol=required` | `tasi(C,X)` + `p(politika,p4)`; C imzalı kaynak (M-f sınıfı) |
| `local_req` (P2) | `tasi(yerel_politika,X)`, taşıyıcı sabitlenmiş (M-d sınıfı) |
| `allpresent` / `enforce_if_present` (P1) | öz-sinyal taşıyıcısı: PQ kanıtının **varlığı** beklenti taşır. Gücü, varlığı koruyan imzanın gücüdür: DNS RRSIG kümesi hiçbir imzayla korunmaz (kimliksiz), Catalyst uzantısı ise klasik temel imzayla korunur. |
| `continuity` (P3) | yerel süreklilik durumu (M-g sınıfı; sabitlenmiş); yalnız ilk temastan sonra vardır |
| `version`, `valid_v`, `seen`, `monotone` | ekosistem türetmesi: 'now' anında kabul edilen sürümler → `pq`/`klasik_alt`. Beklenti taşıyıcısında eski sürüm → `mf_kapali` → `geri_alinir`. |
| `attack` | `ihlal(tum,g1)` (S2, k sınırsız) |

## 1. Genel geçme ölçütü ve nasıl hesaplandığı (ÖK §4.19, IS-PLANI 6.6, KAT-SPEC §0)

Her KAT için dört koşul da sağlanmalı; "belirsiz" tek bir hücre bile o KAT'ı düşürür:
1. **ASP hücreleri %100.** `nsurum` anahtarlarının hepsi (141 anahtarın ASP kısmı) okuma kuralıyla beklenen değere eşit.
2. **Tamarin hücreleri %100.** `nsurum`'daki Tamarin anahtarları beklenen değerde; her koşuda `executable` verified; iyi biçimlilik uyarısı 0.
3. **ASP–Tamarin uyumu %100** ortak hücrelerde. Karşılık tablosu KAT başına §2.5, §3.5, §4.6'da.
4. **KAT-SPEC §6 mutasyonları %100.** 12 mutasyonun her biri, tanımlı olduğu her motorda (ASP ve/veya Tamarin) listelenen hücrelerden en az birini belirtilen yöne döndürmeli.

**Ek maddeler (kapı sayımına ayrıca raporlanır, `nsurum`'da yok):**
- KAT-2 Tamarin duyarlılık lemmaları (`x509/ek_tamarin.tsv`, KAT-SPEC §3(d));
- KAT-3a `kat3a_fail` boş ve `model_gap` yalnız o8'de (KAT-SPEC §4(d) "Geçme (KAT-3a)");
- KAT-3b Tamarin, pilotun aslıyla (`smime/ek_tamarin.tsv`; §4.5).

**Hesaplama:** her klasörün `degerlendir.py`'si (koşu yapmaz; yalnız `sonuc/` çıktılarını okur) → `sonuc/KAT_OZET.{json,md}`. `SONUC.md` bu üç özetin birleşimidir.

Kapıya sayılıp sayılmayacakları yürütücünün kararıdır.

## 2. KAT-1 DNSSEC (`dnssec/`)

**Yeniden üretilen sonuç** (RFC 6840 §5.11 + §6.2 + Ek C.2; RFC 6781 §4.1.4, §4.3.4):
- "Herhangi bir tek geçerli yol" doğrulayıcısında güvenliği en zayıf işaretli algoritma belirler.
- Algoritma geçişi ve yeniden oynatma bu pencereyi uzatır.
- Bütünlük testi, PQ imzalı üst sinyal ve tekdüzelik pencereyi kapatır.

### 2.1 Artefaktlar, kenarlar, kanal
- **`ds`:** üst bölge anahtarıyla imzalı; üst anahtar güven çapası → `sabit(ds)`. `pq(ds)` ⇔ üst anahtar PQ (`kat_ust_sinif`).
- **`dnskey`:** imzacısı DS'nin gösterdiği KSK → `kenar(e_ds_ksk, dnskey, ds)`.
- **`a_rr`:** hedef; imzacısı DNSKEY RRset'teki bir anahtar → `kenar(e_dnskey_anahtar, a_rr, dnskey)`.
- **Kanal:** üçü de ÇEKİLEN. DNS taşımasının kimliği doğrulanmaz (`dns_yaniti`: imzasız, kimliksiz), bu yüzden taşıma her zaman sahtelenebilir. KAT-SPEC §1.1'in H1 sağlık notu: DNS'te kanal ikamesi yok.
- **RFC 6840 §6.2 kenar semantiği:** "any DNSKEY in the zone's signed DNSKEY RRset may be used to authenticate any RRset in the zone". A RRset'in PQ yolu ve klasik alternatifi, kabul edilen DNSKEY sürümünde o sınıftan **herhangi bir** anahtarın listeli olmasından türetilir (`listeli(dnskey,C)`). Anahtar, artefakt türüne bağlanmaz (V2).
- KAT-SPEC'in "kök → TLD → bölge" zinciri, güven çapası olan üst bölge anahtarına indirgenmiştir (KAT-SPEC §2(b) ile aynı).

### 2.2 Zaman ve sürüm
Sürüm tablosu KAT-SPEC §2(b) ile aynı sayılardır (DS v1/v2/v12; DNSKEY v3/v5; `goruldu` = `seen`). Ekosistem türetmesi:
- `gecerli(I,V)`: imza 'now' anında geçerli.
- `kabul_surum(I,V)`: geçerli ve tekdüze doğrulayıcı daha yenisini görmediyse.

Çekirdeğe iki yolla girer:
1. **Yapısal yol (sürümler):**
   - `pq(dnskey)` ⇔ kabul edilen bir DS sürümü PQ KSK'yı listeliyor.
   - `klasik_alt(dnskey)` ⇔ klasik KSK'yı listeleyen bir DS sürümü de kabul ediliyor, **ya da** eski klasik KSK ek güven çapası (Ek C.2).
   - `a_rr` için aynısı, DNSKEY sürümleriyle.
   - Eski DNSKEY v3'ün yeniden oynatılması (K1-07) ve tekdüzeliğin bunu kesmesi (K1-08) böyle girer.
2. **Beklenti taşıyıcısı (DS):**
   - PQ'yu işaretlemeyen eski bir DS sürümünün imzası 'now' anında hâlâ geçerliyse `mf_kapali(tazelik)`.
   - Doğrulayıcı tekdüze değilse `mf_kapali(tekduzelik)`.
   - Çekirdeğin M-f kancası ikisi birlikteyken DS'nin beklentisini geri alır. K1-05 (yeniden oynatma) ile K1-06 (tekdüzelik) böyle ayrışır.

**Zaman:**
- `pencere(A) = now − max(T0, qday)`, T0 = 0 (KAT-SPEC §2(d), durağan anahtarlar); `saat_payi = 0`; τ = `kat_tau`.
- Q-day'in 'now'dan sonra olduğu K1-13'te pencere negatiftir ve çekirdek hiçbir anahtarı kırmaz.

### 2.3 Politika

| KAT-SPEC `pol` | Çekirdek |
|---|---|
| `anyvalid` (RFC 6840 varsayılanı) | P0; beklenti yok |
| `allpresent` | P4 + öz-sinyal taşıyıcıları (`pqvar_dnskey`, `pqvar_a_rr`): imzasız, **kimliksiz**. PQ RRSIG'inin varlığı hiçbir imzayla korunmaz; saldırgan soyar (RFC 9955 §6.2). |
| `required` (bütünlük testi, §5.11 MAY) | P4 + `tasi(ds, dnskey)`, `tasi(ds, a_rr)`. Güncel kabul edilen DS PQ algoritmasını işaretliyorsa (M-f sınıfı: imzalı üst kaynak). DS yalnız klasik işaretliyorsa bütünlük testi yalnız klasiği ister: PQ beklentisi yok (K1-02). |

K1-12'de üst anahtar klasiktir; DS sahtelenebilir, bu yüzden beklenti düşer (V3: "uygulanan sinyal kanalı kadar güçlü").

### 2.4 Tamarin (`dnssec/KAT1_DNSSEC.spthy`)
KAT-SPEC §2(c) taslağı; anlam aynı. Değişiklikler dosya başlığında:
- `#ifdef not`;
- NO_QDAY'de Break kuralları da kalkar;
- NotEq yalnız kullanıldığı bayrakta;
- §6 mutasyonları bütün kural düzeyinde (`MUT_NO_DS_SIG`, `MUT_NO_DS_KSK_MATCH`).

Hazırlıkta 16 benzersiz bayrak kümesinin 16'sı iyi biçimli, uyarı 0 (`dnssec/iyi_bicim/ozet.tsv`; `--prove` yok).

**Sonuç görüldükten sonra (26.09.2026, yürütücü kararı):**
- İlk koşumda K1-11 Tamarin'de falsified çıktı. Taslak bütünlük testini yalnız A RRset adımında uyguluyordu; RFC 6840 §5.11'in "all algorithms signaled in the DS RRset" kuralı DNSKEY adımında yoktu.
- Düzeltilmiş kapı modeli `dnssec/KAT1_DNSSEC_v2.spthy`: `COMPLETENESS`'te bütünlük DNSKEY adımına da uygulanır; mutasyon alternatifleri buna göre tanımlıdır.
- Bu belgedeki eşleme ve okuma kuralları DEĞİŞMEDİ. Ayrıntı: ADIM06-RAPOR §5, §8.

### 2.5 Okuma kuralı ve ASP–Tamarin karşılığı
- **ASP:** SALDIRI ⇔ `ihlal(tum,g1)`; aksi YOK.
- **Tamarin:** `a_rrset_authentic`.
- **Ortak hücreler:** K1-01…K1-15 (15); SALDIRI ↔ falsified, YOK ↔ verified.

### 2.6 Mutasyonlar (KAT-SPEC §6, KAT-1 satırları; `dnssec/mutasyonlar.tsv`)

| Mutasyon | ASP (örnek dosyası değişkesi; çekirdek aynı) | Tamarin | Beklenen dönüş |
|---|---|---|---|
| MUT01 COMPLETENESS → ANYVALID | `kat_politika(anyvalid)` | bayrak değişimi | K1-04, K1-11 → SALDIRI/falsified |
| MUT02 DS imza denetimi silindi | `ds` imzasız sayılır (`kat_mutasyon(ds_imza_denetimi_yok)`) | `MUT_NO_DS_SIG` | K1-04 → SALDIRI/falsified |
| MUT03 DS–KSK eşleşmesi silindi | `dnskey` herhangi bir KSK ile kabul → imzasız sayılır | `MUT_NO_DS_KSK_MATCH` | K1-04 → SALDIRI/falsified |
| MUT04 tekdüzelik kaldırıldı | `kat_tekduze(0)` | K1-06: `OLD_DS_REPLAY` eklenir (KAT-SPEC notu: K1-06'da tekdüzelik = eski DS'nin verilmemesi); K1-08: `MONOTONE` çıkarılır | K1-06, K1-08 → SALDIRI/falsified |
| MUT05 eski sürüm geçerliliği ∞ | `kat_mutasyon(eski_surum_suresiz)` | K1-09 + `DK3_USABLE` | K1-09 → SALDIRI/falsified |

### 2.7 Sınırlar
- Sürüm imzalarının 'now' anında geçerliliği ve tekdüzeliğin eski sürümü dışlaması, ekosistem türetme kurallarıyla (taban dosyası) hesaplanır. Çekirdek bu durumun sonuçlarını hesaplar: K1/K2/K4, beklenti, M-f geri alma, zaman.
- Çekirdeğin kendi zaman modeli kararlı durumdur (τ < W). 'now' anı pencereye (W = now − max(T0, qday)) ve kabul edilen sürümlere yansıtılır.

## 3. KAT-2 X.509 hibrit (`x509/`)

**Yeniden üretilen sonuç** (ÖK §4.19): "PQ bileşeni gerekli kılınmayan politikada PQ kanıtının bozulması kararı değiştirmez" (Kim §VI-A: 27/27; Lee §4.4: "no stack can mandate the binding"). Composite yapısal bağlar (Lee §4.3). Bağlı PQ sertifikasının durumu yalnız politika kapsama alırsa karara girer (Kim Tablo V). P0–P3 M1 altında (Kim Tablo VI).

### 3.1 Model
- **`ee`:** hedef; CA anahtarları çapa → `sabit(ee)`; aktarılan.
- **Hibrit ihraç:** `pq(ee)`.
- **Ayrılabilir şemalarda (Catalyst, Chameleon, Related):** temel klasik imza varsayılan yolda tek başına kabul edilir → `klasik_alt(ee)`.
- **Composite:** tek imzadır. Klasik yol yalnız birlikte yaşamada (aynı CA'nın düz klasik sertifikası da kabul: `coexist_cl`) vardır.

### 3.2 Doğrulayıcı politikası → beklenti taşıyıcısı (çekirdeğin mekanizma sınıfları)

| `vb` | Çekirdek |
|---|---|
| `ignore`, `parse_no_enforce`, `legacy_oid` | P0 (PQ kanıtı karara girmez) |
| `enforce_if_present` (P1, "varsa denetle") | öz-sinyal `pq_kanit_varligi`: yalnız PQ kanıtı **mevcutsa** (geçerli ya da geçersiz) vardır. Varlığı TBS içindeki uzantıyla temel **klasik** imzaya bağlıdır: taşıyıcı klasik imzalı. CRQC klasik anahtarı kırarsa saldırgan soyar (Lee §4.4). |
| `require` (P2, yerel "require-PQC") | `yerel_politika`: sabitlenmiş (M-d); hiçbir senaryoda sahtelenmez |
| `require_tl` (K2b-04/05) | imzalı TL (M-f); TL anahtarı klasik ya da PQ |
| `continuity` (P3) | `sureklilik_durumu`: sabitlenmiş yerel durum; yalnız `seen_hybrid = 1` iken vardır. Kim: "P3 presupposes an external continuity state" |

### 3.3 İki kip
- **`saldiri` (K2b; Kim M2 = CRQC):** senaryo `tum`.
- **`karar` (K2a/K2c/K2d; Kim M1 = CRQC yok, dürüst nesne):** senaryo `bos` (S1).

### 3.4 Karar okuma kuralı (SABİT; `x509/kos.py: karar_oku`)

Çekirdek, doğrulayıcının **bu nesne için PQ kanıtını gerekli kılıp kılmadığını** hesaplar:
- G5 := `ihlal(bos,g5)`: göç etmiş (hibrit ihraç edilmiş) varlığın klasik kanıtı, kimliği doğrulanmış bir PQ beklentisi olmadan kabul ediliyor.
- Bu, Kim'in "classical acceptance" (sessiz terfi) kavramının ve Tamarin `no_silent_promotion`'ın karşılığıdır.

| Çekirdek | Nesnenin kanıt durumu (hücre girdisi) | Etiket |
|---|---|---|
| G5 | herhangi biri | `accept_classical` |
| G5 değil, Related | bağlı PQ sertifikası geçerli / `unknown` / diğer | `accept_hybrid` / `indeterminate` / `reject` |
| G5 değil, diğer | PQ kanıtı doğrulayıcının gözünde geçerli ve algoritma tanınıyor / değil | `accept_hybrid` / `reject` |

- "Doğrulayıcının gözünde geçerli": `kat_pqev = valid`. MUT07'de composite'in PQ bileşeni denetlenmediği için geçerli görülür.
- "Tanınıyor": `vb ≠ legacy_oid` (Kim Tablo IV "loud-fail").

**Neden bu okuma yayımlanmış iddiayı sınar:** İddianın özü, kararın PQ kanıtına **duyarlılığıdır**. Bu duyarlılık tamamen G5'tedir:
- G5 doğruysa etiket kanıt durumundan bağımsızdır: `ignore` / `parse_no_enforce` hücrelerinde valid ve invalid aynı çıkar (Kim 27/27).
- G5 yanlışsa etiket kanıta bağlıdır.

G5'i çekirdek hesaplar. Okuma kuralının kanıt durumunu kullanan kısmı (geçerli → hybrid, değil → reject), nesnenin kendi imzasının geçerliliğidir; politika mantığı değildir.

### 3.5 ASP–Tamarin karşılığı
- **K2b** (`cert_authentic`; K2b-01/02/03/06/07): SALDIRI ↔ falsified.
- **K2d** (`no_silent_promotion`; K2d-01/02/03): `accept_classical` ↔ falsified, `reject` ↔ verified. G5 ile `no_silent_promotion` aynı kavramdır.
- **K2b-04/05/08, K2a, K2c:** ASP-yalnız (KAT-SPEC).

### 3.6 Mutasyonlar (`x509/mutasyonlar.tsv`)

| Mutasyon | ASP | Tamarin | Beklenen |
|---|---|---|---|
| MUT06 V_REQUIRE → V_ENFORCE_IF_PRESENT | K2b-03'te `vb = enforce_if_present` | bayrak değişimi | K2b-03 → SALDIRI/falsified |
| MUT07 composite PQ bileşen denetimi silindi | `comp_pq_denetimi_yok`: composite'in güvencesi klasik bileşene iner (`pq(ee)` yok); PQ kanıtı geçerli görülür | `MUT_COMP_NO_PQ` | K2b-06 → SALDIRI/falsified; K2a-16 → accept |
| MUT08 P2'de bağlı sertifika durum denetimi silindi | Related'da `require` bağlı PQ sertifikasını kapsama almaz (taşıyıcı yok; V9) | – | KAT-2c P2 sütunu → `accept_classical` |
| MUT09 `hybrid_seen` yok sayıldı | süreklilik durumu taşıyıcısı yok | – | K2d-04 → `accept_classical` |

### 3.7 Sınırlar
- Karar etiketleri doğrulayıcının sınıflamasıdır; çekirdek sınıflama yapmaz. Çekirdek, sınıflamanın PQ'ya duyarlı kısmını (G5) hesaplar.
- Composite algoritma tanıma (`legacy_oid`) ve MUT07'deki "geçerli görülme" okuma kuralındadır.
- K2d'nin kanıt durumu `absent`tır (legacy sertifika; M1; kör çalışmanın B8 okuması).

## 4. KAT-3 S/MIME (`smime/`): CEK tabanlı yapı eşlemesi ve gerekçesi

### 4.1 Sorun
Das ve Chattopadhyay (ePrint 2026/1374) şunu söyler: "every valid path to the CEK must satisfy the active migration policy" ve "the confidentiality level of ED is bounded by the weakest valid recipient path protecting K". Bu bir **gizlilik** sonucudur. Çekirdek ise **kimlik doğrulama** (sahtecilik) üzerine kuruludur: gizlilik, şifre çözme ya da anahtar kurtarma semantiği yoktur. ÖK §4.19 bu durumda eşlemenin "yol tabanlı politika sağlama" yapı eşlemesi olarak belgelenmesini ister.

### 4.2 Yapı eşlemesi (ikilik)

| Das (CMS gizliliği) | Çekirdek (kimlik doğrulama) | Neden aynı yapı |
|---|---|---|
| CEK K (tek, paylaşılan) | hedef artefakt `cek` | Korunan tek nesne |
| Alıcı yapısı RI_i: K'ya giden bir kurtarma yolu | `yol(i)` artefaktı ve `kenar(e(i), cek, yol(i))` | Her yol bağımsız bir erişim yolu |
| Saldırgan herhangi bir geçerli RI_j'den K'yı kurtarırsa M açığa çıkar (Önerme 1) | K2 (any-valid-path): kabul edilen HERHANGİ bir tanıtıcı sahtelenebilirse hedef çiğnenir | İkisi de ∃-yol zayıflığı / ∀-yol güvencesi; güvence en zayıf yolunkidir |
| V_i(t) = 1 (alıcı sertifikası geçerli) | kenar var (`ri(…, gecerli)`); geçersiz sertifikalı yol kenarsız | Das'ın kuralı yazıldığı gibi |
| Etkin göç politikası A_t (strict: {PQC}; transitional: {PQC, approved hybrid}) | **sonda:** A_t dışındaki sınıfların yolları kırılabilir (klasik), içindekiler PQ | Politika sağlama = izin dışı her anahtar kırıkken saldırı yokluğu |
| Evrensel kabul (Denk. 8): ∀ geçerli yol, χ_i ∈ A_t | çekirdekte `ihlal` yok | ∀-yol ⇔ hiçbir yol sahtelenemez |
| "Unknown mechanisms fail closed" | unknown hiçbir A_t'de yok (kırılabilir) | kapalı başarısızlık = izin dışı |
| malformed → invalid | invalid sınıfı hiçbir A_t'de yok | |
| Onaylı hibrit KEM (iki bileşen gerekir) | transitional'da PQ sayılır; strict'te izin dışı | Das Aşama 4 |

**Korunan:** yol sayımının tamlığı ve ∀-niceleyici (V12); "geçerli yol" ile "sınıf" ayrımı ve bilinmeyenin kapalı başarısızlığı (V13); en zayıf yol ilkesi.

**Korunmayan (açıkça):**
- Çekirdek CEK'in "kurtarılmasını" değil "sahtelenebilirliğini" hesaplar. Eşleme bir güvenlik semantiği değil, **yapı** eşlemesidir; politika sağlamanın yol yapısını test eder.
- Das'ın Tablo 1 sınıf etiketleri bir raporlama işlevidir. Etiketler sonda sonuçlarından sabit öncelikle okunur (§4.4).
- `model_gap` (o8): CRQC'li saldırgan geçersiz sertifikalı klasik yoldan gizlilikte CEK'i yine kurtarır. Das'ın kuralı bunu kapsam dışı bırakır. Ayrı sondayla okuma notu olarak raporlanır, yazarlara atfedilmez (KAT-SPEC §7.4).

### 4.3 KAT-3a sondaları (`smime/kat3a_smime.lp`)

| Sonda | Kırılabilir (izin dışı) sınıflar | Anlamı |
|---|---|---|
| `kati` | hybrid, classical, unknown, invalid | strict-PQC politikası (A = {pqc}) |
| `gecis` | classical, unknown, invalid | transitional-hybrid (A = {pqc, hybrid}) |
| `klasik` | classical | geçerli klasik yol var mı |
| `bilinmeyen` | unknown | geçerli bilinmeyen yol var mı |
| `gecersiz` | invalid | bozuk yapı var mı |
| `pq_hibrit` | pqc, hybrid | geçerli PQ ya da hibrit yol var mı |
| `tum_klasik_yol` | classical; geçersiz sertifikalı yollar da sayılır | model farkı (o8) |

- Zaman: CRQC var (now 100, qday 0, τ 10).
- MUT11 ("fail-closed: unknown izinli"): politika sondalarında unknown kırılabilir kümeden çıkarılır.

### 4.4 KAT-3a okuma kuralı (SABİT; `smime/kos.py: etiket_3a`)
E(sonda) := `ihlal(tum,g1)`.
- `accept_strict = 1 − E(kati)`, `accept_transitional = 1 − E(gecis)`.
- `out` (Das Aşama 5 önceliği: malformed → invalid; unsafe mixed-mode daha zayıf belirsizlik etiketlerinden önce; unknown fail-closed):
  1. E(gecersiz) → `invalid`;
  2. değilse E(klasik) ∧ E(pq_hibrit) → `unsafe_mixed`;
  3. değilse E(bilinmeyen) → `unknown`;
  4. değilse E(klasik) → `classical_only`;
  5. değilse ¬E(kati) → `pqc_protected`;
  6. değilse ¬E(gecis) → `hybrid_protected`.
- Ek: `kat3a_fail = accept_strict ∧ E(klasik)`; `model_gap = accept_strict ∧ E(tum_klasik_yol)`.

### 4.5 KAT-3b kimlik doğrulama ikiliği (`smime/kat3b_auth.lp`)
- **Model:**
  - TL: çapa imzalı (`sabit`), ağdan ÇEKİLEN, taşıma kimliksiz; ihraççının anahtarlarını tanıtır (`kenar(e_tl_ihracci, cred, tl)`).
  - Kimlik bilgisi: PQ imzalı; birlikte yaşamada klasik alternatifi var.
  - TL girdisi "pq_required" taşıyabilir (M-f); pol = required.
- **Zaman kipleri:**
  - dinamik `qday0`;
  - dinamik `qday200` (CRQC yok);
  - **statik** (zaman kısıtı kaldırılmış: now büyük, τ = 0; bütün klasik anahtarlar kırık).
- **V14 (statik ≡ dinamik):** Tek çekirdekli tasarımda statik politika denetimi, zaman kısıtı kaldırılmış aynı saldırı aramasıdır. `violation(qday=0) = attack(qday=0)` yapı gereğidir; bu bir tasarım özelliğidir, bağımsız bir sınama değildir. `qday=200`'deki ayrışma yalnız çekirdeğin zaman kuralından gelir (`zaman_uygun` yok).
- **Okuma:** dinamik SALDIRI ⇔ E; statik violation = 1 ⇔ E.
- **Pilot eşleri:** KAT-SPEC §4(d) ve `arac/test/calistir.sh` bayrakları (V1 bayraksız … V6 `NO_COEXIST`).

**Pilot modelin iyi biçimliliği (hazırlık bulgusu; koşumdan ÖNCE karara bağlandı).**
- **Sorun:** KAT-SPEC §4(c) pilotun (`referans/pilot/p1/weakest_link.spthy`, `b079cbbb…bd47`) "değiştirilmeden" koşulmasını ister. Ama pilot altı yapılandırmanın altısında Tamarin 1.12 iyi biçimlilik denetiminden geçmez: "Fact multiplicity issues". `Qday` adı hem eylem (`--[ Qday() ]->`) hem kalıcı olgu (`!Qday()`) olarak kullanılmış.
- **Neden lemma hükmünü etkileyemez:** Eylem `Qday()` hiçbir lemmada ya da kısıtta geçmez; lemmalar yalnız `Issued` ve `Accept` kullanır.
- **Çatışma:** projenin kanıt kuralı "iyi biçimlilik uyarısı 0" (ÖK §2H.2; Tamarin çalışmasının 24.09 kuralı), KAT-SPEC'in lafzı "değiştirilmeden".
- **Karar:**
  - Kapı hücreleri `smime/weakest_link_wf.spthy` ile koşulur (`90aa0a4d…a883`). Pilottan tek farkı 24. satırda eylemin adıdır: `Qday()` → `QdayOlayi()` (`diff`: 1 satır, 1 sözcük).
  - Pilotun aslı da aynı altı yapılandırmayla koşulur ve `smime/ek_tamarin.tsv` ile ayrıca raporlanır (kapı hücresi değil).
  - İki sonuç ayrışırsa bu bir bulgu olarak raporlanır; hangisinin sayılacağı yürütücünün kararıdır.
- **Sonuç ve karar (26.09.2026):** İki model 6/6 aynı hükmü ve aynı adım sayısını verdi. Yürütücü kararı: uyarılı model geçersizdir; düzeltmeli kopya kapı hücresidir.

### 4.6 ASP–Tamarin karşılığı
- **KAT-3b:** `attack(qday=0)` ↔ `claims_unforgeability` (V1–V6; iyi biçimli pilot kopyası, §4.5); SALDIRI ↔ falsified.
- **KAT-3a:** Tamarin `cek_secrecy` bayrakları KAT-3a vektörlerinin eşleridir:
  - MIXED ↔ o4 (mlkem + rsa);
  - PQ_ONLY ↔ o1;
  - HYBRID_KEM ↔ o5 (onaylı hibrit).

  ASP değeri, Tamarin'in tehdit modeliyle aynı sondadan okunur: `klasik` (yalnız klasik anahtar kırılır). E ↔ falsified. KAT-SPEC bu karşılığı adıyla vermiyor; tanım bu belgeye aittir (kapıdan önce sabitlendi).

### 4.7 Mutasyonlar (`smime/mutasyonlar.tsv`)

| Mutasyon | Motor | Beklenen |
|---|---|---|
| MUT10 onaylı hibritte ikinci bileşen silindi (`h(<ssc,ssq>) → h(ssc)`) | Tamarin `MUT_HYBRID_ONE` | HYBRID_KEM `cek_secrecy` → falsified |
| MUT11 fail-closed: unknown izinli | ASP (o7, o10; kati ve gecis sondaları) | accept → 1 |
| MUT12 TL beklenti denetimi silindi | ASP (V4, qday0) | SALDIRI |

## 5. Hangi parça nerede hesaplanır (kapsam denetimi; IS-PLANI 6.10 madde 2)

| KAT / hücre ailesi | Çekirdek hesaplar | Eşleme/örnek dosyası sabitler | Okuma kuralı ekler |
|---|---|---|---|
| KAT-1 (15) | kırılma (zaman), any-valid-path, klasik alternatif, beklenti ve sahteliği, M-f geri alma, kanal | sürüm geçerliliği 'now'da, tekdüzeliğin eski sürümü dışlaması | yok (SALDIRI ⇔ ihlal) |
| KAT-2b (8) | aynı | politika → taşıyıcı sınıfı | yok |
| KAT-2a/2c/2d (32) | G5: PQ kanıtı gerekli mi (politika, öz-sinyal, yerel/süreklilik durumu) | politika → taşıyıcı sınıfı; kanıt durumu | kanıt geçerliliği → hybrid / reject / indeterminate |
| KAT-3a (36 değer) | ∀ geçerli yol politikayı sağlıyor mu; sınıf varlıkları (sondalar) | vektörler, sınıflama, politika → kırılabilir sınıflar | Tablo 1 önceliği |
| KAT-3b (18) | saldırı (zamanlı), statik = zamansız saldırı | pilot yapılandırmaları | yok |

## 6. Değiştirilmezlik
- Bu belge, taban ve örnek dosyaları, hücre ve mutasyon tabloları, Tamarin modelleri ve koşucular ilk koşumdan önce `SHA256SUMS`'ta ("hazırlık" bölümü) sabitlendi.
- Koşumdan sonra bunlardan birine dokunulursa fark, gerekçe ve etkisi ADIM06-RAPOR'a "sonuç görüldükten sonra" etiketiyle yazılır. Beklenen değerlere (`nsurum/`) hiç dokunulmaz.
