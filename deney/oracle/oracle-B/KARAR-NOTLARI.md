# NOTLAR — Yürütücüye (Oracle B)

> Oracle türetmesi sırasında ön kayıtta (ÖK v0.8, SHA-256 `dcc84092…`) görülen belirsizlikler, çelişkiler ve uygulama boşlukları. **ÖK değiştirilmedi.** Her not: sorun → Oracle B'nin bu türetmede ne yaptığı → öneri. Öncelik: **Y** (önceden kayıtlı bir değişkeni etkiler), **O** (tanımlayıcı çıktıyı etkiler), **D** (düşük; açıklık).

---

## Y — Önceden kayıtlı değişkenleri etkileyebilenler

**N1 — Dört değerli oracle çıktısının semantiği tanımlı değil (Ö6).**
- *Sorun:* Ö6 yalnız adları verir (`accept-classical`, `accept-hybrid`, `reject`, `indeterminate`). (i) Saf PQ kabulü (K4 tedavi: yalnız ML-DSA-65) hangi değer? (ii) Kontrol kolunda X = EdDSA klasiktir; K1-kontrol "hybrid" mi "classical" mı? (iii) JWS imzası PQ ama sertifika yolunda klasik kenar varsa (K8)?
- *Yapılan:* `accept-hybrid` = kabul + geçerli PQ sınıfı bileşen (saf PQ dahil); kontrol kolundaki her kabul `accept-classical`; etiket yalnız JWS katmanını sınıflar (`YONTEM.md` §6.3).
- *Öneri:* ÖK dondurulmadan semantik yazılsın. Karşılaştırmada ikili eşleme (`accept-*` → kabul) kullanılırsa A/B arasında etiket farkı karar farkı sayılmamalı.

**N2 — V+ denetimi ile §6.5 politikası çelişiyor.**
- *Sorun:* §4.15: "V+: tek geçerli klasik imza → KABUL". Ama §6.5 politikası (R = {X}) ve §2B m.6 (L4c: "Göç etmiş ihraççının yalnız klasik imzalı belgesi reddedilir") altında `VPLUS_ES256` **RED** olmalıdır (G5). Adaptör L4 yapılandırmasındayken V+ koşulursa sağlam bir adaptör "geçersiz" sayılabilir (§4.15 → hedef n_eff dışına çıkar).
- *Yapılan:* `VPLUS_ES256` → `L4`: reject; `P2`/`P0`: accept-classical. Satır notunda uyarı var.
- *Öneri:* V± denetiminin yapılandırması sabitlensin: R_I = ∅ ("eski ihraççı", `P2`) ya da kolun X'iyle imzalı V+ (`VPLUS_EdDSA`, `VPLUS_ML-DSA-65`, `CMP00`) — bunlar üç yapılandırmada da kabul.

**N3 — K8/K9 uyarlamasının composite kolundaki yan etkisi.**
- *Sorun:* §2F m.4 K8'i "yaprak ML-DSA-65, ara CA klasik" (X5C04) ile gerçekler; eşleme X5C04 ve X5C07'yi composite sütununda da birincil sayar. Composite kolunun izinli kümesi {ES256, ML-DSA-65-ES256} olduğundan ML-DSA-65 imzalı bu vektörler bu kolda izin listesiyle reddedilir; B2/B3 davranışı composite kolunda **ölçülemez**.
- *Yapılan:* Composite kolunda iki vektör de üç yapılandırmada `reject` (gerekçe: izin listesi; X5C07'de ayrıca korumasız x5c); not: "UYARLAMA YAN ETKİSİ".
- *Öneri:* K8/K9'u eşlemenin de dediği gibi kol-bağımsız bayrak saymak ve yalnız X = yaprak alg (ML-DSA-65) politikasıyla ölçmek; composite sütununu "uygulanamaz" kaydetmek. (Alternatif — composite kolunda izinli kümeye ML-DSA-65 eklemek — §6.5'i değiştirir.)

