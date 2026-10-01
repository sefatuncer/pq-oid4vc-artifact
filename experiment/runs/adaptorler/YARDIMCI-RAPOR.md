# C3 adaptör yardımcısı — rapor (01.10.2026)

> **Kapsam:** 12 hedef (yürütücü düzeltmesiyle: JOSE-026 ve JOSE-017 çıkarıldı, SDJWT-002 ve JOSE-102 eklendi; JOSE-026/JOSE-017 için adaptör yazılmamıştı).
> **Koşulan tek batarya dosyası:** `experiment/runs/isler_dondurma_oncesi_V.jsonl` (önce 16, yürütücü güncellemesinden sonra 32 satır: JOSE V± + CMP00/01 + COSE V± + COSE-K6/K7). `isler.jsonl`'nin başka satırı koşulmadı; `karar.tsv`/oracle dosyaları açılmadı; manifestten yalnız `dogrulama_girdileri` okundu (`insa` okunmaz, yapısal olarak).
> **Çıktılar:** `experiment/runs/kosu/oncesi/<hedef>.jsonl` (32 satır, `kosu = "oncesi"`), hedef başına `kanit/vpm-kosu.txt` (komut, imaj özeti, çıktı SHA-256, özet).
> **Sentetik duman testleri** (batarya değil; geçici anahtar ve belirteçler): üreteçler `JOSE-087/kanit/sentetik_uret.py`, `COSE-035/kanit/sentetik_cose.py`; sonuçlar hedef başına `kanit/duman-testi.txt`.

## 1. Özet tablo

| Hedef | Derleme | Sürüm (sabitleme) | B6 (desteklenmeyen biçim) | TK ML-DSA / composite | V± kapısı | Not |
|---|---|---|---|---|---|---|
| JOSE-001 IdentityModel | ok | 8.23.0 (nuspec `8b16f418`) | general, sd-jwt-*, oid4vci, dcapi, COSE | **TK1** / TK3 | **geçti** (ES256, ML-DSA-65) | EdDSA yok → kontrol kolu X yok |
| JOSE-002 JWT.NET | ok | 11.1.0 (`5a4a865e`) | aynı | TK3 / TK3 | geçti (ES256) | EdDSA yok; W anahtar türüne indirgenir |
| SDJWT-021 WalletFramework | ok | 3.1.0 (`2ed7a64b`) | general, sd-jwt-general/flattened, dcapi, dpop/tsl/req kompakt, COSE | TK3 / TK3 | **kaldı → adaptör geçersiz** | `typ = vc+sd-jwt` ve ES256 kodda sabit; `Verifier.VerifyPresentation` hep `false` |
| JOSE-070 php-jwt | ok | v7.2.0 (`f502cdbf`) | general, sd-jwt-*, oid4vci, dcapi, COSE | TK3 / TK3 | geçti (ES256, EdDSA) | W = anahtar–alg bağlaması |
| JOSE-071 lcobucci/jwt | ok | 5.6.0 (`bb3e9f21`) | aynı | TK3 / TK3 | geçti (ES256, EdDSA) | JWK API'si yok (PEM'e çevrilir) |
| COSE-035 cose-lib | ok | 4.8.2 (`8849e8bf`) | bütün JOSE/SD-JWT biçimleri | TK3 / TK3 | geçti (ES256, EdDSA, Ed25519) | ML-DSA yalnız HEAD'de (tanımlayıcı) |
| JOSE-087 ruby-jwt | ok | 3.3.0 (`ccf24892`) | general, sd-jwt-*, oid4vci, dcapi, COSE | TK3 / TK3 | geçti (ES256) | EdDSA çekirdekte yok → kontrol kolu X yok |
| JOSE-089 json-jwt | ok | 1.17.2 (`5fc6faed`) | sd-jwt-*, oid4vci, dcapi, COSE (general destekli) | TK3 / TK3 | geçti (ES256) | General JSON'da yalnız ilk imza; EdDSA yok |
| COSE-036 wolfCOSE | ok | git `f907071b` + wolfSSL v5.9.2 | bütün JOSE/SD-JWT biçimleri | **TK1** / TK3 | geçti (ES256, EdDSA, Ed25519, ML-DSA-65) | `WOLFCOSE_ENABLE_DEPRECATED_ALGS` (belgeli makro) gerekiyor |
| JOSE-031 guardian | ok | 2.5.0 (`a9c9838b`) + erlang-jose 1.11.12 | general, sd-jwt-*, oid4vci, dcapi, COSE | TK3 / TK3 | geçti (ES256, EdDSA, Ed25519) | hata nedenleri `:invalid_token`'da birleşir |
| SDJWT-002 affinidi | ok | 1.1.1 (`54a187b6`) | general, sd-jwt-general/flattened, dcapi, dpop/tsl/req kompakt, COSE | TK3 / TK3 | **kaldı → adaptör geçersiz** | `_sd_alg` zorunlu (TypeError); **imza sonucu yok sayılıyor** |
| JOSE-102 jwt-kit | ok | 5.3.0 (`b5f82fb9`) | general, sd-jwt-*, oid4vci, dcapi, COSE | **TK1** (SPI) / TK3 | geçti (ES256, EdDSA, ML-DSA-65) | başlık alg'ı imzalayıcıyla karşılaştırılmıyor |

