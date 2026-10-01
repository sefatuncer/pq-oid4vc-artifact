# Oracle A — `indeterminate` kararlarının nedenleri

> **Kapsam:** `karar.tsv`'de `karar = indeterminate` olan **75 satır** altı nedene ayrılır. Bunların yalnız **4'ü birincildir**: B-1 kapsamında temel `L4` yapılandırmasındaki T7K, T7K-ED25519, T7P ve T7C. Bu dördü `L4-S` ve `L4-Y` alt yapılandırmalarında belirlidir.
> **Kural:** Madde + inşa gerçekleri kararı belirlemiyorsa `indeterminate` yazıldı. Oracle A tahmin yürütmedi ve iki okumadan birini seçmedi. Her grup için şunlar verilir: iki okuma, hangi maddelerin çatıştığı ve belirsizliği neyin giderebileceği.
> Satır listelerini yeniden üretmek için: `karar.tsv` satırları `karar == "indeterminate"` ile süzülür, `not` sütunundaki anahtar sözcüğe göre gruplanır.

## B-1. İzin kümesi dışında ek imza (ÖK §6.5 K5, "politikaya göre") — 32 satır, 4 birincil

**Vektörler:**
- T7K/T7P/T7C (`X-KAYITSIZ-1`) ve T7K-ED25519;
- T4K/T4P/T4C, T6 ve bunların Ed25519 eşleri;
- UNK04 (`ML-DSA-65-P256`), UNK05 (`none`);
- bu vektörlerin bütün MR4 permütasyonları.

Yalnız `L4` yapılandırmasında belirsizdir. Örnek T7P (ML-DSA kolu):

| Okuma | Dayanak | Karar |
|---|---|---|
| **S (sıkı):** mevcut her imza W içinde ve geçerli olmalı | ÖK §4.8 P3 = P2 + R_I, P2 ⊇ P1 ("Mevcut imzaların tümü geçerliyse kabul"); ECCG ACM v2 Not 51 [T135] "the veriﬁcation function accepting if and only if all signatures are correct"; RFC 7515 §5.2 [T316] "unless the algorithm(s) used in the JWS are acceptable to the application, it SHOULD consider the JWS to be invalid" | `reject` |
| **Y (yok say):** W dışı imza kullanılmaz; R ve W içindekiler geçerliyse kabul | RFC 7515 §5.2 [T314] "it is an application decision which of the JWS Signature values must successfully validate"; 8725bis §3.1 [T327] "MUST NOT employ any algorithms outside this configured set" (dışarıdaki algoritma doğrulamada kullanılmaz, nesneyi düşürmesi gerekmez) | `accept-hybrid` (kontrol kolunda `accept-classical`) |

**Neden madde belirlemiyor?**
1. ÖK §6.5 K5 satırı kararı açıkça politikaya bırakıyor: "Politikaya göre (MR2); bayrak B1".
2. RFC 7515 §5.2'deki "algorithm(s) used in the JWS" ifadesi iki biçimde okunabilir: mevcut her imza mı, yoksa uygulamanın dayandığı imzalar mı? Metin bunu ayırmıyor.
3. §6.5 politikası ("R = {X}, izinli {A, X}") P3'ün P1 bileşenini açıkça anmıyor.

**Nasıl kullanılır?**
- Adım 10'da hedefin belgeli semantiği hangi okumaya uyuyorsa (S ya da Y) K5 onunla karşılaştırılır. B1 bu sınıfı kaydeder.
- İki okumaya da uymayan davranış **MR2 ihlalidir**. Örnek: T7'de `accept-classical` (PQ imza doğrulanmadan kabul) ya da T1 kabul edilirken T7'de istisna.
- F_K/F_T yalnız K1–K3'ten hesaplandığı için (ÖK §6.4) B-1 birincil sonuç değişkenlerini etkilemez.

**Gidermek için:** ÖK'de §6.5 politikasının S mi Y mi olduğunun yazılması (NOTLAR N-1).

## B-2. General JSON + birden çok ihraççı imzası + KB-JWT `sd_hash` — 15 satır, 0 birincil

