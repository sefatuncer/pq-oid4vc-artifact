# Oracle A — Yöntem (Adım 9, görev 6 ve 7)

> **Tarih:** 25.09.2026 · **Çalışma:** Oracle A (N-sürüm oracle'ın A kolu).
> **Bağımsızlık:** `deney/oracle/oracle-B/` okunmadı. Brif gereği ayrıca `referans/pilot/`, `model/` ve `gozden-gecirme/adim-0*` (adim-09a ve adim-09b dahil) okunmadı. D-E ve D-S kararlarının içeriği ÖK §2B, §2D ve `IS-PLANI.md` Adım 9'dan alındı.
> **Ölçüm yok:** Hiçbir hedef kütüphane koşulmadı. Hiçbir vektör bir kütüphaneyle ya da kriptografik araçla doğrulanmadı. Vektör dosyaları yalnız base64url ile çözülerek inşa gerçekleri (başlık, talep, zaman) okundu. Ağ erişimi, Docker ve git kullanılmadı.
> **Çıktıyı üreten betik:** `karar_uret.py` (Python 3, yalnız standart kütüphane). Aynı girdilerle her koşuda bayt-aynı `karar.tsv` üretir (§6).

## 0. Girdiler ve kimlikleri

Betik aşağıdaki özetleri denetler. Uyuşmazlıkta durur.

| Girdi | SHA-256 |
|---|---|
| `00-on-kayit/ON-KAYIT-TASLAK.md` (v0.8, çapa 7) | `dcc84092e2ca5eee0fcca8277fbcbd6b06ff613dc3459f63195f44d1ce3df79a` |
| `deney/uretec/vektorler/v1.2/MANIFEST.json` (153 vektör) | `bb17aaa76a3d1859b2dd5df54c62e7039948a715e2c4b4628fed82d184c6e738` |
| `deney/uretec/vektorler/v1.2/SHA256SUMS` | `92663b48f477f51e5a4cdd2a6942d97d36b2d9591fa67af451fd33eb14f0b2a3` |
| `deney/uretec/BATARYA-ESLEME.md` | `d73352179cdf281825d498000b7f9dc6d1df0fe835c8258c6aa2c516e659e3fc` |
| `01-korpus/metin/<belge>.txt` (16 belge; 15'inden alıntı yapıldı, RFC 8725 yalnız özetle denetlendi) | `01-korpus/MANIFEST.csv` `sha256_metin` sütunuyla birebir |

Kullanılan birincil metinler ve sürümleri:
- 8725bis-10 (JWTBCP), composite -04 (JOSECOMP), LAMPS composite -19;
- RFC 7515, 7518, 9864, 9964, 9901, 9449;
- SD-JWT VC -13 ve -19, Token Status List -21;
- HAIP 1.0 Final, OID4VP 1.0 Final, ECCG ACM v2.

## 1. Karar alanı: dört değer (ÖK Ö6)

| Değer | Tanım (Oracle A) |
|---|---|
| `accept-hybrid` | Nesne kabul edilir **ve** yapılandırmaya uygun her kabul yolu geçerli bir PQ bileşeninin doğrulanmasını gerektirir. PQ bileşeni: ML-DSA imzası ya da composite imzanın ML-DSA bileşeni. Yalnız ML-DSA ile imzalı nesnenin kabulü de bu sınıftadır |
| `accept-classical` | Nesne kabul edilir, ama yapılandırma altında kabul için yalnız klasik imza(lar)ın doğrulanması yeterlidir; ya da nesnede yalnız klasik imza vardır |
| `reject` | Yapılandırmaya uygun bir doğrulayıcı nesneyi reddetmek zorundadır (MUST düzeyi). SHOULD düzeyindeki redler `not` sütununda "SHOULD" diye işaretlidir (yalnız VC11/-19) |
| `indeterminate` | Madde + inşa gerçekleri kararı belirlemiyor. Nedenler `BELIRSIZ.md`'de |

Kontrol kollarında (X = EdDSA ya da Ed25519) her kabul `accept-classical`'dır. Böylece kontrol kolunda L4 ölçümü PQ desteğinden ayrılır (ÖK §3.7).

**Etiket bir güvenlik tabanıdır.** P0 (en-az-biri-geçerli) altında ES256 + ML-DSA-65 nesnesinin kabulü `accept-classical`'dır, çünkü kabul için ES256 tek başına yeterlidir. P1 (mevcut-tümü-geçerli) altında aynı nesne `accept-hybrid`'dir, çünkü her mevcut imza doğrulanmak zorundadır. Kim vd.'nin "klasik kabul ≠ hibrit kimlik doğrulama" ayrımı böyle korunur. Ayrıntı: `L4-TURETME.md` §4.

**TK3 notu:** PQ imzayı doğrulayamayan bir hedef `accept-hybrid` üretemez (KRITERLER §5.5). Oracle, hedefin bataryadaki bütün kayıtlı ve taslak algoritmaları desteklediğini varsayar (TK1/TK2 ideali). TK3 hedeflerinin karşılaştırması `adaptor-sozlesme.md` §6'daki kuralla yapılır.

## 2. Politika yapılandırmaları: ÖK §4.13'ten türetme

Her yapılandırma şu dörtlüyle tanımlanır:
- izin kümesi **W**,
- gerekli küme **R**,
- çoklu imza kuralı,
- anahtar yolu.

Her kolda A = ES256. X kola göre değişir: `kontrol-EdDSA` → EdDSA; `kontrol-Ed25519` → Ed25519 (yedek, ÖK §2D m.2); `tedavi-ML-DSA-65` → ML-DSA-65; `tedavi-composite` → ML-DSA-65-ES256. Anahtar–alg bağlama (8725bis §3.1 [T329]; RFC 7515 §5.2 adım 8) **bütün** yapılandırmalarda açıktır, çünkü RFC 7515'e uygun her doğrulama imzayı başlıktaki alg ile doğrular.

| Yapılandırma | W | R | Çoklu imza kuralı | Hangi ÖK gereği bunu istiyor |
|---|---|---|---|---|
| `GEC` | bataryada desteklenen tüm algoritmalar | ∅ | (yalnız tek imzalı nesneler) | §4.15 V± adaptör geçerlilik kapısı; tek imzalı nesnelerin "düz geçerlilik" tabanı |
| `IZIN-A` | {A} | ∅ | (tek imzalı) | §4.13 L1 ("izinsiz algoritma reddediliyor") ve L2 (çağrı başına iki farklı izin listesi: A ile AX) |
| `IZIN-AX` | {A, X} | ∅ | (tek imzalı) | L1/L2'nin olumlu yüzü; **L3** (K10 → RED, §6.5 "RED (L2/L3)"); **L4c-eski ihraççı** (§2B m.6: "eski ihraççının klasik imzalı belgesi kabul edilir") |
| `L4` | {A, X} | {X} | W dışı ek imza: S ile Y ayrışırsa `indeterminate` | §6.5 politikası birebir; §4.13 **L4** ve **L4c-göç**; F_K/F_T'nin oracle'ı (§6.4) |
| `L4-S` | {A, X} | {X} | mevcut her imza W içinde ve geçerli olmalı | §4.8 P3 (= P2 + R_I; P2 ⊇ P1 "mevcut imzaların tümü geçerli"); ECCG ACM Not 51; RFC 7515 §5.2 son paragraf (SHOULD) |
| `L4-Y` | {A, X} | {X} | W dışı imzalar yok sayılır; W içindekiler geçerli olmalı | RFC 7515 §5.2 "application decision" [T314]; 8725bis §3.1 "MUST NOT employ … outside" [T327]; envanterin L4 önerisi (KRITERLER §7.7) |
| `P0` | desteklenen tümü | ∅ | en az bir imza geçerli | §4.8 P0; B5 semantik sınıfı ("en-az-biri-geçerli"); H6'nın başarısızlık modu ayrımı |
| `P1` | desteklenen tümü | ∅ | mevcut imzaların tümü geçerli | §4.8 P1 (ve P2); B5 ("mevcut-tümü-geçerli"); H6 başarısızlık modu |
| `L4-YOL` | {A, X} | {X} | + x5c yolundaki her sertifika imzası PQ olmalı | **B2** ("karışık x5c zinciri politikası ifade edilebilir mi?"); §2D m.13 `yol_sinifi` tanımı; yalnız X5C vektörleri |
| `GEC@-19`, `L4@-19` | GEC / L4 ile aynı | | | `sdjwtvc_surum` duyarlılığı (§2C.2.3, Ö9); **MR3**; yalnız VC01, VC11, VC07, VC08, VC09 (+Ed25519 eşi) |

**Neden bu küme yeterli?**
- **L0:** Ayrı yapılandırma gerekmez. L1 denemesinin başarısızlığıdır (`IZIN-A` altında VPLUS_X kabul ediliyorsa, izin listesi yoktur ya da çalışmıyor).
- **L5:** Ayrı oracle gerekmez. Varsayılan yapılandırmayla koşulan batarya `L4` (L4 için) ve `IZIN-AX` (L3 için) satırlarıyla karşılaştırılır.
- **D_soy:** Varsayılan yapılandırmada gözlenen, tanımlayıcı bir oranıdır (ÖK §6.4, T5). Oracle kararı gerekmez: RFC 7515 §5.2 çoklu imzayı "application decision" olarak bırakır.
- **B1:** `L4-S` ile `L4-Y` ayrımı yakalar. Hedefin K5'teki davranışı hangisine uyuyorsa o kaydedilir; ikisine de uymuyorsa MR2 ihlali olarak işaretlenir.
- **B3:** `L4`/`GEC` altındaki X5C07–X5C09 satırları yakalar.
- **B5:** `P0`, `P1`, `L4-S` ve `L4-Y` satırları birlikte sınıflandırır (`adaptor-sozlesme.md` §5.4).
- **P2, P3 ve P4:** P2, batarya üzerinde P1 ile özdeştir, çünkü alg–anahtar uyuşmazlığı yalnız tek imzalı K10'da var ve her yapılandırmada red. P3 = `L4-S`. P4, kütüphane düzeyinde P3 ile özdeştir: R_I'nin öğrenildiği kanal vektörde temsil edilmez; adaptör R_I'yi API ile sabitler.

**Kapsam kararları:**
- **TSL, DPOP, kapsam-pq/-hibrit vektörleri ve VC12** yalnız `GEC` altında değerlendirildi. Bunlar ihraççı başına politikanın nesnesi değildir. Kapsam vektörleri L4 altında zaten W dışıdır.
- **REQ ailesi** cüzdan tarafıdır (Adım 11; ESLEME "senaryo c"). L4, RP'ye "varlık başına" okumayla uyarlandı: R_RP = {X}. G5 "göç etmiş bir **varlık**" der. Ayrıca OID4VP §5.9.3'e göre DC API'de imza doğrulaması cüzdanın takdirindedir [T268]. Satırlar "cüzdan imzaları doğrular" varsayımıyla yazıldı.
- **X5C ailesi:** Anahtar x5c ve güven çapalarıyla (root-ec, root-ml) çözülür (ÖK §2D m.1). K8/K9 composite kolunda da ML-DSA-65 yapraklıdır (ÖK §2F m.4 uyarlaması). Bu yüzden composite kolundaki X5C04/X5C07 satırlarında politika X = ML-DSA-65 ile örneklendi (NOTLAR N-3).

## 3. Karar kuralı (madde + inşa gerçeği → karar)

1. **İmza geçerliliği manifestten.** Her imzanın `insa` alanı üç değerli bir geçerliliğe çevrilir: geçerli / geçersiz / belirsiz. Dayanakları:
   - `bozuk` → geçersiz (RFC 7515 §5.2 adım 8).
   - Kayıtsız ya da desteklenmeyen alg (`ML-DSA-66`, `ML-DSA-65-P256`, `ml-dsa-65`, `X-KAYITSIZ-1`) → geçersiz [T319]. Büyük/küçük harf duyarlılığı RFC 7515 §4.1.1'dedir.
   - `none` → geçersiz (8725bis §3.2; RFC 9901 §4.1 [T102]).
   - K10 (başlık alg ≠ anahtarın algoritması) → geçersiz [T329], RFC 7515 §5.2 adım 8, RFC 9864 §7 [T335], RFC 7518 §3.4.
   - CMP bozulmaları: composite -04 §4.2, §4.3 [T345], Tablo 5 ve LAMPS -19 §4.3 (vektör başına tablo `karar_uret.py`'de `CMP_KURAL`).
   - CMP05 (asgari olmayan DER) ve CMP06 (artık bayt) → **belirsiz** (`BELIRSIZ.md` B-3).
   - CMP12/13 (bileşen imzası bağımsız alg olarak) → geçersiz. İmza M′ üzerinde üretilmiş; ES256/ML-DSA-65 doğrulaması JWS Signing Input üzerinde ve boş ctx ile yapılır (RFC 7518 §3.4; RFC 9964 §5 [T338]). Bileşen anahtarının bağımsız kullanımı yasaktır [T057].
2. **İmza kümesine yapılandırmanın kuralı uygulanır** (§2 tablosu). Üç değerli mantık kullanılır:
   - kesin bir başarısızlık varsa `reject`: W dışı imza (yalnız S'de), W içinde geçersiz imza ya da R karşılanmıyor;
   - kesin başarısızlık yoksa ve kararın bağlı olduğu bir geçerlilik belirsizse `indeterminate`;
   - ikisi de yoksa kabul.
3. **Aileye özgü yapısal koşullar birleştirilir.** Red her şeye baskındır. Belirsizlik yalnız kabulü belirsizleştirir:
   - SD-JWT VC `typ` (VC11: -13 SHOULD kabul, -19 SHOULD red);
   - x5c'nin başlıktaki yeri ve yinelenmesi (X5C07–X5C09);
   - güven çapasının x5c içinde olması (X5C06);
   - kid ile x5c çatışması (X5C10);
   - `crit` (RFC 7515 §4.1.11);
   - KB-JWT `sd_hash` bağlaması (RFC 9901 §8.1);
   - DPoP'ta alg kaydı ve `jwk` içinde özel anahtar (RFC 9449 §4.3 madde 5 ve 7);
   - x509_hash ve imzasız istek (OID4VP §5.9.3, A.2; HAIP §5.2).
4. **Etiket** §1'e göre verilir.
5. **Dayanak** kararı belirleyen maddelerle başlar, sonra yapılandırma tanımı gelir. Satır bir ÖK §6.5 vakasıysa (K1–K11, V±) o vakanın ÖK satırı da eklenir. Her alıntı betik tarafından korpus metninde bulunur ve satır numarası hesaplanır. Bulunamayan alıntı üretimi durdurur. Tam madde listesi URL'leriyle `maddeler.tsv`'dedir (107 madde).

**İnşa denetimi (`insa_denetimi.txt`, 467 denetim, hepsi geçti).** Kararın dayandığı her inşa gerçeği vektör dosyasının base64url çözümüyle doğrulandı:
- zaman: bütün `exp` > `simdi` ≥ `iat`; KB-JWT `iat` = simdi − 100 s; DPoP `iat` = simdi − 10 s;
- imza alg dizileri manifestle aynı;
- `typ` değerleri, x5c yeri, `crit` yeri, K10 başlık alg ≠ anahtar türü;
- DPoP `jwk` içinde `priv` yalnız DPOP10'da; TSL `sub`.

## 4. Birincil / ikincil ayrımı (ÖK §2G m.4)

- `sinif = birincil`: (vektör, kol) çifti `BATARYA-ESLEME.md` §1'de o kolda **birincil** olarak geçiyor. Yedek kol, köşeli parantezli `-ED25519` eşleriyle ve ortak dosyalarla (T3, VPLUS/VMINUS_ES256, VC10) doldurulur.
- `sinif = ikincil`: Geri kalan her şey. Bu, ESLEME'deki ikincil vektörleri, yalnız MR tablosunda geçen vektörleri (MR4 permütasyonları dahil) ve eşleme dışı vektörleri (UNK01–03, CRIT, DPOP, TSL, …) kapsar.
- `vaka` sütunu vektörün hangi vakaya ya da ilişkiye bağlandığını yazar: `K1`, `K5(ikincil)`, `MR1`, `MR4(T1K_both_valid)`, `MR4-dışı tanımlayıcı(…)`, `eşleme-dışı`.
- Birincil kapsam denetimi betikte yapılır. Her birincil (vektör, kol) için `L4` satırı vardır. V± için `GEC`, K8/K9 için `L4-YOL` satırı da vardır.

## 5. Kapsam dışı ve uygulanamaz hücreler

- **B6 (desteklenmeyen biçim):** General JSON ve flattened JSON vektörlerinde karar, hedefin bu serileştirmeyi desteklediği varsayımıyla verilir. Desteklemeyen hedefteki gözlem "uygulanamaz" olur, oracle sapması sayılmaz (ÖK §4.13 B6). Bunun dayanakları: RFC 9901 §8 "OPTIONAL", HAIP §6.1 "JSON serialization MAY", 8725bis §3.14 (JWT kütüphanesinin JSON girdiyi reddetmesi).
- **Composite X.509:** Kapsam dışı (ÖK §2D m.1, "HAIP §6.1.1 sapması"). Composite nesneler kid/JWKS ile çözülür.
- **Durum listesi denetimi:** VC vektörleri `status` (idx 7) taşır. Durum listesi ayrı bir vektördür (TSL); SD-JWT VC §2.4'e göre denetim SHOULD'dur. Oracle kararı durum listesine bağlanmadı.
- **Satır sayısı** (vektör × yapılandırma × kol): **858.** Bütün 153 vektör en az bir satırla kapsandı.

## 6. Üretim ve doğrulama

```bash
cd <proje_koku>
PYTHONIOENCODING=utf-8 python deney/oracle/oracle-A/karar_uret.py "$(cygpath -w "$PWD")"
sha256sum -c deney/oracle/oracle-A/SHA256SUMS
```

- **Çıktılar:** `karar.tsv`, `maddeler.tsv`, `karar_ozet.json`, `insa_denetimi.txt`.
- **Belirlenimcilik:** Betik rastgelelik, saat ya da ağ kullanmaz. İki koşu bayt-aynıdır (`SHA256SUMS` ile denetlenir).
- **`karar.tsv` sütunları:** `vektor_id`, `politika`, `kol`, `sinif`, `vaka`, `karar`, `dayanak`, `not`.
  - `dayanak` biçimi: `[Tnnn] BELGE §bölüm (sürüm; metin/BELGE.txt:satır): "birebir alıntı"`, birden çok madde ` | ` ile ayrılır.
  - `not` sütunu `insa:` özetiyle başlar ve kararın gerekçesini verir. Yalnız bilgi amaçlı madde anıları (ör. B6) `not`'ta köşeli parantez içindedir.