Örneklem dışı (yazılmadı): JOSE-026 dart_jsonwebtoken, JOSE-017 jwt-cpp.

## 2. Ortak tasarım (bütün adaptörlerde aynı)
- **Çağrı:** KOSUCU §2 birebir (`adaptor /is/<isler> /c/<hedef>.<kosu>.jsonl`; `/v` hem `v1.3` hem `vektorler/` bağlamasıyla çalışır). Koşum `--network none`, `--memory=4g`.
- **Çıktı alanları:** KOSUCU §3 zorunlu alanları + `sozlesme`, `anahtar_yolu`. `adaptor_sha256` imaj yapımında adaptör kaynaklarından hesaplanır; `hedef_surum` kilit dosyasından.
- **Politika:** `temel = politika.split('|')[0].split('@')[0]` (yürütücü kuralı); GEC/P0/P1/P2 = yerel destek, R = ∅; IZIN-A/AX; L4 ailesi W = {A, X}, R = {X}. Tek imzalı nesnede etkin izin listesi = R (L4c "göç etmiş ihraççı"). Çok imzalı nesnede belgeli kural yoksa `ifade-edilemedi` (B4 satır sayıları NOTLAR'da). L4-YOL → `ifade-edilemedi` (hiçbir hedefte yol sınıfı API'si yok). Ek `VARSAYILAN` politikası (L5/B5 için; `isler.jsonl`'de yok) desteklenir.
- **Anahtar yolu:** hedef içinde bütün kollarda aynı: `JWK` (çoğu), `JWKS` (php-jwt kid'li), `dogrudan` (lcobucci, JWT.NET, jwt-kit), `COSE_Key` (COSE hedefleri); DPoP'ta `jwk-basligi`.
- **B6:** API incelemesiyle önceden; ESLEME.md §3. SD-JWT hedeflerinde kompakt `jws-cekirdek` vektörleri `"<jws>~"` olarak sunulur (yürütücü kuralı); OID4VCI toplu yanıtta `credentials[0]`.

## 3. Yürütücü kararı gereken noktalar
1. **SDJWT-021 ve SDJWT-002 V± kapısı:** V vektörleri düz JWS (`typ: JWT`, `_sd_alg` yok). SDJWT-021 `typ ≠ vc+sd-jwt`'yi, SDJWT-002 `_sd_alg`'sız yükü reddediyor → iki hedef **adaptör geçersiz** (gerekçeli). SD-JWT biçimli V± çifti olmadan bu hedeflerde kapı anlamlı değil.
2. **SDJWT-002 güvenlik gözlemi (ön bilgi):** imza doğrulama sonucu kullanılmıyor (`sd_jwt_verifier.dart`), sentetik bozuk imzalar `isVerified == true`. Batarya/oracle kullanılmadan, kaynak ve sentetik veriyle görüldü; ÖK ön-bilgi beyanına eklenmesi önerilir. Dışa bildirim yapılmadı.
3. **COSE-036:** ölçüm `WOLFCOSE_ENABLE_DEPRECATED_ALGS` ile; varsayılan derleme −7/−8'i reddeder. Alternatif: ESP256 (−9) vektörleri.
4. **JOSE-102 TK1:** ML-DSA `@_spi(PostQuantum)` arkasında (README'de belgeli) — "belgeli genel API" yorumu.
5. **Kontrol kolu X yok:** JOSE-001, JOSE-002, JOSE-087, JOSE-089 EdDSA/Ed25519 desteklemiyor (ruby-jwt için README'nin `jwt-eddsa` eklentisi eklenmedi).
6. **SDJWT-021 devir sürümü:** IdentityModel 8.0.1/7.5.2 (JOSE-001 8.23.0).
7. COSE-035 belgeli doğrulayıcısı README'deki çağıran kalıbıdır (alg/crit denetimi çağıranda) — L düzeyi yorumu.
8. **İş dosyaları CRLF:** `isler*.jsonl` CRLF satır sonu taşıyor; Swift adaptöründe bu bir çökme nedeniydi (düzeltildi). Diğer koşucular için bilgi.

## 4. Docker
- Oluşturulan ve korunan imajlar (dondurma sonrası koşum için): `a10-jose-001:1`, `a10-jose-002:1`, `a10-sdjwt-021:1`, `a10-jose-070:1`, `a10-jose-071:1`, `a10-cose-035:1`, `a10-jose-087:1`, `a10-jose-089:1`, `a10-cose-036:1`, `a10-jose-031:1`, `a10-sdjwt-002:1`, `a10-jose-102:1`.
- Geçici `a10-sdjwt-021-kaynak:1` (yalnız kaynak okuma) silindi. Toplu silme/prune yapılmadı; başka konteyner/imaja dokunulmadı. Bütün konteynerler `--rm`.

## 5. Gizlilik
- Ağ yalnız imaj yapımında anonim paket kayıtları (nuget.org, packagist/GitHub dist, rubygems.org, hex.pm, pub.dev, GitHub anonim git) için kullanıldı. Hiçbir API'ye kişisel veri gönderilmedi; dışa dönük eylem yok. (Kopyalanan `composer.lock` dosyalarında paket yazarlarının kamuya açık Packagist e-posta alanları vardır; kullanıcı verisi değildir.)
