# SDJWT-025 spruceid ssi (ssi-sd-jwt 0.6.0): evidence-rule second attempt

| Field | Value |
|---|---|
| Library | spruceid ssi, crate `ssi-sd-jwt` 0.6.0 with `ssi-jws` 0.5.0, `ssi-jwt` 0.6.0, `ssi-jwk` 0.4.0, `ssi-claims-core` 0.2.0 |
| Repository / commit | https://github.com/spruceid/ssi, `16cd58715aa209f3151560ad59bd6ac65b90fa89` (`.cargo_vcs_info.json` of the crate); the `src/` trees of all five crates are identical to this commit |
| Environment | `pq-a09-env-rust:1.0` (rustc 1.98.1). Features and lock from the installation record's information run `_bilgi-SDJWT-025-ozellik` (`ssi-jws`/`ssi-jwk` with `secp256r1`, `ed25519`); the lock used differs only in the root package entry. The last line of `attempt-run.log` (23) is that count of differing lock lines |
| Date | 2026-10-03 (UTC 2026-10-02 23:30 to 23:40) |
| Time spent | about 11 minutes |
| X | EdDSA (Ed25519) |
| Form | **L4c** |
| Verdict | **not-expressible** |
| API hook found | no hook that can make an algorithm decision per issuer (the only verification hook, `JWKResolver`, receives only the key id) |

## Form and basis

`SdJwt` holds a compact JWS (`Jws`) plus disclosures (`crates/claims/crates/sd-jwt/src/lib.rs` L110-297); `ssi-jws`
has no JWS JSON serialization type (scan: no `JwsJson`/`General`/`"signatures"`). Single-signature only: L4c.

## API scan (summary; full commands and outputs in `api-scan.txt`)

- Verification entry points: `SdJwt::decode_verify_concealed`, `decode_reveal_verify_any`, `decode_reveal_verify<T, P>`
  with `P: ResolverProvider<Resolver: JWKResolver> + DateTimeProvider` (`sd-jwt/src/lib.rs` L322-368).
- `VerificationParameters` holds a resolver, JSON-LD and EIP-712 loaders and a date-time; no algorithm option
  (`crates/claims/core/src/verification/parameters.rs` L24-38).
- `JWKResolver::fetch_public_jwk(&self, key_id: Option<&str>)` is the only caller-supplied verification hook
  (`crates/jwk/src/resolver.rs` L9-21). It receives the key id only: not the issuer, not the algorithm.
  The run prints each call: the only input is `key_id`.
- `JwsSignature::validate_proof` resolves the key by `kid` and calls `verify_bytes(header.algorithm, ...)`
  (`crates/claims/crates/jws/src/verification.rs` L102-122). `verify_bytes_warnable` rejects when the JWK `alg`
  member differs from the header (`jws/src/lib.rs` L673-687): a per-key binding (L3).
- `ValidateJwsHeader<E>` is a header hook, but for SD-JWT it is fixed by the library: `SdJwtPayload` has an
  empty blanket impl (`sd-jwt/src/lib.rs` L726) and `JWTClaims<T>` returns `Ok(())` for every `T`
  (`crates/claims/crates/jwt/src/claims/mixed/mod.rs` L85-89). A caller-defined claims type `T` reaches only
  `ValidateClaims<P, JwsSignature>`, which receives the claims and the signature bytes, not the header.

## Attempt (`attempt/src/main.rs`, output `attempt-run.log`)

Own keys: migrated issuer P-256 (`mig-es256`) and Ed25519 (`mig-eddsa`), legacy issuer P-256 (`leg-es256`).
One resolver holds the keys of both issuers.

1. Validity check: V+ accepted, V- rejected.
2. Per-key binding (JWK `alg` = the key's own algorithm): the migrated ES256 object is still accepted (required:
   reject). The binding works as L3 (an EdDSA object naming the ES256-bound kid is rejected) but cannot express R.
3. Two paths reach the three L4c decisions only by taking the migrated issuer's ES256 key out of use:
   (a) the resolver withholds `mig-es256` ("unknown key"); (b) the P-256 key is labelled `alg: EdDSA`, an
   inconsistent JWK. In both, the migrated issuer's record no longer holds a usable ES256 key. Contract §5.3
   requires the migrated record to reject the classical object although it holds the classical key, so these
   paths are recorded but not counted.
4. Own code after verification (B4 record only): a per-issuer check of the header `alg` and the `iss` claim after
   a successful library verification gives the three decisions (15 lines).

Summary line of the run: 6 of 7 checked rows as required; the mismatch is the migrated ES256 row of section 2.

## Verdict

**not-expressible.** No hook in the API can apply an algorithm decision per issuer: the resolver sees only the key
id, the header hooks are fixed by the library for SD-JWT payloads, and there is no allow-list. The attempt
with the documented mechanisms failed (section 2); the decisions are reached only by removing the classical key
(section 3, not counted) or by own code (section 4, B4: 15 lines).

Line reference: spruceid/ssi @ `16cd58715aa209f3151560ad59bd6ac65b90fa89`, `crates/jwk/src/resolver.rs` L9-21
(`JWKResolver::fetch_public_jwk` takes only `key_id`), `crates/claims/crates/jws/src/verification.rs` L102-122
(key resolved by `kid`, header `alg` used without policy), `crates/claims/crates/sd-jwt/src/lib.rs` L726
(empty `ValidateJwsHeader` impl for `SdJwtPayload`), `crates/claims/crates/jwt/src/claims/mixed/mod.rs` L85-89.
