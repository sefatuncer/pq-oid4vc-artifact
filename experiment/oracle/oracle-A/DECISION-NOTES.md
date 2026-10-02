# Oracle A → notes to the maintainers (25.09.2026)

> The PR was **not changed.** The following are the gaps, contradictions and recommendations I found in the pre-registration. Priority order: **N-0 critical**; N-1–N-4 need a decision before the freeze; the rest are clarifications.
> No target was run. The oracle decisions were derived only from the clauses + the `insa` facts.
>
> (Quotations from the pre-registration are translated from Turkish; quotations from specifications are verbatim.)

## N-0 (CRITICAL). The battery has no vectors for the COSE stratum

- **Situation:**
  - 5 of the n = 31 are COSE targets: COSE-001 Signum, COSE-014 cose-js, COSE-034 go-cose, COSE-035 cose-lib, COSE-036 wolfCOSE. All five verify only COSE_Sign1/COSE_Sign.
  - The 153 vectors of v1.2, however, are entirely in JWS/SD-JWT form: artefact types `jws-cekirdek`, `sd-jwt-vc`, `oid4vp-istek`, `dpop`, `sd-jwt-vc+kb`, `status-list-token`.
  - PR §2D item 8 writes this only as a validity threat: "v1 has no COSE/mdoc, JWE and WIA/KA". Its effect on the measurement is not written.
- **Consequence:** for these 5 targets every row of the battery becomes B6 ("not applicable"). Y_L4 cannot be verified behaviourally; F_K, F_T and D_soy cannot be computed.
  - The L level can be determined only by API scanning. Without behavioural verification, the evidence rule (§4.14) does not support a "not expressible" verdict → most come out **undetermined**.
  - n_eff will most likely be ≤ 26. The thresholds are re-read from PR Appendix A; e.g. ≤ 8 / ≥ 18 for n = 26.
- **Options (the decision is the maintainers' and the user's; a candidate major deviation, İ7):**
  - (a) Produce a **COSE battery** with COSE_Sign (multi-signer) and COSE_Sign1 counterparts (K1–K5, K7, K10, V±). `pqjose` already supports COSE. This requires a new anchor and must be done before the freeze (PR §2E item 4).
  - (b) Classify the COSE targets by API scanning and remove them from the primary analysis (n_eff drops, the reason is written).
  - (c) Report the COSE stratum only descriptively.
- **My recommendation:** (a). RQ3 of the PR says "JOSE/COSE/SD-JWT libraries"; if the COSE quota (5) is not measured, the sample design is wasted.

## N-1. Is the §6.5 policy S or Y for an extra signature outside the allowed set?

- The PR leaves K5 open as "Depending on the policy (MR2)". The two definitions also differ in this respect:
  - §4.8 P3 = P2 + R_I and P2 ⊇ P1 ("all present signatures valid") → **S**.
  - The L4 proposal of the inventory (CRITERIA §7.7: "every algorithm in the required set present and valid") → **Y**.
- Oracle A therefore wrote `indeterminate` for the K5 family under `L4` and gave two sub-configurations (`L4-S`, `L4-Y`). There is no primary effect: F_K/F_T are computed only from K1–K3, and there S = Y.
- **Recommendation:** add one sentence to §6.5 in the v1.0 consolidation. Example: "For K5 the oracle is the S (P3/P1) or the Y (R-only) row, according to the documented multi-signature semantics of the target; behaviour that fits neither is an MR2 violation." The values of B1 should also be tied to these two rows.

## N-2. L4c: the battery has no separate "old issuer"

