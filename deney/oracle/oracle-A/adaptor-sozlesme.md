# C3 adaptör sözleşmesi (Adım 9, görev 7 ve 7a) — Oracle A önerisi

> **Durum:** Oracle A'nın taslağı, 25.09.2026. Oracle B'nin sözleşmesiyle karşılaştırılıp yürütücü tarafından birleştirilecek; dondurma paketine girecek.
> **Bağlayıcı kaynaklar:**
> - ÖK §2B (n = 31; L4m/L4c; TK1–TK3; MR4; devir), §2D m.1–2 (anahtar yolu, `EdDSA`/`Ed25519`), §2E m.3 (etikete duyarlılık), §2G m.4 (birincil/ikincil);
> - ÖK §4.13–§4.15 (L0–L5, B1–B6, kanıt kuralı, belirsiz ve adaptör geçersiz), §6.4–§6.6 ve §6.11;
> - IS-PLANI Adım 9 görev 7/7a ve Adım 10.
>
> **Oracle:** `karar.tsv` (Oracle A) ve Oracle B'nin kararları. A–B uyuşmazlığı "belirsiz" sınıfına girer (ÖK §4.15).

## 1. Kapsam ve roller

- **Adaptör:** Hedef kütüphanenin **belgeli genel API'si** üzerinden bir vektörü, bir politika yapılandırması altında doğrulayan ince bir sarmalayıcıdır. Kütüphane kodu **değiştirilmez**.
  - Adaptör kendi doğrulama döngüsünü yazmaz. Yazarsa bu "özel kodla ifade edilebilir" (B4) kaydıdır ve L düzeyini yükseltmez (ÖK §4.13).
- **Koşucu:** Deneme düzenini yönetir. Adaptörü taze konteynerde çağırır, çıktıyı JSONL'ye yazar, oracle ile karşılaştırır ve ayrışma dedektörünü çalıştırır.
- **Oracle:** Beklenen kararı (vektör, politika, kol) üçlüsü için verir. Adaptör oracle'ı **görmez**.
- **Ön kayıt koruması:** Dondurmadan önce hedeflerde yalnız kurulum ve V± (`GEC` altında `VPLUS_*`/`VMINUS_*`) koşulabilir. K1–K11 koşulmaz (IS-PLANI Adım 9 "Ön kayıt koruması"; risk R12).

## 2. Girdi

### 2.1 Vektör

- `deney/uretec/vektorler/v1.2/<aile>/<id>.<jws|sdjwt|json>` ve MANIFEST girdisi.
- **`dogrulama_girdileri`:** `jwks`/`jwk`/`kid`, `guven_capalari`, `simdi` = 1790003700, `kb_aud`/`kb_nonce`, `htm`/`htu`, `beklenen_origin`.
- **Saat:** Adaptör saati `simdi` olarak verir: sahte saat ya da API'nin "şimdiki zaman" parametresi. Bunu yapamayan hedefte `exp` içeren vektörler yine geçerlidir (exp = 1821536000). KB-JWT ve DPoP `iat` değerleri de gerçek saatle geçerlilik penceresinin dışında kalır. Bu durumda `hata_sinifi = zaman` ile `indeterminate` yazılır ve hedef başına not düşülür.

### 2.2 Politika yapılandırması (JSON)

```json
{
  "politika": "L4",                     // GEC | IZIN-A | IZIN-AX | L4 | L4-S | L4-Y | P0 | P1 | L4-YOL
  "kol": "tedavi-ML-DSA-65",            // kontrol-EdDSA | kontrol-Ed25519 | tedavi-ML-DSA-65 | tedavi-composite
  "A": "ES256",
  "X": "ML-DSA-65",                     // EdDSA | Ed25519 | ML-DSA-65 | ML-DSA-65-ES256
  "W": ["ES256", "ML-DSA-65"],          // izin kümesi
  "R": ["ML-DSA-65"],                   // ihraççı başına gerekli küme (R_I); IZIN-*/GEC/P0/P1'de []
  "coklu_imza": "gerekli-kume",         // en-az-biri (P0) | mevcut-tumu (P1) | gerekli-kume (L4) | gerekli-kume+tumu (L4-S) | gerekli-kume+W-disi-yok (L4-Y)
  "ihracci": {"iss": "https://issuer.example", "durum": "goc-etmis"},   // L4c: goc-etmis | eski
  "anahtar_yolu": "JWKS",               // JWKS | JWK | dogrudan | x5c+capa (yalnız X5C) | jwk-basligi (yalnız DPoP)
  "zincir_politikasi": null,            // L4-YOL: "yol-tam-pq"
  "sdjwtvc_surum": "-13",               // -13 (birincil) | -19 (MR3)
  "kb_gerekli": true,                   // VP ailesi
  "simdi": 1790003700
}
```

