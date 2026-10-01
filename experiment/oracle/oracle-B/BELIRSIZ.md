# BELİRSİZ KARARLAR — Oracle B

> `karar.tsv`'de `karar = indeterminate` olan **89 satırın** (732 satırın %12,2'si) nedenleri. Ölçüt (`YONTEM.md` §6.3): Maddeler MUST/MUST NOT/REQUIRED düzeyinde kabul ile ret arasında seçim yapmıyorsa ya da karar için gereken bağlam `insa` / `dogrulama_girdileri`'nde yoksa karar belirsizdir. SHOULD/RECOMMENDED/MAY yalnız **yön** olarak yazılır.
>
> **Önceden kayıtlı değişkenlere etkisi: yok.** Birincil (vektör, kol) çiftlerinin 159 satırının hiçbiri `indeterminate` değildir. Aşağıdaki satırların hepsi ikincil, MR eşi ya da eşleme dışıdır (ÖK §2G m.4: tanımlayıcı).
>
> Kısaltma: `@-13` / `@-19` = `politika` sütunundaki `|sdjwtvc=-13` / `|sdjwtvc=-19` eki.

| # | Neden | Satır |
|---|---|---|
| B1 | Çok imzalı SD-JWT+KB'de `sd_hash` bağlaması tanımsız | 18 |
| B2 | SD-JWT VC -19'da JSON serileştirme kapsam dışı | 26 |
| B3 | `typ` = `vc+sd-jwt` geçişi | 16 |
| B4 | `crit`'te yalnız MAY | 6 |
| B5 | Güven çapası x5c içinde | 3 |
| B6 | x5c ve başka anahtarı gösteren kid birlikte | 3 |
| B7 | Asgari olmayan DER (composite ECDSA bileşeni) | 3 |
| B8 | DPoP nonce/ath bağlamı verilmemiş | 6 |
| B9 | İmzasız OID4VP isteği, L4 (göç etmiş RP beklentisi) | 8 |
| | **Toplam** | **89** |

---

## B1 — Çok imzalı SD-JWT+KB'de `sd_hash` hangi imzaya bağlı? (18 satır)

**Satırlar:** `VP05_GJ_ES256_MLDSA65_kb`, `VP07_GJ_sd_hash_ikinci_imza`, `VP05_GJ_ES256_MLDSA65_kb-SIRA-ters` — `tedavi-ML-DSA-65`; `L4`, `P2`, `P0` × `@-13`, `@-19`.

**Maddeler:**
- RFC 9901 §8.1 (`RFC9901.txt:1900-1909`): "the digest in the sd_hash claim MUST be computed over the SD-JWT as described in Section 4.3.1 [...] the SD-JWT Compact Serialization part is built by concatenating the protected header, the payload, and the signature of the JWS JSON serialized SD-JWT". General JSON'da birden çok "protected header" ve "signature" vardır; hangisinin kullanılacağı yazılmaz.
- RFC 9901 §8.3 (`:1987-1989`): ifşalar ve `kb_jwt` "MUST be included in the first unprotected header" — ilk imza nesnesini öne çıkarır ama `sd_hash` hesabını bağlamaz.
- RFC 9901 §7.3 (5g) (`:1867-1870`): doğrulayıcı `sd_hash`'i eşleştirmek ZORUNDA.
- ÖK §2D m.4 (`:412`): "General JSON serileştirmede birden çok imza varsa `sd_hash`'in hangi imzayı bağladığı tanımsızdır."

