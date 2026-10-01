# SDJWT-010 sd-jwt-payload 0.5.1 (+ josekit 0.8.7): policy to API mapping

Adapter: `src/main.rs` plus the shared runner `../common/adapter_common.rs`.
Image: `a10-sdjwt-010:1`. Call: `a10-sdjwt-010:1 SDJWT-010 <jobs.jsonl> <out.jsonl> <run>`.

## 1. API used

sd-jwt-payload parses SD-JWTs and resolves disclosures; it verifies no signature (no verifier type, no crypto crate in its lock). Following the contract's reading for such libraries, the issuer-signed JWT is verified with the JOSE layer the crate's own example and test use:

```
let sd_jwt = sd_jwt_payload::SdJwt::parse(presentation)?;                       // sd_jwt.rs L135
let jwt = sd_jwt.presentation().split_once('~').0;                              // as in tests/api_test.rs L148-155
let verifier = josekit::jws::<ALG>.verifier_from_jwk(&josekit::jwk::Jwk::from_map(jwk))?;
josekit::jwt::decode_with_verifier(jwt, &verifier)?;                            // josekit jwt.rs L87-92
sd_jwt.into_disclosed_object(&Sha256Hasher::new())?;                            // README "Verifying"; sd_jwt.rs L174
```

Facts from the sources:

- sd-jwt-payload `c47e52c31545f7ede55ad1259f275f31595e2322`: `dev-dependencies.josekit = { version = "0.8.4", features = ["vendored"] }` (Cargo.toml L111-113), resolved to 0.8.7 in the published `Cargo.lock` (L288-289). `examples/sd_jwt.rs` and `tests/api_test.rs` use josekit; the test `sd_jwt_is_verifiable` verifies the issuer JWT with `josekit::jwt::decode_with_verifier`.
- `_sd_alg` is optional (`SdJwtClaims._sd_alg: Option<String>`, sd_jwt.rs L34). `into_disclosed_object` replaces digests and fails on unused disclosures (decoder.rs L33).
- KB-JWT: only parsed (`typ` must be `kb+jwt`, `alg` not `none`; key_binding_jwt_claims.rs L32-47); never verified.
- josekit 0.8.7: a verifier is built for one algorithm; `deserialize_compact_with_selector` requires header `alg` == verifier algorithm (jws_context.rs L428-437) and, if the JWK has a `kid`, header `kid` == that `kid` (L439-446). Algorithms: HS*, RS*, PS*, ES256/384/512, ES256K, EdDSA (jws.rs L21-42). No ML-DSA (0 matches).

## 2. Key path (`anahtar_yolu`)

`JWK` in every arm: public JWK resolved with the reference rule (`kid`, otherwise `issuer/<alg>` role), passed unchanged to `josekit::jwk::Jwk::from_map` and `<ALG>.verifier_from_jwk`.

## 3. Policies

`temel = politika.split('|')[0].split('@')[0]`; the original value is written to the output. W from `allowed()` with S = {ES256, ES384, ES512, ES256K, RS256, RS384, RS512, PS256, PS384, PS512, EdDSA}; E = W ∩ S.

| Policy | W | Verifier built for |
|---|---|---|
| `GEC`, `P0`, `P1`, `P2` (and any unknown name) | S | header `alg` if in E, else `red`/`alg-desteklenmiyor` without a call |
| `IZIN-A` | {ES256} | ES256 (pinned; josekit refuses any other header `alg`) |
| `IZIN-AX` | {ES256, X} | control arm: E = {ES256, EdDSA}, header `alg` if in E; treatment arms: ES256 (pinned) |
| `L4`, `L4-S`, `L4-Y` (migrated issuer) | {X} | control arm: EdDSA (pinned); treatment arms: E empty, `red`/`alg-desteklenmiyor` |
| `L4`, `L4-S`, `L4-Y` (`iss` = legacy issuer) | {ES256, X} | as `IZIN-AX` |
| `L4-YOL` | | `ifade-edilemedi` (no x5c path-class policy) |
| any policy with `artefakt` starting with `vp` | | `ifade-edilemedi` (KB-JWT cannot be verified through the library) |

`iss` is read from the issuer-signed JWT. `L4-S`/`L4-Y` differ only for multi-signature objects, which the library cannot parse. No custom verification code (B4 = 0): the glue builds the verifier (selection rule above) and calls the two libraries in the documented order.

## 4. Serialisations (B6)

| `serilestirme` | Decision |
|---|---|
| `sd-jwt-compact` | supported |
| `compact` | supported as an SD-JWT without disclosures (`<jws>~`); signature and payload unchanged (same as `compact-as-sdjwt` in the Python reference) |
| everything else (SD-JWT JSON, JWS JSON flattened/general, `COSE_Sign1`, `COSE_Sign`) | `uygulanamaz` + `bicim-desteklenmiyor`: `SdJwt::parse` only reads the `~`-separated compact form (sd_jwt.rs L135-162). josekit could read JWS JSON, but that would measure the JOSE layer alone. |

## 5. Error to `hata_sinifi`

| Source | Class |
|---|---|
| `JoseError::InvalidSignature` | `imza-gecersiz` |
| `JoseError::UnsupportedSignatureAlgorithm` | `alg-desteklenmiyor` |
| `JoseError::InvalidJwkFormat`, `InvalidKeyFormat` (key not usable for the chosen verifier) | `alg-anahtar-uyusmazligi` |
| `JoseError::InvalidJwsFormat`/`InvalidJwtFormat` with "alg header claim is not" | `alg-izin-disi` |
| same with "kid header claim" (missing or different `kid`) | `anahtar-bulunamadi` |
| same with "critical name" | `crit` |
| other `InvalidJwsFormat`/`InvalidJwtFormat`, `InvalidJson` | `ayristirma` |
| other `JoseError` | fallback `klass()` |
| `sd_jwt_payload::Error::DeserializationError` | `ayristirma` |
| other `sd_jwt_payload::Error` (unused disclosure, hasher, digest collision, ...) | `istisna-diger` |
| adapter: no permitted algorithm / header alg without josekit verifier | `alg-desteklenmiyor` |
| adapter: no key for kid/alg | `anahtar-bulunamadi` |
| runner: panic / 60 s exceeded / vector file unreadable | `cokme` / `zaman-asimi` / `istisna` + `adaptor-hatasi` |

## 6. Output fields

As in the reference adapters (see JOSE-091/MAPPING.md section 6); `hedef_surum` is the sd-jwt-payload version. On acceptance `dogrulanan_algoritmalar` = `[{"sira":0,"alg":verifier.algorithm().name(),"sonuc":"gecerli"}]`.
