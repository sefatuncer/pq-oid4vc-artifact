# SDJWT-002 selective_disclosure_jwt (affinidi-sdjwt-dart) — politika → API eşlemesi (sözleşme 1.0 §2.2, KOSUCU §2)

- **Hedef:** pub.dev `selective_disclosure_jwt` **1.1.1** (etiket `selective_disclosure_jwt-v1.1.1` → `54a187b64095`), `pubspec.lock` ortamla aynı (`dart pub get --enforce-lockfile`; geçişli `dart_jsonwebtoken`, `pointycastle`).
- **İmaj:** `a10-sdjwt-002:1` (`FROM pq-a09-env-dart:1.0`, analitik kapalı; `dart compile exe`). **Çağrı:** `… a10-sdjwt-002:1 adaptor /is/<isler> /c/SDJWT-002.<kosu>.jsonl`.
- **Kaynak:** `bin/adaptor.dart` (iskelet + adaptör).

## 1. Ortak kurallar
`JOSE-087/MAPPING.md` §1 ile aynı (normalleştirme, P2, L4-YOL → `ifade-edilemedi`).

## 2. Politika → API
Belgeli yol (README "Usage"): `SdJwtHandlerV1().decodeAndVerify(sdJwtToken: s, verifier: SDKeyVerifier(SdPublicKey(jwk_map, SdJwtSignAlgorithm.x)), verifyKeyBinding: kb)` → `SdJwt.isVerified`.
- `SDKeyVerifier.isAllowedAlgorithm(alg)` = `SdJwtSignAlgorithm.isSupported(alg)` (sabit: kütüphanenin desteklediği her alg); **imza, `SdPublicKey`'e bağlanan algoritmayla doğrulanır** (başlık alg'ıyla değil; `sdkey.dart` SDKeyVerifier). Politika bu yüzden **anahtar–alg iğnesiyle** kurulur.

| Politika | Yapılandırma |
|---|---|
| GEC / P0 / P1 / P2 / VARSAYILAN | `SdPublicKey(jwk, doğal_alg)` (EC P-256 → es256, P-384 → es384, OKP → eddsa) |
| IZIN-A / IZIN-AX | iğne = doğal alg ∈ W∩destek ise o, değilse W∩destek'in ilki; W∩destek boşsa doğrulayıcı kurulamaz → `red/alg-desteklenmiyor` (kütüphane çağrılmaz) |
| L4 / L4-S / L4-Y | aynı kural, W_etkin = R = {X} |
| L4-YOL | `ifade-edilemedi` |

- `verifyKeyBinding = (artefakt == "sd-jwt-vc+kb")`; `kb_aud`/`kb_nonce` için API parametresi yok.
- `Verifier` arayüzünün özel uygulaması (`isAllowedAlgorithm` = W) belgeli bir genişleme noktasıdır; özel kod sayıldığı için kullanılmadı (B4 adayı, NOTLAR).
- **Anahtar yolu `JWK`** (JWK haritası → `JWTKey.fromJWK`). **x5c:** API x5c almaz; X5C vektörlerinde anahtar manifest kid'iyle verilir.
- **Sunum:** kompakt `jws-cekirdek` vektörleri `"<jws>~"` (yürütücü kuralı); OID4VCI toplu yanıtta `credentials[0]`.
- `dogrulanan_algoritmalar`: kabulde iğnelenen alg (kütüphane imzayı bu alg ile doğrular).

## 3. B6 kararları
| Serileştirme / artefakt | Karar |
|---|---|
| sd-jwt-compact; compact `jws-cekirdek` (`"<jws>~"`); oid4vci-toplu-yanit | desteklenir |
| compact `dpop`, `status-list-token`, `oid4vp-istek`; general; sd-jwt-general; sd-jwt-flattened; dcapi-json-parametre; COSE_* | **B6** (`SdJwt.parse` yalnız `~` ayrımlı kompakt SD-JWT) |

## 4. Sonuç → hata_sinifi
Kütüphane imza hatasını yutar (`sd_jwt_verifier.dart`: istisna → `_isJwsVerified = false`); `isVerified == false` durumunda sınıf başlık alg'ı, W ve iğneden çıkarılır:
| Durum | hata_sinifi |
|---|---|
| `isVerified != true`, alg kütüphanede yok | `alg-desteklenmiyor` |
| alg ∉ W | `alg-izin-disi` |
| alg ≠ iğne | `alg-anahtar-uyusmazligi` |
| aksi (KB istendiyse `kb`) | `imza-gecersiz` / `kb` |
| `SdJwt.parse` istisnası ("Invalid SD-JWT …", `_sd_alg` yokken `TypeError`) | `ayristirma` (`TypeError` → `sonuc_ham = istisna`) |
| `SdPublicKey` kurulamadı (AKP) / iğne kurulamadı | `alg-desteklenmiyor` |
| diğer | `istisna-diger` |
