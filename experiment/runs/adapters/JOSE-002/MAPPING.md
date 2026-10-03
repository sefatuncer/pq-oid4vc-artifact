# JOSE-002 JWT (jwt-dotnet/jwt) — policy → API mapping (contract 1.0 §2.2, RUNNER §2)

- **Target:** NuGet `JWT` **11.1.0** (nuspec commit `5a4a865eaad9`; assembly version 11.0.0.0), `packages.lock.json` the same as the environment (+ Newtonsoft.Json 13.0.4).
- **Image:** `a10-jose-002:1` (`FROM pq-a09-env-dotnet:1.0`). **Call:** `… a10-jose-002:1 adaptor /is/<isler> /c/JOSE-002.<kosu>.jsonl`.
- **Source:** `Adaptor.cs`, `Ortak.cs` (same skeleton as JOSE-001).

## 1. Shared rules
The same as `JOSE-087/MAPPING.md` §1 (normalisation, P2, L4-YOL included). Clock: `WithDateTimeProvider(SabitSaat(simdi))` (the library's `IDateTimeProvider` interface).

## 2. Policy mechanism: algorithm object bound to the key
JWT.NET has no allow-list option and no JWK API. Documented use: `JwtBuilder.Create().WithAlgorithm(new ES256Algorithm(ecdsaPublicKey)).MustVerifySignature().Decode(token)`.
- **Key path `dogrudan` (direct):** the selected JWK (EC) is converted in the adapter into an `ECDsa.Create(ECParameters{Q = x,y})` object (BCL).
- **W:** if the natural alg of the key type (P-256 → ES256, P-384 → ES384) is in W, that algorithm object is configured; otherwise no algorithm is given and the library rejects with `InvalidOperationException` ("Can't decode a token…").

| Policy | Configuration |
|---|---|
| GEC / P0 / P1 / P2 / VARSAYILAN | natural alg ∈ {ES256, ES384} |
| IZIN-A / IZIN-AX | natural alg ∈ {ES256} / {ES256, X} (only ES256 if X has no JWT.NET counterpart) |
| L4 / L4-S / L4-Y (compact) | natural alg ∈ {X} — no algorithm can be set up for X ∈ {EdDSA, Ed25519, ML-DSA-65, composite} |
| L4 / L4-S / L4-Y, legacy issuer (payload `iss` = `https://legacy-issuer.example`) | legacy-issuer record of L4c: W = {A, X}, R = ∅, i.e. the allow-list of `IZIN-AX`. The record is selected by the `iss` of the object before the library call (pre-registration §5.13, contract §5.3: "L4c (consecutive)", decision D9) |
| L4-YOL | `ifade-edilemedi` |

`dogrulanan_algoritmalar`: on acceptance the `Name` of the configured algorithm object (the object that performs the verification).

## 3. B6 decisions
| Serialization | Decision |
|---|---|
| compact | supported (`JwtDecoder`, 3 parts) |
| general, sd-jwt-*, oid4vci-toplu-yanit, dcapi-json-parametre, COSE_* | **B6** (no JSON serialization/SD-JWT/COSE API) |

## 4. Exception → hata_sinifi
| Library exception | hata_sinifi |
|---|---|
| `SignatureVerificationException`, alg exists in the library / does not exist | `imza-gecersiz` (`alg-anahtar-uyusmazligi` if the message contains "algorithm") / `alg-desteklenmiyor` |
| `InvalidOperationException` "Can't decode a token" (no algorithm configured): alg not in the library / alg ∉ W / alg ∈ W | `alg-desteklenmiyor` / `alg-izin-disi` / `alg-anahtar-uyusmazligi` (`sonuc_ham = red`) |
| `TokenExpiredException`, `TokenNotYetValidException` | `zaman` |
| `InvalidTokenPartsException`, `FormatException`, `ArgumentException` | `ayristirma` |
| `NotSupportedException` | `alg-desteklenmiyor` |
| other | `istisna-diger` |
