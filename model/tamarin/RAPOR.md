# Adım 4 — Tamarin kural şemaları R1–R5 (kanıtlanmış soyutlamanın Katman 2'si)

- **Tarih:** 24.09.2026
- **Çalışma:** tamarin (Adım 4)
- **Klasör:** `model\tamarin\`
- **Araçlar:**
  - Tamarin 1.12.0 + Maude 3.5.1. İmaj `pq-a02-tamarin:1.12.0`, kimliği `sha256:59b648d6…`. Sürüm satırları `sonuc\calistir_log.txt` dosyasında.
  - Datalog karşılaştırması için clingo 5.8.2 (`pq-a02-solver:1.0`). Bu hafif, ayrı bir değerlendirme adımıdır; bir Tamarin sonucu değildir.
- **Kanıt kuralı:** Rapordaki her sayı `sonuc\` altındaki dosyalardan alındı. Tabloların kaynak dosyası her tablonun altında yazılı. Tablolar bu dosyalardan betikle üretildi, elle aktarılmadı.
- **Adım 5A eki (24.09.2026):** §12'de. İçerik:
  - R6 zaman penceresi ve H5'in biçimsel hâli,
  - R7 tekdüze beklenti, M-f/M-g/M-h karşılaştırması,
  - ProVerif ikinci görüşü.
  
  §0–§11 Adım 4'e aittir ve değişmedi.

## 0. Özet

- **Kapsam:** 5 kural şeması, 34 varyant, 196 lemma koşumu.
  - Toplam 230 konteyner koştu: 34 liste koşumu ve 196 lemma koşumu.
  - Her lemma ayrı bir konteynerde koştu (`metrikler.txt`, `calistir_log.txt`).
- **Beklentiyle uyum:** Beklenen ile gözlenen sonuç 196/196 örtüşüyor. Beklentiler koşumdan önce `betik\varyantlar.tsv` dosyasına yazılmıştı.
- **Kabul ölçütü:** R1–R5'in beşi de GEÇTİ.
  - Korumalı varyantta güvenlik lemması verified.
  - Mutantta güvenlik lemması falsified.
  - `executable` bütün varyantlarda verified.
- **Mutasyon skoru:** 11/11 (%100).
  - Her korumanın kaldırılması iz verdi.
  - Her iz, kaldırılan korumanın açtığı yoldan geçiyor.
    - Anahtar korumalarında (R1, R3, R4, R5) o anahtar CRQC ile kırılıyor.
    - Beklenti korumalarında (R2) doğrulayıcı klasik yolu beklentisiz ya da saldırganın verdiği `'none'` değeriyle açıyor; ardından ihraççının klasik anahtarı kırılıyor.
- **Katman 1↔2 bağı:** Datalog (clingo) tahmini ile Tamarin hükmü 44/44 güvenlik lemmasında aynı. Uyum bayrak uzayının tamamında (34 yapılandırma) sağlanıyor.
- **Kaynak kullanımı:**
  - En uzun koşum 1,58 s; en yüksek bellek 95,7 MiB.
  - Bütün koşumlar merdivenin 1. basamağında (`--prove`) kapandı; kapanmayan yok.
  - İyi biçimlilik uyarısı yok (`uyarilar.txt` boş).
- **Planı etkileyen bulgu (soyutlama sınırı):**
  - R1'in ek varyantı `X_alt_ca`'da ihraççının kendi zinciri tamamen PQ. Yine de aynı kök altında klasik kalmış ikinci bir CA, dürüst ihraççının adıyla sahteciliğe izin veriyor (G1 falsified).
  - `pq(L)`'yi yalnız gerçek ebeveyne bakarak okuyan naif Datalog bu varyantta "güvenli" diyor. 44 satırdaki tek uyumsuzluk bu.
  - Tahmini doğru yapan, "kabul edilen bütün imzacılar" (anahtar sınıfı) semantiği.
  - Ayrıntı §6.5'te; ASP'ye etkisi `KARAR-NOTLARI.md` dosyasında.

## 1. Kapsam, tehdit modeli ve ortak yapı

### 1.1 Tehdit modeli (karar belgesi §7.4 ile eşleme)

| §7.4 | Modeldeki karşılığı |
|---|---|
| S1: Dolev–Yao ağ saldırganı | Tamarin'in yerleşik saldırganı. Ağdaki her iletiyi görür, düşürür, değiştirir ve yeniden oynatır. |
| S2: CRQC(τ, k) | Tek seferlik `Qday` kuralı `!CRQC()` olgusunu üretir. `Unique('qday')` kısıtı vardır; Q-day hiç gerçekleşmeyebilir de. Q-day'den sonra `CRQC_Break_*` kuralları, saldırganın **gözlediği** (`In(pk(sk))`) klasik açık anahtarın özel anahtarını açığa çıkarır. τ=0 ve k sınırsızdır; bu, S2'nin en güçlü biçimidir. τ ve k R6'nın konusu. |
| S3: topla-sonra-sahtele | Kısmen modellendi. R4'te cihaz açık anahtarı yalnız sunumda görünür. Saldırgan önce bir sunumu gözlemeli, anahtarı ancak sonra çıkarabilir. |
| ML-DSA/SLH-DSA EUF-CMA güvenli | PQ anahtarlar için kırma kuralı **yok**. |
| Operatörler ve ihraççılar dürüst | Kurulum kuralları saldırgansız ve taze anahtarla çalışır. İçeriden saldırgan yok. |
| Doğrulayıcı sınanan politikaya uyar | Doğrulayıcı kuralları politikanın kendisidir. Örnekler: P0 (en az biri geçerli), beklentiyle kapılı klasik yol. |

İmzalar semboliktir (`builtins: signing`). Doğrulama `Eq(verify(sig, m, pk), true)` kısıtıyla yapılır.

### 1.2 Ortak model yapısı

**Bayraklar.** Bayrak tanımlıysa koruma var demektir.
- **Korumalı varyant:** Bütün korumalar açık.
- **Mutant:** Tam olarak bir koruma kaldırılmış.
- **Ek:** Bayrak uzayının geri kalanı. Datalog uyumunu bütün uzayda sınamak için koşuldu.
- **Ek-sınır:** Soyutlama sınırı testi (R1'de `ALT_CA` ve `NAME_BIND`).
- **Ek-H5:** H5 ön sinyali (R4'te `SINGLE_USE`).

**Lemma aileleri** (her modelde):
- **Sağlık:** `executable`, `executable_post_qday`, `attack_needs_crqc`. Bunlara kurala özgü `executable_legacy`, `attack_needs_crqc_G5` ve `executable_single_use_enforced` eklenir.
- **Güvenlik:** `G1_claims_unforgeability`, `G2_presentation_unforgeability`, `G5_no_classical_acceptance`.
- **Mutasyon:** `M_*` (exists-trace).
  - Yalnız ilgili koruma kaldırılmışsa modele girer.
  - Hedefin ihlal edildiği bir iz ister. Aynı izde kaldırılan korumaya bağlı olayı da ister:
    - anahtar korumalarında o anahtarın `Broken(...)` olayı,
    - R2'de göç etmiş ihraççının klasik yoldan kabulü (`AcceptVia(…,'classical')` ya da `UsedExpectation(I,'none')`) ve ihraççının klasik anahtarının kırılması.
- **Bilgi ve sınır:**
  - `S1_downgrade_trace` (R2): Q-day'siz downgrade izi.
  - `X_alt_ca_forges_honest_issuer` (R1).

**Önişlemci sınırı.** Tamarin 1.12'de iç içe `#ifdef`, atlanan dalda ayrıştırma hatası veriyor; bu denendi. `not (A | B)` biçimi de ayrıştırılmıyor. Bu yüzden modeller yalnız düz Boole koşulları kullanıyor (ör. `#ifdef A & not B`).

**Koşum düzeni.**
- Her lemma ayrı bir konteynerde koşar: `--rm`, `--memory=12g --memory-swap=12g`, `timeout 600`.
- Aynı anda yalnız bir Tamarin konteyneri çalışır. Başka bir Tamarin konteyneri varsa betik bekler.
- Sonlanmama merdiveninin 1→3→5→6 basamaklarını `betik\calistir.sh` kendiliğinden uygular. 2. ve 4. basamak model düzeyindedir ve elle yapılır; hiçbirine gerek kalmadı (§7).

## 2. Kural başına biçimsel ifade, model ve bulgu

Her kural için sırasıyla şunlar verilir:
- İngilizce ve Türkçe ifade.
- Tamarin lemması.
- Tamarin'in bayrak uzayında doğruladığı koşul. Kaynak: `datalog_uyum.csv` ve `varyant_ozeti.csv`.
- İz içeriği. Kaynak: `izler.csv`; izdeki protokol kuralları JSON izlerinden okundu.

### 2.1 R1 — zincir (`modeller\R1_chain.spthy`)

**EN.** Let a verifier with a pinned anchor key accept credential `c` of issuer `I` iff it validates the chain anchor → `ca_cert` → `iss_cert` → `cred`. Under S1+S2, claims unforgeability (G1) holds iff the root, CA and issuer signing keys are all PQ. For every classical key `k` on the chain there is a trace in which `k` is extracted after Q-day and a never-issued credential is accepted, even when every link below `k` carries a PQ signature.

**TR.** Doğrulayıcının çıpa anahtarı sabitlenmiş olsun. Doğrulayıcı `I` ihraççısının `c` kimlik bilgisini ancak çıpa → `ca_cert` → `iss_cert` → `cred` zincirini doğrularsa kabul etsin. S1+S2 altında G1, kök, CA ve ihraççı imza anahtarlarının üçü de PQ ise ve ancak o zaman sağlanır. Zincirdeki her klasik `k` anahtarı için bir iz vardır: `k` Q-day'den sonra çıkarılır ve hiç ihraç edilmemiş bir kimlik bilgisi kabul edilir. `k`'nin altındaki halkalar PQ imzalı olsa bile bu iz vardır.

**Lemma:**
```
lemma G1_claims_unforgeability:
  "All I c #j. Accept(I, c) @ #j ==> (Ex #i. Issued(I, c) @ #i & #i < #j)"
lemma M_<k>_classical:   /* k ∈ {root, ca, issuer}; yalnız k klasikse */
  exists-trace "Ex I c #j #b. Accept(I, c) @ #j & Broken('<k>') @ #b & not (Ex #i. Issued(I, c) @ #i)"
```

**Tamarin'in doğruladığı koşul:** G1 verified ⇔ `ROOT_PQ ∧ CA_PQ ∧ ISS_PQ`. Bu, 8 bayrak yapılandırmasının 8'inde sağlanıyor.

**Datalog eşlemesi:**
- `ROOT_PQ ⇔ pq(ca_cert)`, `CA_PQ ⇔ pq(iss_cert)`, `ISS_PQ ⇔ pq(cred)`.
- `anchored(ca_cert)`, çünkü `ca_cert`'i sabitlenmiş kök anahtarı imzalar.

**İzler:**
- **`M_root`:** İzdeki kurallar `Root_Setup, Qday, CRQC_Break_Root, Verify`.
  - Saldırgan kök anahtarını çıkarıp CA sertifikasını, ihraççı sertifikasını ve kimlik bilgisini kendisi üretiyor.
  - Dürüst CA'nın ve ihraççının kuralları izde yok. Sahtecilik iki düzey aşağı yayılıyor.
- **`M_ca`:** `CA_Setup, Qday, CRQC_Break_CA, Verify`.
- **`M_iss`:** `CA_Setup, Issuer_Setup, Qday, CRQC_Break_Issuer, Verify`.

**Ek-sınır varyantları:**
- **`X_alt_ca`:** Aynı kök altında ikinci bir CA klasik kalmış.
  - Sonuç: G1 falsified.
  - İz: `AltCA_Setup, Qday, CRQC_Break_AltCA, Verify`.
  - `X_alt_ca_forges_honest_issuer` verified: Kurulmuş dürüst bir ihraççının adı sahtelenebiliyor.
- **`X_alt_ca_namebind`:** Doğrulayıcı ihraççı adını kendi CA'sına bağlıyor. Sonuç: G1 verified.

### 2.2 R2 — downgrade (`modeller\R2_downgrade.spthy`)

**EN.** Consider a migrated issuer holding a PQ key and a verifier whose default policy is any-valid (P0). G1 and G5 hold iff the classical key has been retired (no coexistence) or the verifier holds an *authenticated* per-issuer "PQ required" expectation. If the expectation is absent or unauthenticated, G5 is violated without any Q-day (S1 suffices), and G1 is violated after Q-day (S1+S2).

**TR.** Göç etmiş ve PQ anahtarı olan bir ihraççı ile varsayılan politikası "en az biri geçerli" (P0) olan bir doğrulayıcı düşünelim. G1 ve G5 şu iki koşuldan biri varsa sağlanır, yoksa sağlanmaz:
- klasik anahtar emekliye ayrılmıştır (birlikte yaşama yok),
- doğrulayıcıda ihraççı başına, **kimliği doğrulanmış** bir "PQ zorunlu" beklentisi vardır.

Beklenti yoksa ya da kimliği doğrulanmamışsa G5 Q-day olmadan da ihlal edilir; S1 yeter. G1 ise Q-day'den sonra ihlal edilir (S1+S2).

**Lemma:**
```
lemma G1_claims_unforgeability:
  "All I c #m #j. Migrated(I) @ #m & Accept(I, c) @ #j ==> (Ex #i. Issued(I, c) @ #i & #i < #j)"
lemma G5_no_classical_acceptance:
  "All I c #m #j. Migrated(I) @ #m & AcceptVia(I, c, 'classical') @ #j ==> F"
lemma S1_downgrade_trace:   /* bilgi: Q-day'siz downgrade */
  exists-trace "Ex I c #m #j. Migrated(I) @ #m & AcceptVia(I, c, 'classical') @ #j & not (Ex #q. QdayEv() @ #q)"
```

**Tamarin'in doğruladığı koşul:** G1 ve G5 verified ⇔ `NO_COEXIST ∨ EXPECT_AUTH`. Bu, 6 yapılandırmanın 6'sında sağlanıyor. `S1_downgrade_trace` yalnız `M_expect_unauth` ve `M_expect_absent`'te verified; öbür 4 yapılandırmada falsified (`ozet.csv`).

**Datalog eşlemesi:**
- `coexist(cred) ⇔ ¬NO_COEXIST`.
- `EXPECT_AUTH ⇔ convey(cfg,cred)`; `cfg` sahtelenemez.
- `EXPECT_UNAUTH ⇔ convey(net,cred)`; `net` sahtelenebilir.

**İzler:**
- **G5 ihlali (her iki mutant):** `Migrated_Issuer_Setup, Issue_Migrated, Verify_Classical`.
  - İzde Q-day de kırılma da yok: Dürüstçe ikili ihraç edilmiş klasik kopya klasik yoldan kabul ediliyor.
  - `M_expect_unauth` varyantında `pq_required` dışındaki beklenti değerini ağdan saldırgan sağlıyor, çünkü dürüst duyuru kuralı izde yok.
- **G1 ihlali:** `Migrated_Issuer_Setup, Qday, CRQC_Break_Issuer_Classical, Verify_Classical`.

