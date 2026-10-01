# Adım 1 bulguları ve plan etkisi

> **Tarih:** 24.09.2026 · **Hazırlayan:** korpus çalışması · **Amaç:** "Adım 1 sonu gözden geçirme"ye girdi.
>
> **Dayanaklar:**
> - `MANIFEST.csv` (51 dosya; `korpus_dogrula.py` → 51/51 OK)
> - `traceability/izlenebilirlik.csv` (400 satır; 400/400 alıntı doğrulandı)
> - `terim_sayimi.txt`, `korpus_on_karsilastirma.txt`
>
> `Txxx` = matris satırı. Etiketler: **[olgu]** birincil metinden · **[Ç]** çalışmanın çıkarımı, Adım 2'de sınanmalı.
>
> **Gizlilik:** Bütün sorgular anonimdi; e-posta ya da kişisel veri hiçbir yere gönderilmedi.

---

## 1. 23.09.2026'dan sonraki yeni sürümler ve olaylar

**23.09.2026 akşamı (Sürüm 3'ün tamamlanmasından sonra) ile 24.09.2026 arasında yeni bir spesifikasyon sürümü ya da kapan bir çalışma yok.** Kontrol listesi:

| Kaynak | Kontrol (anonim) | Sonuç |
|---|---|---|
| IETF datatracker (6 taslak) | Revizyon + geçmiş sayfası | Yeni revizyon yok. Tek olay: `draft-ietf-lamps-pq-composite-sigs-19` RPC durumu 23.09.2026'da "Awaiting Second editor" oldu (RFC Editör kuyruğunda ilerliyor) [olgu] |
| OIDF GitHub | OpenID4VP #791, HAIP #381, connect #2153 | Son yorumlar 12.09 (#791), 26.08 (#381) ve 28.08 (#2153). Sürüm 3'ten sonra yeni yorum yok [olgu] |
| openid.net | `-1_0.html` (errata URL'si) ile `-final.html` karşılaştırıldı | OID4VCI ve HAIP bayt-özdeş. OID4VP yalnız bir kaynakça girdisinde farklı ([OIDF.OID4VCI] draft 16 ↔ 15); normatif metin aynı. Errata sürümü yok [olgu] |
| ETSI deliver | TS 119 612 / 602 / 475 / 411-8 / 312 klasörleri; TR 119 330-4 | En yeni sürümler MANIFEST'te. TR 119 330-4 `deliver`'da yok (yayımlanmamış) [olgu] |
| arXiv (anonim API) | "post-quantum credential", "OpenID4VP", "SD-JWT", "EUDI quantum" | Kapan çalışma yok. Teğet komşu: arXiv:2609.04566 (03/07.09.2026), güven alanı bölümleme + PQ kimlik doğrulama maliyeti optimizasyonu. §6.5 komşu matrisine "yöntem komşusu" olarak eklenebilir [olgu + Ç] |

**Sürüm 3'te yer almayan, 23.09'dan önce yayımlanmış ve plana etkisi olan olgular:**

1. **ETSI TS 119 312 V2.1.1 (2026-06), "Cryptographic Suites"** [olgu, T035, T356–T359, T036, T037]:
   - PQC'yi normatif olarak içeriyor: ML-DSA-44/65/87, SLH-DSA, LMS/XMSS. HashML-DSA yasak.
   - §6.4.1: "Acceptance requires both signatures to be valid" (AND).
   - §6.4.2: protokol düzeyi hibrit, "multi-signature constructions in XAdES" dahil.
   - RSA<3000 bit ile yeni sertifika 31.12.2026'dan sonra yasak; eski sertifikalar en geç 31.12.2028'de biter.
   - Göç takvimi "under development" bir belgeye bırakılmış.
   - TL imzaları doğrudan bu belgeye bağlı (TS 119 612 §5.7.1, T014). Denetçi C'nin "hiçbiri henüz normatif metin üretmedi" hükmü güven hizmetleri kripto katmanı için **artık doğru değil**. Beklenti taşıma ve birlikte yaşama için ise hâlâ doğru (§2.b).
2. **SD-JWT VC -19 IETF Last Call'ı 15.09.2026'da tamamlandı** [olgu, datatracker]: SECDIR "Has Issues", ARTART "Ready with Issues". IESG durumu "Waiting for AD Go-Ahead"; IANA "Not OK" (11.09). Bir -20 revizyonu olası [Ç]. Sürüm sabitleme duyarlılığı gerekiyor.
3. **ETSI EUDI profilleri** (Sürüm 3'te adı geçmiyor) [olgu]:
   - TS 119 602 V1.1.1 (2025-11): LoTE; EUDI profilleri compact JAdES, ≤ 6 ay (T021–T025).
   - TS 119 475 V1.2.1 (2026-03): WRPRC; JAdES B-B, `x5c` (T257–T260).
   - TS 119 411-8 V1.1.1 (2025-10): WRPAC; kısa ömürlü değil (T261).
4. **AB PQC yol haritası SSS (NIS CG, 15.04.2026):** hibrit imza rehberliği yol haritası kapsamı dışında (T362, T363) [olgu]. Boşluk argümanını güçlendiriyor.
5. **RFC 9864 (Ekim 2025):** RFC 7518 ve 9053'ü güncelliyor; OID4VP meta verisi "fully-specified" algoritma kimliklerine dayanıyor (T142, T226, T331, T334) [olgu].

---

## 2. Sürüm 3 varsayımlarını doğrulayan ve onlarla çelişen bulgular

### 2.a Doğrulananlar (birincil metin + betik)

| Sürüm 3 iddiası | Sonuç | Dayanak |
|---|---|---|
| HAIP ve ARF v3.0.0'da "quantum" 0 kez | ✓ | `terim_sayimi.txt`: HAIP 0; ARF (13 dosya) 0; OID4VCI/OID4VP 0; ARF'deki 8 "hybrid" yalnız CTAP taşıması; SD-JWT VC'deki tek "quantum" örnek veride ("Quantum Mechanics") |
| 8725bis-10: 21.08.2026; §3.1 "permitted for itself and that issuer"; PQ/hibrit geçmiyor | ✓ | T327–T329; terim sayımı 0; datatracker: RFC Ed Queue, Blocked (25.08) |
| composite -04 §6.2 (`x5c` composite imzalı) | ✓ | T055, T056, T057 |
| RFC 9955 karşılıklı dışlama ve soyma | ✓ | T348–T353 |
| RFC 6840 §5.11 "any single valid path" | ✓ | T364, T365 |
| ECCG ACM v2 Note 50/51, AND; v3 taslağında 52/53 | ✓ | T134–T136, T138 |
| HAIP "MUST support DPoP" (ihraç tarafı) | ✓ | T374 |
| client-attestation -11 §10.5 (8 kB) | ✓ | T192; WGLC 08.09.2026 |
| OID4VCI A.3.4 "MUST NOT be re-encoded" | ✓ | T121 |
| TSL -21 ve LAMPS composite -19 RFC Editör kuyruğunda | ✓ | MANIFEST notları (datatracker, 23.09.2026) |
| SD-JWT VC -19 tarihi 31.08.2026 | ✓ | Belge başlığı |
| OID4VP #791 "1.2 or later"; HAIP #381 "1.2" | ✓ | GitHub API (24.09.2026) |
| LOTL anlık görüntüsü | ✓ | `data/` SHA-256 eşleşiyor; seq 394, yayım 2026-09-10, NextUpdate 2027-03-10 (181 gün), `rsa-sha512`, 43 işaretçi |
| Ön korpus kopyaları taze indirmeyle aynı | ✓ | `korpus_on_karsilastirma.txt`: 3 `.txt` bayt-eşit; 3 PDF metni taze PDF'ten bayt/metin-özdeş yeniden üretiliyor |

### 2.b Düzeltme gerektiren ya da çelişen bulgular

1. **S0 tabanı ("bütün halkalar ES256/P-256, HAIP 1.0") normatif olarak kısmen doğru.** [olgu: T122, T170, T196, T221, T395–T398, T123]
   - HAIP §7 ES256'yı yalnız şu doğrulamalar için asgari kılıyor: WUA/KA/jwt proof (ihraççı), KB-JWT ve durum bilgisi (doğrulayıcı), imzalı istek ve meta veri (cüzdan).
   - **İhraççının kimlik bilgisi imzası, `x5c` zincirleri ve TL/LoTE listede yok.** Bunlar için "Verifiers are assumed to determine in advance the cryptographic suites supported by the Ecosystem."
   - Öneri: S0 = "HAIP asgarisi + ekosistemin bant dışı seçtiği klasik süitler". Bu bant dışılık, M-d'nin normatif dayanağı olarak da kullanılabilir.
2. **Senaryo (d) "spesifikasyon dışı" etiketi yanlış genelleme.** [olgu: T113–T115, T120]
   - HAIP 1.0, SD-JWT VC **-13**'ü sabitliyor. -13'te JWS JSON serileştirmesi (dolayısıyla General JSON çoklu ihraççı imzası) **OPTIONAL** biçim; HAIP §6.1 "JSON serialization MAY be supported".
   - -19'da ise "kapsam dışı ama yasak değil".
   - OID4VCI A.3.4 kimlik bilgisini "string" olarak istiyor.
   - Öneri: §7.5(d) şöyle yazılsın: "HAIP 1.0 profilinde isteğe bağlı (MAY), SD-JWT VC -19'da kapsam dışı, OID4VCI teslim biçimiyle belirsiz". Bu, (d)'yi stres yapılandırmasından **spesifikasyonun izin verdiği** bir yapılandırmaya taşır. H3/H6 için değeri artar.
3. **A09 "cüzdan kanıtlaması (WUA)" artık tek nesne değil.** [olgu: T204–T208, T399, T400]
   - ARF v3.0.0 ana metni Key Attestation (KA) ve Wallet Instance Attestation (WIA) ayrımı yapıyor. WIA < 24 sa; KA uzun ömürlü ve iptal bakım süreli. İkisi de **yalnız ihraççıya** sunuluyor, RP'ye değil. Ek 2.02'deki gereksinim kimlikleri ise hâlâ "WUA_xx".
   - Sonuç: sunum yolunda (G2/G4) WUA artefaktı yok. WUA yalnız ihraçta cihaz anahtarını bağlıyor.
   - Öneri: ASP'de A09a WIA ve A09b KA ayrı düğümler, ayrı pencereler.
4. **H1 "kanal ikamesi" bir öneri değil, spesifikasyonlarda fiilen var ve tutarsız ele alınıyor.** [olgu: T309–T311, T071, T083, T086, T282, T002, T157, T307, T308]
   - Fiilen var olan örnekler:
     - JWT VC Issuer Metadata: ihraççı anahtarı yalnız HTTPS ile;
     - imzasız ihraççı meta verisi varsayılan;
     - imzasız DC API isteği: origin ve WebPKI;
     - LOTL indirme kanalı: OJEU özetiyle sabitlenmiş.
   - Karşı taraf: TSL durum listesini taşımadan bağımsız tasarlıyor. 8725bis-10, RFC 8725'teki "TLS yeterli olabilir" cümlesini kaldırmış.
   - Öneri: H1'in anlatısı "hangi koşulda ikame edilebilir" sorusundan "spesifikasyonlar bu ikameyi zaten yapıyor; hangi hücrelerde güvenli" sorusuna kaysın. Yanlışlanma koşulu değişmez.
5. **ETSI hakkındaki güncellik hükmü güncellenmeli** (bkz. §1, madde 1).
   - TS 119 312 V2.1.1 normatif PQ ve AND-hibrit getiriyor. Beklenti taşıma, sunset ve birlikte yaşamayı ise tanımlamıyor.
   - Boşluk tanımı şöyle daraltılmalı: "algoritma kataloğu var, **beklenti/geçiş semantiği** yok".
   - TS 119 612'nin tek `ds:Signature` kuralı (T016) ile TS 119 312'nin "XAdES çoklu imza" hibriti (T035) arasındaki tanımsızlık, M-f/sunset önerisi için somut bir TS 119 612 değişiklik noktası.
6. **EUDI'de final bir PQ JOSE yolu yok.** [olgu + Ç: T133, T134, T023–T025, T345]
   - ARF OIA_03/WUA_04 ACM v2'yi zorunlu kılıyor. ACM v2 saf ML-DSA'yı "shouldn't" diye niteliyor. RFC 9964 saf ML-DSA. JOSE composite taslak (-04). EUDI LoTE'leri compact JAdES, yani tek imza.
   - Sonuç: senaryo (a) (composite `alg`) EUDI için neredeyse **tek** uyumlu yol. (b) (ikili ihraç) ise kimlik bilgisi düzeyinde tek imzayla yapılabiliyor.
   - Öneri: C3 kontrol–tedavi tasarımında "tedavi = composite -04" ana kol, "saf ML-DSA" ikincil kol olsun.
7. **Bilinen-cevap testi dayanağı: RFC 7583 algoritma geçişini kapsamıyor.** [olgu: T373]
   - Doğru dayanak: RFC 6781 §4.1.4 (ekleme ve kaldırma sırası, TTL beklemesi: T369–T372) ile RFC 6840 §5.11–5.12 (T364–T368).
   - Karar §7.9'daki "RFC 6781 ve/veya RFC 7583" ifadesi "RFC 6781 §4.1.4 + RFC 6840 §5.11" olarak netleşmeli.
8. **Pencerelerin çoğu tanımsız.** [olgu: OZET Bulgu 3]
   - Sayısal sınır yalnız TL/LoTE (≤ 6 ay), WIA (< 24 sa) ve ARF'nin ≤ 24 sa kısa ömürlü kimlik bilgisi seçeneği için var.
   - KB-JWT, DPoP, durum listesi, meta veri ve kimlik bilgisi `exp` pencereleri "acceptable/local policy".
   - Saat kayması payı "birkaç dakika" (T392): hızlı τ rejimiyle aynı ölçek.
   - H2'nin "spesifikasyon pencereleri" iddiası yalnız bu üç sayıya dayanabilir; gerisi ön kayıtta gerekçelendirilmiş parametre aralığı olmalı.
9. **G2–G4 ekosistem metninde politikaya bağlı.** [olgu: T178, T228, T247, T253, T264, T254]
   - RP için iptal ve cihaz bağı denetimi "önerilir, zorunlu değil".
   - RP kimlik doğrulaması başarısızken kullanıcıya "yine de sun" seçeneği var.
   - Kayıt sertifikası doğrulaması 24 ay ertelenmiş.
   - Sürüm 3'ün "doğrulayıcı sınanan politika dışında doğru çalışır" varsayımı korunabilir, ama **politika parametreleri** açıkça sayılmalı.
10. **DC API akışında G2'nin yeniden oynatma koruması da WebPKI'ye bağlı.** [olgu + Ç: T227, T280]
    - `aud` = origin ve `expected_origins`, platformun WebPKI ile doğruladığı origin'e dayanıyor.
    - H1'deki WebPKI bağımlılığı yalnız çekilen artefaktlarla sınırlı değil; DC API'de sunum bağlamına da uzanıyor. Tamarin R3'te ayrı bir kural adayı.

---

## 3. Sonraki adımlara somut etkiler ve öneriler

### 3.1 ASP modeli (artefakt, kenar, kanal, pencere)

- **Artefakt kümesi:** 13 artefakt korunur; A09 ikiye ayrılır (A09a WIA, A09b KA). 13 dışı üç **kenar-artefakt** eklenir:
  - Access CA CRL/OCSP (T255, T256);
  - JWT VC Issuer Metadata / JWK Set (T309);
  - ihraççının OAuth AS meta verisi (T188, T381).
- **Kanal sınıfları:** aktarılan / çekilen / sabitlenmiş'e iki etiket eklenir:
  - `sunan-ucundan-cekilen`: A12 `request_uri` (T284);
  - `yalniz-tasima`: nesne imzası olmayan çekilen yollar (T309, T071, T282, özetsiz Type Metadata).

  H1'in biçimsel sınaması bu iki etiketi ayırt etmeli.
- **Kenarlar:** `threat-model/guven-bagimliligi.dot` doğrudan ASP olgu listesine çevrilebilir (28 kenar).
  - Durum listesi delegasyonu (EKU) ayrı ve isteğe bağlı kenar (T159–T161, T180).
  - "Birden çok geçerli TL imzacısı" OR kenarı (T008, T018).
- **Pencereler:**
  - Sabit: TL/LoTE ≤ 6 ay (LOTL örneği 181 gün); WIA < 24 sa; kimlik bilgisi ≤ 24 sa seçeneği.
  - Parametrik: KB-JWT `iat` penceresi, DPoP penceresi, durum listesi `exp`/`ttl`, meta veri `exp`, kimlik bilgisi `exp`, saat payı (dakikalar).
  - Önerilen tarama aralıkları ön kayıtta yazılmalı [Ç].
- **Politika parametreleri:** P0–P4'e ek olarak `iptal_denetimi ∈ {var, yok}`, `cihaz_bagi ∈ {var, yok}`, `rp_auth_fail_open ∈ {var, yok}`, `wrprc_dogrulama ∈ {faz0, faz1}`, `sdjwtvc_surum ∈ {-13, -19}`.

### 3.2 Tamarin kural şemaları R1–R7

| Kural | Korpustan somut içerik | Öneri |
|---|---|---|
| R1 zincir | OJEU → LOTL → TL/LoTE → CA → ihraççı → kimlik bilgisi; çıpa `x5c`'de yok (T043); LoTE compact JAdES tek imza (T023) | LoTE düğümünde çoklu imza modellenmesin; yalnız composite `alg` |
| R2 downgrade | JWS JSON "uygulama kararı / en az biri" (T314, T315); DC API'de imza doğrulaması takdirde (T268); cüzdan imzasızı da kabul eder (T281); bilinmeyen parametre yok sayılır (T385, T387); karşı önlem `crit` (T386) | R2'ye "imzasızlaştırma" (M-b0) ve "bilinmeyen başlığın yok sayılması" alt kuralları eklensin |
| R3 kanal | `yalniz-tasima` yolları (T309, T071, T282) ile "nesne imzası + kanal" (TLPub_03/05: T027, T028) ve "yalnız nesne" (TSL T157) karşıtlığı; DC API origin (T227, T280) | R3'ü üç kanal türüyle parametrele; G2 için origin bağımlılığını ekle |
| R4 WSCD | `cnf` her sunumda açık (T218, T220); tek kullanımlık yalnız cüzdanda, geri düşüşlü (T230, T231); doğrulayıcı zaman denetimi yapar (T143) | H5 izi için doğrulayıcı tarafında "tek kullanımlık zorlanmaz" olgusunu sabit al |
| R5 çıpa | OJEU sabitleme (T001, T029); kanal sertifikası da OJEU'da (T002); birden çok TL imzacısı = OR (T008, T018) | "Çıpa sabitlenmiş ama liste klasik imzalı" hücresi H4 için aday |
| R6 zaman penceresi | §3.1'deki pencereler; `exp` sonrası ret (T391); saat payı (T392) | τ_hızlı ≈ saat payı sınırını ızgaraya koy |
| R7 tekdüze beklenti | Emsaller: iptal geri alınamaz (VCR_04, T176); DPoP nonce downgrade yasağı (T382); DNSSEC'te "önce DS'yi kaldır" (T371) | M-f taşıyıcı adayları: TL/LoTE hizmet uzantısı (TS 119 612/602), WRPRC alanı (TS 119 475), OpenID Federation meta verisi ("authoritative data takes precedence", T295) |

### 3.3 Mekanizma sınıfları M-a…M-f

- **M-a** (kimliği doğrulanmamış yetenek). Sınıfa aynı semantikteki normatif örnekler eklenir:
  - meta veri `Accept` başlığı (T072);
  - `wallet_metadata` / `request_object_signing_alg_values_supported` (T285);
  - AS meta verisi alg listeleri (T188, T381);
  - `client_metadata.vp_formats_supported` (T390).
- **M-b** (çoklu imza, biri yeter): metin semantiği tanımlamıyor (T273); fiilen OR. **Yeni taban M-b0 önerilir:** "imzasızlaştırma". HAIP cüzdanı imzasız isteği desteklemeye zorluyor (T281); DC API'de imza doğrulaması takdirde (T268). M-b0, M-b'den daha zayıf ve daha yaygın bir düşürme yolu olabilir [Ç].
- **M-c** (çoklu istek): istemci düzeyinde benzeri ABCA'da var: "client MAY try … different algorithms" (T189).
- **M-d** (bant dışı): normatif dayanağı HAIP §7 "Verifiers are assumed to determine in advance…" (T123) ve 8725bis §3.1 (T328).
- **M-e** (meta veri, "supported"): doğrulandı (T079, T125). Meta veri modelinin "required" ifade edebildiği gösterildi: `encryption_required`, `key_attestations_required` (T393, T394). Bir **M-e′** alt varyantı ("meta veriye `*_alg_values_required` eklenirse") ablasyon olarak modellenebilir; meta veri çekilen ve TLS'e bağlı olduğu için H1 ile etkileşir [Ç].
- **M-f** (önerilen): taşıyıcı seçimini korpus kısıtlıyor.
  - LoTE compact JAdES, tek imza (T023–T025). LoTE ancak kendisi composite imzalıysa PQ beklenti taşıyabilir.
  - WRPRC doğrulaması 24 ay ertelenmiş (T254). Erken fazda WRPRC taşıyıcısına güvenilemez.
  - OpenID Federation önceliği (T295) üçüncü aday.
  - Öneri: M-f'nin ilk taşıyıcısı TL/LoTE hizmet uzantısı olsun, WRPRC ikincil olsun; ablasyonda "taşıyıcı" bir bileşen olarak ayrıca raporlansın.

### 3.4 C3 oracle maddeleri

Oracle'ın maddeye bağlanabileceği birincil cümleler:

| Yetenek basamağı | Madde (satır) |
|---|---|
| L1 genel izin listesi | RFC 8725 §3.1 (T323); 8725bis §3.1 ilk cümle (T327) |
| L2 çağrı başına izin listesi | RFC 7515 §5.2 son paragraf (T316); RFC 9901 §7.1-2a ve §7.3-5b (T103, T213) |
| L3 anahtar/ihraççı başına bağlama | 8725bis §3.1 "permitted for itself and that issuer" (T328); alg ↔ `kid` tutarlılığı (T329); tek anahtar tek alg (T324, T335); PQ anahtarlarda `alg` zorunlu (T337) |
| L4 gerekli algoritma kümesi | Doğrudan normatif madde **yok**. Yakın dayanaklar: composite AND (T345), TS 119 312 §6.4.1 AND (T356), ACM v2 AND (T135) + beklenti (G5: T048, T215) |
| Bayrak: bilinmeyen alg/başlık | RFC 7515 §4 bilinmeyen başlık yok sayılır (T385); `crit` (T386) |
| Bayrak: karışık/korumasız `x5c` | RFC 7515 §6 (T040); COSE korumasız kova (T060); composite geriye uyumsuz (T053) |
| Bayrak: MAC kabulü | TSL (T145), ABCA (T183) |

Öneri: L4 için "normatif madde yok" olgusu ön kayıtta açıkça yazılsın. L4 oracle'ı "8725bis §3.1 + composite AND + G5 tanımı" birleşiminden türetilir. N-sürüm oracle bu türetmeyi bağımsız yapmalı.

### 3.5 Hipotezler H1–H6

- **H1:** Anlatı "fiilen var olan ikame" olarak güncellenmeli (§2.b-4). Yanlışlanma koşulu aynen kalabilir. DC API origin bağımlılığı (G2) ek alt hücre olur.
- **H2:** Sabit pencereler üç sayıya dayanır; geri kalanı parametrik. "Saat payı ≈ τ_hızlı" sınırı ızgaraya eklensin.
- **H3:** M-b0 eklenmeli. M-f bileşen ablasyonuna "taşıyıcı" boyutu eklenmeli (§3.3).
- **H4:** Aday hücreler korpusla somutlaştı.
  - Durum listesi delegasyonu: farklı çıpa, EKU yalnız "should" (T159–T161, T180).
  - A.3.2.2: semantik tanımsız (T273).
  - WebPKI: JWT VC Issuer Metadata, imzasız istek (T309, T282).
- **H5:** Tek kullanımlık cüzdanda zorlanıyor ve geri düşüyor (T230, T231); doğrulayıcı zorlamıyor (T143, T144).
  - Ek gözlem [Ç]: kısa ömür, uzun ömürlü ihraççı anahtarı çıkarıldığında G1'i korumaz. Tehdit modeli §8'deki dipnot bu nedenle eklendi.
- **H6:** Oracle dayanakları §3.4'te. Sürüm sabitleme (-13/-19) C3 dahil etme ölçütlerine yazılmalı.

### 3.6 Korpusa eklenmesi önerilen belgeler (Adım 2 öncesi)

- **ETSI TS 119 182-1 (JAdES):** LoTE ve WRPRC imza profili; compact/tek imza ayrıntısı.
- **ETSI TS 119 472-2/-3:** OID4VP/OID4VCI EUDI profilleri; ARF bunlara atıf yapıyor.
- **ETSI EN 319 411-1:** CRL/OCSP pencereleri ve 24 saatlik iptal kuralı.
- **OpenID Federation 1.0:** M-f taşıyıcı adayı.
- **RFC 5280** (yol doğrulama) ve **RFC 9101** (JAR): R1 ve R2 ayrıntısı.
- Hepsi açık erişimli. ISO/IEC 18013-5 ücretli ve kapsam dışı.
