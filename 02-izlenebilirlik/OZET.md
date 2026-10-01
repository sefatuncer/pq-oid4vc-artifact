# İzlenebilirlik matrisi — özet (Adım 1)

> **Tarih:** 24.09.2026 · **Hazırlayan:** korpus çalışması (Adım 1)
> **Girdi:** `01-korpus/MANIFEST.csv` (51 dosya, SHA-256 sabit) · **Matris:** `izlenebilirlik.csv`
> **Doğrulama:** `alinti_dogrula.py` → `alinti_dogrulama.txt`: **395/395** alıntı metinde birebir bulundu (391'i yalnız boşluk daraltmayla, 4'ü ek olarak satır sonu tire birleştirmesiyle; 300 karakter sınırını aşan yok).
> **Sayılar:** `ozet_tablolari.py` → `kapsama_tablolari.md` (bu dosyadaki bütün sayılar oradan).
> **Oluşturucu:** `matris_olustur.py` (satırlar birincil metin okunarak elle yazıldı; betik yalnız kimlik atar ve CSV yazar).

## 1. Kapsam ve yöntem

- **395 satır**, matriste **39 belge** geçiyor. 13 artefaktın **13'ü** en az 7 satırla kapsanıyor. Artefakta bağlanamayan genel JOSE/COSE, hibrit ve bilinen-cevap (DNSSEC) kuralları "genel" altında (79 satır).
- Seçim ölçütü: algoritma seçimi/müzakeresi, güven zinciri, beklenti taşıma, anahtar bağlama, tazelik/geçerlilik/önbellek, çoklu imza ve downgrade ile ilgili normatif (MUST/SHALL/SHOULD/MAY…) ya da bu kuralları yorumlamak için gerekli bilgi cümleleri. Sayı hedefi gözetilmedi.
- "anahtar_sozcuk = bilgi" satırları normatif olmayan ama tehdit modelini doğrudan etkileyen cümlelerdir (NOTE, gerekçe, varsayım). Baskın anahtar sözcük dağılımı: MUST 129 · bilgi/diğer 124 · SHALL 47 · SHOULD 30 · MUST NOT 25 · MAY 10 · RECOMMENDED 8 · OPTIONAL 8 · REQUIRED 6 · SHALL NOT 3 (`kapsama_tablolari.md` T3).
- Her satır **tek** artefakta bağlandı; birden çok artefaktı ilgilendiren durumlar `not` sütununda yazılı. `kanal` sütunu, o cümlenin artefaktın kanalı hakkında söylediğini sınıflar (genel satırlarda "belirsiz").

### T1. Artefakt × belge grubu (satır sayısı; kaynak `kapsama_tablolari.md`)

| Artefakt | OIDF | IETF-OAuth | IETF-JOSE | IETF-COSE | IETF-PQUIP | IETF-LAMPS | ARF | ETSI | AB-rehber | BCT | Akademik | Toplam |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A01 LOTL | · | · | · | · | 1 | · | · | 5 | 1 | · | · | 7 |
| A02 TL/LoTE | 2 | · | · | · | · | · | 6 | 21 | · | · | · | 29 |
| A03 CA (x5c zinciri) | 3 | · | 4 | 3 | · | 5 | 1 | 1 | · | · | · | 17 |
| A04 ihraççı sertifikası | 4 | 5 | 2 | 2 | · | · | 1 | 1 | · | · | 1 | 16 |
| A05 imzalı ihraççı meta verisi | 19 | · | · | · | · | · | 1 | · | · | · | · | 20 |
| A06 Type Metadata | · | 11 | · | · | · | · | · | · | · | · | · | 11 |
| A07 kimlik bilgisi (SD-JWT VC) | 7 | 18 | 1 | · | · | · | 5 | · | · | · | · | 31 |
| A08 durum listesi belirteci | 4 | 25 | · | · | · | · | 6 | 1 | · | · | · | 36 |
| A09 cüzdan kanıtlaması (WUA: WIA/KA) | 11 | 21 | · | · | · | · | 7 | · | · | · | · | 39 |
| A10 WSCD anahtarı ve KB-JWT | 18 | 9 | · | · | · | · | 4 | · | · | · | · | 31 |
| A11 RP erişim/kayıt sertifikası | 10 | · | · | · | · | · | 14 | 5 | · | · | · | 29 |
| A12 OID4VP istek nesnesi | 35 | · | · | · | · | · | 1 | · | · | · | · | 36 |
| A13 taşıma (TLS/WebPKI) | 5 | 5 | 3 | · | · | · | · | · | · | · | 1 | 14 |
| genel | 11 | 7 | 25 | 5 | 7 | · | · | 4 | 10 | 10 | · | 79 |
| **Toplam** | 129 | 101 | 35 | 10 | 8 | 5 | 46 | 38 | 11 | 10 | 2 | 395 |

