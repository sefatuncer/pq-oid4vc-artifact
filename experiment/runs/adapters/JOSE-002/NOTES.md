# JOSE-002 JWT.NET 11.1.0 — adapter notes (01.10.2026)

## 1. Version pinning
- Latest published release 11.1.0 (2026-07-06; tags in date format, nuspec commit `5a4a865eaad9`; not the frame HEAD `034f1fe9faef`).

## 2. TK proposal
| Arm | Proposal | Evidence |
|---|---|---|
| ML-DSA-65 | **TK3** | `JwtAlgorithmName`: HS256/384/512, RS256…RS4096, ES256/384/512, None; EdDSA/ML-DSA/JWK 0 matches (`evidence/api-tarama.txt`). `IAlgorithmFactory` extension point (TK2 out of scope) |
| composite | **TK3** | the same |

## 3. V± result (`evidence/vpm-kosu.txt`)
- ES256: VPLUS ×4 `kabul`, VMINUS ×4 `red/imza-gecersiz`. EdDSA/Ed25519, ML-DSA-65, CMP: `red/alg-desteklenmiyor`. COSE B6.
- **Gate: passed (ES256 only).**

## 4. Issues and notes for the maintainers
1. **No control arm X** (no EdDSA/Ed25519).
2. JWT.NET verifies with the configured algorithm object; whether the header alg is compared with the name of the object is not documented in the API (the L3 behaviour will be measured with K10 after the freeze; not tested here).
3. The documented route for a W with several algs is `WithAlgorithmFactory(IAlgorithmFactory)` (e.g. `ECDSAAlgorithmFactory`); a factory that selects the alg from the header was not used because it loosens the key–alg binding; W is reduced to a single key type (MAPPING §2).
4. Multi-signature B6; no B4 candidate.

## 5. Run record
- Smoke test `evidence/duman-testi.txt`. In the first smoke version `e.ToString()` (the stack trace contains "JWT.Algorithms") wrongly gave `alg-anahtar-uyusmazligi` → switched to `e.Message` (before the battery run).
- Pre-freeze file: 13:08Z, ~13:59Z, 14:05Z; V± results the same.
