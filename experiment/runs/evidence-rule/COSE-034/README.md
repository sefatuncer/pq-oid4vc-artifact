# COSE-034 go-cose v1.3.0: evidence-rule second attempt

| Field | Value |
|---|---|
| Library | go-cose, module `github.com/veraison/go-cose` v1.3.0 (go.sum `h1:2/H5w8kd...`) |
| Repository / commit | https://github.com/veraison/go-cose, `e5c68f97dfbb7dc2677e891ceea9a8eafe42ddb4` (tag v1.3.0) |
| Environment | `pq-a09-env-go:1.0` (go1.27.1), go.mod/go.sum of the installation record; the downloaded module is identical to the commit archive |
| Date | 2026-10-03 (UTC 2026-10-02 23:04 to 23:09) |
| Time spent | about 6 minutes |
| X | EdDSA |
| Form | **L4m** (primary); L4c run as a supplement |
| Verdict L4m | **not-expressible** without own code (B4 record: 25 lines) |
| Verdict L4c (supplement) | reachable only if the migrated issuer's ES256 key is left out of its record; see below |
| API hook found (L4m) | no |

## Form and basis

`SignMessage` (COSE_Sign) with several `Signature`s is a public type with `Sign` and `Verify`
(`sign.go` L283-475). The API is marked "EXPERIMENTAL" in its doc comments but is exported and documented.
The target supports multi-signature objects, so the form is L4m.

## API scan (summary; full commands and outputs in `api-scan.txt`)

- `NewVerifier(alg, key)` binds one algorithm to one public key (`verifier.go` L36-92). Every verify call
  checks the protected `alg` header against `verifier.Algorithm()` and returns `ErrAlgorithmMismatch`
  otherwise (`headers.go` L428-442). This is a per-key binding (an L3 mechanism).
- `SignMessage.Verify(external, verifiers ...Verifier)` requires exactly one verifier per signature, in the
  order of the signatures, and requires every signature to verify (`sign.go` L445-475; count check L452-459,
  loop L468-474). Its doc comment says: "See `Signature.Verify()` for advanced verification scenarios like
  threshold policies" (L433-437).
- `Signature.Verify(verifier, protected, payload, external)` verifies a single signature (L180-207).
- There is no option, callback or type that expresses a required algorithm set, an allow-list or an issuer.
  The `Verifier` interface (`verifier.go` L12-23) is an extension point for algorithms, not for policy;
  the count and order checks run before any verifier is called.
- The README (L206-208) mentions `cose.RegisterAlgorithm`; it does not exist in the v1.3.0 sources
  (`grep -rn RegisterAlgorithm` has no match). It would register algorithms, not express a policy.

## Attempt (`main.go`, output `attempt-run.log`)

Own keys: migrated issuer ES256 and Ed25519; legacy issuer ES256.

1. Validity check: V+ accepted, V- rejected (COSE_Sign and COSE_Sign1).
2. L4m, R = {EdDSA}, W = {ES256, EdDSA}, three static verifier lists:
   - `[vES256, vX]`: T1 accept, T2 reject, T3 reject, **T5 reject** ("2 verifiers for 1 signatures"),
     T1 permuted reject.
   - `[vX]`: **T1 reject** ("1 verifiers for 2 signatures"), T2 reject, T3 reject, T5 accept.
   - `[vX, vES256]`: T1 reject, T5 reject; only the permuted T1 is accepted.

   No static configuration gives T1 accept, T2 reject, T3 reject and T5 accept, because the verifier list
   must match the number and order of the signatures of each object.
3. Own code (recorded as B4 only): a loop over `m.Signatures` that calls `Signature.Verify` for each
   signature whose algorithm is in R and then checks that every element of R was seen (25 lines).
   It gives T1 accept, T2 reject, T3 reject, T5 accept, permuted T1 accept.
4. L4c supplement (COSE_Sign1). `Sign1Message.Verify(external, verifier)` takes one alg-bound verifier.
   With the migrated record `{Verifier(EdDSA, migrated key)}` and the legacy record
   `{Verifier(ES256, legacy key)}`, the three L4c decisions are as required; the migrated ES256 object is
   rejected by the library's `ErrAlgorithmMismatch`. If the migrated record also holds its ES256 key
   (`Verifier(ES256, migrated ES256 key)`), the migrated ES256 object is accepted. The per-issuer
   restriction therefore exists only as "do not configure the classical key of a migrated issuer"; the
   library has no way to attach R to an issuer record that holds that key (contract §5.3 asks that the
   migrated record reject the classical object although it holds the classical key).

Summary line of the run: 17 of 23 checked rows as required; all 6 mismatches are L4m rows of the static
configurations, by design of the test.

## Verdict

**L4m: not-expressible** through the documented API without own code. No hook found in the scan, the
attempt with every static configuration failed, and the line reference shows why:
veraison/go-cose @ `e5c68f97dfbb7dc2677e891ceea9a8eafe42ddb4`, `sign.go` L433-475 (`SignMessage.Verify`:
one verifier per signature, positional, all must verify; required-set policies are left to own code with
`Signature.Verify`). Expressible with custom code: 25 lines (B4).

L4c supplement: if the maintainers count "a migrated issuer's record contains only verifiers for
algorithms in R" as a per-issuer policy, L4c is reachable through the alg-bound verifier
(`verifier.go` L36-92, `headers.go` L428-442, `sign1.go` L126-154); under the contract §5.3 reading it is
not. This matters only if the target's form were L4c.