Kapsamı zayıf hücreler (bilinçli): A01 LOTL'yi yalnız ETSI tanımlıyor (OIDF'de LOTL yok). A06 Type Metadata yalnız SD-JWT VC'de tanımlı. A13 için ayrı bir TLS spesifikasyonu korpusa alınmadı; yalnız OID4VC/JOSE metinlerinin TLS'e dayandığı yerler var.

## 2. Önemli bulgular

### Bulgu 1 — Algoritma **beklentisini** ("required") taşıyan normatif bir kanal yok

Korpusun hiçbir yerinde "bu varlık **şu** algoritma(lar)la imzalar; başkasını kabul etme" anlamında, kimliği doğrulanmış ve varlık başına bir beklenti alanı **yok**. Mevcut kanallar dört sınıfa ayrılıyor:

| Sınıf | Nerede | Semantik | Satırlar |
|---|---|---|---|
| (i) Yetenek beyanı ("supported/uses") | OID4VCI ihraççı meta verisi; OID4VP cüzdan/doğrulayıcı meta verisi; ABCA ve DPoP AS meta verisi; HAIP §7-8 | "supported"/"uses"; zorlayıcı kural ancak ihraççının **kendi** yayımladığı proof kümesini kendisinin uygulaması (T236) | T079, T081, T142, T226, T285, T389, T390, T188, T381, T125, T126 |
| (ii) Yerel/bant dışı politika | 8725bis §3.1 ("permitted for itself and that issuer"); SD-JWT VC §2.5 ("permitted … according to policy"); ABCA/DPoP "acceptable per local policy"; HAIP §7 "Verifiers are assumed to determine in advance…" | Yükümlülük var, **taşıma kanalı tanımsız** | T328, T046, T048, T184, T378, T123 |
| (iii) Ekosistem düzeyi izin listesi | ARF OIA_03/WUA_04 → ECCG ACM v2; HAIP §7 ES256 asgarisi | Varlık başına değil; ACM v2 ML-DSA'yı yalnız hibrit öneriyor | T133, T202, T122, T134 |
| (iv) Liste üyeliği | TL/LoTE ServiceDigitalIdentity (varlık başına sertifika kümesi) | Birden çok geçerli sertifika (farklı algoritmalı olabilir) = OR; "required/sunset" yok | T008, T018, T017 |

Destekleyici gözlemler:
- Meta veri modeli "required" **ifade edebiliyor**, ama yalnız şifreleme (`encryption_required`, T393) ve anahtar kanıtlaması (`key_attestations_required`, T394) için. İmza algoritması için eşdeğer alan yok.
- Meta veri varsayılan olarak **imzasız** ve yalnız TLS ile korunuyor (T070, T071, T086). İmzalı sürüm ekosistem seçimi (T083, T085); `exp` isteğe bağlı (T076).
- En yakın emsaller korpusta var, ama hiçbiri OpenID4VC'de doğrulayıcıyı bağlamıyor:
  - DNSSEC DS kaydı (üstten kimliği doğrulanmış algoritma sinyali). Buna karşın doğrulayıcılar "any single valid path" uyguluyor (T366, T364, T365).
  - DPoP "nonce downgrade" yasağı: sunucunun verdiği beklenti soyulamaz (T382).
  - JOSE `crit`: beklentiyi nesne içinde zorunlu kılan tek JOSE aracı (T386). Karşıtı, bilinmeyen başlıkların yok sayılması (T385, T387).
  - OID4VP'de "yetkili kaynaktaki veri, istek içindeki `client_metadata`'ya üstün gelir" (T295). M-f için doğal bağlanma noktası.
