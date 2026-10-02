# COSE-001 Signum indispensable-cosef 3.26.0: evidence-rule second attempt

| Field | Value |
|---|---|
| Library | Signum, Maven `at.asitplus.signum:indispensable-cosef:3.26.0` (`indispensable-cosef-jvm-3.26.0.jar` sha256 `ab789399...`, equal to the installation record) |
| Repository / commit | https://github.com/a-sit-plus/signum, `84f24c5b99829874482cb6940a54304b4b590178` (tag 3.26.0) |
| Environment | `pq-a09-env-jvm:1.0` (OpenJDK 25.0.4, Gradle 9.6.1), Kotlin JVM plugin 2.4.10 (the stdlib version of the target's closure) |
| Date | 2026-10-03 (UTC 2026-10-02 23:10 to 23:18) |
| Time spent | about 9 minutes |
| X | ES384 (`CoseAlgorithm.Signature` has no EdDSA) |
| Form | **L4c** |
| Verdict | **not-expressible** |
| API hook found | no |

## Form and basis

`CoseSigned` is documented as "Representation of a signed COSE_Sign1 object" (`CoseSigned.kt` L19-30);
the only signature context string is `"Signature1"` (`CoseBytes.kt` L38, `CoseSigned.kt` L128). The module has
no COSE_Sign type, so it supports only single-signature objects: L4c.

## API scan (summary; full commands and outputs in `api-scan.txt`)

- The public surface of `CoseSigned` is data access, `serialize`, `prepareCoseSignatureInput`, and the companion
  functions `create`, `prepare`, `deserialize` (`CoseSigned.kt` L34-133; confirmed by reflection on the pinned
  jar). There is no verification function in the module: `grep -rni verif` over `indispensable-cosef/src`
  finds only a comment and the key-operation enum value `VERIFY`.
- No allow-list, required set, issuer policy, trust store or callback exists in the module.
- The documented verification path (README L251-262) is a Supreme `Verifier` obtained by the caller with
  `<algorithm>.verifierFor(publicKey)`, applied to bytes the caller prepares. Supreme (0.16.0 at this commit)
  is a separate artefact and is not in the target's resolved dependency closure; its `Verifier.verify(data, sig)`
  checks one signature for an algorithm the caller chose and knows nothing of COSE headers or issuers.

## Attempt (`attempt/Main.kt`, output `attempt-run.log`)

Own keys: migrated issuer ES256 and ES384, legacy issuer ES256; COSE_Sign1 objects built with
`CoseSigned.prepare` / `create` and signed with JCA.

1. Reflection on the pinned jar: no public method of `CoseSigned` or its companion contains "verif".
   `deserialize` of the migrated ES256 object succeeds without any check.
2. A decision can only be reached by caller-assembled verification: `prepareCoseSignatureInput()` plus a JCA
   `Signature` for an algorithm chosen by the caller (6 lines). Validity check: V+ accepted, V- rejected.
3. L4c with own code (B4 record only): a per-issuer policy map plus the caller-assembled verification
   (11 more lines, 17 in total) gives migrated ES256 reject, migrated ES384 accept, legacy ES256 accept.
   These decisions come from own code, not from a library mechanism.

## Verdict

**not-expressible.** The target has no verification API, so there is no place where an algorithm policy,
per issuer or otherwise, can be configured; every decision, including the L4c decisions, is own code (B4: 17 lines).

Line reference: a-sit-plus/signum @ `84f24c5b99829874482cb6940a54304b4b590178`,
`indispensable-cosef/src/commonMain/kotlin/at/asitplus/signum/indispensable/cosef/CoseSigned.kt` L19-48
(COSE_Sign1 type whose only verification-related member is `prepareCoseSignatureInput`) and L88-133
(companion: `deserialize`, `create`, `prepare`; no verify); README L251-262 (verification is done by a
separate `Verifier` for an algorithm chosen by the caller).
