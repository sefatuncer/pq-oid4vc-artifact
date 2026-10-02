# L4 oracle'ının türetilmesi (ÖK Ö6) — Oracle A

> **Görev (ÖK Ö6, satır 173):** "**L4 oracle'ı:** Doğrudan bir normatif madde yok. Oracle 8725bis §3.1 + composite AND + G5 tanımından türetilir. N-sürüm oracle bu türetmeyi bağımsız yapar."
> **ÖK §4.20 (satır 940):** "Oracle, 8725bis §3.1'in PQ/composite ile birleşimidir."
> Satır numaraları `spec-corpus/metin/<BELGE>.txt` ve `00-on-kayit/ON-KAYIT-TASLAK.md` (v0.8, SHA-256 `dcc84092…`) dosyalarına aittir. Her alıntı `karar_uret.py` tarafından metinde bulunarak doğrulanır (`maddeler.tsv`).
> Oracle B'nin türetmesi görülmedi.

## 1. Öncüller (birebir)

**8725bis-10 §3.1 (JWTBCP)**
- **Ö1** [T327] (s.463–466): "Libraries MUST provide a mechanism that enables developers to explicitly restrict the set of algorithms permitted for use and MUST NOT employ any algorithms outside this configured set when performing cryptographic operations."
- **Ö2** [T328] (s.482–485): "When a recipient receives a JWT signed by a particular issuer, it MUST determine which algorithms are permitted for itself and that issuer and ensure that the received JWT complies with those requirements."
- **Ö3** [T329] (s.468–471): "The library MUST verify that the algorithm specified in the "alg" or "enc" header parameter is consistent with the algorithm associated with the key identified by the corresponding identifier (e.g., "kid") during key lookup."
- **Ö4** (s.488–491): "each key MUST be used with exactly one algorithm. Compliance with this requirement MUST be enforced and validated at the time the cryptographic operation is executed."
- **Ö5** 8725bis §3.3 (s.565–567): "All cryptographic operations used in the JWT MUST be validated and the entire JWT MUST be rejected if any of them fail to validate. This is true of JWTs with a single set of Header Parameters."

**composite -04 (JOSECOMP)**
- **Ö6** §4.3 [T345] (s.452–453): "The Verify algorithm MUST validate a signature only if all component signatures were successfully validated."
- **Ö7** §6.1 (s.1020–1030): "By requiring the successful verification of both the ML-DSA component and the traditional component, this construction ensures: … *Impersonation Prevention:* … even if the traditional signature component is compromised."

**G5 (ÖK §4.7)**
- **Ö8** (s.767): "Göç etmiş bir varlık, ilan ettiği eski-sürüm penceresi dışında yalnız klasik kanıtla kabul edilemez."
- G5'in üç biçimi var (ÖK §2D m.10). Biri **G5-göç** (s.447): "göçten sonra, ilk temas da dahil, yalnız klasik kanıtla kabul yok".

**Bağlayıcı çerçeve**
- **Ö9** RFC 7515 §5.2 [T314, T315] (s.810–816): "When there are multiple JWS Signature values, it is an application decision which of the JWS Signature values must successfully validate for the JWS to be accepted. … However, in all cases, at least one JWS Signature value MUST successfully validate, or the JWS MUST be considered invalid."
- **Ö10** RFC 7515 §5.2 son paragraf [T316] (s.892–895): "Even if a JWS can be successfully validated, unless the algorithm(s) used in the JWS are acceptable to the application, it SHOULD consider the JWS to be invalid."

**ÖK tanımları**
- **Ö11** §6.5 (s.1054): "İhraççı başına gerekli küme R = {X}, izinli küme {A, X}."
- **Ö12** §4.13 L4 (s.844): "'Gerekli algoritma kümesi' semantiği: PQ bileşeni yoksa ret … Yapılandırılmış hâlde K1 KABUL, K2 RED, K3 RED (§6.5)".
- **Ö13** §2B m.6 (s.255–257): L4m "PQ bileşeni yoksa ret" ve L4c "Göç etmiş ihraççının yalnız klasik imzalı belgesi reddedilir, eski ihraççının klasik imzalı belgesi kabul edilir". "Y_i = L4m (hedef çoklu imzayı destekliyorsa), aksi hâlde L4c."
- **Ö14** §4.8 (s.775–779):
  - P1 "Mevcut imzaların tümü geçerliyse kabul. İmza silinmesi (soyma) fark edilmez";
  - P3 "P2 + ihraççı başına gerekli küme R_I".
