# KAT kör türetme girdisi (yürütücü tarafından hazırlandı)

> Bu dosya `literatur/analiz/KAT-SPEC.md`'nin **beklenen değer, dayanak, taslak kod, mutasyon ve uygulama bölümleri çıkarılmış** hâlidir. Amaç: ÖK §4.19 ve KAT-SPEC §5.3 gereği ikinci, bağımsız ve kör beklenen-değer türetmesi. Hücre tanımları (girdiler) aynen korunmuştur.

# KAT-SPEC: Bilinen-cevap testleri şartnamesi (Adım 6)

> **Hazırlayan:** literatür çalışması · 23–24.09.2026
> **Durum:** Uygulanabilir şartname taslağı. **Kod parçaları çalıştırılmadı.** Adım 6 çalışması önce N-sürüm ilkesiyle bağımsız bir beklenen-değer tablosu türetmeli (§5.3), sonra koşturmalı.
> **Dayanak:** Sentez §7.9 Katman 3/4, §7.12, §7.15 (6. hafta kapısı: "bilinen-cevap testlerinin hepsi geçti"), §7.14 (kapsam: 3 test).
> **Kaynak metinler** (salt okundu, yazılmadı):
> - `01-korpus/metin/RFC6840.txt`, `RFC6781.txt`, `RFC7583.txt`, `RFC9955.txt`
> - `literatur/metin/kim2026_x509_hybrid.txt`, `lee2026_eprint1416.txt`, `das2026_smime_eprint1374.txt`
> - Pilot: `referans/pilot/p1/weakest_link.spthy`, `p2/*.lp`
>
> **RFC metinleri:** Korpusta bulundu. Alıntılar metinden birebir alındı ("metin doğrulandı").
>
> **Etiketler:** L✓ (bu çalışma tam metinden okudu) · [Y] (kendi çıkarım) · tahmin.

---

## 0. Amaç ve genel geçme ölçütü

**Amaç:** Modelin (ASP çekirdeği + Tamarin kural şemaları) başka katmanlarda **yayımlanmış** üç sonucu yeniden ürettiğini göstermek. Böylece model sadakati ve genellenebilirlik sınanır. Katkı iddiası yoktur.

| KAT | Yeniden üretilecek sonuç | Sınanan model varsayımı (özet) |
|---|---|---|
| **KAT-1** DNSSEC | "Herhangi bir tek geçerli yol" kuralı altında güvenliği en zayıf işaretli algoritma belirler. Algoritma geçişi ve yeniden oynatma bu pencereyi uzatır. İmza bütünlüğü testi, PQ ile imzalı bir üst sinyal ve tekdüzelik bu pencereyi kapatır | ∃-yol politika semantiği; anahtar–artefakt bağlama; beklenti kanalı (sinyal ≠ uygulama); sürüm, zaman ve yeniden oynatma |
| **KAT-2** X.509 hibrit | "Klasik kabul ≠ hibrit kimlik doğrulama": varsayılan yolda PQ kanıtını bozmak kararı değiştirmez. Composite yapısal olarak bağlar. Bağlı PQ sertifikanın iptali karara girmez | Ayrılabilir ve atomik kodlama; kararın PQ kanıtına duyarlılığı; yaşam döngüsü kapsamı; saklama (M1) ile sahteleme (M2) ayrımı |
| **KAT-3** S/MIME | "Every valid path to the CEK must satisfy the active migration policy" ve bunun kimlik doğrulama ikiliği | Yol sayımının tamlığı; ∀-niceleyici; statik politika denetimi ile dinamik saldırı aramasının eşdeğerliği |

**Genel geçme ölçütü** (hepsi birlikte sağlanmalı):
1. Her hücrede ASP sonucu beklenen değere **%100** eşit.
2. Her mantıksal hücrede Tamarin sonucu beklenen değere **%100** eşit.
   - Mantıksal hücre, zamanı yalnız bayrakla temsil edilen hücredir.
   - "analysis incomplete" çıkarsa sentez §7.9'daki sonlanmama merdiveni uygulanır.
   - Merdivenden sonra da kapanmazsa hücre **belirsiz** sayılır ve KAT **kalır**.
