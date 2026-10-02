# SDJWT-001 vck 7.0.1: evidence-rule second attempt

| Field | Value |
|---|---|
| Library | vck, Maven `at.asitplus.wallet:vck:7.0.1` (`vck-jvm-7.0.1.jar` sha256 `c50d76c6...`); resolved closure includes Signum `indispensable-josef` 3.24.0 and `supreme` 0.15.0 (jar hashes equal to the installation record) |
| Repository / commit | https://github.com/a-sit-plus/vck, `a3e66b1a4e80b3053b6921bb4dae3d704dc022bf` (tag 7.0.1) |
| Environment | `pq-a09-env-jvm:1.0` (OpenJDK 25.0.4, Gradle 9.6.1), Kotlin JVM plugin 2.4.10 |
| Date | 2026-10-03 (UTC 2026-10-02 23:18 to 23:24) |
| Time spent | about 7 minutes |
| X | ES384 (Signum `JwsAlgorithm.Signature` has no EdDSA) |
| Form | **L4c** |
| Verdict | **expressible** through two documented function-interface parameters of `VerifyJwsObject` (caller-written per-issuer check, 8 lines; no own verification loop) |
| API hook found | yes: `PublicJsonWebKeyLookup` and `VerifyJwsSignatureFun` |

## Form and basis

An SD-JWT is `SdJwtSigned(jws: JwsCompact, ...)` (`openid-data-classes/.../jws/SdJwtSigned.kt` L16-25): the
issuer-signed part is a compact JWS with one signature. `JwsGeneral` appears only in OpenID request objects,
not in the credential path. Form: L4c.

## API scan (summary; full commands and outputs in `api-scan.txt`)

- No algorithm allow-list, required set or issuer policy option exists in `vck` (the `SupportedAlgorithmsContainer*`
  hits are OpenID metadata data classes that are not used in `vck/src/commonMain`).
- `ValidatorSdJwt(verifySignature, verifyJwsSignature, verifyJwsObject, ...)` (`agent/ValidatorSdJwt.kt` L30-40)
  checks the issuer signature through `SdJwtInputValidator` -> `verifyJwsObject(sdJwtSigned.jws)`
  (`SdJwtInputValidator.kt` L19-23, L70).
- `VerifyJwsObject(verifyJwsSignature, jwkSetRetriever, publicKeyLookup)` (`jws/JwsService.kt` L652-696) accepts if
  any loaded key verifies. Keys come from the header (`jwk`/`x5c`), then `jku`, then the documented callback
  `PublicJsonWebKeyLookup` ("Clients get the parsed [JwsCompact] and need to provide a set of keys", L485-491),
  in that order (L678-683).
- `VerifyJwsSignatureFun` (L502-507) is the documented per-key signature check; the default `VerifyJwsSignature`
  (L513-529) uses the header `alg` without any policy. JWK `alg` members are not checked (the key is converted to
  `CryptoPublicKey`).

## Attempt (`attempt/Main.kt`, output `attempt-run.log`)

Own keys: migrated issuer `https://issuer.example` with ES256 and ES384 keys, legacy issuer
`https://legacy-issuer.example` with its own ES256 key. The verifier always holds the complete key set of each
issuer. All decisions go through the documented `ValidatorSdJwt.verifySdJwt`.

1. Validity check (lookup returns the issuer's key set, no policy): V+ accepted, V- rejected.
2. L4c, policy in `PublicJsonWebKeyLookup`: one `ValidatorSdJwt` instance with the per-issuer records
   `R = {MIG: {ES384}, LEG: {}}`, `W = {ES256, ES384}`; the lookup returns the issuer's keys only if the header
   `alg` is acceptable for the `iss` of the object. Migrated ES256 reject, migrated ES384 accept, legacy ES256
   accept. Limitation shown by the run: an object that carries a key in its own header `jwk` bypasses the lookup
   and is accepted (library behaviour, L678-683).
3. L4c, the same check in a `VerifyJwsSignatureFun` that wraps the library's `VerifyJwsSignature`:
   migrated ES256 reject, migrated ES384 accept, legacy ES256 accept, the header-`jwk` object reject, a corrupted
   ES384 object reject. This hook is applied to every candidate key, whatever its source.

```kotlin
val policySig = VerifyJwsSignatureFun { jws, key ->
    if (acceptable(jws)) VerifyJwsSignature(VerifySignature())(jws, key)
    else KmmResult.failure(IllegalArgumentException("alg not acceptable for issuer"))
}
ValidatorSdJwt(verifyJwsObject = VerifyJwsObject(verifyJwsSignature = policySig,
    publicKeyLookup = PublicJsonWebKeyLookup { jws -> issuerKeys[iss(jws)] }))
```

Summary line of the run: 12 of 12 checked rows as required.

## Verdict

**expressible.** The library has no native algorithm-policy option, but its verification classes take documented
function-interface parameters that receive the parsed JWS (header `alg`, payload `iss`) before or during the key
check. A per-issuer check of 8 caller-written lines (policy records, `acceptable` and the `iss` helper) in either hook gives the
L4c decisions in one validator instance; the signature verification is still done by the library.

Interpretation note for the maintainers: if a caller-written check inside a documented callback does not count as
"the library's own mechanism", this result is "expressible with custom code" (B4, 8 lines). In either reading the
API has a hook, so condition 1 of the evidence rule does not hold.

Line reference for the hooks: a-sit-plus/vck @ `a3e66b1a4e80b3053b6921bb4dae3d704dc022bf`,
`vck/src/commonMain/kotlin/at/asitplus/wallet/lib/jws/JwsService.kt` L485-491 (`PublicJsonWebKeyLookup`),
L502-507 (`VerifyJwsSignatureFun`), L652-696 (`VerifyJwsObject`), and
`vck/src/commonMain/kotlin/at/asitplus/wallet/lib/agent/ValidatorSdJwt.kt` L30-40.
