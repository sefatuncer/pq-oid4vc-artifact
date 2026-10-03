# C3 (H6) istatistik çıktısı

- Araç: c3istat 1.0.0 · Python 3.11.16 · numpy 2.4.6 · scipy 1.17.1 · statsmodels 0.15.0
- Girdi: `c3-input-secondary-mldsa-tk-sensitivity.json` · SHA-256 `18bae2541521e4f85f78c2820ac09747d9645a751d04535b2c3bda687b9a4c3e` · veri türü **olcum** · şema c3-istat-girdi/1.0
- İki uygulama (kesin ↔ kütüphane): 97 uyumlu + 0 sınırda / 97; hata 0 → **GEÇERLİ**
- UYARI: veri_turu = olcum: bu çalıştırma yalnız dondurulmuş ön kayıttan SONRA geçerlidir (ÖK §10)

## H6 hükmü: **YANLIŞLAMA**

birincil analiz ve duyarlılık (ii) birlikte X ≥ u (ÖK §3.7, §2B.5; Değişiklik 8 m.17). Birincil: yanlislama; duyarlılık (i): yanlislama.

## T1 (birincil, Holm dışı) ve duyarlılıklar

| Analiz | n_eff | X | c | u | P(X′ ≤ X) | P(X′ ≥ X) | Oran | Wilson %95 GA | Karar |
|---|---|---|---|---|---|---|---|---|---|
| Birincil | 30 | 21 | 10 | 20 | 0,991938 | 0,021387 | 0,7000 | [0,5212; 0,8334] | yanlislama |
| (i) belirsiz = 1 | 30 | 21 | 10 | 20 | 0,991938 | 0,021387 | 0,7000 | [0,5212; 0,8334] | yanlislama |
| (ii) belirsiz = 0 | 30 | 21 | 10 | 20 | 0,991938 | 0,021387 | 0,7000 | [0,5212; 0,8334] | yanlislama |
| Pilot hariç | 23 | 14 | 7 | 16 | 0,894980 | 0,202436 | 0,6087 | [0,4079; 0,7784] | belirsiz |
| Devralan hariç | 29 | 21 | 9 | 20 | 0,995935 | 0,012060 | 0,7241 | [0,5428; 0,8530] | yanlislama |
| Adaptör geçersiz = 0 | 31 | 21 | 10 | 21 | 0,985275 | 0,035378 | 0,6774 | [0,5014; 0,8143] | yanlislama |

## T2–T5 ve Holm (aile T2–T5, m = 4, α = 0,05)

| Test | Veri | p (ham) | p (Holm) | Holm reddi | Etki büyüklüğü |
|---|---|---|---|---|---|
| T2 McNemar (TK1+TK2) | n_çift = 2; b = 0, c = 0 | 1,000000 (kesin 1) | 1,000000 | hayır | fark 0,0000 [−0,5734; 0,5734] (Newcombe 10, eşl.) |
| T3 Fisher | SDJWT [0, 0] / JOSE [0, 2] | 1,000000 (kesin 1) | 1,000000 | hayır | OR tanımsız [0,0000; ∞] (koşullu kesin); fark — |
| T4 Fisher | 8725bis_sonrasi=1 [10, 0] / 8725bis_sonrasi=0 [14, 5] | 0,133636 (kesin 1058/7917) | 0,400909 | hayır | OR ∞ [0,5150; ∞] (koşullu kesin); fark 0,2632 [−0,0500; 0,4879] (Newcombe 10) |
| T5 binom (üst) | 6/6 | 0,015625 (kesin 1/64) | 0,062500 | hayır | oran 1,0000 [0,6097; 1,0000] |

Devralan hariç T2 (tanımlayıcı, Holm dışı): n_çift = 2, b = 0, c = 0, p = 1,000000. TK3 (tanımlayıcı): {'a': 3, 'b': 1, 'c': 0, 'd': 0}.

## Wilson %95 GA (ÖK §6.8)