- PR §2B item 6: "In the same verifier instance … the classically signed document of the old issuer is accepted."
- v1.2 has a single `iss` (`https://issuer.example`) and a single ES256 issuer key (issuer/ES256). The classical copy of the migrated issuer (VC10[0], VPLUS_ES256) and "the document of the old issuer" are the same key and the same `iss`.
- Oracle A gave two configurations: `L4` (migrated → reject) and `IZIN-AX` (old → accept-classical). The "same instance" condition is met only if the API can bind the issuer record to the key (`adapter-contract.md` §5.3).
- **Recommendation:**
  - either add an "old issuer" vector with a separate `iss` and a separate ES256 key to the battery (new anchor),
  - or write the clarification "L4c can be tested with the same API mechanism in two consecutive configurations; in that case it is marked as 'L4c (consecutive)'" into the PR.

## N-3. Policy instantiation of K8/K9 in the composite arm

- PR §2F item 4 realises K8 in the composite arm too with X5C04, which has an ML-DSA-65 leaf. The mapping makes the same adaptation for K9 (X5C07).
- If the policy of the composite arm is read as R = {ML-DSA-65-ES256}, X5C04 is **rejected** merely because of the algorithm and B2 is never tested.
- Oracle A instantiated the policy in these rows with **X = ML-DSA-65**. The rows carry a note. This interpretation is not written in the PR; A and B are likely to diverge here.
- **Recommendation:** add "for K8/K9 in the composite arm R = {ML-DSA-65}" to PR §2F item 4, or write B2/B3 explicitly as "arm-independent, measured in the ML-DSA-65 arm".

## N-4. DPoP: the composite algorithms are not registered at IANA

- RFC 9449 §4.3 item 5 [T378]: "The alg JOSE Header Parameter indicates a **registered** asymmetric digital signature algorithm [IANA.JOSE.ALGS]…".
- composite -04 §7.1: "are **requested** to be added to the … registry".
- Therefore a server conforming to RFC 9449 must reject DPOP06, DPOP07 and DPOP09 (ML-DSA-65-ES256, ML-DSA-65-Ed25519). Oracle A wrote them as `reject`; note: "accept-hybrid if registered".
- **Effect:** the M3 deployment constraint table of Step 12 should carry not only the size but also the **registration condition**. Until the draft becomes an RFC, composite DPoP is non-conforming to the specification regardless of the library. This could be a short but non-obvious deployment note in the paper (estimate).

## N-5. The meaning of the four-valued label is not defined in the PR

- Ö6 lists the four values but does not write by which criterion `accept-hybrid` and `accept-classical` are distinguished.
- Oracle A's definition (`METHOD.md` §1; `L4-DERIVATION.md` §4): "accept-hybrid ⇔ acceptance **and** every acceptance path allowed by the configuration requires the verification of a valid PQ component". With this definition:
  - an ES256 + ML-DSA object under P0 → `accept-classical`;
  - the same object under P1 → `accept-hybrid`;
  - an object signed only with ML-DSA → `accept-hybrid`.
- If Oracle B uses a different definition, a "disagreement" appears in identical acceptance decisions merely because of the label. That is not a real oracle disagreement.
- **Recommendation:** report the A–B comparison at two levels: (i) coarse (accept / reject / undetermined) and (ii) four-valued. Writing the definition into the PR is recommended.

## N-6. DER strictness of the composite ECDSA component (CMP05, CMP06)

- -04 §4.5.1 defines the encoding as DER, but for decoding only says: "Decoding simply reverses these two steps".
- LAMPS -19 §4.3 says "raising an error in the event that the input is malformed", but does not define "malformed".
- The tradSig of CMP06 is 72 bytes, so it is not caught by the "≤ 72" bound of -04 Table 2 either.
- Oracle A wrote `indeterminate` for both vectors (UNDETERMINED B-3).
- **Recommendation:** a candidate editorial addition to DB-2 (the descriptive text of composite -04). Example text: "Ecdsa-Sig-Value MUST be DER; verifiers MUST reject non-minimal encodings and trailing data." A human decision; nothing was sent.

## N-7. Version pinning can change the TK assignment

- The interim record of the environment work of 25.09 contains two facts:
  - cose-lib 4.8.2 has no ML-DSA source; HEAD `1c854bf63c5c` has it.
  - The go-cose v1.3.0 README does not contain the basis of the inventory's "ML-DSA partial"; HEAD has it.
