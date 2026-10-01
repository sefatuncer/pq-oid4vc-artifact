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