**Kapsam denetimi (varlık başına):** `executable_legacy` 6 varyantın 6'sında verified. Klasik yol eski ihraççı için her varyantta çalışıyor. Yani koruma, klasik yolun toptan kapatılmasından değil, varlık başına beklentiden geliyor.

### 2.3 R3 — kanal (`modeller\R3_channel.spthy`)

**EN.** Under coexistence, let the per-issuer expectation reach the verifier over a channel authenticated by key `k_ch`. The channel is either an object signature (TL/LoTE entry, signed metadata) or a nonce-bound transport session with the authoritative source. G1 and G5 hold iff `k_ch` is PQ. If `k_ch` is classical, every downgrade of a migrated issuer requires a CRQC break, so the channel is sound before Q-day. After Q-day there is a trace that forges "PQ not required" and then accepts classical-only evidence (G5) or a forged classical credential (G1).

**TR.** Birlikte yaşama döneminde, ihraççı başına beklenti doğrulayıcıya `k_ch` anahtarıyla doğrulanan bir kanaldan ulaşsın. Kanal iki biçimde olabilir:
- nesne imzası (TL/LoTE kaydı, imzalı meta veri),
- yetkili kaynakla nonce'a bağlı bir taşıma oturumu.

G1 ve G5 ancak ve ancak `k_ch` PQ ise sağlanır. `k_ch` klasikse, göç etmiş ihraççının her downgrade'i bir CRQC kırılması gerektirir; kanal Q-day'e kadar sağlamdır. Q-day'den sonra "PQ gerekmez" beklentisini sahteleyen bir iz vardır. Bu izin devamında ya yalnız klasik kanıt kabul edilir (G5) ya da sahte bir klasik kimlik bilgisi kabul edilir (G1).

**Lemma:** G1 ve G5 R2'dekiyle aynı. Ek sağlık lemması:
```
lemma attack_needs_crqc_G5:
  "All I c #m #j. Migrated(I) @ #m & AcceptVia(I, c, 'classical') @ #j ==> (Ex k #b. Broken(k) @ #b & #b < #j)"
```

**Tamarin'in doğruladığı koşul:**
- G1 ve G5 verified ⇔ `CHAN_PQ`. Bu, iki kanal türünde de, 4 yapılandırmanın 4'ünde sağlanıyor.
- `attack_needs_crqc_G5` 4 yapılandırmanın 4'ünde verified.

**Datalog eşlemesi:** `CHAN_PQ ⇔ pq(chan)`, `anchored(chan)`, `convey(chan,cred)`. `VIA_TLS`'in Datalog karşılığı yoktur.

**İzler:**
- **`M_obj_classical`, G5:** `Channel_Setup, Qday, CRQC_Break_Channel, Migrated_Issuer_Setup, Issue_Migrated, Verify_Classical`.
  - Yalnız kanal anahtarı kırılıyor; dürüst klasik kopya kabul ediliyor.
- **`M_obj_classical`, G1:** Kanal anahtarı ve ihraççının klasik anahtarı birlikte kırılıyor.
- **`M_tls_classical`:** Aynı izler, ayrıca `Verifier_Fetch`.

**H1 notu:**
- Beklenti durağan olduğu sürece nesne imzası ve taşıma katmanı aynı hükmü verir. Tazelik farkı ancak beklenti zamanla değiştiğinde ortaya çıkar (R7).
- Aktarılan artefaktın yetkili kaynakla kimliği doğrulanmış bir oturumu yoktur. Bu durum R2'nin `EXPECT_UNAUTH` varyantına karşılık gelir.

### 2.4 R4 — WSCD cihaz anahtarı (`modeller\R4_wscd.spthy`)

**EN.** Presentation unforgeability / holder binding (G2) holds iff both keys are PQ: the device key bound as `cnf` and exercised in the KB-JWT, and the issuer key. With a classical device key there is a trace in which a genuinely issued, PQ-signed credential is presented with a KB-JWT forged for a fresh verifier nonce. In that trace the device key is extracted from its observed `cnf` public key. Wallet-side one-time use combined with global verifier-side single use does not remove this trace.

**TR.** Sunum sahtelenemezliği / holder binding (G2) ancak ve ancak iki anahtar da PQ ise sağlanır: `cnf` olarak bağlanan ve KB-JWT'yi imzalayan cihaz anahtarı ile ihraççı anahtarı. Cihaz anahtarı klasikse şöyle bir iz vardır:
- cihaz anahtarı, gözlenen `cnf` açık anahtarından çıkarılır,
- gerçekten ihraç edilmiş, PQ imzalı kimlik bilgisi taze bir doğrulayıcı nonce'u için sahte bir KB-JWT ile sunulur.

Cüzdan tarafında tek kullanım ve doğrulayıcı tarafında küresel tek kullanım birlikte uygulansa bile bu iz ortadan kalkmaz.

**Lemma:**
```
lemma G2_presentation_unforgeability:
  "All I c pkd n #j. AcceptPres(I, c, pkd, n) @ #j ==> (Ex #p. Presented(pkd, n) @ #p & #p < #j)"
```

**Tamarin'in doğruladığı koşul:** G2 verified ⇔ `DEV_PQ ∧ ISS_PQ`. Bu, 4 yapılandırmanın 4'ünde ve 2 `SINGLE_USE` varyantında sağlanıyor.

**Datalog eşlemesi:** `DEV_PQ ⇔ pq(kb)`, `ISS_PQ ⇔ pq(cred)`, `signed_under(kb,cred)`, `anchored(cred)`.

**İzler:**
- **`M_dev`:** `Issuer_Setup, Issue, Holder_Present, Qday, CRQC_Break_Device, Verifier_Challenge, Verifier_Accept`.
  - Kimlik bilgisi bir kez görünüyor; bu, toplama anı.
  - Ardından sahte KB-JWT ile kabul ediliyor.
- **`M_iss`:** `Issuer_Setup, Qday, CRQC_Break_Issuer, Verifier_Challenge, Verifier_Accept`.
  - İzde `Issue` ve `Holder_Present` yok: Saldırgan kendi cihaz anahtarını bağlayan bir kimlik bilgisini kendisi sahteliyor.

**H5 ön sinyali:**
- `H5_single_use_dev_classical` varyantında G2 falsified ve `M_device_key_classical` verified.
- Tek kullanım kısıtlarının gerçekten etkili olduğunu `executable_single_use_enforced` gösteriyor (2/2 verified).

### 2.5 R5 — çıpa (`modeller\R5_anchor.spthy`)

**EN.** With a PQ issuer key and the chain LOTL → TL → `cred`, G1 holds iff the TL signing key is PQ and either the TL key is pinned out of band or the LOTL key is PQ. In particular, a pinned PQ TL key makes G1 independent of the LOTL key type, whereas pinning a classical TL key does not help.

**TR.** İhraççı anahtarı PQ ve zincir LOTL → TL → `cred` olsun. G1 ancak ve ancak şu iki koşul birlikte sağlanırsa geçerlidir:
- TL imza anahtarı PQ'dur,
- TL anahtarı bant dışı sabitlenmiştir ya da LOTL anahtarı PQ'dur.

Sonuç olarak, sabitlenmiş bir PQ TL anahtarı G1'i LOTL anahtarının türünden bağımsız kılar. Klasik bir TL anahtarını sabitlemek ise işe yaramaz.

**Lemma:** G1, R1'dekiyle aynı. Mutasyon lemmaları:
- `M_pin_removed`: TL sabitlenmemiş ve LOTL klasik; izde `Broken('lotl')` var.
- `M_anchor_classical`: TL anahtarı klasik; izde `Broken('tl')` var.

**Tamarin'in doğruladığı koşul:** G1 verified ⇔ `TL_PQ ∧ (PIN_TL ∨ LOTL_PQ)`. Bu, 8 yapılandırmanın 8'inde sağlanıyor.

**Datalog eşlemesi:**
- `PIN_TL ⇔ anchored(tl)`, `TL_PQ ⇔ pq(tl)`, `LOTL_PQ ⇔ pq(lotl)`.
- `anchored(lotl)`, `signed_under(tl,lotl)`, `signed_under(cred,tl)`, `pq(cred)`.

**İzler:**
- **`M_pin`:** `LOTL_Setup, Qday, CRQC_Break_LOTL, Verify_via_LOTL`.
  - Saldırgan LOTL işaretçisini kendi TL anahtarına yöneltiyor. `TL_Setup` izde yok.
- **`M_tl`:** `LOTL_Setup, TL_Setup, Pin_TL_Out_Of_Band, Qday, CRQC_Break_TL, Verify_Pinned_TL`.

## 3. Sonuç tablosu (34 varyant)

**Kısaltmalar ve sütunlar:**
- **V** verified, **F** falsified demektir. Exists-trace lemmada V "iz bulundu", F "iz yok" anlamına gelir.
- **Sağlık:** Varyanttaki sağlık lemmalarından kaçının verified çıktığı.
- **Lemma:** Varyantta koşan lemma sayısı.
- **Süre:** Varyanttaki lemma koşumlarının en uzunu. Konteyner içinde duvar saatiyle ölçüldü; Tamarin başlangıcı ve Maude dahil, konteyner açılışı hariç.
- **Bellek:** cgroup `memory.peak` değeri; Maude dahil.

| Kural | Varyant | Rol | Bayraklar (`-D`) | Güvenlik | Mutasyon / ek lemma | Sağlık | Lemma | Maks. süre (s) | Maks. bellek (MiB) | Beklendiği gibi |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | `P_all_pq` | korumalı | ROOT_PQ, CA_PQ, ISS_PQ | G1 V | - | 3/3 | 4 | 1,32 | 75,5 | EVET |
| R1 | `M_root` | mutant | CA_PQ, ISS_PQ | G1 F | M_root_classical V | 3/3 | 5 | 1,47 | 84,4 | EVET |
| R1 | `M_ca` | mutant | ROOT_PQ, ISS_PQ | G1 F | M_ca_classical V | 3/3 | 5 | 1,38 | 84,9 | EVET |
| R1 | `M_iss` | mutant | ROOT_PQ, CA_PQ | G1 F | M_issuer_classical V | 3/3 | 5 | 1,35 | 77,7 | EVET |
| R1 | `E_iss_only` | ek | ISS_PQ | G1 F | M_root_classical V · M_ca_classical V | 3/3 | 6 | 1,58 | 94,2 | EVET |
| R1 | `E_ca_only` | ek | CA_PQ | G1 F | M_root_classical V · M_issuer_classical V | 3/3 | 6 | 1,55 | 93,6 | EVET |
| R1 | `E_root_only` | ek | ROOT_PQ | G1 F | M_ca_classical V · M_issuer_classical V | 3/3 | 6 | 1,48 | 89,4 | EVET |
| R1 | `E_none` | ek | - | G1 F | M_root_classical V · M_ca_classical V · M_issuer_classical V | 3/3 | 7 | 1,58 | 95,7 | EVET |
| R1 | `X_alt_ca` | ek-sınır | ROOT_PQ, CA_PQ, ISS_PQ, ALT_CA | G1 F | X_alt_ca_forges_honest_issuer V | 3/3 | 5 | 1,47 | 89,8 | EVET |
| R1 | `X_alt_ca_namebind` | ek-sınır | ROOT_PQ, CA_PQ, ISS_PQ, ALT_CA, NAME_BIND | G1 V | - | 3/3 | 4 | 1,52 | 76,1 | EVET |
| R2 | `P_expect_auth` | korumalı | EXPECT_AUTH | G1 V · G5 V | - | 4/4 | 7 | 0,96 | 78,1 | EVET |
| R2 | `M_expect_unauth` | mutant | EXPECT_UNAUTH | G1 F · G5 F | M_expectation_unauthenticated V | 4/4 | 8 | 0,97 | 76,3 | EVET |
| R2 | `M_expect_absent` | mutant | - | G1 F · G5 F | M_expectation_absent V | 4/4 | 8 | 0,88 | 76,6 | EVET |
| R2 | `E_nocoexist_auth` | ek | NO_COEXIST, EXPECT_AUTH | G1 V · G5 V | - | 4/4 | 7 | 0,84 | 75,8 | EVET |
| R2 | `E_nocoexist_unauth` | ek | NO_COEXIST, EXPECT_UNAUTH | G1 V · G5 V | - | 4/4 | 7 | 0,87 | 75,8 | EVET |
| R2 | `E_nocoexist_none` | ek | NO_COEXIST | G1 V · G5 V | - | 4/4 | 7 | 0,81 | 75,6 | EVET |
| R3 | `P_obj_pq` | korumalı | CHAN_PQ | G1 V · G5 V | - | 5/5 | 7 | 1,29 | 78,0 | EVET |
| R3 | `P_tls_pq` | korumalı | CHAN_PQ, VIA_TLS | G1 V · G5 V | - | 5/5 | 7 | 1,44 | 80,0 | EVET |
| R3 | `M_obj_classical` | mutant | - | G1 F · G5 F | M_channel_classical V | 5/5 | 8 | 1,27 | 78,6 | EVET |
| R3 | `M_tls_classical` | mutant | VIA_TLS | G1 F · G5 F | M_channel_classical V | 5/5 | 8 | 1,56 | 78,4 | EVET |
| R4 | `P_dev_iss_pq` | korumalı | DEV_PQ, ISS_PQ | G2 V | - | 3/3 | 4 | 1,5 | 80,2 | EVET |
| R4 | `M_dev` | mutant | ISS_PQ | G2 F | M_device_key_classical V | 3/3 | 5 | 1,46 | 81,7 | EVET |
| R4 | `M_iss` | mutant | DEV_PQ | G2 F | M_issuer_classical V | 3/3 | 5 | 1,4 | 81,7 | EVET |
| R4 | `E_none` | ek | - | G2 F | M_device_key_classical V · M_issuer_classical V | 3/3 | 6 | 1,57 | 84,9 | EVET |
| R4 | `H5_single_use_dev_classical` | ek-H5 | ISS_PQ, SINGLE_USE | G2 F | M_device_key_classical V | 4/4 | 6 | 1,46 | 83,7 | EVET |
| R4 | `H5_single_use_protected` | ek-H5 | DEV_PQ, ISS_PQ, SINGLE_USE | G2 V | - | 4/4 | 5 | 1,41 | 76,8 | EVET |
| R5 | `P_pin_tlpq` | korumalı | PIN_TL, TL_PQ | G1 V | - | 3/3 | 4 | 1,0 | 75,0 | EVET |
| R5 | `M_pin` | mutant | TL_PQ | G1 F | M_pin_removed V | 3/3 | 5 | 1,48 | 84,6 | EVET |
| R5 | `M_tl` | mutant | PIN_TL | G1 F | M_anchor_classical V | 3/3 | 5 | 1,08 | 75,1 | EVET |
| R5 | `E_none` | ek | - | G1 F | M_pin_removed V · M_anchor_classical V | 3/3 | 6 | 1,56 | 92,5 | EVET |
| R5 | `E_lotlpq` | ek | LOTL_PQ | G1 F | M_anchor_classical V | 3/3 | 5 | 1,4 | 84,1 | EVET |
| R5 | `E_lotlpq_tlpq` | ek | LOTL_PQ, TL_PQ | G1 V | - | 3/3 | 4 | 1,32 | 73,8 | EVET |
| R5 | `E_pin_lotlpq` | ek | PIN_TL, LOTL_PQ | G1 F | M_anchor_classical V | 3/3 | 5 | 0,98 | 76,0 | EVET |
| R5 | `E_all_pq_pin` | ek | PIN_TL, TL_PQ, LOTL_PQ | G1 V | - | 3/3 | 4 | 0,89 | 74,4 | EVET |