- **Ö15** ECCG ACM v2 Not 51 [T135] (s.946): "the veriﬁcation function accepting if and only if all signatures are correct".

## 2. Neden tek bir kaynak L4'ü vermez?

| Tek başına kaynak | Ne verir | Neden L4 değil |
|---|---|---|
| 8725bis §3.1 (Ö1–Ö4) | İzin listesi (L1/L2), ihraççı başına izinli küme ve alg–anahtar bağlama (L3) | "complies with those requirements" (Ö2) gereksinimin **içeriğini** söylemez. İzin kümesi {A, X} olan bir doğrulayıcı yalnız A ile imzalı nesneyi (K3) kabul eder, yine de Ö1–Ö4'e uyar |
| composite AND (Ö6) | **Tek bir** composite imzanın içinde iki bileşenin birlikte doğrulanması (K7) | JWS düzeyinde imza kümesinden söz etmez. composite imza bütünüyle soyulursa (K3) Ö6 hiç devreye girmez |
| G5 (Ö8) | Güvenlik hedefi: göç etmiş varlık yalnız klasik kanıtla kabul edilemez | Bir doğrulayıcı kuralı değildir. "Göç etmiş" bilgisinin (R_I) doğrulayıcıya nasıl ulaştığı kütüphane düzeyinin dışında kalır (P3/P4 kanalı) |
| P1 / ECCG AND (Ö14, Ö15) | Mevcut her imza geçerli olmalı | ÖK'nin kendi notu: "İmza silinmesi (soyma) fark edilmez". K3 kabul edilir |
| RFC 7515 §5.2 (Ö9) | Asgari kural: en az bir imza geçerli (P0) | Hangi imzaların gerektiğini uygulamaya bırakır |

**Sonuç.** L4, bu kaynakların **birleşimidir**. G5, Ö2'deki "gereksinim"in içeriğine bir PQ taşıyan algoritmayı zorunlu olarak koyar. Ö1 ve Ö3 bu gereksinimin algoritma ve anahtar düzeyinde nasıl uygulanacağını belirler. Ö6, composite X'in "geçerli" sayılması için PQ bileşeninin de geçerli olmasını sağlar.

## 3. Türetme

İhraççı I göç etmiş olsun ve eski-sürüm penceresi `simdi` anında kapalı olsun. Batarya zaman boyutlu beklenti taşımaz; oracle pencerenin kapalı olduğunu varsayar (§7).

1. **Gereksinimin içeriği (Ö2 + Ö8).**
   - Ö8'e göre I'nin yalnız klasik kanıtla sunulan nesnesi kabul edilemez.
   - Ö2'ye göre doğrulayıcı "itself and that issuer" için izinli algoritmaları belirlemek ve nesnenin bunlara uyduğunu sağlamak zorundadır.
   - O hâlde I için gereksinim şunu içermelidir: **en az bir PQ taşıyan algoritma X mevcut ve geçerli olmalı.**
   - Bu, ÖK'nin gerekli kümesidir: R_I ⊇ {X}. §6.5 politikası bunu R = {X} olarak sabitler (Ö11).
2. **İzin kümesi (Ö1).** W_I = {A, X}. W dışındaki bir algoritma kriptografik işlemde kullanılamaz.
3. **Anahtar–alg bağlama (Ö3, Ö4; RFC 7515 §5.2 adım 8; RFC 9864 §7 [T335]).** Her imza, başlığındaki alg ile ve o alg'a bağlı anahtarla doğrulanır. Uyuşmazlık o imzayı geçersiz kılar (K10).
4. **composite içi AND (Ö6).**
   - X = ML-DSA-65-ES256 ise "X geçerli" ⇔ ML-DSA bileşeni geçerli **ve** ECDSA bileşeni geçerli (K6, K7). Böylece R_I'nin karşılanması PQ bileşeninin doğrulanmasını kesin olarak içerir (Ö7).
   - X = ML-DSA-65 ise bu zaten doğrudan PQ'dur.
