# SDJWT-021 WalletFramework.SdJwtVc 3.1.0 — adaptör notları (01.10.2026)

## 1. Sürüm sabitleme
- Yayımlanmış son sürüm 3.1.0 (iki çelişen etiket; nuspec commit `2ed7a64b9c44` ile çözüldü — ortam kaydı). Kaynak alıntıları aynı commit'ten (GitHub anonim, yalnız okuma için geçici imaj `a10-sdjwt-021-kaynak:1`; sonra silindi).

## 2. TK önerisi
| Kol | Öneri | Kanıt |
|---|---|---|
| ML-DSA-65 | **TK3** | `SdJwtDoc.cs` L61 `ValidAlgorithms = new string[] {"ES256"}`; geçişli IdentityModel 8.0.1'de ML-DSA yok (`evidence/api-tarama.txt`) |
| composite | **TK3** | aynı |

## 3. V± sonucu (`evidence/vpm-kosu.txt`) — **KALDI**
- VPLUS_ES256 ×4: `red/typ` — iç neden IDX10257 "Type: 'JWT'. Did not match: validationParameters.ValidTypes" (kütüphane yalnız `vc+sd-jwt` kabul eder; V vektörleri `typ: JWT`).
- VMINUS_ES256 ×4: `red/imza-gecersiz`. EdDSA/Ed25519/ML-DSA-65/CMP: `red/alg-desteklenmiyor`. COSE B6.
- **Düzeltme denemeleri (2):**
  1. `Verifier.VerifyPresentation` yolu (sentetik veride; `evidence/deneme1-verifypresentation.txt`): geçerli belirteç IDX10208 ile reddedildi; kaynakta yöntem her zaman `false` döndürüyor (`evidence/kaynak-alintilari.txt`).
  2. `SdJwtDoc.AssertThatJwtSignatureIsValid` yolu (batarya V±): V+ `typ` sabiti yüzünden reddedildi.
  - Kütüphanede başka genel doğrulama yolu yok; `typ` ve alg kodda sabit (`SdJwtDoc.cs` L55–62) → adaptörle düzeltilemez.
- **Sonuç: adaptör geçersiz (V± kapısı, gerekçeli).** Sentetik duman testinde `typ: vc+sd-jwt` + ES256 belirteci kabul, bozuk eşi red (`evidence/duman-testi.txt`, SENT_SD_vc_*): adaptör yolu çalışıyor; red nedeni kütüphane kısıtı.

## 4. Yürütücüye notlar
1. **Hedefin genel API'si -13 SD-JWT VC'lerini (`typ: dc+sd-jwt`) de reddeder** (yalnız `vc+sd-jwt`): bataryadaki VC* vektörlerinin çoğu `typ` ile düşecek. Ölçüm kapsamı (n_eff dışı mı, devir kümesi JOSE-001 üzerinden mi) yürütücü kararıdır.
2. **Devir sürüm farkı:** IdentityModel 8.0.1/7.5.2 (JOSE-001: 8.23.0).
3. Politika parametresi yok → IZIN/L4 ailesi `ifade-edilemedi`. "İfade edilemez" kanıt kuralı (sözleşme §5.5) için: tarama kayıtlı, kaynak satırları kayıtlı (`SdJwtDoc.cs` L49–73, `Verifier.cs`); ikinci bağımsız çalışma denemesi gerekir.
4. B4 alternatifi: `SdJwtDoc.IssuerSignedJwt`'yi doğrudan IdentityModel `JsonWebTokenHandler` ile doğrulamak (≈ 10 satır) — bu WalletFramework'ün değil IdentityModel'in ölçümü olur.

## 5. Koşu kaydı
- Dondurma-öncesi dosya: 13:13Z, ~13:59Z (normalleştirme) ve 14:05Z; V± aynı. (L4-YOL değişikliği bu hedefte kod değiştirmedi; `adaptor_sha256` 13:59Z koşusundan beri aynı.)
