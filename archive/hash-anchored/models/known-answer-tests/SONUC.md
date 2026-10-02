# Adım 6: Bilinen-cevap testleri (KAT), SONUÇ

- **Tarih:** 26.09.2026 · **Çalışma:** asp (Adım 6) · **Çapa 8:** commit `2d16592` (ÖK v0.9 §2H)
- **İki koşum birlikte sunulur (yürütücü kararı 26.09.2026):**
  - **ilk koşum:** commit `e4c1090`; KAT-1 KALDI kaydı korunur;
  - **düzeltme sonrası koşum:** yalnız KAT-1 Tamarin; `dnssec/KAT1_DNSSEC_v2.spthy`, "sonuç görüldükten sonra düzeltme"; sonuçlar `dnssec/sonuc_v2/`.

  Bilimsel kapıda V-d'yi bağımsız gözden geçirme değerlendirecek.
- **Beklenen değerler:** `nsurum/kat_nsurum.tsv` (`3609f793…2aec`), `ilk_ajan` sütunu (tek kaynak; K2d Tamarin = `no_silent_promotion`). Dokunulmadı.
- **Tek çekirdek:** `models/asp/cekirdek.lp`. Özeti üç ASP koşucusunda önce = sonra = `a32372a7…0b38` (commit `45cbd0f`). `kat_core.lp` ve `hon_decision.lp` kullanılmadı.
  - ASP yalnız ilk koşumda koşuldu; düzeltme ASP'ye ve çekirdeğe dokunmaz.
- **Hazırlık kimliği (ilk koşumdan önce):** `2d23e35b…024b`, 2026-09-26T11:07:00Z (`dnssec/HAZIRLIK_SHA256SUMS`). Eşleme ve okuma kuralları: `ESLEME.md`.
- **Araçlar:**
  - clingo 5.8.2: `pq-a02-solver:1.0` (`sha256:02c637eb…`);
  - Tamarin 1.12.0: `pq-a02-tamarin:1.12.0` (`sha256:59b648d6…`).
  - Konteyner öneki `pq-a06-`. Tamarin sınırları: 12 GB, 600 s.
- **Koşum ölçüleri:**
  - İlk koşum: bütün Tamarin satırları (42 kapı ve mutasyon + 9 ek) merdivenin ilk basamağında kapandı. En uzun lemma 2,66 s, bellek tepesi en çok 148,2 MiB.
  - Düzeltme sonrası: 22 satır, hepsi ilk basamakta. En uzun 3,33 s, en çok 139,1 MiB.
  - En uzun ASP hücresi 3,5 ms.

## Özet (V-d; ÖK §4.19, IS-PLANI 6.6)

| KAT | Koşum | ASP hücreleri | Tamarin hücreleri | ASP–Tamarin | Mutasyonlar (KAT-SPEC §6) | executable / iyi biçimlilik | V-d |
|---|---|---|---|---|---|---|---|
| KAT-1 DNSSEC | ilk koşum (v1) | 15/15 | **14/15** | **14/15** | 5/5 | hepsi verified / uyarı 0 | **KALDI** |
| KAT-1 DNSSEC | düzeltme sonrası (v2) | 15/15 (ilk koşum) | 15/15 | 15/15 | 5/5 | hepsi verified / uyarı 0 | **GEÇTİ** |
| KAT-2 X.509 hibrit | ilk koşum | 40/40 | 8/8 | 8/8 | 4/4 | hepsi verified / uyarı 0 | GEÇTİ |
| KAT-3 S/MIME | ilk koşum | 54/54 | 9/9 | 9/9 | 3/3 | hepsi verified / uyarı 0 | GEÇTİ |

**V-d:**
- ilk koşum: **2/3** (KAT-1 KALDI);
- düzeltme sonrası: **3/3**.

