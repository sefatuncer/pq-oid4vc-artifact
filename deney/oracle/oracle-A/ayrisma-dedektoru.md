# Ayrışma dedektörü — tasarım (Oracle A önerisi; Adım 10'da koşulur)

> **Dayanak:**
> - ÖK §4.20: "Kütüphaneler arası sonuçlar çoğunluk oyu olarak değil, ayrışma dedektörü olarak kullanılır."
> - IS-PLANI Adım 9 görev 6: "aynı vakada farklı karar veren hedeflerin listesi; çoğunluk oyu kullanılmaz (Adım 10'da koşulur)".
> - IS-PLANI Adım 10 görev 10: `ayrisma.csv`.
>
> **Bu belge yalnız tasarımdır.** Hiçbir hedef ölçülmedi; aşağıdaki örnekler **uydurma veri değil, biçim örneğidir** ve gerçek hedef adı taşımaz.

## 1. Amaç ve ilke

- **Amaç:** Aynı test hücresinde farklı karar veren hedefleri **listelemek**. Liste şu işlere yarar:
  - olası uygulama hatalarını,
  - spesifikasyon belirsizliklerini,
  - PQ'ya özgü ayrışmaları öne çıkarmak.
- **Çoğunluk oyu YOK.** Grup büyüklükleri raporlanır, ama hiçbir karar "çoğunluk öyle dediği için doğru" sayılmaz. Tek başına kalan hedef "yanlış" diye işaretlenmez.
- **Doğruluk yalnız oracle'dan gelir** (A ve B'nin uzlaştığı hücreler; ÖK §4.15). Dedektör oracle'dan bağımsız çalışır. Oracle ile ilişki yalnız **yan bilgi** olarak yazılır.
- **Betimseldir:** Önceden kayıtlı testlere (T1–T5) ve Holm ailesine girmez.

## 2. Girdiler

| Girdi | Kaynak |
|---|---|
| Hedef kararları | `deney/kosum/kosu/r{1,2,3}/<hedef>.jsonl` (`adaptor-sozlesme.md` §3) |
| Oracle A, Oracle B | `deney/oracle/oracle-A/karar.tsv`, Oracle B'nin karar dosyası (yapılandırma adları eşleme tablosuyla hizalanır; NOTLAR N-12) |
| TK ataması, kontrol etiketi | `deney/kosum/tk-atamasi.csv` |
| L düzeyleri, L4 biçimi | `deney/kosum/L-duzeyleri.csv` |
| Devir kümeleri | `adaptor-sozlesme.md` §7 |
| Birincil/ikincil | `karar.tsv` `sinif` sütunu (ÖK §2G m.4) |

## 3. Hücre ve karar

- **Hücre** h = (vektör, politika, kol, sdjwtvc_sürüm).
- **Kontrol kolunda etiket normalleştirme:** `kontrol-Ed25519` kolundaki `…-ED25519` eşleri, `kontrol-EdDSA`'daki kaynak vektörle aynı hücreye eşlenir. Eşleme `insa.v1_esi` ya da `insa.etiket_esi` alanıyla yapılır. Böylece yedek etiketi kullanan hedef, `EdDSA` kullanan hedefle karşılaştırılabilir. Kullanılan etiket hücre satırında ayrıca gösterilir.
- **Hedefin hücre kararı** k_t(h):
  - üç koşuda aynıysa o değer;
  - değilse `kararsız`.
  - `uygulanamaz` (B6) ve adaptörü geçersiz hedefler hücreden çıkarılır ve ayrı listelenir.

## 4. Algoritma

```
girdi: K[t][h] (3/3 kararlı ya da "kararsız"), ORACLE_A[h], ORACLE_B[h], TK[t][kol], DEVIR = {küme: {hedefler}}
çıktı: ayrisma.csv, ayrisma_ozet.md

for h in sırala(tüm hücreler):                       # vektör kimliği, politika, kol sırası; belirlenimci
    T = {t : K[t][h] ∉ {uygulanamaz}, t adaptör-geçerli}
    grup_karar  = böl(T, anahtar = K[t][h])            # 4 değer + "kararsız"
    grup_kabul  = böl(T, anahtar = kaba(K[t][h]))       # kaba: accept-* → "kabul", reject, indeterminate, kararsız
    if |grup_kabul anahtarları| ≥ 2:     tür = "karar-ayrışması"
    elif |grup_karar anahtarları| ≥ 2:   tür = "kabul-türü-ayrışması"    # accept-classical ↔ accept-hybrid
    else: continue                                     # ayrışma yok
    oracle = ORACLE_A[h] if ORACLE_A[h] == ORACLE_B[h] else "A≠B (belirsiz)"
    for küme in DEVIR: if küme ⊆ T and |{K[t][h] : t ∈ küme}| ≥ 2: küme_içi = True
    pq_ozgu = (kol ∈ tedavi) and (eş kontrol hücresinde karar-ayrışması YOK)   # §5
    yaz(h, grup_karar, tür, oracle, küme_içi, pq_ozgu, TK dağılımı, sinif)
```

- **Kaba karar:** Tür önce karar düzeyinde (kabul ↔ red) belirlenir. Kabul türü farkı ayrı bir türdür. Böylece "PQ doğrulamadan kabul" ile "PQ doğrulayarak kabul" ayrımı kaybolmaz.
- **Devir kümeleri:** Hedefler hem tek tek hem küme olarak gösterilir.
  - Küme içinde ayrışma varsa, aynı doğrulama çekirdeğini paylaşan iki birim farklı karar vermiş demektir. Örnek: WalletFramework ↔ IdentityModel. Bu, adaptör ya da yapılandırma farkına işaret eder ve adaptör denetimine gider.
