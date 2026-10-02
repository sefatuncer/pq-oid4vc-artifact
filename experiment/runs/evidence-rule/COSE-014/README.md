# COSE-014 cose-js 0.9.0: evidence-rule second attempt

| Field | Value |
|---|---|
| Library | cose-js, npm `cose-js` 0.9.0 (integrity `sha512-iYQvus+3...`) |
| Repository / commit | https://github.com/erdtman/cose-js, `421bcaa5dded58890d00243c91b9f7155a613458` (npm gitHead) |
| Environment | `pq-a09-env-node:1.0` (Node v24.21.0), `npm ci --ignore-scripts` with the lock of the installation record |
| Date | 2026-10-03 (UTC 2026-10-02 22:59 to 23:04) |
| Time spent | about 6 minutes |
| X | ES384 (cose-js 0.9.0 has no EdDSA/Ed25519: `lib/sign.js` L16-37) |
| Form | **L4m** (primary); L4c run as a supplement |
| Verdict L4m | **expressible** for R = {X}: one documented `cose.sign.verify` call with the key of the required algorithm |
| Verdict L4c (supplement) | not-expressible: no algorithm, issuer or callback option; line reference below |
| API hook found | for L4m: yes (signer selection by the supplied key's `kid`); for L4c: none |

## Form and basis

- The verification API accepts COSE_Sign (tag 98) with an array of signers and checks the signer whose
  unprotected `kid` equals `verifier.key.kid` (`lib/sign.js` L188-195, L241-269). Multi-signer COSE_Sign
  objects are therefore processed by the documented `verify`/`verifySync`, so the form is L4m.
- The creation API accepts only one signer (`lib/sign.js` L90-96: "Only one signer is supported").
  The two-signer test objects were built by merging the signer arrays of two single-signer COSE_Sign
  messages over the same body (test-object generation only).
- Because creation is single-signer, L4c (COSE_Sign1) was also tested as a supplement.

## API scan (summary; full commands and outputs in `api-scan.txt`)

- Public exports of `cose.sign`: `SignTag`, `Sign1Tag`, `create`, `verify`, `verifySync`.
- `verify(payload, verifier, options)`: `verifier = {key: {x, y, kid}, externalAAD}`; the only option is
  `defaultType` (L208-222). There is no algorithm allow-list, no per-key or per-issuer algorithm binding,
  no callback and no multi-signature rule. The algorithm is read from the header and used as is
  (L260, L273), restricted only by the built-in table (L146-152).
- The README documents `cose.sign.create` and `cose.sign.verify` with a key object only (README L35-70).

## Attempt (`attempt.js`, output `attempt-run.log`)

Own keys: migrated issuer ES256 (`kid` mig-es256) and ES384 (`kid` mig-es384); legacy issuer ES256.

1. Validity check (COSE_Sign1): V+ accepted, V- rejected.
2. L4m, R = {ES384}, W = {ES256, ES384}. Configuration: `cose.sign.verify(msg, {key: {x, y, kid: 'mig-es384'}})`.
   T1 accept, T2 reject ("Signature missmatch"), T3 reject ("Failed to find signer"), T5 accept, all as required.
   T3 with the ES256 signer relabelled `kid = mig-es384` (the kid is unprotected) is also rejected.
   For contrast, the same objects verified with the classical key accept T2 and T3.
3. L4c supplement (COSE_Sign1): a record that holds the migrated issuer's ES256 key accepts the migrated
   ES256 object (required: reject). The library has no option to refuse an algorithm for a key or issuer.
   Supplying only the migrated issuer's ES384 key would reject the ES256 object, but only because the
   P-256 signature does not verify under a P-384 key (no algorithm binding exists); this removes the
   classical key from the record and is not counted (contract §5.3).

Summary line of the run: 11 of 12 checked rows as required; the mismatch is the L4c supplement row.

## Verdict

- **L4m: expressible** for the tested configuration R = {X}. The library verifies exactly the signer that
  the supplied key designates and rejects the object when that signer is missing or invalid; supplying the
  key of the required algorithm therefore yields T1 accept, T2 reject, T3 reject, T5 accept with one
  documented call, no callback code and no own loop. Limits: the other signatures are not checked (this is
  allowed under L4, not under L4-S), and a required set with more than one algorithm would need one call
  per element.
- **L4c (supplement): not-expressible.** Line reference: erdtman/cose-js @
  `421bcaa5dded58890d00243c91b9f7155a613458`, `lib/sign.js` L208-222 (the only inputs are the key object and
  `defaultType`) and L270-283 (COSE_Sign1 path: the header `alg` is used without any policy check).
  If the maintainers assigned L4c to this target, the evidence rule can be satisfied for L4c
  (no hook, failed attempt, line reference); if they assigned L4m, it is not, because L4m is expressible.
