# JOSE-031 guardian — policy → API mapping (contract 1.0 §2.2, RUNNER §2)

- **Target:** Hex `guardian` **2.5.0** (tag v2.5.0 → `a9c9838b40f8`) + `jose` (erlang-jose) 1.11.12; `mix.lock` the same as the environment (`mix deps.get --check-locked`). Erlang/OTP 29 crypto → OpenSSL 3.5.7.
- **Image:** `a10-jose-031:1` (`FROM pq-a09-env-elixir:1.0`, `MIX_ENV=prod`). **Call:** `… a10-jose-031:1 adaptor /is/<isler> /c/JOSE-031.<kosu>.jsonl`.
- **Source:** `lib/adaptor.ex` (skeleton + adapter in one file; module `A10.Guardian` with `use Guardian, otp_app: :adaptor, issuer: "a10-adaptor"`).

## 1. Shared rules
The same as `JOSE-087/MAPPING.md` §1 (normalisation, P2, L4-YOL → `ifade-edilemedi`). 60 s per vector (`Task.yield`). Clock: Guardian uses the real clock (no fake-clock option); not affected, because `exp` lies in the future.

## 2. Policy → API
`Guardian.decode_and_verify(A10.Guardian, jwt, %{}, secret: JOSE.JWK.from_map(jwk), allowed_algos: W_etkin)` — the documented options `secret` and `allowed_algos` of Guardian (`guardian/token/jwt.ex` L17–39, `decode_token` L328–343 → `JOSE.JWT.verify_strict(secret, algos, token)`).

| Policy | `allowed_algos` |
|---|---|
| GEC / P0 / P1 / P2 | ["ES256", "ES384", "EdDSA", "Ed25519", "Ed448"] (erlang-jose native; `jose_jws.erl` from_map) |
| IZIN-A / IZIN-AX | ["ES256"] / ["ES256", X] |
| L4 / L4-S / L4-Y (compact) | [X] |
| L4 / L4-S / L4-Y, legacy issuer (payload `iss` = `https://legacy-issuer.example`) | legacy-issuer record of L4c: W = {A, X}, R = ∅, i.e. the allow-list of `IZIN-AX`. The record is selected by the `iss` of the object before the library call (pre-registration §5.13, contract §5.3: "L4c (consecutive)", decision D9) |
| VARSAYILAN | not given (module configuration/Guardian default) |
| L4-YOL | `ifade-edilemedi` |

- **Key path `JWK`:** `JOSE.JWK.from_map(jwk)`; an AKP (ML-DSA) key cannot be built (`FunctionClauseError`) → `red/alg-desteklenmiyor`.
- `dogrulanan_algoritmalar`: Guardian returns only the claims → `[]`.

## 3. B6 decisions
| Serialization | Decision |
|---|---|
| compact | supported (a Guardian token is a compact string; `peek` decodes compact) |
| general, sd-jwt-*, oid4vci-toplu-yanit, dcapi-json-parametre, COSE_* | **B6** (the Guardian API takes no JSON serialization/SD-JWT/COSE) |

## 4. Result → hata_sinifi
Guardian reduces the `{false, _, _}` result of `verify_strict` and the caught exceptions to a single `{:error, :invalid_token}` (`jwt.ex` L336–342). The distinction is made in the adapter from the header alg and W:
| Guardian result | hata_sinifi |
|---|---|
| `:invalid_token`, header alg not in the library | `alg-desteklenmiyor` |
| `:invalid_token`, alg ∉ W | `alg-izin-disi` |
| `:invalid_token`, alg ∈ W | `imza-gecersiz` |
| `:token_expired`, `:token_not_yet_valid` | `zaman` |
| `:secret_not_found` | `anahtar-bulunamadi` |
| `{:error, %Exception{}}` (rescue) | `istisna-diger` (`sonuc_ham = istisna`) |
| error from `JOSE.JWK.from_map` | `alg-desteklenmiyor` |
