# Dondurma girdisi — `experiment/statistics/` (C3 / H6 istatistik betikleri)

**Hazırlayan:** istatistik çalışması (Adım 9, görev 9) · **Tarih:** 25.09.2026 · **Araç:** `c3istat` 1.0.0.

**Durum:** Yalnız sentetik veriyle doğrulandı. Hiçbir hedef kütüphaneye dokunulmadı; hiçbir gerçek ölçüm verisi kullanılmadı.

**Dayanak:** ÖK `00-on-kayit/ON-KAYIT-TASLAK.md` taslak v0.6 (çapa 5 `facbf26`): §2B, §2D-A, §2E, §3.7, §6, Ek A, Ek C.

**Açık kararlar:** Dondurmadan önce yürütücünün karar vermesi gereken yorumlar `KARAR-NOTLARI.md` N-1…N-12'dedir. Bu kararlar `betikler/c3istat/yapilandirma.py`'deki sabitleri değiştirebilir. Değişirse testler yeniden koşulur ve bu dosyadaki özetler yenilenir.

## 1. Dondurulacak dosyalar ve SHA-256

Kaynak: `SHA256SUMS`; `tumunu_calistir.sh` adım 4 üretir. Doğrulamak için bu klasörde `sha256sum -c SHA256SUMS` çalıştırılır.

`SHA256SUMS` dosyasının kendi SHA-256'sı: `513ac318770c2f7199fd878d4a6eb9fff8ec2cfcf01adeb6ccabec8e4f06f370`

| Dosya | SHA-256 |
|---|---|
| `Dockerfile` | `ce1c006cc496945af95275c8ed4fb9dec2bed5c5c5341b24b8f869b601a778c3` |
| `tumunu_calistir.sh` | `65df0818d2a54fcf3d7c6ea981f287a98f4d4b636a661c4c0a0690bf51449d0d` |
| `SEMA.md` | `92bb18b74592a517df32c079f67b7457628295494fd28098d9f0bb001421ca5c` |
| `.dockerignore` | `0576991d5e27469f781a4128b2eea9a6bdfad56d5e808177560390668356d5e2` |
| `betikler/requirements.txt` | `3cd6369bbf144f740cc1b82ec8d355b522c9dea8698b1266f34e880da2c54c7f` |
| `betikler/c3istat/__init__.py` | `809b210e9e26e0747a7e326c375a087c9d8de5f398cc3aacebda8d040f42684a` |
| `betikler/c3istat/__main__.py` | `6990410d729888995e6463cd1c6d14867302cdbcc80218f50201274f8479c6ff` |
| `betikler/c3istat/analiz.py` | `39f206acd30dfe5be758d1ebcf5e4d8622cfb30b0be1b92d996452620a803ccf` |
| `betikler/c3istat/bootstrap.py` | `df51f9a55a7b2889acc8603e0ecd4495de48fdbb6c508f09d2da929444f9db74` |
| `betikler/c3istat/karsilastir.py` | `5378604763427c160916e97908b15e3975c67f092a7b997215b31ea54dae37c5` |
| `betikler/c3istat/kesin.py` | `e5d6ac2fc76bc29971090898f067d9f66995b7c26598603e433376e20bbf7be0` |
| `betikler/c3istat/rapor.py` | `7de41aa0be63011f5bdfd9f332349308ddc97d021a8a73ead182d7230a2e9738` |
| `betikler/c3istat/referans.py` | `537386516291b9d4a52de38b5f058a26df168f46964512e9767cefe1f5c0283e` |
| `betikler/c3istat/sema.py` | `f7221f182c16a0bafed020691f3bd8bae6f3741c930bf02c1a871f33096a6f22` |
| `betikler/c3istat/yapilandirma.py` | `b0b980421e4cf6ae34c88309ebe261f3565de2f50ea8bac04b00c56e09339abc` |
| `sentetik-testler/_ortak.py` | `caa11f84d8e1209bf6753bc215a20fa40b5130957c49e712ce8ab8a86080f8b6` |
| `sentetik-testler/calistir.py` | `276520703822656239783a63d2979129e20ecfae241f5ec24713a7fb5e3d7859` |
| `sentetik-testler/ornek_veri_uret.py` | `1af397ed60147982e687568ce2a1d6db003a56c0b117c2415dc6f70bb50eec79` |
| `sentetik-testler/test_bootstrap.py` | `d136725937d2d9301be2f37f11cc130410b1e187b3dc4d61ada530336a131b4a` |
| `sentetik-testler/test_ek_a.py` | `59a3f9a6df742de3dbcd3cb4bf12f45329764a34f5731ce9e60dda52e209db9e` |
| `sentetik-testler/test_iki_uygulama.py` | `1854af21c8ccf1d4544ec5df72b6c344001b586b3e9f113844b086e7444b3533` |
| `sentetik-testler/test_sema.py` | `c5dca3eccb4ecdc3d817b56016e7794381ea7c9512563ececaf53e54d993efbf` |
| `sentetik-testler/test_sinir.py` | `6a66788c8012f4139906c3cbb85143b342180c236dbe30add9c593273fcb697d` |
| `sentetik-testler/test_uctan_uca.py` | `e9539f26d0d3596658ceced4888db3268e5a4a61a847a081686dfdcc270a246a` |
| `sentetik-testler/test_yayimlanmis.py` | `bec0e449986879ba36ac77a7351c8a4d8635f819ff6e0342428b239901455d80` |
| `sentetik-testler/data/ornek_n31_sentetik.json` | `0420f58d7221281f8fb96254394f2f66b7f230e45178332fcb24d24ad52ff57a` |
| `sentetik-testler/data/yayimlanmis_ornekler.json` | `c4d950b744ca9ff20d979956a59bd2d16e9eff21bd173d3e1b649854fc7aa63a` |
| `sentetik-testler/data/ornek_n31_sentetik_hedefler.csv` | `4840fdc3197357eb380984810e37b2d1eaaf20b4dd12c2b118622ff027cc9c4a` |
| `sentetik-testler/data/ornek_n31_sentetik_vakalar.csv` | `13663258db5565e876560768f30c69e8f101f17c5e5b6dbb74c52933574c2ab3` |
| `kaynak/NEWCOMBE-KAYNAK.md` | `a9eaf810614fd15fe25ec592f30dd1c513887d57097977459ef6f2d5b1500e35` |