- Yapılandırmaların anlamı `YONTEM.md` §2'dedir. Adaptör bu JSON'u hedefin belgeli API çağrılarına çevirir. Çeviri tablosu hedef başına `deney/kosum/adaptorler/<hedef>/ESLEME.md`'ye yazılır.
- Hedefin API'si bir alanı ifade edemiyorsa (ör. R) adaptör o alanı **atlamaz**. Satırı `sonuc_ham = ifade-edilemedi` ile işaretler. Bu kayıt L düzeyi protokolüne (§5) girdi olur.

## 3. Çıktı (satır başına bir JSON nesnesi; `kosu/r{1,2,3}/<hedef>.jsonl`)

```json
{
  "sozlesme": "adaptor-sozlesme/1.0",
  "hedef_id": "JOSE-083", "hedef_surum": "2.15.0", "hedef_commit": "1d41a647…", "imaj_ozeti": "sha256:…",
  "adaptor_sha256": "…", "batarya": "v1.2", "manifest_sha256": "bb17aaa7…",
  "kosu": "r1", "tarih_utc": "2026-11-05T10:00:00Z",
  "vektor_id": "T1P_both_valid", "vektor_sha256": "…",
  "politika": "L4", "kol": "tedavi-ML-DSA-65", "tk": "TK2", "sdjwtvc_surum": "-13",
  "kontrol_etiketi": null,                  // kontrol kolunda "EdDSA" ya da "Ed25519" (7a)
  "kullanilan_alg_etiketi": "ML-DSA-65",    // X için kullanılan başlık etiketi
  "anahtar_yolu": "JWKS", "api_yolu": "jwt.PyJWS().decode_complete(..., algorithms=[...])",
  "sonuc_ham": "kabul",                     // kabul | red | istisna | zaman-asimi | cokme | uygulanamaz | ifade-edilemedi
  "karar": "accept-hybrid",                 // accept-classical | accept-hybrid | reject | indeterminate | uygulanamaz
  "hata_sinifi": null,                      // §3.2
  "hata_ozeti": null, "hata_sha256": null,  // ilk 200 karakter + tam metnin özeti
  "dogrulanan_algoritmalar": [
    {"sira": 0, "alg": "ES256", "sonuc": "gecerli"},
    {"sira": 1, "alg": "ML-DSA-65", "sonuc": "gecerli"}
  ],                                        // sonuc: gecerli | gecersiz | denenmedi | bilinmiyor
  "pq_servis_cagrilari": 1,                 // yalnız TK2: yerel PQ doğrulama servisinin günlüğünden
  "sure_ms": 14, "zaman_asimi": false,
  "stdout_sha256": "…", "stderr_sha256": "…"
}
```

### 3.1 Gözlemden dört değerli karara eşleme