- **Sonuç (M-e için):** "supported" ile "required" arasındaki fark birincil metinde doğrulandı. HAIP §7 ve OID4VCI meta verisi beklenti değil yetenek taşıyor. Meta veri ise, H1 anlamında, TLS'e dayanan çekilen bir artefakt.

### Bulgu 2 — Artefaktların kanal sınıflandırması (dayanak satırlarıyla)

| Artefakt | Sınıf | Dayanak | Nüans (korpustan) |
|---|---|---|---|
| A01 LOTL | **çekilen**; çıpa **sabitlenmiş** (OJEU) | T001–T003; T004, T005 | İndirme kanalının sertifikası da OJEU'da özetle sabitlenmiş (T002). Taşıma kimlik doğrulaması WebPKI'den bağımsız sabitlemeye dayanabiliyor |
| A02 TL/LoTE | **çekilen** | T008–T025, T027, T028, T030 | LoTE çıpaları OJEU'da (T029). Yayım hem imzalı hem "secure channel" (T027, T028) |
| A03 CA (x5c) | **aktarılan** (ara sertifikalar); çıpa **çekilen** | T038, T040, T043; T063 | Çıpa x5c'de YASAK (T043, T198, T243). Çıpa her zaman TL/LoTE'den gelir |
| A04 ihraççı sertifikası | **aktarılan** (x5c yaprak) | T039, T042, T045 | **Alternatif yol:** JWT VC Issuer Metadata ile anahtar yalnız HTTPS'ten **çekilir**, nesne imzası yok (T309–T311). Kanal ikamesi spesifikasyonda fiilen tanımlı |
| A05 imzalı ihraççı meta verisi | **çekilen** | T070–T087 | İmzasız biçim zorunlu, imzalı isteğe bağlı (T071). Kayıt sertifikası meta verinin içinde değerle taşınıyor (T088) |
| A06 Type Metadata | **çekilen**; özet bağı **aktarılan**; önbellek **sabitlenmiş** | T094, T095; T090; T093 | İmzasız. Bütünlük `vct#integrity` ile kimlik bilgisindeki özetten geliyor. Özet yoksa tek koruma HTTPS |
| A07 kimlik bilgisi | **aktarılan** | T102–T110, T112–T121 | — |
| A08 durum listesi | **çekilen** | T145–T165 | Çevrimdışı kullanımda **aktarılan** olabilir (T166). TSL, taşıma güvenliğine dayanmamayı tasarım ilkesi yapıyor (T157) |
| A09 WUA (WIA/KA) | **aktarılan** | T181–T208 | AS algoritma desteği çekilen meta veride (T188) |
| A10 WSCD anahtarı/KB-JWT | **aktarılan** | T209–T214, T216–T236 | Cihaz açık anahtarı kimlik bilgisinin `cnf` alanında, her sunumda açıkta (T218, T220). c_nonce çekilen (T237) |
| A11 RP erişim/kayıt sertifikası | **aktarılan** (değerle) | T240–T247, T249–T252 | Çıpa LoTE'den çekilen (T245). İptal CRL/OCSP ile çekilen (T255). Çevrimdışı CRL önbelleği sabitlenmiş (T256) |
| A12 istek nesnesi | **aktarılan** | T268–T274, T276–T281, T283 | Yönlendirmeli akışta `request_uri`'den **çekilir** (T284). Ama kaynak doğrulanacak RP'nin kendisi, yetkili üçüncü taraf değil. Bu yüzden H1 anlamında "çekilen" sayılmamalı |
| A13 TLS/WebPKI | sunucu sertifikası **aktarılan**, kök deposu **sabitlenmiş** | T302–T305; T313 | x5u, jku ve meta veri gibi çekilen artefaktların taşıyıcısı (T306, T309, T312) |

Tam satır listesi için `kapsama_tablolari.md` T2 ve T2b'ye bakın.

### Bulgu 3 — Geçerlilik/kabul pencereleri ve önbellek kuralları

**Sayısal bir üst sınır yalnız iki yerde tanımlı:** TL/LoTE için ≤ 6 ay ve WIA için < 24 saat. Kalan pencerelerin hepsi "acceptable window", "local policy" ya da isteğe bağlı `exp`.

