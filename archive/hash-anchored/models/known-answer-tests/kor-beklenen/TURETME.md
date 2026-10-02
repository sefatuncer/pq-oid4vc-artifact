# Kör türetme: KAT-1/2/3 beklenen değerleri (kat-kor, Adım 6 görev 0)

> Değerler yalnız `GIRDI/KAT-KOR-GIRDI.md` içindeki hücre tanımlarından ve birincil kaynaklardan türetildi. Model, taslak kod ya da ilk çalışmanın tablosu görülmedi; hiçbir araç koşturulmadı. Birincil kaynaklardaki satır numaraları `BEKLENEN-KOR.tsv`'nin `satir` sütunundadır. Etiket: [Y] kendi çıkarımım.

## 0. Ortak yorum kararları

### 0.1 Zaman sabitleri (`now`, `qday`, `tau`, `exposure`)

Girdi dosyası şu sayısal değerleri vermiyor; bunlar taslak kodla birlikte çıkarılmış:
- varsayılan `now`, `qday`, `tau` ve `exposure` değerleri,
- sürümlerin imza geçerlilik aralıkları (`version(I,V,Inc,Exp)`).

Girdide açıkça olan tek zaman tanımı KAT-3b'de: "`qday=0` (bütün klasik anahtarlar kırık)" ve "`qday=200` (CRQC yok)". Bu yüzden:

1. **Sayısal etkileşim bu çalışma için belirsiz.** Hangi `now` anında hangi sürümün imzasının geçerli olduğu ya da τ'nun kırılma anını ne kadar geciktirdiği girdiden okunamıyor.
2. **Değerleri mantıksal durumdan türettim.** Mantıksal durumu hücrenin Tamarin bayrakları kodluyor (CRQC var/yok, eski DS ya da DNSKEY sürümü kullanılabilir mi). Gerekçe girdi §0'da:
   - ölçüt 2: "Mantıksal hücre, zamanı yalnız bayrakla temsil edilen hücredir",
   - ölçüt 3: ortak hücrelerde ASP ile Tamarin %100 uyumlu olmalı.

   Yani bayrak kümesi, ASP sabitlerinin mantıksal izdüşümüdür [Y].
3. **Varsayılan (hücrede `qday` verilmemişse):**
   - CRQC etkindir ve bütün klasik anahtarlar `now` anında kırıktır. Bu, KAT-3b'deki "qday=0" tanımına benzetme [Y]. Tamarin'de karşılığı `NO_QDAY` bayrağının yokluğudur.
   - PQ anahtarlar kırılmaz.
   - `comp` anahtar yalnız bütün bileşenleri kırılırsa kırılır (girdi §1.1). Dolayısıyla CRQC altında composite kırılmaz.
4. **τ:** Tamarin τ'yu modellemiyor (girdi §1.4). τ > 0 olup bir klasik anahtarın kırılma anı (max(qday, exposure) + τ [Y]) hücrenin `now` değerini aşarsa, o hücrenin ASP değeri SALDIRI'dan YOK'a dönebilir. Bu koşullu bağımlılık `BELIRSIZ.md` §B'de listelendi.

### 0.2 Değer eşlemesi ve saldırgan

- **Değer eşlemesi:** ASP'de SALDIRI ⟺ Tamarin'deki all-traces kimlik doğrulama lemması falsified, çünkü saldırı izi lemmaya karşı örnektir.
- **Saldırgan:**
  - Dolev-Yao ağ saldırganı: yanıtları seçer, düşürür ve yeniden oynatır.
  - CRQC: kırık klasik anahtarla imza sahteler.
  - Kendi anahtarını üretebilir (girdi §2(c) Not: "Saldırgan kendi anahtarını üretebilir").
  - Eski imzalı sürümü, imzası geçerli kaldığı sürece yeniden oynatabilir (RFC 6781 §4.3.4).
- **Kanal (girdi §1.1):** KAT-1'de taşıma kimliği doğrulanmamıştır. Saldırgan, yanıtta hangi RRSIG'lerin bulunacağını kendisi seçer.

---

## 1. KAT-1 DNSSEC

### 1.1 Semantik

**Aşamalar.** RFC 6781 §4.1.4, Şekil 8 altı aşama sayar: initial, new RRSIGs, new DNSKEY, new DS, DNSKEY removal, RRSIGs removal.
- Hücrelerde `r3` her zaman DS_PQ bayrağıyla geliyor. Şekil 8'de DS yalnız "new DS" aşamasında yeni anahtara geçer (satır 1566–1572: `DS_K_2`, `RRSIG_par(DS_K_2)`).
- Buradan numaralandırma 0 tabanlı çıkıyor [Y]: r0 initial, r1 new RRSIGs, r2 new DNSKEY, r3 new DS, r4 DNSKEY removal, r5 RRSIGs removal.
- 1 tabanlı okumada r3 = new DNSKEY olurdu. O aşamada DS hâlâ `DS_K_1` (klasik) olduğundan bu okuma DS_PQ bayrağıyla çelişir.
- Sonuçlar numaralandırmaya duyarsız: r2 iki okumada da DS_CL'dir, r5 iki okumada da DNSKEY RRset'inde yalnız Q anahtarları bulunur.

**Anahtarlar.**
- Algoritma 1 klasik (C): `K_1`, `Z_10`. Algoritma 2 PQ (Q): `K_2`, `Z_11`.
- **DK3:** iki algoritmanın anahtarlarını içeren DNSKEY RRset'i, {K_1, K_2, Z_10, Z_11} (Şekil 8 satır 1558–1563).
- **DK5:** yalnız Q anahtarlarını içeren RRset, {K_2, Z_11} (satır 1580–1582).
- **DK3_USABLE:** DK3 kullanılabilir; ya günceldir ya da imzası hâlâ geçerli eski bir sürümdür.
- **`dds`:** Double-DS aşaması. Üst bölge `DS_K_1` ile `DS_K_2`'yi birlikte yayımlar (RFC 6781 §4.1.2, Şekil 5, satır 1307–1308) → DS_BOTH.
- **Üst bölge anahtarı:** Varsayılanı PQ kabul ettim, çünkü K1-12 `parent_class=cl` sapmasını ayrıca veriyor [Y].