3. ASP ile Tamarin sonuçları ortak hücrelerde **%100** uyumlu.
4. **Mutasyon:** §6'da listelenen her koruma kaldırıldığında en az bir "YOK" hücresi "SALDIRI"ya dönmeli.
5. **Süre:**
   - ASP hücresi 10 s'nin altında.
   - Tamarin lemması 600 s ve 12 GB sınırında (pilotta benzer boyutlar 1 s'nin altındaydı).
   - Toplam KAT paketi 15 dakikanın altında (tahmin).

**ASP'de sonuç okuma:** "Saldırı var" sorusu şöyle yanıtlanır:
- Çekirdek + örnek + `:- not attack.` kısıtı **SAT** ise saldırı vardır (clingo çıkış kodu 10 ya da 30).
- **UNSAT** ise saldırı yoktur (çıkış kodu 20).

Deterministik karar modülünde (`hon_decision.lp`) tek cevap kümesi okunur (`decision/2`).

---

## 1. Ortak çekirdek

### 1.1 Girdi sözlüğü (ekosistemden bağımsız)

| Olgu | Anlam | KAT-1 | KAT-2 | KAT-3 |
|---|---|---|---|---|
| `key(K)`, `key_class(K,C)`, C ∈ {cl, pq, comp} | Anahtar ve sınıfı. comp: kırılması için bütün bileşenlerin kırılması gerekir | KSK/ZSK, üst bölge anahtarı | CA'nın klasik/PQ/composite anahtarı | ihraççı ve TL anahtarları |
| `comp_part(K,K1)` | composite bileşeni | — | ● | — |
| `exposure(K,T0)` | Açık anahtarın saldırgana görünür olduğu ilk an (bkz. CRQC-TAKVIMI §1) | ● | ● | ● |
| `art(A)`, `owner(A,E)`, `target(T)` | Artefakt, sahibi, sahtelenmek istenen hedef | DS, DNSKEY, A RRset | EE sertifikası | kimlik bilgisi, TL |
| `slot(A,S,K)` | A üzerindeki S imzası (K ile) | RRSIG'ler | temel/alt/composite imza | TL ve kimlik bilgisi imzaları |
| `intro_s(K,I)` / `intro_v(K,I,V)` | I artefaktı K'yı tanıtır (sürümsüz / V sürümünde) | DS→KSK, DNSKEY→ZSK | — | TL→ihraççı anahtarları |
| `introducer(I)`, `validates(I,X)` | I'nın tanıttığı anahtarlar X'i doğrulayabilir (kenar) | ds→dnskey, dnskey→a_rr | — | tl→cred |
| `anchor(K)`, `anchored(K,X)` | Güven çapası K, X'i doğrudan doğrular | kp→ds | CA→ee (yalnız uç varlık kapsamı; Kim'in test kapsamı) | ktl→tl |
| `version(I,V,Inc,Exp)`, `versioned(I)`, `seen(I,V)` | İmzalı sürüm, imza geçerlilik aralığı ve doğrulayıcının gördüğü en yeni sürüm (tekdüzelik) | ● | — | — |
| `signal_s/3`, `signal_v/4`, `local_req/2` | Beklenti: I, E için C sınıfını gerekli kılar. Yerel politika P2 | DS'nin işaretlediği algoritmalar | yerel P2 ya da TL'den gelen beklenti | TL'deki "pq_required" |

**Kanal sınıfı** (sentez §7.4):
- KAT-1'deki bütün artefaktlar **çekilen** türdedir. DNS taşıması kimliği doğrulanmamıştır; bu yüzden H1 tipi ikame mümkün değildir. Bu, H1 için bir sağlık hücresidir.
- KAT-2'deki sertifika **aktarılan** türdedir.
- KAT-3b'de TL **çekilen**, kimlik bilgisi **aktarılan** türdedir.

**Politika eşlemesi:**