| Gözlem | Karar |
|---|---|
| Kütüphane kabul etti **ve** en az bir PQ imzasının (ML-DSA ya da composite) doğrulandığı gösterildi. Kanıt: kütüphanenin sonuç nesnesi (RFC 7515 §5.2 adım 10) ya da TK2 servis günlüğü | `accept-hybrid` |
| Kütüphane kabul etti ve PQ doğrulaması gösterilemedi. Örnek: TK3 ya da yalnız klasik imzaya dayanan kabul | `accept-classical` |
| Kütüphane reddetti ya da doğrulama istisnası attı (§3.2'deki bir sınıfla) | `reject` |
| Zaman aşımı, çökme ya da 3 tekrarda aynı olmayan sonuç (ÖK §6.11) | `indeterminate` |
| Hedef bu serileştirmeyi belgeli API'siyle desteklemiyor (B6) | `uygulanamaz` (karşılaştırmaya girmez) |

**B6 ile red ayrımı:**
- B6 **önceden, API incelemesiyle** belirlenir. Örnek: hedefte General JSON doğrulama API'si yok → General JSON vektörleri koşulmaz ve `uygulanamaz` yazılır.
- API varsa vektör koşulur. Ayrıştırma hatası artık bir **red**dir (`hata_sinifi = ayristirma`).
- 8725bis §3.14 uyarınca JWT kütüphanelerinin JSON girdiyi reddetmesi B6'dır, sapma değildir.

### 3.2 Hata sınıfları (kapalı liste)

`imza-gecersiz`, `alg-desteklenmiyor`, `alg-izin-disi`, `alg-anahtar-uyusmazligi`, `gerekli-kume-eksik`, `anahtar-bulunamadi`, `zincir-gecersiz`, `x5c-korumasiz`, `baslik-cakismasi`, `crit`, `typ`, `zaman`, `kb`, `sd_hash`, `ayristirma`, `istisna-diger`, `zaman-asimi`, `cokme`, `adaptor-hatasi`, `bicim-desteklenmiyor` (B6).

- Eşleme hedef başına `ESLEME.md`'de kütüphanenin istisna türlerinden yapılır. Eşlenemeyen istisna `istisna-diger` olur ve mesaj özeti kaydedilir.
- **"Yanlış ön-özet" (CMP10):** CMP10'u **kabul eden** hedef, taksonomide "yanlış ön-özet uygulayıcı hatası" sınıfına yazılır (ÖK §2D m.5).

## 4. Zaman aşımı, tekrar, sürüm sabitleme

- **Zaman aşımı:**
  - vektör başına 60 s (sert);
  - hedef × koşu başına 30 dk.
  - Aşım `zaman-asimi` → `indeterminate` olur.
  - JVM/.NET ısınması ölçüm dışıdır. Adaptör bir süreçte bütün vektörleri sırayla işler; süre vektör başına ölçülür.
- **Tekrar:** 3 koşu (r1–r3), her biri taze konteynerde. Hücre değeri ancak 3/3 aynıysa geçerlidir; aksi hâlde "kararsız" → belirsiz (ÖK §6.11).
- **Sürüm sabitleme:**
  1. Hedef, dondurma anındaki `CERCEVE.csv` `son_commit_sha` ile sabitlenir (KRITERLER §7 m.6).
     - Ortam çalışması (25.09 ara kaydı) birçok hedefte yayım etiketinin bu commit'ten farklı olduğunu kaydetti.
     - **cose-lib 4.8.2'de ML-DSA kaynağı yok; HEAD'de var.**
     - **Kural önerisi:** TK ataması envanterin dayandığı commit'teki API'ye göre yapıldığı için ölçüm o commit'ten derlenmiş hedefle yapılır. Yayım sürümü ve commit'i ayrıca kaydedilir. Tarihsel taban (ÖK §6.12) yayım sürümlerinden geriye gider. Karar yürütücüdedir (NOTLAR N-7).
  2. Kilit dosyası özeti, imaj özeti ve adaptör kodunun SHA-256'sı her çıktı satırına yazılır.
  3. Batarya (v1.2, çapa 7) ve oracle (`karar.tsv` SHA-256'sı) ilk ölçümden önce `sha256sum -c` ile denetlenir. Uyuşmazlıkta ölçüm başlamaz (IS-PLANI Adım 10.3).

## 5. L düzeyi belirleme protokolü (ÖK §4.13; L4m/L4c ÖK §2B m.6)

L düzeyi **kontrol kolunda** belirlenir (X = EdDSA, gerekirse Ed25519; ÖK §3.7). Tedavi kolları F_T ve B bayrakları içindir. Her adımda API taraması, yapılandırma denemesi ve batarya doğrulaması birlikte yürür.

### 5.0 Adaptör geçerlilik kapısı (ÖK §4.15)

- **Satırlar:** `GEC` × {`VPLUS_ES256`, `VPLUS_EdDSA` | `VPLUS_EdDSA-ED25519`, `VMINUS_ES256`, `VMINUS_EdDSA` | …}. Oracle: V+ → accept, V− → reject.
- En fazla iki düzeltme denemesi yapılır. Geçemeyen hedef **adaptör geçersiz** olur (n_eff dışı, gerekçeli).
- Tedavi kollarında `VPLUS_ML-DSA-65`/`VMINUS_ML-DSA-65` ve `CMP00`/`CMP01` aynı kapıdan geçer. TK1/TK2'nin çalıştığını bu gösterir; geçemezse o kol TK3'e düşer (§6).

### 5.1 API taraması

- Belgelenmiş seçenekler, tip tanımları ve genel dışa aktarımlar taranır. Örnek komut: `rg -n "algorithms|allowlist|RegisterJws|register_algorithm|required|all|any" <kaynak>`. Komut ve çıktı `kanit/<hedef>/api-tarama.txt`'ye yazılır (ÖK §4.14).
- Her L basamağı için aday mekanizma listelenir:
  - genel izin listesi,
  - çağrı başına izin listesi,
  - anahtar/ihraççı başına bağlama,
  - gerekli küme ya da çoklu imza kuralı.

### 5.2 Basamaklar

| Basamak | Yapılandırma ve vektörler | Başarı ölçütü (oracle ile birebir) |
|---|---|---|
| **L1** | Genel izin listesi. `IZIN-A` (W={ES256}) ile `VPLUS_ES256` ve `VPLUS_EdDSA`; ardından `IZIN-AX` | IZIN-A: VPLUS_EdDSA → reject, VPLUS_ES256 → accept-classical. IZIN-AX: ikisi de accept-classical. (Tedavi kollarında ayrıca `UNK01–03` her yapılandırmada reject.) |
| **L2** | Aynı doğrulayıcı örneğinde iki çağrı: `IZIN-A` ve `IZIN-AX` (çağrı başına) | İki çağrının kararları oracle'daki IZIN-A ve IZIN-AX satırlarıyla aynı |
| **L3** | `IZIN-AX` + belgelenmiş anahtar/ihraççı başına alg bağlama. `K10K_alg-EdDSA_anahtar-ES256` [-ED25519], `K10K_alg-ES256_anahtar-Ed25519` ve `VPLUS_*` | K10 (iki yön) → reject; VPLUS_* → accept. **Ek koşul:** reddin, bağlama mekanizmasından geldiği API kanıtıyla gösterilmeli. Anahtar türü uyuşmazlığından doğan rastlantısal ret L3 sayılmaz (RFC 7515 §5.2 adım 8 zaten ret üretir) |
| **L4m** (hedef General JSON çoklu imzayı destekliyor) | `L4` (R={X}, W={A,X}) ile `T1K`, `T2K`, `T3`, `T5K` [yedek eşleri] | T1K accept-classical, T2K reject, T3 reject, T5K accept-classical. **Y_i = 1** |
| **L4c** (yalnız kompakt) | Aynı doğrulayıcı örneğinde ihraççı başına politika: I_göç (R={X}) ve I_eski (R=∅). Göç: `VPLUS_ES256` → reject, `VPLUS_EdDSA` → accept-classical. Eski: `VPLUS_ES256` → accept-classical (`IZIN-AX` satırı) | Üç kararın hepsi oracle ile aynı → **Y_i = 1**. Batarya sınırı ve "aynı örnek" yorumu §5.3'te |
| **L5** | Varsayılan yapılandırma (yalnız anahtar verilir). L3 ve L4 vektörleri koşulur | Kararlar L3 için `IZIN-AX`, L4 için `L4` satırlarıyla aynıysa L5 |

- Hedefin L düzeyi, belgeli API ile ulaşılan **en yüksek** basamaktır (ÖK §4.13).
- **Y_i:** Hedef çoklu imzayı destekliyorsa L4m, desteklemiyorsa L4c (ÖK §2B m.6). Hangi biçimin uygulandığı `L-duzeyleri.csv`'ye yazılır.
- **"Özel kodla ifade edilebilir":** Kod ve satır sayısı B4 olarak kaydedilir. L düzeyi yükselmez.

### 5.3 L4c'nin "aynı doğrulayıcı örneği" koşulu ve batarya sınırı

- v1.2'de ayrı bir eski ihraççı kimliği yok: tek `iss` ve tek ES256 ihraççı anahtarı.
- **Öneri (yürütücü kararı; NOTLAR N-2):** Adaptör aynı doğrulayıcı örneğine iki ihraççı politika kaydı koyar. Politika kaydı, API'nin ihraççıyı tanıdığı anahtara bağlanır: `iss`, `kid` ya da anahtar nesnesi.
  - VPLUS_ES256, "göç" kaydının anahtarıyla doğrulanınca reject olmalı.
  - "Eski" kaydının anahtarıyla (aynı ES256 anahtar materyali, ayrı kayıt) doğrulanınca accept-classical olmalı.
- API ihraççıyı yalnız `iss` ile tanıyorsa aynı baytlar iki kayda ayrılamaz. O durumda L4c, iki **ardışık** yapılandırmayla aynı API mekanizması üzerinden sınanır ve "L4c (ardışık)" diye işaretlenir. Bu, ÖK metninden bir sapma adayıdır.

### 5.4 Bayraklar

- **B1** (bilinmeyen composite alg): K5 (`T7*`, ikincil `T4*`, `T6`, `UNK04/05`). Kayıt değerleri:
  - `L4-S` satırıyla aynıysa "red";
  - `L4-Y` satırıyla aynıysa "yok sayma";
  - istisnayla bütün doğrulama düşüyorsa "bütün doğrulamanın düşmesi".
  - Hiçbiriyle aynı değilse **MR2 ihlali**.
- **B2** (karışık x5c politikası ifade edilebilir mi?): `L4-YOL` × X5C03/04/05. Hedef yol sınıfı politikasını API ile kurabiliyor ve üçünde de reject veriyorsa B2 = 1.
- **B3** (korumasız x5c işleniyor mu?): `L4` ya da `GEC` × X5C07/08/09. Oracle üçünde de reject. Hedef X5C07 ya da X5C08'i kabul ediyorsa B3 = 1.
- **B4:** özel kod satır sayısı (boş satır ve yorum hariç).
- **B5** (semantik sınıf): Hedefin **varsayılan** yapılandırmasında T1/T2/T3/T7 kararları oracle'ın `P0` / `P1` / `L4-S` / `L4-Y` satırlarından hangisiyle aynıysa sınıf odur:
  - en-az-biri-geçerli: P0 (T2 kabul);
  - mevcut-tümü-geçerli: P1 (T2 red, T3 kabul, T7 red);
  - gerekli-küme: L4-S ya da L4-Y (T3 red);
  - hiçbiriyle aynı değilse "diğer".
- **B6:** §3.1'deki biçim desteği.
- **MR4:** Kaynak vektör ile permütasyon eşinin kararı her yapılandırmada aynı olmalıdır (oracle'da 165/165 aynı). Farklıysa ayrı MR4 bayrağı yazılır (ÖK §2B m.8). VP05-SIRA-ters MR4 dışıdır.

### 5.5 "İfade edilemez" kanıt kuralı (ÖK §4.14)

"İfade edilemez" hükmü yalnız şu üç koşul birlikte sağlanırsa verilir:
1. §5.1'deki taramada kanca yok (komut ve çıktı kayıtlı);
2. iki bağımsız çalışma denemesi başarısız;
   - farklı oturumlarda yapılır;
   - ikinci çalışma yalnız hedefi ve bu sözleşmeyi görür;
   - her deneme en fazla 45 dk;
3. kaynak kodda satır referansı var: depo + commit SHA + dosya + satır aralığı.

Eksik koşulda sonuç **belirsiz** olur.

## 6. Tedavi kolu ataması: TK1 / TK2 / TK3 (ÖK §2B m.7; KRITERLER §5.5)

**Kural (kol başına ayrı: ML-DSA-65 kolu ve composite kolu):**
1. **TK1 yerel:** Sabitlenen commit'teki belgeli genel API algoritmayı yerel olarak doğrular. Kanıt: `destek_kanitlari.csv`'de sabit commit'li satır ya da belge satırı.
   - V± kapısı o kolda geçer: `VPLUS_ML-DSA-65` / `VMINUS_ML-DSA-65` ya da `CMP00` / `CMP01`.
   - Çalışma zamanı koşulu Linux konteynerinde sağlanır (ör. PHP 8.4 + OpenSSL 3.5; .NET MLDsa).
2. **TK2 eklenti:** Yerel destek yok, ama belgeli genel bir genişleme noktası var: algoritma kaydı, doğrulayıcı geri çağrısı ya da Signer/Verifier arayüzü. Bu noktaya `deney/imzalayici`'deki yerel PQ doğrulama servisi kütüphane kodu değiştirilmeden takılabilir.
   - **Politika katmanı kütüphanenin kalır:** alg izin listesi ve çoklu imza semantiği. Eklenti yalnız "bu imza bu anahtarla geçerli mi?" sorusunu yanıtlar.
   - V± kapısı eklentiyle geçer. Servis günlüğü `pq_servis_cagrilari` alanına yazılır.
3. **TK3 bilinmeyen-alg:** Yukarıdakilerin hiçbiri yok. Yalnız bilinmeyen alg davranışı gözlenir. Oracle karşılaştırmasında `accept-hybrid` beklenen hücrede hedefin `accept-classical` vermesi **PQ'ya özgü başarısızlık**tır. T2 (McNemar) TK3 hedeflerini içermez; TK3 tanımlayıcı raporlanır.
4. **Öncelik:** TK1 > TK2 > TK3. Eklenti kütüphane kodunu değiştirmeyi gerektiriyorsa TK2 sayılmaz.
5. **Dondurma:** Atama ölçümden önce yapılır; yalnız API incelemesi ve V± kapısıyla (davranış ölçümü değil). "İncelenecek" hedefler adaptör yazımı sırasında API incelemesiyle TK2 ya da TK3'e atanır (OZET P5). Sonuç `tk-atamasi.csv`'ye gerekçe satırıyla yazılır.

**Ön atama (envanterden; `OZET.md` §2 ve §3.2, `destek_kanitlari.csv`). Bağlayıcı değildir; kural 5'le dondurulur.**

| Hedef | ML-DSA-65 kolu | composite kolu | Dayanak ve not |
|---|---|---|---|
| JOSE-009 panva/jose | TK1 | TK3 | `types.d.ts` L23–25 (ML-DSA-44/65/87); composite deseni 0 eşleşme |
| JOSE-001 IdentityModel | TK1 | incelenecek | MlDsaSecurityKey; composite 0 eşleşme; .NET MLDsa ortamı |
| JOSE-083 pyjwt | TK2 | TK2 | `register_algorithm` (OZET §3.2) |
| JOSE-055 jjwt | TK2 | TK2 | `parserBuilder().sig().add` |
| JOSE-034 jose2go | TK2 | TK2 | `RegisterJws` |
| JOSE-033 golang-jwt | incelenecek | incelenecek | Keyfunc'a bırakılmış bağlama; kayıt mekanizması API incelemesiyle |
| JOSE-052 java-jwt, JOSE-002 JWT.NET, JOSE-071 lcobucci, JOSE-087 ruby-jwt, JOSE-089 json-jwt | incelenecek | incelenecek | OZET §3.2 m.3 |
| JOSE-065 node-jsonwebtoken, JOSE-084 python-jose, JOSE-070 php-jwt, JOSE-092 jsonwebtoken, JOSE-091 frank_jwt, JOSE-104 Swift-JWT | TK3 | TK3 | ML-DSA ve composite desenleri 0 eşleşme; eklenti kanıtı yok (JOSE-065 "incelenecek" notlu) |
| JOSE-102 jwt-kit | TK1 koşullu, Linux'ta TK3 olası | TK3 | README L281 "MLDSA requires macOS 26+" |
| SDJWT-015 identity-common-ts | TK2 | TK2 | doğrulayıcı geri çağrısı; `allowedIssuerAlgorithms` |
| SDJWT-018 sd-jwt-python | TK1-dolaylı (jwcrypto) | incelenecek | doğrulama jwcrypto'ya devredilir; ortam: jwcrypto 1.6.1, mldsa modülü var |
| SDJWT-010 sd-jwt-payload | TK2 adayı | TK2 adayı | `JwsSigner` trait (kripto-bağımsız) |
| SDJWT-021 WalletFramework | TK3 | TK3 | ES256 kodda sabit; IdentityModel'e devreder (§7) |
| SDJWT-025 ssi, SDJWT-001 vck, SDJWT-004 authlete, SDJWT-002 affinidi | incelenecek | incelenecek | authlete: ortam kaydına göre JWS imza doğrulamasını çağırana bırakıyor (NOTLAR N-8) |
| COSE-035 cose-lib | TK1 (yalnız HEAD) | TK3 | 4.8.2'de ML-DSA yok; sürüm sabitlemeye bağlı (§4) |
| COSE-036 wolfCOSE | TK1 | TK3 | `WOLFCOSE_LEAN_VERIFY_MLDSA`; GPL-3.0 |
| COSE-034 go-cose | TK2 | TK2 | Signer/Verifier arayüzü (README L270–322, HEAD) |
| COSE-001 Signum, COSE-014 cose-js | TK3 | TK3 | ML-DSA/composite 0 eşleşme |

**COSE tabakası için uyarı:** v1.2 bataryasında COSE vektörü yok. 153 vektörün hepsi JWS/SD-JWT biçiminde (ÖK §2D m.8). Bu yüzden 5 COSE hedefi için davranışsal L düzeyi ve F_K/F_T batarya ile ölçülemez; bütün satırlar B6 olur. Karar yürütücüdedir (NOTLAR **N-0**).

## 7. Devralma ilişkileri (D-E7; ÖK §2B m.9)

| Devralan | Doğrulamayı devrettiği | n içinde mi? | Kaynak |
|---|---|---|---|
| SDJWT-021 WalletFramework.SdJwtVc | JOSE-001 Microsoft IdentityModel (`JwtSecurityTokenHandler`) | **evet: devir kümesi** | OZET §4 |
| SDJWT-001 vck | Signum `indispensable-josef/cosef` (COSE-001 ile aynı proje) | aday (ortam 25.09) | `deney/ortam/derleme-sonuc.csv` notu |
| SDJWT-018 sd-jwt-python | jwcrypto | hayır (jwcrypto n dışı) | OZET §4 |
| REF-003 EUDI doğrulayıcısı | eudi-lib-jvm-sdjwt-kt + Nimbus | n dışı (REF) | OZET §2.4 |
| REF-011 Credo | SDJWT-015 identity-common-ts (`@openid4vc/*`) | REF n dışı; hedef n içinde | OZET §4 |
| irmago (REF yedeği) | jwx | n dışı | OZET §4 |

**Kurallar:**
- T1 ve T2, devralan hedefler çıkarılarak yeniden hesaplanır (tanımlayıcı, Holm dışı).
- Ayrışma dedektörü devir kümelerini tek birim olarak da gösterir (`ayrisma-dedektoru.md` §4).
- SDJWT-004 authlete imza doğrulamasını çağırana bırakıyorsa politika katmanı kütüphanede değildir. Bu hedefin L düzeyi API taramasıyla "L0 (imza politikası yok)" ya da kapsam dışı (K1) olarak değerlendirilmelidir. Karar yürütücüdedir.

## 8. Görev 7a kuralları (ÖK §2D m.1–2, §2E m.3)

1. **Anahtar yolu:** Doğrulama anahtarı **bütün kollarda** hedefin belgeli API'siyle verilir (JWK/JWKS ya da doğrudan anahtar nesnesi). Kollar arasında **aynı yol** kullanılır; `anahtar_yolu` alanı her satırda kaydedilir. Kollar arasında farklı yol kullanan hedefin kontrol–tedavi karşılaştırması geçersiz sayılır.
2. **`x5c` yalnız X5C vektörlerinde:** X5C01–X5C10'da anahtar x5c ve güven çapalarıyla (`anahtarlar/v1/pki/root-ec.pem`, `root-ml.pem`) çözülür. Diğer vektörlerde başlıkta x5c olsa bile anahtar belgeli API ile verilir. Hedef x5c'yi yok sayamıyorsa yine de doğrudur, çünkü bataryadaki zincirler geçerlidir. Bu davranış not edilir.
3. **Composite X.509 kapsam dışıdır:** Composite nesneler kid/JWKS ile çözülür ve "**HAIP §6.1.1 sapması**" olarak etiketlenir. K8 ve K9 composite kolunda ML-DSA-65 yapraklı X5C04/X5C07 ile koşulur (ÖK §2F m.4). Oracle bu satırlarda politikayı X = ML-DSA-65 ile örnekler.
4. **Kontrol etiketi:**
   - Birincil etiket `EdDSA`'dır.
   - Hedef `EdDSA`'yı desteklemiyor ama `Ed25519`'u (RFC 9864) **belgeli olarak** destekliyorsa kontrol kolu `-ED25519` eşleriyle koşulur (kol = `kontrol-Ed25519`).
   - İkisini de destekliyorsa `EdDSA` kullanılır.
   - Kullanılan etiket `kontrol_etiketi` alanına ve `tk-atamasi.csv`'ye yazılır. Tek etiketli izin listesi diğer etiketi reddeder (ÖK §2E m.3). Bu yüzden izin kümesi W her zaman kullanılan etiketle kurulur. Yedeğin kullanılması Y_L4 tanımını değiştirmez.
5. **Ortak dosyalar:** `T3_stripped_to_ES256`, `VPLUS_ES256`, `VMINUS_ES256` ve `VC10_ikili_ihrac` her kolda kolun W/R'siyle yeniden değerlendirilir. Oracle'da her kol için ayrı satır vardır.

## 9. Oracle ile karşılaştırma kuralı

1. **Uyum birimi:** (hedef, vektör, politika, kol, 3/3 kararlı hücre).
2. Karşılaştırmaya girmeyenler:
   - oracle A ile B'nin uyuşmadığı hücreler → belirsiz (ÖK §4.15);
   - oracle `indeterminate` hücreler → raporlanır ama sapma sayılmaz;
   - hedef `uygulanamaz` (B6) hücreler.
3. **Sapma türleri:**
   - **karar sapması:** accept-* ↔ reject;
   - **PQ doğrulamasız kabul:** oracle `accept-hybrid`, hedef `accept-classical`. L4 ailesinde bu bir sapmadır, çünkü R uygulanmamıştır;
   - **zararsız kabul türü farkı:** oracle `accept-classical`, hedef `accept-hybrid`. Örnek: P0 satırında hedefin bütün imzaları doğrulaması. Kaydedilir, sapma sayılmaz.
4. **F_K / F_T (ÖK §6.4):** Hedefin en iyi ulaşılabilir yapılandırmasında (API ile en yüksek L) K1–K3 birincil vektörlerinden en az birinde karar sapması ya da PQ doğrulamasız kabul varsa 1.
   - K: kontrol kolu; T: tedavi kolu. Composite ana kol; ML-DSA-65 ikincil kol ayrı raporlanır.
   - Karşılaştırma `L4` satırlarıyladır. Hedefin S ya da Y semantiği K1–K3'ü değiştirmez.
5. **Birincil sonuç değişkenleri** (Y_L4'ün batarya kısmı, F_K, F_T, D_soy, B1–B6) yalnız `sinif = birincil` satırlardan hesaplanır (ÖK §2G m.4). İkincil satırlar tanımlayıcıdır.