5. **Hangi imzaların doğrulanacağı (Ö9).** RFC 7515 bunu uygulamaya bırakır; L4 bunu şöyle sabitler: **R_I'deki her algoritma için mevcut ve geçerli bir imza bulunmalı.** Buradan:
   - K1 (A + X, ikisi geçerli) → kabul;
   - K2 (X bozuk) → R karşılanmaz → **red**;
   - K3 (X soyulmuş) → R karşılanmaz → **red**;
   - K4 (yalnız X) → kabul.

   Bunlar Ö12'deki davranışsal ölçütün (K1 KABUL, K2 RED, K3 RED) ta kendisidir.
6. **Diğer imzalar (Ö5, Ö10).**
   - W içindeki ve kullanılan imzalar geçerli olmalıdır (Ö5: "All cryptographic operations used … MUST be validated").
   - W **dışındaki** ek imzalar için kaynaklar iki okumaya izin verir. ÖK de K5'i "Politikaya göre (MR2)" diye açık bırakır (s.1062):
     - **S (sıkı):** Ö10 + Ö14 (P3 ⊇ P1) + Ö15. Mevcut her imza W içinde ve geçerli olmalı → K5 **red**.
     - **Y (yok say):** Ö9 + Ö1. W dışındaki imza kullanılmaz ve nesneyi düşürmez → K5, K1 ile aynı karar.

**L4 karar fonksiyonu.** Bir nesnenin imza kümesi Σ olsun; her σ ∈ Σ için alg(σ) ve geçerlilik g(σ) verilsin.

```
L4-S(Σ) = KABUL  ⇔  ∀σ∈Σ: alg(σ)∈W  ∧  ∀σ∈Σ: g(σ)=geçerli  ∧  ∀x∈R: ∃σ∈Σ: alg(σ)=x ∧ g(σ)=geçerli
L4-Y(Σ) = L4-S(Σ ∩ {σ : alg(σ)∈W})          (Σ ∩ W boşsa RED; RFC 7515 §5.2 "at least one")
L4(Σ)   = L4-S(Σ)  eğer L4-S(Σ) = L4-Y(Σ);  aksi hâlde indeterminate  (yalnız W dışı ek imza varsa ayrışır)
```

Geçerlilik üç değerlidir (geçerli / geçersiz / belirsiz). Kesin bir başarısızlık her zaman reddir. Kesin başarısızlık yoksa ve karar belirsiz bir imzaya bağlıysa sonuç `indeterminate` olur (`YONTEM.md` §3).

## 4. Dört değerli çıktı (ÖK Ö6, s.171)

"Kim vd.'nin politika-parametrik sözleşmesi" ayrımı **kabulün neye dayandığıdır.** Oracle A'nın tanımı:
- `accept-hybrid` ⇔ kabul **ve** yapılandırmaya uygun her kabul yolu geçerli bir PQ bileşeninin doğrulanmasını gerektirir.
- `accept-classical` ⇔ kabul **ve** yalnız klasik imzaların doğrulanması kabul için yeterlidir.

L4 altında R = {X} olduğu için:
- X PQ taşıyorsa (ML-DSA-65, ML-DSA-65-ES256) her kabul `accept-hybrid`'dir;
- kontrol kollarında (X = EdDSA / Ed25519) her kabul `accept-classical`'dır.

Kontrol kolu L4'ü **API yeteneği** olarak ölçer, PQ desteğinden bağımsız (ÖK §3.7).

**Karşıtlık (Kim tarzı çift):** Aynı T1P nesnesi
- P1 altında `accept-hybrid` (mevcut her imza doğrulanmak zorunda),
- P0 altında `accept-classical` (ES256 tek başına yeterli).

Soyulmuş T3 ise P0 ve P1 altında `accept-classical`, L4 altında `reject`. "Klasik kabul ≠ hibrit kimlik doğrulama" farkı bu üç satırda görünür.

