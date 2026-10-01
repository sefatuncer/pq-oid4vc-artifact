# JOSE-092 jsonwebtoken 11.1.0: policy to API mapping

Adapter: `src/main.rs` plus the shared runner `../common/adapter_common.rs`.
Image: `a10-jose-092:1`. Call: `a10-jose-092:1 JOSE-092 <jobs.jsonl> <out.jsonl> <run>`.

## 1. API used

```
let key = DecodingKey::from_jwk(&jwk)?;                 // jsonwebtoken::jwk::Jwk from the published JWK
let mut v = Validation::new_for_family(key.family());
v.algorithms = W restricted to key.family();            // per-call allow-list
v.validate_exp = false; v.validate_nbf = false; v.validate_aud = false; v.required_spec_claims.clear();
jsonwebtoken::decode::<serde_json::Value>(token, &key, &v)
```

Crypto backend: feature `aws_lc_rs` (primary backend of the environment record), default feature `use_pem` kept.

Facts from the source (`jsonwebtoken-11.1.0`, commit `4c0ae752e9acc108c8e2c4c8ed8128dc66014210`):

- `Validation::algorithms` is the allow-list; `decode` rejects a header `alg` not in it (`decoding.rs` L278-279, again L356-358).
- Every entry of `algorithms` must belong to the family of the verifying algorithm, otherwise the call fails with `InvalidAlgorithm` (`decoding.rs` L346-353). A mixed list such as {ES256, EdDSA} therefore rejects every token. `Validation::new_for_family` (`validation.rs` L115) builds the per-family list the library expects.
- The header `alg` is deserialised into the closed `Algorithm` enum (`header.rs` L160; `FromStr` in `algorithms.rs` L75): HS256/384/512, ES256/384, RS256/384/512, PS256/384/512, EdDSA. Any other name (Ed25519, ML-DSA-65, ML-DSA-65-ES256) fails while the header is parsed.
- `DecodingKey::from_jwk` returns `UnsupportedAlgorithm` for key types it does not know, e.g. AKP (`decoding.rs` L213-229).
- `CryptoProvider` (`crypto/mod.rs` L83, `install_default` L96) lets an application replace the crypto backend for the existing `Algorithm` values only; it cannot introduce a new algorithm name.

## 2. Key path (`anahtar_yolu`)

`JWK` in every arm: public JWK resolved with the reference rule (`kid`, otherwise `issuer/<alg>` role), deserialised into `jsonwebtoken::jwk::Jwk`, then `DecodingKey::from_jwk`.

## 3. Policies

`temel = politika.split('|')[0].split('@')[0]`; the original value is written to the output. W comes from `allowed()` as in the reference adapters, with S = {ES256, ES384, RS256, RS384, RS512, PS256, PS384, PS512, EdDSA}. Names that do not parse into `Algorithm` drop out. The list given to the library is W ∩ family(key).

| Policy | W | `Validation::algorithms` (EC key / Ed25519 key) |
|---|---|---|
| `GEC`, `P0`, `P1`, `P2` (and any unknown name) | S | [ES256, ES384] / [EdDSA] (= `new_for_family`) |
| `IZIN-A` | {ES256} | [ES256] / [] |
| `IZIN-AX` | {ES256, X} | control arm (X = EdDSA): [ES256] / [EdDSA]; treatment arms: [ES256] / [] |
| `L4`, `L4-S`, `L4-Y` (migrated issuer) | {X} | control arm: [] / [EdDSA]; treatment arms: [] / [] |
| `L4`, `L4-S`, `L4-Y` (`iss` = legacy issuer) | {ES256, X} | as `IZIN-AX` |
| `L4-YOL` | | `ifade-edilemedi` (no x5c path-class policy) |

An empty list makes the library reject the token with `InvalidAlgorithm` (`alg-izin-disi`).
`L4-S` and `L4-Y` differ only for multi-signature objects; jsonwebtoken reads compact JWS only.
No custom verification code (B4 = 0); glue limited to building `Validation::algorithms`.

## 4. Serialisations (B6)

| `serilestirme` | Decision |
|---|---|
| `compact` | supported |
| everything else (`sd-jwt-compact`, JWS JSON flattened/general, SD-JWT JSON, `COSE_Sign1`, `COSE_Sign`) | `uygulanamaz` + `bicim-desteklenmiyor` (`decode`/`decode_header` split a compact token into exactly three parts, `decoding.rs` L332-337; no JSON serialisation API) |

## 5. Error to `hata_sinifi`

| `ErrorKind` | Class |
|---|---|
| `InvalidSignature` | `imza-gecersiz` |
| `InvalidAlgorithm`, `MissingAlgorithm` | `alg-izin-disi` |
| `InvalidAlgorithmName`, `UnsupportedAlgorithm`, `Json` with "unknown variant" (unknown header `alg`) | `alg-desteklenmiyor` |
| `InvalidEcdsaKey`, `InvalidEddsaKey`, `InvalidRsaKey`, `InvalidKeyFormat` | `alg-anahtar-uyusmazligi` |
| `InvalidToken`, `Base64`, `Utf8`, other `Json` | `ayristirma` |
| `ExpiredSignature`, `ImmatureSignature` | `zaman` (not reachable: claim checks off) |
| anything else | `istisna-diger` |
| adapter: header not decodable / JWK not deserialisable | `ayristirma` |
| adapter: no key for kid/alg | `anahtar-bulunamadi` |
| runner: panic / 60 s exceeded / vector file unreadable | `cokme` / `zaman-asimi` / `istisna` + `adaptor-hatasi` |

## 6. Output fields

As in the reference adapters (see JOSE-091/MAPPING.md section 6). On acceptance `dogrulanan_algoritmalar` = `[{"sira":0,"alg":TokenData.header.alg,"sonuc":"gecerli"}]`; this is the algorithm the library used to build the verifier.
