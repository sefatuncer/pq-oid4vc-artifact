# JOSE-031 guardian 2.5.0 — adaptör notları (01.10.2026)

## 1. Sürüm sabitleme
- Yayımlanmış son sürüm 2.5.0 (etiket → `a9c9838b40f8`; çerçeve HEAD `6e86224f9c0a` değil). ÖK madde 13: JOSE-104 yerine örneklemde.

## 2. TK önerisi
| Kol | Öneri | Kanıt |
|---|---|---|
| ML-DSA-65 | **TK3** | erlang-jose 1.11.12 `jose_jws.erl` from_map: Ed25519/Ed448/EdDSA, ES*, HS*, Poly1305, PS*, RS*, none; ML-DSA/AKP 0 eşleşme (`kanit/api-tarama.txt`) |
| composite | **TK3** | aynı |

## 3. V± sonucu (`kanit/vpm-kosu.txt`)
- ES256 ×4 `kabul` / VMINUS ×4 `red/imza-gecersiz`; EdDSA `kabul` / VMINUS `red`; `Ed25519` etiketi `kabul` / VMINUS `red` (erlang-jose iki etiketi de tanır → kontrol kolu `EdDSA`, sözleşme §8 m.4).
- ML-DSA-65, CMP00/01: `red/alg-desteklenmiyor` (AKP JWK kurulamaz). COSE B6.
- **Kapı: geçti (ES256 + EdDSA + Ed25519).**

## 4. Notlar
1. Guardian hata nedenlerini `:invalid_token`'da birleştirir; `hata_sinifi` ayrımı adaptör çıkarımıdır (ESLEME §4). Karar (kabul/red) kütüphanenindir.
2. L2: `allowed_algos` çağrı başına seçenektir (belgeli). L3: `JOSE.JWT.verify_strict` imzayı anahtar türü ile alg uyumuna göre doğrular (davranış dondurma sonrası K10 ile ölçülecek).
3. L4c: Guardian `SecretFetcher` davranışı (`fetch_verifying_secret(mod, headers, opts)`) başlığa göre ihraççı anahtarı seçmeye izin verir (belgeli genişleme; ihraççı başına alg kümesi `allowed_algos` ile çağrı başına).
4. Çoklu imza B6; B4 adayı yok. `dogrulanan_algoritmalar` boş (Guardian göstermez).

## 5. Koşu kaydı
- Duman testi `kanit/duman-testi.txt`. Dondurma-öncesi dosya: 13:15Z, ~13:59Z, 14:05Z; V± aynı.
