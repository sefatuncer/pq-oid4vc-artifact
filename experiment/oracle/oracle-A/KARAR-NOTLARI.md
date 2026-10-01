# Oracle A → yürütücü notları (25.09.2026)

> ÖK **değiştirilmedi.** Aşağıdakiler ön kayıtta bulduğum boşluklar, çelişkiler ve önerilerdir. Öncelik sırası: **N-0 kritik**; N-1–N-4 dondurmadan önce karar gerektirir; geri kalanı netleştirmedir.
> Hiçbir hedef koşulmadı. Oracle kararları yalnız madde + `insa` gerçeklerinden türetildi.

## N-0 (KRİTİK). COSE tabakası için bataryada vektör yok

- **Durum:**
  - n = 31'in 5'i COSE hedefidir: COSE-001 Signum, COSE-014 cose-js, COSE-034 go-cose, COSE-035 cose-lib, COSE-036 wolfCOSE. Beşi de yalnız COSE_Sign1/COSE_Sign doğrular.
  - v1.2'nin 153 vektörü ise tümüyle JWS/SD-JWT biçimindedir: artefakt türleri `jws-cekirdek`, `sd-jwt-vc`, `oid4vp-istek`, `dpop`, `sd-jwt-vc+kb`, `status-list-token`.
  - ÖK §2D m.8 bunu yalnız bir geçerlilik tehdidi olarak yazıyor: "v1'de COSE/mdoc, JWE ve WIA/KA yok". Ölçüme etkisi ise yazılı değil.
- **Sonuç:** Bu 5 hedefte bataryanın bütün satırları B6 ("uygulanamaz") olur. Y_L4 davranışsal olarak doğrulanamaz; F_K, F_T ve D_soy hesaplanamaz.
  - L düzeyi yalnız API taramasıyla belirlenebilir. Kanıt kuralı (§4.14) davranış doğrulaması olmadan "ifade edilemez" hükmünü desteklemez → çoğu **belirsiz** çıkar.
  - n_eff büyük olasılıkla ≤ 26 olur. Eşikler ÖK Ek A'dan yeniden okunur; ör. n = 26 için ≤ 8 / ≥ 18.
- **Seçenekler (karar yürütücünün ve kullanıcının; büyük sapma adayı, İ7):**
  - (a) COSE_Sign (çok imzacılı) ve COSE_Sign1 karşılıkları olan bir **COSE bataryası** üretmek (K1–K5, K7, K10, V±). `pqjose` COSE'u zaten destekliyor. Bu yeni bir çapa gerektirir ve dondurmadan önce yapılmalıdır (ÖK §2E m.4).
  - (b) COSE hedeflerini API taramasıyla sınıflayıp birincil analizden çıkarmak (n_eff düşer, gerekçe yazılır).
  - (c) COSE tabakasını yalnız tanımlayıcı raporlamak.
- **Önerim:** (a). ÖK'nin RQ3'ü "JOSE/COSE/SD-JWT kütüphaneleri" diyor; COSE kotası (5) ölçülmezse örneklem tasarımı boşa düşer.

## N-1. §6.5 politikası izin kümesi dışındaki ek imzada S mi, Y mi?

- ÖK K5'i "Politikaya göre (MR2)" diye açık bırakıyor. İki tanım da bu yönde farklı:
  - §4.8 P3 = P2 + R_I ve P2 ⊇ P1 ("mevcut imzaların tümü geçerli") → **S**.
  - Envanterin L4 önerisi (KRITERLER §7.7: "gerekli kümedeki her algoritmanın mevcut ve geçerli olması") → **Y**.
- Oracle A bu yüzden `L4`'te K5 ailesine `indeterminate` yazdı ve iki alt yapılandırma (`L4-S`, `L4-Y`) verdi. Birincil etkisi yok: F_K/F_T yalnız K1–K3'ten hesaplanır ve orada S = Y.
- **Öneri:** v1.0 birleştirmesinde §6.5'e bir cümle eklenmesi. Örnek: "K5 için oracle, hedefin belgeli çoklu imza semantiğine göre S (P3/P1) ya da Y (R-yalnız) satırıdır; ikisine de uymayan davranış MR2 ihlalidir." B1'in değerleri de bu iki satıra bağlanmalı.

## N-2. L4c: bataryada ayrı bir "eski ihraççı" yok

- ÖK §2B m.6: "Aynı doğrulayıcı örneğinde … eski ihraççının klasik imzalı belgesi kabul edilir."
- v1.2'de tek `iss` (`https://issuer.example`) ve tek ES256 ihraççı anahtarı (issuer/ES256) var. Göç etmiş ihraççının klasik kopyası (VC10[0], VPLUS_ES256) ile "eski ihraççının belgesi" aynı anahtar ve aynı `iss`'tir.
- Oracle A iki yapılandırma verdi: `L4` (göç → reject) ve `IZIN-AX` (eski → accept-classical). "Aynı örnek" koşulu ancak API ihraççı kaydını anahtara bağlayabiliyorsa sağlanır (`adaptor-sozlesme.md` §5.3).
- **Öneri:**
  - ya bataryaya ayrı `iss` ve ayrı ES256 anahtarla bir "eski ihraççı" vektörü eklemek (yeni çapa),
  - ya da ÖK'ye "L4c, aynı API mekanizmasıyla iki ardışık yapılandırmada sınanabilir; bu durumda 'L4c (ardışık)' olarak işaretlenir" netleştirmesini yazmak.