**Vektörler:**
- VP05 (sd_hash ilk imzayla kurulmuş),
- VP07 (sd_hash ikinci imzayla kurulmuş),
- VP05-SIRA-ters (MR4 dışı tanımlayıcı).

Yapılandırmalar: `L4`, `L4-S`, `L4-Y`, `P0`, `P1`.

**Çatışma:**
- RFC 9901 §8.1: "the SD-JWT Compact Serialization part is built by concatenating the protected header, the payload, and the signature of the JWS JSON serialized SD-JWT". Tekil "the signature" General JSON'da birden çok imza varken hangi imza olduğunu söylemiyor.
- RFC 9901 §7.3 (5g) ise sd_hash eşleşmesini zorunlu tutuyor: "verify that it matches the value of the sd_hash claim".
- ÖK §2D m.4 bunu zaten kayda geçirmiş: "`sd_hash`'in hangi imzayı bağladığı tanımsızdır". Bu bir dış bildirim adayıdır (DB-1).

**Sonuç:** İhraççı imzası düzeyinde karar belirlidir. Örnek: VP05 `L4` altında R sağlanır ve imza düzeyinde `accept-hybrid` olur. KB doğrulamasının sonucu ise doğrulayıcının seçtiği imzaya bağlı: ilk imza, ikinci imza ya da hepsini deneme. Bu yüzden `indeterminate`.
- İhraççı imzası düzeyinde red olan hücreler belirsiz değildir. Örnek: VP06 `L4` altında R karşılanmıyor → `reject`.
- VP06'da tek imza olduğu için sd_hash bağlaması tektir → `P0`/`P1`/`GEC` altında `accept-classical`.

**Gidermek için:** RFC 9901 errata ya da SD-JWT VC profili (DB-1). ÖK §2D m.4 gereği bu hücreler zaten **tanımlayıcı** raporlanır. Hedefin hangi imzayı özete aldığı gözlem olarak kaydedilir.

## B-3. Composite ECDSA bileşeninin DER katılığı — 10 satır, 0 birincil

**Vektörler:**
- CMP05: asgari olmayan DER, değerler geçerli;
- CMP06: geçerli imza + sonda 1 artık bayt.

Yapılandırmalar: `GEC`, `IZIN-AX`, `L4`, `L4-S`, `L4-Y`. `IZIN-A`'da alg W dışında kaldığı için `reject` belirlidir.

**Çatışma:**
- composite -04 §4.2: "the ECDSA signature is encoded as an Ecdsa-Sig-Value". §4.5.1 kodlamayı DER olarak tanımlar ama çözme için yalnız şunu der: "Decoding simply reverses these two steps."
  - Asgari olmayan bir INTEGER, "adımları tersine çevirerek" aynı r değerine çözülür → kabul yönü.
  - Katı bir DER ayrıştırıcı reddeder → red yönü.
- LAMPS -19 §4.3: "Deserialization reverses this process, raising an error in the event that the input is malformed." "Malformed" tanımlanmamış.
- CMP06'nın tradSig'i 72 bayttır ve -04 Tablo 2'deki "≤ 72" sınırına sığar. Bu yüzden -04 §4.3'teki uzunluk denetimi de ayırt etmez.
- DER'in kanoniklik kuralı (X.690) korpusta yok.

**Gidermek için:** composite taslağına "Ecdsa-Sig-Value MUST be DER-encoded and verifiers MUST reject non-canonical encodings and trailing data" benzeri bir cümle eklenmesi. Bu, DB-2'nin yanına bir editoryal not adayıdır (NOTLAR N-6). Vektörler ikincildir (K7 ikincil).

## B-4. `crit` için alıcıya MAY — 8 satır, 0 birincil

**Vektörler:**
- CRIT03: `crit=["alg"]`,
- CRIT04: `crit=[]`.

Yapılandırmalar: `GEC`, `L4`, `L4-S`, `L4-Y`.

