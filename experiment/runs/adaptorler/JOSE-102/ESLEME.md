# JOSE-102 jwt-kit — politika → API eşlemesi (sözleşme 1.0 §2.2, KOSUCU §2)

- **Hedef:** vapor/jwt-kit **5.3.0** (`b5f82fb9dc23`; çerçeve HEAD `0c74d3201bff` değil) + swift-crypto 4.5.2, swift-asn1 1.7.3, swift-certificates 1.21.0, swift-log 1.15.1 — `Package.resolved` ortamla aynı.
- **İmaj:** `a10-jose-102:1` (`FROM pq-a09-env-swift:1.0`; Swift 6.4, Linux). **Çağrı:** `… a10-jose-102:1 adaptor /is/<isler> /c/JOSE-102.<kosu>.jsonl`.
- **Kaynak:** `Sources/Adaptor/Adaptor.swift`, `Package.swift`.

## 1. Ortak kurallar
`JOSE-087/ESLEME.md` §1 ile aynı (normalleştirme, P2, L4-YOL → `ifade-edilemedi`). Saat: yük türü `Yuk: JWTPayload` içinde `exp.verifyNotExpired(currentDate: simdi)` (jwt-kit'in belgeli yük doğrulama kalıbı). İş dosyası CRLF güvenli okunur.

## 2. Politika mekanizması: koleksiyona kaydedilen anahtar nesnesi
jwt-kit'te izin listesi yoktur. `JWTKeyCollection.verify` kid'e göre imzalayıcıyı seçer (kid yoksa varsayılan) ve **imzayı kayıtlı anahtar nesnesinin algoritmasıyla doğrular; başlık `alg`'ı imzalayıcıyla karşılaştırılmaz** (`JWTSigner.swift` verify, `kanit/api-tarama.txt`). Politika bu yüzden **hangi anahtar nesnesinin kaydedildiğiyle** kurulur:
- Anahtar yolu **`dogrudan`** (bütün kollarda): EC → `ES256PublicKey/ES384PublicKey(parameters: (x, y))`, OKP → `EdDSA.PublicKey(x:curve: .ed25519)`, AKP → `MLDSA65PublicKey/MLDSA87PublicKey(rawRepresentation:)` (`@_spi(PostQuantum) import JWTKit`; README "MLDSA" bölümü).
- Anahtarın doğal alg'ı W_etkin içindeyse `keys.add(ecdsa:|eddsa:|mldsa:, kid:)`; değilse koleksiyon boş kalır → kütüphane `JWTError.noKeyProvided`.

| Politika | Kayıt |
|---|---|
| GEC / P0 / P1 / P2 / VARSAYILAN | anahtar her zaman kaydedilir (doğal alg kütüphanede varsa) |
| IZIN-A / IZIN-AX | doğal alg ∈ {ES256} / {ES256, X} |
| L4 / L4-S / L4-Y (kompakt) | doğal alg ∈ {X} |
| L4-YOL | `ifade-edilemedi` |

`dogrulanan_algoritmalar`: kabulde kayıtlı anahtarın algoritması (kütüphane doğrulamayı onunla yapar).

## 3. B6 kararları
| Serileştirme | Karar |
|---|---|
| compact | desteklenir (`DefaultJWTParser`, 3 bölüm) |
| general, sd-jwt-*, oid4vci-toplu-yanit, dcapi-json-parametre, COSE_* | **B6** (JWS JSON/SD-JWT/COSE API'si yok) |

## 4. Hata → hata_sinifi
| Kütüphane hatası | hata_sinifi |
|---|---|
| `JWTError.signatureVerificationFailed` | `imza-gecersiz` |
| `.claimVerificationFailure` (exp) | `zaman` |
| `.malformedToken`, `.invalidHeaderField` | `ayristirma` |
| `.noKeyProvided`, `.unknownKID`: başlık alg kütüphanede yok / alg ∉ W / aksi | `alg-desteklenmiyor` / `alg-izin-disi` / `anahtar-bulunamadi` |
| anahtar nesnesi kurulamadı ya da anahtar türü kütüphanede yok (composite) | `alg-desteklenmiyor` |
| diğer | `istisna-diger` |
