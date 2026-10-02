# Evidence rule: second independent attempts

## Purpose

Pre-registration Section 5.14 gives the verdict "not expressible" only if (1) the API scan finds no hook,
(2) two independent attempts failed and (3) a source line reference exists; otherwise the result is
"indeterminate". This folder holds the **second** attempt for the seven targets whose L4 configuration
(L4m or L4c, the one that determines Y_i) was recorded as not expressible by the first attempt.

The second attempt was made on 2026-10-03 in a separate session without access to the first attempt: no
adapter, output, analysis, note or decision of the first attempt was opened. Inputs were the target list with
pinned versions, the excerpt of pre-registration Sections 5.13-5.14, the adapter contract
(`experiment/oracle/oracle-A/adapter-contract.md`, §2.2, §5, §5.5) and the installation records
(`experiment/environments/hedefler/<target>/`, `experiment/environments/derleme-sonuc.csv`).

## Method

Per target, time-boxed to 45 minutes (no target needed more than 11 minutes):

1. **Pinned source.** The package was installed in a container of the target's language image
   (`pq-a09-env-*:1.0`) with the lock data of the installation record (pip `--require-hashes`, `npm ci`, go.sum,
   frozen Gemfile.lock, Gradle with jar hashes checked against the record, Cargo.lock of the record). The source
   archive of the pinned commit was fetched anonymously from `codeload.github.com` and compared with the
   installed sources; line references use the commit archive.
2. **API scan.** Documented options, type definitions and public exports were scanned with `grep -rnE`
   (`rg` is not installed on the host) for allow-lists, per-key or per-issuer algorithm binding, required-set or
   multi-signature rules and callbacks. Commands and outputs: `<target>/api-scan.txt`.
3. **Attempt.** A small program against the documented API, run on objects made with own keys (never the
   study's battery vectors): validity check (V+ accept, V- reject), then the L4 configuration, then any
   alternative path found in the scan. Source and run log: `<target>/`.
4. **Verdict:** `expressible`, `not-expressible` or `undetermined` (time box reached).

Rules applied in every target:

- **X** is the first label in the order EdDSA, Ed25519, ES384 that the pinned library supports.
- **Form**: L4m if the documented verification API processes objects with several signatures, otherwise L4c.
  Where the other form is meaningful it was run as a supplement and reported separately.
- **Key material**: the verifier holds the complete key set of each issuer (migrated issuer: classical and X key;
  legacy issuer `https://legacy-issuer.example`: its own ES256 key). Contract §5.3 asks that the migrated
  record reject the classical object although it holds the classical key. Paths that reach the decisions only
  by withholding, dropping or relabelling the migrated issuer's classical key are recorded but not counted.
- **Same verifier instance (L4c)**: one verifier configuration must serve both issuers. Choosing a different
  configuration per object in caller code is "L4c (consecutive)" in contract §5.3, a candidate deviation; it is
  recorded separately.
- **Hook**: a documented extension point that the library consults during verification and that receives what
  the policy needs (issuer and algorithm). A per-issuer check written inside such a callback counts as reaching
  the policy through the API (no own verification loop); its line count is recorded. Code that assembles the
  verification itself, or loops over signatures, or checks after verification, is own code (B4) and does not
  count.

No image was built. Containers were started with `docker run --rm`, names prefixed `ev-`, `--memory=4g`, one at
a time; attempt runs used `--network none` where no download was needed.

## Results

| Target | Library (pinned) | Form | Second attempt | Hook | Rule 5.14 satisfied |
|---|---|---|---|---|---|
| SDJWT-018 | sd-jwt-python 0.10.4 | L4c | **expressible** via the documented key callback `cb_get_issuer_key(issuer, header)` (8 caller lines); L4m supplement also reached | yes | no |
| COSE-014 | cose-js 0.9.0 | L4m | **expressible** for R = {X}: `cose.sign.verify(msg, {key: X key})` checks exactly the designated signer; L4c supplement not expressible | yes (L4m) | no |
| COSE-034 | go-cose v1.3.0 | L4m | **not-expressible**: `SignMessage.Verify` needs one alg-bound verifier per signature, in order (B4: 25 lines); L4c supplement only by leaving out the classical key | no | yes |
| COSE-001 | Signum indispensable-cosef 3.26.0 | L4c | **not-expressible**: COSE_Sign1 data types without any verification API (B4: 17 lines) | no | yes |
| SDJWT-001 | vck 7.0.1 | L4c | **expressible** via the documented `PublicJsonWebKeyLookup` / `VerifyJwsSignatureFun` parameters of `VerifyJwsObject` (8 caller lines) | yes | no |
| JOSE-089 | json-jwt 1.17.2 | L4c | **not-expressible** in one configuration; only a per-call allow-list, so "L4c (consecutive)" is reachable | no (per-call allow-list only) | yes, unless "L4c (consecutive)" counts |
| SDJWT-025 | spruceid ssi-sd-jwt 0.6.0 | L4c | **not-expressible**: the only hook (`JWKResolver`) sees only the key id; header hooks fixed for SD-JWT (B4: 15 lines) | no | yes |

Machine-readable summary: `experiment/runs/analysis/evidence-rule.csv`.

## Points for the maintainers

- **SDJWT-018 and SDJWT-001** contradict the first attempt: both libraries pass the parsed header and the issuer
  to a documented callback during verification, and a short per-issuer check there yields the three L4c
  decisions with the library doing all signature verification. If the maintainers read "the library's own
  mechanism" so that caller code inside a callback does not count, these become "expressible with custom code"
  (B4, 8 lines each); either way condition 1 of Section 5.14 ("no hook in the API") does not hold.
- **COSE-014** depends on the form: as L4m it is expressible (designated-signer verification); as L4c it is not.
  The form was decided here as L4m because the documented `verify` processes COSE_Sign with several signers,
  although `create` accepts only one signer.
- **JOSE-089** depends on whether "L4c (consecutive)" (contract §5.3) is accepted as L4c.
- **COSE-034, COSE-001, SDJWT-025** satisfy the rule with this second attempt (no hook, failed attempt, line
  reference), as does JOSE-089 under the strict reading.