**Politikalar.**
- **`anyvalid`:** RFC 6840 §5.11 "Validators SHOULD accept any single valid path" (s. 594–595). Ayrıca §5.4 "accept any valid RRSIG as sufficient" (s. 446–448) ve Ek C.2 (s. 1027–1044).
- **`required`:** İmza bütünlüğü testi. §5.11 bu testi, doğrulayıcının "insist that all algorithms signaled in the DS RRset work" demesi olarak tanımlar (s. 595–599).
  - Gerekli sınıflar, DS'nin işaretlediği algoritmalardır (girdi §1.1: `signal_s/3`, `signal_v/4` = "DS'nin işaretlediği algoritmalar").
  - DNSKEY RRset'indeki algoritmalar gerekli kılınmaz (§5.11: "MUST NOT insist that all algorithms signaled in the DNSKEY RRset work").
- **`allpresent`:** P1, "fırsatçı: varsa denetle" (girdi §1.1 politika eşlemesi; DNSSEC sütunu "—"). Yanıtta bulunan her RRSIG doğrulanır, bulunmayan tolere edilir.
- **`monotone=1`:** "RRSIG geçerliliği içinde geri dönüşü reddetme" (girdi §1.1). Doğrulayıcı en yeni sürümü görmüştür (`seen`) ve daha eskisini reddeder [Y].

**Tamarin lemması `a_rrset_authentic`:** Kabul edilen A RRset'i dürüst bölgenin yayımladığı RRset'tir. Saldırı izi varsa lemma falsified olur.

### 1.2 Hücre hücre türetme

| Hücre | Durum | Belirleyen kural (birincil) | ASP | Tamarin |
|---|---|---|---|---|
| K1-01 | r2, DS=K_1 (C), anyvalid | Zincir DS→K_1→DNSKEY→Z_10→A bütünüyle klasik; CRQC K_1'i (ya da Z_10'u) kırar. RFC 6781 §4.2.1: "vulnerable as long as … a DS record in the parent zone points to it" | SALDIRI | falsified |
| K1-02 | r2, DS=K_1, required | DS yalnız C'yi işaretliyor. Bütünlük testi yalnız C'yi ister; sahte C imzası bunu karşılar. §4.2.1 aynı; RFC 6840 §5.11 (s. 570–571: DS "signal[s] which algorithms") [Y] | SALDIRI | falsified |
| K1-03 | r3, DS=K_2 (Q), DK3 güncel, anyvalid | DS→K_2 gerçek DK3'ü doğrular. DK3'te Z_10 durur; RFC 6840 §6.2: "any DNSKEY in the zone's signed DNSKEY RRset may be used to authenticate any RRset". Z_10 ile sahte A kabul edilir | SALDIRI | falsified |
| K1-04 | r3, DS=K_2, required | Bütünlük testi DS'nin işaretlediği Q'nun çalışmasını ister (§5.11 s. 595–599). Sahte A RRset'i geçerli Q imzası taşıyamaz. Üst bölge PQ olduğundan DS de sahtelenemez | YOK | verified |
| K1-05 | K1-04 + now=50, OLD_DS_REPLAY | Eski DS_K_1'in üst bölge imzası hâlâ geçerli. RFC 6781 §4.3.4: "the DS can be replayed as long as it has a valid signature". Yeniden oynatılan DS yalnız C'yi işaretler, bütünlük testi yalnız C'yi ister | SALDIRI | falsified |
| K1-06 | K1-05 + monotone=1 | Tekdüze doğrulayıcı yeni DS sürümünü görmüştür ve eski DS'yi reddeder [Y]. Durum K1-04'e indirgenir | YOK | verified |
| K1-07 | r5, DK5 güncel + DK3 eski ama imzası geçerli, anyvalid | Eski DK3, K_2 imzası geçerli olduğu için DS→K_2 ile doğrulanır ve içindeki Z_10 kullanılabilir. RFC 6781 §4.2.2: "until the RRSIG over the compromised ZSK has expired, the zone may still be at risk"; §4.2.1.1 (s. 1893–1895) "upper limit on how long the compromised KSK can be used in a replay attack" | SALDIRI | falsified |
| K1-08 | K1-07 + monotone=1 | Doğrulayıcı DK5'i görmüştür ve eski DK3'ü reddeder. Güncel DK5'te Z_10 yok; RFC 6840 §5.12: "MUST disregard RRSIGs … that do not (currently) have a corresponding DNSKEY" | YOK | verified |
| K1-09 | r5, now=150, yalnız DK5 | DK3'ün ve eski DS'nin imza süresi doldu (bayrakta DK3_USABLE ve OLD_DS_REPLAY yok). Klasik anahtar hiçbir geçerli yolda değil; §5.12 sahte Z_10 imzasını dışlar. Pencere kapandı (§4.2.2 "until … has expired") | YOK | verified |
| K1-10 | dds, DS={K_1,K_2}, anyvalid | Double-DS'de DS_K_1 hâlâ K_1'i gösterir (§4.1.2 s. 1307–1308). §4.2.1 "a DS record in the parent zone points to it"; anyvalid'de tek geçerli yol yeter | SALDIRI | falsified |
| K1-11 | dds, required | DS iki algoritmayı da işaretliyor. Bütünlük testi Q'yu da ister (§5.11 s. 595–599); sahte A için Q imzası yok | YOK | verified |
| K1-12 | r3, required, üst bölge klasik | Kırık üst bölge anahtarı sahte DS'yi imzalar (C'yi ya da saldırganın kendi anahtarını işaretler). Sinyal sahtelenince bütünlük testi yalnız C'yi ister. RFC 6781 §4.2.1 (s. 1842–1843): "A compromised KSK can be used to sign the key set of an attacker's version of the zone"; bu cümle üst bölgeye uygulandı [Y] | SALDIRI | falsified |
| K1-13 | r3, anyvalid, qday=200 | CRQC yok (NO_QDAY), hiçbir anahtar ele geçirilmemiş. §4.2.1'deki açık yalnız "compromised" anahtarla doğar [Y] | YOK | verified |
| K1-14 | K1-09 + extra_ta=1 | Ek güven çapası, eski klasik çapa olarak yorumlandı [Y] (bkz. 1.4). RFC 6840 Ek C.2: "subject to the compromise of the weakest of these trust anchors … keep old trust anchors configured in perpetuity"; RFC 6781 §4.2.1: "vulnerable as long as the compromised KSK is configured as the trust anchor" | SALDIRI | falsified |
| K1-15 | r3, allpresent | RRSIG'ler ayrı kayıtlardır; saldırgan sahte A'yı yalnız sahte Z_10 RRSIG'iyle gönderir. Bulunan her imza geçerli, Q yokluğu tolere edilir. RFC 9955 §6.2: "if a system does skip a component signature, security does not rely on the security of all component signatures" | SALDIRI | falsified |

