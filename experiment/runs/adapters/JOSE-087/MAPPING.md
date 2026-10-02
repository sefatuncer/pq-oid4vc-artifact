# JOSE-087 ruby-jwt — policy → API mapping (contract 1.0 §2.2, RUNNER §2)

- **Target:** `jwt` gem 3.3.0 (tag v3.3.0 → `ccf24892fec8`), `Gemfile.lock` CHECKSUMS `sha256=44cc34fb…` (the same file as the environment record, `experiment/environments/targets/JOSE-087/output/`).
- **Image:** `a10-jose-087:1` (`FROM pq-a09-env-ruby:1.0`; Ruby 3.4.11, ruby-openssl → OpenSSL 3.5.7). `bundle install` only when the image is built (rubygems.org, anonymous); runs with `--network none`.
- **Call:** `docker run --rm --network none -v <v1.3>:/v:ro -v <anahtarlar>:/anahtarlar:ro -v <isler>:/is:ro -v <cikti>:/c a10-jose-087:1 adaptor /is/<isler> /c/JOSE-087.<kosu>.jsonl`
- **Source:** `adaptor.rb` (library-specific), `ortak.rb` (same skeleton as JOSE-089). `adaptor_sha256` = `sha256(sha256sum adaptor.rb ortak.rb)` is computed when the image is built.

## 1. Shared rules (the same for all my targets)

| Topic | Rule |
|---|---|
| Policy name normalisation (maintainers 01.10) | `temel = politika.split('|')[0].split('@')[0]`; the suffixes `|sdjwtvc=-13/-19` and `@-19` only split the oracle expectation and do not change the library configuration. The original value of the job row is written to the `politika` field of the output |
| P2 | P1 + key–alg binding = library default → the same set as GEC/P0/P1 (W = native support, R = ∅) |
| A, X | A = ES256; X from the arm: kontrol-EdDSA → EdDSA, kontrol-Ed25519 → Ed25519, tedavi-ML-DSA-65 → ML-DSA-65, tedavi-composite → ML-DSA-65-ES256 (RUNNER §1) |
| GEC, GEC@-19, P0, P1 | W = the subset of the battery's algorithms that the library supports **natively** (METHOD §2 "all supported algorithms"), R = ∅ |
| IZIN-A / IZIN-AX | W = {A} / {A, X}, R = ∅ |
| L4, L4-S, L4-Y, L4@-19, L4-YOL | W = {A, X}, R = {X} |
| Single-signature object (compact; General JSON with one signature) | The multi-signature rule stays empty. If R ≠ ∅, the effective allow-list is R: a single signature satisfies R only if it is X itself, and R ⊆ W. Thus L4/L4-S/L4-Y on a compact object are built with the library's **allow-list** mechanism (L4c "migrated issuer" record; contract §5.2). P0/P1 equal GEC for a single signature |
| Multi-signature object | If the library has no documented multi-signature rule (at-least-one / all / required set), `ifade-edilemedi`; no custom loop is written (B4) |
| Key path (contract §8 item 1) | **`JWK` in all arms:** the header `kid` is looked up in the vector's JWKS (`dogrulama_girdileri.jwks`); without `kid`, `alg_kid[alg]` of the manifest, and without that the single `kid`. The selected JWK is turned into a key with the library's documented JWK import API. For DPoP the header `jwk` (`jwk-basligi`). x5c is not used in non-X5C vectors (§8 item 2) |
| Clock | The library uses the real clock (no fake-clock API). In the V/T/CMP/K10 vectors `exp` = 1821536000 > real clock; not affected |
| VARSAYILAN (additional, not in jobs-v1.3.jsonl) | For contract §5.2 L5 / §5.4 B5: only the key is given, no allow-list. Supported so that it can be run after the freeze |
| sonuc_ham | `kabul`: the library raised no error. `red`: the library's verification error class (under `JWT::Error`). `istisna`: another exception. Adapter error → `adaptor-hatasi` |
| dogrulanan_algoritmalar | On acceptance the `alg` value of the header returned by `JWT.decode` (the library uses only the verifier matching `valid_alg?(alg)`; `jwa.rb` create_verifiers); on rejection `[]` |