## N-3. K8/K9'un composite kolundaki politika örneklemesi

- ÖK §2F m.4, K8'i composite kolunda da ML-DSA-65 yapraklı X5C04 ile gerçekleştiriyor. K9 için de ESLEME aynı uyarlamayı yapıyor (X5C07).
- Composite kolunun politikası R = {ML-DSA-65-ES256} olarak okunursa X5C04 salt algoritma nedeniyle **reddedilir** ve B2 hiç sınanmamış olur.
- Oracle A bu satırlarda politikayı **X = ML-DSA-65** ile örnekledi. Satırlarda not var. ÖK'de bu yorum yazılı değil; A ile B'nin burada ayrışma olasılığı yüksek.
- **Öneri:** ÖK §2F m.4'e "composite kolunda K8/K9 için R = {ML-DSA-65}" eklenmesi, ya da B2/B3'ün açıkça "kol-bağımsız, ML-DSA-65 kolunda ölçülür" diye yazılması.

## N-4. DPoP: composite algoritmaları IANA'da kayıtlı değil

- RFC 9449 §4.3 madde 5 [T378]: "The alg JOSE Header Parameter indicates a **registered** asymmetric digital signature algorithm [IANA.JOSE.ALGS]…".
- composite -04 §7.1: "are **requested** to be added to the … registry".
- Bu yüzden RFC 9449'a uygun bir sunucu DPOP06, DPOP07 ve DPOP09'u (ML-DSA-65-ES256, ML-DSA-65-Ed25519) reddetmek zorundadır. Oracle A bunları `reject` yazdı; not: "kayıt olursa accept-hybrid".
- **Etki:** Adım 12'deki M3 dağıtım kısıtı tablosu yalnız boyutu değil, **kayıt koşulunu** da taşımalı. Composite DPoP, taslak RFC olana kadar kütüphaneden bağımsız olarak spesifikasyona aykırıdır. Bu makalede kısa ama bariz olmayan bir dağıtım notu olabilir (tahmin).

## N-5. Dört değerli etiketin anlamı ÖK'de tanımlı değil

- Ö6 dört değeri sayıyor, ama `accept-hybrid` ile `accept-classical`'ın hangi ölçütle ayrıldığını yazmıyor.
- Oracle A'nın tanımı (`YONTEM.md` §1; `L4-TURETME.md` §4): "accept-hybrid ⇔ kabul **ve** yapılandırmaya uygun her kabul yolu geçerli bir PQ bileşeninin doğrulanmasını gerektirir". Bu tanımla:
  - P0 altında ES256 + ML-DSA nesnesi → `accept-classical`;
  - P1 altında aynı nesne → `accept-hybrid`;
  - yalnız ML-DSA imzalı nesne → `accept-hybrid`.
- Oracle B farklı bir tanım kullanırsa, aynı kabul kararlarında yalnız etiket nedeniyle "uyuşmazlık" çıkar. Bu gerçek bir oracle uyuşmazlığı değildir.
- **Öneri:** A–B karşılaştırması iki düzeyde raporlansın: (i) kaba (kabul / red / belirsiz) ve (ii) dört değerli. ÖK'ye tanımın yazılması önerilir.

## N-6. composite ECDSA bileşeninin DER katılığı (CMP05, CMP06)

- -04 §4.5.1 kodlamayı DER olarak tanımlıyor, ama çözme için yalnız şunu diyor: "Decoding simply reverses these two steps".
- LAMPS -19 §4.3 "raising an error in the event that the input is malformed" diyor, ama "malformed"ı tanımlamıyor.
- CMP06'nın tradSig'i 72 bayt olduğu için -04 Tablo 2'deki "≤ 72" sınırına da takılmıyor.
- Oracle A her iki vektöre `indeterminate` yazdı (BELIRSIZ B-3).
- **Öneri:** DB-2'ye (composite -04 açıklama metni) editoryal ek aday. Örnek metin: "Ecdsa-Sig-Value MUST be DER; verifiers MUST reject non-minimal encodings and trailing data." İnsan kararı; hiçbir şey gönderilmedi.

## N-7. Sürüm sabitleme TK atamasını değiştirebilir

- Ortam çalışmasının 25.09 ara kaydı iki olgu içeriyor:
  - cose-lib 4.8.2'de ML-DSA kaynağı yok; HEAD `1c854bf63c5c`'de var.
  - go-cose v1.3.0 README'sinde envanterin "ML-DSA kısmi" dayanağı yok; HEAD'de var.