### 1.3 Zaman etkileşimi (KAT-1)

- **K1-05 (`now=50`):** Eski DS'nin imzasının 50'de hâlâ geçerli olduğunu OLD_DS_REPLAY bayrağından çıkardım. Sayısal aralık girdide yok.
- **K1-07/K1-08 (`now` varsayılan):** Eski DK3'ün K_2 imzasının hâlâ geçerli olduğunu DK3_USABLE bayrağından çıkardım.
- **K1-09/K1-14 (`now=150`):** Bayraklarda DK3_USABLE ve OLD_DS_REPLAY yok. Buradan DK3'ün ve eski DS'nin imza süresinin 150'de dolduğunu çıkardım.
- **K1-13 (`qday=200`):** NO_QDAY bayrağından çıkarım: varsayılan `now` < 200 ve CRQC yok.
- **τ ve `exposure`:** KAT-1 hücrelerinde verilmemiş. K1-05'in SALDIRI değeri, K_1 ya da Z_10'un `now=50`'den önce kırılmış olmasına bağlı. Yani max(qday, exposure) + τ ≤ 50 olmalı [Y]. Bu koşul Tamarin bayraklarının kodladığı durumdur; sayısal olarak doğrulanamadı (BELIRSIZ.md §B).

### 1.4 Yorum kararları (KAT-1)

1. **K1-14 `extra_ta`, eski klasik çapa olarak yorumlandı.** Hücre tanımı çapanın sınıfını vermiyor.
   - Yeniden üretilecek sonuç RFC 6840 Ek C.2'nin "weakest of these trust anchors" ve "old trust anchors configured in perpetuity" cümleleri. C→Q geçişinde eski çapa klasiktir.
   - Çapa PQ olsaydı hücre K1-09'un kopyası olurdu.
   - Kaynak, klasik çapa için tek sonuç veriyor: SALDIRI.