- **Kararsız hedefler:** Hücrede ayrı bir grup olarak listelenir (ÖK §6.11 "kararsız → belirsiz").

## 5. Ayrışma türleri ve öncelik (triyaj sırası; oy değildir)

Bu sıra yalnız hangi ayrışmanın önce inceleneceğini belirler. Hiçbir hedefin kararını değiştirmez.

1. **Oracle belirli, en az bir hedef sapıyor.** Hücrede oracle A = B ve belirli; en az bir grup oracle'dan farklı. Olası uygulama hatası. Birincil hücreler önce gelir.
   - Karar oracle'dan bağımsız verilir: oracle'la uyumlu grup küçük de olsa "doğru" o gruptur.
2. **PQ'ya özgü ayrışma.** Tedavi kolu hücresinde karar ayrışması var, ama aynı vakanın kontrol kolu hücresinde yok. Örnek: K1'de kontrol kolunda bütün hedefler aynı karar veriyor, composite kolunda gruplar ayrışıyor. T2'nin (F_T = 1 ∧ F_K = 0) hücre düzeyindeki karşılığıdır. TK1/TK2/TK3 dağılımıyla birlikte raporlanır.
3. **Oracle belirsiz, hedefler ayrışıyor.** Spesifikasyon belirsizliğinin **ampirik kanıtı** (`BELIRSIZ.md` B-1…B-6). Örnekler:
   - K5 (S/Y),
   - VP05/VP07 (`sd_hash`),
   - CMP05/CMP06 (DER katılığı),
   - X5C10 (kid ↔ x5c).

   Dış bildirim adaylarıyla (DB-1, DB-2) ilişkilendirilir.
4. **Kabul türü ayrışması.** Bütün hedefler kabul ediyor, ama bir kısmı PQ imzayı doğrulamadan kabul ediyor. Tipik olarak TK3 ile TK1/TK2 ayrımıdır; tanımlayıcı raporlanır.
5. **MR4 hedef içi ayrışması.** Bu, hedefler arası ayrışma değildir, ama aynı tabloda gösterilir: bir hedef kaynak vektörde ve permütasyon eşinde farklı karar veriyor. ÖK §2B m.8'deki ayrı MR4 bayrağıdır. VP05-SIRA-ters MR4 kapsamı dışındadır.

## 6. Çıktı şeması

### `ayrisma.csv` (hücre başına bir satır; yalnız ayrışan hücreler)

| Sütun | Açıklama |
|---|---|
| `hucre` | `<vektor_id>|<politika>|<kol>|<sdjwtvc_surum>` (etiket normalleştirilmiş) |
| `vektor_id`, `politika`, `kol`, `sinif`, `vaka` | `karar.tsv`'den |
| `tur` | `karar-ayrismasi` / `kabul-turu-ayrismasi` |
| `oncelik` | §5'teki 1–5 |
| `oracle_A`, `oracle_B`, `oracle_uzlasi` | uzlaşı yoksa `A≠B (belirsiz)` |
| `gruplar` | JSON: `{"reject": ["JOSE-…", …], "accept-classical": […], "kararsiz": […]}` |
| `grup_boyutlari` | JSON: `{"reject": 7, "accept-classical": 3}`. Yalnız bilgi amaçlı, oy değil |
| `tk_dagilimi` | JSON: grup başına TK1/TK2/TK3 sayısı |
| `l4_bicimi` | grup başına L4m/L4c |
| `devir_kume_ici` | `evet`/`hayir` + küme adı |
| `kontrol_etiketi` | EdDSA/Ed25519 grup dağılımı (kontrol kolunda) |
| `hariç` | uygulanamaz (B6) ve adaptör geçersiz hedefler |
| `not` | serbest metin; ör. "BELIRSIZ B-2" |

### `ayrisma_ozet.md`

- Tür ve öncelik başına hücre sayısı.
- Birincil ve ikincil ayrımı.
- PQ'ya özgü ayrışmaların listesi.
- Devir kümesi içi ayrışmalar.
- Oracle belirsizliği ile ayrışmanın örtüştüğü hücreler.

### Biçim örneği (uydurma değil; yer tutucu adlar)

```
hucre=T7P_plus_kayitsiz|L4|tedavi-ML-DSA-65|-13  tur=karar-ayrismasi  oncelik=3
oracle_A=indeterminate  oracle_B=<B>  gruplar={"reject":["<hedef-1>"],"accept-hybrid":["<hedef-2>"],"accept-classical":["<hedef-3>"]}
not: BELIRSIZ B-1 (S/Y). accept-classical grubu MR2 ihlali adayıdır (PQ imza doğrulanmadan kabul)
```

## 7. Doğrulama (Adım 9 görev 8 ile birlikte; kütüphanesiz)

Dedektör betiği Adım 10'dan önce **sentetik** hedef kararlarıyla sınanır. Hiçbir hedef koşulmaz. Sınama vakaları:
1. Bütün hedefler aynı → 0 satır.
2. İki hedef, K3'te accept-classical ↔ reject → 1 satır, `karar-ayrismasi`, öncelik 1.
3. Bütün hedefler kabul ediyor, biri accept-classical → `kabul-turu-ayrismasi`.
4. Kontrol kolunda ayrışma yok, tedavi kolunda var → `pq_ozgu` işareti.
5. Devir kümesinin iki üyesi farklı → `devir_kume_ici = evet`.
6. `-ED25519` eşleri normalleştirilince aynı hücreye düşer.
7. B6 hedef hücreden çıkar.
8. Aynı girdiyle iki koşu bayt-aynı çıktı verir.

**Belirlenimcilik:** sıralama sabittir, rastgelelik yoktur. Betik özeti dondurma paketine girer (ÖK §10).
