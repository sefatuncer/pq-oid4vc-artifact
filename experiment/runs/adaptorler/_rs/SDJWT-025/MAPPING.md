# SDJWT-025 ssi-sd-jwt 0.6.0 (spruceid/ssi): policy to API mapping

Adapter: `src/main.rs` plus the shared runner `../common/adapter_common.rs`.
Image: `a10-sdjwt-025:1`. Call: `a10-sdjwt-025:1 SDJWT-025 <jobs.jsonl> <out.jsonl> <run>`.

## 1. API used

```
let params = VerificationParameters::from_resolver(jwk).with_date_time(simdi);   // ssi-claims-core parameters.rs L41-55
// sd-jwt-compact
SdJwt::new(presentation)?.decode_reveal_verify_any(&params).await                 // ssi-sd-jwt lib.rs L341-357
// compact (plain JWS): the JWT layer ssi-sd-jwt itself delegates to
JwsStr::new(token)?.to_decoded_jwt()?.verify(&params).await                       // ssi-jwt decoding.rs L36-50
```

Both paths end in the same proof check: `JwsSignature::validate_proof` resolves the key through the resolver and calls `verify_bytes(header.alg, ...)` (ssi-jws verification.rs L107-121). Registered JWT claims (`exp`, `nbf`, `iat`) are validated at `simdi` = 1790003700.

Facts from the sources (ssi-sd-jwt commit `16cd58715aa209f3151560ad59bd6ac65b90fa89`, path `crates/claims/crates/sd-jwt`):

- No algorithm allow-list exists anywhere in the path (`VerificationParameters` holds resolver, JSON-LD loader, EIP-712 loader and date-time only). The header `alg` selects the algorithm.
- The only algorithm restriction is the JWK `alg` member: if present it must equal the header `alg` (ssi-jws lib.rs L680-687, `AlgorithmMismatch`). The published JWKS carries no `alg` for EC/OKP keys, so this binding is inactive with the battery keys.
- Algorithm names are a closed list (ssi-jwk algorithm.rs L120-215): HS*, RS*, PS*, EdDSA, EdBlake2b, ES256, ES384, ES256K, ES256K-R, ESKeccakK(R), ESBlake2b(K), AleoTestnet1Signature. Key types are EC, RSA, oct, OKP (lib.rs L135-141). No ML-DSA, composite or AKP (0 matches).
- `SdJwtPayload.sd_alg` is mandatory (lib.rs L710-713): a plain JWS wrapped as `<jws>~` does not decode ("missing field `_sd_alg`"), although RFC 9901 makes `_sd_alg` optional.
- KB-JWT: payload type `KbJwtPayload` (kb.rs L16) and `SdHash::verify` (kb.rs L112) exist, but there is no entry point that verifies a KB-JWT.
- Feature set: `ssi-jws` and `ssi-jwk` with `default-features = false` plus `secp256r1` and `ed25519` (P-256 via `p256` 0.13.2, Ed25519 via `ed25519-dalek` 2.2.0). ES384 is not compiled in (would need `secp384r1`).

## 2. Key path (`anahtar_yolu`)

`JWK` in every arm: public JWK resolved with the reference rule (`kid`, otherwise `issuer/<alg>` role), deserialised into `ssi_jwk::JWK` and used as the resolver of `VerificationParameters` (the resolver returns that key for any `kid`).

## 3. Policies

`temel = politika.split('|')[0].split('@')[0]`; the original value is written to the output. Same rule as the Python reference for its SD-JWT target (SDJWT-018): only configurations without an algorithm restriction can be expressed.

| Policy | Mapping |
|---|---|
| `GEC`, `P0`, `P1`, `P2` | verified as in section 1 |
| `IZIN-A`, `IZIN-AX` | `ifade-edilemedi`: no allow-list in the API |
| `L4`, `L4-S`, `L4-Y` (with or without suffixes) | `ifade-edilemedi`: no allow-list, no required set |
| `L4-YOL` | `ifade-edilemedi`: no x5c path-class policy |
| any other name | `ifade-edilemedi` |
| any policy with `artefakt` starting with `vp` | `ifade-edilemedi`: no KB-JWT verification entry point |

No custom verification code (B4 = 0). For the L-level protocol: the JWK `alg` member is a documented per-key binding (L3 candidate). It is not used to emulate allow-lists here (see NOTES.md, Decision).

## 4. Serialisations (B6)

| `serilestirme` | Decision |
|---|---|
| `sd-jwt-compact` | supported (ssi-sd-jwt) |
| `compact` | supported through ssi-jwt (`JwsStr` + `ToDecodedJwt`) |
| everything else (SD-JWT JSON, JWS JSON flattened/general, `COSE_Sign1`, `COSE_Sign`) | `uygulanamaz` + `bicim-desteklenmiyor`: ssi-sd-jwt accepts only the `~`-separated compact grammar (lib.rs L98-110) and ssi-jws 0.5 has no JWS JSON serialisation API |

## 5. Error to `hata_sinifi`

| Source | Class |
|---|---|
| `Invalid::Proof(InvalidProof::Signature)` | `imza-gecersiz` |
| `Invalid::Proof(AlgorithmMismatch | KeyMismatch)` | `alg-anahtar-uyusmazligi` |
| `Invalid::Claims(Expired | Premature | MissingIssuanceDate)` | `zaman` |
| `Invalid::Claims(Other)`, `Invalid::Proof(Missing)` | `istisna-diger` |
| `ProofValidationError::InvalidSignature` | `imza-gecersiz` (ssi-jws maps every non-signature failure of `verify_bytes`, such as key/algorithm mismatch or an algorithm not compiled in, to this variant; verification.rs L116-119) |
| `ProofValidationError::InvalidInputData` with "unknown variant" (unknown header `alg`) | `alg-desteklenmiyor` |
| other `InvalidInputData` (decode/reveal errors, unused disclosure, missing `_sd_alg`) | `ayristirma` |
| `UnknownKey`, `MissingPublicKey` | `anahtar-bulunamadi` |
| `InvalidKey`, `InvalidKeyUse` | `alg-anahtar-uyusmazligi` |
| `MissingAlgorithm` | `alg-desteklenmiyor` |
| adapter: JWK not deserialisable ("unknown variant": AKP key type or ML-DSA `alg`) | `alg-desteklenmiyor` (other JWK errors: `ayristirma`) |
| adapter: no key for kid/alg | `anahtar-bulunamadi` |
| runner: panic / 60 s exceeded / vector file unreadable | `cokme` / `zaman-asimi` / `istisna` + `adaptor-hatasi` |

## 6. Output fields

As in the reference adapters (see JOSE-091/MAPPING.md section 6). On acceptance `dogrulanan_algoritmalar` = `[{"sira":0,"alg":<decoded header alg>,"sonuc":"gecerli"}]`; ssi verifies with exactly this value (`verify_bytes(claims.header.algorithm, ...)`).
