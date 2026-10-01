# YÖNTEM — Oracle B (Adım 9, görev 6)

> **Çalışma:** Oracle B (N-sürüm oracle'ın B kolu; ÖK §4.20). **Tarih:** 25.09.2026.
> **Çıktı klasörü:** `deney/oracle/oracle-B/` (yalnız buraya yazıldı).
> **Durum:** Türetme. Hiçbir hedef kütüphane koşulmadı, hiçbir vektör dosyası açılmadı ya da doğrulanmadı. Kararlar yalnız (i) birincil spesifikasyon maddelerinden ve (ii) `MANIFEST.json` içindeki `insa` / `dogrulama_girdileri` gerçeklerinden çıkarıldı.

---

## 1. Amaç

C3 ölçümünde hedeflerin kararlarının karşılaştırılacağı **politika-parametrik, dört değerli** beklenen kararı (ÖK Ö6: `accept-classical`, `accept-hybrid`, `reject`, `indeterminate`) v1.2 bataryasının her vektörü × politika yapılandırması × kol için üretmek. L4 oracle'ının maddelerden türetilmesi ayrıca `L4-TURETME-B.md`'dedir.

## 2. Bağımsızlık protokolü

- `deney/oracle/oracle-A/` ve `deney/oracle/` kökündeki başka hiçbir şey **listelenmedi ve okunmadı**. Yalnız `mkdir -p deney/oracle/oracle-B` çalıştırıldı.
- `referans/` (pilot dahil), `model/`, `gozden-gecirme/`, `IS-PLANI.md` **açılmadı**.
- Açılan her dosya ve kapsamı `ERISIM-KAYDI.md`'de. ÖK'nin §2D B bölümü (m.9–17; biçimsel kısım sonuçları) okunan parçaya denk geldi; türetmede **kullanılmadı** (bkz. `L4-TURETME-B.md` §0).
- Ağ erişimi, Docker, git kullanılmadı. Kişisel veri hiçbir yere gönderilmedi.

## 3. Sabit girdiler

| Girdi | SHA-256 |
|---|---|
| `deney/uretec/vektorler/v1.2/MANIFEST.json` | `bb17aaa76a3d1859b2dd5df54c62e7039948a715e2c4b4628fed82d184c6e738` (ÖK §2G m.2 ile aynı) |
| `deney/uretec/vektorler/v1.2/SHA256SUMS` | `92663b48f477f51e5a4cdd2a6942d97d36b2d9591fa67af451fd33eb14f0b2a3` (ÖK §2G m.2 ile aynı) |
| `deney/uretec/BATARYA-ESLEME.md` | `d73352179cdf281825d498000b7f9dc6d1df0fe835c8258c6aa2c516e659e3fc` (ÖK §2G m.2 ile aynı) |
| `00-on-kayit/ON-KAYIT-TASLAK.md` (v0.8, okunduğu hâl) | `dcc84092e2ca5eee0fcca8277fbcbd6b06ff613dc3459f63195f44d1ce3df79a` |

Korpus dosyalarının özetleri §8'de.

## 4. Politika yapılandırmalarının türetilmesi (ÖK §4.13 + §6.5, §4.8 ve §2B m.6'dan)

### 4.1 Girdi maddeler (ÖK)

- **§6.5:** "Birinci imza A = ES256." (s. 1048); "İhraççı başına gerekli küme R = {X}, izinli küme {A, X}." (s. 1054). X: kontrolde EdDSA; tedavide ML-DSA-65 ya da composite -04.
- **§4.13:** L0–L5 basamakları; L4 = "Yapılandırılmış hâlde K1 KABUL, K2 RED, K3 RED" (s. 844). Ek bayrak **B5 semantik sınıf: "en-az-biri-geçerli / mevcut-tümü-geçerli / gerekli-küme / diğer"** (s. 859).
- **§2B m.6:** L4m (çoklu imza; "PQ bileşeni yoksa ret") ve L4c (yalnız kompakt; aynı doğrulayıcıda ihraççı başına "PQ/composite zorunlu"; "Göç etmiş ihraççının yalnız klasik imzalı belgesi reddedilir, eski ihraççının klasik imzalı belgesi kabul edilir.") (s. 255–257).
- **§4.8:** P0 any-valid; P1 all-present-valid ("İmza silinmesi (soyma) fark edilmez"); P2 = P1 + anahtar–alg bağlama; P3 = P2 + ihraççı başına R_I (klasik kanal); P4 = P3 (PQ kanal) (s. 775–779).
- **§6.4:** F_K/F_T "en iyi ulaşılabilir yapılandırmada" K1–K3'te oracle'dan sapma; D_soy varsayılan yapılandırmada K3 kabulü (s. 1043–1044).

### 4.2 Türetilen yapılandırmalar

Her kolda X kolun ikinci algoritmasıdır; **izinli = {ES256, X}** üç yapılandırmada da ortaktır (§6.5). Üç yapılandırma, B5'in üç adlandırılmış sınıfına ve §4.8'in kütüphane düzeyinde ayırt edilebilen politikalarına birebir karşılık gelir:

| Kod (`politika`) | Tanım | ÖK karşılığı | Kabul kuralı |
|---|---|---|---|
| **`L4`** (birincil) | R_I = {X}, izinli = {ES256, X}, anahtar–alg bağlama | §6.5 politikası; §4.13 L4; §2B m.6 L4m ve L4c'nin "göç etmiş ihraççı" yarısı; §4.8 P3 ≡ P4; B5 "gerekli-küme" | Mevcut **her** imza izinli bir alg ile, o alg'e bağlı anahtarla geçerli **ve** R_I'deki her alg için geçerli bir imza var |
| **`P2`** | R_I = ∅, izinli = {ES256, X}, anahtar–alg bağlama | §4.8 P1/P2; §2B m.6 L4c'nin "eski ihraççı" yarısı; B5 "mevcut-tümü-geçerli" | Mevcut **her** imza izinli alg ile geçerli (en az bir imza) |
| **`P0`** | R_I = ∅, izinli = {ES256, X}, anahtar–alg bağlama | §4.8 P0; RFC 7515 §5.2 asgarisi; B5 "en-az-biri-geçerli" | **En az bir** imza izinli alg ile geçerli |

**Gerekçeler:**
1. **Neden üç yapılandırma?** ÖK'nin önceden kayıtlı B5 bayrağı hedefin çoklu imza semantiğini üç adlandırılmış sınıfa ayırır. Bir hedefin sınıfını belirlemek için her sınıfın beklenen kararı gerekir; bu yüzden oracle, bu üç sınıfın her biri için karar üretir. H6 metni de başarısızlıkların "en az biri geçerli" ve "mevcut tümü geçerli" modlarına ayrılacağını söyler (§2 H6).
2. **Neden `P1` değil `P2`?** 8725bis §3.1 anahtar–alg tutarlılığını **kütüphane** yükümlülüğü olarak koşulsuz koyar (`JWTBCP.txt:468-471`). Uyumlu bir kütüphane için bağlamasız P1 yapılandırması yoktur; bu yüzden P1 ≡ P2 ve kod `P2`'dir. Aynı nedenle `P0` da bağlama içerir (K10 her yapılandırmada `reject`).
3. **Neden P3 ile P4 ayrılmıyor?** P3/P4 farkı R_I'nin hangi kanaldan öğrenildiğidir. Kütüphane R_I'yi API yapılandırmasıyla alır; kanal kütüphanenin gözlem alanı dışındadır. Kütüphane düzeyinde P3 ≡ P4 ≡ `L4`.
4. **L4c nereye düşer?** L4c'nin iki yarısı iki ayrı yapılandırmadır: göç etmiş ihraççı = `L4`; eski ihraççı = `P2` (tek imzalı belgelerde `P2` ≡ `P0`). Tek imzalı (kompakt) vektörlerde bu iki satırın karşılaştırması L4c'nin davranış ölçütünü verir (ör. `VPLUS_ES256`: `L4` → `reject`, `P2` → `accept-classical`).
5. **Neden "varsayılan yapılandırma" oracle'ı yok?** D_soy (§6.4) ve L5 oracle ile karşılaştırılmaz; doğrudan gözlemdir. Varsayılan davranış spesifikasyonda tanımlı değildir (8725bis §3.1 yalnız "mekanizma sağla" der). Ayrı bir varsayılan satırı büyük ölçüde `indeterminate` üretirdi ve önceden kayıtlı hiçbir değişkene girmezdi.
6. **L1–L3 davranış ölçütleri:** L1 ("izinsiz algoritma reddediliyor") üç yapılandırmada da ortak izinli kümeyle sınanır (ör. `UNK01/03`, `VC04/05`, `CMP14/15` her yapılandırmada `reject`). L3 ölçütü K10 her yapılandırmada `reject`.

### 4.3 `L4`'te "mevcut her imza geçerli" koşulu neden var?

Kaynak: ÖK §4.8'de P3 = P2 + R_I ve P2 = P1 + bağlama, P1 = "Mevcut imzaların tümü geçerliyse kabul" (kümülatif tanım). Ayrıca "composite AND" öncülü: composite -04 §4.3 "MUST validate a signature only if all component signatures were successfully validated" ve ACM2 Note 51 "the veriﬁcation function accepting if and only if all signatures are correct". Ayrıntılı türetme `L4-TURETME-B.md` §2'de. Sonuç: `L4`'te izinli olmayan ya da geçersiz **ek** bir imza (K5) kararı `reject` yapar; `P0`'da aynı vektör kabul edilir. Bu, MR2'nin ("etkisi politikaya göre öngörülebilir") beklediği politika bağımlılığıdır.

## 5. Kollar ve vektör–kol ataması

| `kol` | X | izinli |
|---|---|---|
| `kontrol-EdDSA` | EdDSA | {ES256, EdDSA} |
| `kontrol-Ed25519` (ÖK §2D m.2 yedek) | Ed25519 | {ES256, Ed25519} |
| `tedavi-ML-DSA-65` | ML-DSA-65 | {ES256, ML-DSA-65} |
| `tedavi-composite` | ML-DSA-65-ES256 | {ES256, ML-DSA-65-ES256} |

- `alg` karşılaştırması harfe duyarlıdır ve etiket bazlıdır (RFC 7515 §4.1.1). `kontrol-EdDSA`'da `Ed25519` etiketli imza izinli değildir, tersi de geçerlidir (ÖK §2E m.3'teki araç olgusuyla tutarlı).
- **Atama kuralı:** Manifestteki `kol` dört koldan biriyse vektör yalnız o kolda değerlendirilir. `kol` ∈ {`ortak`, `klasik-taban`, `kapsam-pq`, `kapsam-hibrit`, `null`} ise dört kolun hepsinde değerlendirilir (bu vektörlerin kararı kolun X'ine bağlı olabilir ya da kol-bağımsızdır; her iki durumda da satırlar açıkça yazılır).
- **Eşlemeden gelen ek kol atamaları** (`BATARYA-ESLEME.md`): `X5C04` ve `X5C07` → ayrıca `tedavi-composite` (K8/K9 birincil sütunu); `K10K_alg-ES256_anahtar-Ed25519` → ayrıca `kontrol-Ed25519` (yedek kolda eşi yok, aynı dosya); `VC10_ikili_ihrac` → dört kol (K11 birincil, "politika kola göre").

## 6. Karar kuralı

### 6.1 İmza düzeyi

Her imza s için, kolun izinli kümesi altında:
- `alg(s)` izinli değilse → s **doğrulanmaz** ve geçersiz sayılır (8725bis §3.1 "MUST NOT employ any algorithms outside this configured set"; RFC 7515 §4.1.1 "not valid if the "alg" value does not represent a supported algorithm").
- `alg(s)` anahtarın bağlı olduğu algoritmayla tutarsızsa → geçersiz (8725bis §3.1; RFC 9964 §3 AKP anahtarında `alg` zorunlu).
- `insa` "gecerli" değilse (bozuk bayt, kayıtsız etiketin rastgele baytı, `none`) → geçersiz.
- Composite imza, ancak iki bileşen de doğru kodlanmış ve doğru M′/ctx üzerinde geçerliyse geçerlidir (composite -04 §4.2–§4.5.1).

### 6.2 Belge düzeyi

`P0`, `P2`, `L4` §4.2'deki kabul kurallarıyla uygulanır. Çoklu imzada imzaların sırası kararı etkilemez (RFC 7515 §5.2 adım 9–10 her imzayı ayrı doğrular; §7.2.1 her imzayı kendi başlığıyla hesaplar). Bu yüzden MR4 eşlerinin kararı kaynaklarınınkiyle aynıdır.

### 6.3 Dört değerli çıktı semantiği (ÖK Ö6 değerleri; ÖK'de semantik tanımlı değil — `KARAR-NOTLARI.md` N1)

| Değer | Bu oracle'daki anlamı |
|---|---|
| `accept-hybrid` | Kabul; kabulün dayandığı geçerli ve izinli imzalar arasında **en az bir PQ sınıfı bileşen** (ML-DSA ya da composite) var. Saf PQ kabulü (ör. K4 tedavi) de bu değere düşer; ayrı bir "accept-pq" değeri yok. |
| `accept-classical` | Kabul; kabul yalnız klasik imzalara dayanıyor. Kontrol kolunda X = EdDSA klasik olduğundan kontrol kolundaki her kabul `accept-classical`'dır. |
| `reject` | İlgili maddeler ve yapılandırma altında kabul yolu yok. |
| `indeterminate` | Maddeler kararı belirlemiyor: hem kabul hem ret uyumlu (MAY/SHOULD düzeyi, tanımsız yorum, eksik bağlam). Her `indeterminate` satırın nedeni `BELIRSIZ.md`'de. |

- **Karşılaştırma eşlemesi:** Hedef çıktısı ikili ise (kabul/ret), `accept-*` → kabul. `indeterminate` satırlar sapma hesabına girmez (ÖK §4.15 "belirsiz" sınıfı).
- **Belirlenmişlik eşiği:** Karar ancak MUST / MUST NOT / REQUIRED düzeyinde bir madde ya da yapılandırmanın kendi tanımı zorluyorsa belirlenmiş sayılır. SHOULD/RECOMMENDED/MAY düzeyi tek başına kararı belirlemez; yönü `not`'ta yazılır.
- `accept-hybrid` etiketi yalnız JWS/imza katmanını sınıflar. Sertifika yolunda klasik kenar varsa (K8) bu `not`'ta ve B2 bayrağı üzerinden raporlanır.

### 6.4 Belirleme için kullanılan bağlam varsayımları (insa + dogrulama_girdileri)

- `insa` alanında "gecerli" yazan her yapı (imza, zincir, SD-JWT ifşaları, zaman talepleri, `typ`) geçerli üretilmiş kabul edilir; bu türetme vektör dosyası açmaz.
- Anahtar çözümleme: JWS çekirdek, SD-JWT VC (kid), DPoP ve istek vektörlerinde `dogrulama_girdileri`'ndeki anahtar/JWKS (ÖK §2D m.1, D-S1). **X5C ailesinde** anahtar `x5c` üzerinden çözümlenir (ÖK §2D m.1: "zincir davranışı yalnız X5C vektörlerinde ... ölçülür"). Composite kimlik bilgilerinde x5c olmaması "HAIP §6.1.1 sapması" etiketiyle kabul edilir (ÖK §2D m.1).
- KB-JWT algoritması da kolun izinli kümesine tabidir; R_I yalnız ihraççı (imzalayan varlık) imzasına uygulanır.
- İstek nesnesi (REQ), durum listesi (TSL) ve DPoP vektörlerinde R_I, imzalayan varlığa (RP, durum ihraççısı, DPoP istemcisi) **benzetmeyle** uygulanır; DPoP için bu, RFC 9449 §4.3(5)'teki "acceptable per local policy" koşuludur. Bu satırlar önceden kayıtlı değişkenlere girmez.

## 7. Özel durumlar ve sürüm boyutu

- **SD-JWT VC sürümü** (`sdjwtvc_surum`, ÖK Ö9 ve §2D m.7): Parametrenin kapsamı "senaryo (d) vektörleri (JSON serileştirmenin statüsü) ve VC11" (§2D m.7). Bu vektörlerde (`VC07/08/09` ailesi ve permütasyonları, `VP05/06/07`, `VP05-SIRA-ters`, `VC11`) her yapılandırma iki satıra bölünür: `…|sdjwtvc=-13` ve `…|sdjwtvc=-19`. Diğer SD-JWT VC vektörlerinde karar iki sürümde aynıdır; `politika` sürüm eki taşımaz ve `not` bunu belirtir. Manifestte yalnız `-13` için tanımlı düzleştirilmiş JSON vektörleri (`X5C07/08/09`, `CRIT02`) `-13` okumasıyla tek satırdır.
- `-19`'da JSON serileştirilmiş SD-JWT VC'nin ayrıntıları "beyond the scope" olduğundan kabul yolu olan kararlar `indeterminate` olur; kabul yolu olmayan (`reject`) kararlar değişmez.
- JSON serileştirmeyi desteklemeyen hedefte bu satırlar B6 ("uygulanamaz") kapsamındadır; oracle, biçimi destekleyen doğrulayıcının kararını verir.
- Vektöre özgü kurallar (CMP, X5C, CRIT, VP, REQ, DPoP, VC11/VC12) `karar.tsv`'nin `dayanak` ve `not` sütunlarında, belirsizler `BELIRSIZ.md`'de.

## 8. Dayanak biçimi ve alıntı doğrulaması

- Biçim: `BELGE §bölüm [matris kimliği varsa Tnnn] “birebir kısa alıntı” (sürüm; dosya:satır)`. Birden çok madde ` ; ` ile ayrılır. Matris kimlikleri `02-izlenebilirlik/izlenebilirlik.csv`'deki satırlardır.
- Her alıntı, betik tarafından kaynak dosyada **verilen satır aralığında, boşluk normalize edilerek alt dize olarak** aranır; bulunamayan alıntı betiği durdurur (`turet_karar.py`, `alinti_denetimi()`). Satırlar yalnız `
`'de bölünür (grep/sed numaralamasıyla aynı; sayfa sonu karakterleri satır saymaz). Satır sonundaki tire boşluksuz birleştirilir (RFC metinlerinde gerçek tiredir: `case-`/`sensitive`, `ML-DSA-`/`65`). Dayanaktaki alıntı kaynak metnin birebir alt dizesidir; yalnız satır kırılımları tek boşluğa indirgenmiştir. `L4-TURETME-B.md` ve `BELIRSIZ.md`'deki uzun alıntılar da aynı yöntemle ayrıca doğrulandı.
- Atıf yapılan belgeler (sürüm; SHA-256):

| Kısa ad | Belge | SHA-256 (`01-korpus/metin/…`) |
|---|---|---|
| JWTBCP | draft-ietf-oauth-rfc8725bis-10 (21.08.2026) | `0f20c55d5d4094225d57f68db16061659c7e31a617b32f192839669950cd1339` |
| JOSECOMP | draft-ietf-jose-pq-composite-sigs-04 (10.09.2026) | `f23f9ad996ac1f85e1d39584a03554754cc74e0a07f186d1288e009d9578250d` |
| LAMPSCOMP | draft-ietf-lamps-pq-composite-sigs-19 (21.04.2026) | `bedaa29011c2e076c7f7e47f46c03caf5b1283d41cf5d01f7685f38dfaa014f8` |
| RFC9964 | RFC 9964 (Mayıs 2026) | `00470379e12eeae80e37872b2b4b3163831c572dbfa90b9dc9a9a9eb0c92aa28` |
| RFC7515 | RFC 7515 (Mayıs 2015) | `dd12efc0e7f03477160e4f9e1a939897341a97684f9addf66c7fbfa7bab9040c` |
| RFC9864 | RFC 9864 (Ekim 2025) | `52748a942507056e471b29e37baabcd7b15eb75ea78a2fda89cc4dee1dea8cbe` |
| RFC9901 | RFC 9901 (Kasım 2025) | `072bfcdbd4c89f70004198a788b161bb25c341393d38232ea7dd7f2d360efbf0` |
| SDJWTVC | draft-ietf-oauth-sd-jwt-vc-19 (31.08.2026) | `4c05560e1f698ed7e40bbb710bb5accfb8126d647b769d45d8653834e35f49e6` |
| SDJWTVC13 | draft-ietf-oauth-sd-jwt-vc-13 (06.11.2025) | `d71c0078c2d8004cf5d8b0fc400585d5869c8fa6bbff06ecd7da23bf26b7f61d` |
| HAIP | OpenID4VC HAIP 1.0 Final (24.12.2025) | `37057efeac8a434699e15c2b723abc8076aa6b3a7775497627334f3e442809d0` |
| OID4VP | OpenID4VP 1.0 Final (09.07.2025) | `e0a2ae4ccc1bdda8ab6536be10c5e823c661fbef9813452df30ffc30cc101fa9` |
| RFC9449 | RFC 9449 (Eylül 2023) | `e09416d29421414ac0ee47b81726538e9bc8cd20af2dcfae1a10bc337537a769` |
| TSL | draft-ietf-oauth-status-list-21 (21.06.2026) | `8bc7b293f92e4c38a4a04110276bc012de114026c3cd3a7d1b5b6a2dae0449f1` |
| ACM2 | ECCG Agreed Cryptographic Mechanisms v2.0 (Nisan 2025) | `8d731a28dc0fd63b0f34e5bffd675163f4aed6ee37e3ef530769b451f6584e71` |
| ÖK | ON-KAYIT-TASLAK v0.8 | `dcc84092e2ca5eee0fcca8277fbcbd6b06ff613dc3459f63195f44d1ce3df79a` |
| Matris | `02-izlenebilirlik/izlenebilirlik.csv` | `79b6b19e9f06865888cde9f4a6a1ff441f6aa607f1f98dfd39a6d7492ef0c26d` |

## 9. Birincil / ikincil

- `birincil_mi = evet`: (vektör, kol) çifti `BATARYA-ESLEME.md` §1'de o kol sütununda **birincil** olarak geçiyor (yedek `-ED25519` eşleri ve V+/V− dahil). ÖK §2G m.4: önceden kayıtlı değişkenler yalnız bunlardan hesaplanır.
- `birincil_mi = hayır`: eşlemede ikincil, yalnız MR eşi (MR1/MR3/MR4) ya da eşleme dışı. Bunların `not`'unda rolü yazılır.

## 10. Çıktı biçimi

- `karar.tsv`: UTF-8, sekmeyle ayrılmış, **alıntı karakteri yok** (okurken `csv.QUOTE_NONE` kullanın). Alanlarda sekme ve yeni satır yoktur (betik denetler). Başlık satırı: `vektor_id politika kol birincil_mi karar dayanak not`.
- Satır sırası: kol → vektör (manifest sırası) → politika (`L4`, `P2`, `P0`; sürüm ekli olanlarda önce `-13`).

## 11. Araç ve yeniden üretim

- `turet_karar.py` (Python 3, yalnız standart kütüphane): vektör başına elle yazılmış olgu tablosunu (imza listesi manifestle **çapraz denetlenir**) ve özel kuralları uygular; alıntıları kaynak metinde doğrular; `karar.tsv` ve dağılım özetini üretir. Vektör dosyası açmaz; ağ kullanmaz.
- Çalıştırma: `PYTHONIOENCODING=utf-8 python turet_karar.py` (klasör kökünden, proje kökünü otomatik bulur).
- Artımlı üretim: `--kollar k1,k2,…` seçeneğiyle kollar birikimli olarak yazıldı (kontrol-EdDSA → + kontrol-Ed25519 → + tedavi-ML-DSA-65 → + tedavi-composite); her koşum `karar.tsv`'yi seçili kolların kanonik sırasıyla yeniden yazar. Son hâl dört kolun birleşimidir (seçeneksiz koşum).

## 12. Sınırlılıklar

- Kararlar spesifikasyon ve ÖK maddelerinin bu çalışmanın okumasıdır; oracle A ile uyuşmazlık "belirsiz" sınıfına girer (ÖK §4.15).
- `insa` gerçekleri doğru kabul edildi (üreteç öz-doğrulaması T10 ve yürütücü yeniden üretimi ÖK §2G m.3'te).
- REQ/TSL/DPoP satırlarındaki R_I benzetmesi önceden kayıtlı değildir; bu satırlar tanımlayıcıdır.

## 13. Sonuç özeti (`turet_karar.py` çıktısı, 25.09.2026)

- **732 satır**; 153 vektörün hepsi; 53 birincil (vektör, kol) çifti × 3 yapılandırma = 159 birincil satır. Sürüm ekli satır: 96 (§7).
- Alıntı denetimi: betikteki 116 maddenin hepsi kaynak satır aralığında bulundu. Manifest çapraz denetimi: `insa` değeri "gecerli" olmayan her imza için elle yazılmış durum var; bütün kimlikler manifestte.
- İki bağımsız koşum aynı `karar.tsv` özetini verdi (belirlenimci).

| Kesit | Satır | accept-classical | accept-hybrid | reject | indeterminate |
|---|---|---|---|---|---|
| Tümü | 732 | 169 | 101 | 373 | 89 |
| Birincil (birincil_mi = evet) | 159 | 48 | 23 | 88 | 0 |
| İkincil / MR / eşleme dışı | 573 | 121 | 78 | 285 | 89 |
| politika L4 (sürüm ekli dahil) | 244 | 14 | 29 | 172 | 29 |
| politika P2 (sürüm ekli dahil) | 244 | 64 | 29 | 121 | 30 |
| politika P0 (sürüm ekli dahil) | 244 | 91 | 43 | 80 | 30 |
| kol kontrol-EdDSA | 144 | 56 | 0 | 76 | 12 |
| kol kontrol-Ed25519 | 144 | 56 | 0 | 76 | 12 |
| kol tedavi-ML-DSA-65 | 246 | 31 | 62 | 106 | 47 |
| kol tedavi-composite | 198 | 26 | 39 | 115 | 18 |

- ÖK §4.13 L4 ölçütü (K1 KABUL, K2 RED, K3 RED) dört kolun `L4` satırlarında türetmeden **çıktı** (girdi olarak verilmedi); tablo `L4-TURETME-B.md` §3.
- Birincil satırlarda `indeterminate` yok; 89 belirsiz satırın hepsi tanımlayıcı vektörlerdedir (`BELIRSIZ.md`).
