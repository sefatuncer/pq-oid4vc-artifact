# JOSE-089 json-jwt — policy → API mapping (contract 1.0 §2.2, RUNNER §2)

- **Target:** `json-jwt` 1.17.2 (tag v1.17.2 → `5fc6faed950f`), `Gemfile.lock` CHECKSUMS `sha256=97e37c1c…` (the same file as the environment record).
- **Image:** `a10-jose-089:1` (`FROM pq-a09-env-ruby:1.0`; Ruby 3.4.11, OpenSSL 3.5.7). Runs with `--network none`.
- **Call:** `docker run --rm --network none -v <v1.3>:/v:ro -v <anahtarlar>:/anahtarlar:ro -v <isler>:/is:ro -v <cikti>:/c a10-jose-089:1 adaptor /is/<isler> /c/JOSE-089.<kosu>.jsonl`
- **Source:** `adaptor.rb`, `ortak.rb` (same skeleton as JOSE-087).

## 1. Shared rules

The same as `JOSE-087/MAPPING.md` §1 (A/X; GEC = the battery algorithms the library supports natively; IZIN-A/AX; L4 family W = {A, X}, R = {X}; effective allow-list for a single-signature object = R; key path `JWK` in all arms; only `dogrulama_girdileri` from the manifest; the additional policy VARSAYILAN; `sonuc_ham` kabul/red/istisna).
- **Policy name normalisation (maintainers 01.10):** `temel = politika.split('|')[0].split('@')[0]` (the suffixes `|sdjwtvc=…`, `@-19` only split the oracle); the original `politika` is written to the output. **P2** (P1 + key–alg binding) is in the GEC/P0/P1 set.

## 2. Policy → API

| Policy | API call |
|---|---|
| GEC / P0 / P1 (single signature) | `JSON::JWT.decode(girdi, JSON::JWK.new(jwk), [:ES256, :ES384])` |
| IZIN-A / IZIN-AX | `… [:ES256]` / `… [:ES256, X]` |
| L4 / L4-S / L4-Y (single signature: compact or General JSON with one signature) | `… [X]` (effective allow-list = R) |
| L4 / L4-S / L4-Y, legacy issuer (payload `iss` = `https://legacy-issuer.example`) | legacy-issuer record of L4c: W = {A, X}, R = ∅, i.e. the allow-list of `IZIN-AX`. The record is selected by the `iss` of the object before the library call (pre-registration §5.13, contract §5.3: "L4c (consecutive)", decision D9) |
| P0 / P1 / L4 / L4-S / L4-Y — **multi-signed General JSON** | **`ifade-edilemedi`**: the library has no option for a multi-signature rule; `decode_json_serialized` verifies only `signatures.first` (`lib/json/jws.rb` L199–216, `evidence/api-scan.txt`). A loop over every signature would be custom code (B4, NOTES §4) |
| VARSAYILAN | `JSON::JWT.decode(girdi, JSON::JWK.new(jwk))` (no algorithm list → `algorithms.blank?` accepts every alg; for a multi-signed object only the first signature) |
| L4-YOL | X5C (SD-JWT) → B6; in a supported format `ifade-edilemedi` (no path-class API) |

`girdi` (input): a string for compact; for General JSON the Hash returned by `JSON.parse` (the library treats a Hash input as JSON serialization, `lib/json/jose.rb` L59–64). For a multi-signed object the key is selected from the header of the first signature (`alg_kid`).

**dogrulanan_algoritmalar:** on acceptance the `alg` of the returned `JSON::JWS` object (for General JSON the first signature; the library verifies only that one).

## 3. B6 decisions (by API review)

| Serialization | Decision | Basis |
|---|---|---|
| compact | supported | `decode_compact_serialized` |
| general | **supported** (only the first signature is verified) | `decode_json_serialized` (`signatures.first`) |
| sd-jwt-compact, sd-jwt-general, sd-jwt-flattened | **B6** | no SD-JWT API (disclosures/`~` are not processed) |
| oid4vci-toplu-yanit, dcapi-json-parametre | **B6** | JSON envelope, not a JWS |
| COSE_Sign, COSE_Sign1 | **B6** | no COSE API |

## 4. Exception → hata_sinifi

| Library exception | hata_sinifi |
|---|---|
| `JSON::JWS::UnexpectedAlgorithm` "Unexpected alg header", alg in the library (ES256/ES384) | `alg-izin-disi` |
| the same, alg not in the library (EdDSA, ML-DSA, composite, unregistered, none) | `alg-desteklenmiyor` |
| `UnexpectedAlgorithm` "Unknown Signature Algorithm" | `alg-desteklenmiyor` |
| `UnexpectedAlgorithm` (caused by a TypeError, key type ≠ alg) | `alg-anahtar-uyusmazligi` |
| `JSON::JWK::UnknownAlgorithm` "Unknown Key Type" (OKP/AKP JWK) | `alg-desteklenmiyor` |
| `JSON::JWK::Set::KidNotFound` | `anahtar-bulunamadi` |
| `JSON::JWS::VerificationFailed` (key present) / (no key could be selected) | `imza-gecersiz` / `anahtar-bulunamadi` |
| `JSON::JWT::InvalidFormat` | `ayristirma` |
| other | `istisna-diger`; 60 s → `zaman-asimi` |

json-jwt does not check `exp`/`iat` (claim validation is left to the application); no clock setting is needed.
