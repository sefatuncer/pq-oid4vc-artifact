# COSE-035 web-auth/cose-lib 4.8.2: evidence-rule second attempt

| Field | Value |
|---|---|
| Library | web-auth/cose-lib 4.8.2 with spomky-labs/cbor-php 3.4.2 (Packagist; composer.lock of the installation record, sha256 `77b7428a...`) |
| Repository / commit | https://github.com/web-auth/cose-lib, `8849e8bf043a2d42d0bec5bda5db2469ad376148` (tag 4.8.2); cbor-php https://github.com/Spomky-Labs/cbor-php, `8f5ea00a07ad529d20886505cdbeb2b9ac7bb2d6` (3.4.2). Both installed packages are identical to the commit archives |
| Environment | `pq-a09-env-php:1.0` (PHP 8.4.26, OpenSSL 3.5.8, sodium loaded), `composer install` frozen to the record's composer.lock |
| Date | 2026-10-03 (UTC 09:34 to 09:42) |
| Time spent | about 7 minutes |
| X | EdDSA (-8) |
| Form | **L4m** (primary); L4c run as a supplement |
| Verdict L4m | **not-expressible** without own code (B4 record: 23 lines) |
| Verdict L4c (supplement) | **not-expressible** in one configuration; reachable only by relabelling or withholding the migrated issuer's ES256 key, or with own code that selects a Manager per issuer (B4: 14 lines) |
| API hook found | no |

## Form and basis

The library has no message-level verification function. Its documented verification path, for COSE_Sign1 and for
COSE_Sign, is caller code around the primitive `Signature::verify(string $data, Key $key, string $signature)`
(`src/Algorithm/Signature/Signature.php` L11-34): decode the message with cbor-php, read the headers, build the
Sig_structure and call `verify` (README L71-137; `doc/Usage.md` L233-295).

COSE_Sign with several signers is supported and documented: `CoseSignature::all()` gives the checked signer list
(`src/Signature/CoseSignature.php` L71-89), `Signature` is the per-signer Sig_structure (`src/Signature/Signature.php`
L11-79), and `doc/Usage.md` L324-386 and `examples/02-sign-multiple-signers.php` L77-100 verify every signer in a
caller loop. The target therefore supports multi-signature objects (pre-registration Section 5.13: Y_i = L4m), and
the form is L4m. `doc/` and `examples/` are export-ignored and absent from the archive; they were read from an
anonymous `git fetch` of the same commit (`src/` identical to the archive).

## API scan (summary; full commands and outputs in `api-scan.txt`)

- The only public `verify` functions are the algorithm primitives (data, key, signature) and
  `CertificateSignatureVerifier::verify/verifySubjectPublicKeyInfo` (algorithm identifier, X.509 certificate or SPKI,
  data, signature). None of them sees a COSE message, a header, a signer list or an issuer. cbor-php's
  `CoseSign1Tag`/`CoseSignTag` carry the structure only: "verifying a signature ... belongs to a COSE implementation
  such as web-auth/cose-lib" (cbor-php `src/Tag/AbstractCoseTag.php` L24-31).
- `Manager` is one set of algorithm identifiers; `get()` throws "Unsupported algorithm" for an identifier that was not
  registered (`src/Algorithm/Manager.php` L97-109). It is a global allow-list (L1/L2 mechanism) with no issuer and no
  notion of a required algorithm.
- Key restrictions (opt-in, `withKeyRestrictionsEnforced()`): a key's `alg` (label 3) and `key_ops` (label 4) are
  checked against the algorithm that uses it (`src/Algorithm/KeyRestrictionAware.php` L9-29,
  `src/Algorithm/KeyRestrictionEnforcement.php` L40-49, `src/Key/Key.php` L232-254). This is a per-key binding (an
  L3 mechanism); it cannot make a correctly labelled ES256 key refuse ES256.
- No option, type, callback or interface expresses a required algorithm set, a per-issuer policy or a signer count.
  The README places the algorithm decision on the caller: "The library verifies signatures; it does not decide what a
  message is allowed to say. Checking that `alg` is the one expected for that key ... are the caller's
  responsibility" (README L133-137; `doc/Usage.md` L297-309).

## Attempt (`attempt.php`, output `attempt-run.log`)

Own keys: migrated issuer ES256 and Ed25519, legacy issuer `https://legacy-issuer.example` ES256. Objects were built
with the documented creation path (`Signature1`/`Signature` + `sign` + cbor-php tags).

1. Reflection on the installed package: no public method of the message, signer, header, Manager or Key classes
   contains "verif", "polic", "allow", "requir" or "issuer"; only the primitives do.
2. Validity check (documented path, Manager W = {ES256, EdDSA}): V+ accepted, V- rejected (COSE_Sign1 and COSE_Sign).
3. L4m, R = {EdDSA}, W = {ES256, EdDSA}, documented COSE_Sign loop with every configurable library object:
   - Manager W (with or without key restrictions, keys labelled with their own `alg`): T1 accept, T2 reject,
     **T3 accept**, T5 accept. The documented loop is "every present signature verifies" (all-present-valid).
   - Manager R = {EdDSA} (with or without key restrictions): **T1 reject** ("Unsupported algorithm"), T2 reject,
     T3 reject, T5 accept.
   - Recorded, not counted: migrated ES256 key relabelled `alg = -8` with enforcement: T1 reject, T5 accept.

   No configuration gives T1 accept, T2 reject, T3 reject and T5 accept.
4. Own code (recorded as B4 only): the signer loop plus a check that every element of R was among the verified
   signatures (23 lines). It gives T1 accept, T2 reject, T3 reject, T5 accept, permuted T1 accept.
5. L4c supplement (COSE_Sign1), migrated record holding its ES256 and Ed25519 keys, legacy record its ES256 key:
   - one configuration, Manager W: migrated ES256 **accept**; Manager R: legacy ES256 **reject**;
     Manager W with key restrictions and honest `alg` labels: migrated ES256 **accept**.
   - Recorded, not counted (README rule "Key material"): migrated ES256 key relabelled `alg = -8`, or given
     `key_ops = [sign]`, or left out: the three decisions are as required.
   - Own code (B4 only, "L4c (consecutive)"): the caller reads the issuer, picks that issuer's Manager
     (migrated: {EdDSA}; legacy: W) and assembles the verification (14 lines): migrated ES256 reject, migrated
     EdDSA accept, legacy ES256 accept.

Summary line of the run: 26 of 35 checked rows as required; all 9 mismatches are rows of the static library
configurations (6 L4m, 3 L4c), by design of the test.

## Verdict

**L4m: not-expressible** through the documented API without own code. No hook found in the scan, the attempt with
every configurable library object failed, and the line reference shows why: web-auth/cose-lib @
`8849e8bf043a2d42d0bec5bda5db2469ad376148`, `src/Algorithm/Signature/Signature.php` L11-34 (the only verification
primitive: data, key, signature), `src/Algorithm/Manager.php` L97-109 (one algorithm set, no required set),
`src/Signature/CoseSignature.php` L71-89 (signer list without verification), README L133-137 (the algorithm decision
is the caller's); `doc/Usage.md` L368-386 at the same commit (per-signer verification written by the caller).
Expressible with custom code: 23 lines (B4).

L4c supplement: not-expressible in one verifier configuration under the contract §5.3 reading. The per-key `alg`
restriction rejects the migrated ES256 object only if the migrated issuer's ES256 key is relabelled or withheld; a
per-issuer Manager is reachable only by caller code that selects it ("L4c (consecutive)", 14 lines). This matters
only if the target's form were L4c.
