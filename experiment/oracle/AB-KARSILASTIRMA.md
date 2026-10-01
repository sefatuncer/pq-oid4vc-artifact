# Oracle A ↔ B karşılaştırması (yürütücü, 25.09.2026)

**Girdiler:**
- `oracle-A/karar.tsv` `dd21fdba…` (858 satır; 11 yapılandırma).
- `oracle-B/karar.tsv` `2cca1295…` (732 satır; L4/P0/P2 ve sürüm ekleri).
- B, A bitmeden commit edildi (`037e468` < `be1904f`). İkisi de diğerinin klasörünü okumadığını beyan etti.

**Anahtar:** (vektor_id, politika, kol). Ortak yapılandırmalar L4 ve P0.

| Yapılandırma | Kapsam | Ortak | Eşit | En az biri belirsiz | Kesin farklı |
|---|---|---|---|---|---|
| L4 | iki oracle'da da birincil | 53 | 48 | 4 (K5: A temel L4'te belirsiz) | **1** |
| L4 | tümü | 138 | 102 | 40 | 1 |
| P0 | iki oracle'da da birincil | 20 | 16 | 0 | **4** |
| P0 | tümü | 61 | 41 | 0 | 20 |

**Kesin farkların hepsi, iki oracle'ın da ÖK'de tanımsız diye işaretlediği noktalardan geliyor:**
1. **X5C04 (K8), composite kolu, L4:** A = accept-hybrid, B = reject. Composite kolunda K8/K9'un politikası tanımsız (A N-3, B N3). Uyarlanmış vektör ML-DSA-65 imzalı; composite kolunun izin kümesinde bu algoritma yok.
2. **T1P, T1C, T7P, T7C, P0:** A = accept-classical, B = accept-hybrid. "accept-hybrid / accept-classical" ayrımının tanımı yok (A N-5, B N1). P0'da PQ imzası da geçerliyken kabulün sınıfı belirsiz.
3. **K5 (fazladan imza):** A temel L4'te belirsiz dedi; S/Y alt yapılandırmaları ekledi. B sıkı okumayla red dedi (A N-1, B N4).

**Sonuç:**
- Rastgele hata görülmedi. Uyuşmazlıklar ÖK'deki üç tanım boşluğuna yoğunlaşıyor.
- ÖK §4.20 gereği bu hücreler "belirsiz" sınıfına girer. Tanımlar ÖK'ye yazılıp (dondurmadan ÖNCE) her iki oracle aynı tanımla yeniden türetilirse kapanır.
- Oracle'ların ortak kararlaştırılacak maddeleri: `KARAR-NOTLARI.md` (A: N-0…N-12; B: N1…N17).
