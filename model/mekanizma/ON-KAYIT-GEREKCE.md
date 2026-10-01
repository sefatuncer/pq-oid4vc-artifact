# Adım 7 görev 0 — Mekanizma düzeyi beklentilerin gerekçesi

- **Tarih:** 25.09.2026. **Yazan:** Tamarin çalışması.
- **Durum:** Hiçbir mekanizma koşumu yapılmadı. Beklentiler `on_kayit_varyantlar.tsv`'de; bu belge her beklentinin gerekçesini ve kaynağını verir.
- **Kaynak gösterimi:**
  - `T###`: izlenebilirlik matrisi satırı (`02-izlenebilirlik\izlenebilirlik.csv`).
  - `reddy-01 §x`, `vicente-02 §x`, `sheffer-02 §x`: `literatur\metin\` altındaki birincil metinler.
  - `#791`, `#2153`: OIDF GitHub tartışmaları (arşiv: `..\Yeni\_calisma\dogrulama_2026-09-23\c791.json`, `i2153.json`, `c2153.json`).
  - `R2`, `R3`, `R7`, `R7h`, `R7hx`, `S_online_core`: kural düzeyi sonuçlar (`model\tamarin\`). Bunlar **gerekçe olarak** anılır; kural düzeyi beklentiler burada yeniden kaydedilmez.
- **Kategori:** her beklenti şu üçünden biridir:
  - **kanıt:** all-traces lemma verified beklenir;
  - **iz:** all-traces lemma falsified beklenir (saldırı izi);
  - **koşullu kanıt:** kanıt, yazılı bir varsayım altında beklenir. Varsayım tabloda "varsayım" satırında yazılıdır.

## 0. Ortak tanımlar

**G5'in üç biçimi** (ÖK §2D.10; `modeller\ortak_g5.spthy`, her modele `#include` ile girer):

| Biçim | Lemma | Anlamı |
|---|---|---|
| G5-zamansız | `G5_untimed` | Doğuştan göçmüş varlık (kurulumda `BornMigrated`) yalnız klasik kanıtla hiçbir zaman kabul edilmez. R2/R3'teki durağan biçim |
| G5-zamanlı | `G5_timed`, `no_rollback` | Sunset'ten sonra klasik kabul yok; beklentiyi bir kez görmüş doğrulayıcı geri dönmez |
| G5-göç | `G5_migrated` | Göçten sonra, ilk temas dahil, yalnız klasik kanıtla kabul yok |

Ek bilgi lemması `first_contact_downgrade` (exists-trace): beklentiyi hiç görmemiş doğrulayıcı göçten sonra klasik kabul ediyor mu (L-D1).

**Varlık türleri** (her modelde):
- doğuştan göçmüş (G5-zamansız kurgusu),
- göç eden (yaşam döngüsü `'none' → Migrate → 'pq_required' → Sunset → 'retired'`),
- eski (hiç göç etmez; klasik yolu canlı tutar; varlık başına kapsamı anlamlı kılar).

Yaşam döngüsü olay sırasıyla ve kısıtlarla kodlanır (R7 yöntemi; doğrusal durum döngüsü yok).

**Saldırgan:** Dolev–Yao (S1) ve Q-day'den sonra gözlenen klasik anahtarı çıkaran CRQC (S2; tek evreli, τ yok; zaman boyutu R6'da). PQ anahtar kırılmaz.

**"Boş doğru" (vacuous) notu:** Beklenti durumu tutmayan mekanizmalarda `SeenPQReq` hiç oluşmaz. Bu yüzden `no_rollback` = V boş yere doğrudur ve `executable_learn` = F beklenir. Tablolarda "V (boş)" diye işaretlidir.

**Beklenti kategorisi:**
- **iz:** taban kurguda G5 ya da G4 ihlali beklenir;
- **kanıt:** bütün G5 biçimleri beklenir;
- **koşullu kanıt:** kanıt, yazılı bir varsayım (ör. PQ WebPKI, cüzdanda kimliği doğrulanmış beklenti) altında beklenir.

## 0.1 Kapsam ekonomisi (yürütücü kararı, 25.09.2026)

Kullanıcı talimatı: akademik olarak faydasız ya da boşa emek olacak iş yapılmaz. Bu yüzden beklenti dosyasında üç tür satır vardır:

| Rol | Anlamı | Koşum |
|---|---|---|
| koşulacak (`mekanizma`, `kosul`, `tasiyici`, `ablasyon`, `3b`, `3a`) | Yeni mekanizma düzeyi sonuç: `beklenti_kapsami` (3 × 3), taşıyıcı ikamesi, M-h'nin iki tipi, A.3.2.2, M-a / M-b / M-b0 / M-d / M-e / M-e′ | çapadan ve teknik kapıdan sonra |
| `5A-kapsandi` | Boyut 5A'da R7 ile zaten sınandı: kimlik doğrulama / PQ kanal, tazelik / sabitleme, tekdüzelik, varlık başına, sunset, M-g ile öz-beyan ve ilk temas | yok; satır R7 varyantına atıftır (çapa 3) |
| `indirgendi` | Başka bir satıra ya da R7 kanal sınıfına indirgenir; indirgeme gerekçesi ilgili bölümdedir | yok |

- **İndirgemede kullanılan tek biçimsel argüman (kural üst kümesi):** Bir varyant ötekinden yalnız kural ekleyerek (aynı kısıtlarla) elde ediliyorsa, izleri ötekinin izlerinin üst kümesidir. Bu yüzden alt modelde F olan all-traces lemması ve V olan exists-trace lemması üst modelde de aynı hükmü alır. Örnek: `REG_PQ` yalnız bir kırma kuralını kaldırır (§2.3); `ATK_*` bayrakları yalnız kurulum kuralı ekler (§3.2).
- **Kanal sınıfı argümanı** (öteki indirgemeler): sonuç kanalın sınıfına bağlıdır: PQ ile doğrulanmış ve karar anında güncel / yeniden oynatılabilir / klasik ile doğrulanmış / kimliksiz. Aynı sınıftaki iki kanal aynı hükmü alır. Bu bir modelleme argümanıdır, araç çıktısı değildir; taşıyıcı ikamesi satırları (§4) aynı argümanı koşumla sınar.
- Mekanizmalar için ProVerif ikinci görüşü ve emülatör için iz dışa aktarımı bu adımda yapılmaz.
- Koşulacak satır sayısı 33'tür: M_istek 3, M_metaveri 4, Mf_yol 17 (çekirdek 1 + 3b 9 + taşıyıcı 7), M_h 9. Değişiklik 8 ile 10 satır eklendi (Mg_yol 6, Mf_ek 4); toplam 43 (§9).

## 1. İstek yönü: M-b0, M-a, M-b, M-c, OID4VP A.3.2.2 (görev 3)

### 1.1 Model ve beklentiler

**Model:** `modeller\M_istek.spthy`.
- **Taraflar:** Varlık, istek imzalayan RP'dir; doğrulayan cüzdandır. İstekler cüzdanın taze nonce'una bağlıdır (wallet_nonce).
- **RP anahtarları:** cüzdanda özgün biçimde bilinir. Erişim sertifikası zinciri dışarıda tutuldu; yol boyutu `Mf_yol`'da.
- **G4 (RP kimlik doğrulaması):** göçten sonra kabul edilen istek RP'den gelmiş olmalı.
- **Model kısıtı `RequestSamePhase`:** Dürüst istek oluşturulduğu yaşam döngüsü evresinde kabul edilir. İstek nesneleri kısa ömürlüdür; kısıt, göç sınırını aşan yapay yarışı dışlar. Sahte isteklere uygulanmaz.

| Varyant | Bayraklar | Kategori | G5 zamansız / göç / zamanlı / NR | G4 | FCD izi | `M_downgrade_s1` / `M_forgery_crqc` |
|---|---|---|---|---|---|---|
| `MB0_taban` | MB0 | **iz** (S2) | F / F / F / V (boş) | F | var | F / V |
| `MB0_webpki_pq` | MB0, WEBPKI_PQ | **koşullu kanıt** (varsayım: kaynak doğrulaması PQ WebPKI) | V / V / V / V (boş) | V | yok | F / F |
| `MB0_wallet_expect` | MB0, WALLET_EXPECT | **koşullu kanıt** (varsayım: cüzdanda kimliği doğrulanmış, güncel RP başına beklenti) | V / V / V / V | V | yok | F / F |
| `MA_taban` | MA | **iz** (S1) | F / F / F / V (boş) | F | var | V / V |
| `MA_wallet_expect` | MA, WALLET_EXPECT | **koşullu kanıt** (aynı varsayım) | V / V / V / V | V | yok | F / F |
| `MB_taban` | MB | **iz** (S1) | F / F / F / V (boş) | F | var | V / V |
| `MB_wallet_expect` | MB, WALLET_EXPECT | **koşullu kanıt** (aynı varsayım) | V / V / V / V | V | yok | F / F |
| `MB_key_expiry` | MB, KEY_EXPIRY | kısmi: yalnız zamanlı biçim | F / F / **V** / V (boş) | F | var | V / V |
| `MC_taban` | MC | **iz** (S1) | F / F / F / V (boş) | F | var | V / V |
| `A322_taban` | A322 | **iz** (S1) | F / F / F / V (boş) | F | var | V / V |
| `A322_wallet_expect` | A322, WALLET_EXPECT | **koşullu kanıt** (aynı varsayım) | V / V / V / V | V | yok | F / F |

