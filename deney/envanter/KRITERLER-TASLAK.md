# C3 dahil etme ölçütleri — TASLAK (Adım 9a; ön kayda girecek)

> **Durum:** Taslak. Ön kayıt dondurulmadan önce yürütücünün onayına sunulur.
> **Kapsam:** Yalnız çerçeve ve meta veri. Bu belgedeki hiçbir karar kütüphane **davranışına** dayanmaz. Davranış ölçümü (adaptör, test vektörü) ön kayıt dondurulduktan sonra yapılır.
> **Kaynak:** Bütün sayılar `topla.py` çıktılarından gelir: `CERCEVE.csv`, `SECIM.csv`, `ESIK-DUYARLILIK.csv`, `TARAMA.csv`, `topla_kayit.json`. Anlık görüntü 23–24.09.2026 tarihlidir; ham yanıtlar `onbellek/` altındadır.
> **Ön kayıt kararıyla uyum (ÖK §2A Ö6):**
> - Referans doğrulayıcılar (REF) n'nin **dışında** tutulur ve ayrı raporlanır.
> - Tedavinin ana kolu composite -04, ikincil kolu saf ML-DSA-65'tir.
> - Oracle dört değerlidir: accept-classical / accept-hybrid / reject / indeterminate.

---

## 0. Birim, popülasyon, tabakalar

- **Birim (hedef):** JWS, COSE ya da SD-JWT imzasını **asimetrik** olarak doğrulayan bir yazılım kütüphanesi ya da bir OpenID4VP doğrulayıcısı (RP).
  - Bir kod tabanından (depodan) **tek** birim alınır.
  - Çok paketli depolarda birim, doğrulama API'sini taşıyan paket ya da modüldür (`paket_adi`, `alt_dizin`).
- **Popülasyon:** Çerçeve tarihinde (**REF_TARIH = 23.09.2026**) açık kaynak olarak erişilebilen ve §1'deki kaynaklardan en az birinde görünen hedefler.
- **Tabakalar.** Bir birim tek tabakaya girer. Atama önceliği yüksekten düşüğe şöyledir:
  1. **REF:** OID4VP doğrulayıcısı ya da doğrulayıcı rolü olan OID4VC yığını. **n'ye girmez**, ayrı raporlanır.
  2. **SDJWT:** Birincil amacı SD-JWT / SD-JWT VC olan kütüphane.
  3. **COSE:** Birincil amacı COSE (RFC 9052) olan kütüphane.
  4. **JOSE:** Genel JWS/JWT kütüphanesi.
- **Örneklem büyüklüğü:** n = JOSE + SDJWT + COSE.
- SD-JWT desteği olan genel JOSE kütüphaneleri JOSE tabakasında kalır; `sd_jwt` sütunu bu desteği ayrıca gösterir.

## 1. Çerçeve kaynakları (tanımlama)