| Artefakt | Pencere / önbellek kuralı | Satırlar |
|---|---|---|
| LOTL, TL | Next update − issue ≤ **6 ay**. Next update geçmişse liste atılır. Önbellekte daha erken yayım olabileceği hesaba katılır; "regularly" kontrol edilir | T010, T009, T003, T011, T012 |
| LoTE | EUDI profillerinde ≤ **6 ay**; genel profilde profile bırakılmış; geçmişse atılır | T021, T020, T019 |
| İmzalı ihraççı meta verisi | `iat` REQUIRED, `exp` OPTIONAL → **tanımsız** | T075, T076 |
| Type Metadata | Özet varsa **süresiz** önbellek; yoksa HTTP önbellek modeli (max-age) | T093, T094, T101 |
| Kimlik bilgisi | `exp`/`nbf` OPTIONAL. HAIP süre sınırlamayı önerir (sayı yok). ARF'de ≤ **24 sa** kısa ömürlü seçenek var (durum listesi gerekmez). Zaman denetimi doğrulayıcıda; cüzdan süresi dolmuşu sunabilir. Saat kayması payı "birkaç dakika" | T117, T118, T116, T175, T143, T144, T391, T392 |
| Durum listesi | `exp` RECOMMENDED, `ttl` RECOMMENDED. `exp`/`ttl` HTTP başlıklarına üstün gelir. `iat` yerel politikaya bağlı. Sınırlar kullanım durumuna bırakılmış; sonuçta RP karar verir | T149, T148, T150, T151, T153, T162, T163, T164 |
| WUA (WIA/KA) | WIA < **24 sa**; iptal bakım süresi ayrı ve uzun. KA `exp` (jwt proof ile zorunlu). ABCA'da tazelik "local policy" | T204, T205, T207, T200, T186, T187, T182 |
| KB-JWT | `iat` "acceptable window" (**tanımsız**). `nonce` istek başına taze. DC API'de `aud` = origin | T212, T210, T211, T222, T224, T225, T227 |
| DPoP / key proof | "acceptable window" (tanımsız). Nonce verildiyse nonce'suz kanıt reddedilir. c_nonce önbelleğe alınmaz; ömrünü ihraççı belirler | T380, T382, T234, T237, T238 |
| RP erişim sertifikası | 24 saatten uzun geçerliyse iptal edilebilir olmalı. Kısa ömürlü sertifika uygulanmaz. İptal CRL/OCSP ile; çevrimdışı CRL önbelleği | T249, T261, T255, T256 |
| RP kayıt sertifikası | 24 saatten uzunsa iptal edilebilir. Doğrulama zorunluluğu yönetmelikten **24 ay sonra** başlıyor | T250, T254, T089, T253 |
| Verifier Attestation JWT | `exp` REQUIRED; süresi geçmişse ret | T265 |

**Model için sonuç:** H2'nin "kabul penceresi" parametresi spesifikasyondan ancak TL/LoTE (≤6 ay), WIA (<24 sa) ve ARF'nin ≤24 sa kısa ömürlü kimlik bilgisi seçeneği için sayı olarak alınabilir. KB-JWT, DPoP, durum listesi ve meta veri pencereleri **parametrik** kalmak zorunda; değer aralıkları ön kayıtta gerekçelendirilmeli.

### Bulgu 4 — Çoklu imza ve OID4VP A.3.2.2: fiilî semantik "biri yeter"

