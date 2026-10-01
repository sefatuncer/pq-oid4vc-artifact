# pq-a09-signer — PQ/composite JWS imzalayıcı ve doğrulayıcı (`pqjose`, Adım 9b)

> **Bizim deney aracımızdır.** C3 deneylerinin ve CRQC emülatörünün kullanacağı imzalayıcı/doğrulayıcı. Hedef kütüphanelerin davranışını ölçmez (o iş ön kayıt dondurulduktan sonra).

## Durum (son güncelleme: 24.09.2026)

| Alt görev | Durum |
|---|---|
| 1. Konteyner (`Dockerfile`, `requirements.txt`) | ✅ `pq-a09-signer:1.0` |
| 2. `pqjose` kitaplığı (JWS compact/flattened/general; ES256, ES384, EdDSA/Ed25519/Ed448, ML-DSA-44/65/87, composite -04 ×6; JWK EC/OKP/AKP; x5c) | ✅ |
| 3a. Dış test vektörleri (RFC 9964 Ek A, composite -04 Ek A.1) | ✅ T01 **156/156** |
| 3b. OpenSSL çapraz doğrulama (iki yönlü) + dilithium-py | ✅ T02 **68/68** (OpenSSL 44/44, dilithium-py 18/18) |
| 3c. Negatif testler | ✅ T03 **103/103** (negatif 84/84 reddedildi; pozitif kontrol 19/19) |
| 3d. Boyutlar ve P4 karşılaştırması | ✅ T04 **29/29** (ML-DSA birebir; EC ±2 B) |
| x5c (klasik / ML-DSA / karışık zincir) | ✅ `pki.py`, `x509.py` (T02-O5, T03-N8) |
| Üreteç (`deney/uretec`) | ✅ ayrı README; **v1.1** (A9 yedek kuralı: kontrol kolunun `Ed25519` eşleri, 100 vektör), A6 DPoP boyut tablosu ve **v1.2** (ÖK §6.5 bataryası tamamlandı: MR4, K5/T7, K10, V+/V−; 153 vektör; `BATARYA-ESLEME.md`) orada |
| Ek gereksinim (9a D-E3/D-E5, TK2 "eklenti"): `servis/` — PQ ilkel doğrulama servisi (HTTP yerel + CLI) | ✅ T05 **121/121** (t01 69/69, t02 45/45 aynı sonuç) + T05b entegrasyon; bkz. `servis/README.md` |
| Son imaj inşası + tüm testlerin imaj içinden koşumu (`testler/tumunu_calistir.sh`) | ✅ `pq-a09-signer:1.0` = `beeb05a70a97`, `pq-a09-credgen:1.0` = `55ac321117b7` |
| `KARAR-NOTLARI.md` | ✅ |
| (isteğe bağlı) LAMPS composite X.509 | kapsam dışı (gerekçe §7); yürütücü kararı A1: **şimdilik yapılmayacak**, HAIP §6.1.1 sapması olarak etiketli |

## 1. Kurulum

```bash
docker build -t pq-a09-signer:1.0 deney/imzalayici
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-info pq-a09-signer:1.0          # sürümler
sh deney/imzalayici/testler/tumunu_calistir.sh                                   # tüm testler (imaj içinden)
```

Son inşa (24.09.2026): `pq-a09-signer:1.0` imaj kimliği `beeb05a70a97` (223 MB). Tüm test sonuçları bu imajın içinden, kaynak bağlanmadan üretildi.

