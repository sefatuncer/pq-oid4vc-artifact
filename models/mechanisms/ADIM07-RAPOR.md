# Adım 7 raporu: mekanizma modelleri (yürütücü kapanışı, 01.10.2026)

**Koşum:** Tamarin çalışması, 26.09.2026 13:43'ten itibaren. Çapa 8 (`2d16592`, 13:39) beklentileri koşumdan önce sabitledi; `on_kayit_varyantlar.tsv` SHA-256 `ebb87d64…` her koşumun başında denetlendi.
**Kapanış:** Yürütücü, 01.10.2026. 26.09 koşumu son birkaç ek satırda kesilmişti. `betik/calistir.sh` kaldığı yerden sürdürüldü (aynı imaj, aynı model dosyaları).
**Tablolar:** `sonuc/tablolar.md` (betikten); ham veriler `sonuc/ozet.csv`, `sonuc/karsilastirma.csv`, `sonuc/ham/`.

## 1. Kabul ölçütleri

| Ölçüt (IS-PLANI 7.6) | Sonuç |
|---|---|
| 1. Her sınıf için kesin sonuç | ✓ M-a, M-b/A.3.2.2, M-b0, M-d, M-e, M-e′, M-f (çekirdek, 3b, taşıyıcılar), M-g (sheffer; EK [8a]), M-h (reddy, vicente). **762 lemma koşumunun hepsi 1. basamakta kapandı**; "kapanmadı" yok |
| 2. Sadeleştirilmiş M-f için G5'in üç biçimi, yol dahil | ✓ `MF_cekirdek`: G5_untimed / G5_migrated / G5_timed / no_rollback ve G5_path_* biçimlerinin hepsi **verified** |
| 2a. Beklentiler koşumdan önce çapada | ✓ Çapa 8 13:39 < ilk koşum 13:43 |
| 2b. Görev 3b: 3 kapsam × 3 saldırı; M-h'nin iki varyantı | ✓ (§2.2, §2.4) |
| 3. A3 boyutları | ✓ Taşıyıcı ikamesi (A3-7), çevrimdışı ek 2×2 (EK [8b]); kural düzeyindeki boyutlar 5A'da |
| 4. Görev 3a'nın üç sorusu | ✓ (§2.4) |
| 6. İyi biçimlilik 0; ≤10 dk; ≤12 GB | İyi biçimlilik **762/762 temiz**; bellek en çok 5,4 GB. Süre: bir koşum 26.09'da 7.024 s duvar süresi kaydetti (`MF_tas_federasyon_bayat` / `M_weak_path_forgery`). 01.10'da aynı komutla 600 s sınırı altında yeniden koşuldu: **78 s, aynı hüküm (verified)**. Kayıt, yerel makinenin askıya alınmasından kaynaklanan bir duvar saati yapaylığı olarak değerlendirildi (sapma notu) |
| Beklenti uyumu | **760/762** (§3) |

## 2. Sonuçlar (G5 biçimleri; F = iz, V = kanıt)

### 2.1 İstek yönü ve meta veri

