# JOSE-091 frank_jwt 3.1.4: policy to API mapping

Adapter: `src/main.rs` plus the shared runner `../common/adapter_common.rs`.
Image: `a10-jose-091:1`. Call: `a10-jose-091:1 JOSE-091 <jobs.jsonl> <out.jsonl> <run>`.

## 1. API used

```
frank_jwt::decode(token: &str, key: &Vec<u8> /* PEM */, algorithm: frank_jwt::Algorithm,
                  &ValidationOptions::dangerous()) -> Result<(header, payload), frank_jwt::Error>
```

Facts from the source (`frank_jwt-3.1.4/src/lib.rs`, commit `556a9046563e8fd131aa6174da8c059acde77190`):

- `Algorithm` has nine variants: HS256/384/512, RS256/384/512, ES256/384/512 (L54-64). No EdDSA, Ed25519, ML-DSA or composite value exists; the scan finds 0 matches for these names in the crate.
- `decode` verifies under the `algorithm` argument only (L167-181, `verify_signature` L333-375). The header `alg` is decoded but never compared with that argument. The library has no allow-list, no registry and no per-key binding: the caller pins one algorithm per call.
- The key is a PEM document (`ToKey` for `Vec<u8>`): `Rsa::public_key_from_pem` for RS*, `PKey::public_key_from_pem(..).ec_key()` for ES* (L345-373).
- `ValidationOptions` only controls the `exp` check against the wall clock (L66-91, L430-446); the signature check in `decode` is unconditional (L174).

## 2. Key path (`anahtar_yolu`)

Same in every arm: the public JWK is resolved with the reference rule (`kid` in `v1`/`v1.3` `acik-jwks.json`, otherwise the `issuer/<alg>` role), converted to a SubjectPublicKeyInfo PEM with the `openssl` crate that frank_jwt itself links (0.10.81), and passed directly (`dogrudan`, PEM). Conversion covers EC P-256/384/521, RSA, OKP Ed25519/Ed448; any other key type (AKP: ML-DSA, composite) gives `red` / `alg-desteklenmiyor` before the call.

## 3. Policies

`temel = politika.split('|')[0].split('@')[0]`; the original `politika` value is written to the output. W comes from `allowed()` exactly as in the reference adapters, with S = {ES256, ES384, ES512, RS256, RS384, RS512} (asymmetric members of `Algorithm`). E = W ∩ S, in the order of W.

| Policy | W | What is passed to `decode` |
|---|---|---|
| `GEC`, `P0`, `P1`, `P2` (and any unknown name) | S | E has several members: the header `alg` if it is in E; otherwise `red`/`alg-desteklenmiyor` without a call |
| `IZIN-A` | {ES256} | `Algorithm::ES256` (pinned) |
| `IZIN-AX` | {ES256, X} | X is never in S, so E = {ES256}: `Algorithm::ES256` (pinned) |
| `L4`, `L4-S`, `L4-Y` (migrated issuer) | {X} | E is empty: `red`/`alg-desteklenmiyor` without a call (no permitted algorithm exists in the library) |
| `L4`, `L4-S`, `L4-Y` (`iss` = legacy issuer) | {ES256, X} | `Algorithm::ES256` (pinned) |
| `L4-YOL` | | `ifade-edilemedi` (no x5c path-class policy) |

Notes:
- With a pinned algorithm frank_jwt ignores the header. A token whose header says `EdDSA` but whose signature is a valid ES256 signature under the resolved key is accepted under `IZIN-A` (smoke test J20). This is the library's behaviour, recorded as such.
- `L4-S` and `L4-Y` differ only for multi-signature objects; frank_jwt reads compact JWS only, so both map like `L4`.
- No custom verification code (B4 = 0). Glue limited to building the `algorithm` argument (selection rule above).

## 4. Serialisations (B6, decided from the API before running)

| `serilestirme` | Decision |
|---|---|
| `compact` | supported |
| everything else (`sd-jwt-compact`, JWS JSON flattened/general, SD-JWT JSON, `COSE_Sign1`, `COSE_Sign`) | `uygulanamaz` + `bicim-desteklenmiyor` (`decode` splits on `.` and requires exactly three segments, L267-280) |

## 5. Error to `hata_sinifi`

| Source | Class |
|---|---|
| `Error::SignatureInvalid` | `imza-gecersiz` |
| `Error::SignatureExpired`, `Error::ExpirationInvalid` | `zaman` (not reachable with `dangerous()`) |
| `Error::JWTInvalid`, `Error::FormatInvalid`, `Error::ProtocolError` | `ayristirma` |
| `Error::OpenSslError` (PEM key of the wrong type for the pinned algorithm) | `alg-anahtar-uyusmazligi` |
| `Error::IssuerInvalid`, `Error::AudienceInvalid`, `Error::IoError` | `istisna-diger` |
| adapter: header not decodable | `ayristirma` |
| adapter: no key for kid/alg | `anahtar-bulunamadi` |
| adapter: no permitted algorithm in `Algorithm`, header alg not in `Algorithm`, key type not convertible | `alg-desteklenmiyor` |
| runner: panic / 60 s exceeded / vector file unreadable | `cokme` / `zaman-asimi` / `istisna` + `adaptor-hatasi` |

`hata_ozeti` holds the first 200 characters of the message.

## 6. Output fields

Same fields as the reference adapters: `hedef_id`, `hedef_surum` (read from Cargo.lock at build time), `adaptor_sha256` (SHA-256 of `src/main.rs` followed by `common/adapter_common.rs`), `kosu`, `vektor_id`, `politika`, `kol`, `sonuc_ham`, `hata_sinifi`, `hata_ozeti`, `dogrulanan_algoritmalar`, `api_yolu`, `sure_ms`. On acceptance `dogrulanan_algoritmalar` = `[{"sira":0,"alg":<algorithm passed to decode>,"sonuc":"gecerli"}]`, i.e. the algorithm frank_jwt actually verified (not the header value).