**Ayrıntı:**
- `nsurum` 141 anahtar. İlk koşumda 140'ı beklenen değerde; tek uyumsuzluk K1-11, Tamarin `a_rrset_authentic`. Düzeltme sonrası 141/141.
- ASP'nin 109 değerinin hepsi ilk koşumda beklenen değerde.
- Düzeltme yalnız K1-11'i değiştirdi (falsified → verified). Öteki 14 KAT-1 Tamarin hücresinin ve 7 Tamarin mutasyon satırının hükmü ilk koşumla aynı. Tablo: aşağıdaki KAT-1 bölümü.
- Mutasyonlar "katı dönme" ölçütüyle sayıldı: mutasyonlu değer beklenen yönde ve mutasyonsuz temel koşudan farklı.

## K1-11: ilk koşumdaki uyumsuzluk (iz, tanı) ve düzeltme
- **Gözlenen (ilk koşum):** falsified, 12 adım (`dnssec/sonuc/tamarin_ham/K1-11.tam__a_rrset_authentic__b1.txt`). Aynı hücrede ASP beklenen değeri verdi: YOK.
- **İz:**
  1. `Break_Zone_Classical`: klasik KSK `~kc` ve ZSK açığa çıkar.
  2. Saldırgan DNSKEY RRset'ini kendi ZSK'larıyla (`pk(x)`, `pk(x.1)`) kurar ve `~kc` ile imzalar.
  3. `Validate_DNSKEY_via_KSKcl`: gerçek çift-DS `pk(kc)`'yi listelediği için kabul edilir.
  4. `DKok` → `Validate_A_complete_both`: A RRset iki saldırgan anahtarıyla imzalıdır.
  5. `AcceptA`, `SignedA` olmadan gerçekleşir.
- **Tanı:** test modelinin kodlama hatası, Tamarin tarafında. Yürütücü iki modeli bağımsız koşarak doğruladı.
  - KAT-SPEC §2(c) taslağı `COMPLETENESS`'i yalnız A RRset adımında uygular; DNSKEY adımı "herhangi bir tek yol" kalır.
  - RFC 6840 §5.11'in "insist that all algorithms signaled in the DS RRset work" kuralı DNSKEY adımında uygulanmıyordu.
  - ASP eşlemesi bütünlüğü zincirin tamamında uygular (`tasi(ds,dnskey)`, `tasi(ds,a_rr)`); ASP ilk koşumda doğruydu.
- **B2 alternatif okuması (yalnız tanıda kullanıldı):** "test yalnız DNSKEY RRset'inde" okuması K1-04, K1-06 ve K1-11'in üçünü de falsified yapardı. Gözlenen yalnız K1-11; bu yüzden fark B2'nin alternatifi değil.
- **Düzeltme (yürütücü kararı):** `dnssec/KAT1_DNSSEC_v2.spthy` = tanı modelinin kuralları (`dnssec/tani/`), "düzeltilmiş kapı modeli".
  - **Tek genişletme:** §6 mutasyon alternatifleri v2 doğrulayıcılarına göre tanımlandı; `COMPLETENESS`'te bütünlük korunur, yalnız adı geçen denetim silinir. Tanı modelinde bu durumda eski doğrulayıcılar devreye giriyordu.
  - `COMPLETENESS` verilmeyen her bayrak kümesinde v2 v1 ile aynıdır (diff: ADIM06-RAPOR §8).
  - `KAT1_DNSSEC.spthy` dokunulmadan kaldı.
- **Düzeltme sonrası koşum:**
  - 15 hücre ve 7 mutasyon satırının hepsi v2 ile yeniden koşuldu.
  - Yalnız K1-11 değişti (verified, 28 adım); öteki 21 satırın hükmü v1 ile aynı.
  - İyi biçimlilik: 16/16 bayrak kümesi, uyarı 0.
- **Kural (ÖK §2C.1):** Yedek teste geçilmedi; beklenen değere dokunulmadı. İlk koşumun KALDI kaydı korunur; iki koşum birlikte sunulur.

