# pqdogrula — PQ ilkel doğrulama servisi (C3 tedavi kolu TK2 "eklenti")

**Gerekçe:** Adım 9a kararı D-E3/D-E5 (`gozden-gecirme\adim-09a.md`; ön kayıt §2B). C3'te TK2 kolunda hedef kütüphanenin **kamuya açık genişletme noktasına** (ör. Java Nimbus `JWSVerifier`, Go crypto arayüzü, .NET `SecurityKey`/`SignatureProvider`, PHP jwt-framework algoritma kaydı, JS `jose` özel doğrulayıcı) ince bir eklenti takılır; eklenti yalnız **kriptografik ilkeli** bu servise sordurur. **Politika kararı kütüphanede kalır** (hangi alg kabul edilir, kaç imza gerekir, anahtar nasıl seçilir, x5c/crit/typ). Hedefler 9 dil grubunda, bizim kitaplık Python olduğu için dil bağımsız bir HTTP arayüzü ve bir CLI sağlanır.

## 1. Ne yapar / ne yapmaz

| Yapar | Yapmaz |
|---|---|
| `alg` + açık anahtar + imzalanan baytlar + imza → `{gecerli, bilesenler, hata}` | JWS/JWT/SD-JWT ayrıştırma, başlık işleme, `kid`/`x5c` çözümleme, zincir doğrulama |
| ML-DSA-44/65/87 (RFC 9964; ctx boş) | alg izin listesi, gerekli küme, çoklu imza semantiği (hepsi kütüphanede) |
| composite -04: ML-DSA-44-ES256, ML-DSA-65-ES256, ML-DSA-87-ES384, ML-DSA-44-Ed25519, ML-DSA-65-Ed25519, ML-DSA-87-Ed448 — bileşen bazında sonuç | klasik alg (ES256, EdDSA…): kütüphanenin kendi desteği kullanılır; servis `hata` döner |
| AKP JWK'de `jwk.alg == istek alg` denetimi (RFC 9964 §3: AKP'de `alg` ZORUNLU), uzunluk/kodlama denetimi | anahtar saklama, imzalama, günlük tutma |

Kriptografi `pqjose` ile aynı yoldan gider (cryptography 50.0.1 / gömülü OpenSSL 4.0.2; composite: -04 §4.3, bileşen AND).

## 2. Arayüz

**İstek (JSON):**

| Alan | Zorunlu | Açıklama |
|---|---|---|
| `alg` | ✔ | yukarıdaki 9 değerden biri |
| `jwk` **ya da** `acik_anahtar` / `acik_anahtar_hex` | ✔ (biri) | `jwk`: AKP (`kty=AKP`, `alg`, `pub`); `priv` varsa **yok sayılır**. `acik_anahtar`: base64url ham açık anahtar (ML-DSA: FIPS 204 pk; composite: `mldsaPK ‖ tradPK`, -04 §4.1) |
| `imzalama_girdisi` / `_hex` | ✔ | imzalanan baytlar. JWS: `ASCII(BASE64URL(protected) '.' BASE64URL(payload))`; COSE: `Sig_structure` baytları |
| `imza` / `_hex` | ✔ | ham imza baytları (JWS'te base64url çözülmüş) |

**Yanıt:** `{"gecerli": bool, "alg": str, "bilesenler": {"ml": bool} | {"ml": bool, "trad": bool} | null, "hata": null | str, "servis": "pqdogrula/1"}`. `hata` doluysa istek ya da serileştirme sorunu vardır ve `gecerli=false`'tur (ör. composite'te DER bozukluğu: `"serilestirme: DER: …"`).

