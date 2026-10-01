# JOSE-031 guardian — politika → API eşlemesi (sözleşme 1.0 §2.2, KOSUCU §2)

- **Hedef:** Hex `guardian` **2.5.0** (etiket v2.5.0 → `a9c9838b40f8`) + `jose` (erlang-jose) 1.11.12; `mix.lock` ortamla aynı (`mix deps.get --check-locked`). Erlang/OTP 29 crypto → OpenSSL 3.5.7.
- **İmaj:** `a10-jose-031:1` (`FROM pq-a09-env-elixir:1.0`, `MIX_ENV=prod`). **Çağrı:** `… a10-jose-031:1 adaptor /is/<isler> /c/JOSE-031.<kosu>.jsonl`.
- **Kaynak:** `lib/adaptor.ex` (iskelet + adaptör tek dosyada; `A10.Guardian` modülü `use Guardian, otp_app: :adaptor, issuer: "a10-adaptor"`).

## 1. Ortak kurallar
`JOSE-087/ESLEME.md` §1 ile aynı (normalleştirme, P2, L4-YOL → `ifade-edilemedi`). Vektör başına 60 s (`Task.yield`). Saat: Guardian gerçek saati kullanır (sahte saat seçeneği yok); `exp` geleceği gösterdiği için etkilenmez.

## 2. Politika → API
`Guardian.decode_and_verify(A10.Guardian, jwt, %{}, secret: JOSE.JWK.from_map(jwk), allowed_algos: W_etkin)` — Guardian'ın belgeli `secret` ve `allowed_algos` seçenekleri (`guardian/token/jwt.ex` L17–39, `decode_token` L328–343 → `JOSE.JWT.verify_strict(secret, algos, token)`).

| Politika | `allowed_algos` |
|---|---|
| GEC / P0 / P1 / P2 | ["ES256", "ES384", "EdDSA", "Ed25519", "Ed448"] (erlang-jose yerel; `jose_jws.erl` from_map) |
| IZIN-A / IZIN-AX | ["ES256"] / ["ES256", X] |
| L4 / L4-S / L4-Y (kompakt) | [X] |
| VARSAYILAN | verilmez (modül yapılandırması/Guardian varsayılanı) |
| L4-YOL | `ifade-edilemedi` |

- **Anahtar yolu `JWK`:** `JOSE.JWK.from_map(jwk)`; AKP (ML-DSA) anahtarı kurulamaz (`FunctionClauseError`) → `red/alg-desteklenmiyor`.
- `dogrulanan_algoritmalar`: Guardian yalnız talepleri döndürür → `[]`.

## 3. B6 kararları
| Serileştirme | Karar |
|---|---|
| compact | desteklenir (Guardian belirteci kompakt dizedir; `peek` kompakt çözer) |
| general, sd-jwt-*, oid4vci-toplu-yanit, dcapi-json-parametre, COSE_* | **B6** (Guardian API'si JSON serileştirme/SD-JWT/COSE almaz) |

## 4. Sonuç → hata_sinifi
Guardian, `verify_strict`'in `{false, _, _}` sonucunu ve yakalanan istisnaları tek bir `{:error, :invalid_token}`'a indirger (`jwt.ex` L336–342). Ayrım adaptörde başlık alg'ı ve W ile yapılır:
| Guardian sonucu | hata_sinifi |
|---|---|
| `:invalid_token`, başlık alg kütüphanede yok | `alg-desteklenmiyor` |
| `:invalid_token`, alg ∉ W | `alg-izin-disi` |
| `:invalid_token`, alg ∈ W | `imza-gecersiz` |
| `:token_expired`, `:token_not_yet_valid` | `zaman` |
| `:secret_not_found` | `anahtar-bulunamadi` |
| `{:error, %Exception{}}` (rescue) | `istisna-diger` (`sonuc_ham = istisna`) |
| `JOSE.JWK.from_map` hatası | `alg-desteklenmiyor` |