| Çekirdek `pol` | Sentez §7.10(c) | Kim vd. | DNSSEC |
|---|---|---|---|
| `anyvalid` | P0 | P0 / varsayılan yol | RFC 6840 varsayılanı |
| `allpresent` | P1 | P1 (fırsatçı: varsa denetle) | — |
| `required` + `local_req` | P2 | P2 | "signature completeness" |
| `required` + imzalı kaynaktan `signal` | P3 (kaynak klasik) / P4 (kaynak PQ) | — (P3 durum kaynağı açık) | DS sinyali + bütünlük testi |
| `monotone=1` | M-f'nin tekdüzelik bileşeni | P3 (süreklilik) | RRSIG geçerliliği içinde geri dönüşü reddetme |

### 1.2 ASP çekirdeği `kat_core.lp` (TASLAK; çalıştırılmadı)

> [taslak kod bloğu çıkarıldı: kör türetme birincil kaynaktan yapılır]

**Basitleştirme notu:** Dürüst ara artefaktların politikayı sağladığı varsayılıyor. KAT'larda dürüst ara artefaktlar her iki algoritmayla imzalı olduğundan bu varsayım sonucu değiştirmez. Asıl modelde bir `hon_ok/1` koşuluyla daraltılmalı [Y].

### 1.3 Dürüst karar modülü `hon_decision.lp` (KAT-2a/2c/2d; TASLAK)