| Değişken | Kategori | x/n | Oran | GA |
|---|---|---|---|---|
| L düzeyi | L0 | 5/30 | 0,1667 | [0,0734; 0,3356] |
| L düzeyi | L1 | 0/30 | 0,0000 | [0,0000; 0,1135] |
| L düzeyi | L2 | 0/30 | 0,0000 | [0,0000; 0,1135] |
| L düzeyi | L3 | 4/30 | 0,1333 | [0,0531; 0,2968] |
| L düzeyi | L4 | 21/30 | 0,7000 | [0,5212; 0,8334] |
| L düzeyi | L5 | 0/30 | 0,0000 | [0,0000; 0,1135] |
| L ≥ k (ek) | L≥1 | 25/30 | 0,8333 | [0,6644; 0,9266] |
| L ≥ k (ek) | L≥2 | 25/30 | 0,8333 | [0,6644; 0,9266] |
| L ≥ k (ek) | L≥3 | 25/30 | 0,8333 | [0,6644; 0,9266] |
| L ≥ k (ek) | L≥4 | 21/30 | 0,7000 | [0,5212; 0,8334] |
| L ≥ k (ek) | L≥5 | 0/30 | 0,0000 | [0,0000; 0,1135] |
| B1 | red | 0/2 | 0,0000 | [0,0000; 0,6576] |
| B1 | yok_sayma | 2/2 | 1,0000 | [0,3424; 1,0000] |
| B1 | dogrulama_duser | 0/2 | 0,0000 | [0,0000; 0,6576] |
| B5 | en_az_biri_gecerli | 2/6 | 0,3333 | [0,0968; 0,7000] |
| B5 | mevcut_tumu_gecerli | 1/6 | 0,1667 | [0,0301; 0,5635] |
| B5 | gerekli_kume | 0/6 | 0,0000 | [0,0000; 0,3903] |
| B5 | diger | 3/6 | 0,5000 | [0,1876; 0,8124] |
| B2 | 1 | 2/12 | 0,1667 | [0,0470; 0,4480] |
| B3 | 1 | 0/1 | 0,0000 | [0,0000; 0,7935] |
| B4_ozel_kod | 1 | 2/30 | 0,0667 | [0,0185; 0,2132] |
| B6 | 1 | 30/30 | 1,0000 | [0,8865; 1,0000] |
| Y_L4 | L4m | 2/6 | 0,3333 | [0,0968; 0,7000] |
| Y_L4 | L4c | 19/24 | 0,7917 | [0,5953; 0,9076] |

## Küme bootstrap (ÖK §6.9; B = 10.000; tohum 20260927; yüzdelik tip 7)

| Kapsam | k | Vaka | Oracle'a uymayan oran | %95 GA | Durum |
|---|---|---|---|---|---|
| tum | 30 | 102 | 0,3431 | [0,2045; 0,4608] | tamam |
| K | 30 | 84 | 0,2262 | [0,1111; 0,3452] | tamam |
| T | 6 | 18 | 0,8889 | [0,7778; 1,0000] | tamam |

## Tanımlayıcılar

- n = 31; n_eff (T1) = 30; adaptör geçersiz: SDJWT-021; Y_L4 belirsiz: yok
- Tabaka: {'COSE': 5, 'JOSE': 18, 'SDJWT': 8}; TK: {'TK1': 6, 'TK3': 24}; L4 biçimi: {'L4c': 24, 'L4m': 6}; kontrol etiketi: {'ES384': 13, 'EdDSA': 17}
- Belirsiz nedenleri: {'B1': {'uygulanamaz': 28}, 'B2': {'uygulanamaz': 18}, 'B3': {'uygulanamaz': 29}, 'B5': {'uygulanamaz': 24}, 'D_soy': {'uygulanamaz': 24}, 'F_K': {'uygulanamaz': 24}, 'F_T': {'uygulanamaz': 24}, 'surum_8725bis_sonrasi': {'uygulanamaz': 1}}; kararsız hücre (vaka): 0
- B4 satır: {'n': 2, 'medyan': 8.0, 'min': 8, 'max': 8}; devralanlar: [{'hedef_id': 'SDJWT-001', 'devraldigi_hedef': 'COSE-001'}]; pilotlar: ['JOSE-009', 'JOSE-033', 'JOSE-034', 'JOSE-065', 'JOSE-083', 'JOSE-084', 'SDJWT-015']
- REF (n dışı): yok

