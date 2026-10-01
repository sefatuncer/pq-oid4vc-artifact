# pq-a09-credgen — kimlik bilgisi ve test vektörü üreteci (Adım 9b)

> **Bizim deney aracımızdır.** Vektörlerin **ne olduğunu** tanımlar (inşa gerçekleri, sınanan L basamağı/bayrak, spesifikasyon dayanağı). Beklenen kararı (kabul/red; oracle) **yazmaz** — oracle, ön kayıt gereği N-sürüm olarak ayrı üretilecek. Hedef kütüphane davranışı burada ölçülmez.

## Durum (son güncelleme: 26.09.2026)

| Alt görev | Durum |
|---|---|
| `uretec/sdjwt.py` — RFC 9901: ifşa, özet yerleştirme, compact/General JSON ihraç, KB-JWT, öz-doğrulama | ✅ |
| `uretec/statuslist.py`, `uretec/artefakt.py` — Token Status List, OID4VP istek nesnesi (JAR/DC API), DPoP | ✅ |
| `uretec/anahtar.py` — belirlenimci anahtarlar (39 rol) + test PKI (14 sertifika) → `anahtarlar/v1/` | ✅ |
| `vector-generator/vektorler.py` — test vektörü seti v1 → `vektorler/v1/` (**93 vektör**, 10 aile) | ✅ |
| Öz-doğrulama `testler/t10_oz_dogrulama.py` | ✅ v1 **471/471** (imaj içinden) |
| İmaj `pq-a09-credgen:1.0` | ✅ `55ac321117b7` (FROM `pq-a09-signer:1.0` = `beeb05a70a97`) — v1'i üreten inşa |
| **v1.1** (A9 yedek kuralı: kontrol kolunun `Ed25519` etiketli eşleri) — `uretec/v11.py` → `vektorler/v1.1/` (**100 vektör** = v1'in 93'ü bayt-aynı + 7 eş) | ✅ T10 v1.1 **549/549**; bkz. §5b |
| DPoP boyut tablosu (A6; talep kümesi + composite üst sınır) — `uretec/boyut_dpop.py` → `sonuclar/v1.1_dpop_boyutlari.*` | ✅ bkz. §6 |
| İmaj `pq-a09-credgen:1.1` | ✅ `bd96803a15cd` (FROM `pq-a09-signer:1.0` = `beeb05a70a97`; v1 üretim kodu değişmedi) |
| **v1.2** (ÖK §6.5 eşleme eksikleri: MR4, K5/T7, K10, V+/V−, Ed25519 eşleri) — `uretec/v12.py` → `vektorler/v1.2/` (**153 vektör** = v1.1'in 100'ü bayt-aynı + 53) | ✅ T10 v1.2 **944/944**; imajla bağımsız yeniden üretim `diff -r` farksız (157 dosya); bkz. §5c |
| `BATARYA-ESLEME.md` (ÖK §6.5 K1–K11, V+/V−, MR1–MR4 × 3 kol) — `uretec/esleme.py` | ✅ bağımsız denetim T11 **293/293** |
| İmaj `pq-a09-credgen:1.2` | ✅ `5984112f66f6` (FROM `pq-a09-signer:1.0` = `beeb05a70a97`; v1/v1.1 üretim kodu değişmedi) |
| **v1.3** (Oracle A N-0/N-2: COSE bataryası + L4c "eski ihraççı") — `uretec/cbor.py`, `uretec/cose.py`, `uretec/v13.py` → `vektorler/v1.3/` (**200 vektör** = v1.2'nin 153'ü bayt-aynı + 45 COSE + 2 L4c) ve `anahtarlar/v1.3/` | ✅ T10 v1.3 **1440/1440**; imajla bağımsız yeniden üretim `diff -r` farksız (204 + 6 dosya); bkz. §5d |
| COSE uygulamasının dış vektörlerle doğrulanması — `testler/t12_cose.py` (RFC 9964 Ek A COSE, -04 Ek A.2 COSE, korpus satırları) | ✅ **138/138**; -04 ML-DSA-87-ES384 COSE örneği iç tutarsız (erratum adayı; §5d) |
| `BATARYA-ESLEME.md` v1.3 (+ §3 COSE K1–K11, V±, MR1–MR4 × 3 kol; §4 L4c) | ✅ T11 **592/592** (v1.2 eşlemesi güncel ÖK'ye karşı 293/293; kopyası `sonuclar/BATARYA-ESLEME_v1.2.md`) |
| İmaj `pq-a09-credgen:1.3` | ✅ `492b326d64fc` (FROM `pq-a09-signer:1.0` = `beeb05a70a97`; v1/v1.1/v1.2 üretim kodu değişmedi) |

## 1. Kurulum ve kullanım

Önce imzalayıcı imajı (`experiment/signer`, `pq-a09-signer:1.0`) inşa edilir; üreteç onun üstüne kurulur, ek paket yoktur.

```bash
docker build -t pq-a09-signer:1.0  experiment/signer
docker build -t pq-a09-credgen:1.0 experiment/vector-generator
# üretim (çıktı dizinine: anahtarlar/v1, vektorler/v1, sonuclar/v1_boyutlar.csv)
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-credgen -v "$(cygpath -m "$PWD/experiment/vector-generator"):/work" pq-a09-credgen:1.0
# öz-doğrulama (korpus salt okunur bağlanır)
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-t10 -v "$(cygpath -m "$PWD/experiment/vector-generator"):/work" \
  -v "$(cygpath -m "$PWD/spec-corpus/metin"):/korpus:ro" pq-a09-credgen:1.0 \
  python /opt/vector-generator/testler/t10_oz_dogrulama.py /work /korpus /work/sonuclar
```

İmajlar (son inşa, 24.09.2026): `pq-a09-signer:1.0` = `beeb05a70a97`, `pq-a09-credgen:1.0` = `55ac321117b7`. Vektör seti ve T10 bu imajlardan (kaynak bağlanmadan) üretildi; özetler önceki inşayla aynı.
Ortam: Python 3.11.16, cryptography 50.0.1 (gömülü OpenSSL 4.0.2), sistem OpenSSL 3.5.7 (Debian 13).

## 2. Belirlenimcilik ve sabitleme

- **Anahtarlar:** `pqjose.keys.derive_key(tür, "v1/<rol>")` = HKDF-SHA256 (IKM `"PQ-OID4VC Adim 9b test vektorleri v1"`, salt `"pqjose/derive/v1"`, info = etiket|tür). ML-DSA: 32 B tohum (RFC 9964 §4); EC: FIPS 186-5 benzeri fazla bitli indirgeme; Ed25519/Ed448: ham tohum. Composite anahtarların bileşenleri **ayrı etiketlerle taze** türetilir (-04 §6.2: bileşen anahtarı başka bağlamda kullanılmaz).
- **İmzalar:** ML-DSA belirlenimci varyant (FIPS 204, rnd = 0³², OpenSSL `deterministic:1`); ECDSA RFC 6979; EdDSA doğası gereği. Sertifikalar: sabit seri no ve geçerlilik (2026-01-01 … 2036-12-31), belirlenimci imza.
- **Zaman:** T0 = 1790000000 (2026-09-21T14:13:20Z); tüm vektörler için doğrulama anı `simdi` = T0 + 3700. KB-JWT `iat` = T0 + 3600; DPoP `iat` = simdi − 10.
- **Tuz / jti / sahte özet:** HKDF'den türetilir.
- Sonuç: yeniden üretim **bayt-bayt aynı** (T10-C). Anahtarlar ayrıca dosyada saklanır ve SHA-256 ile sabitlenir:

| Dosya | SHA-256 |
|---|---|
| `anahtarlar/v1/SHA256SUMS` | `c941feb5ee70de6adbd2f3f9468ae8f9a2d265897db232c34d4dfda8f7ccfc1a` |
| `vektorler/v1/SHA256SUMS` | `90b28b2a25e8469776c44b16bcd3c03cc05fa465aaf3dee4bc6dd5aac467e197` |
| `vektorler/v1/MANIFEST.json` | `a4b559eddc082d71c5340e2f5e92d81f13cb7d5e9a5f7ad4089b524df43a8891` |
| `vektorler/v1/b-uyumlu/vectors.json` | `31a875516d7ce5f2a487a5037f8d696f3b9e2e8b49f409b378bbfddbf2d16cde` |

(Test anahtarlarıdır; gerçek kişi/kurum verisi yoktur. Sentetik PID: "Erika Mustermann".)

## 3. Anahtarlar ve test PKI'si (`anahtarlar/v1/`)

- `acik-jwks.json` (CA hariç tüm roller; `kid` = RFC 7638 parmak izi), `ozel/<rol>.json` (özel JWK), `roller.json` (rol → tür, kid, türetme etiketi; sertifika bilgileri), `pki/*.pem|*.der`, `pki/guven-capalari.pem`, `bilesen-yeniden-kullanim-jwks.json` (yalnız CMP12/13), `SHA256SUMS`.
- Roller: `issuer/{ES256, ES384, EdDSA, Ed448, ML-DSA-44/65/87, 6 composite}`, `status/{ES256, ML-DSA-65, ML-DSA-65-ES256}`, `rp/{ES256, ML-DSA-65, ML-DSA-65-ES256, enc}`, `holder/{ES256, ML-DSA-65, ML-DSA-65-ES256}`, `dpop/*`, `ca/*`.
- PKI (HAIP 1.0 §6.1.1: `x5c` = [yaprak, ara CA]; kök `x5c`'ye konmaz):

| Sertifika | Anahtar | İmzalayan | Zincir sınıfı |
|---|---|---|---|
| root-ec / root-ml | P-256 / ML-DSA-65 | kendisi | güven çapası |
| int-ec / int-ml | P-256 / ML-DSA-65 | root-ec / root-ml | — |
| int-ml-rootec | ML-DSA-65 | **root-ec** | PQ ara CA, klasik kök |
| issuer-ec@int-ec, issuer-ml@int-ml | ES256 / ML-DSA-65 | int-ec / int-ml | tam-klasik / tam-PQ |
| issuer-ec@int-ml | ES256 | int-ml | karışık (klasik yaprak + PQ ara) |
| issuer-ml@int-ec | ML-DSA-65 | int-ec | karışık (PQ yaprak + klasik ara) |
| issuer-ml@int-ml-rootec | ML-DSA-65 | int-ml-rootec | karışık (klasik kök halkası) |
| status-ec@int-ec, status-ml@int-ml | ES256 / ML-DSA-65 | — | durum listesi imzacısı |
| rp-ec@int-ec, rp-ml@int-ml | ES256 / ML-DSA-65 | — | RP (SAN: verifier.example) |

- **Composite X.509 yok:** LAMPS composite sertifika OpenSSL 3.5'te desteklenmiyor → composite anahtarlar `kid`/JWKS (JWT VC Issuer Metadata benzeri) ile çözülür. Bu, composite kolunda HAIP'in `x5c` zorunluluğundan **sapma**dır (bkz. `experiment/signer/KARAR-NOTLARI.md`).

## 4. Kimlik bilgisi üreteçleri

| Artefakt | Modül | Biçim ve kurallar |
|---|---|---|
| SD-JWT VC (PID) | `artefakt.issue_vc` | `typ=dc+sd-jwt`; `iss, iat, exp, vct, cnf.jwk, status` açık; 10 ifşa (nesne özelliği, iç içe nesne, dizi öğesi) + 2 sahte özet; `_sd` sıralı; `_sd_alg=sha-256` |
| -13 / -19 kipleri | `sdjwtvc_surum` alanı | İki sürümde veri biçimi aynı (`dc+sd-jwt`). Farklar: JWS JSON serileştirme -13 §3.2'de **isteğe bağlı**, -19 §2.2'de ayrıntıları **kapsam dışı**; `vc+sd-jwt` geçiş kabulü yalnız -13 §3.2.1'de. JSON vektörleri `["-13"]`, compact olanlar `["-13","-19"]` etiketlidir |
| KB-JWT / SD-JWT+KB | `sdjwt.make_kb_jwt`, `artefakt.present` | `typ=kb+jwt`; `iat, aud, nonce, sd_hash`; DC API'de `aud = "origin:https://verifier.example/"` (OID4VP A.4) |
| General JSON SD-JWT | `sdjwt.issue_general` / `present_general` | `disclosures` ve `kb_jwt` yalnız ilk korumasız başlıkta (RFC 9901 §8.3); `sd_hash` geçici compact biçim **ilk imza** ile (belirsizlik; VP07 ikinci imza okumasını içerir) |
| Token Status List | `statuslist.py`, `artefakt.status_token` | `typ=statuslist+jwt`; `sub, iat, exp, ttl, status_list{bits, lst}`; zlib 9; Ek C test vektörleriyle bayt-aynı |
| OID4VP istek nesnesi | `artefakt.request_compact`, `request_multisigned` | `typ=oauth-authz-req+jwt`; `client_id=x509_hash:<b64u(SHA-256(yaprak DER))>` (HAIP §5); DC API `response_mode=dc_api.jwt`, `expected_origins`, DCQL; çoklu imzalıda `client_id` yalnız ilgili imzanın korumalı başlığında (A.3.2.2); imzasız: `openid4vp-v1-unsigned` |
| DPoP kanıtı | `artefakt.dpop` | `typ=dpop+jwt`, `jwk` (açık), `jti, htm, htu, iat` (+ `ath`, `nonce`) |

## 5. Test vektörü seti v1 (`vektorler/v1/`)

Dosyalar: `<aile>/<id>.jws` (compact JWS), `.sdjwt` (SD-JWT compact, `~` ayraçlı), `.json` (JWS JSON / SD-JWT JSON / DC API isteği / toplu yanıt). `MANIFEST.json` ve `MANIFEST.csv` her vektör için:

`id, dosya, sha256, bayt, aile, artefakt, serilestirme, aciklama, kol` (kontrol-EdDSA / tedavi-ML-DSA-65 / tedavi-composite / klasik-taban / ortak), `senaryo` (§7.5 a–d, M-b0), `sdjwtvc_surum`, `sinanan{basamak, plan_bayraklari, ek_etiketler}`, `dayanak` (MANIFEST id + bölüm), `insa` (**üretim gerçekleri**: her imzanın alg'ı, anahtar rolü, nasıl kurulduğu — "gecerli", "bozuk: bayt 5, bit 0", …; x5c zinciri ve sınıfı), `dogrulama_girdileri` (JWKS, kid'ler, güven çapaları, `simdi`, `kb_aud/kb_nonce`), `b_pilot_esi`, `dcapi_protokol`.

> `insa` alanları kabul/red hükmü **değildir**; vektörün nasıl üretildiğini söyler. Oracle bunları ve spesifikasyon maddelerini girdi olarak kullanır.

| Aile | Sayı | İçerik | Başlıca sınanan |
|---|---|---|---|
| **T** | 14 | B'nin P3 T1–T6'sı **gerçek** imzalarla: T1/T2 × {K: ES256+EdDSA, P: ES256+ML-DSA-65, C: ES256+ML-DSA-65-ES256}; T3 (soyulmuş, kollar arası ortak); T4 × 3 kol (+ geçerli ek imza); T5 × 3 (yalnız tek alg); T6 (ES256+EdDSA+composite). Yük ve başlıklar B'ninkiyle aynı (`{"alg":…}`), T2 bozulması B'deki gibi `s[5]^=1` | L1, L2, L4; bilinmeyen-composite-alg |
| **UNK** | 5 | kayıtsız `ML-DSA-66`, kayıtsız composite adı `ML-DSA-65-P256`, küçük harf `ml-dsa-65`, General JSON + kayıtsız composite, General JSON + `alg:none` | L1; bilinmeyen-composite-alg |
| **CMP** | 17 | ML-DSA-65-ES256 referans + bileşen bozulmaları (ML / ECDSA / DER uzunluk / ham r‖s / asgari olmayan DER / artık bayt / kesik / farklı iletiler / sıra ters), uygulayıcı hatası taklitleri (ML bileşeni boş ctx; SHA-256 ön-özet; 0x00'sız M'), ayrılabilirlik (ECDSA bileşeni ES256 diye; ML bileşeni ML-DSA-65 diye), ML-DSA-65-Ed25519 bileşen bozulmaları | L4 (composite içi AND), L3 (anahtar yeniden kullanımı) |
| **X5C** | 10 | tam-klasik, tam-PQ, 3 karışık zincir (klasik yaprak+PQ ara; PQ yaprak+klasik ara; PQ ara+klasik kök), kök x5c içinde, korumasız x5c, korumasız x5c zincir ikamesi (imza aynı), x5c hem korumalı hem korumasız, x5c + başka anahtarı gösteren kid | L3; karışık-x5c, korumasız-x5c |
| **REQ** | 10 | imzalı ES256 / ML-DSA-65 (x509_hash), composite (önkayıtlı istemci), çoklu imzalı (A.3.2.2) + PQ soyulmuş / klasik soyulmuş / PQ bozuk, **M-b0** imzasız (client_id yok / client_id korunmuş), `alg:none` | L1, L3, L4; senaryo c, M-b0 |
| **VC** | 12 | ES256 x5c, ML-DSA-65 x5c, composite kid, ML-DSA-44/87 kid, ML-DSA-65-Ed25519 kid, General JSON ×3 (senaryo d; kontrol EdDSA dahil), ikili ihraç (senaryo b), `typ=vc+sd-jwt`, `alg:none` | L1, L3, L4 |
| **VP** | 7 | SD-JWT+KB: ES256/ES256, ML-DSA-65/ES256 (PQ ihraççı + klasik cihaz anahtarı), ML-DSA-65/ML-DSA-65, composite/composite; General JSON + KB; **PQ imzası soyulmuş ama KB geçerli**; sd_hash ikinci imza okuması | L1, L3, L4; sd_hash belirsizliği |
| **TSL** | 3 | ES256 x5c, ML-DSA-65 x5c, composite kid | L1, L3 |
| **DPOP** | 10 | 7 alg asgari talep + 2 (`ath`+`nonce`) + özel anahtarlı `jwk` | L1; boyut eşiği |
| **CRIT** | 5 | anlaşılmayan `x-pq-beklenti` (M-f taşıyıcı adayı), korumasız crit, crit=["alg"], crit=[], listelenen parametre yok | L1; crit |

Kapsam (vektör sayısı): L1 51, L2 6, L3 32, L4 34. **L0** ayrı vektör gerektirmez (L1 etiketli vektörlerde kısıt yoksa L0); **L5** varsayılan yapılandırmayla L3/L4 vektörlerinin koşulmasıyla ölçülür (vektör özelliği değil). Plan bayrakları (§7.17): bilinmeyen-composite-alg 4, karışık-x5c 4, korumasız-x5c 3; "özel kodla ifade için satır sayısı" vektör değil, ölçüm çıktısıdır.

**B uyumlu dosya:** `vektorler/v1/b-uyumlu/vectors.json` — B'nin `p3_node.mjs`/`p3_py.py` yapısıyla aynı (`pub1`=ES256, `pub2`=EdDSA, `vectors.T1…T6`), ek olarak `pub_mldsa65`, `pub_composite`. T4–T6 artık rastgele bayt değil gerçek PQ/composite imzadır.

## 5b. Test vektörü seti v1.1 (`vektorler/v1.1/`) — C3 bataryası

**Tanım.** v1.1 = v1'in 93 vektörü (dosyalar, `b-uyumlu/vectors.json` ve manifest girdileri **bayt-aynı**) + `kol = kontrol-EdDSA` olan **her** v1 vektörünün `alg = "Ed25519"` etiketli eşi (7 eş). v1 donmuştur: `vektorler/v1/` ve `anahtarlar/v1/` değiştirilmedi (üretim sırasında salt-okunur bağlandı; ağaç özetleri önce/sonra aynı). Yeni anahtar yok; **`anahtarlar/v1` aynen kullanılır**.

| v1 kontrol vektörü | v1.1 eşi | Değişen |
|---|---|---|
| `T1K_both_valid` | `T1K_both_valid-ED25519` | imza #1 başlığı `{"alg":"Ed25519"}` + o imza |
| `T2K_second_tampered` | `T2K_second_tampered-ED25519` | aynı; ardından v1'deki bozulma (`s[5]^=1`) |
| `T4K_plus_ML-DSA-65` | `T4K_plus_ML-DSA-65-ED25519` | imza #1 |
| `T5K_only_EdDSA` | `T5K_only_EdDSA-ED25519` | imza #0 |
| `T6_plus_composite` | `T6_plus_composite-ED25519` | imza #1 |
| `VC09_GJ_ES256_EdDSA` | `VC09_GJ_ES256_EdDSA-ED25519` | imza #1 (aynı tuzlar/ifşalar; ES256 imzası bayt-aynı) |
| `DPOP02_EdDSA` | `DPOP02_EdDSA-ED25519` | tek imza (aynı `jti`, `iat`, `jwk`); 378 → 380 B |

Eşler: aynı anahtar (`issuer/EdDSA`, `dpop/EdDSA` = Ed25519), aynı yük, aynı yapı; **yalnız** `EdDSA` etiketli imzanın korumalı başlığındaki `alg` ve ona bağlı imza farklıdır (Ed25519 belirlenimci). Bunu üretici içindeki koruma denetimi ve T10-E bağımsız olarak doğrular. Manifest: `kol = "kontrol-Ed25519"`, `dayanak` += `RFC9864 §2.2 (Tablo 2: Ed25519)`, `RFC9864 §4.1.1 (JOSE kaydı: Ed25519)`, `RFC9864 §4.1.2 (EdDSA: Deprecated)` (bölümler `spec-corpus/metin/RFC9864.txt`'ten doğrulandı), `insa.v1_esi`, `insa.etiket_degisikligi`.

**Yedek kural (A9).** Kontrol kolunun birincil etiketi `EdDSA`'dır (ön kayıt §3.7/§6.5, B uyumu). Bir hedef `EdDSA`'yı desteklemiyor ama RFC 9864'teki `Ed25519`'u **belgeli olarak** destekliyorsa, o hedefin kontrol kolu `-ED25519` sonekli vektörlerle koşulur ve kullanılan etiket **hedef başına kaydedilir**.

**A1 kararı (anahtar yolu).** C3'te L düzeyi ölçümlerinde doğrulama anahtarı **bütün kollarda** hedefin belgeli API'siyle (JWK/JWKS ya da doğrudan anahtar) verilir; kollar arasında **aynı yol** kullanılır. `x5c`/zincir davranışı **yalnız X5C vektörlerinde**, klasik ve ML-DSA zincirleriyle ölçülür. Composite X.509 v1/v1.1 kapsamı dışındadır; bu, **HAIP §6.1.1'den sapma** olarak etiketlenir. LAMPS composite X.509 şimdilik **yapılmayacak**.

**A6 kararı (boyut raporu).** DPoP boyutları **talep kümesiyle birlikte** (asgari / +ath / +ath+nonce) raporlanır; composite imza boyu için **üst sınır** kullanılır (ML-DSA-65-ES256: 3309 + 72 = **3381 B**; ML-DSA-44-ES256 2492 B; ML-DSA-87-ES384 4731 B). Tablo: §6 ve `sonuclar/v1.1_dpop_boyutlari.{csv,json}`.

**Kimlik (ön kayıtta C3 bataryası olarak çapalanacak):**

| Dosya | SHA-256 |
|---|---|
| `vektorler/v1.1/MANIFEST.json` | `e37ee97e4087829d94ce63109e1466c0cdb8d23c3eab25a84bcf7fee8181e102` |
| `vektorler/v1.1/SHA256SUMS` | `8f4466f2ea13cd84f9a646ca801e89e7ba3a950b4e60d56db215e1962333a40c` |
| `anahtarlar/v1/SHA256SUMS` (kullanılan anahtarlar; v1 ile aynı) | `c941feb5ee70de6adbd2f3f9468ae8f9a2d265897db232c34d4dfda8f7ccfc1a` |

v1.1 manifesti v1 çapalarını da taşır (`v1_capalari`: v1 `MANIFEST.json` `a4b559ed…8891`, v1 `SHA256SUMS` `90b28b2a…e197`) ve `anahtar_sha256sums` alanını içerir.

**Üretim ve doğrulama:**

```bash
docker build -t pq-a09-credgen:1.1 experiment/vector-generator
K="$(cygpath -m "$PWD/experiment/vector-generator")"
RO="-v $K/vektorler/v1:/work/vektorler/v1:ro -v $K/anahtarlar/v1:/work/anahtarlar/v1:ro"   # v1 salt-okunur
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-credgen -v "$K:/work" $RO pq-a09-credgen:1.1          # v1.1
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-t10 -v "$K:/work" $RO -v "$(cygpath -m "$PWD/spec-corpus/metin"):/korpus:ro" \
  pq-a09-credgen:1.1 python /opt/vector-generator/testler/t10_oz_dogrulama.py /work /korpus /work/sonuclar v1.1
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-boyut -v "$K:/work" $RO pq-a09-credgen:1.1 python -m uretec.boyut_dpop /work
```

Üretici önce v1'i geçici dizinde baştan üretir ve donmuş v1 ile (`vektorler/v1` ve `anahtarlar/v1` `SHA256SUMS`) karşılaştırır; fark varsa v1.1 üretilmez.

**T10 v1.1 (`sonuclar/t10_oz_dogrulama_v1.1.*`) — 549/549:** v1'deki A–D denetimleri 100 vektörün tamamında; ek olarak **E**: v1'in 93 vektörü v1.1'de bayt-aynı ve manifest girdileri aynı; `b-uyumlu` aynı; v1 çapaları ve anahtar özeti doğru; her kontrol-EdDSA vektörünün tam bir eşi var; her eş v1'den yalnız EdDSA→Ed25519 başlığı ve o imza bakımından farklı; eşlerdeki Ed25519 imzaları **OpenSSL CLI ile çapraz doğrulandı** (6 geçerli, T2K eşinde 1 bozuk); `pqjose` `Ed25519` etiketini **kabul ediyor** (T eşleri `allowed = required` kümesiyle, VC09 eşi ES256 x5c + Ed25519 kid ile, DPoP eşi gömülü jwk ile); izin listeleri **etikete duyarlı**: listede yalnız `EdDSA` varken `Ed25519` imzası, yalnız `Ed25519` varken v1'deki `EdDSA` imzası `alg-izinli-degil` ile reddediliyor (hedeflerde de etiketin ayrı kaydedilmesi gerekçesi).

## 5c. Test vektörü seti v1.2 (`vektorler/v1.2/`) — ÖK §6.5 bataryasının tamamlanması

**Neden.** Yürütücünün ÖK §6.5 eşleme denetimi (`gozden-gecirme/adim-09b.md` §8) v1.1'de şu eksikleri buldu: K5'in kontrol ve composite kollarında kayıtsız etiketli üçüncü imza, K10, temiz V−, MR4 (imza sırası permütasyonu). Hiçbir hedef ölçülmemişti.

**Tanım.** v1.2 = v1.1'in 100 vektörü (dosyalar, `b-uyumlu/vectors.json`, manifest girdileri **bayt-aynı**) + 53 yeni vektör. `vektorler/v1/`, `vektorler/v1.1/` ve `anahtarlar/v1/` üretim ve testler boyunca **salt-okunur** bağlandı; ağaç özetleri önce ve sonra aynı. Yeni anahtar yok. Üretici önce v1.1'i (ve onun içinde v1'i) geçici dizinde baştan üretip donmuş sürümlerle karşılaştırır; fark varsa durur.

| Grup | Sayı | İçerik |
|---|---|---|
| MR4 (ÖK §2B m.8, §2C m.4) | 24 (+9 Ed25519 eşi) | Kimlik `<id>-SIRA-<kısa-ad>`. İki imzalılar ters: T1K/P/C, T2K/P/C, VC07/08/09, REQ04. Üç imzalılar iki permütasyon: T4K/P/C ve T6 → `ek-once` ([ek, ES256, X]) ve `ters`; T7K/P/C → `kayitsiz-once` ve `ters` (ÖK listesine ek; K5 birincil vektörleri çok imzalı). Her imzanın korumalı başlığı ve imza baytları ile yük **bayt-aynı**; yalnız sıra değişir. SD-JWT VC'de `disclosures` her zaman **yeni** ilk korumasız başlıkta (RFC 9901 §8.3; `insa.mr4.ifsalar_yeni_ilk_basliga_tasindi`) |
| MR4 dışı, tanımlayıcı | 1 | `VP05_GJ_ES256_MLDSA65_kb-SIRA-ters`: KB-JWT değişmez; `sd_hash` artık ilk imzayı değil 2. sıradaki (ES256) imzayı bağlar (RFC 9901 §8.1 belirsizliği; ÖK §2D m.4) |
| K5 (T7) | 3 (+1) | `T7K/T7P/T7C_plus_kayitsiz` = T1* (ilk iki imza bayt-aynı) + `alg: "X-KAYITSIZ-1"` etiketli üçüncü imza; baytlar rastgele ve belirlenimci (HKDF `v1.2/T7<kol>/kayitsiz-imza`, 128 B). K5'in birincil vektörleri; T4*/T6 ikincil |
| K10 | 6 (+1) | Her kolda iki yön: kontrol `alg=EdDSA`+ES256 anahtarı, `alg=ES256`+Ed25519 anahtarı; ML-DSA `alg=ML-DSA-65`+ES256, `alg=ES256`+ML-DSA-65 (AKP); composite `alg=ML-DSA-65-ES256`+saf ML-DSA-65, `alg=ML-DSA-65`+composite. İmza, başlık alg'ıyla değil **gerçek anahtarın kendi algoritmasıyla** üretilmiş geçerli imzadır (`insa.k10`). Anahtar `dogrulama_girdileri.jwk` (JWK) ve `acik-jwks.json`+`kid` ile verilir (ÖK §2D m.1). `alg=ES256`+Ed25519 yönü EdDSA etiketi içermediği için eşi yok (bayt-aynı olurdu) |
| V+ / V− | 6 (+2) | `VPLUS_/VMINUS_{ES256, EdDSA, ML-DSA-65}`: tek imzalı compact JWS (`{"alg","kid","typ":"JWT"}`), V− orta baytta bit çevrili. Composite için `CMP00` (V+) ve `CMP01` (V−) yeniden kullanılır. `VPLUS/VMINUS_ES256` üç kolda ortak (ÖK §4.15: tek geçerli klasik imza) |
| Ed25519 eşleri (ÖK §2D m.2) | 13 | EdDSA etiketi taşıyan her yeni kontrol vektörünün `-ED25519` eşi |

**Eşleme.** `BATARYA-ESLEME.md` (`uretec/esleme.py`): satırlar K1–K11, V+, V−, MR1–MR4; sütunlar kontrol / ML-DSA-65 / composite; her hücrede birincil ve ikincil kimlikler ve ÖK §6.5 oracle kararı **ÖK metninden ayrıştırılarak** alıntılanır (vektörler karar içermez). Uygulanamayan hücreler gerekçeli (K6/K7 yalnız composite; K8/K9 kol-bağımsız bayrak); K8, composite yaprak yerine ML-DSA yaprakla (`X5C04`) uyarlanmıştır (D-S1). 107 kimlik kullanıldı; v1.2'nin eşlemede geçmeyen yeni kimliği yok. Bağımsız denetim `testler/t11_esleme_denetim.py` (ayrı ayrıştırıcı): **293/293**.

**Kimlik (C3 bataryası çapası için):**

| Dosya | SHA-256 |
|---|---|
| `vektorler/v1.2/MANIFEST.json` | `bb17aaa76a3d1859b2dd5df54c62e7039948a715e2c4b4628fed82d184c6e738` |
| `vektorler/v1.2/SHA256SUMS` | `92663b48f477f51e5a4cdd2a6942d97d36b2d9591fa67af451fd33eb14f0b2a3` |
| `anahtarlar/v1/SHA256SUMS` (değişmedi) | `c941feb5ee70de6adbd2f3f9468ae8f9a2d265897db232c34d4dfda8f7ccfc1a` |
| `BATARYA-ESLEME.md` | `d73352179cdf281825d498000b7f9dc6d1df0fe835c8258c6aa2c516e659e3fc` |
| (alıntılanan) `00-on-kayit/ON-KAYIT-TASLAK.md` | `c239d42367d81ddca1c83f35219b578c592e6b7968f689964f591f4d5b698b6e` |

v1.2 manifesti `v1_1_capalari` (v1.1 `MANIFEST.json` `e37ee97e…e102`, `SHA256SUMS` `8f4466f2…a40c`), `v1_capalari` ve `anahtar_sha256sums` alanlarını taşır.

**Üretim ve doğrulama:**

```bash
docker build -t pq-a09-credgen:1.2 experiment/vector-generator
K="$(cygpath -m "$PWD/experiment/vector-generator")"
RO="-v $K/vektorler/v1:/work/vektorler/v1:ro -v $K/vektorler/v1.1:/work/vektorler/v1.1:ro -v $K/anahtarlar/v1:/work/anahtarlar/v1:ro"
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-credgen -v "$K:/work" $RO pq-a09-credgen:1.2                      # v1.2
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-esleme -v "$K:/work" $RO -v "$(cygpath -m "$PWD/00-on-kayit"):/onkayit:ro" \
  pq-a09-credgen:1.2 python -m uretec.esleme /work /onkayit/ON-KAYIT-TASLAK.md                                         # eşleme
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-t10 -v "$K:/work" $RO -v "$(cygpath -m "$PWD/spec-corpus/metin"):/korpus:ro" \
  pq-a09-credgen:1.2 python /opt/vector-generator/testler/t10_oz_dogrulama.py /work /korpus /work/sonuclar v1.2                 # T10
```

**T10 v1.2 (`sonuclar/t10_oz_dogrulama_v1.2.*`) — 944/944** (v1 471/471 ve v1.1 549/549 değişmedi). A–D denetimleri 153 vektörde; ek olarak **F**: v1.1'in 100 vektörü v1.2'de bayt-aynı ve manifest girdileri aynı; çapalar doğru; MR4 eşlerinde yük ve her (korumalı başlık, imza) çifti korunmuş, imza geçerlilikleri permütasyonla birebir taşınmış, SD-JWT VC'lerde ifşalar yeni ilk başlıkta ve `pqjose` sonucu kaynakla aynı; VP05 eşinde `sd_hash` artık 2. sıradaki imzayı bağlıyor; T7'de ilk iki imza T1* ile bayt-aynı, üçüncü imza kayıtsız etiket + HKDF baytları, `pqjose` AND → `alg-bilinmiyor`; K10'da imza gerçek anahtarla geçerli, **OpenSSL CLI ile çapraz doğrulandı**, `pqjose` L3 → RED; V+ / V− `pqjose` ve OpenSSL ile beklendiği gibi; yeni Ed25519 eşlerinde yalnız etiket ve o imza farklı, OpenSSL ile doğrulandı; EdDSA etiketi taşıyan her yeni kontrol vektörünün eşi var.

**Bağımsız yeniden üretim (25.09.2026):** proje dizini tamamen salt-okunurken `pq-a09-credgen:1.2` ile geçici dizine yeniden üretim → `diff -r` **fark yok (157 dosya)**; `BATARYA-ESLEME.md` ve `sonuclar/v1.2_boyutlar.csv` bayt-aynı.

## 5d. Test vektörü seti v1.3 (`vektorler/v1.3/`) — COSE ve L4c "eski ihraççı"

**Neden.** Oracle A iki eksik buldu (N-0, N-2): n = 31'in 5'i COSE hedefi olduğu hâlde v1.2'de COSE vektörü yok; L4c'nin ihraççı başına politikası (ÖK §2B m.6) için ayrı kimlikli "eski ihraççı" yok. Kullanıcı COSE setini onayladı; ÖK §2H m.12. Hiçbir hedef ölçülmedi.

**Tanım.** v1.3 = v1.2'nin 153 vektörü (dosyalar, `b-uyumlu/vectors.json`, manifest girdileri **bayt-aynı**) + 47 yeni vektör. `vektorler/v1/`, `v1.1/`, `v1.2/` ve `anahtarlar/v1/` üretim ve testler boyunca **salt-okunur** bağlandı; ağaç özetleri önce ve sonra aynı. Üretici önce v1.2'yi (ve onun içinde v1.1 ile v1'i) geçici dizinde baştan üretip donmuş sürümle karşılaştırır; fark varsa durur. Ekonomi: brifte olmayan aile eklenmedi.

**COSE (RFC 9052; `uretec/cbor.py` belirlenimci CBOR, `uretec/cose.py`).** COSE_Sign (etiket 98; K1–K5, MR4) ve COSE_Sign1 (etiket 18; K6–K10, V±). Yük: belirlenimci CBOR harita `{"iss","vct","given_name"}`; korumalı başlık `{1: alg}`; `kid` (etiket 4) korumasız başlıkta = JWK `kid`'inin base64url-çözülmüş 32 baytı; `external_aad` boş; ECDSA imzası r‖s (RFC 9053 §2.1); composite imza -04 (M′ = Prefix‖Label‖0x00‖PH(ToBeSigned), ML-DSA ctx = Label, ECDSA bileşeni DER). **Algoritma kimlikleri korpustan birebir** (satır numaraları `uretec/cose.py` `KAYNAK` ve manifest `cose_kimlik_kaynaklari`; T12 ve T10-G korpus satırlarıyla yeniden denetler):

| Etiket | COSE | Kaynak |
|---|---|---|
| ES256 | −7 | RFC9053:248; RFC 9864 §4.2.2 "Deprecated" (RFC9864:467); HAIP §7 "-7 or -9, as applicable" (HAIP:498) |
| EdDSA | −8 | RFC9053:365; RFC 9864 §4.2.2 "Deprecated" (RFC9864:491) |
| Ed25519 | −19 | RFC9864:225, 439 |
| ML-DSA-65 | −49 | RFC9964:367 (AKP kty 7: RFC9964:405; pub −1: 427) |
| ML-DSA-65-ES256 | −55 | JOSECOMP:1268 "TBD (request assignment -55)" → **talep edilen, kayıtlı değil** (manifestte `kayit_durumu`) |

| Grup | Sayı | İçerik |
|---|---|---|
| K1 / K2 / K4 | 3 + 3 + 3 | Her kol (X = EdDSA / ML-DSA-65 / composite): K1 COSE_Sign ES256 + X ikisi geçerli; K2 X imzasının 5. baytında bit çevrili; K4 yalnız X (tek imzacısı K1'in ikinci COSE_Signature'ıyla bayt-aynı) |
| K3 | 1 | `COSE-K3_X_soyuldu`: yalnız ES256 imzacısı; üç kolda ortak dosya (K1K/K1P/K1C'nin ilk imzacısıyla bayt-aynı) |
| K5 | 3 | K1 + üçüncü imzacı: kayıtsız tstr alg `"X-KAYITSIZ-1"`, korumasız başlık boş, 128 B HKDF baytı (`v1.3/COSE-K5<kol>/kayitsiz-imza`) |
| K6 / K7 | 1 + 2 | Composite COSE_Sign1 geçerli; K7 ML-DSA bileşeni (bayt 1654) ve ECDSA bileşeni (r son bayt; DER geçerli) ayrı ayrı bozuk |
| K8 / K9 | 1 + 1 | ML-DSA-65 COSE_Sign1; K8 **korumalı** x5chain (RFC 9360, etiket 33) = [ML-DSA-65 yaprak, klasik ara CA] (karışık; D-S1 uyarlaması), K9 **korumasız** x5chain (tam-PQ). Güven çapası x5chain dışında |
| K10 | 6 | Her kolda iki yön, COSE_Sign1 (JOSE K10 ile aynı çiftler); imza gerçek anahtarın algoritmasıyla geçerli (`insa.k10`) |
| V+ / V− | 6 | `COSE-VPLUS_/VMINUS_{ES256, EdDSA, ML-DSA-65}` COSE_Sign1; V− orta baytta bit çevrili. Composite için K6 (V+) ve K7-ML (V−) yeniden kullanılır |
| MR4 | 6 | K1 ve K2 (üç kol) COSE_Sign imzacı sırası ters (`-SIRA-ters`); her COSE_Signature bayt-aynı taşınır |
| Ed25519 eşleri | 9 | EdDSA (−8) etiketi taşıyan her kontrol vektörünün Ed25519 (−19) eşi (A9 yedek kuralı) |
| **L4c** | 2 | `L4C-JOSE_eski_ES256` (compact, `{"alg","kid","typ":"JWT"}`) ve `L4C-COSE_eski_ES256` (COSE_Sign1): **eski ihraççı** `iss = https://legacy-issuer.example`, anahtar `issuer-eski/ES256` (türetme etiketi `v1.3/issuer-eski/ES256`, kid `GGKBh_lE…MHw`), yalnız ES256. Göç etmiş ihraççının karşılıkları mevcut vektörlerdir: yalnız X → `VPLUS_ML-DSA-65` / `CMP00` / `COSE-VPLUS_ML-DSA-65` / `COSE-K6`; yalnız ES256 → `VPLUS_ES256` / `COSE-VPLUS_ES256` |

K11 COSE'da uygulanamaz (ikili ihraç OID4VCI/SD-JWT VC biçimine bağlı; imza düzeyi karşılığı L4c-2). MR3 COSE'da uygulanamaz (SD-JWT VC -13/-19 boyutu yok). Vektörler kabul/red beklentisi **içermez**; L4c için yalnız `insa.ihracci` gerçekleri (iss, kid, türetme etiketi) vardır.

**Anahtarlar (`anahtarlar/v1.3/`):** `ozel/issuer-eski__ES256.json` (tek yeni anahtar), `acik-jwks.json`, `acik-jwks-l4c.json` (göç etmiş ihraççının 3 anahtarı + eski ihraççı; `ihraccilar`: iss → kid), `cose-anahtarlar.json` (5 rolün açık COSE_Key'i, belirlenimci CBOR hex; EC2 / OKP / AKP), `roller.json`, `SHA256SUMS`. `anahtarlar/v1/` değişmedi.

**Eşleme.** `BATARYA-ESLEME.md` v1.3: §1–§2 JOSE/SD-JWT (v1.2 ile aynı; tek fark K8/K9'un kontrol ve composite hücreleri ÖK §2H m.9'a göre "—": "Composite kolunun sonucu değildir"), §3 COSE (K1–K11, V±, MR1–MR4 × 3 kol; birincil/ikincil ÖK §2G m.4), §4 L4c (iki tedavi kolu × 3 satır; ÖK §2B m.6 ve §6.5 K4 alıntıları), §5 dürüstlük notları. 154 kimlik; v1.3'ün eşlemede geçmeyen yeni kimliği yok. T11: **592/592**. v1.2 eşlemesinin kopyası `sonuclar/BATARYA-ESLEME_v1.2.md` (`d7335217…`).

**Kimlik (C3 bataryası çapası için):**

| Dosya | SHA-256 |
|---|---|
| `vektorler/v1.3/MANIFEST.json` | `a81424470cf2b773c346795aa1b1880aecd841b77254ebb0c077432bc3c5390a` |
| `vektorler/v1.3/SHA256SUMS` | `a5b678d60ff474f1991168a694f52acb6d1c8a42b9648b4e8e63913042768812` |
| `anahtarlar/v1/SHA256SUMS` (değişmedi) | `c941feb5ee70de6adbd2f3f9468ae8f9a2d265897db232c34d4dfda8f7ccfc1a` |
| `anahtarlar/v1.3/SHA256SUMS` | `5d0ccf6bc8cf5de3061ecab1a6c55f8d1165fe10235f366ecd4807b830bb160c` |
| `BATARYA-ESLEME.md` | `6795ee65f5161b4db90942f7058924061273e5d1eb1546dce444cabb2c7cb982` |
| (alıntılanan) `00-on-kayit/ON-KAYIT-TASLAK.md` | `87932cf00b74063066386b1ade066720c4ac645df3f1e75d895ab9bbc43e3f47` |

v1.3 manifesti `v1_2_capalari` (v1.2 `MANIFEST.json` `bb17aaa7…e738`, `SHA256SUMS` `92663b48…b2a3`), `v1_1_capalari`, `v1_capalari` ve iki anahtar dizininin `anahtar_sha256sums` alanlarını taşır.

**Üretim ve doğrulama:**

```bash
docker build -t pq-a09-credgen:1.3 experiment/vector-generator
K="$(cygpath -m "$PWD/experiment/vector-generator")"
RO="-v $K/vektorler/v1:/work/vektorler/v1:ro -v $K/vektorler/v1.1:/work/vektorler/v1.1:ro -v $K/vektorler/v1.2:/work/vektorler/v1.2:ro -v $K/anahtarlar/v1:/work/anahtarlar/v1:ro"
DIS="-v $(cygpath -m "$PWD/spec-corpus/metin"):/korpus:ro -v $(cygpath -m "$PWD/00-on-kayit"):/onkayit:ro"
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-credgen -v "$K:/work" $RO pq-a09-credgen:1.3                        # v1.3
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-esleme -v "$K:/work" $RO $DIS \
  pq-a09-credgen:1.3 python -m uretec.esleme /work /onkayit/ON-KAYIT-TASLAK.md                                         # eşleme
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-t10 -v "$K:/work" $RO $DIS pq-a09-credgen:1.3 sh -c 'cd /opt/vector-generator/testler &&
  python t10_oz_dogrulama.py /work /korpus /work/sonuclar v1.3 &&
  python t11_esleme_denetim.py /onkayit/ON-KAYIT-TASLAK.md /work/BATARYA-ESLEME.md /work/vektorler/v1.3/MANIFEST.json &&
  python t12_cose.py /korpus /opt/pq/dis-vektorler /work/sonuclar'                                                     # T10, T11, T12
```

**T12 (`sonuclar/t12_cose.*`) — 138/138:** (A) `KAYNAK`'taki 40 kimlik (algoritma, başlık, etiket, anahtar parametreleri) korpus satırında birebir; (B) RFC 9964 Ek A.2 COSE (ML-DSA-44/65/87): COSE_Key çözülüp ekleme sırasıyla bayt-aynı yeniden kodlanır, AKP COSE parmak izi = kid, Sig_structure = `raw_to_be_signed`, imza `pqjose` ve dilithium-py ile doğrulanır, **belirlenimci yeniden imzalama COSE_Sign1'i bayt-aynı üretir**; (C) -04 Ek A.2 COSE (6 composite): tohumdan anahtar, bizim korumalı başlık + Sig_structure kodlamamızla **M′ birebir**, composite imza ve bileşenler (OpenSSL CLI, dilithium-py) doğrulanır; EdDSA'lı örneklerde imzamız bayt-aynı. **İstisna:** ML-DSA-87-ES384 örneğinde gösterilen Sig_structure'ın SHA-512'si gösterilen M′ içindeki PH ile eşleşmiyor (bileşenler gösterilen M′ üzerinde geçerli; alg/kid/sıra/özet varyantları denendi) → örnek COSE_Sign1 olarak doğrulanamaz, **erratum adayı**; aynı anahtar ve başlıkla bizim imzamız iç tutarlı.

**T10 v1.3 (`sonuclar/t10_oz_dogrulama_v1.3.*`) — 1440/1440** (v1 471/471, v1.1 549/549, v1.2 944/944 değişmedi). A–D 153 JOSE vektöründe ve L4C-JOSE'de; C'de v1.3 `MANIFEST.json/.csv`, `SHA256SUMS` ve `anahtarlar/v1.3/SHA256SUMS` yeniden üretimde bayt-aynı; ek olarak **G** (`testler/t10_cose.py`): v1.2'nin 153 vektörü bayt-aynı ve manifest girdileri aynı; çapalar doğru; kimlik kaynakları korpus satırlarında; eski ihraççı anahtarı etiketinden yeniden türetiliyor ve v1 anahtarlarından farklı; COSE_Key = JWK; her COSE vektöründe etiket/yapı, dış ve iç CBOR belirlenimci, yük, alg etiketi korumalı başlıkta, kid; **her imza üç yolla** (`pqjose`, OpenSSL CLI, ML-DSA için dilithium-py) insa iddiasıyla tutarlı; composite bileşen durumları; K2/K3/K4/K5/V−/K7 arasındaki bayt ilişkileri; x5chain konumu, OpenSSL zincir geçerliliği, sınıfı ve yaprak anahtarı; K10 başlık/anahtar uyuşmazlığı; MR4'te her COSE_Signature bayt-aynı taşınmış; Ed25519 eşlerinde yalnız −8→−19 ve o imza farklı; L4c'de eski ihraççı vektörleri eski anahtarla geçerli, göç etmiş ihraççının ES256 anahtarıyla geçersiz.

**Bağımsız yeniden üretim (26.09.2026):** `experiment/vector-generator` tamamen salt-okunurken `pq-a09-credgen:1.3` ile geçici dizine üretim → `diff -r` **fark yok** (`vektorler/v1.3` 204 dosya, `anahtarlar/v1.3` 6 dosya); `BATARYA-ESLEME.md` ve `sonuclar/v1.3_boyutlar.csv` bayt-aynı.

**Boyutlar (COSE / JOSE):** COSE vektörleri base64url yükü olmadığı için JOSE karşılıklarının %51–74'ü: `COSE-VPLUS_ES256` 174 B (JOSE 341), `COSE-VPLUS_ML-DSA-65` 3.421 B (4.672), `COSE-K6` composite 3.491 B (`CMP00` 4.775), `COSE-K1P` 3.533 B (`T1P` 4.781), `COSE-K8` 6.295 B (`X5C04` 11.540), `COSE-K9` 14.659 B (`X5C07` 21.564). Tamamı `sonuclar/v1.3_boyutlar.csv`.

## 6. Boyutlar (`sonuclar/v1_boyutlar.csv`, `sonuclar/v1.1_boyutlar.csv`, `sonuclar/v1.1_dpop_boyutlari.*`)

DPoP, talep kümesine göre (A6; `bayt / üst sınır`; nginx 1.31.6 varsayılan başlık değeri eşiği 8.182 B, Node 24.15 16.348 B — P4):

| alg | asgari | +ath | +ath+nonce |
|---|---|---|---|
| ES256 / EdDSA / Ed25519 | 440 / 378 / 380 | 510 / 448 / 450 | 556 / 494 / 496 |
| ML-DSA-44 | 5.805 | 5.875 | 5.921 |
| ML-DSA-65 | 8.128 | **8.198** (> nginx, +16 B) | **8.244** |
| ML-DSA-87 | **11.023** | **11.093** | **11.139** |
| ML-DSA-44-ES256 (üst sınır) | 6.032 | 6.102 | 6.148 |
| ML-DSA-65-ES256 (üst sınır) | **8.356** | **8.426** | **8.472** |
| ML-DSA-87-ES384 (üst sınır) | **11.350** | **11.420** | **11.466** |
| ML-DSA-65-Ed25519 | **8.292** | **8.362** | **8.408** |

Kalın: nginx eşiğini aşıyor. ML-DSA-65 asgari kümede 54 B altında, `ath` eklenince 16 B üstünde (P4'teki "≈8.192 B, 10 B üstünde" değeri bu kümeye karşılık gelir). Composite ve ML-DSA-87 her kümede üstünde; hiçbiri Node eşiğini aşmıyor.

Diğer artefaktlar:

| Artefakt | Bayt |
|---|---|
| SD-JWT VC ES256 + x5c (klasik) | 3.838 |
| SD-JWT VC ML-DSA-65 + x5c (tam-PQ) | 26.409 |
| SD-JWT VC ML-DSA-65-ES256 (kid) | 6.537 |
| SD-JWT+KB: ML-DSA-65 ihraççı + ML-DSA-65 KB | 33.983 |
| Status List Token ML-DSA-65 + x5c | 24.719 |
| OID4VP istek ML-DSA-65 + x5c / çoklu imzalı ES256+ML-DSA-65 | 25.619 / 27.797 |

(Vektör dosyalarındaki DPoP boyutları gerçek imza boyuyla ölçülmüştür, ör. DPOP06 ML-DSA-65-ES256 8.355 B; raporlamada yukarıdaki üst sınır tablosu kullanılır — A6.)

## 7. Öz-doğrulama (T10; `sonuclar/t10_oz_dogrulama.*`) — 471/471

- **A.** TSL Ek C (1/2/4/8 bit): çözme eşit ve **kodlama bayt-aynı** (zlib 9); RFC 9901 §4.2.3 özet örneği.
- **B.** 93 vektör dosyasının SHA-256'sı manifestle; `SHA256SUMS` (96 + 71 dosya).
- **C.** Geçici dizine yeniden üretim → `vektorler/v1` ve `anahtarlar/v1` bayt-bayt aynı.
- **D.** Her vektörün `insa` iddiaları: imza sayısı ve alg etiketleri; "geçerli/bozuk" imzaların kriptografik durumu; CMP bileşen durumları (ml/trad/serileştirme) ve uygulayıcı hatası taklitlerinin kendi sapmalı M'/ctx'leriyle tutarlılığı; ayrılabilirlik vektörlerinde bileşenin M' üzerinde gerçek olduğu; x5c zincirlerinin OpenSSL ile geçerliliği ve sınıfı (tam-klasik/tam-PQ/karışık); `client_id` = x509_hash(yaprak); TSL durum değerleri; DPoP `jwk`; KB-JWT'nin cnf anahtarıyla geçerliliği ve `sd_hash`'in iddia edilen imzayı kapsaması.

## 8. Sınırlılıklar

- Composite X.509 (LAMPS -19) üretilmedi → composite kolunda `x5c` yok; **HAIP §6.1.1'den sapma** olarak etiketli. Yürütücü kararı A1: L düzeyi ölçümlerinde anahtar bütün kollarda hedefin belgeli API'siyle (JWK/JWKS ya da doğrudan anahtar) verilir; zincir davranışı yalnız X5C vektörlerinde (klasik ve ML-DSA zincirleri) ölçülür; LAMPS composite X.509 şimdilik yapılmayacak.
- v1.1'deki `-ED25519` eşleri yalnız kontrol kolunu kapsar (A9 yedek kuralı); diğer kolların etiketleri değişmez.
- ML-DSA imzaları **belirlenimci** varyantla üretildi (tekrarlanabilirlik için); gerçek dağıtım hedged kullanır. Doğrulama açısından fark yok.
- v1–v1.2 vektörleri JOSE/SD-JWT düzeyindedir; v1.3 COSE_Sign/COSE_Sign1 ekler (§5d). mdoc (ISO/IEC 18013-5 MSO/DeviceResponse), JWE (yanıt şifreleme), wallet attestation ve key attestation vektörleri yok. COSE'da ES256 yalnız −7 ile üretildi (ESP256 −9 yok; §5d).
- OID4VP isteklerinde DCQL ve `client_metadata` asgari tutuldu; tam OID4VP akışı (yanıt, `request_uri` alımı, `wallet_nonce`) üretilmez.
- `vc+sd-jwt` dışında -13/-19 veri biçimi aynı olduğundan iki kip aynı dosyayı paylaşır; ayrım manifestteki `sdjwtvc_surum` etiketindedir.