- The TK bases of the inventory belong to HEAD commits. Measured with the release version, cose-lib drops from TK1 to TK3.
- **Recommendation:** apply CRITERIA §7 item 6 ("pinned with son_commit_sha") and measure with the target built from the pinned commit. Record the release version separately. This decision must be taken before the TK table is frozen (`adapter-contract.md` §4).

## N-8. SDJWT-004 authlete/sd-jwt does not verify signatures (environment record)

- According to the environment work, the only run-time dependency of the library is gson; the JWS signature is left to the caller.
- In that case the policy layer is not in the library.
  - Either the inclusion criterion K1 ("asymmetric verification") is not met → exclusion and replacement by a reserve (CRITERIA §5.4),
  - or it is measured as L0 "no signature policy".
- **Recommendation:** decide before the behavioural measurement, by API review only.

## N-9. The REQ vectors are wallet-side; OID4VP leaves request signature verification to the wallet's discretion

- OID4VP §5.9.3 [T268]: "it is at the discretion of the Wallet whether it validates the signature on the Request Object" (DC API).
- Oracle A's REQ rows were written under the assumption "the wallet verifies signatures". For the RP, L4 was adapted with the "per entity" reading R_RP = {X} (G5 "a migrated entity").
- These rows are used not in the library battery but in Step 11 (wallet path). Writing the assumption into the Step 11 design is recommended.

## N-10. Policy difference between ECCG ACM v2 and §6.5 K4 (information)

- ACM2 Note 51: ML-DSA "shouldn't be used in a standalone way".
- §6.5 K4, however, says "X only → ACCEPT" and accepts T5P in the ML-DSA arm.
- The two are different policies; the oracle followed §6.5. An ECCG-conforming verifier that rejects T5P appears as a "deviation" against the §6.5 oracle. This should be mentioned in the Step 13 discussion.

## N-11. Clock injection should be an adapter precondition

- The time of the vectors is fixed: `simdi` = 1790003700 (2026-09-21). KB-JWT `iat` = simdi − 100 s, DPoP `iat` = simdi − 10 s.
- A measurement with the real clock (November 2026) falls outside these windows. For a target that cannot inject the clock, the VP and DPOP cells become undetermined with a `zaman` (time) error.
- **Recommendation:** add the question "can the clock be injected?" to the adapter gate (`adapter-contract.md` §2.1).

## N-12. The key of the A–B comparison

- The comparison key should be (vektor_id, politika, kol). Oracle A's configuration names: GEC, IZIN-A, IZIN-AX, L4, L4-S, L4-Y, P0, P1, L4-YOL, @-19.
- **Recommendation:** align the names of Oracle B with a mapping table. Rows present in only one oracle should be reported separately as "single oracle"; they should not count as disagreements.
- For the coarse comparison the primary §6.5 cells are proposed as the core set: `sinif = birincil` and policy `L4` or `GEC`. These are 92 of the 316 primary rows (L4: 53, GEC: 39). 4 of these 92 rows are `indeterminate` (the base L4 rows of the K5 family).

## N-13. Minor consistency notes

- **Count of fallback twins in PR §2E item 1:** v1.1 says "7 twins". In v1.2 **every** control vector with an EdDSA label has its `-ED25519` twin; the script checked this. The only control vector without a twin is `K10K_alg-ES256_anahtar-Ed25519`, because it carries no EdDSA label. The oracle used this vector unchanged in the fallback arm.
- **VC11 (-19):** the rejection is at SHOULD level (RFC 9901 §9.11 RECOMMENDED; the transition note was removed in -19). MR3 will flag this row as an "expected version effect".
- **8725bis §3.14:** JWT libraries are required to reject General JSON input. This shows that K1–K5 (scenario d) are meaningful only for targets with a JWS JSON API; consistent with the PR label "outside the specification". In the adapter contract this rejection was counted as B6, not as an oracle deviation.