| Bileşen | Sürüm / özet | Gerekçe |
|---|---|---|
| Taban imaj | `python:3.11-slim@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534` (Debian 13 "trixie", Python 3.11.16) | Resmî imaj, özetle sabit; OpenSSL 3.5.7 tabanda hazır olduğu için **apt kullanılmaz** → imaj yalnız taban özeti + PyPI özetleriyle yeniden üretilebilir |
| Sistem OpenSSL (CLI) | 3.5.7-1~deb13u2 (9 Jun 2026) | ML-DSA-44/65/87 yerleşik; belirlenimci ML-DSA (`deterministic:1`), bağlam dizesi, tohumdan anahtar, `-not_before/-not_after`, RFC 6979 (`nonce-type:1`) — çapraz doğrulayıcı ve PKI üreticisi |
| cryptography | 50.0.1 (`sha256:51afcfce…497a`), gömülü OpenSSL **4.0.2** | `mldsa` modülü: tohumdan anahtar + bağlam (ctx) destekli imza/doğrulama; ECDSA `deterministic_signing` |
| cffi / pycparser | 2.1.1 / 3.0 (özetler `requirements.txt`'te) | cryptography bağımlılığı |
| dilithium-py | 1.4.0 (yalnız testlerde) | OpenSSL kod tabanından bağımsız saf-Python FIPS 204 — üçüncü uygulama |

Dockerfile'daki sürüm kapısı beklenen sürümler değilse inşayı durdurur. Kitaplık (OpenSSL 4.0.2) ile çapraz doğrulayıcı (OpenSSL 3.5.7) **farklı OpenSSL sürümleridir**; dilithium-py tamamen bağımsızdır.

## 2. Kitaplık (`pqjose/`)

| Modül | İçerik |
|---|---|
| `params.py` | alg tabloları: RFC 7518/9864/9964; composite -04 Tablo 5 (alg, ön-özet), Tablo 7 (Label), §4.2 Prefix |
| `der.py` | -04 §4.5: Ecdsa-Sig-Value (katı DER: asgari kodlama, tek baytlık uzunluk, artık bayt reddi), ECPrivateKey (Tablo 4), X9.62 nokta |
| `mldsa.py` | ML-DSA: tohumdan anahtar, hedged imza (cryptography), belirlenimci imza (OpenSSL CLI), doğrulama |
| `composite.py` | -04 §4.2–4.4: `M' = Prefix ‖ Label ‖ 0x00 ‖ PH(M)`, ML-DSA(ctx=Label) ‖ Trad; bileşen bazında doğrulama (AND) |
| `keys.py` | JWK: EC, OKP, AKP (RFC 9964: `pub`, `priv`=32 B tohum, pub/priv tutarlılık denetimi §7.4), composite AKP (pub = mldsaPK‖tradPK, priv = seed‖tradSK); RFC 7638 parmak izi (AKP: alg,kty,pub); HKDF ile belirlenimci türetme |
| `algs.py` | imzalama/doğrulama ilkelleri; anahtar–alg bağlama (8725bis §3.1) |
| `jws.py` | compact / flattened / general serileştirme; katı ayrıştırma (yinelenen ad, ayrık başlıklar, kanonik base64url); **politika tabanlı doğrulama** |
| `x509.py`, `pki.py` | x5c çözümleme, OpenSSL ile zincir doğrulama, zincir sınıfı (tam-klasik / tam-pq / karışık); belirlenimci test PKI'si |
| `openssl.py` | OpenSSL CLI sarmalayıcısı |
| `cli.py` | `python -m pqjose info|keygen|sign|verify|thumbprint` |
| `../servis/pqdogrula.py` | PQ ilkel doğrulama servisi (HTTP + CLI) — TK2 eklentileri için; bkz. `servis/README.md` |

Desteklenen `alg`'lar: `ES256`, `ES384`, `EdDSA` (RFC 8037, çok biçimli), `Ed25519`, `Ed448` (RFC 9864), `ML-DSA-44/65/87` (RFC 9964), `ML-DSA-44-ES256`, `ML-DSA-65-ES256`, `ML-DSA-87-ES384`, `ML-DSA-44-Ed25519`, `ML-DSA-65-Ed25519`, `ML-DSA-87-Ed448` (-04 Tablo 5).

**Doğrulayıcı politikası (`jws.Policy`)** — bizim doğrulayıcımızın varsayılanı:
- `semantics='all'` (**AND**): mevcut tüm imzalar geçerli olmalı; `'any'` = RFC 7515 §7.2 asgarisi (P0).
- `required_algs` (**L4**): gerekli algoritma kümesi. AND tek başına soymayı yakalamaz; soyma yalnız beklenen kümeyle reddedilir (T03 kontrol bilgisi).
- `allowed_algs` (L1/L2), `keys` + `kid` + anahtar–alg bağlama (L3), `trust_anchors` + `attime` (x5c), `x5c_pq_only` (karışık zinciri reddet), `require_protected` (alg/crit/x5c/jwk/jku/x5u korumalı olmalı), `understood_crit`, `allow_embedded_jwk` (DPoP), `expected_typ`.
- Bilinmeyen alg, `none`, izinsiz alg, anlaşılmayan crit → o imza geçersiz (fail-closed).
- Composite sonuçları bileşen bazında raporlanır: `imza-gecersiz:bilesen(ml=False,trad=True)` ya da `imza-gecersiz:serilestirme: …`.

Örnek:

```python
from pqjose import jws
from pqjose.keys import derive_key
k = derive_key('ML-DSA-65-ES256', 'ornek'); k.kid = k.thumbprint()
tok = jws.sign(b'{"iss":"https://issuer.example"}', jws.Signer(k, {'kid': k.kid}), 'compact', deterministic=True)
r = jws.verify(tok, jws.Policy(keys=[k.public_only()], required_algs=frozenset({'ML-DSA-65-ES256'})))
print(r.valid, r.to_dict())
```

## 3. Doğrulama (kabul) sonuçları — `sonuclar/`

| Test | Sonuç | Ne gösterir |
|---|---|---|
| **T01** dış vektörler (`t01_dis_vektorler.*`) | **156/156** | RFC 9964 Ek A: 3 JOSE + 3 COSE(ham) ML-DSA vektörü; composite -04 Ek A.1: 6 JOSE vektörü (ML-DSA-44/65-ES256, ML-DSA-87-ES384, ML-DSA-44/65-Ed25519, ML-DSA-87-Ed448). Hepsi **bizim doğrulayıcıda KABUL**; tohumdan açık anahtar, JWK/priv serileştirmesi, `kid` (RFC 7638), `M'` bayt-aynı. **RFC 9964 JWS'leri üreticimizce bayt-bayt yeniden üretildi (3/3)**; taslağın ML-DSA bileşeni belirlenimci (6/6 aynı); EdDSA'lı 3 composite imza **tamamen bayt-aynı**; ECDSA bileşeni rastgele k ile (yalnız doğrulanabilir). Bağımsız: OpenSSL CLI ve dilithium-py her vektörü doğruladı |
| **T02** OpenSSL çapraz (`t02_openssl_capraz.*`) | **68/68** — OpenSSL **44/44**, dilithium-py **18/18** | ML-DSA ×3: pqjose→OpenSSL, OpenSSL→pqjose (tam JWS), tohumdan anahtar eşitliği; klasik ×4 iki yön; composite ×6: pqjose bileşenleri OpenSSL'de (ML-DSA ctx=Label, ECDSA DER / EdDSA), OpenSSL bileşenlerinden kurulan composite pqjose'de; X.509: OpenSSL'in ML-DSA/karışık zincirleri cryptography ile de doğrulandı. Belirlenimci ML-DSA: OpenSSL = dilithium-py (bayt-aynı) |
| **T03** negatif (`t03_negatif.*`) | **103/103** — negatif **84/84 reddedildi**, pozitif kontrol **19/19 kabul** | bozuk imza (13 alg), bozuk yük/başlık, yanlış alg etiketi (8), composite bileşen bozulmaları (ML ve klasik bileşen ayrı ayrı, 6 alg), DER/serileştirme bozulmaları, ayrılabilirlik (ECDSA bileşeni ES256 diye; ML bileşeni ML-DSA-65 diye), soyulmuş/karıştırılmış çoklu imza (EdDSA, ML-DSA-65, composite kolları), crit (5), x5c (korumasız, çapa yok, karışık zincir `x5c_pq_only`, yanlış anahtar, EC yaprak + ML-DSA alg, bozuk base64), biçim (4 parça, yinelenen ad, kanonik olmayan base64url, ayrık olmayan başlıklar, özel anahtarlı `jwk`, typ). **Kontrol bilgisi:** P0 (any-valid) ve beklenen kümesiz P1 (AND) soyulmuş nesneleri **kabul ediyor**; karışık zincirler zincir politikası yokken **kabul** ediliyor |
| **T05** PQ ilkel doğrulama servisi (`t05_servis.*`, `t05b_servis_entegrasyon.txt`) | **121/121** | servis (HTTP tek/toplu + CLI) t01 dış vektörlerinde 69/69, t02 senaryolarında 45/45 kitaplıkla aynı sonuç; iç Docker ağı ve 127.0.0.1 entegrasyonu |
| **T04** boyutlar (`t04_boyutlar.*`, `t04_p4_karsilastirma.csv`, `t04_jws_boyutlari.csv`) | **29/29** | P4 profili (adlar, 20 B seri no, 30 gün UTCTime, BC/KU/SKI/AKI) kopyalandı: **ML-DSA-44/65/87 SPKI, imza, CA ve yaprak sertifika, x5c karakter sayısı P4 ile birebir**; EC-P256 ±2 B (DER ECDSA 70–72 B) |

T04 ve P4 (B, OpenSSL 3.5.6) karşılaştırması:

| alg | SPKI | imza | CA sert. | yaprak sert. | x5c (2 sert., b64 kr.) |
|---|---|---|---|---|---|
| ML-DSA-44 | 1334 = 1334 | 2420 = 2420 | 4054 = 4054 | 4073 = 4073 | 10840 = 10840 |
| ML-DSA-65 | 1974 = 1974 | 3309 = 3309 | 5583 = 5583 | 5602 = 5602 | 14916 = 14916 |
| ML-DSA-87 | 2614 = 2614 | 4627 = 4627 | 7541 = 7541 | 7560 = 7560 | 20136 = 20136 |
| EC-P256 | 91 = 91 | 72 / 70 | 454 = 454 | 474 / 476 | 1240 / 1244 |

JWS boyutları (belirlenimci; `t04_jws_boyutlari.csv`): composite imza = ML-DSA + DER ECDSA (ML-DSA-65-ES256: 3309 + 70…72 = **3379–3381 B**, değişken), ML-DSA-65-Ed25519 3373 B, ML-DSA-87-Ed448 4741 B. Açık AKP JWK (JSON): ML-DSA-65 2643 B, ML-DSA-65-ES256 2736 B. DPoP (asgari talepler): ML-DSA-65 8128 B, ML-DSA-65-ES256 **8355 B (> nginx 8182)**, ML-DSA-87 11023 B.

Testleri koşma (imaj içinden, sonuçlar bağlanan dizine):

```bash
MSYS_NO_PATHCONV=1 docker run --rm --name pq-a09-test -v "$(cygpath -m "$PWD/deney/imzalayici/sonuclar"):/out" \
  -v "$(cygpath -m "$PWD/referans/pilot/p4"):/p4:ro" pq-a09-signer:1.0 sh -c \
  'python /opt/pq/testler/t01_dis_vektorler.py /opt/pq/dis-vektorler /out && python /opt/pq/testler/t02_openssl_capraz.py /out \
   && python /opt/pq/testler/t03_negatif.py /out && python /opt/pq/testler/t04_boyutlar.py /p4 /out'
```

Dış vektörler `testler/dis_vektorler.py` ile korpus metninden (`01-korpus/metin/RFC9964.txt`, `JOSECOMP.txt`; SHA-256'ları `dis-vektorler/00-OZET.json`'da) çıkarılır.

## 4. x5c

- `x5c` standart base64 DER (RFC 7515 §4.1.6). Zincir doğrulaması sistem OpenSSL'i ile (`openssl verify -x509_strict -attime`).
- Zincir sınıfı: yaprak anahtarı + x5c'deki her sertifikanın imzası; tamamı PQ → `tam-pq`, tamamı klasik → `tam-klasik`, aksi → `karisik`. `x5c_pq_only` karışık/klasik halkayı reddeder.
- Belirlenimci PKI `pki.py` ile: klasik (P-256) ve ML-DSA-65 zincirleri, karışık zincirler (klasik yaprak + ML-DSA ara CA; ML-DSA yaprak + klasik ara CA; ML-DSA ara CA + klasik kök). Test vektörlerindeki PKI: `deney/uretec/anahtarlar/v1/pki/`.

## 5. Komut satırı

```bash
python -m pqjose keygen --alg ML-DSA-65 --label issuer --private > k.json
python -m pqjose sign --key k.json --payload yuk.json --serialization compact --deterministic > t.jws
python -m pqjose verify --jws t.jws --keys jwks.json --required ML-DSA-65 --semantics all
python -m pqjose verify --jws t.jws --anchors root-ml.pem --attime 1790003700 --pq-only-chain
```

## 6. Belirlenimcilik

Anahtarlar HKDF-SHA256 ile etiketten türetilir (`keys.derive_key`); `deterministic=True` ile ML-DSA (FIPS 204 belirlenimci varyant; OpenSSL CLI), ECDSA (RFC 6979) ve EdDSA imzaları bayt-bayt tekrarlanır. Varsayılan (`deterministic=False`) ML-DSA imzası hedged'dir (cryptography).

## 7. Sınırlılıklar

- **Composite X.509 (draft-ietf-lamps-pq-composite-sigs-19): kapsam dışı.** OpenSSL 3.5.7 ve cryptography 50.0.1 composite sertifika üretemiyor/doğrulayamıyor. LAMPS -19'da `M'` yapısı JOSE -04 ile özdeş (`Prefix‖Label‖len(ctx)‖ctx‖PH(M)`, boş ctx) ve Ek E'de test vektörleri var; yani `pqjose.composite` ile imza düzeyinde üretim mümkün, fakat zincir doğrulaması için kendi yol doğrulayıcımız gerekir. v1'de yapılmadı; composite anahtarlar `kid`/JWKS ile çözülür (HAIP `x5c` zorunluluğundan sapma; notlara yazıldı).
- COSE: `pqjose` COSE katmanı içermez; T01 yalnız RFC 9964 COSE vektörlerinin **ham** alanlarını (imzalama girdisi/imza/açık anahtar) doğrular. COSE_Sign/COSE_Sign1 yapısı (belirlenimci CBOR, Sig_structure, COSE_Key) v1.3'te üreteçte eklendi: `deney/uretec/uretec/cbor.py`, `cose.py`; RFC 9964 Ek A COSE_Sign1 ve -04 Ek A.2 composite COSE örnekleriyle doğrulaması `deney/uretec/testler/t12_cose.py` (138/138; -04 ML-DSA-87-ES384 COSE örneği iç tutarsız, erratum adayı — NOTLAR H).
- Ayrık/kodlanmamış yük (RFC 7797 `b64:false`) desteklenmez.
- x5c doğrulaması yol kurmayı OpenSSL'e bırakır; CRL/OCSP yok.
- dilithium-py yalnız test bağımlılığıdır; kitaplık yolunda kullanılmaz.