## 5. K1–K11 ve V± kararları (L4 ailesi; `karar.tsv`'den üretildi)

| Vaka | Kol | Vektör | L4 | L4-S | L4-Y | Ek |
|---|---|---|---|---|---|---|
| K1 | kontrol-EdDSA | `T1K_both_valid` | accept-classical | accept-classical | accept-classical |  |
| K1 | tedavi-ML-DSA-65 | `T1P_both_valid` | accept-hybrid | accept-hybrid | accept-hybrid |  |
| K1 | tedavi-composite | `T1C_both_valid` | accept-hybrid | accept-hybrid | accept-hybrid |  |
| K2 | kontrol-EdDSA | `T2K_second_tampered` | reject | reject | reject |  |
| K2 | tedavi-ML-DSA-65 | `T2P_second_tampered` | reject | reject | reject |  |
| K2 | tedavi-composite | `T2C_second_tampered` | reject | reject | reject |  |
| K3 | üç kol | `T3_stripped_to_ES256` | reject | reject | reject |  |
| K4 | kontrol-EdDSA | `T5K_only_EdDSA` | accept-classical | accept-classical | accept-classical |  |
| K4 | tedavi-ML-DSA-65 | `T5P_only_ML-DSA-65` | accept-hybrid | accept-hybrid | accept-hybrid |  |
| K4 | tedavi-composite | `T5C_only_ML-DSA-65-ES256` | accept-hybrid | accept-hybrid | accept-hybrid |  |
| K5 | kontrol-EdDSA | `T7K_plus_kayitsiz` | indeterminate | reject | accept-classical |  |
| K5 | tedavi-ML-DSA-65 | `T7P_plus_kayitsiz` | indeterminate | reject | accept-hybrid |  |
| K5 | tedavi-composite | `T7C_plus_kayitsiz` | indeterminate | reject | accept-hybrid |  |
| K6 | tedavi-composite | `CMP00_gecerli_referans` | accept-hybrid | accept-hybrid | accept-hybrid |  |
| K7 | tedavi-composite | `CMP01_ml_bileseni_bozuk` (CMP02 aynı) | reject | reject | reject |  |
| K8 | ML-DSA-65, composite (uyarlanmış) | `X5C04_karisik_pq_yaprak_klasik_ara` | accept-hybrid | accept-hybrid | accept-hybrid | L4-YOL: reject → B2 |
| K9 | ML-DSA-65, composite (uyarlanmış) | `X5C07_korumasiz_x5c` | reject | reject | reject | kabul eden hedefte B3 = 1 |
| K10 | kontrol / ML-DSA / composite | `K10K_…`, `K10P_…`, `K10C_…` (her kolda iki yön) | reject | reject | reject | IZIN-AX (L3) altında da reject |
| K11 | üç kol | `VC10_ikili_ihrac` (credentials[0]) | reject | reject | reject | IZIN-AX (eski ihraççı) altında accept-classical |
| V+ | her kol | `VPLUS_ES256` / `VPLUS_X` | GEC: accept / accept | | | L4: reject / accept (L4c-göç) |
| V− | her kol | `VMINUS_ES256` / `VMINUS_X` | GEC: reject / reject | | | |

Bütün hücreler ÖK §6.5 tablosuyla (s.1058–1069) uyuşuyor:
- K1 KABUL, K2 RED, K3 RED, K4 KABUL;
- K5 "Politikaya göre": iki alt yapılandırmada belirli;
- K6 KABUL, K7 RED;
- K8 "Bayrak B2": L4'te kabul, L4-YOL'da red;
- K9 "Bayrak B3", K10 RED (L2/L3), K11 RED (G5);
- V+ KABUL, V− RED.

## 6. L4m ve L4c (ÖK §2B m.6)