Sağlık lemmaları bütün varyantlarda V beklenir. Tek istisna `executable_learn`: yalnız `WALLET_EXPECT` ile V, diğerlerinde F (öğrenme kuralı yok).

Tablodaki beklentilerin hepsi kayıtlıdır; hangilerinin koşulacağı §1.3'tedir.

### 1.2 Gerekçe

**Gerekçe:**
- **M-b0 (imzasızlaştırma tabanı).** Kaynaklar:
  - HAIP 5.2: "The Wallet MUST support unsigned, signed, and multi-signed requests" (T281);
  - HAIP 5.2: "unsigned requests depend on the origin information provided by the platform and the web PKI" (T282).

  Göç etmiş RP PQ imzalar, ama cüzdan imzasız isteği kabul etmek zorundadır. Kaynak doğrulaması klasik WebPKI'ye düşer. Q-day'den sonra RP'nin TLS anahtarı çıkarılır ve RP adına imzasız istek üretilir: G4 ve G5 ihlali.
  - S1 tek başına yetmez; kaynak doğrulaması Q-day öncesinde sağlamdır. Bu yüzden `M_downgrade_s1` = F.
  - `WEBPKI_PQ` altında imzasız istek PQ taşıma kanıtıyla gelir (H1 koşulu). Klasik kabul hiç yoktur; bu yüzden FCD izi de yok.
  - Biçimsel dayanak Adım 4'teki `M_expect_unauth`.
- **M-a (yetenek müzakeresi).** #791, 12.09.2026 yorumu:
  > "it sends an HTTP header indicating its signature capabilities (e.g., `Accept-Signature-Algorithms: ML-DSA-65, ES256`) … The Verifier dynamically signs the JWT using the strongest mutually supported algorithm"

  Başlık kimliksizdir; taklit edilen uç ya da aracı "yalnız ES256" gönderir. RP klasik imzalar; cüzdan ES256'yı desteklediği için kabul eder. Bu, Q-day'siz bir downgrade (S1). Downgrade direncinin klasik dayanağı: Bhargavan vd. 2016 (L-D4: bariz olmayan sonuç sayılmaz).
  - Sunset'ten sonra dürüst RP klasik imzalamaz, ama anahtar süresi denetlenmediği için S2 sahteciliği kalır. Bu yüzden `G5_timed` = F.
- **M-b ("biri yeter").** RFC 7515 §5.2: "it is an application decision which of the JWS Signature values must successfully validate" (T314).
  - Saldırgan PQ imzasını soyar. Tek imzalı klasik JWS kabul edilir.
  - `KEY_EXPIRY` yalnız zamanlı biçimi kurtarır; göç ve zamansız biçimler S1 soymasıyla düşmeye devam eder. Bu, sunset denetiminin tek başına yetmediğini gösterir.
- **M-c (çoklu istek).** #791: "request_pqc … A PQC wallet evaluates request_pqc first, while a legacy wallet ignores unknown URL parameters and processes request".
  - Sembolik modelde "varsa önce PQ" tercihi ifade edilemez: olumsuz öncül yok. Saldırgan `request_pqc`'yi düşürür; cüzdan `request`'i işler.
  - Sonuç M-b ile aynı yapıda beklenir (S1).
- **A.3.2.2 (çoklu client_id / güven çerçevesi).** Kaynaklar:
  - "The JWS JSON Serialization … allows the Verifier to use multiple Client Identifiers and corresponding key material to protect the same request" (T269);
  - "needs to authenticate in the context of those trust frameworks" (T270);
  - semantik tanımsız (T273: "Every object in the signatures structure contains the parameters and the signature specific to a particular Client Identifier").

  Cüzdan güvendiği herhangi bir çerçeveyle doğrularsa, F1 (PQ) imzası soyulur ve F2 (klasik) ile kabul edilir: M-b yapısı. İz çıkarsa normatif dayanak T273'teki birebir alıntıdır.
- **Koşullu kanıtlar (`WALLET_EXPECT`).** Cüzdanda kimliği doğrulanmış, güncel ve RP başına bir beklenti varsa, göçten sonra klasik kapı kapanır. Bu, M-f'nin istek yönündeki karşılığıdır (taşıyıcı: TL/LoTE ya da WRPRC faz1; bkz. §4). Beklentiler R7'nin sabitlenmiş kurgusuyla (`A_pinned_min` V/V/V) tutarlıdır; kural düzeyi sonuçları burada yeniden kaydedilmez.

### 1.3 Koşum durumu ve indirgemeler (kapsam ekonomisi)

**Koşulacak:** `MB0_taban`, `MA_taban`, `MB_taban`. `MB_taban` satırının kuralı "M-b / A.3.2.2"dir; görev 3'ün G4 ve G5 sonuçları bu satırdan okunur.

| Satır | Rol | Hedef | Gerekçe |
|---|---|---|---|
| `MC_taban` | indirgendi | `MB_taban` | M-c'nin iki parametresi (`request`, `request_pqc`), iki imzalı bir kabın parametreye bölünmüş hâlidir. Saldırganın `request_pqc`'yi düşürmesi, çoklu imzadan PQ imzasını soymakla aynı etkiyi yapar: cüzdan klasik isteği işler. "Varsa önce PQ" tercihi sembolik modelde ifade edilemez (olumsuz öncül yok); ifade edilebilseydi bile öncelik, PQ parametresinin yokluğunu saldırgan varlığından ayıramaz. |
| `A322_taban` | indirgendi | `MB_taban` | Modelde aynı kurallar (`#ifdef MB \| A322`). A.3.2.2, "biri yeter" sınıfının normatif örneğidir: her imza bir `client_id`'ye ve güven çerçevesine aittir (T269, T273) ve cüzdan güvendiği herhangi biriyle doğrular. Semantik tanımsız olduğu için (T273) model "güvendiği herhangi biriyle doğrular" okumasını kullanır; bu okuma bir varsayımdır ve raporda böyle yazılır. İz çıkarsa normatif dayanak T273'ün birebir alıntısıdır (§1.2). |
| `MB0_webpki_pq` | indirgendi | `MEP_signed_fresh` (kanal sınıfı) | İmzasız isteğin tek kimlik dayanağı kaynak kanalıdır. Kanal PQ ile doğrulanmış ve istek başına güncelse G4 ve G5'in dayandığı sınıf, PQ imzalı taze meta veriyle aynıdır (H1 koşulu). |
| `MB0_wallet_expect`, `MA_wallet_expect`, `MB_wallet_expect`, `A322_wallet_expect` | indirgendi | M-f çekirdeği (`MF_cekirdek`; R7 `A_pinned_min`) | Koşul, cüzdanda RP başına kimliği doğrulanmış güncel beklentidir; bu, M-f çekirdeğinin istek yönüdür. Mekanizma (M-a, M-b, M-b0) koşul sağlandığında sonuca katkı vermez: klasik kapıyı beklenti kapatır. |
| `MB_key_expiry` | 5A-kapsandi | R7 `M_off_sunset`, `G_mg` ↔ `G_mg_no_sunset` | Sunset denetimi yalnız zamanlı biçimi kurtarır; göç ve zamansız biçimler düşmeye devam eder. R7 sonucu: `G_mg` G5_timed = V, `G_mg_no_sunset` G5_timed = F. |

Koşulan üç satırda `WALLET_EXPECT` yoktur; `no_rollback` boş yere doğrudur ve `executable_learn` = F beklenir.

## 2. İhraççı meta verisi ve kayıt: M-d, M-e, M-e′

### 2.1 Model ve beklentiler

**Model:** `modeller\M_metaveri.spthy`.
- **Taraflar:** Varlık ihraççıdır; doğrulayan, kimlik bilgisini kabul eden taraftır.
- **İhraççı anahtarları:** doğrulayıcıda özgün biçimde bilinir.
- **Beklenti değeri:** Yaşam döngüsü durumu kanaldan bir değer olarak gelir. Mekanizma bu değeri kendi anlamıyla okur; kısıtlar `GateValue` ve `LearnReq`'dir:
  - **M-e ("supported"):** klasik kapı, klasik "desteklenenler" içindeyse açıktır. Yani birlikte yaşamada açık, sunset'ten sonra kapalıdır.
  - **M-e′ ve M-d ("required"):** kapı yalnız göç öncesinde açıktır.
- **Kimlik bilgileri uzun ömürlüdür.** Göç öncesinde ihraç edilmiş klasik kimlik bilgisinin göçten ya da sunset'ten sonra sunulması, G5'in sınadığı durumdur; bu yüzden istek modelindeki "aynı evre" kısıtı burada **yoktur**.