- RFC 7515 §4.1.11 üreticiye MUST NOT der: "Producers MUST NOT include Header Parameter names defined by this specification … Producers MUST NOT use the empty list".
- Alıcıya yalnız izin verir: "Recipients MAY consider the JWS to be invalid if the critical list contains any Header Parameter names defined by this specification … or if any other constraints on its use are violated."
- CRIT03'te listelenen "alg" anlaşılan bir parametre olduğu için "not understood → invalid" kuralı da tetiklenmez.

**Karşılaştırma için:** CRIT01, CRIT02 ve CRIT05 belirlidir (`reject`), çünkü listelenen uzantı anlaşılmıyor: "If any of the listed extension Header Parameters are not understood and supported by the recipient, then the JWS is invalid" [T386].

## B-5. Güven çapası `x5c` içinde (X5C06) — 5 satır, 0 birincil

Yapılandırmalar: `GEC`, `L4`, `L4-S`, `L4-Y`, `L4-YOL`.

- HAIP §6.1.1 [T043]: "The X.509 certificate of the trust anchor MUST NOT be included in the x5c JOSE header of the SD-JWT VC." Bu, SD-JWT VC'nin **içeriğine** (üreticiye) yönelik bir yükümlülüktür. Doğrulayıcının böyle bir nesneyi reddetmesi gerekip gerekmediği yazılı değildir.
- RFC 7515 §4.1.6 [T038] uyarınca RFC 5280 yolu kök sertifika x5c içinde olsa da güven çapasından kurulur.
- **İki okuma:** "profil ihlali → red" ile "yol geçerli → kabul (`accept-hybrid`)".

## B-6. `kid` ile `x5c` farklı anahtarları gösteriyor (X5C10) — 5 satır, 0 birincil

Yapılandırmalar: `GEC`, `L4`, `L4-S`, `L4-Y`, `L4-YOL`.

- **Kabul yönü:** SD-JWT VC -19 §2.5 [T045]: "When the protected header of the Issuer-signed JWT contains the x5c parameter, the recipient uses the public key from the end-entity certificate". Anahtar yaprak sertifikadan alınır ve imza geçerlidir.
- **Red yönü:** 8725bis §3.1 [T329]: "The library MUST verify that the algorithm specified in the "alg" … is consistent with the algorithm associated with the key identified by the corresponding identifier (e.g., "kid")". kid issuer/ES256'yı (EC anahtarı) gösteriyor, alg ML-DSA-65.
- Hangi tanımlayıcının "anahtar araması"nı yöneteceği tanımlı değil. RFC 7515 §6 ve Ek D birden çok tanımlayıcının çelişmesini ele almıyor. SD-JWT VC §7.3 [T048] ("an attacker cannot influence the type of verification process used") kid'in etkisini red yönünde okumaya elverişli, ama doğrudan hüküm vermiyor.

## Belirsiz OLMAYAN ama SHOULD düzeyinde olan satırlar (bilgi)

| Satır | Karar | Dayanak | Not |
|---|---|---|---|
| VC11 × `GEC` (-13) | `accept-classical` | SD-JWT VC -13 §3.2.1: "it is RECOMMENDED that Verifiers and Holders accept both vc+sd-jwt and dc+sd-jwt … for a reasonable transitional period" | RECOMMENDED; red MUST ihlali değildir |
| VC11 × `GEC@-19` | `reject` | -19 §2.2.1 [T119] "The typ value MUST use dc+sd-jwt"; geçiş notu -19'da kaldırıldı (-19 değişiklik kaydı); RFC 9901 §9.11 "Verifiers check this value" (RECOMMENDED) | Doğrulayıcı tarafı SHOULD düzeyinde. MR3 bu değişimi "sürüm etkisi" olarak işaretler |
| DPOP06/07/09 × `GEC` | `reject` | RFC 9449 §4.3 madde 5 [T378] "registered asymmetric digital signature algorithm"; composite -04 §7.1 "are requested to be added" | MUST düzeyi; ancak IANA kaydına bağlı. Kayıt olursa karar `accept-hybrid` olur (NOTLAR N-4) |
