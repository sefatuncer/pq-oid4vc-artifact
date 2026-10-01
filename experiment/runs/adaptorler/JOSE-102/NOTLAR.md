# JOSE-102 jwt-kit 5.3.0 — adaptör notları (01.10.2026)

## 1. Sürüm sabitleme
- Yayımlanmış son sürüm 5.3.0 (`b5f82fb9dc23`), ortamın `Package.resolved`'ı (git revizyonları sabit).

## 2. TK önerisi
| Kol | Öneri | Kanıt |
|---|---|---|
| ML-DSA-65 | **TK1** | `Sources/JWTKit/MLDSA/*` (`MLDSA65PublicKey`, `JWTKeyCollection.add(mldsa:)`), README L276–297 (belgeli; `@_spi(PostQuantum)` bayrağı arkasında). `@available(macOS 26)` Linux'u kısıtlamıyor; swift-crypto CryptoExtras MLDSA Linux'ta çalıştı. V± ML-DSA kolunda geçti |
| composite | **TK3** | composite deseni yok; CMP00 `red/alg-desteklenmiyor` |

## 3. V± sonucu (`kanit/vpm-kosu.txt`)
- ES256 ×4 `kabul` / VMINUS ×4 `red/imza-gecersiz`; EdDSA `kabul` / VMINUS `red`; VPLUS_EdDSA-ED25519 (başlık `Ed25519`) `kabul` / VMINUS `red`.
- **ML-DSA-65: VPLUS `kabul` (`dogrulanan: ML-DSA-65`), VMINUS `red/imza-gecersiz`.**
- CMP00/01: `red/alg-desteklenmiyor`. COSE B6.
- **Kapı: geçti (ES256 + EdDSA + ML-DSA-65).** Kontrol etiketi `EdDSA` (`Ed25519` etiketi belgeli değil; kütüphane başlık etiketine bakmadan EdDSA anahtarıyla doğruladığı için kabul etti).

## 4. Yürütücüye notlar
1. **SPI kararı:** ML-DSA API'si `@_spi(PostQuantum)` arkasında ("breaking changes" uyarısı); README'de belgeli. TK1 sayılması için "belgeli genel API" yorumu yürütücü onayı ister (envanter notu "macOS 26+" Linux'ta geçerli değil — ortam kaydıyla tutarlı).
2. **Başlık alg'ı karşılaştırılmıyor (kaynak gözlemi):** `JWTSigner.verify` yalnız kayıtlı algoritmayla imzayı doğrular (`kanit/api-tarama.txt`, JWTSigner.swift). Alg–anahtar uyuşmazlığı vakaları (K10) ve etiket duyarlılığı bu yüzden ilginç olacak; burada ölçülmedi.
3. W yalnız kaydedilen anahtar kümesiyle kurulabilir (ESLEME §2) — kid başına tek imzalayıcı; ihraççı başına politika (L4c) koleksiyon kurulumuyla ifade edilir.
4. Çoklu imza B6; B4 adayı yok. Swift sürücüsünde vektör başına 60 s sınırı yok (async çağrılar sıralı).

## 5. Koşu kaydı
- Duman testi `kanit/duman-testi.txt`. İlk sürümde iş dosyası `split("\n")` ile okunuyordu; CRLF satır sonlarında (Swift'te `"\r\n"` tek Character) tek satır görünüp çöküyordu → `components(separatedBy: .newlines)` (battery koşusundan önce, sentetik veride bulundu).
- Dondurma-öncesi dosya: 13:57Z, ~13:59Z, 14:05Z; V± aynı.