## 2. Policy → API

| Policy | API call |
|---|---|
| GEC / P0 / P1 (single signature) | `JWT.decode(token, nil, true, algorithms: ["ES256","ES384"]) { \|hdr\| JWT::JWK.import(jwk).verify_key }` |
| IZIN-A | `… algorithms: ["ES256"] …` |
| IZIN-AX | `… algorithms: ["ES256", X] …` (X = EdDSA/Ed25519/ML-DSA-65/ML-DSA-65-ES256 resolves to `JWA::Unsupported` in the library) |
| L4 / L4-S / L4-Y (compact) | `… algorithms: [X] …` (effective allow-list = R) |
| L4-YOL | the X5C vectors are in SD-JWT form → B6 first; if it comes in a supported format, `ifade-edilemedi` (no API for an x5c path-class policy; the same rule for all my targets) |
| VARSAYILAN | `JWT.decode(token, nil, true) { … }` (no algorithm given; the library rejects with "An algorithm must be specified") |

**Why `verify_key`:** the README section "JSON Web Key (JWK)" documents `jwk.verify_key`. In 3.3.0, when `JWT.decode` and a JWK object are given together, `validate_jwk_algorithms!` compares the JWA of the JWK with JWA **objects** and rejects even a valid ES256 signature with `VerificationKeyError` (first synthetic smoke run; NOTES §4 item 2). The `verify_key` path keeps the curve–alg check of the ECDSA verifier (`jwa/ecdsa.rb` `IncorrectAlgorithm`).

## 3. B6 decisions (by API review, without running vectors)

| Serialization | Decision | Basis |
|---|---|---|
| compact | supported | `JWT.decode`, `EncodedToken` (3 parts) |
| general, sd-jwt-flattened | **B6** | no JSON serialization parser (`decode.rb` `validate_segment_count!`: only 3 dot-separated parts); 8725bis §3.14 |
| sd-jwt-compact, sd-jwt-general | **B6** | no SD-JWT (`~`-separated, disclosure) API |
| oid4vci-toplu-yanit, dcapi-json-parametre | **B6** | JSON envelope; not an input of a JWT library |
| COSE_Sign, COSE_Sign1 | **B6** | no COSE API |

## 4. Exception → hata_sinifi

| Library exception (message) | hata_sinifi |
|---|---|
| `JWT::UnsupportedKeyType` (OKP/AKP JWK) | `alg-desteklenmiyor` |
| `JWT::IncorrectAlgorithm` "payload algorithm is … verification key was provided" | `alg-anahtar-uyusmazligi` |
| `JWT::IncorrectAlgorithm` "Expected a different algorithm", header alg in the library's list | `alg-izin-disi` |
| the same, header alg not in the library (EdDSA, ML-DSA-*, composite, none, unregistered) | `alg-desteklenmiyor` |
| `JWT::VerificationKeyError` "Algorithm not supported" / "do not support one of the specified" | `alg-desteklenmiyor` / `alg-anahtar-uyusmazligi` |
| `JWT::VerificationError` "Signature verification failed" | `imza-gecersiz` |
| `JWT::SignatureError` "No verification key available", "Could not find public key" | `anahtar-bulunamadi` |
| `JWT::ExpiredSignature`, `ImmatureSignature`, `InvalidIatError` | `zaman` |
| `JWT::InvalidCritError` | `crit` |
| `JWT::MalformedTokenError` (and `Base64DecodeError`) | `ayristirma` |
| other `JWT::Error` / other exception | `istisna-diger` |
| 60 s exceeded (`Timeout`) | `zaman-asimi` |
