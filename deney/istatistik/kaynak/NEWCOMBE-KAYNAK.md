# Newcombe yöntem 10 ve Wilson için yayımlanmış örnek değerlerin kaynağı

**Tarih:** 25.09.2026 (arama 12:25:54–12:30:41 UTC; yürütücü kararıyla en fazla 10 dk).
**Hazırlayan:** istatistik çalışması (Adım 9, görev 9).

## 1. Birincil kaynaklar: ERİŞİLEMEDİ

| Makale | DOI | Durum |
|---|---|---|
| Newcombe RG (1998). Improved confidence intervals for the difference between binomial proportions based on paired data. *Stat Med* 17(22):2635–2650 | `10.1002/(SICI)1097-0258(19981130)17:22<2635::AID-SIM954>3.0.CO;2-C` | Kapalı erişim |
| Newcombe RG (1998). Interval estimation for the difference between independent proportions: comparison of eleven methods. *Stat Med* 17(8):873–890 | `10.1002/(SICI)1097-0258(19980430)17:8<873::AID-SIM779>3.0.CO;2-I` | Kapalı erişim |

Denenen yasal yollar:
- OpenAlex (anonim, `mailto` yok): iki makale için de `is_oa = false`, `oa_status = closed`, `any_repository_has_fulltext = false`.
- Scholar Gateway (Wiley): yalnız özet döndü (`total_chunks = 1`). Eşleştirilmiş makalenin özeti yöntem numarasını doğruluyor: "*A computationally simpler method based on the score interval for the single proportion also performs well (method 10).*"
- Wiley bağlantısı: HTTP 403. Ödeme duvarı **atlatılmadı**.
- CiteSeerX kaydı Wayback Machine'e yönleniyor; HTTP 429. Arşiv kopyası **kullanılmadı**.

Sonuç: Newcombe'un tablolarındaki değerler birincil metinden **doğrulanamadı**.

## 2. Kullanılan açık erişimli ikincil kaynak

**R paketi `ratesci`** (Pete Laud; CRAN; lisans GPL (≥ 3)).
- Depo: `https://github.com/petelaud/ratesci`, commit `7ad93a580144fe78b9545263975621967bd8c0a0` (21.09.2026).
- Paket sürümü (DESCRIPTION): `1.1.0.9000`.
- Dosya: `tests/testthat/test3.R`, SHA-256 `57bb060993d3cad7f36827109018ec97dd962b0a727a56d280668a01206b20f4`.
  - Dosyanın ilk satırı: "`# Tests of outputs vs published examples in the literature`".
- Tanım dosyası: `R/moverpairci.R`, SHA-256 `d49c463b94411385bbe4342a6990130df6c2970f97fc04a5351618efa83c1094`.

Aşağıdaki değerler `test3.R`'den **birebir** aktarıldı. Parantez içindeki satır numaraları bu commit'e göredir. Dosyanın kendisi GPL olduğu için depoya kopyalanmadı; yalnız bu kısa alıntılar tutuldu.

| # | Veri | Yöntem (ratesci çağrısı) | Kaynakta verilen değer | Kaynaktaki açıklama |
|---|---|---|---|---|
| Y1 | x = 15, n = 148 | `wilsonci(cc = FALSE)` | (0,0624; 0,1605) | "Single proportion, Newcombe examples" (s. 347, 360–364) |
| Y2 | x = 0, n = 20 | aynı | (0; 0,1611) | aynı |
| Y3 | x = 1, n = 29 | aynı | (0,0061; 0,1718) | aynı |
| Y4 | x1 = 5, n1 = 56; x2 = 0, n2 = 29 | `moverci(type = "wilson")` (kare-ve-topla) | (−0,0381; 0,1926) | "Newcombe RD example (d)", "Newcombe/'Score'/Square&add" (s. 7, 20–24) |
| Y5 | (a, b, c, d) = (20, 12, 2, 16) | `moverpairci(type = "wilson", corc = TRUE)` | (0,0562; 0,3292) | "and against Newcombe's method 10 result" (s. 525–528) |
| Y6 | (20, 12, 2, 16) | `moverpairci(type = "wilson", corc = FALSE)` | (0,0618; 0,3242) | "example from Newcombe, against Newcombe's method 8 result" (s. 520–523) |
| Y7 | (1, 1, 7, 12) | `moverpairci(type = "wilson", corc = TRUE)` | (−0,507; −0,026) | "MOVER Wilson - Fagerland use Newcombe's correlation-corrected 'method 10'" (s. 487–492; Fagerland vd. 2014 örneği) |

**Tablo düzeni** (`moverpairci` belgesi): x = (a, b, c, d).
- a: iki koşulda da olay,
- b: yalnız 1. koşulda olay,
- c: yalnız 2. koşulda olay,
- d: hiçbirinde olay yok.

Fark θ = (a + b)/N − (a + c)/N = (b − c)/N.

## 3. Yöntem 10'un tanımı: bu kaynaktan çıkan kritik ayrıntı

`R/moverpairci.R` (commit yukarıda) korelasyonu şöyle hesaplıyor:
- φ̂ = (ad − bc) / √((a+b)(c+d)(a+c)(b+d)).
- `corc = TRUE` ("Newcombe's adjusted correlation estimate") ve ad − bc > 0 ise: φ* = max(ad − bc − N/2, 0) / √(…).
- Payda 0 ise ya da değer tanımsızsa φ = 0.

ratesci, yayımlanmış yöntem 10 sonucunu (Y5) ancak **bu düzeltilmiş φ\*** ile yeniden üretiyor. Düz φ̂ ile Y6'yı ("method 8") üretiyor.

Bu yüzden `c3istat` eşleştirilmiş Newcombe yöntem 10'u φ\* ile uygular. ÖK bu ayrıntıyı yazmıyor; `KARAR-NOTLARI.md` N-3'e bakın.

## 4. Sınırlılık

- Değerler ikincil bir kaynaktan (açık kaynaklı bir paketin, yayımlanmış örneklerle karşılaştırma testleri) alındı. Newcombe'un basılı tablolarıyla karşılaştırma **yapılmadı**.
- Güvence üç katmanlı:
  1. Y1–Y7'nin `c3istat` tarafından 4 (Y7'de 3) ondalıkta yeniden üretilmesi;
  2. iki bağımsız uygulamanın her sentetik vakada uyumu;
  3. yöntem tanımından elle doğrulanabilir sınır vakaları.
- **Önerilen insan adımı:** Kurum erişimi olan biri iki makalenin örnek tablolarını açıp Y4–Y6'yı karşılaştırırsa bu sınırlılık kalkar. Değerler `sentetik-testler/veri/yayimlanmis_ornekler.json` dosyasına birincil kaynak etiketiyle eklenebilir.
