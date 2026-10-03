# JOSE-001 Microsoft.IdentityModel.JsonWebTokens — policy → API mapping (contract 1.0 §2.2, RUNNER §2)

- **Target:** the package set of `System.IdentityModel.Tokens.Jwt` **8.23.0** (environment record; nuspec commit `8b16f418b3d5`) → `Microsoft.IdentityModel.JsonWebTokens` / `.Tokens` 8.23.0. `packages.lock.json` the same as the environment (`dotnet restore --locked-mode`).
- **Image:** `a10-jose-001:1` (`FROM pq-a09-env-dotnet:1.0`; .NET 10.0.12, Ubuntu 26.04 OpenSSL 3.5.5, `MLDsa.IsSupported=True`). Telemetry off.
- **Call:** `… a10-jose-001:1 adaptor /is/<isler> /c/JOSE-001.<kosu>.jsonl`. **API scan:** `adaptor tara '<regex>'` (reflection; `Ortak.cs` `Tara`).
- **Source:** `Adaptor.cs`, `Ortak.cs` (same skeleton as JOSE-002, SDJWT-021).

## 1. Shared rules
The same as `JOSE-087/MAPPING.md` §1 (A/X, W/R, effective allow-list for a single signature = R, key path `JWK`, VARSAYILAN, only `dogrulama_girdileri`, policy name normalisation `split('|')[0].split('@')[0]`, P2 ∈ {GEC, P0, P1}, L4-YOL → `ifade-edilemedi`). 60 s per vector (`Task.Wait`).

## 2. Policy → API
`new JsonWebTokenHandler().ValidateTokenAsync(jwt, new TokenValidationParameters { ValidAlgorithms = W_etkin, IssuerSigningKey = new JsonWebKey(jwk_json), ValidateIssuer = false, ValidateAudience = false, RequireExpirationTime = false, ValidateLifetime = true })`

| Policy | `ValidAlgorithms` |
|---|---|
| GEC / P0 / P1 / P2 | {ES256, ES384, ML-DSA-44, ML-DSA-65, ML-DSA-87} (native; `SecurityAlgorithms.EcdsaSha256/384`, `MlDsa44/65/87`) |
| IZIN-A / IZIN-AX | {ES256} / {ES256, X} |
| L4 / L4-S / L4-Y (compact) | {X} |
| L4 / L4-S / L4-Y, legacy issuer (payload `iss` = `https://legacy-issuer.example`) | legacy-issuer record of L4c: W = {A, X}, R = ∅, i.e. the allow-list of `IZIN-AX`. The record is selected by the `iss` of the object before the library call (pre-registration §5.13, contract §5.3: "L4c (consecutive)", decision D9) |
| VARSAYILAN | `null` (library default) |
| L4-YOL | `ifade-edilemedi` |

- `RequireExpirationTime = false`: the K10 vectors have no `exp`; the default (true) would reject them with `IDX10225` regardless of the signature. `ValidateLifetime` on (real clock; `exp` = 1821536000).
- `IdentityModelEventSource.ShowPII = true` is for diagnosis only: it makes the "Exceptions caught" part of the IDX10511 message (the actual cause, e.g. IDX10696) visible; it does not change the verification behaviour.
- `dogrulanan_algoritmalar`: on acceptance `(result.SecurityToken as JsonWebToken).Alg`.

## 3. B6 decisions
| Serialization | Decision | Basis |
|---|---|---|
| compact | supported | `JsonWebTokenHandler` |
| general, sd-jwt-*, oid4vci-toplu-yanit, dcapi-json-parametre | **B6** | no JWS JSON serialization and no SD-JWT API (reflection scan: `evidence/api-scan.txt`) |
| COSE_* | **B6** | no COSE |

## 4. Exception → hata_sinifi
| Library result (`TokenValidationResult.Exception`, including inner messages) | hata_sinifi |
|---|---|
| `SecurityTokenInvalidAlgorithmException` / IDX10696, alg exists in the library / does not exist | `alg-izin-disi` / `alg-desteklenmiyor` |
| IDX10634/IDX10652/`NotSupportedException`, alg exists in the library / does not exist | `alg-anahtar-uyusmazligi` / `alg-desteklenmiyor` |
| `SecurityTokenSignatureKeyNotFoundException` | `anahtar-bulunamadi` |
| `SecurityTokenInvalidSignatureException` (IDX10511), header alg not in the library (EdDSA, composite, unregistered: "Exceptions caught" empty) | `alg-desteklenmiyor` |
| the same, alg exists in the library | `imza-gecersiz` |
| `SecurityTokenExpired/NotYetValid/NoExpiration/InvalidLifetime` | `zaman` |
| `SecurityTokenMalformedException`, `ArgumentException` | `ayristirma` |
| `SecurityTokenInvalidTypeException` | `typ` |
| other | `istisna-diger` |