| Kod | Kaynak | Tam tanım | Gürültü tabanı |
|---|---|---|---|
| **J** | jwt.io kütüphane listesi | `jsonwebtoken/jsonwebtoken.github.io@60b70f7d8d20` içindeki `src/data/libraries-next.json` (SHA-256 `3b1573be…5477`). **37 dil, 110 girdi, 107 benzersiz depo** (104 GitHub + 3 Bitbucket). `panva/jose` 4 dil başlığında yinelenir. Denetim A'nın "106" sayısıyla 1 fark vardır; sayım anının ve normalleştirmenin farkından kaynaklanması olası | yok; hepsi aday |
| **H** | Halef kuralı | Kullanımdan kalktığını ve **açık bir halef** gösterdiğini beyan eden adayın halefi de çerçeveye girer: square/go-jose → go-jose/go-jose; authlib.jose → authlib/joserfc; sd-jwt-js → identity-common-ts; Sphereon SSI-SDK → Sphereon IDK | yok |
| **P** | Pilot kümesi | Sürüm 3 §9.2: `jose`, `@sd-jwt/core`, `jwcrypto`, `Authlib`, `joserfc` | yok |
| **T** | GitHub konu aramaları | `topic:sd-jwt`, `topic:sd-jwt-vc`, `topic:cose`, `topic:oid4vp`, `topic:openid4vp` (arama API'si, yıldıza göre, ilk 100) | ≥5★ |
| **K** | Paket kaydı aramaları | npm (`text=sd-jwt`, `keywords:cose`, `text=cose`), crates.io, NuGet, Packagist, Maven Central, RubyGems, pub.dev, pkg.go.dev; PyPI için ad yoklaması (`sd-jwt`, `pyeudiw`, `pycose`, `cwt`, `joserfc`) | npm ≥100/ay; crates ≥300/90 gün; NuGet ≥1.000 toplam; Packagist ≥50 toplam; RubyGems ≥1.000 toplam; pub.dev ≥100/30 gün; Go: depo ≥5★. Ad ya da açıklamada SD-JWT/COSE geçmeli |
| **O** | Kuruluş listeleri | `eu-digital-identity-wallet`, `openwallet-foundation`, `openwallet-foundation-labs`, `cose-wg` (ecosyste.ms). Ad/açıklama süzgeci: `sd-?jwt\|cose\|verifier\|openid4vp\|oid4vp\|oid4vc\|jose\|jws` | süzgeç |
| **G / Gt** | Plan ve görev tanımı | G: Sürüm 3 §9.2'deki referans doğrulayıcılar (EUDI, ACA-Py `oid4vc`, Credo `openid4vc`). Gt: Adım 9a görev tanımında adı geçenler (walt.id, Sphereon, Spruce, EUDIPLO) | yok |

- **Tanımlama akışı.** 386 arama isabeti gürültü tabanından geçti ve 306 tarama satırına indi. Tarama kararları şöyle dağıldı:

  | Karar | Sayı |
  |---|---|
  | aday | 91 |
  | ilgisiz | 60 |
  | taban-altı | 46 |
  | uygulama | 33 |
  | yinelenen | 32 |
  | belge | 26 |
  | cüzdan | 9 |
  | mdoc | 5 |
  | ihraççı | 3 |
  | jwt.io ile yinelenen | 1 |

  Çerçeve toplamı **198 aday**: JOSE 109, SDJWT 29, COSE 37, REF 23.
- **Bilinçli dışarıda bırakılan sorgu:** `topic:selective-disclosure`. İsabetleri çoğunlukla SD-JWT dışı yaklaşımlardan (BBS, ZK, Merkle) geliyor.
- **Bilinen kapsam boşluğu:** JOSE çerçevesi jwt.io'dur. Bu listede olmayan bazı yaygın kütüphaneler çerçevenin dışında kalır: `fast-jwt`, `josekit`, `jwt-simple`, `did-jwt`, `erlang-jose`, `SimpleJWT`. Bu durum sınırlılık olarak yazılır.

## 2. Tarama (ilgililik; K7)

Her isabet `tarama_kararlari.csv`'de kararı ve gerekçesiyle kayıtlıdır; tümü `TARAMA.csv`'dedir.

| Karar | Tanım |
|---|---|
| `aday` | Doğrulama API'si olan kütüphane ya da RP doğrulayıcısı |
| `yinelenen` | Aynı kod tabanı: halef ya da öncül, çatal, alt paket, yeniden paketleme, tür tanımı |
| `uygulama` | Uygulama, demo, oyun alanı, hata ayıklama aracı, ürün/hizmet SDK'sı, eklenti |
| `cuzdan` / `ihracci` | Cüzdan tarafı ya da ihraççı hizmeti. C3, RP doğrulayıcılarını ölçer |
| `kapsam-disi-mdoc` | mdoc / ISO 18013-5 / ISO 23220-4 (Sürüm 3 §7.4) |
| `belge` | Spesifikasyon, taslak, WG ya da örnek deposu |
| `ilgisiz` | Yalnız CBOR ya da COSE_Key işleyen kütüphane; başka protokol (EDHOC, WebAuthn, FDO, SCITT); uygulamaya özgü kod |
| `taban-alti` | Gürültü tabanının altında kalan isabet |

## 3. Dahil etme ölçütleri (uygunluk)

Bir aday ancak **K1–K8'in hepsini** sağlarsa "uygun" sayılır.

| Kod | Ölçüt | İşlemsel tanım | Veri kaynağı |
|---|---|---|---|
| **K1** | Asimetrik doğrulama | JWS/COSE/SD-JWT imzasını en az bir asimetrik algoritmayla (RS/PS/ES/EdDSA/ML-DSA) doğrular | J: jwt.io `support` bayrakları. Diğerleri: belge |
| **K2** | Etkinlik | Varsayılan dalın HEAD commit'i (committer tarihi) ≥ **2024-09-23** (REF_TARIH − 24 ay) | `git clone --depth 1 --filter=tree:0` (anonim; kimlik yardımcıları kapalı); Bitbucket API; yedek: ecosyste.ms `pushed_at` |
| **K3** | Bakım durumu | Arşivlenmemiş olmalı; README ya da kayıtta "deprecated / not maintained / moved / legacy" beyanı bulunmamalı | ecosyste.ms `archived`; README; `elle_bayraklar.csv` |
| **K4** | Açık lisans | OSI onaylı bir lisans (SPDX). Kaynaklar sırayla okunur: deps.dev → ecosyste.ms → paket kaydı. İlk **geçerli** değer alınır; deps.dev'in "non-standard" dediği birkaç depo diğer kaynaktan çözülür (ör. go-cose → MPL-2.0) | `lisans`, `lisans_kaynagi` |
| **K5** | Popülerlik eşiği | §4'teki eşik. Göstergeler "ya da" ile bağlanır: yıldız, aylık indirme, bağımlı paket (ecosyste.ms). Aylık istatistik yayımlamayan kayıtlarda (NuGet, RubyGems) toplam ≥ 12 × aylık eşik. **İstisnalar:** (a) SDJWT ve REF'te resmî referans uygulamalar (EUDI, OWF, OWF-Labs); (b) REF'te plan kaynaklılar (G). Tek bir büyük tek-deponun (monorepo) küçük bileşenlerinde depo yıldızı kullanılmaz (dotnet/runtime, poco, mORMot, catalyst-voices) | `CERCEVE.csv` |
| **K6** | Linux konteyneri | Linux x86_64 konteynerinde derlenip çalışabilmeli. **Şimdi yalnız ön eleme:** belgeye göre Apple'a, Windows'a ya da tescilli çalışma zamanına bağlı olanlar dışlanır. **Nihai test** §5.4'te | `elle_bayraklar.csv` |
| **K7** | Kapsam | Kütüphane ya da RP doğrulayıcısı olmalı (§2) | tarama |
| **K8** | Tekillik | Aynı kod tabanından tek birim; çatallar ve yeniden paketlemeler dışlanır | tarama; ecosyste.ms `fork` |

**Kanıt ilkesi:**
- Her ölçüt kararı `SECIM.csv`'de ölçüt koduyla gerekçelendirilir (`neden_E*`).
- Veri alınamazsa ölçüt "doğrulanamadı" sayılır ve aday dışlanır.
- `CERCEVE.csv`'deki destek sütunları (General JSON, ML-DSA vb.) **seçimde kullanılmaz.** Bunlar yalnız envanter ve tedavi sınıfı bilgisidir (§5.5).

## 4. Eşik seçenekleri (K5) ve n'ye etkisi

Kaynak: `ESIK-DUYARLILIK.csv`. **n** = JOSE + SDJWT + COSE seçilenleri; **REF n'ye girmez.**

| Seçenek | Tanım | Uygun (JOSE / SDJWT / COSE / REF) | Uygun toplamı (REF hariç) | Seçilen n | Sayımda n (kota yok) |
|---|---|---|---|---|---|
| E1 | Tek biçim, gevşek: ≥50★ ya da ≥10k/ay ya da ≥50 bağımlı | 52 / 10 / 14 / 11 | 76 | **31** | 76 (aralık dışı) |
| **E2 (önerilen)** | Tabakaya göre ölçekli: JOSE ≥200★ / ≥100k / ≥100 bağımlı; SDJWT ve COSE ≥20★ / ≥1k / ≥10; REF ≥20★ | **41 / 15 / 17 / 14** | **73** | **31** (18 + 8 + 5) | 73 (aralık dışı) |
| E3 | Tek biçim, sıkı: ≥200★ ya da ≥100k/ay ya da ≥100 bağımlı | 41 / 9 / 4 / 6 | 54 | 30 (COSE yalnız 4) | 54 (aralık dışı) |
| E4 | Tabakaya göre ölçekli, gevşek: JOSE ≥50★ / ≥10k / ≥50; SDJWT ve COSE ≥10★ / ≥500 / ≥5 | 52 / 17 / 22 / 16 | 91 | 31 | 91 (aralık dışı) |
| E5 | Yüksek eşik + sayım: JOSE ≥1000★ / ≥1M / ≥500; SDJWT ≥50★ / ≥10k / ≥10; COSE ≥40★ / ≥10k / ≥10 | 25 / 10 / 14 / 7 | 49 | 31 | 49 (aralık dışı) |

**Yorum:**
1. **Hiçbir eşik tek başına n'yi 25–40'a indirmiyor.** Kotasız sayım 49–91 hedef üretiyor. Bu yüzden n'yi belirleyen şey eşik değil, **§5'teki kota ve seçim kuralı**dır. Eşik yalnız "uygun havuzu" tanımlar.
2. **Tek biçim eşik küçük tabakaları kurutuyor.** E3'te COSE'da 4 uygun hedef kalıyor ve kota (5) dolmuyor. SD-JWT ve COSE ekosistemleri JOSE'dan en az bir büyüklük mertebesi küçük. Bu nedenle tabakaya göre ölçekli eşik (E2) öneriliyor.
3. **n seçenekten neredeyse bağımsız:** E1, E2, E4 ve E5'te 31, E3'te 30. JOSE'da 9 çekirdek dil grubunun hepsi (E5'te 8'i) temsil ediliyor.
4. **E2'nin gerekçesi:** JOSE'da ≥200★ ya da ≥100k/ay, "üretimde yaygın" eşiğine karşılık gelir. SD-JWT/COSE'da ≥20★ ya da ≥1k/ay, bakımı süren ve gerçekten kullanılan kütüphaneyi hobi projesinden ayırır. Resmî referans istisnası, EUDI/OWF referans kütüphanelerinin düşük yıldız sayısını telafi eder (identity-common-ts yalnız 7★'a sahip ama 100k/ay indirmesi var).

