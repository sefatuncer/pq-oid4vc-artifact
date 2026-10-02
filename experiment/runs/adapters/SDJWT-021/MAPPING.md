# SDJWT-021 WalletFramework.SdJwtVc — policy → API mapping (contract 1.0 §2.2, RUNNER §2)

- **Target:** NuGet `WalletFramework.SdJwtVc` **3.1.0** (nuspec commit `2ed7a64b9c44`); the verifier is in the transitive `WalletFramework.SdJwtLib` 3.1.0. Transitive IdentityModel: `Microsoft.IdentityModel.Tokens` 8.0.1, `System.IdentityModel.Tokens.Jwt` 7.5.2 (different from the 8.23.0 of JOSE-001). `packages.lock.json` the same as the environment.
- **Image:** `a10-sdjwt-021:1` (`FROM pq-a09-env-dotnet:1.0`). **Call:** `… a10-sdjwt-021:1 adaptor /is/<isler> /c/SDJWT-021.<kosu>.jsonl`.
- **Source:** `Adaptor.cs`, `Ortak.cs` (same skeleton as JOSE-001).

## 1. Shared rules
The same as `JOSE-087/MAPPING.md` §1 (normalisation, P2 included).

## 2. Public API and policy mapping
SdJwtLib has two public verification routes (reflection: `evidence/api-scan.txt`; source: `evidence/source-quotes.txt`, commit `2ed7a64b9c44`):
1. `Roles.Implementation.Verifier.VerifyPresentation(string presentation, string issuerJwk) → bool` — in the source `VerifyJwt` is called, but the method **returns `false` in every case** and rejects every token with IDX10208 because of `ValidateAudience = true` + `ValidAudience = null` (`Verifier.cs`, whole file). It cannot produce an acceptance → not used (attempt 1, `evidence/attempt1-verifypresentation.txt`).
2. **`new SdJwtDoc(serialized).AssertThatJwtSignatureIsValid(string issuerJwk, string expectedIssuer)`** (the public `SdJwtDoc` model) — **the route used.** Inside, `JwtSecurityTokenHandler.ValidateToken` is called with `ValidIssuer = expectedIssuer`, **`ValidTypes = {"vc+sd-jwt"}`**, **`ValidAlgorithms = {"ES256"}`** hard-coded (`SdJwtDoc.cs` L49–73).

| Policy | Mapping |
|---|---|
| GEC / P0 / P1 / P2 / VARSAYILAN | `AssertThatJwtSignatureIsValid(jwk_json, iss)` (the API takes only the key and the issuer; the alg/typ set is fixed in the library) |
| IZIN-A, IZIN-AX, L4, L4-S, L4-Y, L4-YOL | **`ifade-edilemedi`**: the API has no parameter for an alg allow-list, a required set or a path policy |

- **Key path `JWK`** (issuer JWK JSON string). **`expectedIssuer`:** the trusted issuer configuration (key ↔ iss): `https://issuer.example`; for the old issuer key (kid `GGKBh_lE…`, `keys/v1.3/roller.json`) `https://legacy-issuer.example`.
- **Presentation format:** compact `jws-cekirdek` vectors are presented, by the maintainers' rule, as an SD-JWT without disclosures: `"<jws>~"` (payload and signature unchanged). For the OID4VCI batch response (VC10) `credentials[0]` is evaluated (BATARYA-ESLEME K11). This API has no KB-JWT verification.
- **x5c:** the API takes no x5c; in the X5C vectors the key is given as a JWK via the manifest kid (deviation from contract §8 item 2; the target has no x5c route).
- `dogrulanan_algoritmalar`: the API returns `void`/`bool` → `[]`.

## 3. B6 decisions
| Serialization / artefact | Decision |
|---|---|
| sd-jwt-compact; compact `jws-cekirdek` (`"<jws>~"`); oid4vci-toplu-yanit (`credentials[0]`) | supported |
| compact `dpop`, `status-list-token`, `oid4vp-istek` | **B6** (not an SD-JWT VC; not an API input) |
| general, sd-jwt-general, sd-jwt-flattened, dcapi-json-parametre | **B6** (`SdJwtDoc` parses only the `~`-separated compact form) |
| COSE_* | **B6** |

## 4. Exception → hata_sinifi
By the inner exception of `InvalidOperationException("Invalid SD-JWT - Issuer Signed Jwt invalid")` (ShowPII on; for diagnosis only):
| Inner cause | hata_sinifi |
|---|---|
| IDX10256/IDX10257 `SecurityTokenInvalidTypeException` | `typ` |
| IDX10511/10634/10500/10503 and header alg not in the library (other than ES256) | `alg-desteklenmiyor` |
| IDX10696 | `alg-izin-disi` |
| IDX10500/10503/10501 | `anahtar-bulunamadi` |
| IDX10511/10504 (signature) | `imza-gecersiz` |
| IDX10222/10223 (lifetime) | `zaman` |
| parsing (IDX12741/14100, JsonReader, FormatException) | `ayristirma` |
| other | `istisna-diger` |