- Envanterin TK dayanakları HEAD commit'lerine ait. Yayım sürümüyle ölçülürse cose-lib TK1 → TK3'e düşer.
- **Öneri:** KRITERLER §7 m.6 ("son_commit_sha ile sabitlenir") uygulanıp ölçüm sabit commit'ten derlenen hedefle yapılsın. Yayım sürümü ayrıca kaydedilsin. Bu karar TK tablosunun dondurulmasından önce alınmalı (`adaptor-sozlesme.md` §4).

## N-8. SDJWT-004 authlete/sd-jwt imza doğrulaması yapmıyor (ortam kaydı)

- Ortam çalışmasına göre kütüphanenin çalışma zamanı bağımlılığı yalnız gson; JWS imzası çağırana bırakılıyor.
- Bu durumda politika katmanı kütüphanede değildir.
  - Ya K1 dahil etme ölçütü ("asimetrik doğrulama") sağlanmıyor → dışlama ve yedekle değiştirme (KRITERLER §5.4),
  - ya da L0 "imza politikası yok" olarak ölçülür.
- **Öneri:** Davranış ölçümünden önce, yalnız API incelemesiyle karar verilmesi.

## N-9. REQ vektörleri cüzdan tarafıdır; OID4VP imza doğrulamasını cüzdanın takdirine bırakıyor

- OID4VP §5.9.3 [T268]: "it is at the discretion of the Wallet whether it validates the signature on the Request Object" (DC API).
- Oracle A'nın REQ satırları "cüzdan imzaları doğrular" varsayımıyla yazıldı. RP için L4, "varlık başına" R_RP = {X} okumasıyla uyarlandı (G5 "göç etmiş bir varlık").
- Bu satırlar kütüphane bataryasında değil, Adım 11'de (wallet-path) kullanılır. Varsayımın Adım 11 tasarımına yazılması önerilir.

## N-10. ECCG ACM v2 ile §6.5 K4 arasında politika farkı (bilgi)

- ACM2 Not 51: ML-DSA "shouldn't be used in a standalone way".
- §6.5 K4 ise "Yalnız X → KABUL" diyor ve ML-DSA kolunda T5P'yi kabul ediyor.
- İkisi farklı politikalardır; oracle §6.5'i izledi. ECCG'ye uyumlu bir doğrulayıcının T5P'yi reddetmesi §6.5 oracle'ına göre "sapma" görünür. Adım 13 tartışmasında belirtilmeli.

## N-11. Saat enjeksiyonu adaptör ön koşulu olmalı

- Vektörlerin zamanı sabit: `simdi` = 1790003700 (2026-09-21). KB-JWT `iat` = simdi − 100 s, DPoP `iat` = simdi − 10 s.
- Gerçek saatle ölçüm (Kasım 2026) bu pencerelerin dışına düşer. Saat enjekte edemeyen hedefte VP ve DPOP hücreleri `zaman` hatasıyla belirsizleşir.
- **Öneri:** Adaptör kapısına "saat enjekte edilebiliyor mu?" sorusunun eklenmesi (`adaptor-sozlesme.md` §2.1).

## N-12. A–B karşılaştırmasının anahtarı

- Karşılaştırma anahtarı (vektor_id, politika, kol) olmalı. Oracle A'nın yapılandırma adları: GEC, IZIN-A, IZIN-AX, L4, L4-S, L4-Y, P0, P1, L4-YOL, @-19.
- **Öneri:** Oracle B'nin adları bir eşleme tablosuyla hizalansın. Yalnız bir oracle'da bulunan satırlar "tek oracle" diye ayrı raporlansın; bunlar uyuşmazlık sayılmamalı.
- Kaba karşılaştırma için §6.5 birincil hücreleri çekirdek küme olarak önerilir: `sinif = birincil` ve politika `L4` ya da `GEC`. Bu, 316 birincil satırın 92'sidir (L4: 53, GEC: 39). Bu 92 satırın 4'ü `indeterminate`'tir (K5 ailesinin temel L4 satırları).

## N-13. Küçük tutarlılık notları

- **ÖK §2E m.1'deki yedek eş sayımı:** v1.1 "7 eş" diyor. v1.2'de EdDSA etiketli **her** kontrol vektörünün `-ED25519` eşi var; betik bunu denetledi. Eşi olmayan tek kontrol vektörü `K10K_alg-ES256_anahtar-Ed25519`'dur, çünkü EdDSA etiketi taşımaz. Oracle bu vektörü yedek kolda aynen kullandı.
- **VC11 (-19):** Red SHOULD düzeyindedir (RFC 9901 §9.11 RECOMMENDED; -19'da geçiş notu kaldırıldı). MR3 bu satırı "beklenen sürüm etkisi" olarak işaretleyecek.
- **8725bis §3.14:** JWT kütüphaneleri General JSON girdiyi zorunlu olarak reddeder. Bu, K1–K5'in (senaryo d) yalnız JWS JSON API'si olan hedeflerde anlamlı olduğunu gösterir; ÖK "spesifikasyon dışı" etiketiyle zaten tutarlı. Adaptör sözleşmesinde bu red B6 sayıldı, oracle sapması sayılmadı.