**N4 — L4'te fazladan imzanın (K5) işlenmesi ÖK'de açık değil.**
- *Sorun:* §6.5 K5: "Politikaya göre (MR2); bayrak B1". §4.13 L4: "PQ bileşeni yoksa ret" — fazladan (izinli olmayan/kayıtsız) imza hakkında sessiz. İki makul okuma: (a) kümülatif §4.8 P3 (= P1 "ECCG AND" + bağlama + R_I) → K5 **RED**; (b) "gerekli küme karşılanınca fazlası yok sayılır" → K5 **KABUL**.
- *Yapılan:* (a) seçildi (`L4-TURETME-B.md` §2 A5, §9 S2): §4.8 kümülatif tanım, ACM v2 Note 51 "accepting if and only if all signatures are correct", 8725bis §3.1 "ensure that the received JWT complies". `P0`'da K5 kabul → MR2 politika bağımlılığı görünür.
- *Öneri:* L4 tanımına fazladan imza kuralı eklensin ve B1'in üç değeriyle (red / yok sayma / doğrulamanın düşmesi) ilişkisi yazılsın. Oracle A (b)'yi okursa ayrışma 4 birincil K5 satırında (`T7K`, `T7K-ED25519`, `T7P`, `T7C`, `L4`) ve K5 ikincillerinde beklenir.

**N5 — L4c için K1–K3 karşılıkları eşlemede yok.**
- *Sorun:* §2B m.6 Y_i'yi yalnız kompakt destekleyen hedeflerde L4c ile tanımlar; ama §6.5 bataryası K1–K5'i General JSON ile gerçekler ve `BATARYA-ESLEME.md` L4c'nin davranış ölçütünü hangi vektörlerin vereceğini söylemez. F_K/F_T (K1–K3'e dayanır) kompakt-yalnız hedefte nasıl hesaplanacak belli değil.
- *Yapılan:* Oracle, kompakt vektörleri iki ihraççı yapılandırmasında verir (`L4-TURETME-B.md` §4).
- *Öneri:* L4c eşlemesi: K1c ≈ `VPLUS_X` @`L4` (KABUL), K2c ≈ `VMINUS_X` @`L4` (RED), K3c ≈ `VPLUS_ES256` @`L4` (RED; göç etmiş ihraççı), eski ihraççı denetimi ≈ `VPLUS_ES256` @`P2` (KABUL); composite kolunda `CMP00` / `CMP01`.

**N6 — B5 sınıflaması için hangi oracle kullanılacak?**
- *Sorun:* §6.4 F_K/F_T'yi "en iyi ulaşılabilir yapılandırmada" L4 oracle'ına göre tanımlar; B5 (en-az-biri-geçerli / mevcut-tümü-geçerli / gerekli-küme / diğer) için karşılaştırma ölçütü yazılı değil.
- *Yapılan:* Üç yapılandırma B5'in üç sınıfına birebir karşılık gelecek biçimde türetildi (`P0`, `P2`, `L4`).
- *Öneri:* B5 = hedefin K1, K2, K3 (ve K5) davranışının hangi sütunla örtüştüğü; hiçbiri → "diğer".

## O — Tanımlayıcı çıktıyı etkileyenler

**N7 — G5'in eski-sürüm penceresi C3'te parametre değil.** K3/K11 RED kararları "penceresi kapanmış göç etmiş ihraççı" varsayar; pencere açıkken doğru karar `P2` sütunudur (`L4-TURETME-B.md` §5). ÖK'de bu varsayım açık yazılmalı.

**N8 — `sdjwtvc_surum` boyutu.** §2D m.7 kapsamı "senaryo (d) vektörleri ... ve VC11" ile sınırlar. Oracle bu vektörlerde her yapılandırmayı `|sdjwtvc=-13` / `|sdjwtvc=-19` diye ikiye böldü; `-19`'da JSON serileştirmeli kabul satırları `indeterminate` (BELIRSIZ B2). (i) MR3'ün "karar değişiyorsa" ölçütü belirlenmiş ↔ belirsiz geçişini nasıl sayacak? (ii) Düzleştirilmiş JSON vektörleri (X5C07/08/09, CRIT02; K9 birincili dahil) manifestte yalnız `-13` için tanımlı; `-19` ayarlı hedefte nasıl koşulacak? (iii) HAIP §9.4 SD-JWT VC -13'e sabitler; birincil sürüm hangisi?