| Mekanizma | Sonuç | Yorum |
|---|---|---|
| M-b0 imzasızlaştırma (HAIP + DC API takdiri) | G5'in üç biçimi F | Taban: imzasız istek kabul edildiği sürece RP beklentisi taşınamaz |
| M-a kimliği doğrulanmamış müzakere (#791) | Üç biçim F; `M_downgrade_s1` V | Ağ saldırganı yetenek başlığını düşürür; CRQC klasik eski anahtarı sahteler |
| M-b / OID4VP A.3.2.2 çoklu imza ("biri yeter") | Üç biçim F | En zayıf güven çerçevesi belirler. **Final spesifikasyonda** (OID4VP 1.0) doğrulama semantiği tanımsız (T273) |
| M-d PQ kayıt kanalı | Göç F (ön kayıtlı beklenti F) | PQ imzalı kayıt güncellemeleri yeniden oynatılabilir; göç öncesi "none" kaydı göçten sonra oynatılır |
| M-e "supported" (PQ imzalı, taze) | Zamansız ve göç F; zamanlı V; no_rollback **F (beklenen V)** | "Supported ≠ required" |
| M-e′ "required" (PQ imzalı, taze) | Zamansız, göç, zamanlı V; no_rollback **F (beklenen V)** | Koşullu kanıt |

### 2.2 M-f ve beklenti kapsamı (görev 3b)
- **`yol_sinifi`:** üç saldırıya karşı bütün G5 ve yol biçimleri V. Saldırılar: farklı adlı alternatif CA, aynı adlı CA, klasik kök + PQ ara.
- **`anahtar`:** G5 V, yol biçimleri F.
- **`yaprak_alg`:** G1 F.
- **Sonuç:** Beklenti, yaprak ya da anahtar düzeyinde değil, **yol sınıfı** düzeyinde bağlanmalıdır. Bu, ad ya da yaprak bağlamasının anahtar değişimi döneminde atlatıldığını gösterir (5A R7h ile tutarlı).

### 2.3 Taşıyıcı ikamesi (A3-7)

| Taşıyıcı | Sonuç |
|---|---|
| TL/LoTE, çekilen ve güncel | Hepsi V |
| OpenID Federation, PQ ara | Hepsi V |
| TL önbelleği | Göç ve zamanlı biçim F |
| WRPRC faz 0 | Hepsi F |
| WRPRC faz 1 | Zamansız V; diğerleri F |
| Federation, klasik ara | Hepsi F |
| Federation, bayat `trust_chain` | Zamansız V; diğerleri F |
| `crit` başlığı | Hepsi F |

### 2.4 M-h ve görev 3a
- **reddy tipi ve vicente tipi taahhüt ekleri:** klasik zincirde ve üç saldırının hepsinde G5'in üç biçimi F.
  - (i) Taahhüt yalnız klasik zincirde taşınıyorsa korumuyor.
  - (ii) Alternatif ya da aynı adlı CA ile taahhütsüz sertifika kabul ettiriliyor; reddy + ad bağlaması da farklı adlı CA'ya karşı F.
  - (iii) M-f'nin varlık başına `yol_sinifi` beklentisi bu saldırıları kapatıyor (§2.2).
- **M-g / sheffer zincir politikası [8a]:**
  - "anahtar PQ" okumasında üç saldırının hepsi F.
  - "imza PQ" okumasında no_rollback ve G1_learned V, ama G5 zamansız, göç ve zamanlı F.
  - `M_cache_cleared` (önbellek sildirme) "anahtar" okumasında V.

### 2.5 Çevrimdışı ek (EK [8b], 2×2)
- Dört tanımın dördünde zamansız ve zamanlı V, göç F.
- Yol no_rollback yalnız **geniş tekdüzelikte** V.
- Yol-zamanlı yalnız **beklenti düzeyi sunset'te** V.
- İkisi birlikte (`EK_mf_yola_duyarli`) yol biçimlerinin üçünü de V yapıyor. Bu, M-f-TANIM'daki yola duyarlı tanımın gerekçesi.

## 3. Beklenmeyen iki sonuç (2/762) — açıklandı

`ME_signed_fresh` ve `MEP_signed_fresh` için `no_rollback`: beklenen V, gözlenen F (15 adım).
- 01.10'da bağımsız yeniden koşum aynı hükmü ve adım sayısını verdi (`sonuc/yeniden_kosum_0110/`).
- **İz:** Göç etmemiş (legacy) ihraççının meta verisi kendi klasik anahtarıyla imzalı (`Issuer_Setup_Legacy`: `!MetaSk($L, ~kc)`). CRQC bu anahtarı çıkarınca saldırgan önce sahte bir "retired"/"pq_required" yanıtı (doğrulayıcı beklentiyi "görür"), sonra sahte bir "none" yanıtı üretir; klasik kabul gerçekleşir.
- **Keşifsel sınama (ön kayıt dışı; `kesif/me_gocmus/`):** Lemma yalnız göç etmiş varlıklarla sınırlandı (`no_rollback_migrated`). Sonuç: **M-e'de verified (38 adım), M-e′'de verified (45 adım).**
- **Yorum:** Beklentiyi taşıyan nesne, beklentinin koruduğu varlığın kendi (kırılabilir) anahtarıyla imzalanırsa beklenti koruma sağlamaz. Bu, öz-beyanlı taşıyıcının döngüselliğidir.
  - Ön kayıtlı beklentiyi yazan çalışma meta veriyi her ihraççı için PQ imzalı varsaymıştı. Model ise göç etmemiş ihraççıyı da kapsıyor.
  - Hüküm **model kusuru değil, kapsam farkı.** Bağımsız teyit: `..\Yeni\makale1` b4 (farklı model, aynı olgu).
- **Makalede:** M-e ve M-e′ için "koşullu kanıt yalnız göç etmiş ihraççıda; öz-imzalı meta veri, göç etmemiş varlık için beklenti taşıyamaz" diye raporlanır.

## 4. H3 ve bilimsel kapı için çıkarımlar
- H3'ün öngörüsü tuttu: M-a, M-b (A.3.2.2) ve M-b0 iz verdi. Ö2 gereği bu izler tek başına (2c′) sayılmaz. (2c) için A.3.2.2'nin **final** spesifikasyonda olması önemlidir.
- Sadeleştirilmiş M-f, `yol_sinifi` kapsamıyla bütün G5 biçimlerinde kanıtlandı. Kapsam boyutu bariz olmayan sonuç adayıdır (ad ya da yaprak bağlamanın atlatılması; reddy ve vicente taahhüt eklerinin klasik zincirde korumaması).
