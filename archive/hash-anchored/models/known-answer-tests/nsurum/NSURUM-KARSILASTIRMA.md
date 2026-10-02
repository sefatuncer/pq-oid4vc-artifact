# KAT beklenen değerleri — N-sürüm karşılaştırması (yürütücü, 25.09.2026)

**Amaç:** ÖK §4.19 ve KAT-SPEC §5.3. İlk çalışmanın beklenen tabloları (`literatur/analiz/KAT-SPEC.md` (d) bölümleri; SHA-256 `f8ba9a51…8b80`) ile kör çalışmanın bağımsız türetmesi (`kor-beklenen/BEKLENEN-KOR.tsv`, `180a655a…a4bb`, commit `f012841`) karşılaştırıldı.

**Zamanlama:** Karşılaştırma ve çözüm, Adım 6'nın hiçbir ASP ya da Tamarin koşumundan ÖNCE yapıldı. Adım 3'ün çekirdeği (`cekirdek.lp`) henüz tamamlanmadı.

## Sonuç (`kat_nsurum.py` → `kat_nsurum.tsv`)

| Durum | Sayı |
|---|---|
| Karşılaştırılan anahtar (hücre × sütun) | 141 |
| **Eşit** | **138** |
| Farklı | **0** |
| Kör çalışma "belirsiz" | 3 (K2d-01/02/03, Tamarin sütunu) |
| Yalnız bir tarafta | 0 |

**Eşleme notları (ilk çalışmanın birleşik hücreleri açılırken):**
- K2a-05/06 "aynı" → accept_classical / accept_classical (K2a-01/02 ile aynı örüntü; Kim Tablo IV).
- KAT-3b'de ilk çalışmanın Tamarin beklentisi = pilot sütunu (SALDIRI ↔ falsified, YOK ↔ verified).
- `qday=200` beklentisi "6/6 attack = YOK" düzyazısından.

## Belirsizliğin kaynağa dönülerek çözümü (K2d Tamarin)

- **Neden belirsizdi:** Yürütücünün redaksiyon sözlüğü KAT-2d'nin Tamarin lemmasını adlandırmadı (yürütücü hatası; beklenen değer değil, spesifikasyon ayrıntısı eksikti). K2d bayraklarında `CRQC` yok, yani saldırgan M1. Kör çalışma üç aday lemma için üç değer örüntüsü verdi (`BELIRSIZ.md` §A1).
- **Kaynak:**
  - KAT-SPEC §3(c) taslağı lemmaları açıkça ayırıyor: `cert_authentic` = "M2: sertifika kimlik doğrulaması" (K2b'nin CRQC'li hücreleri); `no_silent_promotion` = "M1: hibrit niyet — kabul edilen her anahtar hibrit olarak ihraç edilmiş olmalı".
  - K2d, Kim vd. Tablo VI'yı (P0–P3) M1 altında yeniden üretir: "Under M1, P1 provides no more protection than P0: the adversary withholds the post-quantum evidence, P1 tolerates the absence, and the result is accept-classical".
- **Çözüm:** K2d Tamarin lemması = `no_silent_promotion`. Beklenen: K2d-01 (V_IGNORE) **falsified**, K2d-02 (V_ENFORCE_IF_PRESENT) **falsified**, K2d-03 (V_REQUIRE) **verified**. Bu, ilk çalışmanın değerleriyle ve kör çalışmanın en olası saydığı (b) okumasıyla ("kabul ⇒ PQ kanıtı / hibrit ihraç") aynı.
- **Sonuç:** 141/141 anahtarda üzerinde uzlaşılmış bir beklenen değer var.

## Önceden kaydedilen alternatif okumalar (risk notu)

Kör çalışma, değerin yoruma bağlı olduğu hücreleri ve alternatif okumada çıkacak değeri `kor-beklenen/BELIRSIZ.md` §B'ye yazdı:
- zaman sabitleri (K1-05, K1-07, K1-09, K1-13, K1-14);
- bütünlük testinin kapsamı (K1-04, K1-06, K1-11);
- K1-14 ek çapa, K1-15 `allpresent`;
- K2a-10;
- K2d-05 (P3 ilk temas);
- KAT-3a o6, o8, o10;
- KAT-3b V4.

**Kural (ÖK §2C.1):**
- Kapı kararı yukarıdaki üzerinde uzlaşılmış değerlerle verilir. Bir hücre koşulup farklı çıkarsa test yedekle değiştirilmez; başarısızlık raporlanır ve model hatası aranır.
- Önceden yazılmış alternatif okuma yalnız tanıda (model hatası mı, spesifikasyon yorumu mu) kullanılır ve raporlanır. Sonradan yeniden yorum sayılmaz, çünkü koşumdan önce kaydedildi.

**Kimlikler:**
- `kat_nsurum.py` ve `kat_nsurum.tsv`: bu klasörde, `SHA256SUMS`.
- Uzlaşılmış beklenen değerlerin tek kaynağı: `kat_nsurum.tsv` (`ilk_ajan` sütunu; K2d Tamarin satırları yukarıdaki çözümle).