Saldırgan yoktur. Doğrulayıcının dürüst bir nesne üzerindeki kararı, PQ kanıtının durumuna göre hesaplanır. Böylece "karar duyarlılığı" (Kim'in 27 hücresi) sınanır.

> [taslak kod bloğu çıkarıldı: kör türetme birincil kaynaktan yapılır]

### 1.4 Tamarin kalıpları (pilot `weakest_link.spthy` ile aynı üslup)

- `builtins: signing` (KAT-3a'da ayrıca `asymmetric-encryption`, `symmetric-encryption`).
- `restriction Eq`, `restriction NotEq` (gerektiğinde), `restriction Once`.
- `rule Qday` ve `!Qday()`. Q-day'den sonra klasik anahtarı dışarı veren `Break_*` kuralları (S2 soyutlaması). τ Tamarin'de modellenmez; zaman hücreleri bayrakla temsil edilir, τ'yu ASP taşır.
- Politika ve aşama farkları **önişlemci bayraklarıyla** (`-D=BAYRAK`) seçilir. Bileşik koşul gerekiyorsa tek bir bileşik bayrak tanımlanır (örneğin `DS_PQ`). Tamarin 1.12 önişlemcisinin bileşik ifade desteği bu çalışmaca doğrulanmadı.
- Her dosyada iki lemma: `executable` (exists-trace, sağlık) ve kimlik doğrulama lemması (all-traces). KAT-2'de ayrıca bir duyarlılık lemması (exists-trace) var.

### 1.5 Girdi biçimi ve koşum kabuğu (öneri)

Ekosistemden bağımsız YAML → ASP olguları + Tamarin bayrakları. Örnek (KAT-1, K1-03):

> [taslak kod bloğu çıkarıldı: kör türetme birincil kaynaktan yapılır]

Rapor satırı (CSV):

`kat,cell,consts,flags,expected_asp,asp_result,asp_exit,expected_tamarin,tamarin_result,tamarin_s,agree,git_commit,image_digest`

---

## 2. KAT-1: DNSSEC "any single valid path" ve algoritma downgrade'i

### (a) Yeniden üretilecek yayımlanmış sonuç (metin doğrulandı)

**RFC 6840** (Weiler, Blacka, Şubat 2013; Standards Track; RFC 4033/4034/4035/5155'i günceller):

- **§5.11 "Mandatory Algorithm Rules"**, son paragraf:
  > "This requirement applies to servers, not validators. Validators SHOULD accept any single valid path. They SHOULD NOT insist that all algorithms signaled in the DS RRset work, and they MUST NOT insist that all algorithms signaled in the DNSKEY RRset work. A validator MAY have a configuration option to perform a signature completeness test to support troubleshooting."
- **§6.2 "Clarifications on DNSKEY Usage":**
  > "However, be aware that there is no way to tell resolvers what a particular DNSKEY is supposed to be used for -- any DNSKEY in the zone's signed DNSKEY RRset may be used to authenticate any RRset in the zone."
- **Ek C.2 ("Accept Any Success"; §5.10 bunu varsayılan olarak önerir):**
  > "This policy has the disadvantage of making the validator subject to the compromise of the weakest of these trust anchors, while making it relatively painless to keep old trust anchors configured in perpetuity."

**RFC 6781** (Kolkman, Mekking, Gieben, Aralık 2012; DNSSEC Operational Practices v2):

- **§4.1.4 "Algorithm Rollovers":**
  - Muhafazakâr ve liberal yorumları tanımlar.
  - Aşamalar (Şekil 8): initial → new RRSIGs → new DNSKEY → new DS → DNSKEY removal → RRSIGs removal.
  > "When removing an old algorithm, the DS for the algorithm should be removed from the parent zone first, followed by the DNSKEY and the signatures (in the child zone)."
- **§4.3.4 "DS Signature Validity Period":**
  > "Since the DS can be replayed as long as it has a valid signature, a short signature validity period for the DS RRSIG minimizes the time that a child is vulnerable in the case of a compromise of the child's KSK(s)."

**RFC 7583** (Morris vd.; Key Rollover Timing):
- §1 kapsam: "Algorithm rollovers. Only the rolling of keys of the same algorithm is described here: not transitions between algorithms."
- Double-DS KSK zamanlaması: `Iret = DprpP + TTLds`, `Tdea(N) = Tret(N) + Iret`. Bunu yalnız zaman parametrelerinin adlandırması için kullanıyoruz; algoritma geçişi için normatif değildir.

**RFC 9955 §6.2** (genel ilke):
> "As such, if a system does skip a component signature, security does not rely on the security of all component signatures."

**Yeniden üretilecek önerme** (RFC metinlerinin doğrudan mantıksal sonucu):
- "Algoritma downgrade'i" ifadesi RFC 6840'ta **geçmiyor**; sonuç kuralların birleşiminden çıkıyor [Y].
- RFC 6840 doğrulayıcısı altında bir bölge klasik (C) ve PQ (Q) algoritmalarla imzalıysa, doğrulayıcının güvenliği ulaşılabilir en zayıf algoritmanınkine eşittir. Klasik anahtarları sahteleyebilen saldırgan (CRQC), Q imzaları var olsa bile sahte RRset'leri kabul ettirir.
- DS yalnız Q'yu gösterse de DNSKEY RRset'inde C anahtarı kaldıkça saldırı sürer (§6.2).
- Pencere şu koşulların hepsi sağlanınca kapanır: eski DS geri çekildi, eski anahtarlar DNSKEY RRset'inden çıkarıldı, eski imzalı sürümlerin imza geçerliliği doldu (RFC 6781 §4.1.4, §4.3.4).
- Negatif kontroller:
  - İmza bütünlüğü testi + PQ ile imzalı üst bölge sinyali (DS) saldırıyı kaldırır.
  - Tekdüze doğrulayıcı durumu yeniden oynatmayı kaldırır.
  - Üst bölge anahtarı klasikse sinyal sahtelenir ve saldırı geri gelir.

### (b) ASP karşılığı

**Gerekli model öğeleri:**

| Öğe | DNSSEC | Bizdeki karşılık (OpenID4VC) |
|---|---|---|
| Artefakt | `ds` (üst bölge DS RRset), `dnskey` (bölge DNSKEY RRset), `a_rr` (hedef RRset) | TL/LoTE kaydı, `x5c` ya da ihraççı meta verisi `jwks`, kimlik bilgisi ya da durum listesi |
| Kenar (tanıtma) | DS→KSK (`validates(ds,dnskey)`); DNSKEY RRset→her anahtar (`validates(dnskey,a_rr)`) | TL→ihraççı anahtarı; `x5c`→imza anahtarı |
| İmza kenarı | RRSIG'ler (`slot`) | JWS/COSE imzaları |
| Kanal | hepsi çekilen; taşıma kimliği doğrulanmamış | çekilen (TL, durum) / aktarılan (kimlik bilgisi) |
| Beklenti | DS'nin işaretlediği algoritmalar (`signal_v`) | TL/LoTE'deki varlık başına beklenti (M-f) |
| Politika | `anyvalid` (RFC 6840 varsayılanı), `required` (bütünlük testi), `allpresent` | P0, P3/P4, P1 |
| Zaman | sürümler, imza geçerlilik aralıkları, `seen` (tekdüzelik) | TL `nextUpdate`, durum `ttl`, sunset |

**Örnek dosyası `kat1_dnssec.lp`** (çekirdekle birlikte; TASLAK):

> [taslak kod bloğu çıkarıldı: kör türetme birincil kaynaktan yapılır]

### (c) Tamarin karşılığı (asgari kurallar ve lemma; TASLAK)

> [taslak kod bloğu çıkarıldı: kör türetme birincil kaynaktan yapılır]

**Not:**
- `MONOTONE` + `OLD_DS_REPLAY` hücresinde (K1-06) eski DS'ye dönüş ayrı bir kısıtla engellenir. Pratikte K1-06 için `OLD_DS_REPLAY` bayrağı hiç verilmez; bu, tekdüze doğrulayıcının eski DS'yi kabul etmemesinin eşdeğeridir [Y].
- Saldırgan kendi anahtarını üretebilir. Örneğin `pk('k')` ile sahte DS ve DNSKEY kurar. K1-12 bu yolla çıkar.

## 3. KAT-2: X.509 hibrit, "klasik kabul ≠ hibrit kimlik doğrulama"

### (a) Yeniden üretilecek yayımlanmış sonuçlar (L✓)

**Kim vd. 2026** (arXiv:2607.20800v3):
- **§VI-A:**
  > "We ran the invalidated variant of Section V-B beside its valid counterpart in every one of the 27 cells formed by the three separable schemes and the nine configurations. In all 27 the two verdicts were identical."

  İki hücre bilgi vermiyor: wolfSSL zorlayıcı derlemesinde Catalyst kodlama ayrışması ve NSS'nin Chameleon'da ML-DSA anahtarını tanımaması. Kalan 25'i kabul hücresi.
- **Tablo IV (composite):** [sonuç çıkarıldı — birincil metinden okuyun: `literatur/metin/kim2026_x509_hybrid.txt`]
- **§VII, Tablo V (Related, certA geçerli):** leafB durumu revoked / expired / OCSP unknown / absent / valid. [Sonuçlar çıkarıldı — birincil metinden okuyun.]
- **§VIII-A, Tablo VI (P0–P3):**
  > "Under M1, P1 provides no more protection than P0: the adversary withholds the post-quantum evidence, P1 tolerates the absence, and the result is accept-classical, which the policy permits."

  P3 hakkında: "a later accept-classical for an identity recorded as hybrid-required is itself non-accepting". Tablo notu: "P3 presupposes an external continuity state keyed by the relying party's identity notion; we model only the verifier-side implication, not how it is stored or populated".

**Lee vd. 2026** (IACR ePrint 2026/1416):
- **§4.3:** Dokuz standart doğrulayıcı, geçerli ECDSA temel imzası ve geçersiz PQC alt imzası taşıyan Catalyst sertifikasını kabul ediyor.
  > "With Composite, corrupting either the ML-DSA or the classical component of the composite signature is rejected with a signature-verification failure".

  Bu sonuç üç bağımsız doğrulayıcıda ve üç OID ailesinde görüldü.
- **§4.4:** "None of the 15 stacks we tested provides a working default – or even readily configurable – way to require the binding". wolfSSL "does verify a present alt-signature (…) yet there is no mechanism to mark an alt-signature as required, so a stripped classical-only leaf (…) is accepted".
- **§6:** "(…) paired with a require-PQC policy, since no encoding alone defeats a full classical downgrade."

### (b) ASP karşılığı

**Gerekli model öğeleri ve eşleme:**

| Öğe | X.509 | Bizdeki karşılık |
|---|---|---|
| Artefakt | EE sertifikası (`ee`); Related'da `certA` + `leafB` | kimlik bilgisi + `x5c`; ikili ihraç |
| İmza yuvası | Catalyst: `s_base` (klasik, kritik) + `s_alt` (PQ, kritik değil); Composite: tek `s_comp` (comp) | Senaryo (a) composite `alg`; (b)/(d) ayrılabilir (ikili ihraç, General JSON) |
| Kanal | aktarılan | aktarılan (`x5c`, kimlik bilgisi) |
| Politika | `vb` ∈ {ignore, parse_no_enforce, enforce_if_present, require, continuity, legacy_oid} | P0 / P0 / P1 / P2 / tekdüzelik / — |
| Yaşam döngüsü | `bound(certA,leafB)`, `status(leafB,St)` | durum listesi / TL'nin karar kapsamına girip girmemesi |

**KAT-2a/2c/2d**, `hon_decision.lp` (§1.3) ile birlikte (TASLAK):

> [taslak kod bloğu çıkarıldı: kör türetme birincil kaynaktan yapılır]

**KAT-2b** (M2, CRQC ile sahteleme), `kat_core.lp` ile birlikte (TASLAK):

> [taslak kod bloğu çıkarıldı: kör türetme birincil kaynaktan yapılır]

### (c) Tamarin karşılığı (asgari kurallar ve lemmalar; TASLAK)

> [taslak kod bloğu çıkarıldı: kör türetme birincil kaynaktan yapılır]

## 4. KAT-3: S/MIME "every valid path to the CEK" ve kimlik doğrulama ikiliği

### (a) Yeniden üretilecek yayımlanmış sonuç (L✓)

**Das ve Chattopadhyay 2026** (IACR ePrint 2026/1374; alındı 04.07.2026, revize 21.09.2026; "Published elsewhere. ICDSNE 2026"):
- **Özet:**
  > "We model encrypted S/MIME as a multi-recipient CMS object with certificate-bound paths to a shared CEK and show that post-quantum confidentiality is a universal message-level property: every valid path to the CEK must satisfy the active migration policy."
- **§3, Denklem (8):** Accept(ED, P_t) = 1 ⟺ ∀i ∈ R, V_i(t) = 1 ⇒ χ_i(t) ∈ A_t. Burada V_i(t) sertifika geçerliliği, χ_i(t) ∈ {PQC, Hybrid, Classical, Unknown, Invalid} yol sınıfı, A_t politikanın izin verdiği sınıflardır.
- **Önerme 1:**
  > "Therefore, the confidentiality level of ED is bounded by the weakest valid recipient path protecting K."
- **§3.1 Aşama 3–5 ve Tablo 1:**
  - Altı mesaj sınıfı: pqc-protected, hybrid-protected, classical-only, unsafe-mixed-mode, invalid, unknown.
  - Öncelik sırası: malformed → invalid; "unsafe mixed-mode exposure is reported before weaker uncertainty labels"; "Unknown mechanisms fail closed".
  - Kipler: strict-PQC, transitional-hybrid, legacy-audit.

**Okuma notu [Y]:**
- Kural V_i(t)=1 koşullu. Gizlilikte, CRQC sahibi bir saldırgan klasik bir alıcı yolundan (RI) CEK'i sertifika geçersiz olsa bile çıkarabilir. Bu vektör aşağıdaki tabloda o8'dir.
- Yazarlar bu durumu tartışmıyor.
- **Kimlik doğrulama ikiliğinde** bu koşul doğaldır: doğrulayıcının reddettiği yol kabule yol açamaz.
- KAT-3a Das'ın kuralını **yazıldığı gibi** yeniden üretir; o8 ayrıca "model farkı" olarak raporlanır.

### (b) ASP karşılığı

**KAT-3a: literal CMS gizlilik sınıflaması** (TASLAK):

> [taslak kod bloğu çıkarıldı: kör türetme birincil kaynaktan yapılır]

**KAT-3b: kimlik doğrulama ikiliği** (`kat_core.lp` + aşağıdaki; pilot `weakest_link.spthy` ile aynı 6 yapılandırma):

> [taslak kod bloğu çıkarıldı: kör türetme birincil kaynaktan yapılır]

### (c) Tamarin karşılığı

**KAT-3a: CEK gizliliği** (TASLAK):

> [taslak kod bloğu çıkarıldı: kör türetme birincil kaynaktan yapılır]

**KAT-3b:** Pilot `referans/pilot/p1/weakest_link.spthy` **değiştirilmeden** altı bayrak birleşimiyle koşturulur.
- KAT-3b bu sonuçları ASP ikiliğiyle eşleştirir.
- Lemma: `claims_unforgeability`.



---

# HÜCRE TANIMLARI (beklenen sütunlar çıkarıldı)

## 2. KAT-1: DNSSEC "any single valid path" ve algoritma downgrade'i

| Hücre | ASP sabitleri | Tamarin bayrakları |
|---|---|---|
| K1-01 | stage=r2, pol=anyvalid | DS_CL, DK3_USABLE, ANYVALID |
| K1-02 | stage=r2, pol=required | DS_CL, DK3_USABLE, COMPLETENESS |
| K1-03 | stage=r3, pol=anyvalid | DS_PQ, DK3_USABLE, ANYVALID |
| K1-04 | stage=r3, pol=required | DS_PQ, DK3_USABLE, COMPLETENESS |
| K1-05 | stage=r3, pol=required, now=50 | DS_PQ, OLD_DS_REPLAY, DK3_USABLE, COMPLETENESS |
| K1-06 | K1-05 + monotone=1 | DS_PQ, DK3_USABLE, COMPLETENESS (eski DS yok) |
| K1-07 | stage=r5, pol=anyvalid | DS_PQ, DK3_USABLE, DK5, ANYVALID |
| K1-08 | K1-07 + monotone=1 | DS_PQ, DK3_USABLE, DK5, ANYVALID, MONOTONE |
| K1-09 | stage=r5, pol=anyvalid, now=150 | DS_PQ, DK5, ANYVALID |
| K1-10 | stage=dds, pol=anyvalid | DS_BOTH, DK3_USABLE, ANYVALID |
| K1-11 | stage=dds, pol=required | DS_BOTH, DK3_USABLE, COMPLETENESS |
| K1-12 | stage=r3, pol=required, parent_class=cl | DS_PQ, DK3_USABLE, COMPLETENESS, PARENT_CL |
| K1-13 | stage=r3, pol=anyvalid, qday=200 | DS_PQ, DK3_USABLE, ANYVALID, NO_QDAY |
| K1-14 | stage=r5, pol=anyvalid, now=150, extra_ta=1 | DS_PQ, DK5, ANYVALID, EXTRA_TA |
| K1-15 | stage=r3, pol=allpresent | DS_PQ, DK3_USABLE, ALLPRESENT |


## 3. KAT-2: X.509 hibrit, "klasik kabul ≠ hibrit kimlik doğrulama"

| Hücre | scheme | vb | pqev |
|---|---|---|---|
| K2a-01/02 | catalyst | ignore | valid / invalid |
| K2a-03/04 | catalyst | parse_no_enforce | valid / invalid |
| K2a-05/06 | chameleon | ignore | valid / invalid |
| K2a-07/08 | related | ignore | leafb=valid / revoked |
| K2a-09…11 | catalyst | enforce_if_present | valid / invalid / absent |
| K2a-12…14 | catalyst | require | valid / invalid / absent |
| K2a-15/16 | composite | require (composite'i tanıyan) | valid / invalid |
| K2a-17 | composite | legacy_oid | valid |

| Hücre | scheme | pol | expect_src | coexist_cl | Tamarin bayrakları |
|---|---|---|---|---|---|
| K2b-01 | catalyst | anyvalid | none | 0 | CRQC, V_IGNORE |
| K2b-02 | catalyst | allpresent | none | 0 | CRQC, V_ENFORCE_IF_PRESENT |
| K2b-03 | catalyst | required | local | 0 | CRQC, V_REQUIRE |
| K2b-04 | catalyst | required | tl_cl | 0 | (ASP-yalnız) |
| K2b-05 | catalyst | required | tl_pq | 0 | (ASP-yalnız) |
| K2b-06 | composite | anyvalid | none | 0 | CRQC, COMPOSITE |
| K2b-07 | composite | anyvalid | none | 1 | CRQC, COMPOSITE, COEXIST_CLASSICAL |
| K2b-08 | composite | required | local | 1 | (ASP-yalnız) |

| leafB | vb=ignore (varsayılan yol) | vb=require (P2 referansı) |
|---|---|---|
| revoked | ? | ? |
| expired | ? | ? |
| unknown (OCSP) | ? | ? |
| absent | ? | ? |
| valid (kontrol) | ? | ? |

| Hücre | Politika | seen_hybrid | Tamarin |
|---|---|---|---|
| K2d-01 | P0 (ignore) | 0 | V_IGNORE |
| K2d-02 | P1 (enforce_if_present) | 0 | V_ENFORCE_IF_PRESENT |
| K2d-03 | P2 (require) | 0 | V_REQUIRE |
| K2d-04 | P3 (continuity) | 1 | (ASP-yalnız) |
| K2d-05 | P3 (continuity) | 0 (ilk temas) | (ASP-yalnız) |


## 4. KAT-3: S/MIME "every valid path to the CEK" ve kimlik doğrulama ikiliği

| Vektör | Alıcı yolları (tür, sertifika geçerli?) |
|---|---|
| o1 | mlkem ✓ |
| o2 | mlkem ✓, mlkem ✓ |
| o3 | rsa_kt ✓ |
| o4 | mlkem ✓, rsa_kt ✓ |
| o5 | hybrid_kem ✓ (onaylı) |
| o6 | hybrid_kem ✓, ecdh_ka ✓ |
| o7 | mlkem ✓, unknown_oid ✓ |
| o8 | mlkem ✓, rsa_kt ✗ (sertifika geçersiz) |
| o9 | malformed |
| o10 | hybrid_kem ✓ (onaysız) |
| o11 | mlkem ✓, hybrid_kem ✓ (onaylı) |
| o12 | ecdh_ka ✓, rsa_kt ✓ |

| Bayrak |
|---|
| MIXED |
| PQ_ONLY |
| HYBRID_KEM |

| Pilot eşi | tl_class | expect | coexist |
| --- | --- | --- | --- |
| V1 base | cl | 0 | 1 |
| V2 expectTL | cl | 1 | 1 |
| V3 tlPQ | pq | 0 | 1 |
| V4 tlPQ_expectTL | pq | 1 | 1 |
| V5 tlPQ_nocoexist | pq | 0 | 0 |
| V6 tlClassical_nocoexist | cl | 0 | 0 |




## Türetilecek değerler (sözlük; eşleme VERİLMEZ)

- **KAT-1 (her hücre):** ASP ∈ {SALDIRI, YOK}; Tamarin `a_rrset_authentic` ∈ {verified, falsified}.
- **KAT-2a (her satır, `pqev`'deki her değer için ayrı):** `decision(ee,·)` ∈ {accept_classical, accept_hybrid, reject, indeterminate}.
- **KAT-2b (her hücre):** ASP ∈ {SALDIRI, YOK}; Tamarin bayrakları verilmişse `cert_authentic` ∈ {verified, falsified}.
- **KAT-2c (leafB × {vb=ignore, vb=require}):** karar ∈ {accept_classical, accept_hybrid, reject, indeterminate}.
- **KAT-2d (her hücre):** ASP kararı ∈ {accept_classical, accept_hybrid, reject}; Tamarin verilmişse ∈ {verified, falsified}.
- **KAT-3a (o1…o12):** `out` ∈ {pqc_protected, hybrid_protected, classical_only, unsafe_mixed, unknown, invalid}; accept strict ∈ {0,1}; accept transitional ∈ {0,1}.
- **KAT-3 Tamarin `cek_secrecy` (bayrak MIXED, PQ_ONLY, HYBRID_KEM):** ∈ {verified, falsified}.
- **KAT-3b (V1…V6):** `qday=0` (bütün klasik anahtarlar kırık) altında dinamik `attack` ∈ {SALDIRI, YOK} ve statik `violation` ∈ {0,1}; ayrıca `qday=200` (CRQC yok) altında dinamik `attack`; Tamarin `claims_unforgeability` ∈ {verified, falsified}.
