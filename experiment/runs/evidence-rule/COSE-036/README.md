# COSE-036 wolfCOSE f907071b1012: evidence-rule second attempt

| Field | Value |
|---|---|
| Library | wolfCOSE 2.0.0 (`LIBWOLFCOSE_VERSION_STRING`), git commit `f907071b1012`, built with `make all EXTRA_CFLAGS=-DWOLFCOSE_ENABLE_DEPRECATED_ALGS` (`libwolfcose.a` sha256 `ddaafd46...`); the default build of the same tree gives `f826574c...`, equal to the installation record |
| Repository / commit | https://github.com/wolfssl/wolfcose, `f907071b10127f3ae2dd7719749a91b039ff04a1` (tree `78dd09da...` = installation record); the fetched tree is identical to the commit archive |
| Environment | `pq-a09-env-c:1.0` (GCC 15.3.0), wolfSSL v5.9.2-stable (`ac01707f552c`) configured with the record's flags (`--enable-ecc --enable-ed25519 ... --enable-mldsa ...`); source build, no lock file |
| Date | 2026-10-03 (UTC 09:41 to 09:53) |
| Time spent | about 12 minutes |
| X | EdDSA (-8; enabled by `WOLFCOSE_ENABLE_DEPRECATED_ALGS`) |
| Form | **L4m** (primary); L4c run as a supplement |
| Verdict L4m | **not-expressible** without own code (B4 record: 20 lines) |
| Verdict L4c (supplement) | reachable only if the migrated issuer's ES256 key is relabelled (pin -8) or left out; otherwise own code (B4: 16 lines) |
| API hook found | no |

## Form and basis

`wc_CoseSign_Verify(verifyKey, signerIndex, ...)` is the documented verification of COSE_Sign messages with several
signers (`include/wolfcose/wolfcose.h` L1584-1615; `docs/API-Reference.md` L979-1003). `docs/Message-Types.md`
L40-42 names "hybrid classical/PQC signatures during migration" as a use of COSE_Sign. The target processes
multi-signature objects, so the form is L4m.

## API scan (summary; full commands and outputs in `api-scan.txt`)

- `wc_CoseSign_Verify` takes one key and one signer index and verifies only that signer: it checks
  `signerIndex < signatureCount` (`WOLFCOSE_E_INVALID_ARG` otherwise) and skips every other signer without
  verifying it (`src/wolfcose_sign.c` L964-975, L1029-1036). "The caller must match the key to the signer (via kid or
  out-of-band)" (`wolfcose.h` L1587-1588); "Verifiers select which signature to check by index"
  (`docs/Message-Types.md` L63). The scenario example verifies a dual-signed message with two calls at fixed
  indices (`examples/scenarios/multi_party_approval.c` L196-221).
- `wc_CoseSign1_Verify(key, ...)` takes one key (`wolfcose.h` L1222-1249).
- `WOLFCOSE_KEY.alg` is an algorithm pin: a set pin rejects a message algorithm that differs with
  `WOLFCOSE_E_COSE_BAD_ALG` (`wolfcose.h` L174-177, L396-399; `src/wolfcose_sign1.c` L1198-1202;
  `src/wolfcose_sign.c` L1017-1022). This is a per-key binding (an L3 mechanism); it cannot make a correctly pinned
  ES256 key refuse ES256.
- No exported function returns the signer count or verifies a COSE_Sign as a whole; no option, type or callback
  expresses an allow-list, a required algorithm set or an issuer. The only function-pointer types are the signing
  callback `WOLFCOSE_SIGN_CB` (`wolfcose.h` L367-386) and two PSA attestation token (RFC 9783) callbacks in
  `eat_psa.h`. The PSA key resolver (`eat_psa.h` L103-124) receives a UEID and the algorithm, but it is off by
  default, applies only to PSA tokens with the RFC 9783 claim set, its documentation says the resolver "must not use
  that preliminary UEID for authorization" (`docs/PSA-EAT.md` L189-194), and it is not in the measured build
  (`nm`: no `wc_CoseEatPsa*` symbol). It is not a hook for this target.