- **A.3.2.2** yalnız sözdizimini tanımlıyor: imza başına korumalı başlıkta `client_id`, `verifier_info` ve önek parametreleri; diğer her şey yükte (T271, T272). **Cüzdanın hangi ya da kaç imzayı doğrulayacağı tanımsız** (T273).
- Her imza farklı bir güven çerçevesi için (T269, T270). Cüzdan ancak kendi çerçevesinin imzasını doğrulayabilir; semantik yapısı gereği **OR**. Güvenliği, cüzdanın kabul ettiği **en zayıf** çerçeve belirler (M-b hipotezi metinle uyumlu).
- Boşluğu dolduran genel kural RFC 7515 §5.2: hangi imzaların geçerli olması gerektiği "uygulama kararı", asgari "en az biri" (T314, T315, T317).
- DC API'de imza doğrulamasının kendisi bile cüzdan takdirinde (T268). HAIP cüzdanı **imzasız, imzalı ve çoklu imzalı** isteklerin üçünü de desteklemeye zorluyor (T281). RP başına beklenti yoksa imzalı→imzasız düşürme de açık.
- Diğer çoklu imza bağlamları:
  - SD-JWT General JSON: ifşalar ve KB-JWT ilk imzada; doğrulama semantiği tanımsız (T108, T109).
  - COSE_Sign: "bir imza genellikle yeter" (T340, T341).
  - DNSSEC: "any single valid path" (T364).
  - Buna karşılık AND semantiğini yalnız şu kaynaklar tanımlıyor: composite (tek `alg` içinde, T345), ECCG ACM v2 (T135) ve ETSI TS 119 312 V2.1.1 §6.4.1 (T356). Bunlar da soyulmuş bir belgenin reddini ancak **beklenti bilgisiyle** sağlayabiliyor (RFC 9955 karşılıklı dışlama: T349, T350).

### Bulgu 5 — Belirsiz, eksik ya da çelişkili maddeler

1. **HAIP 1.0'da çapraz atıf hataları.**
   - İmzalı meta veri için "Section 11.2.3 in [OIDF.OID4VCI]" yazıyor; OID4VCI 1.0'da doğru bölüm §12.2.3 (T083).
   - "jwt proof type as specified in Appendix E" yazıyor; doğrusu Ek F.1, çünkü Ek E Wallet Attestation (T395).
   - "section 3.5 of [SD-JWT VC]" -13'e göre doğru, güncel -19'da §2.5 (T042).
   - "The X.509 certificate signing the request MUST NOT be self-signed" cümlesi kimlik bilgisi ve durum listesi bağlamlarına da kopyalanmış (T044).
2. **Sürüm parçalanması.**
   - SD-JWT VC: OID4VP -09'u, OID4VCI -11'i, HAIP -13'ü sabitliyor; güncel sürüm -19 (T131, T132, T130, T129).
   - TSL: OID4VCI -12'yi, HAIP -14'ü sabitliyor; güncel sürüm -21 ve RFC Editör kuyruğunda.
   - HAIP'e uyumlu bir uygulama -13 ve -14'ü kullanmalı.
3. **Senaryo (d) (General JSON çoklu imza) "spesifikasyon dışı" değil, "belirsiz".**
   - -13'te JSON serileştirme isteğe bağlı biçim (T114); HAIP "MAY" diyor (T115).
   - -19'da kapsam dışı ama yasak değil (T113).
   - OID4VCI A.3.4 kimlik bilgisini "string" olarak istiyor (T120).
   - Karar belgesi §7.5(d)'deki etiket düzeltilmeli.
4. **TL imzası.**
   - TS 119 612 V2.4.1 tek zarflanmış `ds:Signature` varsayıyor (T016); algoritma listesinde PQ yok (T017).
   - TS 119 312 V2.1.1 (2026-06) ise "XAdES çoklu imza"yı protokol düzeyi hibrit olarak kabul ediyor (T035) ve hibrit kabulünde **iki imzanın da** geçerli olmasını istiyor (T356).
   - İkinci bir (PQ) imzanın TL'de nasıl işleneceği tanımsız.
5. **LoTE ve PQ JOSE.**
   - EUDI LoTE profilleri **compact JAdES** ile imzalanıyor. Compact serileştirme tek imza taşıdığı için hibrit ancak tek bir composite `alg` ile mümkün (T023–T025).
   - JOSE composite yalnız taslak (-04).
   - ARF, ACM v2'yi zorunlu kılıyor (T133). ACM v2 saf ML-DSA'yı "shouldn't" diye niteliyor (T134). RFC 9964 ise saf ML-DSA tanımlıyor.
   - Bugün **final bir standartla ARF-uyumlu PQ JOSE imzası yok** (çıkarım; normatif metin değil).