Kaynak: `sonuc\varyant_ozeti.csv`. Lemma başına ayrıntı `sonuc\ozet.csv` ve `sonuc\degerlendirme.csv` dosyalarında.

**Genel dağılım** (`ozet.csv`, `degerlendirme.csv`):
- **Sonuçlar:** 196 lemma koşumunun 167'si verified, 29'u falsified.
- **Türler:** 118 sağlık, 44 güvenlik, 27 mutasyon, 6 bilgi (`S1_downgrade_trace`), 1 sınır (`X_alt_ca_forges_honest_issuer`).
- **Lemma başına süre:** en az 0,64 s, medyan 1,22 s, en çok 1,58 s. Toplam 228,4 s.
- **Bellek:** en az 69,0 MiB, medyan 75,8 MiB, en çok 95,7 MiB.
- **İspat/iz adım sayısı:** 2 ile 19 arasında.
- **Toplu koşum süresi:** 230 konteyner açılışı dahil 00:02:33 ile 00:12:34 arasında sürdü (`calistir_log.txt`).

## 4. Mutasyon skoru

**Tanım** (`betik\degerlendir.py`). Bir koruma, kaldırıldığı tek-mutant varyantta şu iki koşul birlikte sağlanırsa "öldürülmüş" sayılır:
- bütün güvenlik lemmaları falsified,
- `M_` lemması verified; yani saldırı izi kaldırılan korumaya bağlı olaydan geçiyor (§1.2):
  - anahtar korumalarında o anahtarın kırılması,
  - R2'de beklentisiz ya da `'none'` beklentisiyle klasik yoldan kabul.

**Skor: 11/11 = %100** (`metrikler.txt`).

| Kural | Kaldırılan koruma | Mutant | Güvenlik | Mutasyon lemması | Güvenlik izindeki CRQC kırılması | Sonuç |
|---|---|---|---|---|---|---|
| R1 | kök anahtarı PQ | `M_root` | G1 F | M_root_classical V | G1: CRQC_Break_Root | ÖLDÜ |
| R1 | CA anahtarı PQ | `M_ca` | G1 F | M_ca_classical V | G1: CRQC_Break_CA | ÖLDÜ |
| R1 | ihraççı imzası PQ | `M_iss` | G1 F | M_issuer_classical V | G1: CRQC_Break_Issuer | ÖLDÜ |
| R2 | beklentinin kimlik doğrulaması | `M_expect_unauth` | G1 F · G5 F | M_expectation_unauthenticated V | G1: CRQC_Break_Issuer_Classical; G5: - | ÖLDÜ |
| R2 | beklenti | `M_expect_absent` | G1 F · G5 F | M_expectation_absent V | G1: CRQC_Break_Issuer_Classical; G5: - | ÖLDÜ |
| R3 | PQ kanal (nesne imzası) | `M_obj_classical` | G1 F · G5 F | M_channel_classical V | G1: CRQC_Break_Channel+CRQC_Break_Issuer_Classical; G5: CRQC_Break_Channel | ÖLDÜ |
| R3 | PQ kanal (taşıma) | `M_tls_classical` | G1 F · G5 F | M_channel_classical V | G1: CRQC_Break_Channel+CRQC_Break_Issuer_Classical; G5: CRQC_Break_Channel | ÖLDÜ |
| R4 | PQ cihaz anahtarı | `M_dev` | G2 F | M_device_key_classical V | G2: CRQC_Break_Device | ÖLDÜ |
| R4 | PQ ihraççı imzası | `M_iss` | G2 F | M_issuer_classical V | G2: CRQC_Break_Issuer | ÖLDÜ |
| R5 | sabitleme | `M_pin` | G1 F | M_pin_removed V | G1: CRQC_Break_LOTL | ÖLDÜ |
| R5 | çıpa anahtarı PQ | `M_tl` | G1 F | M_anchor_classical V | G1: CRQC_Break_TL | ÖLDÜ |

Kaynak: `sonuc\metrikler.txt`, `sonuc\varyant_ozeti.csv`, `sonuc\izler.csv`.

**Tabloyu okurken:**
- **"G5: -":** G5 izinde hiçbir kırılma yok. Downgrade Q-day olmadan, S1 ile gerçekleşiyor (§2.2).
- **R2/R3 G1 izleri:** Bu izlerde ihraççının klasik anahtarının kırılması da var. Bu anahtar bir koruma değil, birlikte yaşamanın öncülüdür (`coexist`).
- **Tek-mutant izlerinde kırılan anahtarlar:** Kaldırılan korumanın anahtarı ve (varsa) yalnız bu öncül. Başka bir korumanın anahtarı kırılmıyor.
- **Tek-mutant dışı:** Ek varyantlarda da her `M_` lemması verified. Toplam 27/27 (`ozet.csv`). Yani kalan her klasik anahtar tek başına bir saldırıya yetiyor; bu, K1/K2 ile tutarlı (§6).

## 5. Sağlık lemmaları

| Lemma | Verified / koşum |
|---|---|
| `executable` | 34/34 |
| `executable_post_qday` | 34/34 |
| `attack_needs_crqc` | 34/34 |
| `executable_legacy` | 10/10 |
| `attack_needs_crqc_G5` | 4/4 |
| `executable_single_use_enforced` | 2/2 |
| **Toplam** | **118/118** |

Kaynak: `sonuc\ozet.csv`. Bütün sağlık lemmaları verified: 118/118.