**HTTP uçları:** `GET /v1/saglik` (sürümler, desteklenen alg'ler) · `POST /v1/dogrula` (tek istek) · `POST /v1/dogrula/toplu` (`{"istekler": [...]}` → `{"yanitlar": [...]}`, en fazla 256). Gövde sınırı 4 MiB. Kimlik doğrulama **yok**; istek günlüğü tutulmaz.

**CLI:** `python -m servis.pqdogrula dogrula [--istek DOSYA]` (DOSYA yoksa stdin); çıkış kodu `0`=geçerli, `1`=geçersiz, `2`=istek hatası. `python -m servis.pqdogrula saglik`. `python -m servis.pqdogrula sunucu --host H --port P`.

## 3. Çalıştırma (yalnız yerel)

> Kimlik doğrulama olmadığı için servis **dış ağa açılmaz**: ya iç Docker ağında (önerilen) ya da yalnız `127.0.0.1`'e yayınlanır. `-p 8765:8765` (tüm arayüzler) KULLANMAYIN.

```bash
# (a) C3 için önerilen: dış bağlantısı olmayan iç ağ; hedef kütüphane konteynerleri aynı ağa katılır
docker network create --internal pq-a09-net
docker run -d --name pq-a09-pqdogrula --network pq-a09-net pq-a09-signer:1.0 \
  python -m servis.pqdogrula sunucu --host 0.0.0.0 --port 8765
#   hedefler: http://pq-a09-pqdogrula:8765/v1/dogrula
# (b) elle deneme: yalnız ana makinenin 127.0.0.1'ine yayın
docker run -d --name pq-a09-pqdogrula-yerel -p 127.0.0.1:18765:8765 pq-a09-signer:1.0 \
  python -m servis.pqdogrula sunucu --host 0.0.0.0 --port 8765
# kaldırma
docker rm -f pq-a09-pqdogrula pq-a09-pqdogrula-yerel; docker network rm pq-a09-net
```

## 4. Çağrı örnekleri

- **curl:** `servis/ornekler/curl.sh` (sağlık, tek istek ×2, toplu). İstek dosyaları dış test vektörlerinden üretildi: `istek_ML-DSA-65.json` (RFC 9964 Ek A), `istek_ML-DSA-65-ES256.json` (composite -04 Ek A.1).

```bash
curl -s -X POST -H 'Content-Type: application/json' \
  --data-binary @deney/imzalayici/servis/ornekler/istek_ML-DSA-65-ES256.json http://127.0.0.1:18765/v1/dogrula
# {"gecerli": true, "alg": "ML-DSA-65-ES256", "bilesenler": {"ml": true, "trad": true}, "hata": null, ...}
```

- **Python (yalnız standart kitaplık):** `servis/ornekler/istemci.py` — `compact_jws_dogrula(url, jws, jwk)`: JWS'ten imzalama girdisini ve imzayı çıkarıp servise yollar.
- **Diğer diller (C3'te yazılacak eklentiler için kalıp):** genişletme noktasında `verify(alg, key, signingInput, signature)` çağrısı gelince → `POST /v1/dogrula` gövdesi `{"alg": alg, "jwk": <AKP açık JWK>, "imzalama_girdisi": b64url(signingInput), "imza": b64url(signature)}` → yalnız `gecerli` alanı kütüphaneye döndürülür; `bilesenler` ve `hata` ölçüm günlüğüne yazılır.

## 5. Kabul sonuçları

| Test | Sonuç |
|---|---|
| **T05** (`../testler/t05_servis.py`, `../sonuclar/t05_servis.*`) | **121/121**. t01 dış vektörleri (RFC 9964 JOSE + COSE-ham, composite -04 JOSE; jwk/hex/b64u anahtar biçimleri; imza/ileti/bileşen bozulmaları, artık bayt): **69/69 aynı sonuç**; t02 senaryoları (aynı belirlenimci anahtarlar; pqjose-hedged, OpenSSL, dilithium-py, belirlenimci imzalar; composite: pqjose ve OpenSSL bileşenli; bozuk/kesik): **45/45 aynı sonuç**. Her vaka üç yoldan (HTTP tek, HTTP toplu, CLI) ve `{gecerli, bilesenler}` kitaplıkla birebir; hata yolları (desteklenmeyen alg, jwk.alg uyuşmazlığı, bozuk hex, yanlış pub uzunluğu) ve sağlık ucu |
| **T05b** entegrasyon (`../sonuclar/t05b_servis_entegrasyon.txt`) | iç ağ `pq-a09-net` (`Internal=true`, yayınlanan port 0) üzerinden başka konteynerden çağrı ✔; `127.0.0.1:18765` üzerinden ana makine `curl` ✔ |

## 6. Sınırlılıklar

- HTTP gidiş-dönüşü ek gecikme getirir; C3'te **zamanlama** ölçümleri bu servisle yapılmamalı (yalnız karar/yetenek ölçümü için).
- Servis yalnız PQ/composite ilkelini doğrular; composite X.509 zincirleri yoktur (bkz. imzalayıcı README §7).
- Tek süreçli, iş parçacıklı `http.server`; yük testi amaçlı değildir.