## Ek maddeler (`nsurum`'da yok; ayrıca raporlanır)
- **KAT-2 Tamarin duyarlılık lemmaları** (`accept_with_invalid_pq`, KAT-SPEC §3(d)): 3/3 beklenen yönde. V_IGNORE verified: bozuk PQ kanıtıyla kabul erişilebilir (Kim'in bulgusu). V_ENFORCE_IF_PRESENT ve V_REQUIRE falsified.
- **KAT-3a (KAT-SPEC §4(d)):** `kat3a_fail` boş; `model_gap` yalnız o8 (okuma notu; yazarlara atfedilmez).
- **KAT-3b pilot iyi biçimlilik düzeltmesi — yürütücü KABUL etti (26.09.2026):**
  - Uyarılı model (pilot aslı) geçersizdir; tek sözcüklük düzeltmeli kopya (`smime/weakest_link_wf.spthy`) kapı hücresidir.
  - Pilotun aslı 6/6 aynı hükmü ve aynı adım sayısını verdi (`smime/sonuc/tamarin_ek.csv`); bu bilgi olarak kalır.

## Adım 6 kabul ölçütleri (IS-PLANI 6.6)
1. **V-d:**
   - ilk koşum: 2/3 KAT GEÇTİ (KAT-1 KALDI; Tamarin K1-11);
   - düzeltme sonrası: 3/3.

   Bağımsız gözden geçirme ikisini birlikte değerlendirecek.
2. **Kör beklenen-değer tablosu ilk koşumdan önce hash'lendi:** evet. `kor-beklenen/BEKLENEN-KOR.tsv` `180a655a…` (commit `f012841`); uzlaşılmış tablo `nsurum/kat_nsurum.tsv` çapa 8'de.
3. **Çekirdek (`cekirdek.lp`) özeti testlerden önce ve sonra aynı:** evet (düzeltme ASP'ye dokunmadı).
4. **Birebir alıntılar sabitlenmiş metinde betikle bulundu:** 21/21 (`*/sonuc/alinti_denetimi.tsv`).

## Nasıl üretildi
- **Her klasör:** `uret.py` (örnek dosyaları) → `kos.py` (ASP; konteyner) → `tamarin_kos.py kos` (Tamarin; merdivenli) → `degerlendir.py` (koşu yapmaz) → `sonuc/KAT_OZET.{json,md}`.
- **Düzeltme sonrası (yalnız KAT-1 Tamarin):** `dnssec/tamarin_kos_v2.py` → `dnssec/degerlendir_v2.py` → `dnssec/sonuc_v2/KAT_OZET.{json,md}` → `dnssec/yanyana_v1_v2.py` → `dnssec/sonuc_v2/YANYANA.md`.
  - `tamarin_kos_v2.py` dondurulmuş koşucuyu değiştirmeden içe aktarır.
  - `degerlendir_v2.py`, `degerlendir.py`'den yalnız yol ve etiket satırları değiştirilerek mekanik olarak türetildi.
- **Aşağıdaki bölümler:**
  - KAT-1: `YANYANA.md`;
  - KAT-2 ve KAT-3: ilk koşumun `KAT_OZET.md`'lerinin birebir kopyası;
  - ilk koşumun KAT-1 özeti `dnssec/sonuc/KAT_OZET.md`'de olduğu gibi durur.

---

## KAT-1 DNSSEC: ilk koşum ve düzeltme sonrası koşum (yan yana)

**KAT kararı:**

- ilk koşum (v1, `KAT1_DNSSEC.spthy`, commit `e4c1090`): **KALDI**
- düzeltme sonrası (v2, `KAT1_DNSSEC_v2.spthy`; "sonuç görüldükten sonra düzeltme"): **GEÇTİ**

| Koşul | İlk koşum (v1) | Düzeltme sonrası (v2) |
|---|---|---|
| ASP hücreleri | 15/15 | 15/15 |
| Tamarin hücreleri | 14/15 | 15/15 |
| ASP–Tamarin uyumu | 14/15 | 15/15 |
| Mutasyonlar (KAT-SPEC §6) | 5/5 | 5/5 |
| executable hepsi verified | evet | evet |
| İyi biçimlilik (uyarı 0) | evet | evet |
| Çekirdek özeti önce = sonra = 45cbd0f | evet | evet |

ASP ilk koşumdur; yeniden koşulmadı, `cekirdek.lp`'ye dokunulmadı. v2 yalnız Tamarin tarafını değiştirir.

| Hücre | ASP beklenen | ASP gözlenen | Tamarin beklenen | Tamarin ilk koşum (v1) | Tamarin düzeltme sonrası (v2) | v2 adım | v1→v2 |
|---|---|---|---|---|---|---|---|
| K1-01 | SALDIRI | SALDIRI | falsified | falsified | falsified | 12 | aynı |
| K1-02 | SALDIRI | SALDIRI | falsified | falsified | falsified | 12 | aynı |
| K1-03 | SALDIRI | SALDIRI | falsified | falsified | falsified | 12 | aynı |
| K1-04 | YOK | YOK | verified | verified | verified | 18 | aynı |
| K1-05 | SALDIRI | SALDIRI | falsified | falsified | falsified | 12 | aynı |
| K1-06 | YOK | YOK | verified | verified | verified | 18 | aynı |
| K1-07 | SALDIRI | SALDIRI | falsified | falsified | falsified | 12 | aynı |
| K1-08 | YOK | YOK | verified | verified | verified | 21 | aynı |
| K1-09 | YOK | YOK | verified | verified | verified | 19 | aynı |
| K1-10 | SALDIRI | SALDIRI | falsified | falsified | falsified | 12 | aynı |
| K1-11 | YOK | YOK | verified | falsified ✗ | verified | 28 | **değişti** |
| K1-12 | SALDIRI | SALDIRI | falsified | falsified | falsified | 14 | aynı |
| K1-13 | YOK | YOK | verified | verified | verified | 22 | aynı |
| K1-14 | SALDIRI | SALDIRI | falsified | falsified | falsified | 8 | aynı |
| K1-15 | SALDIRI | SALDIRI | falsified | falsified | falsified | 12 | aynı |

| Mutasyon koşusu | Beklenen | ASP (ilk koşum) | Tamarin v1 | Tamarin v2 | v2 temel hücreden farklı mı |
|---|---|---|---|---|---|
| MUT01.K1-04.tam | falsified | SALDIRI | falsified | falsified | evet |
| MUT01.K1-11.tam | falsified | SALDIRI | falsified | falsified | evet |
| MUT02.K1-04.tam | falsified | SALDIRI | falsified | falsified | evet |
| MUT03.K1-04.tam | falsified | SALDIRI | falsified | falsified | evet |
| MUT04.K1-06.tam | falsified | SALDIRI | falsified | falsified | evet |
| MUT04.K1-08.tam | falsified | SALDIRI | falsified | falsified | evet |
| MUT05.K1-09.tam | falsified | SALDIRI | falsified | falsified | evet |

| Mutasyon | İlk koşum (motor: döndü mü) | Düzeltme sonrası (motor: döndü mü) |
|---|---|---|
| MUT01 | asp: evet, tamarin: evet | asp: evet, tamarin: evet |
| MUT02 | asp: evet, tamarin: evet | asp: evet, tamarin: evet |
| MUT03 | asp: evet, tamarin: evet | asp: evet, tamarin: evet |
| MUT04 | asp: evet, tamarin: evet | asp: evet, tamarin: evet |
| MUT05 | asp: evet, tamarin: evet | asp: evet, tamarin: evet |

## KAT-2 X.509 hibrit — GEÇTİ

| Koşul | Sonuç |
|---|---|
| ASP hücreleri | 40/40 |
| Tamarin hücreleri | 8/8 |
| executable (her Tamarin koşusu) | hepsi verified |
| İyi biçimlilik (uyarı 0) | evet |
| ASP–Tamarin uyumu | 8/8 |
| Mutasyonlar (KAT-SPEC §6) | 4/4 |
| Çekirdek özeti önce = sonra = 45cbd0f | evet |
| Birebir alıntılar | 9/9 |

| Hücre | Sütun | Beklenen | Gözlenen | Çekirdek dayanağı |
|---|---|---|---|---|
| K2a-01 | decision(pqev=valid) | accept_classical | accept_classical | G5 |
| K2a-02 | decision(pqev=invalid) | accept_classical | accept_classical | G5 |
| K2a-03 | decision(pqev=valid) | accept_classical | accept_classical | G5 |
| K2a-04 | decision(pqev=invalid) | accept_classical | accept_classical | G5 |
| K2a-05 | decision(pqev=valid) | accept_classical | accept_classical | G5 |
| K2a-06 | decision(pqev=invalid) | accept_classical | accept_classical | G5 |
| K2a-07 | decision(leafb=valid) | accept_classical | accept_classical | G5 |
| K2a-08 | decision(leafb=revoked) | accept_classical | accept_classical | G5 |
| K2a-09 | decision(pqev=valid) | accept_hybrid | accept_hybrid | G5 yok |
| K2a-10 | decision(pqev=invalid) | reject | reject | G5 yok |
| K2a-11 | decision(pqev=absent) | accept_classical | accept_classical | G5 |
| K2a-12 | decision(pqev=valid) | accept_hybrid | accept_hybrid | G5 yok |
| K2a-13 | decision(pqev=invalid) | reject | reject | G5 yok |
| K2a-14 | decision(pqev=absent) | reject | reject | G5 yok |
| K2a-15 | decision(pqev=valid) | accept_hybrid | accept_hybrid | G5 yok |
| K2a-16 | decision(pqev=invalid) | reject | reject | G5 yok |
| K2a-17 | decision(pqev=valid) | reject | reject | G5 yok |
| K2b-01 | ASP | SALDIRI | SALDIRI | g1 |
| K2b-02 | ASP | SALDIRI | SALDIRI | g1 |
| K2b-03 | ASP | YOK | YOK | g1 |
| K2b-04 | ASP | SALDIRI | SALDIRI | g1 |
| K2b-05 | ASP | YOK | YOK | g1 |
| K2b-06 | ASP | YOK | YOK | g1 |
| K2b-07 | ASP | SALDIRI | SALDIRI | g1 |
| K2b-08 | ASP | YOK | YOK | g1 |
| K2c-revoked | karar(vb=ignore) | accept_classical | accept_classical | G5 |
| K2c-revoked | karar(vb=require) | reject | reject | G5 yok |
| K2c-expired | karar(vb=ignore) | accept_classical | accept_classical | G5 |
| K2c-expired | karar(vb=require) | reject | reject | G5 yok |
| K2c-unknown | karar(vb=ignore) | accept_classical | accept_classical | G5 |
| K2c-unknown | karar(vb=require) | indeterminate | indeterminate | G5 yok |
| K2c-absent | karar(vb=ignore) | accept_classical | accept_classical | G5 |
| K2c-absent | karar(vb=require) | reject | reject | G5 yok |
| K2c-valid | karar(vb=ignore) | accept_classical | accept_classical | G5 |
| K2c-valid | karar(vb=require) | accept_hybrid | accept_hybrid | G5 yok |
| K2d-01 | ASP:karar | accept_classical | accept_classical | G5 |
| K2d-02 | ASP:karar | accept_classical | accept_classical | G5 |
| K2d-03 | ASP:karar | reject | reject | G5 yok |
| K2d-04 | ASP:karar | reject | reject | G5 yok |
| K2d-05 | ASP:karar | accept_classical | accept_classical | G5 |
| K2b-01 | Tamarin:cert_authentic | falsified | falsified | Tamarin (CRQC,V_IGNORE) |
| K2b-02 | Tamarin:cert_authentic | falsified | falsified | Tamarin (CRQC,V_ENFORCE_IF_PRESENT) |
| K2b-03 | Tamarin:cert_authentic | verified | verified | Tamarin (CRQC,V_REQUIRE) |
| K2b-06 | Tamarin:cert_authentic | verified | verified | Tamarin (CRQC,COMPOSITE) |
| K2b-07 | Tamarin:cert_authentic | falsified | falsified | Tamarin (CRQC,COMPOSITE,COEXIST_CLASSICAL) |
| K2d-01 | Tamarin | falsified | falsified | Tamarin (M1_LEGACY,V_IGNORE) |
| K2d-02 | Tamarin | falsified | falsified | Tamarin (M1_LEGACY,V_ENFORCE_IF_PRESENT) |
| K2d-03 | Tamarin | verified | verified | Tamarin (M1_LEGACY,V_REQUIRE) |

| Mutasyon | Motor: döndü mü |
|---|---|
| MUT06 | asp: evet, tamarin: evet |
| MUT07 | asp: evet, tamarin: evet |
| MUT08 | asp: evet |
| MUT09 | asp: evet |

Ek (kapı hücresi değil; KAT-SPEC §3(d) duyarlılık lemmaları):

| Koşu | Beklenen (KAT-SPEC) | Gözlenen | İyi biçimli |
|---|---|---|---|
| EK.duy-ignore.tam | verified | verified | EVET |
| EK.duy-enforce.tam | falsified | falsified | EVET |
| EK.duy-require.tam | falsified | falsified | EVET |

## KAT-3 S/MIME — GEÇTİ

| Koşul | Sonuç |
|---|---|
| ASP hücre değerleri (3a: 36, 3b: 18) | 54/54 |
| Tamarin hücreleri | 9/9 |
| executable (her Tamarin koşusu) | hepsi verified |
| İyi biçimlilik (uyarı 0; kapı modelleri) | evet |
| ASP–Tamarin uyumu | 9/9 |
| Mutasyonlar (KAT-SPEC §6) | 3/3 |
| Çekirdek özeti önce = sonra = 45cbd0f | evet |
| KAT-SPEC §4(d) ek: kat3a_fail boş / model_gap yalnız o8 | evet / evet |
| Birebir alıntılar | 5/5 |

| Hücre | Sütun | Beklenen | Gözlenen | Dayanak |
|---|---|---|---|---|
| V1 | attack(qday=0) | SALDIRI | SALDIRI | V1.qday0.asp |
| V1 | attack(qday=200) | YOK | YOK | V1.qday200.asp |
| V1 | violation(qday=0) | 1 | 1 | V1.statik.asp |
| V2 | attack(qday=0) | SALDIRI | SALDIRI | V2.qday0.asp |
| V2 | attack(qday=200) | YOK | YOK | V2.qday200.asp |
| V2 | violation(qday=0) | 1 | 1 | V2.statik.asp |
| V3 | attack(qday=0) | SALDIRI | SALDIRI | V3.qday0.asp |
| V3 | attack(qday=200) | YOK | YOK | V3.qday200.asp |
| V3 | violation(qday=0) | 1 | 1 | V3.statik.asp |
| V4 | attack(qday=0) | YOK | YOK | V4.qday0.asp |
| V4 | attack(qday=200) | YOK | YOK | V4.qday200.asp |
| V4 | violation(qday=0) | 0 | 0 | V4.statik.asp |
| V5 | attack(qday=0) | YOK | YOK | V5.qday0.asp |
| V5 | attack(qday=200) | YOK | YOK | V5.qday200.asp |
| V5 | violation(qday=0) | 0 | 0 | V5.statik.asp |
| V6 | attack(qday=0) | SALDIRI | SALDIRI | V6.qday0.asp |
| V6 | attack(qday=200) | YOK | YOK | V6.qday200.asp |
| V6 | violation(qday=0) | 1 | 1 | V6.statik.asp |
| o1 | out | pqc_protected | pqc_protected | bilinmeyen=0 gecersiz=0 gecis=0 kati=0 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o1 | accept_strict | 1 | 1 | bilinmeyen=0 gecersiz=0 gecis=0 kati=0 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o1 | accept_transitional | 1 | 1 | bilinmeyen=0 gecersiz=0 gecis=0 kati=0 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o2 | out | pqc_protected | pqc_protected | bilinmeyen=0 gecersiz=0 gecis=0 kati=0 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o2 | accept_strict | 1 | 1 | bilinmeyen=0 gecersiz=0 gecis=0 kati=0 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o2 | accept_transitional | 1 | 1 | bilinmeyen=0 gecersiz=0 gecis=0 kati=0 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o3 | out | classical_only | classical_only | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=0 tum_klasik_yol=1 |
| o3 | accept_strict | 0 | 0 | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=0 tum_klasik_yol=1 |
| o3 | accept_transitional | 0 | 0 | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=0 tum_klasik_yol=1 |
| o4 | out | unsafe_mixed | unsafe_mixed | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=1 tum_klasik_yol=1 |
| o4 | accept_strict | 0 | 0 | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=1 tum_klasik_yol=1 |
| o4 | accept_transitional | 0 | 0 | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=1 tum_klasik_yol=1 |
| o5 | out | hybrid_protected | hybrid_protected | bilinmeyen=0 gecersiz=0 gecis=0 kati=1 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o5 | accept_strict | 0 | 0 | bilinmeyen=0 gecersiz=0 gecis=0 kati=1 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o5 | accept_transitional | 1 | 1 | bilinmeyen=0 gecersiz=0 gecis=0 kati=1 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o6 | out | unsafe_mixed | unsafe_mixed | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=1 tum_klasik_yol=1 |
| o6 | accept_strict | 0 | 0 | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=1 tum_klasik_yol=1 |
| o6 | accept_transitional | 0 | 0 | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=1 tum_klasik_yol=1 |
| o7 | out | unknown | unknown | bilinmeyen=1 gecersiz=0 gecis=1 kati=1 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o7 | accept_strict | 0 | 0 | bilinmeyen=1 gecersiz=0 gecis=1 kati=1 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o7 | accept_transitional | 0 | 0 | bilinmeyen=1 gecersiz=0 gecis=1 kati=1 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o8 | out | pqc_protected | pqc_protected | bilinmeyen=0 gecersiz=0 gecis=0 kati=0 klasik=0 pq_hibrit=1 tum_klasik_yol=1 |
| o8 | accept_strict | 1 | 1 | bilinmeyen=0 gecersiz=0 gecis=0 kati=0 klasik=0 pq_hibrit=1 tum_klasik_yol=1 |
| o8 | accept_transitional | 1 | 1 | bilinmeyen=0 gecersiz=0 gecis=0 kati=0 klasik=0 pq_hibrit=1 tum_klasik_yol=1 |
| o9 | out | invalid | invalid | bilinmeyen=0 gecersiz=1 gecis=1 kati=1 klasik=0 pq_hibrit=0 tum_klasik_yol=0 |
| o9 | accept_strict | 0 | 0 | bilinmeyen=0 gecersiz=1 gecis=1 kati=1 klasik=0 pq_hibrit=0 tum_klasik_yol=0 |
| o9 | accept_transitional | 0 | 0 | bilinmeyen=0 gecersiz=1 gecis=1 kati=1 klasik=0 pq_hibrit=0 tum_klasik_yol=0 |
| o10 | out | unknown | unknown | bilinmeyen=1 gecersiz=0 gecis=1 kati=1 klasik=0 pq_hibrit=0 tum_klasik_yol=0 |
| o10 | accept_strict | 0 | 0 | bilinmeyen=1 gecersiz=0 gecis=1 kati=1 klasik=0 pq_hibrit=0 tum_klasik_yol=0 |
| o10 | accept_transitional | 0 | 0 | bilinmeyen=1 gecersiz=0 gecis=1 kati=1 klasik=0 pq_hibrit=0 tum_klasik_yol=0 |
| o11 | out | hybrid_protected | hybrid_protected | bilinmeyen=0 gecersiz=0 gecis=0 kati=1 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o11 | accept_strict | 0 | 0 | bilinmeyen=0 gecersiz=0 gecis=0 kati=1 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o11 | accept_transitional | 1 | 1 | bilinmeyen=0 gecersiz=0 gecis=0 kati=1 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o12 | out | classical_only | classical_only | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=0 tum_klasik_yol=1 |
| o12 | accept_strict | 0 | 0 | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=0 tum_klasik_yol=1 |
| o12 | accept_transitional | 0 | 0 | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=0 tum_klasik_yol=1 |
| MIXED | Tamarin:cek_secrecy | falsified | falsified | Tamarin (MIXED; KAT3_SMIME.spthy) |
| PQ_ONLY | Tamarin:cek_secrecy | verified | verified | Tamarin (PQ_ONLY; KAT3_SMIME.spthy) |
| HYBRID_KEM | Tamarin:cek_secrecy | verified | verified | Tamarin (HYBRID_KEM; KAT3_SMIME.spthy) |
| V1 | Tamarin:claims_unforgeability | falsified | falsified | Tamarin (-; weakest_link_wf.spthy) |
| V2 | Tamarin:claims_unforgeability | falsified | falsified | Tamarin (EXPECT_IN_TL; weakest_link_wf.spthy) |
| V3 | Tamarin:claims_unforgeability | falsified | falsified | Tamarin (TL_PQ; weakest_link_wf.spthy) |
| V4 | Tamarin:claims_unforgeability | verified | verified | Tamarin (TL_PQ,EXPECT_IN_TL; weakest_link_wf.spthy) |
| V5 | Tamarin:claims_unforgeability | verified | verified | Tamarin (TL_PQ,NO_COEXIST; weakest_link_wf.spthy) |
| V6 | Tamarin:claims_unforgeability | falsified | falsified | Tamarin (NO_COEXIST; weakest_link_wf.spthy) |

| ASP–Tamarin ortak hücre | ASP (Tamarin diliyle) | Tamarin |
|---|---|---|
| MIXED<->o4 | falsified | falsified |
| PQ_ONLY<->o1 | verified | verified |
| HYBRID_KEM<->o5 | verified | verified |
| V1 | falsified | falsified |
| V2 | falsified | falsified |
| V3 | falsified | falsified |
| V4 | verified | verified |
| V5 | verified | verified |
| V6 | falsified | falsified |

| Mutasyon | Motor: döndü mü |
|---|---|
| MUT10 | tamarin: evet |
| MUT11 | asp: evet |
| MUT12 | asp: evet |

Ek (kapı hücresi değil): pilot ASLI ile KAT-3b Tamarin (iyi biçimlilik uyarılı):

| Koşu | Beklenen (nsurum) | Gözlenen (ham) | İyi biçimli |
|---|---|---|---|
| EK.V1.pilot_asli.tam | falsified | falsified | HAYIR |
| EK.V2.pilot_asli.tam | falsified | falsified | HAYIR |
| EK.V3.pilot_asli.tam | falsified | falsified | HAYIR |
| EK.V4.pilot_asli.tam | verified | verified | HAYIR |
| EK.V5.pilot_asli.tam | verified | verified | HAYIR |
| EK.V6.pilot_asli.tam | falsified | falsified | HAYIR |

## Tanı koşusu ayrıntısı (dnssec/tani/sonuc.csv; SONUÇ GÖRÜLDÜKTEN SONRA; v2 düzeltmesinin öncülü, kapı değeri DEĞİL)

| Hücre | Bayraklar | Beklenen | Tanı modeli | Adım | İyi biçimli | executable |
|---|---|---|---|---|---|---|
| K1-02 | DS_CL,DK3_USABLE,COMPLETENESS | falsified | falsified | 12 | EVET | verified |
| K1-04 | DS_PQ,DK3_USABLE,COMPLETENESS | verified | verified | 18 | EVET | verified |
| K1-05 | DS_PQ,OLD_DS_REPLAY,DK3_USABLE,COMPLETENESS | falsified | falsified | 12 | EVET | verified |
| K1-06 | DS_PQ,DK3_USABLE,COMPLETENESS | verified | verified | 18 | EVET | verified |
| K1-11 | DS_BOTH,DK3_USABLE,COMPLETENESS | verified | verified | 28 | EVET | verified |
| K1-12 | DS_PQ,DK3_USABLE,COMPLETENESS,PARENT_CL | falsified | falsified | 14 | EVET | verified |
