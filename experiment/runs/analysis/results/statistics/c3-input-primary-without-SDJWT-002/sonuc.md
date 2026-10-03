# C3 (H6) istatistik çıktısı

- Araç: c3istat 1.0.0 · Python 3.11.16 · numpy 2.4.6 · scipy 1.17.1 · statsmodels 0.15.0
- Girdi: `c3-input-primary-without-SDJWT-002.json` · SHA-256 `46e372ad50836fa40cc9f4e47cd51725bc38659a9bcafae8f9908c6323d1afdc` · veri türü **olcum** · şema c3-istat-girdi/1.0
- İki uygulama (kesin ↔ kütüphane): 95 uyumlu + 0 sınırda / 95; hata 0 → **GEÇERLİ**
- UYARI: n = 30; ÖK §2B.3 n = 31 bekliyor (eşikler n_eff'ten Ek A kuralıyla yeniden hesaplanır)
- UYARI: veri_turu = olcum: bu çalıştırma yalnız dondurulmuş ön kayıttan SONRA geçerlidir (ÖK §10)

## H6 hükmü: **BELİRSİZ**

c < X < u (ÖK §6.13). Birincil: belirsiz; duyarlılık (i): belirsiz.

## T1 (birincil, Holm dışı) ve duyarlılıklar

| Analiz | n_eff | X | c | u | P(X′ ≤ X) | P(X′ ≥ X) | Oran | Wilson %95 GA | Karar |
|---|---|---|---|---|---|---|---|---|---|
| Birincil | 29 | 19 | 9 | 20 | 0,969286 | 0,068023 | 0,6552 | [0,4735; 0,8006] | belirsiz |
| (i) belirsiz = 1 | 29 | 19 | 9 | 20 | 0,969286 | 0,068023 | 0,6552 | [0,4735; 0,8006] | belirsiz |
| (ii) belirsiz = 0 | 29 | 19 | 9 | 20 | 0,969286 | 0,068023 | 0,6552 | [0,4735; 0,8006] | belirsiz |
| Pilot hariç | 22 | 13 | 6 | 16 | 0,856861 | 0,261734 | 0,5909 | [0,3873; 0,7674] | belirsiz |
| Devralan hariç | 28 | 19 | 9 | 19 | 0,982151 | 0,043579 | 0,6786 | [0,4934; 0,8207] | yanlislama |
| Adaptör geçersiz = 0 | 30 | 19 | 10 | 20 | 0,950631 | 0,100244 | 0,6333 | [0,4551; 0,7813] | belirsiz |

## T2–T5 ve Holm (aile T2–T5, m = 4, α = 0,05)

| Test | Veri | p (ham) | p (Holm) | Holm reddi | Etki büyüklüğü |
|---|---|---|---|---|---|
| T2 McNemar (TK1+TK2) | n_çift = 0; b = 0, c = 0 | 1,000000 (kesin 1) | 1,000000 | hayır | — |
| T3 Fisher | SDJWT [0, 0] / JOSE [1, 1] | 1,000000 (kesin 1) | 1,000000 | hayır | OR tanımsız [0,0000; ∞] (koşullu kesin); fark — |
| T4 Fisher | 8725bis_sonrasi=1 [9, 1] / 8725bis_sonrasi=0 [13, 5] | 0,374582 (kesin 112/299) | 1,000000 | hayır | OR 3,3290 [0,2944; 181,5992] (koşullu kesin); fark 0,1778 [−0,1626; 0,4229] (Newcombe 10) |
| T5 binom (üst) | 6/6 | 0,015625 (kesin 1/64) | 0,062500 | hayır | oran 1,0000 [0,6097; 1,0000] |

Devralan hariç T2 (tanımlayıcı, Holm dışı): n_çift = 0, b = 0, c = 0, p = 1,000000. TK3 (tanımlayıcı): {'a': 4, 'b': 2, 'c': 0, 'd': 0}.

## Wilson %95 GA (ÖK §6.8)

| Değişken | Kategori | x/n | Oran | GA |
|---|---|---|---|---|
| L düzeyi | L0 | 6/29 | 0,2069 | [0,0985; 0,3839] |
| L düzeyi | L1 | 0/29 | 0,0000 | [0,0000; 0,1170] |
| L düzeyi | L2 | 0/29 | 0,0000 | [0,0000; 0,1170] |
| L düzeyi | L3 | 4/29 | 0,1379 | [0,0550; 0,3056] |
| L düzeyi | L4 | 19/29 | 0,6552 | [0,4735; 0,8006] |
| L düzeyi | L5 | 0/29 | 0,0000 | [0,0000; 0,1170] |
| L ≥ k (ek) | L≥1 | 23/29 | 0,7931 | [0,6161; 0,9015] |
| L ≥ k (ek) | L≥2 | 23/29 | 0,7931 | [0,6161; 0,9015] |
| L ≥ k (ek) | L≥3 | 23/29 | 0,7931 | [0,6161; 0,9015] |
| L ≥ k (ek) | L≥4 | 19/29 | 0,6552 | [0,4735; 0,8006] |
| L ≥ k (ek) | L≥5 | 0/29 | 0,0000 | [0,0000; 0,1170] |
| B1 | red | 0/2 | 0,0000 | [0,0000; 0,6576] |
| B1 | yok_sayma | 2/2 | 1,0000 | [0,3424; 1,0000] |
| B1 | dogrulama_duser | 0/2 | 0,0000 | [0,0000; 0,6576] |
| B5 | en_az_biri_gecerli | 2/6 | 0,3333 | [0,0968; 0,7000] |
| B5 | mevcut_tumu_gecerli | 1/6 | 0,1667 | [0,0301; 0,5635] |
| B5 | gerekli_kume | 0/6 | 0,0000 | [0,0000; 0,3903] |
| B5 | diger | 3/6 | 0,5000 | [0,1876; 0,8124] |
| B2 | 1 | 2/11 | 0,1818 | [0,0514; 0,4770] |
| B3 | 1 | 0/1 | 0,0000 | [0,0000; 0,7935] |
| B4_ozel_kod | 1 | 2/29 | 0,0690 | [0,0191; 0,2196] |
| B6 | 1 | 29/29 | 1,0000 | [0,8830; 1,0000] |
| Y_L4 | L4m | 2/6 | 0,3333 | [0,0968; 0,7000] |
| Y_L4 | L4c | 17/23 | 0,7391 | [0,5353; 0,8745] |

## Küme bootstrap (ÖK §6.9; B = 10.000; tohum 20260927; yüzdelik tip 7)

| Kapsam | k | Vaka | Oracle'a uymayan oran | %95 GA | Durum |
|---|---|---|---|---|---|
| tum | 29 | 100 | 0,3600 | [0,2209; 0,4766] | tamam |
| K | 29 | 82 | 0,2439 | [0,1275; 0,3636] | tamam |
| T | 6 | 18 | 0,8889 | [0,7778; 1,0000] | tamam |

## Tanımlayıcılar

- n = 30; n_eff (T1) = 29; adaptör geçersiz: SDJWT-021; Y_L4 belirsiz: yok
- Tabaka: {'COSE': 5, 'JOSE': 18, 'SDJWT': 7}; TK: {'TK3': 29}; L4 biçimi: {'L4c': 23, 'L4m': 6}; kontrol etiketi: {'ES384': 13, 'EdDSA': 16}
- Belirsiz nedenleri: {'B1': {'uygulanamaz': 27}, 'B2': {'uygulanamaz': 18}, 'B3': {'uygulanamaz': 28}, 'B5': {'uygulanamaz': 23}, 'D_soy': {'uygulanamaz': 23}, 'F_K': {'uygulanamaz': 23}, 'F_T': {'uygulanamaz': 23}, 'surum_8725bis_sonrasi': {'uygulanamaz': 1}}; kararsız hücre (vaka): 0
- B4 satır: {'n': 2, 'medyan': 8.0, 'min': 8, 'max': 8}; devralanlar: [{'hedef_id': 'SDJWT-001', 'devraldigi_hedef': 'COSE-001'}]; pilotlar: ['JOSE-009', 'JOSE-033', 'JOSE-034', 'JOSE-065', 'JOSE-083', 'JOSE-084', 'SDJWT-015']
- REF (n dışı): yok