**Dondurma paketine GİRMEYENLER:**
- `KARAR-NOTLARI.md`, bu dosya ve `sonuclar/` (kanıt kaydı; özetleri §6'da).
- `kayit/` (Docker listeleri, inşa günlüğü).

## 2. İmaj

| Öğe | Değer |
|---|---|
| Ad | `pq-a09-analiz:1.0` |
| İmaj kimliği | `sha256:f7bc4aa39c305a85d624de8ff9e75f25aa5fec943d035c664fbc2c5243c45966` (25.09.2026 inşası; `kayit/imaj_kimligi.txt`) |
| Taban | `python:3.11-slim@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534` (Python 3.11.16; resmî Docker Hub; projede kullanılan özet) |
| Paketler | `betikler/requirements.txt`: numpy 2.4.6, scipy 1.17.1, statsmodels 0.15.0 + tam bağımlılık kapanışı (pandas 3.0.6, patsy 1.0.3, formulaic 1.2.2, interface-meta 2.0.1, narwhals 2.26.0, packaging 26.3, python-dateutil 2.9.0.post0, six 1.17.0, typing-extensions 4.16.0, wrapt 2.4.1). Hepsi PyPI'den, sürüm ve SHA-256 sabit; `pip install --require-hashes --only-binary=:all: --no-deps` + `pip check` |
| Sürüm kapısı | İnşa, Python 3.11.16 ve numpy/scipy/statsmodels sürümleri beklenenden farklıysa başarısız olur |
| Koşum | `--rm --memory=4g --network none`; konteyner adları `pq-a09-analiz-*` |

**Not:** Docker imaj kimliği yeniden inşada değişebilir (yapılandırmadaki oluşturma zamanı). İçeriği belirleyen şunlardır:
- taban özeti,
- `requirements.txt` özetleri,
- §1'deki dosya özetleri.

Dondurmada yürütücü imajı bir kez kurar ve kimliği pakete yazar. Adım 10 aynı kimlikle koşar.

## 3. Tohumlar

| Tohum | Değer | Kullanım | Dayanak |
|---|---|---|---|
| Bootstrap | **20260927** | `bootstrap.kume_bootstrap_saf/numpy`. Her bootstrap çağrısı (kapsam: hepsi / K / T) yeni bir `random.Random(20260927)` ile başlar | ÖK §6.9, Ek C |
| Diğer Ek C tohumları (20260924–26, 20260928–29) | — | İstatistik betiklerinde **kullanılmaz** (üreteç, mutasyon, örnekleme, diferansiyel test, ek yük) | — |
| Test tohumları | 910001–910005, 910010 | Yalnız sentetik test verisi (`test_iki_uygulama.py`, `ornek_veri_uret.py`). Analiz tohumu değildir | — |

**Rastgele akışın tam tanımı (ÖK'de yok; NOTLAR N-7):**
- `rng = random.Random(20260927)` (Mersenne Twister).
- Kümeler `hedef_id`'ye göre sözlük sırasında dizilir. m = 0 olan kümeler önceden dışlanır; k = kalan küme sayısı.
- r = 1…B ve j = 1…k için `indeks = floor(rng.random() · k)` (replikasyon-öncelikli sıra).
- İstatistik havuzlanmış orandır: θ\* = Σ x / Σ m.
- Yüzdelik GA: Hyndman–Fan tip 7, q = 1/40 ve 39/40.

Python, `random()` dizisinin kararlılığını güvence eder; bu yüzden tanım `randrange` yerine `random()` üzerine kuruldu.

## 4. İzlenebilirlik: ÖK maddesi → uygulama → test

A = `betikler/c3istat/kesin.py`: yalnız standart kütüphane, kesin kesir ve Decimal.
B = `betikler/c3istat/referans.py`: scipy/statsmodels/numpy.
Hat = `betikler/c3istat/analiz.py`.

| ÖK maddesi | Tanım | A / B | Hat | Testler (`sentetik-testler/`) |
|---|---|---|---|---|
| §2B.5, §3.7, §6.6 T1, Ek A | Tek yönlü kesin binom (alt), X = Σ Y_L4. c(n_eff) = max{c : P(X ≤ c) ≤ 0,05}, u = n_eff − c. X ≤ c destek, X ≥ u yanlışlama, arada belirsiz | `kesin.binom_alt_p`, `kesin.kritik_degerler` / `referans.binom_alt_p`, `referans.kritik_degerler` | `t1_karari`, `_t1` | `test_ek_a` (EkATablosu, N31, GenelKural); `test_sinir.T1Karari`; `test_iki_uygulama.test_binom_p_degerleri`, `test_kritik_degerler` |
| §6.3 | n_eff = dahil − adaptör geçersiz − belirsiz. n_eff < 20 ise yalnız tanımlayıcı (Wilson) | — | `analiz_et`, `t1_karari` | `test_sinir.T1Karari` (n_eff_20_alti, n_eff_degisimi, butun_hedefler_belirsiz); `test_uctan_uca.H6Hukmu.test_tanimlayici` |
| §6.10 | (i) belirsiz = 1, (ii) belirsiz = 0. **destek** = birincil VE (i) X ≤ c; yalnız birincil ⇒ **kırılgan destek** | — | `_t1_duyarliliklar`, `h6_hukmu` | `test_uctan_uca.H6Hukmu` (destek, kirilgan_destek, destek_belirsizle_saglam, yanlislama, belirsiz) |
| §0.3, §6.10 | Pilot kütüphaneleri hariç T1 | — | `_t1_duyarliliklar` | `test_uctan_uca.Duyarliliklar.test_pilot_haric` |
| §2B.9 | Devralan hedefler hariç T1 ve T2; tanımlayıcı, Holm dışı | — | `_t1_duyarliliklar`, `analiz_et` (T2d) | `test_uctan_uca.Duyarliliklar.test_devralan_haric_t1_t2` |
| §6.6 T2, §2B.7 | Kesin McNemar (F_K, F_T), iki yönlü; yalnız TK1 + TK2; TK3 ayrı ve tanımlayıcı | `kesin.mcnemar_kesin` / `referans.mcnemar_kesin` (statsmodels) | `_t2`, `_tanimlayici` | `test_iki_uygulama.test_mcnemar`; `test_sinir.McNemarSinir`; `test_uctan_uca.T2KapsamVeEtki` |
| §6.7 T2 | Eşleştirilmiş fark P(F_T=1) − P(F_K=1) + Newcombe yöntem 10 (φ\*) | `kesin.newcombe_eslestirilmis` / `referans.newcombe_eslestirilmis` | `_t2` | `test_yayimlanmis` (Y5–Y7, NewcombeTanimi); `test_iki_uygulama.test_newcombe_eslestirilmis`, `…phi0_statsmodels_bagimsiz`; `test_sinir.NewcombeSinir` |
| §6.6 T3 | Fisher kesin, iki yönlü; PQ'ya özgü = F_T = 1 ∧ F_K = 0; SDJWT ↔ JOSE | `kesin.fisher_iki_yonlu` / `referans.fisher_iki_yonlu` (scipy) | `_t3`, `_fisher_blok` | `test_iki_uygulama.test_fisher`; `test_sinir.FisherSinir`; `test_uctan_uca.T3T4T5.test_t3` |
| §6.6 T4 | Fisher kesin; L ≥ 3; 8725bis-10 (21.08.2026) sonrası sürüm | aynı | `_t4`, `_fisher_blok` | `test_uctan_uca.T3T4T5.test_t4`; `test_sema.test_tarih_bayrak_celiskisi` |
| §6.7 T3, T4 | OR (koşullu MLE) + koşullu kesin GA; fark + Newcombe yöntem 10 (bağımsız) | `kesin.kosullu_or` / `referans.kosullu_or` (scipy `odds_ratio`, conditional); `kesin.newcombe_bagimsiz` / `referans.newcombe_bagimsiz` (statsmodels `newcomb`) | `_fisher_blok` | `test_iki_uygulama.test_kosullu_or`, `test_newcombe_bagimsiz`; `test_yayimlanmis` (Y4); `test_sinir.FisherSinir.test_or_*` |
| §6.6 T5 | Tek yönlü kesin binom (üst), D_soy | `kesin.binom_ust_p` / `referans.binom_ust_p` | `_t5` | `test_uctan_uca.T3T4T5.test_t5`; `test_iki_uygulama.test_binom_p_degerleri` |
| §6.7 T1, T5 | Oran + Wilson %95 GA (+ T1'de 0,5'ten fark) | `kesin.wilson` / `referans.wilson` (statsmodels) | `_t1`, `_t5` | `test_uctan_uca.H6Hukmu.test_etki_buyuklugu_t1`; `test_yayimlanmis` (Y1–Y3); `test_ek_a.Tablo613` |
| §6.6 Holm | Holm (T2–T5), m = 4, α = 0,05; T1 aile dışı | `kesin.holm` / `referans.holm` (statsmodels `multipletests`) | `_holm` | `test_sinir.HolmSinir` (bilinen örnek, eşitlikler, α/k sınırı, permütasyon); `test_iki_uygulama.test_holm`; `test_uctan_uca.T3T4T5.test_holm_butunlesik` |
| §6.8 | Wilson %95 GA: her L basamağı, B1–B6 (B1/B5 kategori başına; B4 = `B4_ozel_kod`) | `kesin.wilson` / `referans.wilson` | `_wilson_tablolari` | `test_uctan_uca.GenelYapi.test_wilson_l_duzeyleri`; `test_iki_uygulama.test_wilson` |
| §6.9 | Küme bootstrap: birim kütüphane, B = 10.000, yüzdelik GA, tohum 20260927 | `bootstrap.kume_bootstrap_saf` / `kume_bootstrap_numpy`; `kesin.yuzdelik_tip7` | `_bootstrap` | `test_bootstrap` (bit düzeyi tekrar, ayrı süreç, bilinen dağılım); `test_iki_uygulama.test_bootstrap_numpy_ve_saf`; `test_uctan_uca.GenelYapi.test_bootstrap_hatti` |
| §6.11 | Kararsız hücre sayısı raporlanır | — | `_tanimlayici` (`kararsiz_hucre_sayisi`) | `test_uctan_uca.CsvJsonEsdegerlik` |
| §6.13 | Eşik tablosu (25/30/40) ve Wilson genişlikleri | `kesin.kritik_degerler`, `kesin.wilson` | — | `test_ek_a.Tablo613` |
| §6.14 | Güç notu (n = 30) | `kesin.binom_cdf` (genel p) | — | `test_ek_a.Not614Guc` |
| §6.6 gerekçe | T1 Holm'a girseydi n = 30'da ≤ 8 / ≥ 22 | `kesin.kritik_degerler(α = 0,01)` | — | `test_ek_a.Not66Holm` |
| §2B.3–4 | n = 31 beklenir (farklıysa uyarı); REF n dışı | — | `analiz_et` | `test_uctan_uca.GenelYapi` (n_uyarisi, ref_hedefler_disarida) |
| §2B.6, §2D-A.2, §4.13–4.15 | Y_L4 (L4m/L4c), kontrol etiketi, L0–L5, B1–B6, belirsiz nedenleri | `sema` | `_tanimlayici`, `_wilson_tablolari` | `test_sema` |
| Ek C | Bootstrap tohumu | `yapilandirma.BOOTSTRAP_TOHUM` | — | `test_bootstrap.BilinenCevap.test_yapilandirma_ok_ile_ayni` |

**Toleranslar ve bıçak sırtı kuralı** (`yapilandirma.TOLERANSLAR`, `karsilastir.py`):
- p ve GA: mutlak 1e-10.
- OR: göreli 1e-8 (mutlak alt sınır 1e-12).
- Bootstrap: 1e-12.
- Karar farkı yalnız referans değeri eşiğe ≤ 1e-12 yakınsa "sınırda" sayılır; o durumda kesin aritmetik (A) esastır ve fark raporlanır.
- Bunun dışındaki her fark hatadır. Hat çıkış kodu 2 verir ve analiz geçersizdir.

## 5. Çalıştırma (Adım 10 için)

1. Önce `sha256sum -c SHA256SUMS` çalıştırılır (bu klasörde). Uyuşmazlık varsa durulur (ÖK §10.7).
2. Girdi `SEMA.md`'ye uygun tek bir JSON dosyasıdır (`veri_turu = "olcum"`). CSV de kabul edilir: `hedefler.csv` + `vakalar.csv`.
3. Komut:

   ```
   docker run --rm --name pq-a09-analiz-kosu --memory=4g --network none \
     -v <girdi>:/girdi:ro -v <cikti>:/cikti pq-a09-analiz:1.0 \
     python -m c3istat analiz --girdi /girdi/<dosya>.json --cikti /cikti
   ```

4. Çıktılar:
   - `sonuc.json` (makine okunur; belirlenimci, tarih içermez; betik özetlerini `arac.betik_sha256`'da taşır),
   - `sonuc.md` (insan okunur tablo),
   - `karsilastirma.json` (her niceliğin iki uygulama karşılaştırması).
5. Çıkış kodları: 0 tamam · 2 iki uygulama uyuşmuyor (analiz geçersiz) · 3 girdi doğrulanamadı (`dogrulama_hatalari.json`).

## 6. Doğrulama kanıtı (25.09.2026; `sonuclar/`)

**Sentetik test takımı** iki taze konteynerde koşuldu; iki koşunun `test_ozeti.json`'ı bayt-aynı:
- test yöntemi **115/115**, alt test **729/729**,
- iki uygulama **56.269/56.269 vaka**, **90.058/90.058 nicelik**. Ailelere göre en büyük sapmalar:
  - binom 2,8e-16; Fisher 3,3e-16; McNemar 4,4e-16;
  - Wilson 3,3e-16; Newcombe (bağımsız ve eşleştirilmiş) 5,6e-16;
  - koşullu OR göreli 4,6e-11;
  - Holm 0; bootstrap 4,4e-16 (dağılım SHA-256'ları eşit).

**Ek A:** n = 20…40 satırlarının 21'i de her iki uygulamayla birebir yeniden üretildi (c, u, P(X ≤ c) 4 ondalık). **n = 31:** c = 10, u = 21, P(X ≤ 10) = 75973189/2147483648 = 0,035378 (ÖK: 0,0354).

**Yayımlanmış örnekler (Y1–Y7):** iki uygulamayla da yeniden üretildi. Kaynak ikincildir; birincil metin erişilemedi (`kaynak/NEWCOMBE-KAYNAK.md`).

**Belirlenimcilik:**
- Örnek sentetik analiz (`data/ornek_n31_sentetik.json`) iki taze konteynerde koşuldu; `sonuc.json`, `sonuc.md` ve `karsilastirma.json` bayt-aynı. `sonuc.json` SHA-256: `388b48a27049b3d52ab559ab3c212fcafeb8f2e02f56ffe45e9ace18ce1931d4`.
- CSV girdisiyle koşum, `girdi` üst veri bloğu dışında JSON koşumuyla aynı.
