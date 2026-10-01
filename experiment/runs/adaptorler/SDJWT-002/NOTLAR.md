# SDJWT-002 selective_disclosure_jwt 1.1.1 — adaptör notları (01.10.2026)

## 1. Sürüm sabitleme
- Yayımlanmış son sürüm 1.1.1 (etiket → `54a187b64095`), ortamın `pubspec.lock`'u.

## 2. TK önerisi
| Kol | Öneri | Kanıt |
|---|---|---|
| ML-DSA-65 | **TK3** | `SdJwtSignAlgorithm`: ES256/384/512, ES256K, RS*, HS*, EdDSA; ML-DSA yok (`kanit/api-tarama.txt`). `Verifier` arayüzü genişleme noktası (TK2 kapsam dışı) |
| composite | **TK3** | aynı |

## 3. V± sonucu (`kanit/vpm-kosu.txt`) — **KALDI**
- VPLUS_ES256 ×4, VPLUS_EdDSA, VPLUS_EdDSA-ED25519 ve VMINUS eşleri: `istisna/ayristirma` — `SdJwt.parse` `"<jws>~"` sunumunda yükte `_sd_alg` olmadığı için `Hasher.fromString(null)` ile `TypeError` atar (`sdjwt.dart` L143–144; `kanit/kaynak-alintilari.txt`). RFC 9901'e göre `_sd_alg` isteğe bağlıdır; V vektörleri SD-JWT değil düz JWS'dir.
- ML-DSA-65, CMP: `red/alg-desteklenmiyor`. COSE B6.
- Yükü değiştirmeden düzeltme yolu yok (`SdJwt._fromParts` özel; `verify()` `SdJwt` nesnesi ister) → **adaptör geçersiz (V± kapısı, gerekçeli).**

## 4. Yürütücüye notlar — ÖNEMLİ
1. **İmza doğrulama sonucu yok sayılıyor (kaynak gözlemi + sentetik duman):** `SdJwtVerifyAction.execute` `verifyJwt(...)`'in döndürdüğü `bool`'u kullanmıyor; istisna yoksa `_isJwsVerified = true` yazıyor (`verify/sd_jwt_verifier.dart`), `SDKeyVerifier.verify` ise hataları yakalayıp `false` döndürüyor (`models/sdkey.dart`). Sentetik (batarya dışı) `_sd_alg`'lı SD-JWT'lerde **bozuk imzalı eşler de `isVerified == true`** döndü (`kanit/duman-testi.txt`, `SENT_SD_*_MINUS_*`). Bu, dondurma öncesi edinilmiş bir ön bilgidir (batarya/oracle kullanılmadı); ÖK sapma/ön-bilgi kaydına girmesi önerilir. Dışa dönük bildirim yapılmadı.
2. Başlık alg'ı yalnız "destekleniyor mu" diye denetlenir; doğrulama `SdPublicKey`'in alg'ıyla yapılır (alg–anahtar bağlaması başlıkla karşılaştırılmaz).
3. V± için SD-JWT biçimli (`_sd_alg`'lı) V+/V− vektörleri yok; bu hedef (ve SDJWT-021) için V± kapısı ancak SD-JWT VC biçimli bir V± çiftiyle anlamlı olur — yürütücü kararı.
4. **B4:** `Verifier` arayüzünü `isAllowedAlgorithm(alg) => W.contains(alg)` ve `SDKeyVerifier`'a devreden `verify` ile uygulamak ≈ 6 satır Dart (yazılmadı).

## 5. Koşu kaydı
- Duman testi `kanit/duman-testi.txt` (sentetik `SENT_SD_*` dahil). Dondurma-öncesi dosya: 13:48Z, ~13:59Z, 14:05Z; V± aynı.
