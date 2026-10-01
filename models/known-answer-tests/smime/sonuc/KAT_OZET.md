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
