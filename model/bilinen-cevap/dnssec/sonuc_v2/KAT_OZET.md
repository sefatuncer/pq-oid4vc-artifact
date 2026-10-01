## KAT-1 DNSSEC (düzeltme sonrası, v2) — GEÇTİ

| Koşul | Sonuç |
|---|---|
| ASP hücreleri | 15/15 |
| Tamarin hücreleri | 15/15 |
| executable (her Tamarin koşusu) | hepsi verified |
| İyi biçimlilik (uyarı 0) | evet |
| ASP–Tamarin uyumu | 15/15 |
| Mutasyonlar (KAT-SPEC §6) | 5/5 |
| Çekirdek özeti önce = sonra = 45cbd0f | evet |
| Birebir alıntılar | 7/7 |

| Hücre | ASP beklenen | ASP gözlenen | Tamarin beklenen | Tamarin gözlenen |
|---|---|---|---|---|
| K1-01 | SALDIRI | SALDIRI | falsified | falsified |
| K1-02 | SALDIRI | SALDIRI | falsified | falsified |
| K1-03 | SALDIRI | SALDIRI | falsified | falsified |
| K1-04 | YOK | YOK | verified | verified |
| K1-05 | SALDIRI | SALDIRI | falsified | falsified |
| K1-06 | YOK | YOK | verified | verified |
| K1-07 | SALDIRI | SALDIRI | falsified | falsified |
| K1-08 | YOK | YOK | verified | verified |
| K1-09 | YOK | YOK | verified | verified |
| K1-10 | SALDIRI | SALDIRI | falsified | falsified |
| K1-11 | YOK | YOK | verified | verified |
| K1-12 | SALDIRI | SALDIRI | falsified | falsified |
| K1-13 | YOK | YOK | verified | verified |
| K1-14 | SALDIRI | SALDIRI | falsified | falsified |
| K1-15 | SALDIRI | SALDIRI | falsified | falsified |

| Mutasyon | Motor: döndü mü |
|---|---|
| MUT01 | asp: evet, tamarin: evet |
| MUT02 | asp: evet, tamarin: evet |
| MUT03 | asp: evet, tamarin: evet |
| MUT04 | asp: evet, tamarin: evet |
| MUT05 | asp: evet, tamarin: evet |