2. **K1-15 `allpresent`, "yanıtta bulunan her RRSIG doğrulanır" olarak yorumlandı.** Girdi eşlemesi bunu "fırsatçı: varsa denetle" diye tanımlıyor.
   - Alternatif okuma: "DNSKEY RRset'indeki her algoritma gerekli" (RFC 6781 §4.1.4'teki "conservative approach", s. 1477–1480). Bu okumayla değer YOK olurdu.
   - Bu okumayı reddettim, çünkü: girdi eşlemesi `allpresent` için DNSSEC karşılığını "—" veriyor; imza bütünlüğü testine karşılık gelen politika zaten `required`; RFC 6840 §5.11 doğrulayıcıya "MUST NOT insist that all algorithms signaled in the DNSKEY RRset work" diyor.
3. **Tekdüzelik.** `monotone=1` hücrelerinde doğrulayıcının en yeni sürümü (DS_K_2 ya da DK5) gördüğü kabul edildi. Görmemiş olsaydı (ilk temas), K1-08 SALDIRI olurdu. Bu varsayım girdi §1.1'deki "geri dönüşü reddetme" tanımından geliyor.
4. **Sahte ZSK yolu.** Bütünlük testi DS'nin işaretlediği algoritmaları A RRset'i dahil zincirin tamamında ister [Y]. RFC 6840 bu testi ayrıntılandırmıyor, yalnız "insist that all algorithms signaled in the DS RRset work" diyor. Test yalnız DNSKEY RRset'inde yapılsaydı, K1-04/06/11 hücrelerinde Z_10 ile sahte A kabul edilir ve değer SALDIRI olurdu. "work" fiili algoritmanın doğrulama yolunda çalışmasını ifade ettiği için ilk okumayı seçtim (BELIRSIZ.md §B).

## 2. KAT-2 X.509 hibrit

### 2.1 Semantik ve sözlük eşlemesi

**Birincil kaynaklar:**
- Kim vd. (`kim2026_x509_hybrid.txt`): §II-B tasarımlar, §III saldırganlar M1/M2, §IV-B politikalar P0–P3, §IV-D beş gözlem sonucu, Tablo IV/V/VI/VII.
- Lee vd. (`lee2026_eprint1416.txt`): §4.1, §4.3, §4.4, §6.

**Sonuç sözlüğü.** Kim iki sözlük kullanıyor:
- **gözlem:** classical-accept, hybrid-verified, loud-fail, identified-but-not-enforced,
- **sözleşme:** accept-classical, accept-hybrid, reject, indeterminate (s. 130).

Değer sözlüğü sözleşme sözlüğüdür. Gözlemi sözleşmeye şöyle eşledim [Y]:
- classical-accept ve identified-but-not-enforced → `accept_classical`. Dayanak s. 130: "a contract result of accept-classical is a statement that such an acceptance is all the policy permits us to report". Şekil 1'in varsayılan yol oku da "→ Accept-classical ✓" diyor (s. 364).
- hybrid-verified → `accept_hybrid`.
- loud-fail → `reject`. Dayanak s. 101: "cannot parse or process the structure and rejects".

**`vb` değerleri (girdi §3(b) eşlemesi) ve kaynak davranışları:**

| vb | Politika | Kaynaktaki davranış |
|---|---|---|
| `ignore` | P0 | classical-accept (Kim s. 102) |
| `parse_no_enforce` | P0 | identified-but-not-enforced (Kim s. 103, s. 296) |
| `enforce_if_present` | P1 | wolfSSL tipi: varsa doğrular, gerekli kılamaz (Lee s. 121; Kim §VI-D s. 306) |
| `require` | P2 | "both classical and post-quantum evidence must be present and valid" (Kim s. 90) |
| `continuity` | P3 | "an identity previously established as hybrid may not silently regress to classical-only" (Kim s. 90). Girdi §1.1 eşlemesi P3'ü `monotone=1`'e bağlıyor |
| `legacy_oid` | — | composite OID'sini tanımayan doğrulayıcı → loud-fail (Kim s. 43, s. 101; Lee s. 99 "each rejects the others’ OID") |

**Saldırganlar:**
- **M1 (saklama):** "It cannot forge a classical signature … so every certificate it presents was issued by a real authority" (Kim s. 60). Yalnız "presents a legitimately issued classical-only certificate … and withholds the post-quantum one" (s. 66).
- **M2 (CRQC):** "can forge RSA or ECDSA signatures, including a certification authority’s, but not a post-quantum signature such as ML-DSA" (s. 61).

**Kapsam.** Girdi §1.1'e göre çapa CA→ee'dir: "yalnız uç varlık kapsamı; Kim'in test kapsamı". Bu yüzden Kim s. 444'teki uyarı bu hücrelerde işlemiyor: "if a classical issuer signature is forgeable, post-quantum evidence at the leaf alone does not establish hybrid authentication". Ara CA yok; CA'nın alternatif (PQ) açık anahtarı çapa yapılandırmasının parçasıdır [Y].

### 2.2 KAT-2a: dürüst karar (saldırgan yok; `hon_decision`)

`KAT-2a-01/02` gibi satır etiketleri tek tek hücre kimliklerine açıldı: 01 = ilk `pqev` değeri, 02 = ikinci değer. 09…11 ve 12…14 = valid / invalid / absent.

| Hücre | scheme, vb, pqev | Kural | Karar |
|---|---|---|---|
| K2a-01 | catalyst, ignore, valid | Klasik yol doğrulanır, PQ kanıtına bakılmaz (s. 102) | accept_classical |
| K2a-02 | catalyst, ignore, invalid | "In all 27 the two verdicts were identical" (s. 238); Lee §4.3 aynı (s. 99) | accept_classical |
| K2a-03 | catalyst, parse_no_enforce, valid | IBNE: "does not let the evidence affect the outcome" (s. 103); kabul klasik kanıta dayanır (s. 241) | accept_classical |
| K2a-04 | catalyst, parse_no_enforce, invalid | "in each the invalidated variant was accepted exactly as the valid one was" (s. 296) | accept_classical |
| K2a-05 | chameleon, ignore, valid | Tablo IV Chameleon satırı: 8 yığının 6'sında C-Acc. Lee s. 128: "its non-critical delta likewise ignored" | accept_classical |
| K2a-06 | chameleon, ignore, invalid | 25 kabul hücresinde geçersiz varyant aynı koşulla kabul edildi (s. 239). NSS'nin "Unsup" hücresi bilgi vermeyen hücredir (girdi §3(a)); `ignore` semantiği bunu değiştirmez | accept_classical |
| K2a-07 | related, ignore, leafB valid | Tablo V kontrol satırı, varsayılan yol classical-accept (s. 324, 386) | accept_classical |
| K2a-08 | related, ignore, leafB revoked | "revoking that certificate changes no verdict" (s. 29); Tablo V (s. 386) | accept_classical |
| K2a-09 | catalyst, enforce_if_present, valid | Zorlayan derleme "accepts a valid alternative signature" (s. 306); Tablo VI P1 geçerli sütunu accept-hybrid | accept_hybrid |
| K2a-10 | catalyst, enforce_if_present, invalid | Lee s. 121: "does verify a present alt-signature – a leaf with a forged ML-DSA alternative signature is rejected"; Kim s. 306 "rejects a forged one" | reject |
| K2a-11 | catalyst, enforce_if_present, absent | Lee s. 121: "a stripped classical-only leaf … is accepted"; Kim s. 445: P1 yokluğu tolere eder | accept_classical |
| K2a-12 | catalyst, require, valid | P2 tanımı (s. 90); Tablo VI P2 geçerli sütunu accept-hybrid | accept_hybrid |
| K2a-13 | catalyst, require, invalid | Tablo VI P2: "non-accepting: reject, or indeterminate if status is unknown" (s. 429). Durum bilinmezliği yok → reject | reject |
| K2a-14 | catalyst, require, absent | "Reject is returned when a required certificate is invalid or absent" (s. 443) | reject |
| K2a-15 | composite, require, valid | Composite'te kanıt tek imzanın içindedir ve kararı etkiler (s. 437); Tablo VII; Tablo IV BC composite = HV | accept_hybrid |
| K2a-16 | composite, require, invalid | Lee s. 99: "corrupting either the ML-DSA or the classical component … is rejected" | reject |
| K2a-17 | composite, legacy_oid, valid | "does not recognize the algorithm identifier and fails to process the certificate" (s. 43); loud-fail reddeder (s. 101); Tablo IV composite satırı 8 yığının 7'sinde LF | reject |

**Yorum kararları (2a):**

1. **K2a-10: reject.**
   - Kim Tablo VI, P1'in "invalid, absent, or unsupported" sütunu için "accept-classical permitted; never accept-hybrid" diyor. Bu okumayla değer accept_classical olurdu.
   - Reject'i seçtim, çünkü: (i) hücrenin `vb` adı zorlamayı söylüyor, Kim'in "outcome-bearing" tanımı da "a failure in it would turn an otherwise accepting result into a non-accepting one" (s. 97); (ii) Kim'in P1 tanımı yalnız yokluğu tolere ediyor: "check … when it is present, tolerate its absence" (s. 90); (iii) bu davranışı gösteren doğrulayıcı ölçümde reddediyor (Lee s. 121, Kim s. 306).
   - Tablo VI'daki "permitted" izin kipidir; reddi yasaklamaz ("never accept-hybrid" koşulu reddetmekle de sağlanır).
   - Risk BELIRSIZ.md §B'de.
2. **K2a-17.** `legacy_oid` "composite OID'sini tanımayan (eski) doğrulayıcı" olarak okundu. Farklı bir composite OID ailesi okumasında da sonuç aynı, çünkü Lee s. 99'a göre aileler "each rejects the others’ OID". Değer iki okumada da reject.
3. **Geçerli/geçersiz eşleşmesi.** Kim'in varsayılan yoldaki bulgusu gözlemdir. Modeldeki `ignore` ve `parse_no_enforce` davranış tanımları aynı sonucu yapısal olarak verir (s. 54: "a verifier can complete classical path validation without processing the post-quantum evidence").

### 2.3 KAT-2b: M2 (CRQC ile sahteleme)

- **Kanıt sınıfları:** Catalyst CA anahtarı = klasik temel imza + PQ alternatif imza. Composite anahtar `comp` sınıfındadır; yalnız bütün bileşenleri kırılırsa kırılır (girdi §1.1). CRQC ML-DSA'yı kırmaz.
- **`coexist_cl=1`:** Aynı kimlik için doğrulayıcının güvendiği, ayrı bir klasik yol da var [Y]. Örnek: geçiş döneminde paralel klasik CA ya da klasik sertifika.
- **`expect_src`:** `local` = yerel P2. `tl_cl` / `tl_pq` = beklentiyi klasik / PQ anahtarla imzalı bir TL taşır (girdi §1.1 politika eşlemesi: "P3 (kaynak klasik) / P4 (kaynak PQ)").

| Hücre | Durum | Kural | ASP | Tamarin `cert_authentic` |
|---|---|---|---|---|
| K2b-01 | catalyst, anyvalid (P0) | M2 CA'nın klasik imzasını sahteler, "can construct certificates that validate classically without any authority having issued them" (Kim s. 61). P0 PQ'ya bakmaz | SALDIRI | falsified |
| K2b-02 | catalyst, allpresent (P1) | M2, alternatif uzantısı olmayan salt klasik bir yaprağı sahte CA imzasıyla kurar. "a stripped classical-only leaf … is accepted" (Lee s. 121); P1 yokluğu tolere eder (Kim s. 445) | SALDIRI | falsified |
| K2b-03 | catalyst, required, local | P2 geçerli PQ alternatif imzası ister; M2 "not a post-quantum signature such as ML-DSA" (Kim s. 61). Çapa CA→ee olduğundan çıkaranın alternatif açık anahtarı sahtelenemez | YOK | verified |
| K2b-04 | catalyst, required, tl_cl | Beklentiyi taşıyan TL klasik imzalı. M2 onu sahteler ve beklentiyi siler [Y]. Kural boş kalır ve durum K2b-01'e indirgenir. Kim s. 433–434: P3'ün riski "depends on where that state comes from" | SALDIRI | (ASP-yalnız) |
| K2b-05 | catalyst, required, tl_pq | TL PQ imzalı ve sahtelenemez (Kim s. 61). Beklenti gerçek; durum K2b-03'e indirgenir | YOK | (ASP-yalnız) |
| K2b-06 | composite, anyvalid, coexist 0 | "There is no path through which it accepts while disregarding the post-quantum component" (Kim s. 43). `comp` kırılmaz, klasik yol yok | YOK | verified |
| K2b-07 | composite, anyvalid, coexist 1 | Paralel klasik yol M2 ile sahtelenir, anyvalid tek yolu yeterli sayar. Lee s. 272: "no encoding alone defeats a full classical downgrade"; s. 173: "Composite included" | SALDIRI | falsified |
| K2b-08 | composite, required, local, coexist 1 | Lee s. 78: "no encoding prevents without a require-PQC policy". Burada o politika var: klasik yol reddedilir, composite sahtelenemez | YOK | (ASP-yalnız) |

**Yorum kararları (2b):**

1. **K2b-04/05.** TL sürümlü değil (girdi §1.1: `version` KAT-2'de "—"). Bu yüzden eski TL'yi yeniden oynatma yolu yok.
   - Saldırganın TL'yi tamamen düşürmesi (TL'siz doğrulama) modelde beklentiyi silmenin tek yolu değil. Doğrulayıcı TL'siz kalırsa ne yapar? Girdi bunu söylemiyor.
   - `tl_pq` için YOK değeri şu varsayıma dayanıyor: sinyal ancak kaynağı sahtelenerek kaldırılabilir [Y].
2. **Tamarin satırları.** `(ASP-yalnız)` hücrelere Tamarin satırı yazılmadı.

### 2.4 KAT-2c: Related, leafB durumu × {ignore, require}

Doğrudan Kim Tablo V'den okundu (s. 374–398). Tabloda satırlar (s. 384) ile sütunlar (s. 386, 388) sütun sütun dökülmüş; hizalama s. 393–398'deki dipnotlarla doğrulandı.

| leafB | vb=ignore (varsayılan yol) | vb=require (P2 referansı) | Dayanak |
|---|---|---|---|
| revoked | accept_classical | reject | Tablo V; s. 443 "revoked, expired, or not presented" |
| expired | accept_classical | reject | aynı |
| unknown (OCSP) | accept_classical | indeterminate | s. 327: "returns indeterminate; treating unknown as a rejection would assert a status the verifier does not have" |
| absent | accept_classical | reject | s. 327: "An absent peer certificate leaves a required certificate missing, so the procedure rejects" |
| valid (kontrol) | accept_classical | accept_hybrid | s. 324–326: varsayılan yol klasik kabul eder; "The policy rules return a hybrid result for that row" |

- Varsayılan yol sütununun "classical-accept" gözlemi `accept_classical` olarak yazıldı (bkz. 2.1).
- Değişmezlik: "the default verdict does not change with leafB’s state" (s. 322).

### 2.5 KAT-2d: P0–P3, M1 saklaması

**Kanıt durumu.** Hücrede `pqev` verilmemiş. Durumu "PQ kanıtı saklandı (absent)" olarak yorumladım [Y], iki gerekçeyle:
- `seen_hybrid` ancak kanıt yokken kararı değiştirebilir. Kanıt geçerliyse P1–P3'ün hepsi accept-hybrid verir (Tablo VI) ve `seen_hybrid` anlamsızlaşır.
- Girdi §3(a), KAT-2d için Kim'in M1 cümlesini alıntılıyor (s. 445).

| Hücre | Politika | Kural | ASP karar | Tamarin |
|---|---|---|---|---|
| K2d-01 | P0 | "P0 (legacy): classical path validation only" (s. 89). Tablo VI P0 iki sütunda da accept-classical | accept_classical | belirsiz |
| K2d-02 | P1 | "Under M1, P1 provides no more protection than P0 … the result is accept-classical" (s. 445) | accept_classical | belirsiz |
| K2d-03 | P2 | "Reject is returned when a required certificate is invalid or absent … or not presented" (s. 443); Tablo VI P2 | reject | belirsiz |
| K2d-04 | P3, seen_hybrid=1 | "a later accept-classical for an identity recorded as hybrid-required is itself non-accepting" (s. 429). Saklanan kanıt "not presented" → reject (s. 443) | reject | (ASP-yalnız) |
| K2d-05 | P3, seen_hybrid=0 (ilk temas) | P3 tanımı: "an identity previously established as hybrid may not silently regress" (s. 90). Önceden hibrit kurulmuş kimlik yoksa geri dönüş de yok → klasik kabul [Y] | accept_classical | (ASP-yalnız) |

**Yorum kararları (2d):**

1. **K2d-05.** Kim Tablo VI'nın P3 satır başlığı "P3 (hybrid + continuity)". Bu başlık, P3'ün P2'yi içerdiği biçiminde de okunabilir; o okumada ilk temasta da reject çıkar.
   - Accept_classical'ı şu gerekçelerle seçtim:
     - girdi §1.1 eşlemesi P3'ü yalnız tekdüzelik bileşenine bağlıyor (`monotone=1`; KAT-1'de `required`'dan bağımsız bir bayrak);
     - Kim'in §IV-B tanımı yalnız geri dönüşü yasaklıyor;
     - Tablo VI notu P3'ün harici bir süreklilik durumu varsaydığını söylüyor ("presupposes an external continuity state", s. 431), §VIII-D de P3 koşulunu "an identity the inventory records as hybrid-required" ile sınırlıyor (s. 452).
   - Risk BELIRSIZ.md §B'de.
2. **K2d Tamarin (01–03) belirsiz.** Değer sözlüğü KAT-2b için lemmayı adlandırıyor (`cert_authentic`), KAT-2d için adlandırmıyor. Girdi §1.4'e göre KAT-2 dosyasında iki aday var: bir kimlik doğrulama lemması (all-traces) ve bir duyarlılık lemması (exists-trace). Adaylar farklı sonuç veriyor (BELIRSIZ.md §A1).


## 3. KAT-3 S/MIME

Birincil kaynak: Das ve Chattopadhyay (`das2026_smime_eprint1374.txt`) §3 ve §3.1.

**Temel kurallar:**
- **Denklem (8)** (s. 149): Accept(ED, P_t) = 1 ⟺ ∀i ∈ R, V_i(t) = 1 ⇒ χ_i(t) ∈ A_t.
  - V_i sertifika geçerliliğidir ve "policy constraints"i de kapsar (s. 142).
  - Yalnız geçerli yollar sınıflanır: "Assign each valid CEK path to …" (Şekil 3, s. 181).
- **Aşama 3, yol sınıfları** (s. 190):
  - ML-KEM (onaylı OID) → PQC.
  - Tanınan hibrit KEM → "Hybrid only when the policy explicitly permits the construction".
  - RSA KeyTrans ve ECDH KeyAgree → Classical.
  - "Unsupported OIDs … are classified as Unknown".
  - "mandatory profile violations are classified as Invalid".
  - "Unknown mechanisms fail closed".
- **Aşama 4, kipler** (s. 191):
  - strict-PQC: A_t = {PQC}.
  - transitional-hybrid: A_t = {PQC, onaylı Hybrid}, ama "still rejects an independent standalone classical fallback to the same CEK".
- **Aşama 5, öncelik** (s. 205): "malformed artifacts are rejected as invalid; unsafe mixed-mode exposure is reported before weaker uncertainty labels; and unknown mechanisms fail closed".
- **Tablo 1** (s. 199–203): altı mesaj sınıfının tanımı.

### 3.1 KAT-3a: literal CMS sınıflaması (o1…o12)

**`out` hangi kipte hesaplanıyor?** Hücrede tek bir `out` sütunu var.
- Sınıfı Tablo 1 tanımlarından okudum. Hibrit KEM'in onaylı olup olmadığını vektör etiketi söylüyor ("(onaylı)" / "(onaysız)") [Y].
- Kabul sütunları Denklem (8)'i iki kipin A_t kümesiyle uygular.

| Vektör | Yol sınıfları (geçerli yollar) | `out` (kural) | strict | transitional |
|---|---|---|---|---|
| o1 | PQC | pqc_protected (Tablo 1: "Every valid recipient path to the CEK is classified as PQC") | 1 | 1 |
| o2 | PQC, PQC | pqc_protected | 1 | 1 |
| o3 | Classical | classical_only (Tablo 1) | 0 | 0 (Classical ∉ A_t) |
| o4 | PQC, Classical | unsafe_mixed (Tablo 1: "At least one valid PQC or hybrid path coexists with at least one independent valid classical path") | 0 (s. 162) | 0 ("still rejects an independent standalone classical fallback") |
| o5 | Hybrid (onaylı) | hybrid_protected (Tablo 1) | 0 (strict yalnız PQC) | 1 |
| o6 | Hybrid, Classical | unsafe_mixed (hibrit onaylı sayıldı [Y]) | 0 | 0 |
| o7 | PQC, Unknown | unknown (Aşama 3 "Unsupported OIDs … Unknown"; Tablo 1 unknown; pqc-protected "no … unknown fallback path" ister) | 0 | 0 (fail closed) |
| o8 | PQC (rsa_kt yolu V=0, kapsam dışı) | pqc_protected (Denklem (8)'in V_i ⇒ koşulu; Tablo 1 "valid" yollardan söz eder) | 1 | 1 |
| o9 | ayrıştırılamaz | invalid (Aşama 5: "malformed artifacts are rejected as invalid"; Aşama 1: "rejects malformed objects") | 0 | 0 |
| o10 | Hybrid değil (onaysız) → Unknown | unknown (Aşama 3 "Hybrid only when the policy explicitly permits"; fail closed) | 0 | 0 |
| o11 | PQC, Hybrid (onaylı) | hybrid_protected (pqc-protected "no … hybrid … fallback" ister) | 0 (s. 205: "only when every valid CEK-recovery path is positively classified as PQC") | 1 |
| o12 | Classical, Classical | classical_only | 0 | 0 |

**Yorum kararları (3a):**

1. **o8 yazıldığı gibi.** Das'ın kuralına göre geçersiz sertifikalı yol (V=0) değerlendirme dışıdır → pqc_protected, 1, 1.
   - Girdideki okuma notu bu vektörü bir "model farkı" olarak işaretliyor: CRQC sahibi saldırgan RSA RecipientInfo'dan CEK'i sertifika geçerliliğinden bağımsız çıkarabilir (Önerme 1'in RecoverCEK'i V_i'ye bakmaz).
   - Bu fark ayrıca raporlanacak. Beklenen değer Das'ın literal kuralıdır.
   - "invalid" sınıfı (Tablo 1: "violates a mandatory … certificate … requirement") o8'e uygulanmadı, çünkü Das sertifika geçerliliğini yol sınıflamasından açıkça ayırıyor (s. 143: "We separate certificate validity from recipient-path classification").
2. **o10 → unknown.** Onaysız hibrit, Aşama 3'e göre Hybrid sınıfına girmez. Das hangi sınıfa gireceğini açıkça yazmıyor.
   - "Unsupported … are classified as Unknown" ve "fail closed" en yakın kural; "invalid" yalnız zorunlu profil ihlali ve bozuk yapı içindir.
   - Kabul değerleri (0, 0) iki okumada da aynı; yalnız `out` değişebilir (BELIRSIZ.md §B).
3. **o6'daki hibrit onaylı sayıldı.** Etiket yok. o6, o4'ün hibrit karşılığı ve transitional kipin "standalone classical fallback" cümlesini sınıyor; bu sınamanın anlamlı olması için hibritin onaylı olması gerekir.
   - Onaysız olsaydı yol kümesi {Unknown, Classical} olurdu ve `out` unknown çıkardı. Kabul değerleri iki durumda da 0.
4. **o9 kabul değerleri.** Bozuk nesnede Denklem (8)'in ∀ niceleyicisi boş kümede boşuna doğru olurdu. Ancak Aşama 1 nesneyi politika değerlendirmesinden önce reddeder → kabul 0.

### 3.2 KAT-3a Tamarin `cek_secrecy`

Tamarin kalıbında `rule Qday` ve `Break_*` kuralları var (girdi §1.4). CRQC anı her izde gelebilir; tehdit Das §3'teki HNDL saldırganıdır (s. 127).

| Bayrak | Yapılandırma [Y] | Kural | Değer |
|---|---|---|---|
| MIXED | ML-KEM + RSA/ECDH alıcısı aynı CEK'e | Önerme 1 (s. 159): "the confidentiality level of ED is bounded by the weakest valid recipient path protecting K"; klasik yol CRQC ile açılır | falsified |
| PQ_ONLY | yalnız ML-KEM | Tek yol PQC; CRQC ML-KEM'i kırmaz | verified |
| HYBRID_KEM | yalnız hibrit KEM (ECDH + ML-KEM) | Tablo 1 hybrid-protected. Birleştirilmiş sırrı elde etmek iki bileşeni de gerektirir [Y]; RFC 9955 §1.3.1'deki "provided that a least one component … remains 'secure'" ilkesinin KEM benzeşimi | verified |

**Yorum:** HYBRID_KEM bayrağının tek başına (klasik yol eklenmeden) koşulduğu varsayıldı. Klasik bir yolla birlikte koşulsaydı o6'ya denk gelir ve değer falsified olurdu.

### 3.3 KAT-3b: kimlik doğrulama ikiliği (V1…V6)

**Semantik** (girdi §1.1, KAT-3 sütunu) [Y]:
- `tl_class`: TL'yi imzalayan çapa anahtarının (`ktl`) sınıfı.
- `expect=1`: TL, ihraççı için "pq_required" sinyalini taşır.
- `coexist=1`: TL, ihraççının PQ anahtarının yanında klasik bir anahtarını da tanıtır.
- TL çekilen, kimlik bilgisi aktarılan türdedir. Saldırgan sahte TL sunabilir (ağ konumu).

**Das kuralının ikiliği.** Bir kimlik bilgisine giden yol, ktl → TL → ihraççı anahtarı → kimlik bilgisi zinciridir. Yolun sınıfı en zayıf halkasıdır; Önerme 1'in ikiliği [Y]. Yolun "geçerli" olması, doğrulayıcının o yolu kabul etmesi demektir: V_i "policy constraints"i içerir (s. 142). PQ imzalı bir kaynaktan gelen beklenti, klasik ihraççı anahtarıyla giden yolu geçersiz kılar.

- **Statik `violation`:** P = {PQ} altında Denklem (8) ihlali, yani klasik halka içeren bir geçerli yol var.
- **Dinamik `attack(qday=0)`:** Bütün klasik anahtarlar kırık (girdi sözlüğü). Kırık bir halkayla sahte kimlik bilgisi kabul ettirilebilir mi?
  - Kırık halka TL ise saldırgan sahte TL ile kendi anahtarını tanıtır. Girdi §2(c) Not: "Saldırgan kendi anahtarını üretebilir".
  - Kırık halka ihraççının klasik anahtarıysa saldırgan kimlik bilgisini doğrudan sahteler.
- **`attack(qday=200)`:** CRQC yok. Hiçbir klasik imza sahtelenemez → her hücrede YOK.

| V | tl_class, expect, coexist | Zayıf halka | attack(qday=0) | violation | attack(qday=200) | Tamarin `claims_unforgeability` |
|---|---|---|---|---|---|---|
| V1 base | cl, 0, 1 | ktl (C) ve ihraççı C anahtarı | SALDIRI | 1 | YOK | falsified |
| V2 expectTL | cl, 1, 1 | ktl (C). Beklenti klasik kaynaktan geliyor; sahte TL onu siler ya da saldırgan anahtarını tanıtır | SALDIRI | 1 | YOK | falsified |
| V3 tlPQ | pq, 0, 1 | ihraççı C anahtarı. TL gerçek ama beklenti yok | SALDIRI | 1 | YOK | falsified |
| V4 tlPQ_expectTL | pq, 1, 1 | yok. Gerçek TL'deki beklenti, C anahtarlı yolu geçersiz kılar (V_i = 0) | YOK | 0 | YOK | verified |
| V5 tlPQ_nocoexist | pq, 0, 0 | yok. Bütün halkalar PQ | YOK | 0 | YOK | verified |
| V6 tlClassical_nocoexist | cl, 0, 0 | ktl (C). Sahte TL saldırganın anahtarını tanıtır | SALDIRI | 1 | YOK | falsified |

**Dayanaklar:**
- Das s. 157: "a single classical recipient path remains enough to expose the protected content if that path can recover K". Kimlik doğrulamada karşılığı: tek bir klasik yol sahteleme için yeter.
- Önerme 1 (s. 159).
- Denklem (8) (s. 149).
- Qday'li Tamarin izi, qday=0 durumuna denk gelir (girdi §1.4).

**Eşdeğerlik:** Statik `violation` ile dinamik `attack(qday=0)` her V'de aynı yönde. Bu, KAT-3'ün sınadığı "statik politika denetimi ile dinamik saldırı aramasının eşdeğerliği" varsayımıyla tutarlı.

**Yorum kararları (3b):**
1. **V4'te `violation=0`.** Bu değer, statik denetimin beklentiyi bir politika kısıtı olarak hesaba kattığı varsayımına dayanıyor. Das s. 142'ye göre V_i bu kısıtı içerir.
   - Statik denetim beklentiyi görmeden yalnız yapısal yolları sayarsa (TL, C anahtarını da tanıtıyor), V4'te violation=1 çıkar ve eşdeğerlik bozulur (BELIRSIZ.md §B).
2. **Doğrulayıcı politikası.** `expect=0` iken doğrulayıcının herhangi bir geçerli yolu kabul ettiği (anyvalid) varsayıldı. Girdide KAT-3b için `pol` verilmemiş. Pilotun altı yapılandırmasının adları (base / expectTL / tlPQ …) beklentinin tek sıkılaştırıcı olduğunu gösteriyor [Y].

## 4. Özet sayılar

- **KAT-1:** 15 hücre, 30 satır (ASP + Tamarin).
- **KAT-2:** 40 hücre, 48 satır.
  - 2a: 17 hücre, 17 satır.
  - 2b: 8 hücre, 13 satır (5 Tamarin).
  - 2c: 10 hücre (5 leafB × 2 vb), 10 satır.
  - 2d: 5 hücre, 8 satır (3 Tamarin).
- **KAT-3:** 21 hücre, 63 satır.
  - 3a: 12 vektör × 3 = 36 satır.
  - `cek_secrecy`: 3 hücre, 3 satır.
  - 3b: 6 × 4 = 24 satır.
- **Toplam:** 141 veri satırı. `belirsiz`: 3 satır (K2d-01/02/03 Tamarin).

## 5. Kesinti ve denetim notu

- **Oturum 1 (24.09.2026):** KAT-1'in 30 satırı ile bu dosyanın §0–§1 bölümleri yazıldı. Kullanım limiti oturumu ~20:14'te kesti.
- **Oturum 2 (25.09.2026):** KAT-1 satırları yeniden türetilmedi, yalnız denetlendi. Ardından KAT-2, KAT-3, `BELIRSIZ.md` ve `SHA256SUMS` yazıldı.
- **Alıntı denetimi:** 141 satırın hepsinde `alinti` alanı, `kaynak` alanında adı geçen ilk birincil dosyada ve `satir` aralığında birebir geçiyor. Boşluklar normalleştirildi. Betik: oturum geçici klasöründeki `alinti_denetle.py`; yalnız metin karşılaştırması yapar. Sonuç: **hatalı 0**.
- KAT-1'de hata bulunmadı; düzeltme yapılmadı.
- Metin içi satır atıfları örneklem olarak `grep -n` ile doğrulandı (Kim s. 54, 97, 241, 324, 326, 364, 396, 431, 452; Das s. 143, 162, 181; RFC 6781 s. 1477, 1558, 1584, 1894; RFC 6840 s. 446, 570, 1027).