| Varyant | Bayraklar | Kategori | G5 zamansız / göç / zamanlı / NR | G1 | FCD izi | `M_downgrade_s1` / `M_forgery_crqc` |
|---|---|---|---|---|---|---|
| `ME_taban` | ME, META_TLS | **iz** (S1: tasarım gereği) | F / F / F / F | F | var | V / V |
| `ME_signed_fresh` | ME, META_SIGNED, FRESH | kanal ablasyonu: yalnız zamanlı biçim | F / F / **V** / **V** | F | var | V / V |
| `MEP_tls_classical` | MEP, META_TLS | **iz** (S2) | F / F / F / F | F | var | F / V |
| `MEP_tls_pq` | MEP, META_TLS, WEBPKI_PQ | **koşullu kanıt** (varsayım: meta veri sunucusunun kimlik doğrulaması PQ; H1) | V / V / V / V | V | yok | F / F |
| `MEP_signed_fresh` | MEP, META_SIGNED, FRESH | **koşullu kanıt** (varsayım: PQ imzalı meta veri karar anında güncel; `iat/exp` penceresi durum değişikliğinden kısa) | V / V / V / V | V | yok | F / F |
| `MEP_signed_stale` | MEP, META_SIGNED | kanal ablasyonu: tazelik yok | **V** / F / F / F | F | var | V / V |
| `MD_static` | MD, MD_STATIC | **koşullu kanıt** (varsayım: bant dışı yapılandırma özgün ve göç/sunset anında güncellenir) | V / V / V / V | V | yok | F / F |
| `MD_reg_classical` | MD | **iz** (S1 yeniden oynatma; S2 sahtecilik) | F / F / F / F | F | var | V / V |
| `MD_reg_pq` | MD, REG_PQ | kanal ablasyonu | **V** / F / F / F | F | var | V / V |
| `MD_reg_pq_monotone` | MD, REG_PQ, MONOTONE | kanal ablasyonu | **V** / F / F / **V** | F | var | V / V |

Sağlık lemmaları bütün varyantlarda V beklenir; `executable_learn` de V'dir. M-e'de öğrenme yalnız `'retired'` ile olur.

Tablodaki beklentilerin hepsi kayıtlıdır; hangilerinin koşulacağı §2.3'tedir.

### 2.2 Gerekçe

**Gerekçe:**
- **M-e (`credential_signing_alg_values_supported`; T079, HAIP §7 T125).** "Supported" bir gereksinim değildir. Birlikte yaşamada ihraççı klasiği de desteklediğini bildirir; doğrulayıcı klasik kanıtı saldırgan olmadan da kabul eder. Bu yüzden G5-zamansız ve G5-göç düşer (S1).
  - Varsayılan kanal imzasız meta veridir: T071 "MUST support returning metadata in an unsigned form"; HAIP 9.3.1.1 T086 "Issuers use and Wallets support unsigned Issuer Metadata". Q-day'den sonra TLS kimlik doğrulaması sahtelenir; sunset'ten sonra bile "klasik desteklenir" denebilir. Bu yüzden zamanlı biçim de düşer.
  - `ME_signed_fresh`: PQ imzalı ve taze bir "supported" listesi sunset'i taşır ve zamanlı biçimi kurtarır. Göç ve zamansız biçim ise "supported ≠ required" yüzünden yine düşer. Mekanizmanın kusuru kanaldan değil anlamdan gelir.
- **M-e′ (`*_alg_values_required`; T393 `encryption_required`, T394 `key_attestations_required` örüntüsü).** "Required" ifade edilebilir. Güvenlik kanala bağlıdır; bu, H1 koşuludur. Kaynaklar:
  - imzasız + klasik TLS: Q-day'den sonra yanıt sahtelenir. İz (S2), S1 yetmez; taze sorgu göç sınırını aşmaz.
  - imzasız + PQ WebPKI, ya da PQ imzalı + taze (T073 "MUST establish trust in the signer"; T075 `iat`, T076 `exp`): koşullu kanıt.
  - PQ imzalı ama tazeliksiz: göç öncesi `'none'` nesnesi yeniden oynatılır (S1). Doğuştan göçmüş ihraççı için böyle bir nesne hiç imzalanmadığından G5-zamansız korunur.
  - Beklentiler R7'nin kanal sonuçlarıyla (çevrimdışı nesne `M_fresh`, taze kanal) tutarlıdır. Kural düzeyi sonuçları burada yeniden kaydedilmez.
- **M-d (DCR / CIMD / bant dışı; #2153 madde 3 ve 5).**
  - Kaynak: "How can a client indicate that they only want post-quantum cryptography if the server also offers traditional cryptography? This can't be per-request since that would allow downgrade attacks. Potential solutions include DCR, CIMD and out-of-band configuration" (13.08.2026).
  - Madde 5: "How can a client … registered to use a non-PQ algorithm change its configuration to use PQ algorithms?"
  - **Durağan bant dışı yapılandırma** (sabitlenmiş görünüm): koşullu kanıt. İlk temastan önce vardır, bu yüzden ilk temas korunur.
  - **Kayıt iletileriyle güncellenen yapılandırma:** kanal klasikse Q-day'den sonra sahtelenir. PQ olsa bile güncelleme iletileri yeniden oynatılabilir; göç öncesi `'none'` kaydı yeniden oynatılır (S1). Bu yüzden göç ve zamanlı biçimler düşer.
  - Tekdüzelik yalnız NR'yi kurtarır; bu, R7'deki çevrimdışı sonuçla aynı yapıdadır.
  - "Kayıt anı klasik bir kanaldan geçiyorsa beklenti sahtelenebilir mi?" sorusunun (S3 §7.5) beklenen cevabı: **evet** (`MD_reg_classical`, S2). Kanal PQ olsa bile güncelleme yoluyla geri alma mümkündür (`MD_reg_pq`, S1).

### 2.3 Koşum durumu ve indirgemeler (kapsam ekonomisi)

**Koşulacak:** `ME_signed_fresh` (M-e), `MEP_signed_fresh` (M-e′, koşullu kanıt), `MEP_tls_classical` (M-e′, çekilen kanal koşulu), `MD_reg_pq` (M-d).
- **M-e′ ayrı bir model değildir:** M-e ailesinin "required" parametresidir (`GateRequired`). `ME_signed_fresh` ↔ `MEP_signed_fresh` çifti aynı kanalı kullanır ve yalnız anlamda ayrılır. Bu, görev metnindeki "'supported' ile farkı" sorusunun doğrudan sınamasıdır.
- **`ME_signed_fresh` M-e satırıdır:** Görev M-e'yi "PQ imzalı ihraççı meta verisi" diye tanımlar. İmzasız TLS kanalı (`ME_taban`) bu tanımın dışındadır.
- **`MD_reg_pq` M-d satırıdır**, ve iş planı metnindeki beklentiyle çelişir. Plan (7.4 madde 2) "PQ kanaldan → kanıt" der. Buradaki ön kayıt ise G5_migrated = F'dir: güncelleme iletileri PQ ile imzalı olsa da yeniden oynatılabilir, ve göç öncesi `'none'` kaydı göçten sonra oynatılır (S1). Bu fark ön kayıt anında bilinçli olarak yazıldı; koşum planın mı bu dosyanın mı doğru olduğunu gösterecek.

| Satır | Rol | Hedef | Gerekçe |
|---|---|---|---|
| `ME_taban` | indirgendi | `ME_signed_fresh` (anlam) + R7 `M_pq_chan` (kanal) | "Supported ≠ required" kusuru en iyi kanalda bile G5_migrated ve G5_untimed'ı düşürür. İmzasız klasik TLS yalnız kanal boyutunu ekler (Q-day'den sonra G5_timed ve NR de düşer); bu boyut 5A'da sınandı. |
| `MEP_tls_pq` | indirgendi | `MEP_signed_fresh` | Aynı kanal sınıfı: PQ ile doğrulanmış, sorgu başına güncel çekilen meta veri (H1 koşulu). |
| `MEP_signed_stale` | 5A-kapsandi | R7 `M_fresh` | Tazeliksiz PQ imzalı nesne = tazelik boyutu. R7 sonucu: G5_migrated = F, first_contact_downgrade = V. |
| `MD_static` | 5A-kapsandi | R7 `A_pinned_min` | Bant dışı durağan yapılandırma = sabitlenmiş, varlık başına beklenti. R7 sonucu: G5_migrated / G5_timed / NR = V / V / V, FCD = F. |
| `MD_reg_classical` | indirgendi | `MD_reg_pq` (kural üst kümesi) + R7 `M_pq_chan` | `REG_PQ` yalnız `CRQC_Break_Registration` kuralını kaldırır. `MD_reg_classical` izleri `MD_reg_pq` izlerinin üst kümesidir: `MD_reg_pq`'daki F hükümleri (G5_migrated, G5_timed, NR, G1) ve V olan exists-trace hükümleri devralınır. Yalnız G5_untimed'ın F olması kanal boyutundandır (S2). |
| `MD_reg_pq_monotone` | 5A-kapsandi | R7 `M_off_monotone` | Tekdüzelik yalnız NR'yi kurtarır. R7 sonucu: `M_fresh` NR = V, `M_off_monotone` NR = F. |

## 3. M-f (sadeleştirilmiş; sertifika yolu dahil) ve görev 3b

### 3.1 Model

**Model:** `modeller\Mf_yol.spthy`. Taşıyıcı boyutu da bu dosyadadır (kip bayrağı; §4).
- **Çıpalar ve yol.** TL/LoTE çıpaları algoritma etiketiyle listeler: `!Anchor(ad, pk, alg)`. Çıpa bant dışıdır: HAIP 6.1.1 "The X.509 certificate of the trust anchor MUST NOT be included in the x5c JOSE header" (T043); ARF 6.6.3.6 "uses a trust anchor of the Provider obtained from a LoTE or Trusted List" (T063).
  - Dürüst çıpa `CAM` (PQ) bütün ihraççıları sertifikalar.
  - Yol derinliği 1 ya da 2'dir. Ara CA'lı yolun dayanağı T064: "the Provider may use an intermediate signing certificate to sign the PID or attestation".
