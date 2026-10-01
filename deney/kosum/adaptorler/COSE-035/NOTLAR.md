# COSE-035 web-auth/cose-lib 4.8.2 — adaptör notları (01.10.2026)

## 1. Sürüm sabitleme
- ÖK madde 14: yayımlanmış son sürüm **4.8.2** (`8849e8bf043a`). Çerçeve HEAD `1c854bf63c5c`'de ML-DSA (`src/Algorithm/Signature/MLDSA`) var, 4.8.2'de yok; madde 14 gereği HEAD yeteneği yalnız tanımlayıcı raporlanır. `spomky-labs/cbor-php` 3.4.2 ortam düzeltmesiyle aynı.

## 2. TK önerisi
| Kol | Öneri | Kanıt |
|---|---|---|
| ML-DSA-65 | **TK3** | 4.8.2 `src/Algorithm/Signature`: ECDSA, EdDSA, FullySpecified, RSA; ML-DSA/AKP/−49/−55 deseni 0 eşleşme (`kanit/api-tarama.txt` sonu). HEAD TK1 adayıdır (tanımlayıcı) |
| composite | **TK3** | aynı |

## 3. V± sonucu (`kanit/vpm-kosu.txt`; COSE V± satırları, yürütücü 01.10)
- COSE-VPLUS_ES256 ×4 `kabul`, COSE-VMINUS_ES256 ×4 `red/imza-gecersiz`.
- COSE-VPLUS_EdDSA (−8) `kabul`, VMINUS `red/imza-gecersiz`; COSE-VPLUS_EdDSA-ED25519 (−19) `kabul`, VMINUS `red/imza-gecersiz`.
- COSE-VPLUS/VMINUS_ML-DSA-65 ve COSE-K6/K7 (−55): `red/alg-desteklenmiyor` (TK3 ile tutarlı).
- JOSE V± satırları: `uygulanamaz/bicim-desteklenmiyor` (B6).
- **Kapı: geçti (ES256 + EdDSA + Ed25519).** Kontrol etiketi: ikisi de destekli → `EdDSA` (sözleşme §8 m.4).

## 4. Notlar
1. **Belgeli doğrulayıcı çağıranın kalıbıdır:** alg ve crit denetimi README'ye göre çağıranın sorumluluğu. Adaptör README kalıbını birebir uygular; izin listesi `Algorithm\Manager`'dır (belgeli `has/get`). L düzeyi değerlendirmesinde bu "belgeli yapılandırma" mı, "README örnek kodu" mu sayılacağı yürütücü kararıdır (kod: `adaptor.php` `algKontrol`, 15 satır).
2. **Çoklu imzacı (COSE_Sign):** belgeli kural yok → `ifade-edilemedi`; B4 alternatifi: `CoseSignature::all()` üzerinde döngü + R/P0/P1 ≈ 10 satır (yazılmadı).
3. **L3:** `Manager::withKeyRestrictionsEnforced()` anahtarın `alg` (etiket 3) alanını uygular; batarya EC2/OKP COSE_Key'leri `alg` taşımaz, bu yüzden bağlama anahtar türü denetimine (verify istisnası) kalır.
4. Sentetik COSE fikstürü: `kanit/sentetik_cose.py` (BATARYA DEĞİL), duman testi `kanit/duman-testi.txt`.

## 5. Koşu kaydı
- Dondurma-öncesi dosya: 13:00Z (32 satır, ilk koşu kapıyı geçti) ve ~13:59Z (politika-adı normalleştirme sonrası imajla; sonuç aynı).
- **Son koşu (14:05Z):** L4-YOL → `ifade-edilemedi` kuralı eklendikten sonra imaj yeniden yapıldı, aynı 32 satırlık dosya yeniden koşuldu (V± sonuçları değişmedi).
