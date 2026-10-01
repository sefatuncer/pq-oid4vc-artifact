# COSE-036 wolfCOSE — politika → API eşlemesi (sözleşme 1.0 §2.2, KOSUCU §2)

- **Hedef:** wolfCOSE @ `f907071b10127f3ae2dd7719749a91b039ff04a1` (yayım yok → CERCEVE `son_commit_sha`; ÖK madde 14), wolfSSL **v5.9.2-stable** (`ac01707f552c`) README "Full Build" bayraklarıyla (`--enable-mldsa` dahil) — ortam kaydıyla aynı.
- **Ölçüm yapılandırması:** wolfCOSE belgeli derleme makrosu **`WOLFCOSE_ENABLE_DEPRECATED_ALGS`** (`docs/Macros.md` L149–157; Makefile `EXTRA_CFLAGS`) ile `make shared`. Gerekçe: batarya ES256'yı RFC 9053 kimliği **−7**, EdDSA'yı **−8** ile taşır; varsayılan derleme bu kimlikleri `COSE_BAD_ALG` ile reddeder (`kanit/duman-varsayilan-derleme.txt`). Kod değişmez. Yürütücü onayı gerekir (NOTLAR §4).
- **İmaj:** `a10-cose-036:1` (`FROM pq-a09-env-c:1.0`). **Çağrı:** `… a10-cose-036:1 adaptor /is/<isler> /c/COSE-036.<kosu>.jsonl`.
- **Kaynak:** `kopru.c` (libkopru.so; yalnız wolfCOSE genel API'si), `adaptor.py` (JSON/G-Ç sürücüsü, ctypes ile aynı süreç; asgari CBOR okuyucu yalnız kid/imzacı sayısı için).

## 1. Ortak kurallar
`JOSE-087/ESLEME.md` §1 ile aynı (normalleştirme, P2, L4-YOL → `ifade-edilemedi`). COSE kimlikleri: ES256 −7, ES384 −35, EdDSA −8, Ed25519 −19, ML-DSA-44/65/87 −48/−49/−50, composite −55.

## 2. Politika mekanizması: anahtarın `alg` iğnesi
wolfCOSE'ta izin listesi API'si yoktur; doğrulama yolu anahtarın `alg` alanını uygular (`WOLFCOSE_KEY.alg` "WOLFCOSE_ALG_*, 0 if unset"; `src/wolfcose_sign1.c` "Honour the key->alg pin on the verify path" L1198–1205) ve alg ile eğri/anahtar türünü bağlar (`wolfCose_AlgCheckCrv`).
- **Anahtar yolu `COSE_Key`:** `cose_key_hex[kid]` → `wc_CoseKey_PeekInfo` → `wc_CoseKey_Init` + `wc_CoseKey_SetEcc|SetEd25519|SetMlDsa` (wolfCrypt nesnesi) → `wc_CoseKey_Decode`.
- **İğne:** GEC/P0/P1/P2/VARSAYILAN → iğne yok (Decode'un bıraktığı değer; AKP anahtarlar kendi `alg`'ını taşır) = kütüphane varsayılanı. IZIN-A/IZIN-AX/L4 ailesi → anahtarın doğal alg'ı W_etkin içindeyse o, değilse W_etkin'in ilk öğesi iğnelenir; kütüphane mesaj alg'ı ≠ iğne ise `COSE_BAD_ALG` verir.

| Politika | Yapılandırma |
|---|---|
| GEC / P0 / P1 / P2 / VARSAYILAN | iğnesiz anahtar |
| IZIN-A / IZIN-AX | iğne ∈ {−7} / {−7, X} |
| L4 / L4-S / L4-Y (COSE_Sign1 ya da tek imzacılı COSE_Sign) | iğne = X (etkin izin listesi = R) |
| çok imzacılı COSE_Sign × her politika | **`ifade-edilemedi`**: `wc_CoseSign_Verify(key, signerIndex, …)` imzacıyı tek tek doğrular; P0/P1/R kuralı için imzacılar üzerinde döngü çağıranın kodu olur (B4) |
| L4-YOL | **`ifade-edilemedi`** (x5chain yol sınıfı API'si yok) |

Doğrulama: `wc_CoseSign1_Verify(key, msg, …, &hdr, &payload)` / `wc_CoseSign_Verify(key, 0, …)`. Kabulde `dogrulanan_algoritmalar = [{alg: hdr.alg}]` (COSE_Sign'da imzacının korumalı alg'ı).

## 3. B6 kararları
| Serileştirme | Karar |
|---|---|
| COSE_Sign1, COSE_Sign | desteklenir |
| compact, general, sd-jwt-*, oid4vci-toplu-yanit, dcapi-json-parametre | **B6** |

## 4. Dönüş kodu → hata_sinifi (`asama`: 1 PeekInfo, 2 anahtar türü/ekleme, 3 Decode, 4 Verify)
| Durum | hata_sinifi |
|---|---|
| aşama < 4 ve `UNSUPPORTED`/`COSE_KEY_TYPE`/`BAD_ALG` ya da alg kütüphanede yok (ör. AKP + −55) | `alg-desteklenmiyor` |
| −9012 `COSE_SIG_FAIL` | `imza-gecersiz` |
| −9020 `CRYPTO` ve alg EdDSA/Ed25519 (wolfCrypt Ed25519 bozuk imzayı CRYPTO olarak döndürür; sentetik duman) | `imza-gecersiz` |
| −9011 `COSE_BAD_ALG` (aşama 4): alg kütüphanede yok / alg ∉ W / alg ∈ W | `alg-desteklenmiyor` / `alg-izin-disi` / `alg-anahtar-uyusmazligi` |
| −9015 `COSE_KEY_TYPE` | `alg-anahtar-uyusmazligi` |
| −9021 `UNSUPPORTED` | `alg-desteklenmiyor` |
| −9002/−9003/−9004/−9006/−9010 CBOR/etiket | `ayristirma` |
| −9014 `COSE_BAD_HDR` (crit varsa `crit`) | `crit` / `ayristirma` |
| diğer | `istisna-diger` |