**L4m (çoklu imza; General JSON'u destekleyen hedef).**
- Hedefin belgeli API'si §3'teki fonksiyonu yapılandırmayla uygulayabiliyorsa L4m vardır. Ölçüt: `L4` (ya da `L4-S`/`L4-Y`) satırlarında K1 kabul, K2 red, K3 red.
- K5 davranışı hangi alt yapılandırmaya uyduğunu gösterir: B1 ve B5.

**L4c (yalnız kompakt).**
- Aynı doğrulayıcı örneğinde ihraççı başına politika gerekir. Oracle satırları:

| Ölçüt | Vektör × yapılandırma | Oracle |
|---|---|---|
| Göç etmiş ihraççının yalnız klasik belgesi RED | `VPLUS_ES256` × L4; `VC10_ikili_ihrac` × L4 (K11); `VC01_ES256_x5c` × L4 | reject |
| Göç etmiş ihraççının X imzalı belgesi KABUL | `VPLUS_X`, `CMP00`, `VC02`, `VC03` × L4 | accept-* |
| Eski ihraççının klasik belgesi KABUL | `VPLUS_ES256`, `VC01`, `VC10` × IZIN-AX | accept-classical |

- **Batarya sınırı:** v1.2'de ayrı bir "eski ihraççı" kimliği yok. Tek `iss` (`https://issuer.example`) ve tek ES256 ihraççı anahtarı (issuer/ES256) var. "Aynı doğrulayıcı örneğinde" iki ihraççı kaydı yalnız aynı baytların iki ayrı politika kaydıyla değerlendirilmesiyle sınanabilir (`adaptor-sozlesme.md` §5.3; NOTLAR N-2).

## 7. G5'in zaman boyutu ve sınırlar

- **Pencere varsayımı:** Oracle, L4 ailesinde "eski-sürüm penceresi kapalı" varsayar. Pencere açık olsaydı klasik kanıt kabul edilebilirdi; bu durum `IZIN-AX` (R = ∅) satırlarına denk düşer. Batarya sunset ya da tarih içeren bir beklenti taşımadığı için G5-zamanlı biçim kütüphane bataryasında sınanmaz. Bu biçim Adım 7 ve 11'in konusudur.
- **Kanal (P3 ↔ P4):** R_I'nin hangi kanaldan öğrenildiği vektörde temsil edilmez. Kütüphane düzeyinde P3 ile P4 aynı kararı verir. Adaptör R_I'yi API ile sabitler (sabitlenmiş çıpa gibi).
- **Sertifika yolu:** L4 imza düzeyindedir. x5c yolunun PQ olması ayrı bir politikadır (`L4-YOL`, B2). Dayanağı ÖK §2D m.13 `yol_sinifi` ve composite -04 §6.2 [T055]: "Because the certificate itself is protected by a composite signature, an attacker cannot forge a fake certificate…".
- **KB-JWT:** L4 ihraççı imzası politikasıdır. General JSON'da çoklu ihraççı imzasıyla KB `sd_hash` bağlaması tanımsızdır (BELIRSIZ B-2).

## 8. Metamorfik ilişkiler (oracle üzerinde öz-denetim; `karar_ozet.json` → `mr_oz_denetim`)

| İlişki | Oracle'da tutuyor mu? | Sayı |
|---|---|---|
| **MR1** (gerekli küme karşılanmıyorsa soyma kabulü artırmamalı) | L4, L4-S, L4-Y altında 4 kolda T1 → kabul, T3 → red | 12/12 |
| **MR2** (bilinmeyen alg eklemenin etkisi öngörülebilir) | S altında T7 → red; Y altında T7 = T1 | 4/4 kol |
| **MR3** (sürüm değişince karar değişiyorsa işaretle) | VC07, VC08, VC09 ve VC09-ED25519: -13 ve -19'da aynı (`L4` / `L4@-19`; JSON desteği varsayımıyla). VC01 ↔ VC11: -13'te ikisi de accept-classical; -19'da VC11 reject (SHOULD düzeyi). Beklenen "sürüm etkisi" budur | 6 vektör |
| **MR4** (imza sırası kararı değiştirmemeli) | Karar fonksiyonu sıradan bağımsız. 165 (permütasyon, yapılandırma, kol) satırı kaynak vektörle aynı. VP05-SIRA-ters MR4 dışıdır (tanımlayıcı; sd_hash bağlaması değişir) | 165/165 |