- **Yol doğrulaması algoritma politikası taşımaz.** RFC 7515 §4.1.6 zinciri RFC 5280'e göre doğrulatır (T038). OID4VP 6.1.1.2 yalnız "at least one X.509 Certificate that matches one of the entries of the Trusted List" ister (T033). Bu yüzden listedeki her klasik çıpa Q-day'den sonra bir saldırı yüzeyidir (TS 119 312 §9.4, T069: "A trust anchor shall remain secure during the whole time period…").
- **Kenar sınıfı:** imzalayan anahtarın algoritmasıdır. Çıpanınki TL'den, ara CA'nınki kendi sertifikasından gelir. `EdgeAlg(V, I, c, a)` kabul edilen yoldaki sınıfları kaydeder.
- **Saldırı yüzeyleri (görev 3b):**
  - `ATK_DIFF`: farklı adlı klasik CA;
  - `ATK_SAME`: aynı adlı klasik CA, yani anahtar değişiminden kalan eski anahtar. Örüntü TS 119 612 A.2'de: "at all times two or more scheme operator public key certificates, with shifted validity periods" (T018);
  - `ATK_ROOT`: klasik kök; saldırgan altında PQ etiketli kendi ara CA'sını kurar.

  3b hücreleri dışındaki bütün M-f satırlarında üç yüzey birlikte açıktır ("A").
- **Kapsam yalnız beklenti `'none'` değilken uygulanır.** `'none'` iken doğrulayıcı bugünkü davranışla her geçerli yolu kabul eder.
- **Yol sınıfı lemmaları** (kabul ölçütü 2, "sertifika yolu dahil"):
  - `G5_path_untimed`, `G5_path_migrated`, `G5_path_timed`, `no_rollback_path`: PQ yaprakla kabul edilen kimlik bilgisinin yolunda klasik kenar yoktur.
  - Algoritma sınıfı için `ortak_g5.spthy` lemmaları aynen geçerlidir (`AcceptClassical` = klasik yaprak).
  - Atıf lemması `M_weak_path_forgery` (exists-trace): klasik kenarlı yoldan PQ yaprakla sahte kimlik bilgisi kabulü (kapsam atlatması).
- **`SCOPE_KEY` idealleştirmesi:** bağlı PQ anahtar, beklentiyle aynı doğrulanmış görünümden gelir (`!PinPQ`). 3b'de yalnız kimliği doğrulanmış çekirdek kipte (FRESH + PQ_CHAN) kullanılır.
- **Ön kayıtta koşulan kipler:** FRESH (çekirdek, 3b), OBJ, WRPRC, FED, CRIT (§4). Öteki kip ve değiştiriciler (PINNED, UNAUTH, GLOBAL, SELF, LAZY, MONOTONE, SUNSET_CHECK, KEY_EXPIRY) modelde durur, ama koşulmaz (§3.3, §3.4).

### 3.2 Çekirdek ve görev 3b

