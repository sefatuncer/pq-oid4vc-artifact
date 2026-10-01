# Adım 6: Bilinen-cevap testleri (KAT), rapor

- **Tarih:** 26.09.2026 · **Çalışma:** asp (Adım 6)
- **Klasör:** `model\bilinen-cevap\`. Yalnız şunlara yazıldı: `ESLEME.md`, `dnssec\`, `x509\`, `smime\`, `SONUC.md`, `ADIM06-RAPOR.md`, `SHA256SUMS`. `kor-beklenen\` ve `nsurum\` salt okunur (§2.4'teki geçici kaza dışında).
- **Beklenen değerlerin tek kaynağı (SABİT, değiştirilmedi):** `nsurum\kat_nsurum.tsv` (`3609f793…2aec`), `ilk_ajan` sütunu. K2d Tamarin lemması `no_silent_promotion` (ÖK §2H.1). Çapa 8: commit `2d16592`.
- **Tek çekirdek:** KAT hücreleri yalnız `model\asp\cekirdek.lp` ile bu klasördeki örnek dosyalarıyla koşuldu. `cekirdek.lp` SHA-256 = `a32372a7c646274ce672c9586e25b34f75f4febb2f966596cc97e7afb89e0b38` (commit `45cbd0f` ile bayt-aynı); koşumdan önce ve sonra aynı.
- **Sonuç (ayrıntı `SONUC.md`):**
  - **İlk koşum (commit `e4c1090`):**
    - V-d 2/3: KAT-2 ve KAT-3 GEÇTİ, **KAT-1 KALDI**.
    - `nsurum` 141 anahtarın 140'ı beklenen değerde; ASP 109/109, Tamarin 31/32, ASP–Tamarin 31/32, mutasyonlar 12/12.
    - Tek uyumsuzluk: K1-11 Tamarin. Tanı: KAT-SPEC §2(c) Tamarin taslağında bütünlük testinin kapsam hatası (§5).
  - **Düzeltme sonrası (yürütücü kararı 26.09.2026; §8):**
    - KAT-1 Tamarin v2 ile yeniden koşuldu; **KAT-1 GEÇTİ**: Tamarin 15/15, ASP–Tamarin 15/15, mutasyonlar 5/5.
    - V-d **3/3**; `nsurum` 141/141.
    - Yalnız K1-11 değişti.
    - İki koşum birlikte sunulur.

## 1. Hazırlık dondurması (ilk koşumdan ÖNCE)
- `SHA256SUMS` (o anki hâli): 319 dosya. Kapsam:
  - ESLEME.md;
  - taban ve örnek dosyaları, hücre ve mutasyon tabloları, Tamarin modelleri, koşucular ve değerlendiriciler;
  - iyi biçimlilik ve alıntı kanıtları;
  - dış referanslar: `../asp/cekirdek.lp`, `nsurum/kat_nsurum.tsv`, pilot aslı `b079cbbb…bd47`.
- **Hazırlık kimliği** = o dosyanın SHA-256'sı: `2d23e35b146d63856c9936c963cd6fffd7526b24008e579c5c8f3b951a85024b`, **2026-09-26T11:07:00Z**. O ana dek hiçbir KAT hücresi koşulmamıştı.
- Donmuş liste bayt-aynı olarak `dnssec\HAZIRLIK_SHA256SUMS`'ta saklanır. Üst düzeyde yalnız `SHA256SUMS` yazılabildiği için bu klasörde duruyor; üç KAT'ı kapsar.
- Son `SHA256SUMS` bütün dosyaların son hâlini kapsar.

## 2. Hazırlık bulguları
1. **Pilot model iyi biçimli değil (KAT-3b).**
   - Hata: "Fact multiplicity issues". `Qday` adı hem eylem hem kalıcı olgu; altı yapılandırmanın altısında görülüyor.
   - Karar koşumdan önce verildi (ESLEME §4.5):
     - kapı hücreleri tek sözcük farklı iyi biçimli kopyayla koşuldu (`smime/weakest_link_wf.spthy`; eylem adı `Qday()` → `QdayOlayi()`; eylem hiçbir lemmada yok);
     - pilotun aslı ek olarak koşuldu.
   - **Sonuç:** iki model aynı hükmü ve aynı adım sayısını verdi (6/6). Onay yine de yürütücüde.
2. **Tamarin iyi biçimlilik (`--prove` yok):**
   - KAT-1 16/16;
   - KAT-2 12/12;
   - KAT-3a 4/4;
   - KAT-3b iyi biçimli kopya 6/6;
   - hepsinde uyarı 0.

   Pilotun aslı 6/6 uyarılı. Koşumdaki her lemma çağrısı iyi biçimliliği yeniden denetledi: kapı modellerinde 0 uyarı.
3. **Alıntılar:** 21/21 birebir bulundu.
   - 20'si yalnız boşluk normalleştirmesiyle bulundu; A2-7, PDF çıkarımındaki tire kaybı nedeniyle `tire_sil` adımıyla.
   - RFC metin özetleri MANIFEST ile aynı. Makale metinlerinin özetleri hazırlıkta kaydedildi; MANIFEST yalnız PDF özetlerini tutuyor.
4. **Şeffaflık (kaza):**
   - Ne oldu: Sözdizimi denetiminde `*/*.py` deseni `nsurum/kat_nsurum.py`'yi de derledi ve `nsurum/__pycache__/` oluştu (14:06).
   - Ne yapıldı: Aynı dakika içinde silindi. `nsurum/SHA256SUMS` üç dosyada OK; git durumu temiz. Beklenen değerlere dokunulmadı.
   - Benzer biçimde bir liste dosyası yanlışlıkla `/tmp`'ye yazıldı ve silindi.
5. **Tamarin bekleme kuralı:**
   - Durum: Tamarin çalışmasının Adım 7 işleri arka arkaya koşuyordu.
   - Uygulama: Koşucu yalnız ≥ 2 GiB bellek kullanan bir Tamarin konteyneri varken bekler. KAT işleri küçüktür (en çok 148 MiB), hafif işlerle aynı anda koşabilir ("aynı anda tek AĞIR iş").

## 3. Koşum sırası
1. **ASP (çapa 8 sonrası):**
   - Sonuçlar: KAT-1 15/15, KAT-2 40/40, KAT-3 54/54 hücre değeri; mutasyon koşularının hepsi beklenen yönde; `kat3a_fail` boş, `model_gap` = {o8}.
   - Çekirdek: özeti üç koşucuda önce ve sonra `a32372a7…0b38`.
   - Süre: en uzun hücre 3,5 ms.
2. **Tamarin, ilk deneme:** ilk çağrıda koşucu hatasıyla durdu; HİÇBİR Tamarin sonucu üretilmedi (§4.1).
3. **Tamarin, yeniden koşum:**
   - KAT-1: 15 hücre + 7 mutasyon satırı;
   - KAT-2: 8 + 2 mutasyon + 3 ek;
   - KAT-3: 9 + 1 mutasyon + 6 ek (pilot aslı).

   Her satırda `executable` + hedef lemma çalıştı; hepsi merdivenin ilk basamağında kapandı. Uyumsuzluk: yalnız K1-11.
4. **Değerlendirme:** her klasörde `degerlendir.py`, `sonuc/KAT_OZET.{json,md}` üretir; `SONUC.md` bunların birleşimidir.
5. **Tanı (SONUÇ GÖRÜLDÜKTEN SONRA; kapı değeri değil):** `dnssec/tani/` (§5).

## 4. Dondurma sonrası değişiklikler ("sonuç görüldükten sonra" etiketi)
1. **`{dnssec,x509,smime}/tamarin_kos.py`, 81. satır.**
   - Sorun: Konteynerdeki çıktı yolu Windows ayırıcısıyla kuruluyordu. `os.path.join('sonuc','tamarin_ham')` → `sonuc\tamarin_ham`; bu, Linux yolunda geçersiz. Bu yüzden ilk Tamarin çağrısı çıktı üretemedi.
   - Düzeltme: `cikti_dizin` → `cikti_dizin.replace('\\', '/')`.
   - Etki: Yalnız yol biçimi; anlam, bayraklar, lemmalar ve okuma kuralı değişmedi. Değişiklik anında Tamarin sonucu henüz yoktu.
2. **`{dnssec,x509,smime}/degerlendir.py`, katı mutasyon ölçütü.**
   - Değişiklik: İlk sürüm bir mutasyon satırını "mutasyonlu değer beklenen değerde" ise döndü sayıyordu. Yeni sürüm ayrıca "mutasyonsuz temel koşunun gözlenen değerinden farklı" olmasını ister (KAT-SPEC §6: "dönmeli").
   - Neden: MUT01'in Tamarin K1-11 satırı yüzünden. K1-11 mutasyonsuz hâlde de falsified olduğundan, ilk sürüm bunu yanlışlıkla "döndü" sayardı.
   - Etki: Değişiklik yalnız öldürülen mutasyon sayısını azaltabilir. Sonuç değişmedi: MUT01'i K1-04 döndürüyor; 12/12.
3. **Eklenen tanı dosyaları:** `dnssec/tani/KAT1_DNSSEC_tani.spthy`, `tani_kos.py`, `sonuc.csv` (§5). Dondurulmuş hiçbir dosyaya dokunmaz; `tani_kos.py`, `tamarin_kos.py`'yi değiştirmeden içe aktarır.
4. **Eklenen kayıt:** `dnssec/HAZIRLIK_SHA256SUMS` (donmuş listenin bayt-aynı kopyası).

Kalan bütün hazırlık dosyaları (eşleme, taban ve örnek dosyaları, tablolar, modeller, `kos.py`'ler) donmuş hâlleriyle aynıdır. Doğrulama: `dnssec/HAZIRLIK_SHA256SUMS` ile `sha256sum -c`. Beklenen başarısızlıklar yalnız §4.1–4.2'deki altı dosyadır.

## 5. K1-11 uyumsuzluğunun tanısı
- **Gözlenen:** Tamarin `a_rrset_authentic` = falsified (12 adım); beklenen verified. Aynı hücrede ASP YOK (beklenen).
- **İz** (`dnssec/sonuc/tamarin_ham/K1-11.tam__a_rrset_authentic__b1.txt`):
  1. `Break_Zone_Classical` klasik KSK'yı ve ZSK'yı açığa çıkarır.
  2. Saldırgan kendi ZSK'larıyla bir DNSKEY RRset'i kurar ve klasik KSK ile imzalar.
  3. `Validate_DNSKEY_via_KSKcl` bunu gerçek çift-DS üzerinden kabul eder.
  4. `Validate_A_complete_both`, iki saldırgan anahtarıyla imzalı A RRset'ini kabul eder.
- **Tanı:** model hatası, Tamarin tarafında.
  - KAT-SPEC §2(c) taslağı bütünlük testini (COMPLETENESS) yalnız A RRset adımında kodluyor; DNSKEY adımı "herhangi bir tek yol" kalıyor.
  - DS iki algoritmayı işaretlediğinde (DS_BOTH) PQ zorunluluğu boşa düşüyor.
  - Hücrenin tanımı ("iki algoritma da zorunlu") ve kör çalışmanın B2 yazılan okuması ("zincirin tamamında") ile çelişir.
  - ASP eşlemesi bütünlüğü zincirin tamamına uygular ve beklenen değeri verir.
- **B2 alternatifi (yalnız tanıda):** "yalnız DNSKEY'de" okuması K1-04, K1-06 ve K1-11'in üçünü de falsified yapardı. Gözlenen yalnız K1-11. Bu yüzden B2 alternatifi değil; taslağa örtük bir üçüncü kapsam ("yalnız yaprak") girmiş.
- **Tanı koşusu:** `dnssec/tani/KAT1_DNSSEC_tani.spthy` bütünlüğü DNSKEY adımına da uygular. Altı COMPLETENESS hücresi (K1-02, K1-04, K1-05, K1-06, K1-11, K1-12) 6/6 beklenen değerde: K1-11 verified (28 adım), diğerleri değişmedi.
- **Kural:** Yedek teste geçilmedi, beklenen değere dokunulmadı. KAT-1 kapı sonucu KALDI. Düzeltilmiş modelin benimsenmesi yürütücü kararıdır (§7 N-KAT-1).

## 6. Adım sonu gözden geçirme (IS-PLANI 6.10)
**1. Plan–gerçekleşen.**
- Üç test de kuruldu ve koşuldu.
- S/MIME eşlemesi CEK tabanlı yapı eşlemesi olarak kuruldu (ESLEME §4); yedek test gerekmedi.
- KAT-2 ve KAT-3 GEÇTİ. KAT-1 KALDI (Tamarin K1-11).

**2. Kalite kontrolü.**
- **GEÇTİ/KALDI hükümleri araç çıktısına mı dayanıyor?** Evet. Her değer `sonuc/*.csv`'den; okuma kuralları koşumdan önce sabitlendi (ESLEME §2.5, §3.4, §4.4, §4.5).
- **Çekirdek değişmedi mi?** Evet; özet önce = sonra.
- **Eşleme iddianın kapsamını aşıyor mu?**
  - KAT-1'de sürüm geçerliliği ekosistem türetme kurallarında.
  - KAT-2 karar hücrelerinde kanıt geçerliliği okuma kuralında.
  - KAT-3a'da sınıf etiketleri okuma kuralında.
  - Politika/güvenlik mantığı çekirdekte (ESLEME §5).
  - İddialar bu kapsamla sınırlı raporlanmalıdır: çekirdek sınıflama yapmaz; sınıflamanın PQ'ya duyarlı kısmını hesaplar.
- **Kör tablo bağımsız ve önceden hash'li mi?** Evet (kör çalışma, commit `f012841`; nsurum çapa 8).
- **V-d hücre tablolarıyla mı değerlendirildi?** Evet (`nsurum` 141 anahtar + KAT-SPEC §6).

**3. Diğer adımlara etkisi.**

| Etkilenen adım | Etki | Gerekli değişiklik | Karar |
|---|---|---|---|
| Adım 8 | V-d ilk koşum 2/3 (KAT-1 KALDI, Tamarin modeli); düzeltme sonrası 3/3 | İki koşum birlikte kapı raporuna; bağımsız gözden geçirme değerlendirir | yürütücü: v2 kabul (26.09) |
| Adım 3 | Çekirdek değişikliği GEREKMEDİ (ASP 109/109) | yok | – |
| Adım 14 | Genellenebilirlik alt bölümü | ASP çekirdeği üç ekosistemde 109/109; S/MIME'nin yapı eşlemesi ve kapsam sınırları (ESLEME §4.2, §5) | yürütücü |
| ÖK | K1-11 düzeltilmiş modeli ve pilot iyi biçimlilik kararı | §11'e "sonuç görüldükten sonra" etiketiyle; yedek test seçilmedi | yürütücü |

**4. Güncellik ve kapılma.** Bu adımda web kullanılmadı; güncellik denetimi yürütücünün proje notları akışındadır.

**5. Karar.** Devam.
- Yürütücü düzeltilmiş Tamarin modelini "sonuç görüldükten sonra düzeltme" etiketiyle kabul etti (26.09.2026).
- KAT-1 v2 ile GEÇTİ; ilk koşumun KALDI kaydı korunur (§8).
- Yedek teste geçilmedi.

## 7. Yürütücüye notlar
- **N-KAT-1 (KARARA BAĞLANDI, 26.09.2026):** KAT-1 K1-11 Tamarin uyumsuzluğu.
  - Karar: Düzeltilmiş Tamarin modeli "sonuç görüldükten sonra düzeltme" etiketiyle kabul edildi. İlk koşumun KALDI kaydı korunur.
  - Uygulama: `dnssec/KAT1_DNSSEC_v2.spthy`, bütün KAT-1 Tamarin hücreleri ve mutasyonları → `dnssec/sonuc_v2/` (§8).
- **N-KAT-2 (KARARA BAĞLANDI, 26.09.2026):** KAT-3b pilot iyi biçimlilik düzeltmesi KABUL edildi. Uyarılı model geçersizdir; tek sözcüklük düzeltmeli kopya kapı hücresidir. Aslının aynı hükmü verdiği raporda kalır.
- **N-KAT-3 (bilgi):** KAT-3a ASP–Tamarin karşılığı (MIXED↔o4, PQ_ONLY↔o1, HYBRID_KEM↔o5; `klasik` sondası) KAT-SPEC'te adıyla yoktu; ESLEME §4.6'da koşumdan önce tanımlandı.
- **N-KAT-4 (bilgi):** KAT-2 duyarlılık lemmaları ve KAT-3a `kat3a_fail`/`model_gap` `nsurum`'da yok; ek olarak raporlandı (hepsi beklenen yönde).
- **N-KAT-5 (bilgi):** `nsurum/__pycache__` kazası (§2.4); temizlendi, bütünlük doğrulandı.

## 8. Düzeltme sonrası koşum (v2; SONUÇ GÖRÜLDÜKTEN SONRA DÜZELTME, yürütücü kararı 26.09.2026)
- **Model:** `dnssec/KAT1_DNSSEC_v2.spthy` (`1df11c22…f21b`), "düzeltilmiş kapı modeli". `KAT1_DNSSEC.spthy` dokunulmadı (`0a77dc2e…19bd`; hazırlık listesiyle aynı).
- **v1 → v2 farkı** (başlık yorumu hariç; `diff`):
  1. tema adı `…_v2`;
  2. üç eski DNSKEY doğrulayıcı bloğuna `not COMPLETENESS` koşulu (bu bloklar yalnız bütünlük testi olmayan bayrak kümelerinde etkin; içerikleri aynı);
  3. `COMPLETENESS` için üç yeni blok:
     - bütünlüklü doğrulayıcılar (`Validate_DNSKEY_complete_{cl,pq,both}`); tanı modelinin mutasyonsuz bloğuyla kural kuralına aynı (özet `0c588cb9…`);
     - bunların `MUT_NO_DS_SIG` alternatifi (yalnız DS imza denetimi silinmiş);
     - bunların `MUT_NO_DS_KSK_MATCH` alternatifi (yalnız DS–KSK eşleşmesi silinmiş).
  - Sonuç: `COMPLETENESS` verilmeyen her bayrak kümesinde v2 v1 ile aynıdır.
  - Tanı modelinden tek fark: mutasyon alternatiflerinin v2 doğrulayıcılarına göre tanımlanması. Tanı modelinde `COMPLETENESS` + `MUT_*` eski, bütünlüksüz doğrulayıcılara düşüyordu; bu, mutasyonun iki korumayı birden kaldırması demekti.
- **Koşucular:**
  - `dnssec/tamarin_kos_v2.py` (`c19f6972…c429`): dondurulmuş `tamarin_kos.py`'yi değiştirmeden içe aktarır; yalnız modeli ve çıktı dizinini (`sonuc_v2/`) değiştirir. Hücreler, bayraklar, lemmalar, merdiven ve sınırlar ilk koşumla aynı.
  - `dnssec/degerlendir_v2.py` (`b642fc44…03e3`): `degerlendir.py`'den mekanik olarak türetildi (6 yol/etiket satırı).
  - `dnssec/yanyana_v1_v2.py`: yan yana tablo.
  - Bu üç dosyanın ve modelin özetleri koşumdan önce kaydedildi: 2026-09-26T11:25:04Z.
- **Sonuç:**
  - İyi biçimlilik: 16/16, uyarı 0.
  - Hücreler: 15/15 beklenen değerde; yalnız K1-11 değişti (falsified → verified, 28 adım), öteki 14 hücrenin hükmü v1 ile aynı. Bütünlük hücrelerinde adım sayıları kural kümesi değiştiği için 19'dan 18'e indi; hükümler aynı.
  - Mutasyonlar: 7/7 satır beklenen yönde ve temel hücreden farklı; 5/5 mutasyon öldürüldü.
  - `executable` 22/22 verified; hepsi merdivenin ilk basamağında (en uzun 3,33 s, en çok 139,1 MiB).
  - **KAT-1 düzeltme sonrası: GEÇTİ** (`dnssec/sonuc_v2/KAT_OZET.{json,md}`, `YANYANA.md`).
- **Bütünlük:**
  - İlk koşumun bütün dosyaları v2 koşusundan etkilenmedi: ilk koşum sonrası `SHA256SUMS` 580/580 OK. v2 yalnız `sonuc_v2/`'ye yazdı.
  - ASP ve `cekirdek.lp`'ye dokunulmadı.
  - Son `SHA256SUMS` yeni dosyaları da kapsar.

## Durum
(son güncelleme 26.09.2026)
- [x] Hazırlık (eşleme, örnekler, modeller, koşucular), iyi biçimlilik, alıntılar, dondurma (`2d23e35b…`)
- [x] İlk koşum: ASP (109/109), Tamarin (31/32), mutasyonlar (12/12), ekler; commit `e4c1090`
- [x] K1-11 tanısı (iz + tanı modeli 6/6)
- [x] Yürütücü kararları: N-KAT-1 (v2 kabul), N-KAT-2 (pilot kopyası kabul)
- [x] Düzeltme sonrası koşum (v2): KAT-1 Tamarin 15/15, mutasyonlar 5/5 → KAT-1 GEÇTİ
- [x] SONUC.md (iki koşum yan yana), ADIM06-RAPOR.md, SHA256SUMS (son)

```yaml
çalışma: "asp"
adim: 6
cekirdek_sha256_once_sonra: "a32372a7c646274ce672c9586e25b34f75f4febb2f966596cc97e7afb89e0b38 (ayni; 45cbd0f; duzeltme ASP'ye dokunmadi)"
hazirlik_kimligi: "2d23e35b146d63856c9936c963cd6fffd7526b24008e579c5c8f3b951a85024b (2026-09-26T11:07:00Z)"
ilk_kosum: {commit: "e4c1090", nsurum: "140/141", asp: "109/109", tamarin: "31/32", asp_tamarin: "31/32", mutasyon: "12/12", vd: "2/3", KAT-1: "KALDI (K1-11)", KAT-2: "GECTI", KAT-3: "GECTI"}
duzeltme_sonrasi: {model: "dnssec/KAT1_DNSSEC_v2.spthy", KAT-1_tamarin: "15/15", KAT-1_asp_tamarin: "15/15", KAT-1_mutasyon: "5/5", degisen_hucre: ["K1-11"], KAT-1: "GECTI", nsurum: "141/141", vd: "3/3"}
pilot_kat3b: "iyi bicimli kopya kapi hucresi (kabul); asli ayni hukum"
alinti: "21/21"
yedek_test: "secilmedi"
acik_sorunlar: []
```
