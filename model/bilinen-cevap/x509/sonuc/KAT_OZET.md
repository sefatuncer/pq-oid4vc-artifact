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
