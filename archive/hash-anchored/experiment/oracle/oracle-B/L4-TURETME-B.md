# L4 ORACLE'ININ BAĞIMSIZ TÜRETİLMESİ — Oracle B

> **Görev:** ÖK Ö6: "**L4 oracle'ı:** Doğrudan bir normatif madde yok. Oracle 8725bis §3.1 + composite AND + G5 tanımından türetilir. N-sürüm oracle bu türetmeyi bağımsız yapar." (`ON-KAYIT-TASLAK.md:173`)
> **Yazan:** Oracle B, 25.09.2026. Oracle A'nın çalışması görülmedi (`ERISIM-KAYDI.md`).
> **Kaynak metinler** (`spec-corpus/metin/`, SHA-256'lar `YONTEM.md` §8): 8725bis = draft-ietf-oauth-rfc8725bis-10 (`JWTBCP.txt`); composite = draft-ietf-jose-pq-composite-sigs-04 (`JOSECOMP.txt`); RFC 7515; RFC 9901; ECCG ACM v2.0 (`ACM2.txt`); ÖK v0.8 (`ON-KAYIT-TASLAK.md`, SHA-256 `dcc84092…`).
> Aşağıdaki alıntılar kaynak satırlardan birebir kopyalanmıştır (satır sonu tireleri birleştirildi). Aynı alıntıların kısa biçimleri `turet_karar.py` tarafından kaynakta otomatik doğrulanır.

---

## 0. Kapsam ve bir bağımsızlık notu

- Türetmenin konusu: bir JOSE/SD-JWT doğrulayıcısının, **ihraççı başına** yapılandırılmış bir politika altında, tek ya da çok imzalı bir belgeyi **kabul mü ret mi** edeceği; kabulse **klasik mi hibrit (PQ bileşenli)** kanıta dayandığı.
- G5 için birincil tanım ÖK §4.7'dir (aşağıda Ö-8). ÖK §2D madde 10'daki "G5-zamansız / G5-zamanlı / G5-göç" adları okunan parçada göründü; bu türetme onların **sonuçlarını** kullanmaz, yalnız §5'te zaman boyutunu tartışırken adlarını anar.

## 1. Öncüller (birebir alıntılar)

**Ö-1 — 8725bis §3.1, izin kümesi (kütüphane yükümlülüğü)** (`JWTBCP.txt:463-466`; matris T327):
> "Libraries MUST provide a mechanism that enables developers to explicitly restrict the set of algorithms permitted for use and MUST NOT employ any algorithms outside this configured set when performing cryptographic operations."

**Ö-2 — 8725bis §3.1, anahtar–algoritma tutarlılığı** (`JWTBCP.txt:468-471`; T329):
> "The library MUST verify that the algorithm specified in the "alg" or "enc" header parameter is consistent with the algorithm associated with the key identified by the corresponding identifier (e.g., "kid") during key lookup."

**Ö-3 — 8725bis §3.1, ihraççı başına izinli algoritmalar (alıcı yükümlülüğü)** (`JWTBCP.txt:482-485`; T328):
> "When a recipient receives a JWT signed by a particular issuer, it MUST determine which algorithms are permitted for itself and that issuer and ensure that the received JWT complies with those requirements."

**Ö-4 — 8725bis §3.1, bir anahtar tek algoritma** (`JWTBCP.txt:488-491`):
> "In accordance with established cryptographic best practices, each key MUST be used with exactly one algorithm. Compliance with this requirement MUST be enforced and validated at the time the cryptographic operation is executed."

**Ö-5 — composite -04 §4.3, bileşen AND'i** (`JOSECOMP.txt:452-453`; T345) ve doğrulama adımları (`JOSECOMP.txt:489`, `497-502`):
> "The Verify algorithm MUST validate a signature only if all component signatures were successfully validated."
> "If Error during deserialization, or if any of the component keys or signature values are not of the correct type or length for the given component algorithm then output "Invalid signature" and stop."
> "if NOT ML-DSA.Verify(mldsaPK, M', ctx=Label) / output "Invalid signature" / if NOT Trad.Verify(tradPK, M') / output "Invalid signature" / if all succeeded, then / output "Valid signature""

**Ö-6 — composite -04 §6.1 ve §6.3, AND'in amacı** (`JOSECOMP.txt:1020-1026`, `1075-1077`; T347):
> "By requiring the successful verification of both the ML-DSA component and the traditional component, this construction ensures: [...] *Dual-Algorithm Security:* An adversary that compromises only one of the component algorithms cannot produce cryptographically protected JOSE/COSE objects as long as the other component remains secure."
> "*Cross-Algorithm Prevention:* The unique label, specific to each composite algorithm, ensures that signatures cannot be removed from the composite and used in other contexts."

**Ö-7 — ACM v2 Note 51, birleştirilmiş imzalarla hibritleme** (`ACM2.txt:946`; T135):
> "For digital signatures, hybridization can consist in concatenating signatures from diﬀerent schemes, the veriﬁcation function accepting if and only if all signatures are correct."

**Ö-8 — G5 tanımı, ÖK §4.7** (`ON-KAYIT-TASLAK.md:767`):
> G5 | downgrade direnci: "Göç etmiş bir varlık, ilan ettiği eski-sürüm penceresi dışında yalnız klasik kanıtla kabul edilemez." | ∀ E #j #m. AcceptClassicalOnly(E)@j ∧ Migrated(E)@m ∧ m < j ⇒ LegacyWindowOpen(E) j anında

**Ö-9 — RFC 7515 §5.2, çoklu imzada karar uygulamanındır** (`RFC7515.txt:810-816`; T314, T315):
> "When there are multiple JWS Signature values, it is an application decision which of the JWS Signature values must successfully validate for the JWS to be accepted. In some cases, all must successfully validate, or the JWS will be considered invalid. In other cases, only a specific JWS Signature value needs to be successfully validated. However, in all cases, at least one JWS Signature value MUST successfully validate, or the JWS MUST be considered invalid."

**Ö-10 — RFC 7515 §4.1.1, desteklenmeyen alg geçersizdir** (`RFC7515.txt:508-511`; T319):
> "The JWS Signature value is not valid if the "alg" value does not represent a supported algorithm or if there is not a key for use with that algorithm associated with the party that digitally signed or MACed the content."

**Ö-11 — ÖK'nin politika ve ölçüt maddeleri:**
- §6.5 (`:1048`, `:1054`): "Birinci imza A = ES256." — "İhraççı başına gerekli küme R = {X}, izinli küme {A, X}."
- §4.13 L4 (`:844`): "\"Gerekli algoritma kümesi\" semantiği: PQ bileşeni yoksa ret | PQ'ya özgü | Yapılandırılmış hâlde K1 KABUL, K2 RED, K3 RED (§6.5)"
- §4.8 P1 (`:776`): "P1 | all-present-valid | ECCG AND | Mevcut imzaların tümü geçerliyse kabul. İmza silinmesi (soyma) fark edilmez"; P3 (`:778`): "P2 + ihraççı başına gerekli küme R_I".
- §2B m.6 (`:255-256`): L4m "PQ bileşeni yoksa ret."; L4c "Aynı doğrulayıcı örneğinde, belgelenmiş API ile **ihraççı başına** "PQ/composite zorunlu" politikası. Göç etmiş ihraççının yalnız klasik imzalı belgesi reddedilir, eski ihraççının klasik imzalı belgesi kabul edilir."

**Ö-12 — Kapsam köprüsü (SD-JWT):** RFC 9901 §7.1 (2a) (`RFC9901.txt:1663-1665`; T103): "Ensure that the used signing algorithm was deemed secure for the application. Refer to [RFC8725], Sections 3.1 and 3.2 for details." — 8725bis §3.1 SD-JWT ihraççı imzasına doğrudan uygulanır. 8725bis'in kendisi JWT'nin kompakt olduğunu hatırlatır (§2.13, `JWTBCP.txt:446-447`: "While JWTs must use the Compact Serialization"); çok imzalı General JSON JWS'ye §3.1 ancak **uzatılarak** uygulanır (bkz. §9, sınırlılık S1).

## 2. Türetme (adım adım)

Gösterim: bir belge D, imza kümesi S(D) = {s₁ … sₙ} (n ≥ 1) taşır; her s için alg(s), anahtar k(s). İhraççı I için doğrulayıcı yapılandırması (Perm_I, R_I).

**A1 — Politikanın nesnesi ihraççıdır.** Ö-3 "permitted for itself and that issuer" der: izin kümesi ihraççıya göre belirlenir. ÖK §6.5 bunu somutlar: Perm_I = {A, X}, A = ES256. → *Kural 1:* Doğrulayıcı her ihraççı için ayrı bir (Perm_I, R_I) tutar.

**A2 — İzin kümesi dışındaki imza doğrulanmaz, dolayısıyla geçerli değildir.** Ö-1: kütüphane yapılandırılan küme dışındaki algoritmayı **kullanamaz** ("MUST NOT employ"). Ö-10: desteklenmeyen/kullanılamayan alg için imza "not valid". → *Kural 2:* alg(s) ∉ Perm_I ⇒ s geçersiz. (Etiket harfe duyarlıdır: RFC 7515 §4.1.1 "The "alg" value is a case-sensitive ASCII string"; 8725bis §2.11 büyük/küçük harf saldırısı.)

**A3 — Anahtar–algoritma bağlaması.** Ö-2 ve Ö-4: alg(s), k(s)'nin bağlı olduğu algoritmayla tutarlı olmalı; bir anahtar tek algoritmayla kullanılır (RFC 9864 §7 de aynı: "A cryptographic key MUST be used with only a single algorithm"; AKP anahtarında `alg` zorunlu, RFC 9964 §3). → *Kural 3:* alg(s) ≠ alg(k(s)) ⇒ s geçersiz. Bu bir **kütüphane** yükümlülüğüdür; hiçbir yapılandırma onu kapatamaz (K10 her yapılandırmada ret).

**A4 — Composite imzanın geçerliliği bileşenlerin AND'idir.** Ö-5: composite imza ancak iki bileşen de geçerliyse geçerlidir; seri çözme hatası, yanlış tür/uzunluk "Invalid signature"dır. → *Kural 4:* composite s geçerli ⇔ ML-DSA bileşeni (M′, ctx = Label üzerinde) ∧ klasik bileşen (M′ üzerinde) geçerli ∧ kodlama doğru.

**A5 — Belge düzeyinde AND (tüm-mevcut-geçerli).** Ö-9'a göre çoklu imzada hangi imzaların geçerli olması gerektiği **uygulamanın kararıdır**; RFC 7515 bunu belirlemez, yalnız "en az bir" alt sınırı koyar. Karar üç öncülle bağlanır:
- Ö-7 (ACM v2): imzaları birleştirerek hibritlemede doğrulama "accepting if and only if all signatures are correct".
- Ö-5/Ö-6: composite, aynı AND'i bileşen düzeyinde zorlar; amacı, tek bileşeni kıran saldırganın nesne üretememesidir.
- Ö-11 (ÖK §4.8): P1 = "all-present-valid", karşılığı "ECCG AND"; P3 = P2 + R_I = P1 + bağlama + R_I (kümülatif).
→ *Kural 5:* L4'te **S(D)'deki her imza** Kural 2–4 anlamında geçerli olmalıdır. Aksi hâlde ret. (Sonuç: K2 — X imzası bozuk — **ret**; K5 — tanınmayan alg'li ek imza — **ret**; bkz. §6.)

**A6 — G5, gerekli kümeyi (R_I) zorunlu kılar.** Kural 5 tek başına soymayı durdurmaz: X imzası silinmiş belgede (K3) kalan tek imza A geçerlidir, yani "mevcut tümü geçerli"dir. ÖK §4.8 bunu açıkça yazar: P1'de "İmza silinmesi (soyma) fark edilmez". Ö-8 (G5): göç etmiş bir varlık, eski-sürüm penceresi dışında **yalnız klasik kanıtla** kabul edilemez. K3'teki belge göç etmiş ihraççıdandır ve yalnız klasik kanıt (ES256) taşır → G5 kabulü yasaklar. Kabulü yalnız klasik kanıta indirgenemeyecek biçimde sınırlamanın en küçük yapılandırma ifadesi, ihraççının PQ algoritmasını **gerekli** kılmaktır: R_I = {X}, X ∈ PQ. Bu, ÖK §6.5'teki "İhraççı başına gerekli küme R = {X}" ile ve Ö-3'teki "ensure that the received JWT complies with those requirements" ile örtüşür (ihraççının gereksinimi artık "X imzası olmalı"dır).
→ *Kural 6:* ∀ x ∈ R_I ∃ s ∈ S(D): alg(s) = x ∧ s geçerli. Aksi hâlde ret.

**A7 — Birleşik L4 kuralı.**

```
L4(D; Perm_I = {A, X}, R_I = {X}) = KABUL  ⇔  n ≥ 1
                                            ∧ ∀ s ∈ S(D): alg(s) ∈ Perm_I ∧ alg(s) = alg(k(s)) ∧ geçerli(s)      [Kural 2–5]
                                            ∧ ∀ x ∈ R_I ∃ s ∈ S(D): alg(s) = x ∧ geçerli(s)                       [Kural 6]
                                   aksi hâlde RET
```

**A8 — Dört değerli çıktı.** KABUL ise, kabulün dayandığı geçerli imzalar arasında PQ sınıfı bir bileşen (ML-DSA ya da composite) varsa `accept-hybrid`, yoksa `accept-classical`. Maddeler kabul/ret arasında karar vermiyorsa `indeterminate` (§7). Kontrol kolunda X = EdDSA klasiktir; Kural 6 orada G5'i değil, **aynı API semantiğini** sınar (ÖK §3.7: "L4, kontrol kolunda ölçülür (ikinci algoritma EdDSA). Böylece API yeteneği PQ desteğinden ayrılır."). Bu yüzden kontrol kolundaki L4 kabulleri `accept-classical`'dır.

**A9 — ÖK §4.13 ölçütüyle tutarlılık denetimi.** Kural A7, dört kolun hepsinde ÖK'nin L4 davranış ölçütünü ("K1 KABUL, K2 RED, K3 RED") verir (§3 tablosu). Ölçüt kuraldan **türetildi**, kurala girdi olarak verilmedi.

## 3. L4m — çoklu imza biçimi (General JSON)

L4m (ÖK §2B m.6: "Belgelenmiş API ile ve kod değiştirmeden 'gerekli algoritma kümesi' semantiği. PQ bileşeni yoksa ret.") A7'nin çok imzalı belgelere doğrudan uygulanmasıdır. İmza sırası karara girmez (RFC 7515 §5.2 adım 9: "repeat this process (steps 4-8) for each digital signature or MAC value"; §7.2.1 her imzayı kendi başlığıyla hesaplar) → MR4 eşleri kaynaklarıyla aynı kararı alır.

Birincil vakalar (karar.tsv'den; `acc-cl` = accept-classical, `acc-hy` = accept-hybrid; P2 ve P0 karşılaştırma için):

| Vaka | Kol | Vektör | L4 | P2 | P0 |
|---|---|---|---|---|---|
| K1 | K-EdDSA | `T1K_both_valid` | acc-cl | acc-cl | acc-cl |
| K1 | K-Ed25519 | `T1K_both_valid-ED25519` | acc-cl | acc-cl | acc-cl |
| K1 | T-ML-DSA-65 | `T1P_both_valid` | acc-hy | acc-hy | acc-hy |
| K1 | T-composite | `T1C_both_valid` | acc-hy | acc-hy | acc-hy |
| K2 | K-EdDSA | `T2K_second_tampered` | reject | reject | acc-cl |
| K2 | K-Ed25519 | `T2K_second_tampered-ED25519` | reject | reject | acc-cl |
| K2 | T-ML-DSA-65 | `T2P_second_tampered` | reject | reject | acc-cl |
| K2 | T-composite | `T2C_second_tampered` | reject | reject | acc-cl |
| K3 | dört kol | `T3_stripped_to_ES256` | reject | acc-cl | acc-cl |
| K4 | K-EdDSA | `T5K_only_EdDSA` | acc-cl | acc-cl | acc-cl |
| K4 | K-Ed25519 | `T5K_only_EdDSA-ED25519` | acc-cl | acc-cl | acc-cl |
| K4 | T-ML-DSA-65 | `T5P_only_ML-DSA-65` | acc-hy | acc-hy | acc-hy |
| K4 | T-composite | `T5C_only_ML-DSA-65-ES256` | acc-hy | acc-hy | acc-hy |
| K5 | K-EdDSA | `T7K_plus_kayitsiz` | reject | reject | acc-cl |
| K5 | K-Ed25519 | `T7K_plus_kayitsiz-ED25519` | reject | reject | acc-cl |
| K5 | T-ML-DSA-65 | `T7P_plus_kayitsiz` | reject | reject | acc-hy |
| K5 | T-composite | `T7C_plus_kayitsiz` | reject | reject | acc-hy |

Okuma: L4 ile P2 yalnız **K3'te** ayrışır (soyma; Kural 6). P2 ile P0 **K2 ve K5'te** ayrışır (Kural 5). Bu üç sütun, B5'in "gerekli-küme / mevcut-tümü-geçerli / en-az-biri-geçerli" sınıflarının ayırt edici imzasıdır: K1–K3 üçlüsü sırasıyla (KABUL, RED, RED) / (KABUL, RED, KABUL) / (KABUL, KABUL, KABUL).

## 4. L4c — yalnız kompakt serileştirme

Kompakt JWS tek imza taşır (RFC 7515 §7.1: "Only one signature/MAC is supported by the JWS Compact Serialization"). n = 1 iken A7 şuna indirgenir:

```
L4c(D; I) = KABUL ⇔ alg(s₁) ∈ Perm_I ∧ alg(s₁) = alg(k(s₁)) ∧ geçerli(s₁) ∧ (R_I = ∅ ∨ alg(s₁) ∈ R_I)
```

L4c'nin iki yarısı **aynı doğrulayıcı örneğinde iki ihraççıdır** (Ö-3 "for itself and that issuer"; ÖK §2B m.6):

| İhraççı | Yapılandırma | Oracle kodu | Yalnız klasik (ES256) belge | X imzalı belge |
|---|---|---|---|---|
| Göç etmiş (pencere kapalı) | R_I = {X}, Perm_I = {A, X} | `L4` | **reject** (G5) | kabul (`accept-hybrid` tedavide, `accept-classical` kontrolde) |
| Eski (göç etmemiş) | R_I = ∅, Perm_I = {A, X} | `P2` (n = 1'de ≡ `P0`) | **accept-classical** | kabul |

Bataryadaki karşılıkları: `VPLUS_ES256` (dört kol; `L4` → reject, `P2` → accept-classical), `VPLUS_EdDSA`, `VPLUS_ML-DSA-65`, `CMP00_gecerli_referans` (X imzalı; üç yapılandırmada kabul), `VMINUS_*` (her yapılandırmada reject), `VC10_ikili_ihrac` (K11: kompakt SD-JWT VC'nin klasik kopyası; `L4` → reject, `P2` → accept-classical). L4c'nin davranış ölçütü, bir hedefin aynı örnekte bu iki satırı birlikte üretip üretemediğidir (ÖK §2B m.6: "eski ihraççının klasik imzalı belgesi kabul edilir").

## 5. Zaman boyutu (G5'in "eski-sürüm penceresi")

G5'in öncülü LegacyWindowOpen(E)'dir: pencere açıkken klasik kabul **serbesttir**. Kütüphane düzeyinde pencere, yapılandırmanın kendisiyle ifade edilir: pencere açık → ihraççı için R_I = ∅ (`P2`); pencere kapalı → R_I = {X} (`L4`). C3 bataryası sabit bir `simdi` kullanır ve pencere parametresi taşımaz; ÖK §6.5 K3/K11 kararları (RED) **penceresi kapanmış** göç etmiş ihraççıyı varsayar. Oracle bu varsayımı `L4` satırlarında uygular, `P2` satırları açık pencereye karşılık gelir. (ÖK §2D m.10'daki G5 biçimlerinin adları bu ayrımı çağrıştırır; sonuçları kullanılmadı.)

## 6. Diğer vakalar L4 altında

| Vaka | L4 kararı | Belirleyen öncül |
|---|---|---|
| K5 (`T7*`, kayıtsız ek imza) | reject | Kural 2 (X-KAYITSIZ-1 ∉ Perm_I, anahtar yok) + Kural 5 (AND). P0'da kabul → MR2'nin beklediği politika bağımlılığı |
| K5 ikincil (`T4*`, `T6`, `UNK04/05`: izinli olmayan gerçek ek imza) | reject | Kural 2 + 5 (ek imza doğrulanamaz; AND bozulur) |
| K6 (`CMP00`) | accept-hybrid | Kural 4 (iki bileşen geçerli) + Kural 6 |
| K7 (`CMP01/02`; ikincil CMP03–04, 06–11, 16) | reject | Kural 4 (bileşen/kodlama/M′/ctx hatası → "Invalid signature") |
| K8 (`X5C04`, ML-DSA kolu) | accept-hybrid | Kural 6 JWS imzasını kısıtlar; zincir RFC 5280'e göre geçerli. §6.5 politikası zincir kenarlarını kısıtlamaz → yol sınıfı B2 ile raporlanır |
| K9 (`X5C07`) | reject | L4'ten değil anahtar çözümlemeden: RFC 7515 §6 + SD-JWT VC -13 §3.5 (korumasız x5c güven kararına giremez) |
| K10 (tüm yönler) | reject | Kural 3 (Ö-2, Ö-4); yapılandırmadan bağımsız |
| K11 (`VC10` klasik kopya) | reject | Kural 6 (G5) |
| V+ `VPLUS_ES256` | reject | Kural 6. ÖK §4.15 V+ için KABUL bekler → V+ denetimi `P2`'de koşulmalı (NOTLAR N2) |

## 7. Maddelerin belirlemediği durumlar (→ `indeterminate`)

L4 kuralı kabul yolu bıraktığında bile şu durumlarda maddeler kararı belirlemez (ayrıntı ve satır listesi `BELIRSIZ.md`):
1. Çok imzalı SD-JWT+KB'de `sd_hash`'in hangi imzaya bağlandığı (RFC 9901 §8.1; ÖK §2D m.4).
2. SD-JWT VC -19'da JSON serileştirilmiş biçimin ayrıntıları kapsam dışı (SD-JWT VC -19 §2.2).
3. `typ` geçişi (VC11): -13 kabulü yalnız RECOMMENDED; -19'da doğrulayıcı `typ` denetimi yalnız RECOMMENDED.
4. `crit` içinde kayıtlı ad / boş liste: doğrulayıcıya yalnız MAY.
5. Güven çapasının x5c içinde olması: HAIP'te üreticiye MUST NOT, doğrulayıcıya kural yok.
6. x5c ile başka anahtarı gösteren kid birlikte: anahtar çözümleme önceliği tanımsız.
7. Asgari olmayan DER (composite ECDSA bileşeni): katı DER reddi doğrulayıcıya açıkça yüklenmemiş; hedef EUF-CMA.
8. DPoP nonce/ath bağlamı verilmemiş.
9. İmzasız OID4VP isteği ile göç etmiş RP beklentisi: HAIP "MUST support unsigned" ile G5 çelişir.

## 8. P0–P4 ve B5 ile ilişki

| ÖK §4.8 | Kütüphane düzeyinde | Oracle kodu | B5 sınıfı |
|---|---|---|---|
| P0 any-valid | + zorunlu bağlama (Kural 3) | `P0` | en-az-biri-geçerli |
| P1 all-present-valid | bağlamasız P1 uyumlu kütüphanede yok → P1 ≡ P2 | `P2` | mevcut-tümü-geçerli |
| P2 = P1 + bağlama | | `P2` | mevcut-tümü-geçerli |
| P3 = P2 + R_I (klasik kanal) | R_I'nin kanalı kütüphanenin dışında → P3 ≡ P4 | `L4` | gerekli-küme |
| P4 = P3 (PQ kanal; M-f) | | `L4` | gerekli-küme |

## 9. Türetmenin sınırları ve alternatif okumalar

- **S1 — JWT → JWS uzatması.** 8725bis §3.1 JWT'ler içindir; JWT kompakttır (§2.13). General JSON çok imzalı JWS'ye (senaryo d) uygulanması bir uzatmadır. Gerekçe: SD-JWT (RFC 9901 §7.1 2a) 8725bis §3.1'e atıf yapar ve RFC 9901 §8 JSON serileştirmeyi tanımlar; ÖK §6.5 senaryo (d)'yi "spesifikasyon dışı" diye etiketler.
- **S2 — AND mi, "yalnız gerekli küme" mi?** Kural 5'in alternatifi, R_I karşılandığında izinli olmayan ek imzaları **yok saymaktır** ("gerekli küme, fazlası serbest"). Bu okumada K5 ve K5 ikincilleri L4'te **kabul** olurdu; K1–K4 değişmezdi. Bu türetme AND'i seçti, çünkü (i) ÖK §4.8 P3'ü P1'in (ECCG AND) üstüne kümülatif tanımlar, (ii) ACM v2 hibritlemede "all signatures are correct" der, (iii) 8725bis §3.1 alıcıdan belgenin ihraççının gereksinimlerine "comply" etmesini ister ve izinli olmayan algoritmalı bir imza taşıyan belge bu gereksinime uymaz. Seçim `KARAR-NOTLARI.md` N4'te işaretlendi; oracle A başka okursa ayrışma K5'te beklenir ve "belirsiz" sınıfına girer.
- **S3 — "accept-hybrid" adı.** Saf PQ kabulü (K4 tedavi) de `accept-hybrid` sayıldı (ÖK'de dört değerin semantiği yok; N1).
- **S4 — Zincir sınıfı.** `accept-hybrid` yalnız JWS katmanını sınıflar; sertifika yolundaki klasik kenarlar (K8) ayrıca B2 ile raporlanır.