6. **RP kimlik doğrulamasında çelişki adayı.**
   - ARF RPA_01a, RP kimlik doğrulamasının tarayıcı ya da işletim sistemine bırakılamayacağını söylüyor (T248).
   - HAIP ise imzasız DC API isteklerinin origin ve WebPKI'ye dayandığını not ediyor ve cüzdana imzasız isteği de kabul ettiriyor (T282, T281).
   - OID4VP DC API'de imza doğrulamasını cüzdan takdirine bırakıyor (T268).
7. **Fail-open seçenekleri.**
   - RP kimlik doğrulaması başarısız olduğunda kullanıcıya "yine de sun" seçeneği verilebiliyor (T247).
   - Kayıt sertifikası başarısızsa devam kararı cüzdan sağlayıcıda (T253).
   - `verifier_info` cüzdan takdirinde (T264).
   - Doğrulayıcı için iptal denetimi (T178) ve cihaz bağı doğrulaması (T228) "önerilir, zorunlu değil".
   - Sonuç: G2, G3 ve G4 ekosistem metninde **politikaya bağlı**; tehdit modeli bunları "doğrulayıcı politikayı uygular" varsayımıyla yazmalı.
8. **Kanal ikamesiyle gerilim.**
   - TSL, taşıma güvenliğine ya da WebPKI'ye dayanmamayı tasarım ilkesi yapıyor (T157).
   - RFC 8725 §3.2 TLS'in JWT imzasının yerini tutabileceğini söylüyordu (T307). 8725bis-10 bu cümleyi **kaldırmış**; yalnız "none, başka yolla korunuyorsa" kalmış (T308).
   - Buna karşın SD-JWT VC'nin JWT VC Issuer Metadata yolu anahtarı yalnız HTTPS ile doğruluyor (T309). HAIP de imzasız meta veriyi varsayılan kabul ediyor (T083, T086).
   - H1 bir "tasarım önerisi" değil, **fiilen var olan** ve standartlar arasında çelişkili ele alınan bir durum olarak çerçevelenmeli.
9. **Durum listesi delegasyonu.** ARF'de durum listesi çıpası ihraççıdan farklı olabilir (T180). TSL ise aynı CA ve EKU'yu yalnız "should" düzeyinde öneriyor (T159–T161). Delegasyon zinciri ekosistemde tanımsız; H4 aday hücresi için metin dayanağı bu.
10. **Tanımsız pencereler.** KB-JWT (T212), DPoP (T380), ABCA (T186), durum listesi (T162), meta veri `exp` (T076), kimlik bilgisi `exp` (T118).
11. **ARF v3.0.0 terminolojisi.** Ana metinde WUA yerini Key Attestation (KA) ve Wallet Instance Attestation'a (WIA) bırakmış (T204–T207). Ek 2.02'deki gereksinim kimlikleri hâlâ "WUA_xx" (T202, T208). Karar belgesindeki A09 artefaktı ikiye ayrılmalı (bkz. `01-korpus/BULGULAR-VE-PLAN-ETKISI.md`).
12. **Bilinen-cevap testleri.**
    - RFC 7583 algoritma geçişini **kapsamıyor** (T373).
    - DNSSEC algoritma geçişi için dayanak RFC 6781 §4.1.4 (T369–T372) ve RFC 6840 §5.11–5.12 (T364–T368).

## 3. Sınırlılıklar

- Satır seçimi ve `artefakt`/`kanal`/`kategori`/`hedef` atamaları tek çalışmanın yorumudur. İkinci bir bağımsız kodlama (N-sürüm) yapılmadı. Adım 2'de örneklem üzerinde tutarlılık denetimi önerilir.
- 4 alıntı yalnız satır sonu tire birleştirmesiyle (D2) eşleşiyor: IETF metnindeki "end-\n entity" ve "SD-\n JWT" gibi bölünmeler.
- mdoc (ISO/IEC 18013-5) kapsam dışı; ücretli olduğu için korpusta yok.
- ETSI TS 119 182-1 (JAdES) korpusta yok: TS 119 602 ve TS 119 475 ona atıf yapıyor.
- ETSI TS 119 472-2/-3 (OID4VC profilleri) korpusta yok: ARF bunlara atıf yapıyor.
- Önerilen ek belgeler: `01-korpus/KARAR-NOTLARI.md`.