**Neden belirsiz:** İhraççı katmanı her üç yapılandırmada kabul verir (iki imza da geçerli; L4'te R karşılanır). KB denetiminin sonucu doğrulayıcının §8.1 okumasına bağlıdır: VP05'te `sd_hash` ilk imzayla (ES256) kurulmuş — "ilk imza" okuyan kabul eder, başka okuma reddeder; VP07'de ikinci imzayla kurulmuş — tersi; VP05-SIRA-ters'te aynı KB, permütasyonla 1. sıraya geçen imzaya bağlı. Her okuma §8.1 ile uyumludur. `@-19`'da ayrıca B2 geçerlidir.

**Not:** Bu, ÖK'nin tanımlayıcı alt hücresidir ("KB bağlaması çoklu imza kümesini korumuyor", §2D m.4); hipotez değildir.

## B2 — SD-JWT VC -19'da JSON serileştirilmiş kimlik bilgisi (26 satır)

**Satırlar (hepsi `@-19`):**
- `VC09_GJ_ES256_EdDSA`, `VC09_GJ_ES256_EdDSA-SIRA-ters` (`kontrol-EdDSA`); `VC09_GJ_ES256_EdDSA-ED25519`, `VC09_GJ_ES256_EdDSA-SIRA-ters-ED25519` (`kontrol-Ed25519`); `VC07_GJ_ES256_MLDSA65`, `VC07_GJ_ES256_MLDSA65-SIRA-ters` (`tedavi-ML-DSA-65`); `VC08_GJ_ES256_composite`, `VC08_GJ_ES256_composite-SIRA-ters` (`tedavi-composite`) — `L4`, `P2`, `P0`.
- `VP06_GJ_pq_soyuldu_kb_gecerli` (`tedavi-ML-DSA-65`) — yalnız `P2`, `P0`. Bu vektörün `L4@-19` satırı `reject`'tir: kabul yolu yok (işlenirse R eksik, işlenmezse biçim desteklenmiyor).

**Maddeler:**
- SD-JWT VC -19 §2.2 (`SDJWTVC.txt:307-309`; T113): "Use of the JWS JSON Serialization per Section 8 of [RFC9901] for SD-JWT VC is not precluded but the specific details are beyond the scope of this specification."
- HAIP §6.1 (`HAIP.txt:468`; T115): "Compact serialization MUST be supported [...] JSON serialization MAY be supported."
- Karşıt: SD-JWT VC -13 §3.2 (`SDJWTVC13.txt:302-304`; T114) biçimi tanımlar ("Section 4 or Section 8 [...] support for the JWS JSON Serialization is OPTIONAL"); bu yüzden `@-13` satırları belirlenmiştir (biçimi desteklemeyen hedef B6 "uygulanamaz").
- ÖK §2D m.7 (`:423`): parametrenin kapsamı "senaryo (d) vektörleri (JSON serileştirmenin statüsü)".

**Neden belirsiz:** -19 biçimi yasaklamaz ama işlemesini de tanımlamaz. RFC 9901 §8'i uygulayan doğrulayıcı `@-13` kararını verir; -19 okumasıyla biçimi reddeden doğrulayıcı da uyumludur. **Yön:** yok. MR3 ("sürüm değişince karar değişiyorsa işaretlenir") bu satırlarla `@-13` satırlarının farkını kullanır.

## B3 — `typ` = `vc+sd-jwt` (VC11) (16 satır)

**Satırlar:** `VC11_typ_vc+sd-jwt`, dört kol × `P2`, `P0` × `@-13`, `@-19`. (`L4` satırları `reject`: klasik tek imza, R eksik.)

**Maddeler:**
- `@-13`: SD-JWT VC -13 §3.2.1 (`SDJWTVC13.txt:323-324`): "The typ value MUST use dc+sd-jwt." — ve (`:336-343`): "it is RECOMMENDED that Verifiers and Holders accept both vc+sd-jwt and dc+sd-jwt as the value of the typ header for a reasonable transitional period."
- `@-19`: SD-JWT VC -19 §2.2.1 (`SDJWTVC.txt:328-329`; T119): "The Issuer MUST include the typ header parameter in the SD-JWT. The typ value MUST use dc+sd-jwt."; geçiş notu kaldırıldı (değişiklik günlüğü `:3614-3620`: "Remove: "Note that this draft used vc+sd-jwt [...]""); doğrulayıcı `typ` denetimi RFC 9901 §9.11'de (`:2316-2319`) yalnız RECOMMENDED.

**Neden belirsiz:** Her iki sürümde de `typ` kuralı üreticiye MUST, doğrulayıcıya en çok RECOMMENDED'dir. **Yön:** `@-13` kabul (RECOMMENDED), `@-19` ret (geçiş notu yok; denetim önerilir). MR3 çiftinin (VC01 ↔ VC11) yorumu bu yönleri kullanabilir; yön bir oracle kararı değildir.

## B4 — `crit`'te kayıtlı ad ya da boş liste (6 satır)

**Satırlar:** `CRIT03_kayitli_ad`, `CRIT04_bos_dizi` — `tedavi-ML-DSA-65`; `L4`, `P2`, `P0`.

**Maddeler:** RFC 7515 §4.1.11 (`RFC7515.txt:703-711`): "Producers MUST NOT include Header Parameter names defined by this specification or [JWA] for use with JWS [...] Producers MUST NOT use the empty list "[]" as the "crit" value. Recipients MAY consider the JWS to be invalid if the critical list contains any Header Parameter names defined by this specification or [JWA] for use with JWS or if any other constraints on its use are violated."

**Neden belirsiz:** Yasak üreticiyedir; alıcıya yalnız MAY verilir. `alg` her alıcıca anlaşıldığından "not understood → invalid" kuralı (§4.1.11 ilk cümle) tetiklenmez; boş listede de anlaşılmayan ad yoktur. **Yön:** yok. (Karşılaştırma: `CRIT01` ve `CRIT05`'te listelenen uzantı anlaşılmadığı için `reject` belirlenmiştir; `CRIT02`'de korumasız `crit` de `reject`.)

## B5 — Güven çapası x5c içinde (3 satır)

**Satırlar:** `X5C06_guven_capasi_x5c_icinde` — `tedavi-ML-DSA-65`; `L4`, `P2`, `P0`.

**Maddeler:** HAIP §6.1.1 (`HAIP.txt:490`): "The X.509 certificate of the trust anchor MUST NOT be included in the x5c JOSE header of the SD-JWT VC." — RFC 7515 §4.1.6 (`RFC7515.txt:596-599`; T038): "The recipient MUST validate the certificate chain according to RFC 5280 [...] and consider the certificate or certificate chain to be invalid if any validation failure occurs."

**Neden belirsiz:** HAIP yükümlülüğü kimlik bilgisini üretene yöneliktir; doğrulayıcıya "reddet" demez. Kökün x5c'de bulunması RFC 5280 yol doğrulamasını bozmaz (çapa yerel olarak yapılandırılmıştır; `guven_capalari`). Hem kabul (yol geçerli) hem ret (profil uygunsuzluğu) uyumludur. **Yön:** yok.

## B6 — x5c ve başka anahtarı gösteren kid (3 satır)

**Satırlar:** `X5C10_x5c_ve_baska_anahtar_kid` — `tedavi-ML-DSA-65`; `L4`, `P2`, `P0`.

**Maddeler:**
- SD-JWT VC -13 §3.5 (`SDJWTVC13.txt:748-754`): "When the protected header of the Issuer-signed JWT contains the x5c parameter, the recipient uses the public key from the end-entity certificate of the certificates from that x5c parameter" → yaprak (ML-DSA-65) anahtarıyla imza geçerli → kabul.
- 8725bis §3.1 (`JWTBCP.txt:468-471`): "The library MUST verify that the algorithm specified in the "alg" [...] is consistent with the algorithm associated with the key identified by the corresponding identifier (e.g., "kid") during key lookup." → kid ile arama yapan kütüphane ES256 anahtarını bulur, ML-DSA-65 ile tutarsız → ret.
- RFC 7515 §4.1.4 (`:551-552`): kid "is a hint".

**Neden belirsiz:** x5c ile kid'in birlikte bulunduğunda hangisinin anahtar çözümlemede öncelikli olduğu maddelerce belirlenmiyor; iki yol da kendi maddesiyle uyumlu ve biri kabul, diğeri ret verir. Manifest de vektörü "Anahtar çözümleme belirsizliği" diye tanımlar. **Yön:** yok (ret yolu güvenli yöndedir ama zorunlu değildir).

## B7 — Asgari olmayan DER, composite ECDSA bileşeni (3 satır)

**Satırlar:** `CMP05_ecdsa_asgari_olmayan_der` — `tedavi-composite`; `L4`, `P2`, `P0`.

**Maddeler:**
- composite -04 §4.5 (`JOSECOMP.txt:555-557`): "the DER-encoded Ecdsa-Sig-Value [RFC3279]"; §4.5.1 (`:606`): "Decoding simply reverses these two steps."; §4.3 (`:489`): yanlış "type or length" → "Invalid signature".
- LAMPS composite -19 §4.3 (`LAMPSCOMP.txt:1300-1301`): "raising an error in the event that the input is malformed".
- composite -04 §6.4 (`JOSECOMP.txt:1101-1103`): "existential unforgeability under chosen-message attack (EUF-CMA) is sufficient to meet the intended security goals."

**Neden belirsiz:** Kodlama DER değil BER'dir (r önünde fazladan 0x00), sayısal değerler geçerli bir imzaya aittir (`insa`). Katı DER çözücü "malformed" sayıp reddeder; "reverses these two steps" okuyan çözücü aynı r, s'yi elde edip kabul eder. Katı DER reddini doğrulayıcıya açıkça yükleyen bir MUST yok; belirtilen güvenlik hedefi EUF-CMA'dır (imza biçim değiştirilebilirliği hedef dışı). **Yön:** yok. (Karşılaştırma: `CMP03` uzunluk baytı bozuk, `CMP04` DER değil, `CMP06` sonda artık bayt → "type or length" hatası olarak `reject` belirlenmiştir.)

## B8 — DPoP nonce/ath bağlamı (6 satır)

**Satırlar:** `DPOP08_ML-DSA-65_ath_nonce` (`tedavi-ML-DSA-65`), `DPOP09_ML-DSA-65-ES256_ath_nonce` (`tedavi-composite`) — `L4`, `P2`, `P0`.

**Maddeler:** RFC 9449 §4.3 (`RFC9449.txt:506-507`): "If the server provided a nonce value to the client, the nonce claim matches the server-provided nonce value." — (`:511-516`): "If presented to a protected resource in conjunction with an access token, [...] ensure that the value of the ath claim equals the hash of that access token".

**Neden belirsiz:** İmza ve algoritma düzeyinde kabul yolu vardır. `dogrulama_girdileri` yalnız `htm`, `htu` (belirteç uç noktası) ve `simdi` verir; sunucunun verdiği nonce ve erişim belirteci yoktur. Denetim 10 ve 12'nin sonucu bu bağlama bağlıdır. **Yön:** yok. (Bu vektörler boyut eşiği tablosu içindir; ÖK §2D m.6.)

## B9 — İmzasız OID4VP isteği, L4 (8 satır)

**Satırlar:** `REQ08_imzasiz_M-b0`, `REQ09_imzasiz_M-b0_client_id_korundu` — dört kol × `L4`. (`P2`/`P0` satırları `accept-classical`: imzasız istek desteklenmek zorunda; REQ09'da `client_id` yok sayılır.)

**Maddeler:**
- HAIP §5.2 (`HAIP.txt:426`; T281): "The Wallet MUST support unsigned, signed, and multi-signed requests as defined in Appendices A.3.1 and A.3.2 of [OIDF.OID4VP]." — (`:428`; T282): "unsigned requests depend on the origin information provided by the platform and the web PKI".
- OID4VP §5.9.3 (`OID4VP.txt:894`; T268): DC API'de "it is at the discretion of the Wallet whether it validates the signature on the Request Object".
- OID4VP A.2 (`:2500`; T279): "The Wallet MUST ignore any client_id parameter that is present in an unsigned request."
- ÖK §4.7 G5 (`:767`): göç etmiş varlık pencere dışında "yalnız klasik kanıtla kabul edilemez".

**Neden belirsiz:** `L4` yapılandırması imzalayan RP için R = {X} bekler; imzasız istekte imza yoktur ve RP kimliği yalnız köken + Web PKI (klasik) ile gelir. HAIP desteklemeyi zorunlu kılar, G5 (ÖK'nin güvenlik hedefi) yalnız klasik kanıtla kabulü yasaklar; üstelik `client_id` yok sayıldığı için cüzdan bu isteği "göç etmiş RP" ile eşleyemeyebilir. Maddeler çelişir ya da belirlemez. Bu, ÖK Ö4'teki **M-b0 (imzasızlaştırma)** taban sınıfıdır ve H3'ün biçimsel kısmında incelenir; kütüphane düzeyi oracle karar vermez. **Yön:** yok.
