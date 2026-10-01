# C3 (H6) istatistik çıktısı

- Araç: c3istat 1.0.0 · Python 3.11.16 · numpy 2.4.6 · scipy 1.17.1 · statsmodels 0.15.0
- Girdi: `ornek_n31_sentetik_hedefler.csv` · SHA-256 `4840fdc3197357eb380984810e37b2d1eaaf20b4dd12c2b118622ff027cc9c4a` · veri türü **sentetik** · şema c3-istat-girdi/1.0
- İki uygulama (kesin ↔ kütüphane): 91 uyumlu + 0 sınırda / 91; hata 0 → **GEÇERLİ**

## H6 hükmü: **BELİRSİZ**

c < X < u (ÖK §6.13). Birincil: belirsiz; duyarlılık (i): belirsiz.

## T1 (birincil, Holm dışı) ve duyarlılıklar

| Analiz | n_eff | X | c | u | P(X′ ≤ X) | P(X′ ≥ X) | Oran | Wilson %95 GA | Karar |
|---|---|---|---|---|---|---|---|---|---|
| Birincil | 28 | 12 | 9 | 19 | 0,285794 | 0,827536 | 0,4286 | [0,2651; 0,6093] | belirsiz |
| (i) belirsiz = 1 | 30 | 14 | 10 | 20 | 0,427768 | 0,707668 | 0,4667 | [0,3023; 0,6386] | belirsiz |
| (ii) belirsiz = 0 | 30 | 12 | 10 | 20 | 0,180797 | 0,899756 | 0,4000 | [0,2459; 0,5768] | belirsiz |
| Pilot hariç | 26 | 12 | 8 | 18 | 0,422509 | 0,721401 | 0,4615 | [0,2876; 0,6454] | belirsiz |
| Devralan hariç | 27 | 11 | 8 | 19 | 0,221034 | 0,876106 | 0,4074 | [0,2451; 0,5927] | belirsiz |

## T2–T5 ve Holm (aile T2–T5, m = 4, α = 0,05)

| Test | Veri | p (ham) | p (Holm) | Holm reddi | Etki büyüklüğü |
|---|---|---|---|---|---|
| T2 McNemar (TK1+TK2) | n_çift = 15; b = 7, c = 0 | 0,015625 (kesin 1/64) | 0,062500 | hayır | fark 0,4667 [0,1388; 0,6920] (Newcombe 10, eşl.) |
| T3 Fisher | SDJWT [4, 4] / JOSE [6, 11] | 0,666819 (kesin 1457/2185) | 0,967304 | hayır | OR 1,7880 [0,2378; 13,8436] (koşullu kesin); fark 0,1471 [−0,2216; 0,4839] (Newcombe 10) |
| T4 Fisher | 8725bis_sonrasi=1 [8, 5] / 8725bis_sonrasi=0 [8, 9] | 0,483652 (kesin 153233/316825) | 0,967304 | hayır | OR 1,7647 [0,3337; 10,1058] (koşullu kesin); fark 0,1448 [−0,1958; 0,4393] (Newcombe 10) |
| T5 binom (üst) | 19/30 | 0,100244 (kesin 53818201/536870912) | 0,300733 | hayır | oran 0,6333 [0,4551; 0,7813] |

Devralan hariç T2 (tanımlayıcı, Holm dışı): n_çift = 14, b = 6, c = 0, p = 0,031250. TK3 (tanımlayıcı): {'a': 1, 'b': 5, 'c': 0, 'd': 9}.

## Wilson %95 GA (ÖK §6.8)