| Lemma | Neyi gösterir |
|---|---|
| `executable` (exists-trace) | Dürüst ihraç → kabul (R4'te ihraç → sunum → kabul) her varyantta erişilebilir. Kısıtlar (`Eq`, `Unique`, tek kullanım) modeli boşaltmıyor. H0'ın "model çalıştırılabilir" maddesi budur. |
| `executable_post_qday` | Dürüst kabul Q-day'den **sonra** da mümkün. Korumalı varyantlardaki "verified", Q-day sonrası kabul imkânsız olduğu için boş yere çıkmış değil. |
| `attack_needs_crqc` (all-traces) | G1/G2 biçimindeki her ihlalden önce bir `Broken(k)` var. Model Q-day öncesinde sağlam; klasik kriptografi yapay olarak kırılmıyor. Her falsified sonucun nedeni CRQC. |
| `executable_legacy` (R2, R3) | Eski ihraççının klasik yolu her varyantta çalışıyor. R3'te bu yol kanalı gerçekten tüketiyor (`UsedExpectation(L,'none')`). Koruma varlık başına; klasik yol toptan kapatılmış değil. |
| `attack_needs_crqc_G5` (R3) | Kimliği doğrulanmış bir kanalda (klasik olsa da) göç etmiş ihraççının her downgrade'i bir kırılma gerektiriyor. Kanal Q-day'e kadar sağlam. |
| `executable_single_use_enforced` (R4, `SINGLE_USE`) | Tek kullanım kısıtları gerçekten işliyor; bir kimlik bilgisi en çok bir kez kabul ediliyor. H5 izi boş bir kısıttan kaynaklanmıyor. |

**Model düzeyindeki diğer sağlık denetimleri** (ham çıktılardan):
- **İyi biçimlilik:** 34 liste koşumunun 34'ünde "All wellformedness checks were successful" (`sonuc\ham\*__liste.txt`; `uyarilar.txt` boş).
  - Pilot `weakest_link.spthy`, `Qday` adını hem eylem hem durum olgusu olarak kullandığı için Tamarin 1.12'de "Fact multiplicity" uyarısı veriyordu.
  - Bu modellerde adlar ayrıldı: eylem `QdayEv()`, durum olgusu `!CRQC()`.
- **Kaynak doyurma:**
  - Kaynak doyurmaya giren 194 lemma koşumunun hepsinde doyurma 1. adımda bitti ("Saturating Sources … Step 1 (Max 5) … Done").
  - Kalan 2 koşum (`executable_single_use_enforced`) doğrudan kısıttan 2 adımda kapandı.
  - Hiçbir ham çıktıda "partial deconstruction" ifadesi yok (0/230).
- **Çıkış kodları:** 230 koşumun hepsinde `rc=0` (`sonuc\ham\*.meta`).
- **H0 ile bağ:** H0 ayrıca "en az biri geçerli politikasında soyma izi"ni istiyor. Bunun modeldeki karşılığı `R2 M_expect_absent` varyantında `S1_downgrade_trace = V`.
  - Bu, P0 altında ikili ihraçta klasik kopyanın kabulü; çoklu imzalı nesnede PQ imzasını soymanın sembolik karşılığı.
  - Q-day'siz bir izdir.

## 6. Datalog karşılığı ve soyutlama bağı

### 6.1 Çekirdek kurallar (`modeller\datalog\core.lp`)

Çekirdek, pilot P2'deki dört kuralın aynısıdır (denetim-B §3.3). Anlam Q-day sonrası içindir:

| Yüklem | Anlam |
|---|---|
| `pq(L)` | `L`'yi **imzalayan** anahtar PQ'dur |
| `classical(L)` | `L`'yi imzalayan anahtar klasiktir |
| `signed_under(L,P)` | `L`'yi imzalayan anahtarı `P` bağlar |
| `anchored(L)` | `L`'yi imzalayan anahtar bant dışı sabitlenmiştir |
| `convey(C,X)` | `X`'e ilişkin beklenti `C` kanalıyla taşınır |
| `coexist(L)` | `L`'nin klasik ve PQ biçimi birlikte geçerlidir |

```
K1  forgeable(L) :- classical(L).
K2  forgeable(L) :- signed_under(L,P), forgeable(P), not anchored(L).
K3  expected(X)  :- convey(C,X), not forgeable(C).
K4  forgeable(L) :- pq(L), coexist(L), not expected(L).
G5 karşılığı (örnek dosyalarında):  violated(g5) :- coexist(X), not expected(X).
```

**Örnek dosyaları.**
- `R1_chain.lp` … `R5_anchor.lp` dosyaları Tamarin `-D` bayraklarını aynı adlarla, küçük harfle `flag/1` olgusu olarak alır.
- `betik\degerlendir.py` her varyant için clingo'yu çalıştırır ve tek kararlı modeli bekler. Bu, 34 yapılandırmanın 34'ünde sağlandı; aksi hâlde betik hata verirdi.

### 6.2 Kural → Datalog eşlemesi

Son sütundaki kapalı biçimler [Y]: kurallardan elle türetildi. clingo'nun 34 yapılandırmada ürettiği tahminler bu kapalı biçimlerle aynı (`datalog_uyum.csv`).

| Kural | Datalog kuralları | İhlal atomu | İhlalin kapalı biçimi [Y] |
|---|---|---|---|
| R1 | K1 + K2 | `violated(g1) :- forgeable(cred)` | `¬pq(cred) ∨ ¬pq(iss_cert) ∨ ¬pq(ca_cert)` |
| R2 | K3 + K4 | g1: `forgeable(cred)`; g5: `coexist ∧ ¬expected` | `coexist(cred) ∧ ¬convey(cfg,cred)`; `net` sahtelenebilir olduğundan `EXPECT_UNAUTH` beklenti sağlamaz |
| R3 | K3 + K4 | R2'deki gibi | `¬pq(chan)`; iki kanal türünde aynı |
| R4 | K1 + K2 | `violated(g2) :- forgeable(kb)` | `¬pq(kb) ∨ ¬pq(cred)` |
| R5 | K1 + K2 (`not anchored` koruması) | `violated(g1) :- forgeable(cred)` | `¬pq(tl) ∨ (¬anchored(tl) ∧ ¬pq(lotl))` |

### 6.3 Uyum: clingo tahmini ↔ Tamarin hükmü

| Kural | Yapılandırma | Güvenlik lemması satırı | `sem=class` uyumu | `sem=naive` uyumu |
|---|---|---|---|---|
| R1 | 10 | 10 | 10/10 | 9/10 |
| R2 | 6 | 12 | 12/12 | 12/12 |
| R3 | 4 | 8 | 8/8 | 8/8 |
| R4 | 6 | 6 | 6/6 | 6/6 |
| R5 | 8 | 8 | 8/8 | 8/8 |
| **Toplam** | **34** | **44** | **44/44** | **43/44** |

Kaynak: `sonuc\datalog_uyum.csv`, `sonuc\metrikler.txt`.
- Karşılaştırma şöyle yapıldı: Datalog `violated(g)` türetiyorsa Tamarin'den `falsified`, türetmiyorsa `verified` beklendi.
- `SINGLE_USE`'un Datalog karşılığı yok. Tahmin değişmedi ve Tamarin de değişmeyen hükmü verdi. Bu, H5 ile tutarlı.

### 6.4 Tamarin sonuçları Datalog kurallarını neden destekliyor?

"Kanıtlanmış soyutlama"nın bağı her örnekte iki yönlü kuruldu.

**(⇒) Kural ateşlenirse saldırı vardır.** Datalog'un ihlal türettiği her yapılandırmada Tamarin somut bir iz buldu. Her kuralın tek başına ateşlenmesini ayrı bir `M_` lemması tanıklıyor:
- **K1 (klasik halka sahtelenebilir):**
  - `M_issuer_classical` (R1): halkanın kendi imza anahtarı klasik.
  - `M_device_key_classical` (R4): KB-JWT'nin anahtarı klasik; kimlik bilgisi gerçek.
  - `M_anchor_classical` (R5): sabitlenmiş çıpanın kendisi klasik.
- **K2 (sahtelenebilirlik aşağı yayılır):**
  - `M_ca_classical` (R1): bir düzey yayılma.
  - `M_root_classical` (R1): iki düzey yayılma; izde dürüst CA ve ihraççı kuralı yok (§2.1).
  - `M_issuer_classical` (R4): sahte `cred` üzerinden `kb`'ye yayılma, yani cnf ikamesi.
  - `M_pin_removed` (R5): lotl → tl → cred yayılması.
- **K3 (beklenti yalnız sahtelenemez kanalla taşınır):**
  - `M_channel_classical` (R3): `forgeable(chan)` beklentiyi düşürüyor.
  - `M_expectation_unauthenticated` (R2): `net` kanalı beklentiyi düşürüyor.
- **K4 (PQ imzalı halka birlikte yaşamada beklentisiz sahtelenebilir):**
  - `M_expectation_absent` ve `M_expectation_unauthenticated` (R2): PQ yolu olan kimlik bilgisi klasik yoldan sahteleniyor.

**(⇐) Kural ateşlenmezse saldırı yoktur.** Datalog'un ihlal türetmediği her yapılandırmada Tamarin all-traces lemmasını kanıtladı. Kanıtlar sınırsız ispattır (`--bound` yok). Yani bu örneklerde K1–K4'ün dışında kalan bir saldırı yok. Kuralların koruyucu koşullarını da doğrulanmış sonuçlar tanıklıyor:
- **K2'deki `not anchored(L)`:** `R5 P_pin_tlpq` verified. Datalog'da `forgeable(lotl)` doğru olduğu hâlde (LOTL klasik) sahtelenebilirlik sabitlenmiş TL'ye geçmiyor.
- **K4'teki `coexist(L)`:** `R2 E_nocoexist_none` hiç beklenti olmadan verified.
- **K3'teki `not forgeable(C)`:** `R3 P_obj_pq` ile `P_tls_pq` ve `R2 P_expect_auth` verified.

**Sonuç.** Her şema örneğinde güvensiz yapılandırmaların kümesi Datalog'da ve Tamarin'de aynı (44/44). Katman 1 kurallarının her ateşlenmesi bir Tamarin iziyle haklılaşıyor. Bu örneklerde kuralların saldırıları eksiksiz kapsadığını da Tamarin ispatları gösteriyor.

**Bağın göstermedikleri:**
- 13 artefaktlı tam modele genelleme. Bu, birleştirilebilirlik gerekçesi ile Katman 3'teki soyutlama örneklemesinin işi.
- Zaman ve τ (R6), geri alma ve tekdüzelik (R7).
- Bir sınıfın bütün üyeleri üzerinden okuma (aşağıda §6.5).

### 6.5 `X_alt_ca`: naif kenar semantiği alternatif yol saldırısını kaçırıyor

**Kurulum** (`R1 X_alt_ca`):
- Bayraklar: `ROOT_PQ, CA_PQ, ISS_PQ` ve `ALT_CA`.
- İhraççının kendi zinciri (kök → CA → ihraççı) tamamen PQ.
- Aynı kök altında ikinci bir CA var ve anahtarı klasik: CA sınıfı kısmen göç etmiş.
- Doğrulayıcı, kökün sertifikaladığı **her** CA'nın imzaladığı `iss_cert`'i kabul ediyor. Ad kısıtı yok.

**Tamarin** (`izler.csv`, `varyant_ozeti.csv`):
- **`X_alt_ca`:** `G1 = F`. İz: `AltCA_Setup, Qday, CRQC_Break_AltCA, Verify` (+ `Root_Setup`).
- **`X_alt_ca_forges_honest_issuer = V`:** İzde dürüst ihraççı kendi PQ CA'sıyla kurulu (`CA_Setup, Issuer_Setup`). Saldırgan yine de o ihraççının adıyla kimlik bilgisi sahteliyor, çünkü alternatif CA'nın klasik anahtarını kırıyor.
- **`X_alt_ca_namebind`:** Doğrulayıcı ihraççıyı kendi CA'sına bağlıyor (`NAME_BIND`). Sonuç: `G1 = V`.

**Datalog** (`metrikler.txt`):
- **`sem=naive` (pilotun örtük okuması):** Yalnız gerçek ebeveyne bakıyor (`signed_under(iss_cert, ca_cert)`, `pq(iss_cert) ⇔ CA_PQ`). "İhlal yok" diyor. 44 satırdaki **tek** uyumsuzluk bu: `R1 X_alt_ca g1: naive=verified tamarin=falsified`.
- **`sem=class`:** `pq(iss_cert)` ancak doğrulayıcının bu ihraççının sertifikası için imzacı olarak **kabul ettiği bütün** CA anahtarları PQ ise doğru. Kural: `alt_acceptable :- flag(alt_ca), not flag(name_bind)`. Bu semantik ihlali doğru tahmin ediyor. `NAME_BIND` altında iki semantik de "güvenli" diyor ve Tamarin'le uyuşuyor.

**Anlamı.** Bir halkanın sahtelenebilirliğini, o halkayı **gerçekte** imzalayan anahtar belirlemez. Belirleyen, doğrulayıcının o halka için imzacı olarak **kabul edeceği** anahtarların en zayıfıdır. Naif kenar semantiği yalnız gerçek imza kenarını izlediği için alternatif yol saldırısını göremiyor. Anahtar sınıfı ("kabul edilen imzacılar kümesi") semantiği bu yüzden gerekli.

**DNSSEC'teki karşılığı.** Bu, DNSSEC'in "herhangi bir geçerli yol" kuralıyla aynı yapıdadır. Birincil kaynak açıldı: `01-korpus\metin\RFC6840.txt`.
- **RFC 6840 §5.11:** *"This requirement applies to servers, not validators. Validators SHOULD accept any single valid path."*
- **RFC 6840 §6.2:** *"… there is no way to tell resolvers what a particular DNSKEY is supposed to be used for -- any DNSKEY in the zone's signed DNSKEY RRset may be used to authenticate any RRset in the zone. For example, if a weaker or less trusted DNSKEY is being used to authenticate NSEC RRsets or all dynamically updated records, that same DNSKEY can also be used to sign any other RRsets from the zone."*
- **RFC 6840 Ek C.2 ("Accept Any Success"):** *"… making the validator subject to the compromise of the weakest of these trust anchors …"*

**Eşleme** [Y]:
- "Herhangi bir DNSKEY herhangi bir RRset'i doğrular" ↔ "kökün sertifikaladığı herhangi bir CA herhangi bir ihraççıyı sertifikalar".
- "Zayıf DNSKEY" ↔ "klasik kalmış CA".
- Ad kısıtı ya da ihraççı→CA bağlaması (`NAME_BIND`) ↔ doğrulayıcıya hangi anahtarın neyi imzalayabileceğini söyleyen, kimliği doğrulanmış sinyal. DNSSEC'te bu sinyal yok (§6.2).

`X_alt_ca`, bu yapıyı kimlik bilgisi zincirinde sembolik olarak yeniden üretiyor. KAT-1 bilinen-cevap testinin kendisi Katman 3'ün işi.

**Katman 1'e (ASP) sonuç:**
- `pq(L)` bir artefakt sınıfı üzerinden okunmalı: "doğrulayıcının `L` için kabul ettiği her imzacı PQ".
- Ya da `signed_under` her kabul edilebilir ebeveyni kenar olarak saymalı.
- Ya da kabul kümesini daraltan bir ad bağlama yüklemi eklenmeli.

Aksi hâlde ASP saldırıları eksik sayar ve asgari kümeler olması gerekenden küçük çıkar; bu, güvenlik iddiası için sağlam olmaz. M2 maliyetinde de bir sınıf ancak bütün üyeleri PQ olduğunda (ya da ad kısıtlı olduğunda) "göç etmiş" sayılmalı. Ayrıntı ve öneri: `KARAR-NOTLARI.md`.

## 7. Sonlanmama merdiveni

| Basamak | Uygulama | Kullanıldığı koşum |
|---|---|---|
| 1 `--prove=<lemma>` | Kendiliğinden | **196/196** |
| 2 `[use_induction]` / `[reuse]` | Model düzeyinde, elle | 0 (gerekmedi) |
| 3 `--auto-sources` | Kendiliğinden (1 kapanmazsa) | 0 |
| 4 tactic / oracle | Model düzeyinde, elle | 0 |
| 5 `--bound=40` | Kendiliğinden (3 kapanmazsa) | 0 |
| 6 "kapanmadı" etiketi | Kendiliğinden | 0 |

Kaynak: `sonuc\ozet.csv` (`merdiven_basamagi` sütunu) ve `sonuc\metrikler.txt`.
- Koşum başına en uzun süre 1,58 s, en yüksek bellek 95,7 MiB. 10 dk ve 12 GB sınırlarının çok altında.

**Neden bu kadar hızlı?** [Y]
- Modellerde sınırsız döngü yok. Zincirler sabit uzunlukta; her rolün tek örneği `Unique` kısıtıyla sağlanıyor.
- Pilottaki `delegation_loop.spthy` farklıydı: sınırsız delegasyon döngüsü yardımsız zaman aşımına uğruyor, `[use_induction]` ile kapanıyordu (`arac\README.md`).
- R6/R7'de sayaç, sürüm ya da epoch gibi yinelenen yapılar gelecek. Orada 2. basamak (tümevarım lemması) büyük olasılıkla gerekecek (tahmin).

## 8. Sınırlılıklar

1. **Sembolik model.**
   - İmzalar ideal. Algoritma karışıklığı, hibrit/composite birleştiricinin zayıf ayrılamazlığı (WNS), kodlama ve uzunluk saldırıları kapsam dışı.
   - "Klasik" ile "PQ" arasındaki tek fark, anahtarın Q-day sonrasında çıkarılabilmesi.
2. **CRQC soyutlaması.**
   - Q-day tek bir küresel olay. Çıkarma anlık (τ=0), pencere başına anahtar sınırı yok (k=∞).
   - Anahtar başına süre ve rejimler (hızlı/orta/yavaş) modellenmedi. Bu R6'nın konusu.
3. **Zaman boyutu yok.**
   - Geçerlilik süreleri, kabul ve açıkta kalma pencereleri, eski-sürüm penceresi ve sunset modellenmedi.
   - Bu yüzden G5 **zamansız** biçimde: "göç etmiş varlık hiçbir zaman yalnız klasik kanıtla kabul edilmez".
   - Karar belgesindeki (§7.4) "ilan ettiği eski-sürüm penceresi dışında" ifadesi R6/R7'de modellenecek.
4. **Anahtar yeniden kullanımı yok.**
   - Aynı anahtarın birden çok rolde (ör. TLS ve nesne imzası) ya da birden çok pencerede kullanılması modellenmedi.
   - Cihaz anahtarı kimlik bilgisi başına tazedir. Bu konu R6/R7'de ele alınacak.
5. **Küçük örnekler.**
   - Her rolün tek örneği var (`Unique` kısıtları). Yalnız R1'in ek-sınır varyantında ikinci bir CA bulunuyor.
   - Datalog–Tamarin uyumu bu örnekler üzerinde gösterildi. Genel bir teorem değildir.
   - Tam 13 artefaktlı modele genelleme, Katman 3 örneklemesi ve birleştirilebilirlik gerekçesiyle kurulacak.
6. **R3'teki taşıma soyutlaması.**
   - TLS, nonce'a bağlı tek bir sunucu kimlik doğrulama imzasına indirgendi. WebPKI zinciri tek bir anahtara katlandı; zincir etkileri R1'de.
   - El sıkışma ayrıntısı ve hibrit KEM gizliliği modellenmedi; ağ saldırganı her şeyi görür.
   - Beklenti durağan olduğundan tazelik farkı sınanmadı (R7).
7. **R4'teki varsayımlar.**
   - Canlı bir sunumun aktarılması (relay) G2 ihlali sayılmadı; kanal bağlaması olmayan KB-JWT için bu standart kabul.
   - İhraç kanalı gizli varsayıldı.
   - `SINGLE_USE` varyantındaki küresel doğrulayıcı durumu idealleştirilmiş ve bilerek en güçlü hâlde; gerçek doğrulayıcılar durum paylaşmaz. Bu varyantın izi bir **ön sinyaldir**; H5'in biçimsel sınaması R6 pencereleriyle yapılacak.
8. **R1 ve R4'ün korumalı varyantları.**
   - Bu iki varyantta hiç klasik anahtar yok; CRQC'ye karşı güvenlik bu yüzden kolay sonuçtur.
   - İçeriği mutantlar ve bayrak uzayının tamamı taşıyor.
   - R2, R3, R5'in korumalı varyantlarında ve R1'in `X_alt_ca_namebind` varyantında CRQC etkin: kırılabilir klasik anahtar var. Orada saldırıyı engelleyen, korumanın kendisi.
9. **Dürüst taraflar.** Kötü niyetli ihraççı ya da TL operatörü kapsam dışı (§7.4).
10. **Doğrulayıcı sayısı.** Her modelde tek bir doğrulayıcı mantığı var. Farklı politikalara sahip doğrulayıcıların bir arada bulunması modellenmedi.
11. **Datalog karşılaştırmasının niteliği.** Karşılaştırma bir Tamarin çıktısı değil, clingo çıktısıdır. Örnek dosyaları bu adımda yazıldı; Adım 3'ün ASP modeliyle birebir aynı değildir. Bağ, çekirdek kurallar (K1–K4) düzeyinde kuruldu.

## 9. Teknik kapıya katkı (Tamarin kısmı)

| Ölçüt (görev tanımı) | Sonuç | Kaynak |
|---|---|---|
| R1–R5'in her birinde korumalı varyant verified, korumasız varyant falsified, `executable` verified | R1–R5 **GEÇTİ** (5/5) | `metrikler.txt` |
| Mutasyon skoru %100 | **11/11 = %100** | `metrikler.txt` |
| Her koşum ≤10 dk ve ≤12 GB | En uzun 1,58 s; en yüksek 95,7 MiB | `ozet.csv` |
| Kapanmayan varsa merdivenle raporlanır | Kapanmayan 0; hepsi 1. basamakta | `ozet.csv` |

**Ek güvence** (kabul ölçütünün ötesinde):
- Beklenen/gözlenen uyumu 196/196.
- Katman 1↔2 (Datalog↔Tamarin) uyumu 44/44.
- Sağlık lemmaları 118/118 verified.
- İyi biçimlilik uyarısı yok.

**Katman 3 için süre kestirimi** (tahmin): Lemma başına medyan süre 1,22 s, konteyner açılışı dahil satır başına yaklaşık 3 s. Buna göre 50–200 örneklik soyutlama örneklemesi, örnek başına ~5 lemmayla dakikalar mertebesinde biter.

**Hüküm:** Teknik kapının Tamarin kısmı **geçti**.

**Kapının açık bıraktıkları:**
- R6 ve R7.
- ASP'nin sınıf semantiği kararı (§6.5).
- Katman 3: soyutlama örneklemesi, bilinen-cevap testleri, ProVerif ikinci görüşü.

## 10. Adım 5 için öneriler

Aşağıdaki tasarımlar önerdir; henüz koşturulmadı. Beklenen sonuçlar tahmindir. Yapı R1–R5 ile aynı olacak:
- bayrak = koruma,
- tek-mutant varyantları,
- `M_` lemmaları,
- sağlık lemmaları,
- Datalog karşılığı ve `betik\` düzeni (lemma başına konteyner, merdiven, JSON iz).

### 10.1 R6 — zaman penceresi (H2, H5; §7.13 "Tamarin R6 örnekleri")

**Önerilen kural ifadesi:**
- Klasik bir `L` halkası ancak şu durumda sahtelenebilir: CRQC, `L`'yi imzalayan anahtarın çıkarılmasını, doğrulayıcı o anahtarı `L` için kabul etmeyi bırakmadan önce bitirebiliyorsa.
- Uzun ömürlü bir anahtarla imzalanan kısa ömürlü artefaktlarda belirleyici pencere artefaktın değil, **anahtarın** penceresidir (anahtar yeniden kullanımı).

**Model taslağı.** Sayısal zaman yok; yalnız olay sırası kullanılıyor, çünkü Tamarin bunu doğrudan destekler.
- **Anahtar penceresi:**
  - `Activate(k)` doğrusal bir `Window(k)` olgusu üretir; `Close(k)` onu tüketir.
  - Doğrulayıcının kabul kuralı `Window(k)`'yi okur (tüket ve yeniden üret). `Close(k)`'den sonra `k` ile kabul imkânsız olur.
- **İki evreli CRQC:**
  - Q-day'den sonra `CRQC_Start(k)` çalışır (`In(pk(k))` gerekir) ve `Extracting(k)` olgusunu üretir.
  - `CRQC_Done(k)` bu olguyu tüketir ve `sk`'yi dışarı verir.
  - Bugünkü tek evreli `CRQC_Break_*` bunun τ=0 hâlidir.
- **τ rejimi, kısıt olarak:**
  - `SLOW` (τ > pencere): `All k #a #d. Activate(k)@a & CRQC_Done(k)@d ==> (Ex #c. Close(k)@c & #c < #d)`.
  - `FAST`: bu kısıt yok.
  - İsteğe bağlı: Tamarin 1.12'nin doğal sayı desteğiyle sayaçlı pencere kurulabilir. Sözdizimi kullanılmadan önce kılavuzdan doğrulanmalı.
- **Bayraklar:**
  - `SLOW`,
  - `SHORT_KEY_WINDOW`: anahtar kısa pencerede döner. Ör. geçerliliği kısa bir kimlik bilgisine bağlı cihaz anahtarı ya da kısa ömürlü durum imza anahtarı.
  - `KEY_REUSE`: imza anahtarı artefakt pencerelerinin ötesinde kullanılmaya devam eder.
- **Beklenen sonuç** (tahmin): İz yalnız `SLOW ∧ SHORT_KEY_WINDOW ∧ ¬KEY_REUSE` durumunda yoktur.
- **Mutantlar:**
  - `SLOW` kaldırılır, yani `FAST` → iz.
  - `SHORT_KEY_WINDOW` kaldırılır → iz.
  - `KEY_REUSE` eklenir → iz.
- **Lemma:** `G_window` (all-traces): Kabul edilen her sahte artefakt için, ilgili `k` anahtarında `CRQC_Done(k) < Close(k)` olmuştur.
- **H5 bağlantısı:** R4 × R6 birleşimi. Cihaz anahtarı klasik, `SINGLE_USE` ve kısa kimlik bilgisi geçerliliği birlikte olsun:
  - `SLOW`'da G2 verified,
  - `FAST`'ta iz.

  Bu, H5'in "yalnızca geçerlilik süresi sınırlar" kısmının biçimsel sınamasıdır.
- **Datalog/ASP karşılığı (sayısal):** `forgeable(L) :- classical(L), key_of(L,K), tau(T), window(K,W), T < W.` ASP A5 ızgarasını tarar; Tamarin her rejim hücresinin sıra-temelli sürümünü doğrular.
- **Merdiven riski:** Döngü yok, yalnız doğrusal olgular var; bu yüzden düşük. Pencere sayaçla kurulursa 2. basamak (`[use_induction]`) gerekebilir.

### 10.2 R7 — tekdüze beklenti (M-f ve A3 bileşen ablasyonu; H3, G5'in zamanlı biçimi)

**Önerilen kural ifadesi:**
- Doğrulayıcı, göç etmiş bir ihraççının beklentisine karşı downgrade'e ve geri almaya (rollback) ancak şu dört koşulla dayanır:
  - kullandığı beklenti PQ ile doğrulanmıştır,
  - taze ya da sabitlenmiştir,
  - doğrulayıcıda tekdüzedir: "PQ zorunlu" bir kez öğrenildiyse daha zayıf bir değerle değiştirilmez,
  - varlık başına kapsamlıdır.
- İlan edilen sunset'ten sonra yalnız klasik kanıt hiçbir zaman kabul edilmez. Bu, G5'in zamanlı biçimidir.

**Model taslağı:**
- **İhraççı yaşam döngüsü:**
  - `Setup(I)`: kayıt `'none'`, sürüm v0.
  - `Migrate(I)`: kayıt `'pq_required'`, sürüm v1.
  - `Sunset(I)`: eski-sürüm penceresinin sonu; klasik anahtar emekliye ayrılır.
- **Kanal (R3'ten):**
  - Kaynak sürümlü nesneler imzalar: `<'expect', I, e, v>`.
  - Saldırgan eski v0 nesnesini kaydeder ve göçten sonra yeniden oynatır. Kanal anahtarı PQ olsa bile bunu yapabilir.
- **Doğrulayıcı seçenekleri (bayrak = bileşen):**
  - `PQ_CHAN`: kanal anahtarı PQ.
  - `FRESH`: nonce'a bağlı taşıma ya da R6 penceresine bağlı nesne.
  - `PINNED`: bant dışı sağlanır, yalnız kimliği doğrulanmış olayla güncellenir.
  - `MONOTONE`: kalıcı `!Sticky(I)`.
  - `PER_ENTITY`: küresel anahtar yerine ihraççı başına beklenti.
  - `SUNSET_CHECK`.
- **Korumalı varyant (M-f):** `PQ_CHAN ∧ (FRESH ∨ PINNED) ∧ MONOTONE ∧ PER_ENTITY ∧ SUNSET_CHECK`. Beklenen: verified.
- **Ablasyon (A3) mutantları ve beklenen izleri** (tahmin):

| Kaldırılan bileşen | Beklenen iz | Mekanizma sınıfı karşılığı |
|---|---|---|
| Kimlik doğrulama | S1 downgrade. R2 `EXPECT_UNAUTH` bunu zaten gösteriyor | M-a (kimliği doğrulanmamış müzakere) |
| PQ kanal | Q-day sonrası beklenti sahteciliği (R3) | M-d (klasik kanaldan kayıt) |
| Tazelik ya da sabitleme | **Geri alma**: PQ imzalı eski v0 `'none'` nesnesinin yeniden oynatılması | M-e ("supported" ile "required" farkı) ve durağan meta veri |
| Tekdüzelik | Bir kez `'pq_required'` görmüş doğrulayıcının sonradan `'none'` kabul etmesi | — |
| Varlık başına kapsam | Küresel "yalnız PQ": eski ihraççı kırılır, `executable_legacy` falsified. Küresel "any-valid": herkes için downgrade | M-b / M-c (biri yeter; saldırgan seçer) |
| Sunset denetimi | Sunset'ten sonra klasik kabul (zamanlı G5 falsified) | — |

- **Lemmalar:**
  - `G5_timed`: `All I c #s #j. Sunset(I)@s & AcceptVia(I,c,'classical')@j & #s < #j ==> F`.
  - `no_rollback`: `All V I c #k #j. SeenPQReq(V,I)@k & AcceptVia(V,I,c,'classical')@j & #k < #j ==> F`.
  - Ayrıca bileşen başına G1 ve `M_*` lemmaları.
- **Datalog karşılığı:** K3'ü genişletir.
  - `expected(X) :- convey(C,X), not forgeable(C), fresh_or_pinned(C,X), monotone(X).`
  - `rollback(X) :- migrated(X), convey(C,X), not fresh_or_pinned(C,X).`
  - G5 ihlali: `coexist(X), not expected(X)`; ayrıca sunset sonrası klasik kabul.
- **Merdiven riski:** Sürüm sayısı sonlu (v0, v1) ve kalıcı durum var; bu yüzden düşük. Çok sürümlü ya da sayaçlı kurgu seçilirse 2. basamak gerekebilir.

### 10.3 Diğer öneriler

1. **ASP sınıf semantiği (§6.5).**
   - `accepted_signer(L,K)` ilişkisi ya da sınıf düzeyinde `pq(L)` tanımı eklenmeli. Ad bağlama yüklemi de eklenmeli.
   - R1b ve R5b çok üyeli sınamalar yapılmalı:
     - TL başına birden çok CA,
     - LOTL'de birden çok TL (LOTL'de 43 işaretçi var; kısmi TL göçü).
   - Karar ASP sonuçları dondurulmadan verilmeli.
2. **Katman 3 örnekleme üreticisi.**
   - ASP'nin asgari kümelerinden bayrak dosyaları üretmeli.
   - Tamarin 1.12'nin önişlemci sınırı nedeniyle yalnız düz Boole `#ifdef` kullanmalı ya da örnek başına ayrı dosya üretmeli.
   - `betik\calistir.sh` ve `betik\degerlendir.py` düzeni doğrudan yeniden kullanılabilir.
3. **KAT-1 (DNSSEC).** `dnssec.yaml` örneğine RFC 6840 §6.2'nin "herhangi bir DNSKEY herhangi bir RRset'i doğrular" kenar semantiği eklenmeli. Bu, `X_alt_ca`'nın aynası.
4. **Sıkılık.** Sonraki adımların koşum betiklerine `--quit-on-warning` eklenebilir. Tamarin 1.12'de böyle bir seçenek var; iyi biçimlilik uyarısında durur.
5. **ProVerif ikinci görüşü (Katman 3.3).** R1–R5'in 11 mutantı ve 5 korumalı varyantı ProVerif'e aktarılabilir. "cannot be proved" sonucu "bilinmiyor" sayılmalı.

## 11. Dosyalar ve yeniden üretim

```
model\tamarin\
  modeller\R1_chain.spthy  R2_downgrade.spthy  R3_channel.spthy  R4_wscd.spthy  R5_anchor.spthy
  modeller\datalog\core.lp  R1_chain.lp … R5_anchor.lp        (Datalog/ASP karşılıkları)
  betik\calistir.sh        toplu koşum (Git Bash); ardından degerlendir.py
  betik\ic_kosum.sh        konteyner içi tek çağrı: süre + cgroup bellek tepesi
  betik\varyantlar.tsv     34 varyant; beklentiler koşumdan önce yazıldı
  betik\degerlendir.py     beklenen/gözlenen, mutasyon skoru, clingo karşılaştırması, iz içerikleri
  sonuc\ozet.csv           kural,varyant,lemma,sonuc,adim,sure_s,bellek_MiB,merdiven_basamagi
  sonuc\degerlendirme.csv  sonuc\datalog_uyum.csv  sonuc\izler.csv  sonuc\varyant_ozeti.csv
  sonuc\metrikler.txt      sonuc\calistir_log.txt  sonuc\uyarilar.txt (boş)  sonuc\sha256.txt
  sonuc\ham\               230 × (.txt tam Tamarin çıktısı, metin izi dahil; .meta rc/süre/bellek)
  sonuc\json\              196 × --output-json (bulunan izler)
```

**Yeniden üretim** (Git Bash, Docker açık):
```
bash model/tamarin/betik/calistir.sh        # bütün varyantlar, ~10 dk (230 konteyner)
bash model/tamarin/betik/calistir.sh R3     # yalnız bir kural
```

**Bütünlük:**
- `sonuc\sha256.txt`, koşumda kullanılan model, Datalog ve betik dosyalarının SHA-256 özetlerini içerir.
- `sha256sum -c` ile yeniden denetlendi: 15/15 OK.

**Docker:**
- Yalnız bu adımın `pq-a04-*` adlı ve `--rm` ile açılan konteynerleri kullanıldı.
- Başka imaja ya da konteynere dokunulmadı. Docker açık bırakıldı.

---

## 12. Adım 5A — R6 zaman penceresi, R7 tekdüze beklenti, M-g/M-h, ProVerif ikinci görüş

- **Tarih:** 24.09.2026.
- **Görev:** Koordinatörün Adım 5A brifi. Dayanaklar:
  - §10'daki R6/R7 önerileri,
  - literatür kararları L-D1 (M-g, M-h, ilk temas) ve L-D3 (anahtarın açıkta kalma penceresi),
  - yeni kural: iyi biçimlilik uyarısı 0 olmalı.
- **Kanıt kuralı:** Bu bölümdeki sayılar şu dosyalardan betikle alındı; elle aktarılmadı:
  - `sonuc\metrikler.txt` (Adım 5A bölümü), `sonuc\ozet.csv`, `sonuc\degerlendirme.csv`, `sonuc\izler.csv`,
  - `sonuc\proverif\metrikler.txt`, `sonuc\proverif\karsilastirma.csv`.

### 12.0 Özet

- **Kapsam:**
  - 4 yeni model: `R6_time`, `R6_h5`, `R7_monotone`, `R7_mh`.
  - 1 keşif modeli: `R7_mh_x`, ön kayıt sonrası.
  - Toplam 41 varyant ve 349 lemma koşumu: R6 105, R6h5 46, R7 130, R7h 33, R7hx 35.
- **Ön kayıt:** Beklentiler koşumdan **önce** `betik\varyantlar.tsv`'ye yazıldı ve özetlendi:
  - ana varyantlar: `sonuc\on_kayit_adim5a_varyantlar.sha256.txt`, 12:45:40,
  - keşif varyantları: `sonuc\on_kayit_adim5a_kesif.sha256.txt`, 19:28:54.
- **Beklenen/gözlenen uyumu: 347/349.**
  - Tek sapma R7h'nin korumalı varyantında (`P_ca_pq_alt_namebind`): G5 ve G1 beklenenin tersine falsified.
  - **Neden:** Ad bağlama yalnız CA **adına** bakıyor. Kök, alternatif klasik CA'yı meşru CA ile **aynı adla** sertifikalayabiliyor.
  - Keşif modeli (R7hx) 35/35 beklendiği gibi çıktı: CA adları tekilse ya da ihraççı CA **anahtarına** bağlanırsa koruma geri geliyor (§12.5).
- **Kabul ölçütü:**
  - R6, R6h5, R7: **GEÇTİ**.
  - R7h: ön kayıttaki biçimiyle **KALDI**. Bu bir model hatası değil, bir bulgu (§12.5).
  - R7hx (keşif): beklendiği gibi.
- **Mutasyon skoru (Adım 5A): 16/16 = %100.**
- **İyi biçimlilik:**
  - Adım 5A'nın 390 ham Tamarin çıktısının 390'ında "All wellformedness checks were successful", uyarı 0.
  - Adım 4 ile birlikte 620/620.
  - `gecersiz_wf` koşumu 0.
- **ProVerif 2.05 ikinci görüşü:**
  - 15 model, 20 güvenlik sorgusu.
  - Kesin sonuç 20/20, Tamarin ile uyum **20/20**, "cannot be proved" 0.
  - Sağlık sorgularında 15/15.
- **Kaynak kullanımı:**
  - En uzun Tamarin koşumu 3,58 s, en yüksek bellek 115,8 MiB.
  - Bütün koşumlar merdivenin 1. basamağında kapandı; kapanmayan yok.
- **Hipotezlere ön sonuçlar** (ayrıntı §12.2–12.6):
  - **H2:** Belirleyici olan belirteç ömrü değil, anahtarın açıkta kalma penceresi. Uzun ömürlü anahtar her rejimde sahtelenebiliyor.
  - **H5:** Klasik cihaz anahtarında tek kullanım, cüzdanda ve doğrulayıcıda birlikte uygulansa bile sahteciliği önlemiyor. Yalnız "geçerlilik penceresi < τ" ve kimlik bilgisi başına anahtar koruyor.
  - **H3:** M-f'nin her bileşeni **her kurguda** gerekli değil.
    - Çevrimiçi (taze) ya da sabitlenmiş kurguda MONOTONE ve SUNSET_CHECK gereksiz.
    - Çevrimdışında ikisi de gerekli.
    - M-g ilk temasta downgrade izi veriyor; M-f vermiyor.
- **M-h:**
  - Taahhüt klasik zincirde Q-day'den sonra sahteleniyor.
  - PQ zincirde ama ad bağlaması yoksa ya da yalnız ada bağlıysa alternatif klasik CA ile atlatılıyor.
  - Ancak anahtar bağlamayla tutuyor.

### 12.1 Ön kayıt, kesinti sonrası denetim ve betik değişiklikleri

**Ön kayıt.**
- `betik\varyantlar.tsv`'ye 36 satır eklendi: R6 12, R6h5 6, R7 13, R7h 5.
- Beklentiler lemma başına, yeni 7. sütunda (`lemma_beklenen`).
- Özet `a88d972e…`, zaman 24.09.2026 12:45:40. Bu zaman, bütün Tamarin koşumlarından önce:
  - duman testi 19:11'den önce,
  - toplu koşum 19:11:34–19:26:39 (R6–R7h),
  - keşif koşumu 19:29:00–19:31:45 (`sonuc\calistir_log.txt`).

**Kesinti sonrası denetim** (kullanım limiti yüzünden oturum kesilmişti):
- Dosyanın özeti ön kayıtla aynı.
- İlk 38 satır (R1–R5) Adım 4 dosyasıyla bayt bayt aynı (`b3165669…`).
- Dosyada CR baytı 0, veri satırlarında `|` 0.
- Biçim düzeltmesi **gerekmedi**; beklentilere dokunulmadı.
- İlk denetimde görülen "CRLF: 81" çıktısı bir sorgu hatasıydı: `$'\r'` çift tırnak içinde yorumlanmıyor. Bayt sayımıyla doğrusu 0.

**Keşif satırları.**
- R7hx için 5 satır, R7h sonucu görüldükten sonra ama R7hx koşumlarından **önce** eklendi.
- Özet `5ebd5b42…`, zaman 19:28:54.
- Ön kayıtlı `R7_mh.spthy` değiştirilmedi (`2077b45a…`). Keşif modeli ayrı dosyada: `R7_mh_x.spthy` (`62ba0c38…`).

**Betik değişiklikleri.**
- `calistir.sh`:
  - 7 sütunlu tabloyu okuyor.
  - Her lemma koşumunda iyi biçimlilik denetimi yapıyor; uyarılı koşum `gecersiz_wf` olarak kaydediliyor ve değerlendirmeye girmiyor.
- `degerlendir.py`:
  - lemma başına beklenti,
  - önek temelli tür sınıflandırması,
  - Datalog karşılaştırması yalnız `.lp` karşılığı olan kurallarda,
  - grup başına metrikler,
  - ham çıktı taraması.
- **Adım 4 çıktıları yeniden üretildi.** Tek fark bir tür etiketi: "bilgi-H3" artık "bilgi". Satır sonu ve etiket normalize edilince `degerlendirme.csv` bayt bayt aynı; Adım 4 metrikleri değişmedi.
- **Duman testi.** Toplu koşumdan önce sonlanmayı denetlemek için 6 temsilî varyant 120 s sınırla koşuldu; her biri 1–3 s sürdü. Resmî kayıt toplu koşumdur.

### 12.2 R6 — zaman penceresi (`modeller\R6_time.spthy`; H2, L-D3)

**EN.** A classical signing key k may stay outside the minimal PQ set iff the CRQC cannot finish extracting k before the verifier stops accepting signatures under k, i.e. iff τ exceeds k's exposure window (public key visible → last acceptance). The window that matters is the key's, not the artefact's. A short-window key is protected only if all three hold:
- τ exceeds its window,
- it is bound to an identity the CRQC cannot break (PQ identity),
- the key itself is not reused beyond the window.

**TR.** Klasik bir imza anahtarı k, asgari PQ kümesinin dışında ancak şu durumda kalabilir: CRQC, doğrulayıcı k altındaki imzaları kabul etmeyi bırakmadan önce k'yi çıkaramıyorsa. Yani τ, k'nin açıkta kalma penceresinden uzun olmalı; bu pencere açık anahtarın görünür olduğu andan son kabule kadar sürer. Belirleyici olan artefaktın değil anahtarın penceresidir. Kısa pencereli bir anahtar ancak üç koşul birlikte sağlanırsa korunur:
- τ penceresinden uzundur,
- CRQC'nin kıramayacağı (PQ) bir kimliğe bağlıdır,
- anahtarın kendisi pencere ötesinde yeniden kullanılmaz.

**Model.**
- **Senaryo:** Token Status List. Durum sağlayıcısının uzun dönemli kimlik anahtarı doğrulayıcıda sabitli.
- **Sertifika ve belirteç:** Durum imza anahtarı `<'stkey', S, pk(k), ep>` sertifikasıyla bağlanır. Belirteç `<'status', S, c, 'valid'>` biçimindedir.
- **Doğrulayıcı:** Sertifikanın `ep` penceresi kapanmadıysa kabul eder. Pencereler kısıtla kodlanıyor; doğrusal durum döngüsü yok.
- **İki evreli CRQC:** `CRQC_Start` Q-day ve gözlenen açık anahtarı ister; `CRQC_Done` özel anahtarı verir. τ bu ikisi arasındaki süredir.
- **Anahtar kipleri:**
  - LONG: tek anahtar,
  - ROTATED: pencere başına taze anahtar,
  - PER_TOKEN: belirteç başına taze anahtar,
  - KEY_REUSE: sertifika döner, anahtar dönmez.
- **Rejimler:**
  - FAST: kısıt yok,
  - MEDIUM: belirteç anahtarı ancak penceresi kapandıktan sonra çıkarılır,
  - SLOW: belirteç ve dönem anahtarları ancak pencereleri kapandıktan sonra çıkarılır.

  Uzun ömürlü ve kimlik anahtarları hiçbir rejimde kısıtlanmaz.
- **Kimlik anahtarı:** `ID_PQ` ile PQ.

**Lemma:**
```
lemma G3_status_unforgeability:
  "All S c st #j. AcceptStatus(S, c, st) @ #j ==> (Ex #i. StatusIssued(S, c, st) @ #i & #i < #j)"
```

**L-D3 ızgarası** (G3; `ID_PQ`, KEY_REUSE yok):

| Anahtar kipi \ rejim | FAST | MEDIUM | SLOW |
|---|---|---|---|
| LONG (uzun ömürlü) | **F** `E_long_fast` | **F** `M_long_medium` | **F** `M_long_slow` |
| ROTATED (rotasyonlu) | **F** `M_rot_fast` | **F** `E_rot_medium` | **V** `P_rot_slow` |
| PER_TOKEN (belirteç başına) | **F** `M_tok_fast` | **V** `P_tok_medium` | **V** `E_tok_slow` |

**Ek ve mutant varyantlar:**

| Varyant | Bayraklar | G3 | İz veren M_ lemması |
|---|---|---|---|
| `M_rot_id` | ROTATED, SLOW (kimlik klasik) | F | `M_identity_key` |
| `M_rot_reuse` | ROTATED, ID_PQ, SLOW, KEY_REUSE | F | `M_long_key` |
| `M_tok_id` | PER_TOKEN, MEDIUM (kimlik klasik) | F | `M_identity_key` |

Kaynak: `sonuc\ozet.csv`, `sonuc\varyant_ozeti.csv`.
- Her varyantta tam olarak bir M_ lemması iz veriyor; o da beklenen saldırı sınıfı. Korumalı varyantlarda hiçbir M_ lemması iz vermiyor.
- Sağlık lemmaları her varyantta verified. `executable_after_window_end` verified olduğundan pencereler gerçekten kapanıyor ve hizmet sürüyor.

**Tamarin'in 12 yapılandırmada doğruladığı koşul:**

G3 verified ⇔ `ID_PQ ∧ ¬KEY_REUSE ∧ ((PER_TOKEN ∧ (MEDIUM ∨ SLOW)) ∨ (ROTATED ∧ SLOW))`

**İzler** (`sonuc\izler.csv`):
- **LONG:** `Provider_Setup, Long_Key, Qday, CRQC_Start, CRQC_Done, Verify_Status`. Çıkarılan uzun ömürlü anahtarla taze belirteç üretiliyor. Belirtecin ömrünün bir önemi yok.
- **ROTATED + FAST:** `Epoch_Start` ile kurulan dönem anahtarı, penceresi açıkken çıkarılıyor.
- **Klasik kimlik:** İzde `Epoch_Start` ya da `Issue_Status_PerToken` yok. Saldırgan kimlik anahtarını çıkarıp kendi durum anahtarını sertifikalıyor; bu, R1'deki zincir kuralı.
- **KEY_REUSE:** `Reused_Key, Epoch_Start_Reuse`. Pencere sertifikada kapansa da anahtarın açıkta kalma penceresi uzun kalıyor.

**H2 ön sonucu.**
- L-D3 sembolik modelde doğrulandı. Belirleyici olan belirtecin ömrü değil, imzalayan anahtarın penceresidir. Uzun ömürlü anahtar her rejimde asgari kümededir.
- Rotasyonlu ve belirteç başına anahtarlar arasındaki fark ancak τ iki pencere sınıfının arasına düştüğünde (MEDIUM) ortaya çıkıyor.
- Sayısal eşleme ASP'nin işi (tahmin). CRQC takvimindeki değerler (hızlı 10 dk, orta 3 gün, yavaş 26 gün) ile pencere uzunlukları karşılaştırılarak hangi hücrenin MEDIUM ya da SLOW olduğuna karar verilecek.

### 12.3 R6h5 — H5'in biçimsel hâli (`modeller\R6_h5.spthy`; R4 × R6)

**EN.** With a classical device (WSCD) key, one-time use enforced both in the wallet and, globally, at verifiers does not prevent CRQC-era presentation forgery. The only remaining protection is time: τ must exceed the credential's validity window, and the device key must not be reused across credentials.

**TR.** Cihaz anahtarı klasikse, tek kullanım hem cüzdanda hem doğrulayıcılarda (küresel olarak) uygulansa bile CRQC dönemindeki sunum sahteciliği önlenmez. Geriye kalan tek koruma zamandır: τ kimlik bilgisinin geçerlilik penceresinden uzun olmalı ve cihaz anahtarı kimlik bilgileri arasında yeniden kullanılmamalı.

| Varyant | Bayraklar | G2 | İz veren M_ lemması | Anlamı |
|---|---|---|---|---|
| `P_single_slow` | SINGLE_USE, SLOW | **V** | — | Pencere < τ: klasik cihaz anahtarı korunuyor |
| `E_nosingle_slow` | SLOW | **V** | — | Tek kullanım olmasa da korunuyor: koruyan pencere |
| `M_single_fast` | SINGLE_USE | **F** | `M_device_key_in_window` | **H5:** tek kullanım sahteciliği önlemiyor |
| `M_single_slow_reuse` | SINGLE_USE, SLOW, KEY_REUSE | **F** | `M_device_key_reused` | Anahtar yeniden kullanılırsa pencere korumaz |
| `E_nosingle_fast` | — | **F** | `M_device_key_in_window` | — |
| `E_devpq_single_fast` | DEV_PQ, SINGLE_USE | **V** | — | PQ cihaz anahtarı |

Kaynak: `sonuc\ozet.csv`.
- `executable_single_use_enforced` 4/4 verified: tek kullanım kısıtları gerçekten işliyor.
- `executable_after_expiry` 6/6 verified: kimlik bilgilerinin süresi doluyor ve hizmet sürüyor.

**İz** (`M_single_fast`): `Issue, Holder_Present, Qday, CRQC_Start_Device, CRQC_Done, Verifier_Challenge, Verifier_Accept`.
- Kimlik bilgisi ve cnf anahtarı bir sunumda görünüyor; bu, toplama anı.
- Cihaz anahtarı pencere içinde çıkarılıyor.
- Taze bir nonce için sahte KB-JWT kabul ediliyor.

**H5 ön sonucu.** Ön kayıttaki H5 öngörüsü sembolik modelde tutuyor: tek kullanımlık toplu ihraç koruma sağlamıyor, yalnız geçerlilik süresi sınırlıyor. Kimlik bilgisi başına cihaz anahtarı ise zorunlu bir koşul. Yanlışlanma koşulu ("doğrulayıcıda tek kullanımla sahteciliğin önlenmesi") gerçekleşmedi: `M_single_fast` = F.

### 12.4 R7 — tekdüze beklenti (`modeller\R7_monotone.spthy`; H3, M-f bileşen ablasyonu A3, M-g, L-D1/L-D2)

**EN.** A PQ-capable verifier resists downgrade and rollback of a migrating issuer's expectation iff the value it relies on at decision time is authentic, current and per entity. That means it comes from an authoritative third party over a PQ-authenticated channel and is either fresh (online) or pinned. Offline, the verifier additionally needs sticky (monotone) state and key expiry at the announced sunset. A self-declared expectation learned on first contact (TOFU, M-g) cannot protect the first contact.

**TR.** PQ yetenekli bir doğrulayıcı, göç eden bir ihraççının beklentisine yönelik downgrade ve geri almaya ancak şu durumda dayanır: karar anında dayandığı değer özgün, güncel ve varlık başınadır. Yani değer yetkili bir üçüncü taraftan, PQ ile doğrulanmış bir kanaldan gelir ve ya taze (çevrimiçi) ya da sabitlenmiştir. Çevrimdışı durumda doğrulayıcı ayrıca yapışkan (tekdüze) duruma ve ilan edilen sunset'te anahtar süresinin dolmasına ihtiyaç duyar. İlk temasta öğrenilen öz-beyanlı beklenti (TOFU, M-g) ilk teması koruyamaz.

**Model.**
- **Yaşam döngüsü:** Göç eden ihraççı için `'none'` → `Migrate` → `'pq_required'` → `Sunset` → `'retired'`. Olay sırası ve kısıtlarla kodlandı.
- **İhraç:** Sunset'e kadar klasik, Migrate'ten sonra PQ; aradaki dönemde ikili ihraç.
- **Eski ihraççı:** Hiç göç etmiyor. Klasik yolu canlı tutuyor ve varlık başına kapsamı anlamlı kılıyor.
- **Doğrulayıcılar (`$V`):** PQ yetenekli. Klasik kanıt yalnız mekanizmanın kapısından geçebiliyor.
- **Mekanizmalar:**
  - M-f: yetkili üçüncü taraf.
  - `MG`: M-g, öz-beyan; PQ kimlik bilgisi beyanı taşır.
- **M-f kipleri:**
  - `PINNED`: senkron sabitleme,
  - `FRESH`: nonce'a bağlı çevrimiçi sorgu; değer kullanım anında güncel (kısıt `Freshness`),
  - ikisi de yoksa çevrimdışı imzalı nesneler: özgün ama yeniden oynatılabilir.
- **Bileşenler:** `PQ_CHAN`, `PER_ENTITY`, `MONOTONE` (yapışkan durum), `SUNSET_CHECK` (klasik anahtarın sertifikalı süresi sunset'te biter).

**Lemmalar:**
- **G5_migrated (Gm):** Göç ettikten sonra yalnız klasik kanıtla kabul yok; ilk teması da kapsar.
- **G5_timed (Gt):** G5'in zamanlı biçimi; sunset'ten sonra klasik kabul yok.
- **no_rollback (NR):** `pq_required` bir kez görüldükten sonra klasik kabul yok.
- **first_contact_downgrade (FCD):** Bilgi amaçlı, exists-trace. Beklentiyi hiç görmemiş bir doğrulayıcı göçten sonra klasik kabul ediyor mu?

| Varyant | Rol | Bayraklar | Gm | Gt | NR | FCD izi | M_ lemmaları | Sağlık |
|---|---|---|---|---|---|---|---|---|
| `P_mf_online` | korumalı | PQ_CHAN, FRESH, MONOTONE, PER_ENTITY, SUNSET_CHECK | V | V | V | yok | - | 5/5 |
| `P_mf_pinned` | korumalı | PINNED, MONOTONE, PER_ENTITY, SUNSET_CHECK | V | V | V | yok | - | 5/5 |
| `M_pq_chan` | mutant: PQ kanal | FRESH, MONOTONE, PER_ENTITY, SUNSET_CHECK | F | V | V | var | M_source_key_broken=V | 5/5 |
| `M_fresh` | mutant: tazelik ya da sabitleme | PQ_CHAN, MONOTONE, PER_ENTITY, SUNSET_CHECK | F | V | V | var | M_stale_object=V | 5/5 |
| `M_per_entity` | mutant: varlık başına kapsam | PQ_CHAN, FRESH, MONOTONE, SUNSET_CHECK | F | V | V | var | M_global_expectation=V | 4/5 |
| `A_online_no_monotone` | ek-ablasyon | PQ_CHAN, FRESH, PER_ENTITY, SUNSET_CHECK | V | V | V | yok | M_rollback=F | 5/5 |
| `A_online_no_sunset` | ek-ablasyon | PQ_CHAN, FRESH, MONOTONE, PER_ENTITY | V | V | V | yok | M_after_sunset=F | 5/5 |
| `A_pinned_min` | ek-ablasyon | PINNED, PER_ENTITY | V | V | V | yok | M_rollback=F, M_after_sunset=F | 5/5 |
| `M_off_monotone` | mutant: tekdüzelik (çevrimdışı) | PQ_CHAN, PER_ENTITY, SUNSET_CHECK | F | V | F | var | M_stale_object=V, M_rollback=V | 5/5 |
| `M_off_sunset` | mutant: sunset denetimi (çevrimdışı) | PQ_CHAN, MONOTONE, PER_ENTITY | F | F | V | var | M_stale_object=V, M_after_sunset=V | 5/5 |
| `G_mg` | ek-mekanizma | MG, MONOTONE, SUNSET_CHECK | F | V | V | var | - | 5/5 |
| `G_mg_no_sunset` | ek-mekanizma | MG, MONOTONE | F | F | V | var | M_after_sunset=V | 5/5 |
| `G_mg_no_cache` | ek-mekanizma | MG, SUNSET_CHECK | F | V | F | var | M_rollback=V | 5/5 |

Kaynak: `sonuc\ozet.csv`, `sonuc\metrikler.txt`.
- 13 varyantın 13'ü, ön kayıttaki bütün beklentilerle aynı.
- `M_per_entity`'deki sağlık 4/5: `executable_learn` = F. Bu önceden yazılmıştı: küresel beklentide öğrenme kuralı yok. Bu yüzden oradaki NR = V boş yere (vacuous) doğrudur.

**Bulgular:**
1. **Çevrimiçi ve sabitlenmiş M-f üç hedefi de ve ilk teması koruyor.** `P_mf_online` ve `P_mf_pinned`: Gm, Gt, NR = V; FCD izi yok.
2. **Çevrimiçi kurguda gerekli bileşenler** (her biri tek başına Gm'yi düşürüyor):
   - **PQ_CHAN** (`M_pq_chan`): Kaynak anahtarı Q-day'den sonra kırılıyor ve taze "none" yanıtı sahteleniyor. İzde `CRQC_Break_Source` var.
   - **FRESH|PINNED** (`M_fresh`): Eski ama özgün "none" nesnesi yeniden oynatılıyor. İzde hiçbir kırılma yok: S1 yeter.
   - **PER_ENTITY** (`M_per_entity`): Küresel "none" değeri, eski ihraççı var olduğu sürece göç etmiş ihraççıyı da açıyor.
3. **Çevrimiçi ve sabitlenmiş kurguda gereksiz bileşenler:**
   - `A_online_no_monotone` ve `A_online_no_sunset` V/V/V; `M_rollback` ve `M_after_sunset` izleri yok.
   - `A_pinned_min` (yalnız PINNED ve PER_ENTITY) V/V/V.
   - Neden: Değer her kararda güncelse kaynağın kendi tekdüze yaşam döngüsü tekdüzeliği ve sunset'i zaten taşıyor.
4. **Çevrimdışı kurguda gerekli bileşenler:**
   - Gm çevrimdışında yapısal olarak düşüyor: bayat nesne, ilk temas.
   - MONOTONE kaldırılınca NR düşüyor (`M_off_monotone`).
   - SUNSET_CHECK kaldırılınca Gt düşüyor (`M_off_sunset`).
5. **M-g (öz-beyan, TOFU) üç varyantta da Gm = F ve FCD izi veriyor.**
   - İz: `Migrating_Issuer_Setup, Migrate, Issue_Classical, Verify_Classical`. Q-day ve kırılma yok: ikili ihracın klasik kopyası ilk temasta kabul ediliyor.
   - Önbellek (MONOTONE) NR'yi, SUNSET_CHECK Gt'yi sağlıyor. İlk teması ise hiçbiri kapatmıyor.

**H3 ön sonucu.**
- "Kimliği doğrulanmamış beklenti G5'i sağlamaz" kısmı Adım 4'te gösterilmişti (R2). "Öz-beyan ilk teması korumaz" kısmı burada Tamarin iziyle gösterildi.
- "M-f yeterli ve **her bileşeni gerekli**" önermesi **bağlama bağlı** çıktı. MONOTONE ve SUNSET_CHECK yalnız çevrimdışı ya da bayat değer kullanan doğrulamada gerekli.
- Bu, ön kayıttaki yanlışlanma koşulunun ikinci kolu ("bir bileşenin gereksiz çıkması → mekanizma sadeleştirilir").
- Sadeleştirilmiş M-f önerisi:
  - **çekirdek:** üçüncü taraf + PQ kimlik doğrulama + varlık başına + güncel (taze ya da sabitlenmiş),
  - **çevrimdışı ek:** tekdüze doğrulayıcı durumu + sunset'te anahtar süresi.
- Bu gereksizlik sonuçları sonradan yorumlanmadı: `A_*` satırlarının V beklentileri ön kayıtta yazılıydı.

### 12.5 R7h — M-h sertifika taahhüdü (`modeller\R7_mh.spthy`) ve keşif R7hx (`modeller\R7_mh_x.spthy`)

**EN.** A PQ commitment carried inside the issuer certificate protects the committed issuer only as far as the certification path does. It also requires the verifier to bind the issuer to its CA's **key**. If the same CA name can also be certified with a classical key, binding to the CA **name** does not exclude that key.

**TR.** İhraççı sertifikasına gömülü PQ taahhüdü, taahhüt eden ihraççıyı ancak sertifika yolu kadar korur. Ayrıca doğrulayıcının ihraççıyı CA'sının **anahtarına** bağlaması gerekir. Aynı CA adı klasik bir anahtarla da sertifikalanabiliyorsa CA **adına** bağlamak o anahtarı dışlamaz.

| Kural | Varyant | Rol | Bayraklar | G5 | G1 | M_/X_ lemmaları |
|---|---|---|---|---|---|---|
| R7h | `P_ca_pq_alt_namebind` | korumalı | CA_PQ, ALT_CA, NAME_BIND | F | F | — |
| R7h | `P_ca_pq_single` | korumalı | CA_PQ | V | V | — |
| R7h | `M_ca_classical` | mutant: taahhüt zinciri PQ | ALT_CA, NAME_BIND | F | F | M_commitment_chain_classical=V |
| R7h | `M_no_namebind` | mutant: ad bağlama | CA_PQ, ALT_CA | F | F | M_alt_ca_bypass=V |
| R7h | `E_ca_classical_single` | ek | — | F | F | M_commitment_chain_classical=V |
| R7hx | `X_repro_prereg` | keşif | CA_PQ, ALT_CA, NAME_BIND | F | F | X_alt_ca_key_used=V |
| R7hx | `X_namebind_unique` | keşif | CA_PQ, ALT_CA, NAME_BIND, UNIQUE_CA_NAMES | V | V | X_alt_ca_key_used=F |
| R7hx | `X_namebind_samename` | keşif | CA_PQ, ALT_CA, NAME_BIND, ALT_SAME_NAME | F | F | X_alt_ca_key_used=V |
| R7hx | `X_keybind_samename` | keşif | CA_PQ, ALT_CA, KEY_BIND, ALT_SAME_NAME | V | V | X_alt_ca_key_used=F |
| R7hx | `X_keybind_distinct` | keşif | CA_PQ, ALT_CA, KEY_BIND | V | V | X_alt_ca_key_used=F |

Kaynak: `sonuc\ozet.csv`, `sonuc\izler.csv`.

**Beklenmeyen sonuç ve nedeni.**
- `P_ca_pq_alt_namebind` (CA_PQ, ALT_CA, NAME_BIND) için V beklenmişti; G5 ve G1 **F** çıktı.
- İz (JSON düğümleri):
  - `AltCA_Setup` kökten `<'ca_cert', $CA, pk(~ka)>` alıyor. Bu, meşru CA ile **aynı ad** (`$CA`).
  - Q-day'den sonra `CRQC_Break_AltCA` çalışıyor.
  - `Verify_Classical`, `!IssuerOfCA($I, $CA)` bağlamasını sağlayıp taahhütsüz bir sertifika kabul ediyor.
- Adım 4'teki R1'de `X_alt_ca_namebind` verified çıkmıştı. Orada `Unique(<'ca', ad>)` kısıtı CA adlarını tekil kılıyordu. R7_mh'de bu varsayım yoktu. Yani R1'in sonucu **CA adı tekilliği** varsayımına bağlıydı.

**Keşif (R7hx, ön kayıt sonrası, 35/35 beklendiği gibi):**
- `X_repro_prereg` sapmayı yeni dosyada yeniden üretiyor.
- `X_namebind_unique`: CA adları tekil kılınınca ad bağlama koruyor (V).
- `X_namebind_samename`: Alternatif CA **aynı adla** geliyorsa ad bağlama atlatılıyor (F). Bu, CA'nın anahtar değişiminde göç öncesi klasik sertifikasının hâlâ geçerli olduğu durumdur.
- `X_keybind_samename` ve `X_keybind_distinct`: İhraççı CA'nın **açık anahtarına** bağlanınca koruma her iki durumda da tutuyor (V).

**Koordinatörün sorusuna cevap** ("taahhüt PQ zincirde ama alternatif klasik CA + ad bağlama yok → taahhütsüz sertifikayla atlatılır mı?"):
- **Evet.** Ayrıntılar:
  - `M_no_namebind`: G5 = F, `M_alt_ca_bypass` = V.
  - Ad bağlama **adla** yapılıyorsa ve alternatif CA aynı adı taşıyabiliyorsa, bağlama olsa da atlatılır (`P_ca_pq_alt_namebind`, `X_namebind_samename`).
  - Taahhüt klasik zincirdeyse Q-day'den sonra sahtelenir: `M_ca_classical` ve `E_ca_classical_single` F; `M_commitment_chain_classical` = V.
  - `M_ca_classical`'da Tamarin'in ilk bulduğu G5 izi de aynı adlı alternatif CA'dan geçiyor. CA kırılması yolu ayrıca M_ lemmasıyla gösterildi.
- **Koruyan kurgular:** anahtar bağlama, tekil CA adları, ya da tek CA (`P_ca_pq_single` V).

### 12.6 M-f / M-g / M-h karşılaştırması (L-D1, L-D2)

| Mekanizma | Beklentinin kaynağı | İlk temas | Koruma koşulu (Tamarin) | Çevrimdışı | Başarısız olduğu durum (iz) |
|---|---|---|---|---|---|
| **M-f** | Yetkili üçüncü taraf (TL/LoTE) | **Korunur** (FCD izi yok; `P_mf_online`, `P_mf_pinned`) | PQ kanal + varlık başına + güncel (taze ya da sabitli) | Tekdüzelik ve sunset'te anahtar süresiyle Gt ve NR korunur; Gm için sabitleme gerekir | Klasik kanal (`M_pq_chan`), bayat nesne (`M_fresh`), küresel beklenti (`M_per_entity`) |
| **M-g** | Öz-beyan: ihraççının kendi PQ kimlik bilgisi (TOFU) | **Korunmaz** (FCD izi; 3/3 varyant) | Önbellek (MONOTONE) yalnız görülmüş varlıklar için; SUNSET_CHECK sunset sonrası için | Önbellek doğrulayıcıda kalır; ilk temas açık | İlk temasta klasik kopyanın kabulü; Q-day gerekmez (`G_mg`) |
| **M-h** | Sertifikaya gömülü taahhüt (CA imzalı) | Korunur, **ancak** yol PQ ve ihraççı **anahtarla** bağlıysa | CA PQ + (anahtar bağlama ya da tekil CA adı ya da tek CA) | Taahhüt her sunumla gelir | Klasik CA (`M_ca_classical`); ad bağlaması yok (`M_no_namebind`); aynı adlı klasik CA (`P_ca_pq_alt_namebind`, `X_namebind_samename`) |

**Yorum** [Y]:
- M-f'nin L-D2'de sayılan ayırt edici özelliği (ilk temasta da korur) Tamarin'de gösterildi.
- M-h, M-g'nin ilk temas açığını kapatıyor, ama yükü sertifika yoluna ve anahtar bağlamaya taşıyor.
- M-h'nin aynı adlı klasik CA ile atlatılması L-D4'te sayılan "M-h'nin alternatif yolla atlatılması" adayına somut bir iz ekliyor. Ancak X_alt_ca'nın kendisi yenilik değil (L-D7).

### 12.7 Mutasyon skoru (Adım 5A)

**Öldürülme ölçütü** (`betik\degerlendir.py`, genelleştirilmiş): Bir mutant şu iki koşul birlikte sağlanırsa öldürülmüş sayılır:
- F beklenen bütün güvenlik lemmaları falsified,
- V beklenen bütün `M_` lemmaları verified.

Böylece izin, kaldırılan korumanın açtığı yoldan geçtiği de doğrulanır.

| Kural | Mutant | Kaldırılan koruma (hangi korumalı varyanttan) | Sonuç |
|---|---|---|---|
| R6 | `M_long_medium` | kısa anahtar penceresi (`P_tok_medium`) | ÖLDÜ |
| R6 | `M_long_slow` | kısa anahtar penceresi (`P_rot_slow`) | ÖLDÜ |
| R6 | `M_rot_fast` | τ pencereden uzun (`P_rot_slow`) | ÖLDÜ |
| R6 | `M_tok_fast` | τ pencereden uzun (`P_tok_medium`) | ÖLDÜ |
| R6 | `M_rot_id` | PQ kimlik bağlama (`P_rot_slow`) | ÖLDÜ |
| R6 | `M_rot_reuse` | anahtarın yeniden kullanılmaması (`P_rot_slow`) | ÖLDÜ |
| R6 | `M_tok_id` | PQ kimlik bağlama (`P_tok_medium`) | ÖLDÜ |
| R6h5 | `M_single_fast` | geçerlilik penceresinin τ'dan kısa olması (`P_single_slow`) | ÖLDÜ |
| R6h5 | `M_single_slow_reuse` | kimlik bilgisi başına cihaz anahtarı (`P_single_slow`) | ÖLDÜ |
| R7 | `M_pq_chan` | PQ kanal (`P_mf_online`) | ÖLDÜ |
| R7 | `M_fresh` | tazelik ya da sabitleme (`P_mf_online`) | ÖLDÜ |
| R7 | `M_per_entity` | varlık başına kapsam (`P_mf_online`) | ÖLDÜ |
| R7 | `M_off_monotone` | tekdüzelik, çevrimdışı (`M_fresh`) | ÖLDÜ |
| R7 | `M_off_sunset` | sunset denetimi, çevrimdışı (`M_fresh`) | ÖLDÜ |
| R7h | `M_ca_classical` | taahhüt zincirinin PQ olması (`P_ca_pq_alt_namebind`) | ÖLDÜ |
| R7h | `M_no_namebind` | ad bağlama (`P_ca_pq_alt_namebind`) | ÖLDÜ |

**Skor: 16/16 = %100** (`sonuc\metrikler.txt`). Adım 4 ile birlikte 27/27.

**Skora girmeyenler:**
- Ablasyon varyantları (`A_*`): kaldırılan bileşenin bu kurguda **gerekmediği** ön kayıtta öngörülmüştü; iz vermemeleri beklenen sonuçtur.
- M-g varyantları (`G_*`) ayrı bir mekanizmadır.
- Keşif varyantları (R7hx).

### 12.8 Sağlık lemmaları ve iyi biçimlilik kanıtı

**Sağlık lemmaları.** Adım 5A'da 178 sağlık lemması koşumunun 178'i beklendiği gibi; 177 verified, 1 F. O F ön kayıtta öngörülmüştü: `M_per_entity`'de `executable_learn` (`sonuc\degerlendirme.csv`).

| Lemma | Verified / koşum | Neyi gösterir |
|---|---|---|
| `executable` | 41/41 | Dürüst akış her varyantta erişilebilir |
| `executable_post_qday` | 28/28 | Q-day'den sonra da dürüst kabul var; korumalı hükümler boş yere çıkmış değil |
| `attack_needs_crqc` | 28/28 | Her ihlal bir CRQC kırılmasından sonra geliyor (R6, R6h5, R7h, R7hx) |
| `executable_after_window_end` | 9/9 | R6'da pencereler gerçekten kapanıyor ve hizmet sürüyor |
| `executable_after_expiry` | 6/6 | R6h5'te kimlik bilgilerinin süresi doluyor ve hizmet sürüyor |
| `executable_single_use_enforced` | 4/4 | Tek kullanım kısıtları gerçekten işliyor |
| `executable_legacy` | 23/23 | Eski ihraççının klasik yolu canlı (R7, R7h, R7hx) |
| `executable_pre_migration` | 13/13 | R7'de beklenti kapısı göçten önce açık |
| `executable_lifecycle` | 13/13 | Migrate ve Sunset erişilebilir; sunset sonrası PQ kabulü var |
| `executable_learn` | 12/13 | Doğrulayıcı `pq_required` öğrenebiliyor. Tek istisna küresel beklentili `M_per_entity`; önceden yazılmıştı |

**İyi biçimlilik** (kural: uyarılı koşum geçersiz):
- Adım 5A'da 390 ham Tamarin çıktısı var: 41 liste koşumu ve 349 lemma koşumu.
- 390'ının hepsinde "All wellformedness checks were successful" satırı bulunuyor; "wellformedness check failed" hiçbirinde yok.
- `calistir.sh` her lemma koşumunda denetledi: `gecersiz_wf` = 0, `uyarilar.txt` boş.
- Adım 4 ile birlikte **620/620**. Kaynak: `sonuc\metrikler.txt`, "İyi biçimlilik taraması" satırları.

### 12.9 ProVerif 2.05 ikinci görüş (R1–R5 alt kümesi)

**Yöntem.**
- R1–R5'in 5 korumalı ve 10 mutant varyantı, `modeller\proverif\*.pvt` şablonlarından `betik\pp.awk` ile üretildi.
- Q-day `phase 1` ile modellendi: klasik anahtarlar 1. evrede saldırgana veriliyor, dürüst süreçler iki evrede de koşuyor.
- **Tamarin modelinden farklar:**
  - Her rolün tek örneği var. R4'te tek bir kimlik bilgisi en üst düzeyde kuruluyor; `phase` talimatı çoğaltılmış süreç içine konmadı.
  - R3 yalnız nesne imzası kanalıyla modellendi.
  - Beklenti kapısı `<>` yerine `= none` eşitlik sınamasıyla yazıldı.
  - Anahtar sızıntısı açık anahtarın gözlenmesini beklemiyor. Bu, daha güçlü bir saldırgan demek.
- Koşum: `betik\proverif_calistir.sh`, 15 model, `--memory=4g`, `timeout 600`.

**Sonuç** (`sonuc\proverif\metrikler.txt`, `karsilastirma.csv`):
- 20 güvenlik sorgusunun **20'si kesin** sonuç verdi; "cannot be proved" 0.
- Tamarin ile uyum **20/20**.
- Sağlık (ulaşılabilirlik) sorgularında 15/15.
- Model başına en uzun süre 0,776 s, bellek tepesi en çok 7,9 MiB.

| Kural | Varyant | Sorgu | ProVerif ham | ProVerif hükmü | Tamarin | Uyum |
|---|---|---|---|---|---|---|
| R1 | `P_all_pq` | executable | false | verified | verified | EVET |
| R1 | `P_all_pq` | G1_claims_unforgeability | true | verified | verified | EVET |
| R1 | `M_root` | executable | false | verified | verified | EVET |
| R1 | `M_root` | G1_claims_unforgeability | false | falsified | falsified | EVET |
| R1 | `M_ca` | executable | false | verified | verified | EVET |
| R1 | `M_ca` | G1_claims_unforgeability | false | falsified | falsified | EVET |
| R1 | `M_iss` | executable | false | verified | verified | EVET |
| R1 | `M_iss` | G1_claims_unforgeability | false | falsified | falsified | EVET |
| R2 | `P_expect_auth` | executable | false | verified | verified | EVET |
| R2 | `P_expect_auth` | G1_claims_unforgeability | true | verified | verified | EVET |
| R2 | `P_expect_auth` | G5_no_classical_acceptance | true | verified | verified | EVET |
| R2 | `M_expect_unauth` | executable | false | verified | verified | EVET |
| R2 | `M_expect_unauth` | G1_claims_unforgeability | false | falsified | falsified | EVET |
| R2 | `M_expect_unauth` | G5_no_classical_acceptance | false | falsified | falsified | EVET |
| R2 | `M_expect_absent` | executable | false | verified | verified | EVET |
| R2 | `M_expect_absent` | G1_claims_unforgeability | false | falsified | falsified | EVET |
| R2 | `M_expect_absent` | G5_no_classical_acceptance | false | falsified | falsified | EVET |
| R3 | `P_obj_pq` | executable | false | verified | verified | EVET |
| R3 | `P_obj_pq` | G1_claims_unforgeability | true | verified | verified | EVET |
| R3 | `P_obj_pq` | G5_no_classical_acceptance | true | verified | verified | EVET |
| R3 | `M_obj_classical` | executable | false | verified | verified | EVET |
| R3 | `M_obj_classical` | G1_claims_unforgeability | false | falsified | falsified | EVET |
| R3 | `M_obj_classical` | G5_no_classical_acceptance | false | falsified | falsified | EVET |
| R4 | `P_dev_iss_pq` | executable | false | verified | verified | EVET |
| R4 | `P_dev_iss_pq` | G2_presentation_unforgeability | true | verified | verified | EVET |
| R4 | `M_dev` | executable | false | verified | verified | EVET |
| R4 | `M_dev` | G2_presentation_unforgeability | false | falsified | falsified | EVET |
| R4 | `M_iss` | executable | false | verified | verified | EVET |
| R4 | `M_iss` | G2_presentation_unforgeability | false | falsified | falsified | EVET |
| R5 | `P_pin_tlpq` | executable | false | verified | verified | EVET |
| R5 | `P_pin_tlpq` | G1_claims_unforgeability | true | verified | verified | EVET |
| R5 | `M_pin` | executable | false | verified | verified | EVET |
| R5 | `M_pin` | G1_claims_unforgeability | false | falsified | falsified | EVET |
| R5 | `M_tl` | executable | false | verified | verified | EVET |
| R5 | `M_tl` | G1_claims_unforgeability | false | falsified | falsified | EVET |

**Pilotla fark** [Y]:
- B'nin pilotunda 4 varyantın 2'si "cannot be proved" vermişti.
- Burada klasik anahtar sızan bütün mutantlarda iz yeniden kuruldu.
- Olası nedenler (doğrulanmadı):
  - kapıda eşitsizlik yerine eşitlik sınaması,
  - dürüst süreçlerin iki evre için ayrı kopyaları.
- Karşılaştırma yalnız kesin sonuçlar üzerinden yapılır; "bilinmiyor" olsaydı uyum oranına girmeyecekti.

### 12.10 Sınırlılıklar (Adım 5A)

1. **Sıra temelli zaman.**
   - τ ve pencereler sayısal değil; rejimler "τ, pencere sınıfından uzun mu" sırasıyla kodlandı (kısıtlar).
   - Hangi gerçek pencerenin hangi sınıfa düştüğü sayısal bir sorudur; ASP'nin işi.
   - CRQC tek anahtar için tek evreli bir çıkarım yapıyor; pencere başına anahtar sınırı k yok.
2. **Tazelik bir kısıt.** R7'de tazelik, "yanıt ile kullanım arasında durum değişmez" kısıtı olarak kodlandı. Bu, "yeterince taze" varsayımının ideal biçimidir. Gerçek yayılma gecikmesi modellenmedi.
3. **Doğrulayıcı davranışı kısıt olarak.** MONOTONE ve SUNSET_CHECK doğrulayıcı davranışı olarak kısıtla modellendi. Bu kurgularda `no_rollback` ve `G5_timed` tanım gereği kolay sonuçlar; bilgi taşıyan sonuçlar, kısıtın **kaldırıldığı** varyantlar.
4. **Yalnız PQ yetenekli doğrulayıcı.**
   - PQ desteği olmayan eski doğrulayıcı ayrı bir rol olarak modellenmedi.
   - G5'in zamanlı biçimi burada PQ yetenekli doğrulayıcının sunset'ten sonraki davranışıdır.
5. **M-h küçük tutuldu.**
   - Eski, taahhütsüz sertifikanın geçerlilik süresi modellenmedi; temiz rotasyon varsayıldı.
   - Taahhüt önbelleği (süreklilik süresi) modellenmedi.
   - M-h'nin TOFU biçimi M-g'ye benzer ve ayrıca sınanmalı.
6. **Keşif ön kayıt sonrası yapıldı.** R7hx, R7h sonucu görüldükten sonra tasarlandı; beklentileri ayrı özetle koşumdan önce sabitlendi. Yine de bir **keşif** olarak raporlanır; ön kayıtlı sonuç 347/349'dur.
7. **ProVerif alt kümesi.**
   - Yalnız R1–R5'in korumalı ve mutant varyantları koşuldu.
   - R6/R7 ProVerif'e aktarılmadı: fazlar τ'yu ve pencereleri ifade etmekte zayıf [Y].
8. **Datalog karşılığı yok.** R6/R7 için Katman 1 ↔ 2 karşılaştırması (clingo) yapılmadı; sayısal pencere ve tazelik ASP modelinin kapsamında (öneri §12.11).
9. **Adım 4 sınırlılıkları geçerli** (§8): sembolik kriptografi, tek örnekli roller, dürüst taraflar.

### 12.11 Teknik kapıya ve sonraki adımlara katkı; öneriler

**Katkı:**
- R6/R7 ve H5'in biçimsel hâli: 41 varyant, 349 lemma, mutasyon skoru 16/16, iyi biçimlilik 0 uyarı.
- ProVerif ikinci görüşü: kesin sonuçlarda 20/20 uyum.
- R7h'deki beklenmeyen sonuç ön kayıtlı sonuç olarak kalıyor; keşif nedenini ayrıştırdı.

**Öneriler:**
1. **ASP (Adım 3) için:**
   - `ad_baglama` parametresi **anahtar bağlama** olarak tanımlanmalı. Ya da CA adlarının tekilliği ayrı bir varsayım olarak yazılmalı.
   - Anahtar değişimi sırasında aynı CA adının klasik ve PQ sertifikaları birlikte geçerli olabilir. "Önce kök" analizinde bu durum ayrı bir hücre olmalı.
   - H2 için `exposure(K)`, `last_accept(K)` ve pencere sınıfları kurulmalı: uzun ömürlü / dönem / belirteç.
   - Durum listesi imza anahtarının 3 değişkesi R6 ızgarasıyla karşılaştırılmalı.
2. **Ön kayıt (yürütücü):**
   - **H3:** "M-f'nin her bileşeni gerekli" yerine bağlama duyarlı bir biçim yazılmalı. Çekirdek bileşenler (üçüncü taraf, PQ, varlık başına, güncel) her kurguda gerekli. Tekdüzelik ve sunset'te anahtar süresi yalnız çevrimdışı ya da bayat değerle doğrulamada gerekli.
   - **G5:** zamansız biçim (R2, R3) ile zamanlı biçim (R7) ayrılmalı.
3. **Soyutlama örneklemesi** (ASP dışa aktarımı hazır olunca): R6/R7 şablonları bayraklarla parametreli olduğundan doğrudan kullanılabilir. Lemma başına süre medyanı 1,03 s.
4. **Adım 7 (M-a…M-h):** M-h için "süreklilik süresi + önbellek" ve "eski sertifikanın geçerliliği" değişkeleri eklenmeli. M-h'nin TOFU açığı M-g ile karşılaştırılmalı.

### 12.12 Adım 5A dosyaları

```
model\tamarin\
  modeller\R6_time.spthy  R6_h5.spthy  R7_monotone.spthy  R7_mh.spthy   (ön kayıtlı)
  modeller\R7_mh_x.spthy                                                (keşif, ön kayıt sonrası)
  modeller\proverif\R1_chain.pvt … R5_anchor.pvt                         (ProVerif şablonları)
  betik\varyantlar.tsv (41 yeni satır), calistir.sh, degerlendir.py (güncellendi)
  betik\pp.awk, ic_kosum_pv.sh, proverif_calistir.sh, proverif_degerlendir.py, proverif_varyantlar.tsv
  sonuc\on_kayit_adim5a_varyantlar.sha256.txt, on_kayit_adim5a_kesif.sha256.txt, sha256_adim5a.txt
  sonuc\ozet.csv, degerlendirme.csv, izler.csv, varyant_ozeti.csv, metrikler.txt (Adım 4 + 5A)
  sonuc\ham\R6__*, R6h5__*, R7__*, R7h__*, R7hx__* (390 dosya) ; sonuc\json\ (izler)
  sonuc\proverif\uretilen\*.pv, ham\*, ozet.csv, karsilastirma.csv, metrikler.txt, log.txt
```

**Yeniden üretim** (Git Bash, Docker açık):
```
for k in R6 R6h5 R7 R7h R7hx; do bash model/tamarin/betik/calistir.sh $k; done   # ≈ 18 dk (bu koşumda 15 + 3 dk)
bash model/tamarin/betik/proverif_calistir.sh                                       # ≈ 30 s
```