**N9 — X5C ailesinde anahtar çözümleme yolu.** §2D m.1 "doğrulama anahtarı bütün kollarda hedefin belgeli API'siyle verilir (JWK/JWKS ya da doğrudan anahtar)" ama "zincir davranışı yalnız X5C vektörlerinde ... ölçülür". Oracle B X5C ailesinde **x5c üzerinden** çözümleme varsaydı. K9 (X5C07) RED kararı buna bağlıdır: anahtar JWKS'ten verilir ve korumasız x5c yok sayılırsa kabul de RFC 7515 §6 ile uyumludur ("if the only information used in the trust decision is a key, these parameters need not be integrity protected"). Adaptör sözleşmesinde yol açıkça yazılmalı.

**N10 — K10 "RED (L2/L3)".** 8725bis §3.1'e göre alg–anahtar tutarlılığı bir **kütüphane** MUST'ıdır; red her yapılandırmada beklenir (P0 dahil). "(L2/L3)" ibaresi redin yalnız L2/L3 yapılandırmasında beklendiği biçiminde okunabilir; netleşmeli.

**N11 — Eşleme dışı 46 vektör ve R_I benzetmesi.** REQ (RP), TSL (durum ihraççısı), DPoP (istemci; RFC 9449 §4.3(5) "acceptable per local policy") vektörlerinde R_I benzetmeyle uygulandı. ÖK eşleme dışı vektörlerin raporlanma biçimini yazmıyor (§2G m.4 yalnız "ikincil vektörler tanımlayıcıdır").

**N12 — K11'de değerlendirilecek kopya.** Eşleme notu VC10.credentials[0]'ı değerlendirir; bir hedefin toplu yanıttaki iki kopyayı ayrı ayrı işleyip işlemediği adaptöre bağlı. Adaptör sözleşmesinde "credentials[0]" açıkça yazılmalı.

**N13 — Kontrol kolunda L4'ün okunuşu.** §4.13 L4 "PQ bileşeni yoksa ret" der; kontrol kolunda (X = EdDSA) bu "X bileşeni yoksa ret" diye okunmalıdır (§3.7'den çıkıyor, açık yazılı değil). Oracle B böyle okudu.

## D — Açıklık / beyan

**N14 — ÖK sürümü.** `BATARYA-ESLEME.md` ÖK v0.6'yı (`c239d423…`) alıntılar; Oracle B'nin okuduğu ÖK v0.8'dir (`dcc84092…`). Kullanılan maddeler (§6.5, §4.13, §4.20, §2B m.6–8) eşlemedeki alıntılarla aynıdır.

**N15 — CMP10 "spesifikasyon-belirsizliği" etiketi.** Normatif Tablo 5 (ML-DSA-65-ES256 ön-özeti SHA512) kararı belirler (RED); -04 §7.1.2 IANA açıklamasındaki "SHA-256" ECDSA bileşeninin iç özetidir. Oracle bunu belirsiz saymadı; D-S5 "yanlış ön-özet" tanımlayıcı sınıfı olarak kalır.

**N16 — MR4 ve SD-JWT VC.** SD-JWT VC permütasyonlarında ifşalar yeni ilk başlığa taşınmış (RFC 9901 §8.3 uyumlu); Oracle B MR4 eşlerini kaynaklarıyla aynı karara bağladı. `VP05…-SIRA-ters` MR4 dışıdır ve B1 nedeniyle belirsizdir.

**N17 — Okuma beyanı.** İstenen §2D madde 1–8'i okurken aynı parçada B bölümü (m.9–17, biçimsel sonuçlar) göründü; türetmede kullanılmadı. İzlenebilirlik matrisinin ilk 8 satırının `not` sütunu `head` çıktısında göründü (LOTL/TL; ilgisiz). Ayrıntı `ERISIM-KAYDI.md`.