| Değişken | Kategori | x/n | Oran | GA |
|---|---|---|---|---|
| L düzeyi | L0 | 4/30 | 0,1333 | [0,0531; 0,2968] |
| L düzeyi | L1 | 4/30 | 0,1333 | [0,0531; 0,2968] |
| L düzeyi | L2 | 6/30 | 0,2000 | [0,0951; 0,3731] |
| L düzeyi | L3 | 4/30 | 0,1333 | [0,0531; 0,2968] |
| L düzeyi | L4 | 6/30 | 0,2000 | [0,0951; 0,3731] |
| L düzeyi | L5 | 6/30 | 0,2000 | [0,0951; 0,3731] |
| L ≥ k (ek) | L≥1 | 26/30 | 0,8667 | [0,7032; 0,9469] |
| L ≥ k (ek) | L≥2 | 22/30 | 0,7333 | [0,5555; 0,8582] |
| L ≥ k (ek) | L≥3 | 16/30 | 0,5333 | [0,3614; 0,6977] |
| L ≥ k (ek) | L≥4 | 12/30 | 0,4000 | [0,2459; 0,5768] |
| L ≥ k (ek) | L≥5 | 6/30 | 0,2000 | [0,0951; 0,3731] |
| B1 | red | 7/30 | 0,2333 | [0,1179; 0,4093] |
| B1 | yok_sayma | 9/30 | 0,3000 | [0,1666; 0,4788] |
| B1 | dogrulama_duser | 14/30 | 0,4667 | [0,3023; 0,6386] |
| B5 | en_az_biri_gecerli | 3/30 | 0,1000 | [0,0346; 0,2562] |
| B5 | mevcut_tumu_gecerli | 11/30 | 0,3667 | [0,2187; 0,5449] |
| B5 | gerekli_kume | 6/30 | 0,2000 | [0,0951; 0,3731] |
| B5 | diger | 10/30 | 0,3333 | [0,1923; 0,5122] |
| B2 | 1 | 3/25 | 0,1200 | [0,0417; 0,2996] |
| B3 | 1 | 13/25 | 0,5200 | [0,3350; 0,6997] |
| B4_ozel_kod | 1 | 5/30 | 0,1667 | [0,0734; 0,3356] |
| B6 | 1 | 8/30 | 0,2667 | [0,1418; 0,4445] |
| Y_L4 | L4m | 5/10 | 0,5000 | [0,2366; 0,7634] |
| Y_L4 | L4c | 7/18 | 0,3889 | [0,2031; 0,6138] |

## Küme bootstrap (ÖK §6.9; B = 10.000; tohum 20260927; yüzdelik tip 7)

| Kapsam | k | Vaka | Oracle'a uymayan oran | %95 GA | Durum |
|---|---|---|---|---|---|
| tum | 30 | 2961 | 0,1017 | [0,0846; 0,1198] | tamam |
| K | 30 | 887 | 0,0428 | [0,0228; 0,0652] | tamam |
| T | 30 | 1187 | 0,1542 | [0,1177; 0,1941] | tamam |

## Tanımlayıcılar

- n = 31; n_eff (T1) = 28; adaptör geçersiz: S-JOSE-04; Y_L4 belirsiz: S-JOSE-06, S-SDJWT-03
- Tabaka: {'COSE': 5, 'JOSE': 18, 'SDJWT': 8}; TK: {'TK1': 6, 'TK2': 9, 'TK3': 15}; L4 biçimi: {'L4c': 20, 'L4m': 10}; kontrol etiketi: {'Ed25519': 1, 'EdDSA': 29}
- Belirsiz nedenleri: {'B2': {'uygulanamaz': 5}, 'B3': {'uygulanamaz': 5}, 'Y_L4': {'kanit_kurali': 1, 'oracle_uyusmazligi': 1}}; kararsız hücre (vaka): 39
- B4 satır: {'n': 5, 'medyan': 20, 'min': 9, 'max': 55}; devralanlar: [{'hedef_id': 'S-SDJWT-05', 'devraldigi_hedef': 'S-JOSE-07'}]; pilotlar: ['S-JOSE-01', 'S-SDJWT-02']
- REF (n dışı): ['S-REF-01', 'S-REF-02']