| Varyant | Bayraklar | Kategori | G5 zamansız / göç / zamanlı / NR | Yol: zamansız / göç / zamanlı / NR | G1 | FCD izi | `M_downgrade_s1` / `M_forgery_crqc` / `M_weak_path_forgery` |
|---|---|---|---|---|---|---|---|
| `MF_cekirdek` | FRESH, PQ_CHAN, SCOPE_PATH, A | **kanıt** (model varsayımı `Freshness`: yanıt kullanım anına dek güncel; gecikme R6'nın konusu) | V / V / V / V | V / V / V / V | V | yok | F / F / F |

**Görev 3b: kapsam × saldırı** (bayraklar FRESH, PQ_CHAN, kapsam, tek saldırı; varyant adı `MF_3b_<kapsam>_<saldırı>`):

| Kapsam \ saldırı | `ATK_DIFF` (farklı adlı klasik CA) | `ATK_SAME` (aynı adlı klasik CA) | `ATK_ROOT` (klasik kök + saldırganın PQ arası) |
|---|---|---|---|
| `yol_sinifi` (SCOPE_PATH) | **kanıt**: G1 V, yol 4 × V | **kanıt** | **kanıt** |
| `anahtar` (SCOPE_KEY) | **kanıt** (G1 V). Yol lemmaları F: yapısal iz, sahtecilik yok (`M_weak_path_forgery` F) | aynı | aynı |
| `yaprak_alg` (SCOPE_LEAF) | **iz** (S2): G1 F, yol 4 × F, `M_weak_path_forgery` V | **iz** | **iz** |

- Dokuz hücrenin hepsinde algoritma sınıfı G5 biçimleri V, FCD yok ve `M_downgrade_s1` F beklenir: beklenti kanalı çekirdektir. `M_forgery_crqc` yol_sinifi ve anahtar kapsamında F, yaprak_alg kapsamında V beklenir.
- **Tutarlılık denetimi:** `ATK_*` bayrakları yalnız kurulum kuralı ekler. Bu yüzden `MF_cekirdek`'teki V hükümleri üç `yol_sinifi` hücresini kapsar (§0.1). Hücreler yine ayrı koşulur, çünkü kabul ölçütü 2b hücre başına araç çıktısı ister; çakışma ayrıca denetlenir.

**Gerekçe (3b):**
- **`yol_sinifi`.** sheffer-02 §3.2: "Post-quantum authentication requires signatures along the entire path … a PQC end-entity certificate paired with a classically signed intermediate does not provide this property".
  - Kapsam her kenarın PQ olmasını ister. Kırılmış klasik çıpa PQ kenar üretemez.
  - Çıpa sınıfı addan değil TL kaydından gelir. Bu yüzden aynı ad (`ATK_SAME`) ve PQ etiketli ara (`ATK_ROOT`) sonucu değiştirmez.
- **`anahtar`.** Beklenti ihraççının PQ anahtarını bağlar. Yol doğrulaması klasik çıpaları hâlâ kabul eder; saldırgan gerçek PQ anahtarı kırılmış klasik CA altında yeniden sertifikalayabilir. Ama kimlik bilgisi yine ihraççınındır: G1 korunur, yol sınıfı lemmaları yapısal olarak düşer.
  - 5A R7hx: anahtar bağlama aynı adlı CA'ya karşı dayanır, CA adı bağlama dayanmaz (M-h, §6).
- **`yaprak_alg`.** Yaprak etiketi, saldırganın kırılmış klasik CA anahtarıyla imzaladığı sertifikadan gelir; PQ etiketli sahte yaprak kabul edilir.
  - Karşıt gerekçe JOSECOMP 6.2'de: "Because the certificate itself is protected by a composite signature, an attacker cannot forge a fake certificate to swap a public key even if the traditional algorithm is broken" (T055). Sertifika imzası klasikse anahtar takası mümkündür.
  - `ATK_ROOT` derinlik-2 yoludur (T064; sheffer-02 §3.2'deki "classically signed intermediate").

**Gerekçe (çekirdek).** Kimliği PQ ile doğrulanmış, karar anında güncel, varlık başına üçüncü taraf beklentisi ve yol_sinifi kapsamı. Yol olmadan aynı çekirdek R7 `S_online_core` ile kanıtlandı (11/11, çapa 4 sonrası). Burada yol ve üç saldırı yüzeyi eklenmiştir; beklenti, yolun G5 sonucunu değiştirmemesidir.
- Güncel görünüm TS 119 612'de hazır değildir: TL "Next update"e kadar önbellekte tutulabilir (T011), indirme sıklığı tanımsızdır (T030). Çevrimiçi sorgu M-f önerisinin parçasıdır.

### 3.3 A3 boyutları 1–6: 5A'da kapsandı (R7; çapa 3)

Bu boyutlar için yeni model ya da koşum yoktur. Beklenti dosyasındaki `5A-kapsandi` satırları aşağıdaki R7 varyantlarına atıftır. Sonuçlar 5A araç çıktısıdır (`model\tamarin\sonuc\ozet.csv`); yürütücünün yeniden koşumu 47/47 aynı hükmü verdi.

| A3 boyutu | Atıf satırı | R7 varyantı | R7 sonucu: G5_migrated / G5_timed / NR / FCD |
|---|---|---|---|
| 1 kimlik doğrulama / PQ kanal | `MF_a3_kimliksiz`, `MF_a3_klasik_kanal` | `M_pq_chan` | F / V / V / V (`M_source_key_broken` V) |
| 2 tazelik / sabitleme | `MF_a3_tazelik`, `MF_cekirdek_sabit` | `M_fresh`; `A_pinned_min`, `P_mf_pinned` | `M_fresh` F / V / V / V; `A_pinned_min` V / V / V / F |
| 3 tekdüzelik | `MF_cevrimdisi_monoton_yok` | `A_online_no_monotone` (çevrimiçi), `M_off_monotone` (çevrimdışı) | V / V / V / F; F / V / **F** / V |
| 4 varlık başına | `MF_a3_kuresel` | `M_per_entity` | F / V / V / V (`M_global_expectation` V) |
| sunset | `MF_cevrimdisi_sunset_yok`, `MF_cevrimdisi_anahtar_suresi` | `A_online_no_sunset` (çevrimiçi), `M_off_sunset` (çevrimdışı) | V / V / V / F; F / **F** / V / V |
| 5 üçüncü taraf ↔ öz-beyan | `MF_a3_oz_beyan` | `G_mg`, `G_mg_no_cache` | F / V / V / V; F / V / **F** / V |
| 6 ilk temas | `MF_a3_ilk_temas` | `G_mg` ↔ `P_mf_online` | FCD V ↔ FCD F |
| çevrimdışı ek | `MF_cevrimdisi` | `M_fresh` | F / V / V / V |

- R7'de G5-zamansız ve sertifika yolu yoktur. A3 × yol çaprazı koşulmaz (kapsam ekonomisi). Yol boyutu yalnız 3b ve taşıyıcı satırlarında sınanır.
- A3-7 (taşıyıcı) ve A3-8 (kapsam) yenidir: §4 ve §3.2.

### 3.4 Yola duyarlı tanım notları (koşum yok; M-f-TANIM'a girdi)

Yol eklenince R7'nin iki tanımı daralır. Model bu tanımları bayrak olarak taşır, ama bunlar ön kayıtta koşulmaz; yürütücü isterse ayrı satır olarak sonradan ön kayda alınabilir. **Değişiklik 8 (26.09.2026):** iki tanım `Mf_ek.spthy` ile 2 × 2 düzende ön kayda alındı (§9.2).
1. **`MONOTONE`:** R7'de "`SeenPQReq`'ten sonra klasik kabul yok" idi. Yola duyarlı tanım: "`SeenPQReq`'ten sonra `'none'` beklentisi hiç kullanılmaz" (`UseNone`). Dar tanımda tekdüze doğrulayıcı, bayat bir `'none'` nesnesiyle PQ etiketli ama klasik kenarlı sahte yolu kabul ederdi. Algoritma sınıfı için iki tanım aynı sonucu verir.
2. **Sunset:** anahtar düzeyi sunset (`KEY_EXPIRY`; TS 119 312 §8.4'teki takvim, T036/T037) yalnız klasik yaprağı kapatır. Sunset'ten sonra bayat `'none'` beklentisi, klasik kenarlı PQ etiketli yolu hâlâ kabul ettirir. Bu yüzden M-f'nin sunset'i beklenti düzeyinde olmalıdır (`SUNSET_CHECK`: `'none'` beklentisi sunset'ten sonra kullanılmaz; sunset anı önceden ilan edilmiş olmalı). Diğer seçenek, sunset'te klasik çıpaların TL'den çıkarılmasıdır.

## 4. M-f taşıyıcı boyutu (A3-7)

**İkame, kaldırma değil.** Taşıyıcı değiştirilir, öteki boyutlar sabit kalır (A, SCOPE_PATH; PQ_CHAN ya da karşılığı). Taşıyıcı `Mf_yol.spthy`'de kip bayrağıdır.

**Hipotez:** Sonuç taşıyıcının adına değil kanal sınıfına bağlıdır:
- çekilen ve güncel,
- aktarılan ya da önbellekte, yeniden oynatılabilir,
- kimliksiz.

İmzalayan algoritma da sonucu belirler. Beklenti vektörleri bu yüzden kanal sınıfı aynı olan satırlarda özdeştir; koşumdan sonra bu eşitlik ayrıca sınanır. Beklenen eşdeğerlik sınıfları:
- {`MF_cekirdek`, `MF_tas_federasyon_pq`}: çekilen ve güncel, PQ;
- {`MF_tas_tl_onbellek`, `MF_tas_wrprc_faz1`, `MF_tas_federasyon_bayat`}: imzalı ama yeniden oynatılabilir;
- {`MF_tas_wrprc_faz0`, `MF_tas_crit_baslik`}: kimliksiz ya da korunan nesnenin içinde;
- {`MF_tas_federasyon_klasik_ara`}: çekilen ve güncel, ama imzalayan klasik (5A `M_pq_chan` ile aynı yapı).

| Varyant | Taşıyıcı ve kanal sınıfı | Bayraklar | Kategori | G5 zamansız / göç / zamanlı / NR (yol aynı) | G1 | `M_downgrade_s1` / `M_forgery_crqc` / `M_weak_path_forgery` |
|---|---|---|---|---|---|---|
| `MF_cekirdek` (§3.2) | TL/LoTE, çekilen ve güncel | FRESH, PQ_CHAN, SCOPE_PATH, A | **kanıt** | V / V / V / V | V | F / F / F |
| `MF_tas_tl_onbellek` | TL/LoTE, önbellek (≤ Next update) | OBJ, PQ_CHAN, SCOPE_PATH, A | taşıyıcı | V / F / F / F | F | V / V / V |
| `MF_tas_wrprc_faz0` | WRPRC, aktarılan, doğrulanmıyor (T254) | WRPRC, PQ_CHAN, SCOPE_PATH, A | **iz** (S1) | F / F / F / F | F | V / V / V |
| `MF_tas_wrprc_faz1` | WRPRC, aktarılan, imzalı, yeniden oynatılabilir | WRPRC, WRPRC_FAZ1, PQ_CHAN, SCOPE_PATH, A | taşıyıcı | V / F / F / F | F | V / V / V |
| `MF_tas_federasyon_pq` | OpenID Federation, çekilen ve güncel, PQ ara | FED, FED_INT_PQ, SCOPE_PATH, A | **koşullu kanıt** (varsayım: çözümleme yanıtı sorguya bağlı ve güncel) | V / V / V / V | V | F / F / F |
| `MF_tas_federasyon_klasik_ara` | OpenID Federation, çekilen, klasik ara anahtar | FED, SCOPE_PATH, A | **iz** (yalnız S2) | F / F / F / F | F | F / V / V |
| `MF_tas_federasyon_bayat` | OpenID Federation, `trust_chain` başlığı ya da önbellek | FED, FED_INT_PQ, FED_STALE, SCOPE_PATH, A | taşıyıcı | V / F / F / F | F | V / V / V |
| `MF_tas_crit_baslik` | `crit` başlığı (yalnız ablasyon) | CRIT, SCOPE_PATH, A | ablasyon, **iz** (S1) | F / F / F / F | F | V / V / V |

- Bütün taşıyıcı satırlarında FCD izi var beklenir; tek istisna `MF_tas_federasyon_pq`'dur (yok). Sağlık lemmaları V beklenir.
- **`MF_tas_wrprc_faz1_ek` indirgendi:** WRPRC faz1 + çevrimdışı ek. Çevrimdışı ekin etkisi 5A'da sınandı (R7 `M_fresh`); taşıyıcı eşdeğerliği `MF_tas_wrprc_faz1` satırıyla sınanır.

**Gerekçe:**
- **TL/LoTE.** Kaynaklar:
  - imza: "Lists of trusted entities shall be signed" (T022); JAdES-B (T023–T025);
  - çıpa OJEU'da sabitli (T001, T029);
  - yeniden oynatma penceresi "Next update" (T009/T019, ≤ 6 ay T010/T021);
  - önbellek (T011).

  Güncel görünüm ya da çevrimiçi sorgu, M-f'nin çekirdek varsayımıdır (§3.2).
- **WRPRC.**
  - İmzalı (T258: "shall be signed with the digital signature of provider of the wallet-relying party registration certificates"). İmzalayanın sertifikası TL'dedir (T260).
  - İstekte ve meta veride değerle taşınır (T252, T088; ihraççı için T087). Yani aktarılan bir artefakttır; varlık hangi sürümü sunacağını seçer, bu da eski sürümün yeniden oynatılabileceği demektir.
  - Faz0'da cüzdan doğrulamaz: "only applies as of 24 months after entry into force" (T254). Bu dönemde WRPRC kimliksiz bir alandır.
  - İptal yalnız 24 saatten uzun geçerlilikte zorunludur (T250). İptal denetimi tazelik sağlayabilir, ama bu modellenmedi (kısıt tablosuna not).
- **OpenID Federation** (`01-korpus\metin\OIDFED.txt`):
  - TA anahtarları bant dışı dağıtılır: "The Trust Anchor's public keys are distributed … in some secure out-of-band way" (§4, satır 897).
  - Alt bildirimler fetch uç noktasından çekilir (§8.1, satır 2407).
  - `exp` zorunludur ve bildirim o ana dek kabul edilir (§3.1 satır 646, §3.2 satır 760). Bu yüzden önbellekteki bildirim geçerlilik süresi içinde yeniden oynatılabilir.
  - `trust_chain` JWS başlığıyla zincir aktarılabilir: "Most signed JWTs MAY include the trust_chain JWS header parameter" (§4.3, satır 964–966). Bu hâl `FED_STALE`'dir.
  - Ara varlık anahtarı klasikse Q-day'den sonra bildirim sahtelenir: PQ bir TA yetmez, federasyon zincirinin kendisi de PQ olmalıdır.
- **`crit` (yalnız ablasyon).** RFC 7515 §4.1.11: "If any of the listed extension Header Parameters are not understood and supported by the recipient, then the JWS is invalid" (T386).
  - `crit`, beklentiyi korunan nesnenin içine koyar. Saldırganın sunduğu klasik kopya işareti taşımaz; durumsuz doğrulayıcıda NR de düşer.
  - İşaret belleğe alınırsa A3-5'e (öz-beyan / TOFU; 5A `G_mg`) dönüşür.
  - Tek yan etkisi, işaretli PQ nesnenin eski doğrulayıcılarda reddedilmesidir: güvenlik değil, birlikte çalışabilirlik maliyetidir; kısıt tablosuna yazılır.

## 5. M-g (sheffer-02): 5A'da kapsandı

Yeni model yoktur. Beklenti dosyasındaki üç satır R7'ye atıftır:

| Atıf satırı | R7 varyantı | R7 sonucu: G5_migrated / G5_timed / NR / FCD |
|---|---|---|
| `MG_ozbeyan` | `G_mg` (MG, MONOTONE, SUNSET_CHECK) | F / V / V / V |
| `MG_sunset_yok` | `G_mg_no_sunset` (MG, MONOTONE) | F / **F** / V / V |
| `MG_onbellek_yok` | `G_mg_no_cache` (MG, SUNSET_CHECK) | F / V / **F** / V |

- **Kategori:** ilk temas izi (G5_migrated F, FCD V); sonraki temaslarda koşullu kanıt (NR V). Koşul, önbelleğin geçerlilik süresinin sürmesidir (`G_mg_no_cache` NR F).
- **Kaynak:** sheffer-02 §1 ("A client begins enforcing the server's PQC commitment only after it has successfully connected to the legitimate server at least once"), §3.6 (önbellek kuralları), §5.1 ("behavior matches the usual trust-on-first-use limitation").

**Ön kayda alınmamış aday (koşum yok; yürütücü kararına).** sheffer-02'nin zincir politikası iki okumaya açıktır.
- §3.1 tanımı: "a PQC end-entity certificate is one that is not traditional-only: the EE signature employs post-quantum cryptography".
- §3.2 kuralı: "the client MUST apply its PQC policy to every CertificateEntry … using the same criterion as in Section 3.1".

İki okuma şunlardır:
- **İmza okuması** (her sertifikanın üzerindeki imza PQ): `yol_sinifi` ile aynıdır. Önbellek dolduktan sonra 3b saldırıları kapanır.
- **Anahtar okuması** (her sertifikanın anahtarı "not traditional-only"): klasik bir CA'nın imzaladığı PQ anahtarlı sertifika geçer. Bu durumda önbellek dolduktan sonra da 3b saldırıları geçer. Ayrıca saldırgan böyle bir zincirle `algorithm_validity_period = 0` gönderip önbelleği sildirebilir (§3.6 madde 2: "the client MUST clear the cached information") ve sonra klasik yola düşürebilir.

§3.2'nin ilk cümlesi imza okumasının amaçlandığını gösterir, ama normatif ölçüt §3.1'e gönderme yapar. Bu belirsizlik koşumla sınanmadı. `M_h.spthy`'deki yol altyapısıyla 2–4 satırlık bir ek olarak ön kayda alınabilir. **Değişiklik 8 (26.09.2026):** iki okuma `Mg_yol.spthy` ile ön kayda alındı (§9.1).

## 6. M-h (reddy-01, vicente-02) ve görev 3a

### 6.1 Model

**Model:** `modeller\M_h.spthy`. Yol altyapısı (çıpalar, `ATK_*`, derinlik 1–2) Mf_yol ile aynıdır; yol doğrulaması iki taslakta da değişmez.
- **reddy tipi (`MH_REDDY`).** PQCHC eki PQC sertifikasındadır.
  - Doğrulayıcı, yol doğrulamasından sonra SAN ve yaprak algoritmasını önbelleğe alır (§3.3).
  - Önbellek varken yalnız geleneksel yaprak reddedilir (§3.3, "SHOULD treat the behavior as suspicious and terminate"; varsayım R1: SHOULD uygulanır).
  - Pencere, iptal ve PQC→PQC değişimi modellenmez.
- **vicente tipi (`MH_VICENTE`).** Klasik sertifika, gelecekteki PQ anahtarının özetini taşır (§4.1).
  - Doğrulayıcı ilk gördüğü taahhüdü tutar (varsayım V2).
  - Ardıl PQ sertifikası yalnız özet eşleşirse kabul edilir (varsayım V1: taahhüt hatası reddedilir).
  - Klasik sertifika kabulü değişmez: taahhüt danışma niteliğindedir.
- **`CA_PQ` yoksa** dürüst CA klasiktir: görev 3a (i).
- **`NAME_BIND`** (yalnız reddy): önbellek, yaprağı imzalayan CA'nın adını da tutar (R7h'deki ad bağlama).
- **Lemmalar:**
  - `ortak_g5` (ilk temas dahil);
  - `G1_claims_unforgeability`;
  - öğrenme sonrası: `G1_learned` (her kabul), `G1_learned_pq` (PQ yaprakla kabul; 3b ölçütü), `no_rollback_path`;
  - yalnız vicente: `G1_learned_pq_genuine` (gerçek taahhüdü sabitlemiş doğrulayıcı);
  - atıf: `M_downgrade_s1`, `M_forgery_crqc`.

### 6.2 Varyantlar ve beklentiler

| Varyant | Bayraklar | Rol | G5 zamansız / göç / zamanlı / NR | FCD izi | G1 | `G1_learned` | `G1_learned_pq` | `G1_learned_pq_genuine` | `no_rollback_path` | `M_downgrade_s1` / `M_forgery_crqc` |
|---|---|---|---|---|---|---|---|---|---|---|
| `MH_reddy_klasik_zincir` | MH_REDDY | 3a (i) | F / F / F / V | var | F | F | F | — | F | V / V |
| `MH_reddy_farkli_ad` | MH_REDDY, CA_PQ, ATK_DIFF | 3b | F / F / F / V | var | F | F | F | — | F | V / V |
| `MH_reddy_ayni_ad` | MH_REDDY, CA_PQ, ATK_SAME | 3b | F / F / F / V | var | F | F | F | — | F | V / V |
| `MH_reddy_klasik_kok` | MH_REDDY, CA_PQ, ATK_ROOT | 3b | F / F / F / V | var | F | F | F | — | F | V / V |
| `MH_reddy_adbag_farkli_ad` | MH_REDDY, CA_PQ, NAME_BIND, ATK_DIFF | 3a (ii) sınırı | F / F / F / V | var | F | F | F | — | F | V / V |
| `MH_vicente_klasik_zincir` | MH_VICENTE | 3a (i) | F / F / F / F | var | F | F | F | V | F | V / V |
| `MH_vicente_farkli_ad` | MH_VICENTE, CA_PQ, ATK_DIFF | 3b | F / F / F / F | var | F | F | F | V | F | V / V |
| `MH_vicente_ayni_ad` | MH_VICENTE, CA_PQ, ATK_SAME | 3b | F / F / F / F | var | F | F | F | V | F | V / V |
| `MH_vicente_klasik_kok` | MH_VICENTE, CA_PQ, ATK_ROOT | 3b | F / F / F / F | var | F | F | F | V | F | V / V |

- **Kategoriler:**
  - Bütün satırlarda G5 biçimleri **iz**dir: ilk temas korunmaz. Bu, taslakların kendi önyükleme sınırıdır (reddy §5.3; sheffer-02 §5.1).
  - reddy NR **kanıt**tır (R1 varsayımıyla); vicente NR **iz**dir (danışma niteliği).
  - `G1_learned_pq` iki tipte de **iz**dir.
  - vicente `G1_learned_pq_genuine` **koşullu kanıt**tır (V1, V2).
- Sağlık lemmaları V beklenir; `executable_learn` V'dir.
- `no_rollback_path` F'nin kaynağı tipe göre değişir:
  - reddy ve klasik zincir: sahte ya da dürüst klasik kenarlı yol;
  - vicente + `CA_PQ`: gerçek PQ anahtarın klasik CA altında yeniden sertifikalanması (yapısal, `anahtar` kapsamındaki gibi).

### 6.3 Gerekçe

- **reddy.** Kaynaklar:
  - §3.1: "This extension does not extend the certificate’s validity period and does not modify path validation procedures as defined in [RFC5280]."
  - §3.3 önbellek: "the server identity (as indicated in the certificate’s SubjectAltName), the PQC or composite algorithm identifier … associated with the end-entity certificate".
  - §3.3 kural: "If, within the effective continuity window, a relying party observes only a traditional certificate while the cached PQC/composite certificate remains unrevoked, the relying party SHOULD treat the behavior as suspicious and terminate the connection."
  - Algoritma farklıysa bile red yoktur: "If the operator changes from one PQC algorithm to another … the relying party MUST start a new continuity period."

  Tek denetim yaprak algoritmasıdır. Q-day'den sonra herhangi bir klasik CA anahtarı aynı SAN için PQC etiketli sertifika imzalar; RFC 5280'e göre klasik zincir geçerlidir; reddy denetimi de geçer. Sonuç: `G1_learned_pq` = F.
- **vicente.** Kaynaklar:
  - §4.1: taahhüt, CA imzasıyla korunan klasik sertifikadadır.
  - §4.2: "When a subsequently issued certificate for the same subject presents a post-quantum key, the following verification procedure applies".
  - §4.2: "A relying party MUST NOT treat a PQCHC commitment as a reason to accept a certificate it would otherwise reject. The commitment is advisory."
  - §7: "The commitment is advisory and MUST NOT be treated as authentication of the committed post-quantum key."
  - REQ-3 (uyuşmazlık = taahhüt hatası), REQ-4 (süre sonrası uygulanmaz).

  Sonuçlar:
  - Klasik kabul değişmez: NR = F, `G1_learned` = F.
  - Taahhüt klasik sertifikada taşındığı için, Q-day'den sonra sahte bir taahhüt doğrulayıcının ilk öğrendiği taahhüt olabilir (zehirleme): `G1_learned_pq` = F.
  - Gerçek taahhüdü sabitlemiş doğrulayıcı için PQ ardıllar yalnız dürüst anahtarla kabul edilir: `G1_learned_pq_genuine` = V.
  - §7.2 CA'nın yeniden ihracını "CA-compromise scenario" sayar. CRQC altında her klasik CA bu anlamda ele geçirilmiştir, yani taslağın kendi tehdit varsayımı düşer.
- **Ad bağlama sınırı (`MH_reddy_adbag_farkli_ad`).** 5A R7hx: ad bağlama yalnız CA adları tekse tutar. Mekanizma düzeyinde ara CA vardır: herhangi bir klasik CA anahtarını tutan saldırgan, meşru CA'nın adını taşıyan bir ara CA sertifikası çıkarabilir. Böylece bağlama, farklı adlı alternatif CA'ya karşı bile düşer. Ön kayıt F'dir. V çıkarsa ya yol modeli hatalıdır ya da ara CA'lar ad kısıtıyla sınırlıdır; bu incelenir.
- **Pencere sonrası (koşum yok):** reddy'nin "effective continuity window"u ve vicente'nin `commitmentNotAfter`'ı (REQ-4) bittikten sonra koruma yoktur. Bu, taslak metninden doğrudan çıkar ve 5A `G_mg_no_cache` ile aynı yapıdadır; ayrı satır açılmadı.

**(b) niteleyicisi (ÖK §2C madde 3; raporda gerekçelendirilecek):**
- **reddy: aday.** Taslağın kendi işleme kuralları altında (§3.1 yol doğrulaması değişmez; §3.3 önbellek SAN + algoritma), bir CRQC saldırganı güven deposundaki herhangi bir klasik CA'dan sahte PQC sertifikası sunar ve fark edilmez. Oysa taslağın amacı (§1) CRQC ile MitM'i engellemektir.
  - **Uyarı:** sheffer-02 §3.2 (ortak yazar Reddy) "a PQC end-entity certificate paired with a classically signed intermediate does not provide this property" der. Olgu komşu literatürde öngörülmüştür; bu yüzden (b)'nin "türetilemeyen" koşulu tartışmalıdır. Rapor bunu açıkça tartışmalıdır.
- **vicente: aday değil.** Taslak taahhüdün danışma niteliğinde olduğunu ve kimlik doğrulama olmadığını açıkça söyler (§7). Klasik düşüş tasarım gereğidir. Zehirleme ise taahhüdün klasik sertifikada taşınmasının doğrudan sonucudur (3a-i).

### 6.4 Görev 3a: beklenen cevaplar

- **(i) Taahhüt eki yalnız klasik zincirde taşınıyorsa korur mu?** → **Hayır.**
  - reddy (`MH_reddy_klasik_zincir`): `G1_learned_pq` = F. Q-day'den sonra klasik CA anahtarı saldırganın anahtarına PQC etiketli sertifika imzalar; önbellekteki algoritma eşleşir.
  - vicente (`MH_vicente_klasik_zincir`): `G1_learned_pq` = F (sahte taahhüt ilk öğrenilir) ve NR = F (danışma). Anahtar bağlama yalnız gerçek taahhüdü sabitlemiş doğrulayıcıda tutar (`G1_learned_pq_genuine` = V).
  - İki tipte de G5'in üç biçimi F'dir (ilk temas).
- **(ii) Ad bağlaması olmadan alternatif CA yoluyla taahhütsüz bir sertifika kabul ettirilebilir mi?** → **Evet.**
  - reddy (`MH_reddy_farkli_ad`): alternatif CA'nın PQC sertifikası kabul edilir, PQCHC eki olsa da olmasa da; reddy yaprağı imzalayan CA'yı denetlemez.
  - vicente (`MH_vicente_farkli_ad`): alternatif CA'nın taahhütsüz klasik sertifikası kabul edilir (danışma; `G1_learned` = F). PQ yolu da zehirlemeyle açıktır (`G1_learned_pq` = F).
  - Ad bağlamayla da cevap evettir: saldırgan meşru CA'nın adını taşıyan bir ara CA kullanır (`MH_reddy_adbag_farkli_ad`).
- **(iii) M-f'nin varlık başına kapsamı bu yolu kapatıyor mu?**
  - **Evet**, `yol_sinifi` (`MF_3b_yol_*`: G1 V, yol lemmaları V) ve `anahtar` (`MF_3b_anahtar_*`: G1 V) ile.
  - **Hayır**, `yaprak_alg` ile (`MF_3b_yaprak_*`: G1 F).
  - reddy'nin önbelleği, fiilen yaprak_alg kapsamı artı ilk temas açığıdır; eşleşen F bundandır.

## 7. KB çoklu imza alt hücresi (görev 3c; betimsel)

Model yazılmadı (kapsam ekonomisi). 3c tanımlayıcı bir alt hücredir, yeni bir doğrulayıcı hipotezi değildir (IS-PLANI 3c). Beklenen cevap RFC 9901 metninden (`01-korpus\metin\RFC9901.txt`):
- **§8.1:** "the digest in the sd_hash claim MUST be computed over the SD-JWT as described in Section 4.3.1 … the SD-JWT Compact Serialization part is built by concatenating the protected header, the payload, and the signature of the JWS JSON serialized SD-JWT". General JSON'da birden çok imza varken "the signature" tekildir; hangisi olduğu tanımsızdır.
- **§8.3:** "disclosures and kb_jwt MUST be included in the first unprotected header". Bu, pratikte ilk imzaya işaret eder.
- **§8.1:** "Unprotected headers other than disclosures are not covered by the digest".
- **Beklenen sonuç:** KB-JWT en fazla bir imzayı bağlar.
  - Bağlanan imza klasikse, PQ imzası soyulunca KB-JWT geçerli kalır.
  - Bağlanan imza PQ ise soyma `sd_hash` uyuşmazlığıyla yakalanır.

  Senaryo (d) ve H5 için alt hücre notudur; içerik D-S3 ve DB-1 ile aynıdır.
- Araç kanıtı istenirse küçük bir model (iki imza × bağlanan imzanın seçimi) sonradan ön kayda alınabilir.

## 8. Özet tablo: mekanizma × G5 biçimi (ön kayıt)

| Mekanizma | Kanıt satırı | G5 zamansız | G5 göç | G5 zamanlı | NR | Beklenen kategori |
|---|---|---|---|---|---|---|
| M-b0 | `MB0_taban` | F | F | F | V (boş) | iz (S2). Koşul: PQ ile doğrulanmış kaynak kanalı (indirgendi, §1.3) |
| M-a | `MA_taban` | F | F | F | V (boş) | iz (S1) |
| M-b / A.3.2.2 | `MB_taban` | F | F | F | V (boş) | iz (S1); A.3.2.2 okuması varsayım (T273) |
| M-c | → `MB_taban` | F | F | F | V (boş) | iz (S1); indirgeme (§1.3) |
| M-d | `MD_reg_pq` | V | F | F | F | iz (S1: kayıt güncellemesinin yeniden oynatılması). Durağan yapılandırma koşullu kanıt (R7 `A_pinned_min`). Plan metniyle çelişen ön kayıt (§2.3) |
| M-e | `ME_signed_fresh` | F | F | V | V | iz (S1: supported ≠ required) |
| M-e′ | `MEP_signed_fresh` / `MEP_tls_classical` | V / F | V / F | V / F | V / F | koşullu kanıt (PQ ile doğrulanmış taze kanal) / iz (S2, klasik WebPKI) |
| M-f çekirdek (yol dahil) | `MF_cekirdek` | V | V | V | V | kanıt; yol biçimleri de V |
| M-f çevrimdışı ek | R7 `M_fresh` (5A) | — | F | V | V | 5A sonucu |
| M-g | R7 `G_mg` (5A) | — | F | V | V | ilk temas izi; sonraki temaslarda koşullu kanıt |
| M-h reddy | `MH_reddy_*` | F | F | F | V | iz (ilk temas); öğrenmeden sonra 3b saldırıları geçer (`G1_learned_pq` F) |
| M-h vicente | `MH_vicente_*` | F | F | F | F | iz (danışma); gerçek taahhüdü sabitlemiş doğrulayıcıda PQ ardılları için koşullu kanıt |

## 9. EK — Değişiklik 8 (26.09.2026): M-g zincir politikasının iki okuması ve yola duyarlı M-f tanımları

Yürütücü, §3.4 ve §5'teki iki aday grubu ön kayda aldı. Önceki 63 satır ve önceki model dosyaları değişmedi. Özetleri çapaya bağlanacak dosyalara dokunmamak için iki yeni model dosyası eklendi: `Mg_yol.spthy` ve `Mf_ek.spthy`. Yeni satırlar beklenti dosyasının sonundaki [8] bloğundadır.

### 9.1 M-g (sheffer-02) zincir politikası × görev 3b (`modeller\Mg_yol.spthy`)

**Model:**
- Yol altyapısı `Mf_yol` ve `M_h` ile aynıdır: `CAM` (PQ), `ATK_*`, derinlik 1–2.
- **Taahhüt**, PQ imzalı kimlik bilgisinin içinde taşınır: `m` ∈ {`'commit'`, `'zero'`, `'nocommit'`}.
  - Dürüst PQ kimlik bilgisi `'commit'` taşır (§3.7: "If a PQC certificate is used, the server MUST send exactly the four-octet algorithm_validity_period").
  - Klasik kimlik bilgisi `'nocommit'` taşır.
- **Önbellek (§3.6):**
  - Politikaya uyan kabul + `'commit'` önbelleği doldurur (`SeenPQReq`).
  - Politikaya uyan kabul + `'zero'` önbelleği siler (`CacheEnd`; madde 2: "the client MUST clear the cached information").
  - Önbellek varken politika dışı kabul yoktur (§3.2).
  - Uzantılı nesne politika dışı zincirle kabul edilmez (§3.2: "including because the server sends non-empty pq_cert_available extension data").
  - Süre modellenmez; süre boyutu 5A'da sınandı (R7 `G_mg_no_cache`).
- **Okumalar:**
  - `MG_ANAHTAR`: her CertificateEntry'nin **anahtarı** PQ (§3.1: "not traditional-only"). Çıpa CertificateEntry değildir (HAIP 6.1.1, T043), bu yüzden çıpadan çıkan kenar denetlenmez.
  - `MG_IMZA`: her CertificateEntry'nin üzerindeki **imza** PQ ve yaprak anahtarı PQ (§3.2'nin ilk cümlesi: "signatures along the entire path"). Bu okuma `yol_sinifi` ile aynıdır.
- **Yeni atıf lemması `M_cache_cleared`** (exists-trace): dolmuş önbellek saldırganca sildirilebilir mi.

| Varyant | Okuma | Saldırı | G5 zamansız / göç / zamanlı / NR | FCD izi | G1 | `G1_learned` | `G1_learned_pq` | `no_rollback_path` | `M_downgrade_s1` / `M_forgery_crqc` / `M_cache_cleared` |
|---|---|---|---|---|---|---|---|---|---|
| `EK_mg_anahtar_farkli_ad`, `_ayni_ad`, `_klasik_kok` | anahtar | DIFF / SAME / ROOT | F / F / F / **F** | var | F | **F** | **F** | **F** | V / V / **V** |
| `EK_mg_imza_farkli_ad`, `_ayni_ad`, `_klasik_kok` | imza | DIFF / SAME / ROOT | F / F / F / V | var | F | V | V | V | V / V / F |

**Gerekçe:**
- **İki okumada da ilk temas korunmaz** (§5.1: "behavior matches the usual trust-on-first-use limitation"). G5'in üç biçimi F'dir; okumalar yalnız önbellek dolduktan sonra ayrışır.
- **Anahtar okuması.** Q-day'den sonra saldırgan kendi PQ anahtarını kırılmış bir klasik CA altında sertifikalar (üç yüzeyin herhangi biri).
  - Derinlik 1'de tek CertificateEntry yapraktır ve anahtarı PQ'dur; derinlik 2'de (`ATK_ROOT`) saldırganın ara CA'sının anahtarı da PQ'dur. Politika sağlanır.
  - Önbellek dolduktan sonra sahte PQ kimlik bilgisi kabul edilir: `G1_learned_pq` = F.
  - Aynı zincirle `'zero'` gönderilir ve önbellek silinir (`M_cache_cleared` = V). Ardından klasik yol yeniden açılır: NR = F.
  - §5.1 bu bağımlılığı sezer ("Cached entries are only as reliable as the authenticated channel that produced them"). §5.2 ise sıfır/sıfır dışı değiştirmeyi yalnız DoS olarak ele alır, düşürme olarak değil.
- **İmza okuması.** Her sertifika imzası PQ olmalıdır. Tek PQ çıpa `CAM` saldırgan anahtarı imzalamaz. Önbellek dolduktan sonra her kabul gerçektir (`G1_learned` = V) ve önbellek silinemez. Bunun iki sebebi vardır: dürüst varlık bu yaşam döngüsünde taahhüdü geri çekmez, saldırgan da politikayı sağlayan bir zincir üretemez.
- **Kategori:**
  - anahtar okuması: önbellekten sonra **iz** (S2);
  - imza okuması: önbellekten sonra **koşullu kanıt** (koşullar: önbellek süresi sürer; dürüst varlık geri çekmez).
- **Neden önemli:** Taslağın kendi işleme kuralı sonucu belirler. §3.2'nin ilk cümlesi imza okumasını amaçladığını gösterir. Ama normatif ölçüt §3.1'e gönderme yapar; §3.1'deki "not traditional-only" ifadesi doğal olarak bir anahtar niteliği (PQ ya da composite anahtar) gibi okunur.
  - Anahtar okumasında taslağın koruması, herhangi bir klasik CA anahtarını tutan CRQC saldırganına karşı düşer. Bu, reddy ile aynı türden bir (b) niteleyicisi adayıdır.
  - Aynı uyarı geçerlidir: taslak §3.2'de klasik imzalı ara CA'yı açıkça anar. Rapor iki okumayı da sunmalı ve hangisinin taslak metnine uyduğunu tartışmalıdır.

### 9.2 M-f çevrimdışı ekinin yola duyarlı tanımları, 2 × 2 (`modeller\Mf_ek.spthy`)

**Model:** `Mf_yol`'un OBJ kipinin özdeş kopyasıdır: TL/LoTE önbelleği, PQ imzalı ama yeniden oynatılabilir beklenti nesnesi, `SCOPE_PATH` ve üç saldırı yüzeyi birlikte. Yalnız iki eksen bayraklıdır:
- **tekdüzelik:**
  - `MONOTONE_DAR` (R7 tanımı: `'pq_required'`den sonra klasik yaprak yok);
  - `MONOTONE_GENIS` (`'pq_required'`den sonra `'none'` beklentisi hiç kullanılmaz);
- **sunset:**
  - `SUNSET_ANAHTAR` (iş planı 7.1: "sunset'te klasik anahtarın süresinin dolması"; TS 119 312 §8.4 takvimi, T036/T037);
  - `SUNSET_BEKLENTI` (`'none'` beklentisi sunset'ten sonra kullanılmaz; sunset anı önceden ilan edilmiş olmalı).

| Varyant | Tekdüzelik | Sunset | G5 zamansız / göç / zamanlı / NR | Yol: zamansız / göç / zamanlı / NR | G1 | FCD izi | `M_downgrade_s1` / `M_forgery_crqc` / `M_weak_path_forgery` |
|---|---|---|---|---|---|---|---|
| `EK_mf_r7_tanimlari` | dar | anahtar | V / F / V / V | V / F / **F** / **F** | F | var | V / V / V |
| `EK_mf_monoton_genis` | geniş | anahtar | V / F / V / V | V / F / **F** / V | F | var | V / V / V |
| `EK_mf_sunset_beklenti` | dar | beklenti | V / F / V / V | V / F / V / **F** | F | var | V / V / V |
| `EK_mf_yola_duyarli` | geniş | beklenti | V / F / V / V | V / F / V / V | F | var | V / V / V |

**Öngörü:**
- Algoritma sınıfındaki G5 biçimleri dört satırda aynıdır. Bu, R7 sonucunun (`M_fresh`, `M_off_monotone`, `M_off_sunset`) yolla yeniden üretimidir: göç biçimi ilk temasta F, zamanlı biçim ve NR V.
- Yol sınıfındaki biçimler eksenlere göre ayrışır: tekdüzelik ekseni NR_yol'u, sunset ekseni zamanlı_yol'u belirler.
- Yalnız yola duyarlı birleşim, yol biçimlerine algoritma biçimleriyle aynı profili verir.

**Gerekçe:**
- Dar tekdüzelik yalnız klasik yaprağı kapatır. Önbelleği görmüş doğrulayıcı sonraki bir oturumda bayat `'none'` nesnesini kullanırsa, PQ etiketli ama klasik kenarlı sahte yol kabul edilir.
- Anahtar düzeyi sunset yalnız klasik ihraççı anahtarını kapatır. Sunset'ten sonra bayat `'none'` ile klasik kenarlı PQ yol kabul edilir; bu yolda klasik ihraççı anahtarı kullanılmaz.

**Kategori** (`EK_mf_yola_duyarli`):
- zamansız biçim ve NR **kanıt**;
- göç biçimi **iz** (ilk temas);
- zamanlı biçim **koşullu kanıt** (sunset önceden ilan edilmiş);
- yol biçimleri aynı profildedir.

Öteki üç satır ablasyondur.

**Sonuç öngörüyü doğrularsa:** M-f-TANIM (görev 9) yola duyarlı tanımları kullanır. İş planındaki "sunset'te klasik anahtarın süresinin dolması" ifadesinin yerine beklenti düzeyinde sunset (ya da sunset'te klasik çıpaların TL'den çıkarılması) yazılır.

### 9.3 Koşum ve iyi biçimlilik

- 10 yeni koşum satırı eklendi: 6 `Mg_yol`, 4 `Mf_ek`. İyi biçimlilik 10/10 temiz (uyarı 0; `--derivcheck-timeout=60`). Kayıt: `iyi_bicimlilik_on_kayit.txt` sonundaki EK bloğu.
- Koşulacak satır sayısı 43'e çıktı (33 + 10). Koşum çapa 8'den ve teknik kapıdan sonra yapılır.
