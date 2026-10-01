# COSE-036 wolfCOSE @ f907071b1012 — adaptör notları (01.10.2026)

## 1. Sürüm sabitleme
- Yayım yok → CERCEVE `son_commit_sha` `f907071b1012` (ÖK madde 14); wolfSSL v5.9.2-stable `ac01707f552c`, ortamın bayraklarıyla. `HEDEF_SURUM = git:f907071b1012`. GPL-3.0: yalnız ölçülür.

## 2. TK önerisi
| Kol | Öneri | Kanıt |
|---|---|---|
| ML-DSA-65 | **TK1** | `wolfcose.h` `WOLFCOSE_ALG_ML_DSA_65 (-49)`, `WOLFCOSE_KTY_AKP`, `wc_CoseKey_SetMlDsa`; wolfSSL `--enable-mldsa` (`WOLFSSL_HAVE_MLDSA`); V± ML-DSA kolunda geçti |
| composite | **TK3** | −55/composite yok; COSE-K6/K7 `red/alg-desteklenmiyor` (AKP + −55 anahtarı `UNSUPPORTED`) |

## 3. V± sonucu (`evidence/vpm-kosu.txt`; COSE V± satırları)
- COSE-VPLUS_ES256 ×4 `kabul`, VMINUS ×4 `red/imza-gecersiz`.
- COSE-VPLUS_EdDSA (−8) `kabul`, VMINUS `red/imza-gecersiz`; COSE-VPLUS_EdDSA-ED25519 (−19) `kabul`, VMINUS `red/imza-gecersiz`.
- **COSE-VPLUS_ML-DSA-65 `kabul` (`dogrulanan: ML-DSA-65`), COSE-VMINUS_ML-DSA-65 `red/imza-gecersiz`.**
- COSE-K6/K7 (−55): `red/alg-desteklenmiyor`. JOSE satırları B6.
- **Kapı: geçti (ES256 + EdDSA + Ed25519 + ML-DSA-65)** — `WOLFCOSE_ENABLE_DEPRECATED_ALGS` yapılandırmasıyla.

## 4. Yürütücüye notlar (karar gerekir)
1. **RFC 9053 kimlikleri varsayılan derlemede kapalı:** varsayılan `make` ile −7 ve −8 `COSE_BAD_ALG` (−9011) ile reddedilir (sentetik kanıt `evidence/duman-varsayilan-derleme.txt`; `docs/Macros.md` L149–157 "Off by default"). Ölçüm, belgeli makroyla açılmış derlemeyle yapıldı. Alternatif: varsayılan derleme + ES256 için ESP256 (−9) vektörleri (BATARYA-ESLEME NOTLAR H açık sorusu). Ortam kaydı (`kur.sh`) makrosuz `make all` idi.
2. Politika mekanizması `alg` iğnesidir (tek alg); çok alg'lı W'de doğal alg seçilir (ESLEME §2). Bu bir adaptör eşleme kararıdır.
3. **B4:** COSE_Sign çoklu imzacı kuralı için `wc_CoseSign_Verify` üzerinde imzacı döngüsü ≈ 12 satır C (yazılmadı).
4. Python sürücüsünde ctypes çağrıları kesilemez → vektör başına 60 s sınırı uygulanmaz (koşucu düzeyinde süre sınırı önerilir).

## 5. Koşu kaydı
- Duman testleri: `evidence/duman-varsayilan-derleme.txt` (makrosuz), `evidence/duman-testi.txt` (makrolu; fikstür `../COSE-035/evidence/sentetik_cose.py`, ML-DSA-65 dahil).
- Dondurma-öncesi dosya: 13:45Z (ilk), ~13:59Z, 14:05Z; V± aynı.