**E2'de dışlama nedenleri** (bir adayın birden fazla nedeni olabilir; REF dahil 198 aday):

| Kod | Sayı |
|---|---|
| K5 (eşik altı) | 85 |
| K2 (etkin değil) | 56 |
| K1 (simetrik-yalnız) | 15 |
| K3 (arşiv/terk) | 14 |
| K4 (lisans) | 12 |
| K6 (platform) | 4 |

Yalnız K5 nedeniyle dışlananların sayısı 41'dir.

## 5. Tabaka kotaları ve seçim kuralı

### 5.1 Kotalar

| Tabaka | Kota | Gerekçe |
|---|---|---|
| JOSE | 18 | 9 çekirdek dil grubu × 2 (görev: "dil başına 1–2 önde gelen kütüphane") |
| SDJWT | 8 | OID4VC'ye özgü katman. Fisher karşılaştırması için ≥8 |
| COSE | 5 | Uygun havuz küçük (E2'de 17). mdoc kapsam dışı olduğu için ağırlık düşük |
| **n** | **31** | Hedef n≈30 (25–40) |
| REF | 3 (n dışı) | Sürüm 3 §9.2'deki üç doğrulayıcı. Emülatör en fazla 2 doğrulayıcıda (Sürüm 3 §7.14) |

### 5.2 Popülerlik puanı (eşikten bağımsız, tabaka içi)

- Her gösterge için, o tabakada göstergesi bulunan bütün çerçeve adayları arasında **orta-sıra yüzdeliği** hesaplanır: p = (#<v + 0,5·#=v) / n. Göstergeler: yıldız, aylık indirme, bağımlı paket, yalnız-toplam indirme.
- `pop_puani` mevcut yüzdeliklerin en yüksek olanıdır; eşitlik bozucu ikinci en yüksek yüzdeliktir; son eşitlikte `id` belirler.
- Böylece yıldızı olmayan Bitbucket depoları (Nimbus, jose4j), indirme istatistiği olmayan kayıtlar (Maven, Go) ve genç ama çok indirilen kütüphaneler (joserfc) karşılaştırılabilir hâle gelir.

### 5.3 Seçim kuralı (deterministik; `topla.py` → `secim()`)

1. **JOSE:**
   - Çekirdek 9 dil grubunun her birinden (JS/TS, Python, JVM, Go, Rust, .NET, PHP, Ruby, Swift/ObjC) popülerlik sırasıyla **en çok 2** hedef alınır.
   - Kota dolmazsa çekirdek dışı gruplardan (C/C++, Diğer) yine popülerlik sırasıyla, grup başına en çok 2 hedef eklenir.
2. **SDJWT ve COSE:** Dil grubu başına en çok 2 hedef, popülerlik sırasıyla, kota dolana kadar alınır.
3. **REF:** Önce plan kaynaklılar (G), sonra popülerlik sırası; kota dolana kadar.
4. **Yedekler:**
   - (i) Seçilen her dil grubunda sıradaki uygun aday (grup içi değiştirme için).
   - (ii) Tabakanın genel sırasında seçilmemiş ilk 2 uygun aday.

### 5.4 Linux testi ve değiştirme kuralı (K6, nihai)

- Seçilen her hedef, ön kayıttaki sürümüyle (§7) Linux konteynerinde derlenir.
- Süre sınırı hedef başına ≤4 çalışma-saatidir. Derleme ve en küçük bir doğrulama çağrısı çalışmazsa hedef düşer.
- Yerine önce aynı dil grubunun yedeği (5.3-4-i), yoksa tabakanın genel yedeği (5.3-4-ii) gelir.
- Her değiştirme gerekçesiyle `SECIM-DEGISIKLIK.csv`'ye yazılır (ön kayda **ek** olarak).
- Davranış sonucu bir hedefi değiştirmek için **gerekçe olamaz.**

### 5.5 Tedavi sınıfı (bilgi amaçlı; seçimi etkilemez)

Tedavi kolları ÖK §2A Ö6'ya göre composite -04 (ana) ve ML-DSA-65'tir (ikincil). Her hedefe bir tedavi sınıfı atanır:

| Sınıf | Anlamı |
|---|---|
| **T1-yerel** | Kütüphane ilgili PQ algoritmasını kendisi doğrular |
| **T2-eklenti** | Kamuya açık API'yle kendi PQ doğrulayıcımız kaydedilebilir ya da geri çağrıyla verilebilir; politika katmanı kütüphanenindir |
| **T3-bilinmeyen-alg** | Kütüphane PQ imzayı doğrulayamaz. Yalnız "bilinmeyen alg" davranışı gözlenir; oracle çıktısı accept-classical, reject ya da indeterminate olabilir |

Sınıf, `destek_kanitlari.csv`'ye dayanarak ölçüm öncesinde dondurulur.

## 6. Dışlama nedenleri (kodlu)

| Kod | Neden | Örnek |
|---|---|---|
| D1 (K1) | Yalnız simetrik (HS*) | pgjwt, jwt.q, 1c-jwt, JSONWebToken.swift |
| D2 (K2) | Son 24 ayda commit yok | ruby-jose (2024-01), COSE-JAVA (2021), COSE-C (2020), sd-jwt-kotlin (2024-05) |
| D3 (K3) | Arşivlenmiş, terk edilmiş ya da halefe devredilmiş | square/go-jose, SermoDigital/jose, rhonabwy (arşiv); Authlib (`authlib.jose` kullanımdan kalktı → joserfc); Sphereon SSI-SDK ("legacy" → IDK); TBD ssi-sdk |
| D4 (K4) | Açık lisans doğrulanamadı | deps.dev "non-standard" ve başka kaynak yok |
| D5 (K5) | Eşik altı | E2 tablosu |
| D6 (K6) | Platforma bağlı | JOSESwift (Apple Security/CommonCrypto/CryptoKit), yourkarma/JWT (iOS/macOS), SwiftyJWT (iOS), jose-rt (WinRT) |
| D7 (K7) | Kapsam dışı | Uygulama/demo/belge/cüzdan/ihraççı/mdoc (tarama aşaması) |
| D8 (K8) | Yinelenen ya da çatal | sd-jwt-js → identity-common-ts; oid4vc-ts; SIOP-OID4VP; mozilla go-cose çatalları |
| D9 | Uygun ama kota dışı | E2'de JOSE 14, SDJWT 1, COSE 8 aday. Yedek listesine girmeyenler |

## 7. Ön kayda girecek sabitler

1. `REF_TARIH = 2026-09-23`; etkinlik sınırı `2024-09-23`.
2. jwt.io veri dosyası: commit `60b70f7d8d20`, SHA-256 `3b1573be…5477`.
3. §1'deki sorgu dizgeleri ve gürültü tabanları; `onbellek/` anlık görüntüsü. Önerilen: `onbellek/` ve girdi dosyalarının SHA-256 listesi (`tarama_kararlari.csv`, `jwtio_esleme.csv`, `elle_bayraklar.csv`, `destek_kanitlari.csv`).
4. K1–K8 tanımları, E2 eşikleri ve istisnaları; geçersiz lisans kümesi; K5 toplam-indirme kuralı; tek-depo yıldız istisnası.
5. Popülerlik puanı (§5.2), kotalar (§5.1), seçim ve yedek kuralı (§5.3), Linux testi ve değiştirme kuralı (§5.4).
6. **Sürüm sabitleme:** Her hedef, dondurma anındaki `CERCEVE.csv` `son_commit_sha` değeriyle sabitlenir. Paket kaydında aynı koda karşılık gelen son sürüm varsa o sürüm de yazılır. Tarihsel taban için son 3–5 sürüm (Sürüm 3 §7.10d) bu sabitten geriye doğru seçilir.
7. **L4'ün işlemselleştirilmesi (öneri, bkz. OZET §6):** Kompakt-yalnız hedefte L4, "ihraççı başına gerekli algoritma kümesi"nin tek imzalı JWS'de uygulanmasıdır. Çoklu imzalı hedefte L4, gerekli kümedeki her algoritmanın **mevcut ve geçerli** olmasının istenmesidir.
8. Tedavi sınıfı ataması (§5.5) ve bağımlılık kümeleri (OZET §5, risk R6) ölçümden önce dondurulur.
9. Binom eşikleri: n=31'de çoğunluk iddiası **≥21/31** (p=0,035), çoğunluğun yokluğu **≤10/31** (p=0,035). n=30'da sırasıyla ≥20 ve ≤10 (p=0,049). Değiştirme sonrası n değişirse eşik aynı kuralla yeniden hesaplanır.

## 8. Karar bekleyen maddeler (yürütücüye)

1. **Eşik:** E2 öneriliyor. E1, E4 ve E5 aynı n'yi üretiyor, yalnız uygun havuzun genişliği değişiyor. E3, COSE kotasını doldurmuyor.
2. **Pilot kütüphaneleri:** Kural gereği `jose` ve `@sd-jwt/core` seçildi. `joserfc` yedekte kaldı. `jwcrypto` uygun ama kota dışında (Python'da pyjwt ile python-jose önde). Authlib K3 nedeniyle dışlandı. Öneri: pilotlar zorla eklenmesin; duyarlılık analizi "n + pilotlar" olarak raporlansın.
3. **Fisher katmanı:** "SD-JWT'ye özgü / genel JOSE" karşılaştırması tabakaya (SDJWT 8 / JOSE 18) göre mi, yoksa `sd_jwt` sütununa göre mi yapılacak? Öneri: tabakaya göre.
4. **COSE kotası:** 5 hedefle COSE yalnız betimsel raporlanabilir; çıkarımsal test yapılamaz.
5. **Kapsam genişletme (isteğe bağlı):** jwt.io dışındaki JOSE kütüphaneleri için kayıt taraması (J4). Maliyeti ≈2–4 çalışma-saati; n'yi değiştirmez, yalnız dış geçerliliği artırır.