## Attempt (`attempt.c`, `run.sh`, output `attempt-run.log`)

Own keys (wolfCrypt): migrated issuer ES256 (P-256) and Ed25519, legacy issuer `https://legacy-issuer.example`
ES256; verification keys are public-only and pinned to their own algorithm, as the header recommends. Objects were
made with `wc_CoseSign1_Sign` and `wc_CoseSign_Sign`.

1. Validity check: V+ accepted, V- rejected (COSE_Sign1; COSE_Sign with the two-call pattern of the example).
   Recorded: `Verify(A key, 0)` alone accepts T2, because the corrupted X signature at index 1 is not checked.
2. L4m, R = {EdDSA}, W = {ES256, EdDSA}, four static lists of (key, index) calls, all of which must succeed:
   - `[(A,0), (X,1)]`: T1 accept, T2 reject, T3 reject, **T5 reject**, **permuted T1 reject**.
   - `[(X,1)]`: T1 accept, T2 reject, T3 reject (index out of range), **T5 reject** (index out of range),
     **permuted T1 reject**.
   - `[(X,0)]`: **T1 reject** (`WOLFCOSE_E_COSE_BAD_ALG`), T2 reject, T3 reject, T5 accept, permuted T1 accept.
   - `[(X,0), (A,1)]`: **T1 reject**, T2 reject, T3 reject, **T5 reject**, permuted T1 accept.

   No static configuration gives T1 accept, T2 reject, T3 reject and T5 accept, because each call names the signer
   position, which differs between the objects.
3. Own code (recorded as B4 only): a loop over signer indices that tries the issuer's pinned keys at each index until
   the index is out of range, and then requires that an EdDSA signer verified (20 lines). It gives T1 accept,
   T2 reject, T3 reject, T5 accept, permuted T1 accept. (The corrupted Ed25519 signature is reported by this build as
   `WOLFCOSE_E_CRYPTO`, `src/wolfcose_sign.c` L1134-1139; a reject either way.)
4. L4c supplement (COSE_Sign1), migrated record = {ES256 key pinned -7, Ed25519 key pinned -8}, legacy record =
   {ES256 key pinned -7}: migrated ES256 with the record's ES256 key **accept**, migrated EdDSA accept, legacy ES256
   accept. Recorded, not counted (README rule "Key material"): with the migrated ES256 key relabelled (pin -8) or
   left out, the migrated ES256 object is rejected with `WOLFCOSE_E_COSE_BAD_ALG`.
5. L4c with own code (B4 only): per-issuer records, key lookup by kid, and a check of the returned `hdr.alg` against
   the issuer's allowed set after verification (16 lines): migrated ES256 reject, migrated EdDSA accept, legacy ES256
   accept.

Summary line of the run: 21 of 29 checked rows as required; all 8 mismatches are rows of the static
configurations (7 L4m, 1 L4c), by design of the test.

## Verdict

**L4m: not-expressible** through the documented API without own code. No hook found in the scan, the attempt with
every static configuration failed, and the line reference shows why: wolfssl/wolfcose @
`f907071b10127f3ae2dd7719749a91b039ff04a1`, `include/wolfcose/wolfcose.h` L1584-1615 (`wc_CoseSign_Verify`: one
key, one caller-chosen signer index; "the caller must match the key to the signer") and `src/wolfcose_sign.c`
L964-975 and L1029-1036 (only the indexed signer is verified, the others are skipped); `docs/Message-Types.md`
L63-71 ("Verifiers select which signature to check by index"). A required set over the signers exists only as own
code with `wc_CoseSign_Verify`: 20 lines (B4).

L4c supplement: if the maintainers count "a migrated issuer's record pins its keys to algorithms in R" as a
per-issuer policy, L4c is reachable through the key pin (`wolfcose.h` L174-177, `src/wolfcose_sign1.c` L1198-1202),
but only by relabelling the migrated issuer's ES256 key to EdDSA or by leaving it out; under the contract §5.3
reading (the migrated record holds its classical key) it is not. This matters only if the target's form were L4c.
