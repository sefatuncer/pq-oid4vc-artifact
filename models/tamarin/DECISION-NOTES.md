# Step 4 (Tamarin) → notes to the maintainers

- **Date:** 24.09.2026
- **Details:** `REPORT.md`
- **Source:** all numbers were taken from the files in `sonuc\`.

## A. Findings that affect the plan

1. **Step 3 (ASP) needs a decision on class semantics.** This finding rests on tool evidence.
   - **Evidence:**
     - In variant `R1 X_alt_ca` the issuer's own chain is fully PQ. With a second CA under the same root that has stayed classical, G1 is **falsified**.
     - `X_alt_ca_forges_honest_issuer` is **verified**: the name of an established honest issuer is forged.
     - Once binding the issuer to its own CA (`NAME_BIND`) is added, G1 is verified.
   - **Datalog side:**
     - The implicit reading of the pilot (`pq(L)` = the real parent is PQ) says "secure" for this variant. This is the only disagreement in 44 rows (`metrikler.txt`).
     - The class semantics (`pq(L)` = **all** signers that the verifier accepts for `L` are PQ) agrees on 44/44.
   - **Recommendation:** one of these three routes should be chosen in the ASP model:
     - define `pq(L)` over all members of the artefact class,
     - add `accepted_signer(L,K)` edges,
     - add a name-binding predicate.

     Otherwise the minimal sets undercount the attacks. In the M2 cost, too, a class should count as migrated only if all its members are PQ (or the name is constrained). Examples: all CAs in the TL; the 43 pointers of the LOTL and the 107 TL signer certificates (§7.10).
   - **Importance:** a candidate cell in which the "root first" order is insufficient under a partial class migration (H4). It can be considered as a candidate non-obvious result.
   - **Consequence for KAT-1:** the edge semantics of RFC 6840 §6.2 should be added to the DNSSEC example: "any DNSKEY … may be used to authenticate any RRset". The primary source was opened and checked in `spec-corpus\metin\RFC6840.txt`.

2. **G5 is handled in two forms.**
   - Step 4 proved the **untimed** G5: a migrated entity is never accepted with classical evidence only.
   - The definition in the design document (§7.4) says "outside its announced legacy-version window". This timed form is the job of R7 (sunset).
   - **Recommendation:** the pre-registration text should state explicitly which form is tested in which step.

3. **The "fresh" condition of H1 has not been tested yet.** In R3 an object signature and a nonce-bound transport gave the same verdict, because the expectation is static. A freshness difference can only show if the expectation changes over time. Therefore R7 should contain a versioned expectation and replay; otherwise the freshness part of H1 lacks Tamarin evidence.

## B. Early signals for the hypotheses (information)

4. **H3, class M-a: S1 is enough.**
   - Without an expectation, or with an unauthenticated one, `S1_downgrade_trace` is verified: the trace contains neither Q-day nor a break.
   - With an authenticated expectation, or without coexistence, this trace does not exist (4/4 falsified).
5. **H5 preliminary signal.**
   - In the R4 `SINGLE_USE` variant, single use in the wallet and global single use at the verifier were applied together. With a classical device key G2 is still falsified.
   - The verifier's global state was deliberately set up in the strongest (idealised) form.
   - The formal H5 test will be done with the R6 windows (R4 × R6).

## C. Tool and process notes

6. **The Tamarin 1.12 preprocessor.**
   - A nested `#ifdef` in a skipped branch gives a parse error.
   - `#ifdef not (A | B)` is not parsed. Plain `&` and `not` work.
   - The layer-3 sample generator should produce flat conditions or write a separate file per instance.
7. **Well-formedness warning in the pilot model.**
   - `tools\regression-tests\p1\weakest_link.spthy` uses the name `Qday` both as an action and as a state fact. Tamarin 1.12 therefore reports "WARNING: 1 wellformedness check failed! The analysis results might be wrong!". The pilot outputs (`tools\regression-tests\p1\out_V*.txt`) carry this warning.
   - In R1–R5 the names were separated; the well-formedness check passes in 34/34 variants.
   - The paper should cite the R1–R5 results instead of the pilot figures.
8. **Use of clingo.**
   - The Datalog comparison was done in the image `pq-a02-solver:1.0`: about 10 s at the end of the batch run, with a 2 GB limit.
   - The Tamarin results do not depend on this step. If the use of the image is considered against the rules, the comparison can be re-run separately.
9. **Time and layer-3 estimate.** The batch run with 230 containers took about 10 minutes. Median per lemma 1.22 s. Layer-3 sampling (50–200 instances) finishes in the order of minutes (estimate).
10. **Method note.**
    - The protected variants of R1 and R4 have no classical key; their security is therefore an easy result.
    - The paper should foreground the instances in which the protection is really tested: the protected variants of R2, R3, R5 and R1 `X_alt_ca_namebind`. In these the CRQC is active and it is the protection itself that prevents the attack.
11. **Interruption.**
    - The session was interrupted (usage limit) after the runs had finished.
    - The runs were not repeated. The report was written from the files in `sonuc\`.
    - `betik\iz_dok.py`, prepared before the interruption but never run, was deleted. The text traces are already in the `sonuc\ham\*.txt` files.

---

# Step 5A (24.09.2026) → notes to the maintainers

**Details:** `REPORT.md` §12. Source of the numbers: `sonuc\metrikler.txt` (Step 5A section) and `sonuc\proverif\metrikler.txt`.

## D. Findings that affect the plan

12. **Unexpected result in R7h: name binding is not enough, key binding is needed.** This finding rests on tool evidence.
    - **Pre-registered expectation:** G5 and G1 = V for the protected `P_ca_pq_alt_namebind` (CA_PQ, ALT_CA, NAME_BIND).
    - **Observed:** both **F**. Pre-registered total 347/349.
    - **Trace:** the root certifies the alternative classical CA **with the same name** as the legitimate CA. Name binding therefore accepts the certificate without commitment.
    - **Exploration (R7hx):** with a separate pre-registration digest, 35/35 as expected:
      - if CA names are unique, name binding protects,
      - if there is a classical CA with the same name (CA key change), it is circumvented,
      - **key binding** protects in both cases.
    - **Effect on Step 4:** the result `X_alt_ca_namebind` = V in R1 depended on the assumption that CA names are unique (`Unique(<'ca', name>)`).
    - **To be passed to the ASP model (Step 3):** the parameter `ad_baglama` (name binding) should be defined as **key binding**. Or "CA name unique" should be written as a separate assumption. The key-change period, in which classical and PQ certificates of the same name are valid together, should be a separate cell.
    - **Importance:** a concrete trace for the candidate "circumvention of M-h via an alternative path" in L-D4. Circumvention even under name binding is, as an estimate, a candidate non-obvious result. The novelty assessment should be made by the maintainers.
13. **The pre-registration text of H3 should be updated.** The prediction "every component of M-f is necessary" turned out to be **context-dependent**.
    - **Online (FRESH) or pinned set-up:** MONOTONE and SUNSET_CHECK are unnecessary (`A_online_no_monotone`, `A_online_no_sunset`, `A_pinned_min`: V/V/V). This was a pre-registered prediction.
    - **Offline set-up:** both are necessary (`M_off_monotone`, `M_off_sunset`).
    - **Core needed in every set-up:** third party + PQ channel + per entity + current value.
    - The "the mechanism is simplified" branch of the falsification condition in the pre-registration applies. The simplified M-f definition is in `REPORT.md` §12.4.
14. **The two forms of G5 were formalised.**
    - Untimed form: R2, R3, R7h.
    - Timed form: R7 `G5_timed`, after the sunset.
    - In addition `G5_migrated`, which covers first contact.
    - The pre-registration should write the three as separate goals.

## E. Preliminary results for the hypotheses

15. **H2 (L-D3 confirmed).**
    - A long-lived status signing key can be forged in every regime.
    - A rotated key is protected only in SLOW, a per-token key in MEDIUM and SLOW.
    - There are two extra conditions: PQ identity binding and no key reuse.
    - Window classes are needed in the ASP model: long-lived / period / token. In addition `exposure(K)` and `last_accept(K)`.
16. **H5 (formal):** with a classical device key, single use (wallet + global verifier) does not prevent forgery (`M_single_fast` = F). Only these two together protect: a validity window shorter than τ and a device key per credential.
17. **H3 / L-D1 (M-f ↔ M-g):**
    - M-g gives a downgrade trace at first contact in all three variants; no Q-day is needed.
    - M-f (online or pinned) protects the first contact.
    - The distinguishing property of L-D2 was shown in Tamarin.

## F. Tool and process notes

18. **The well-formedness rule was applied.**
    - `calistir.sh` checks every lemma run; a run with a warning is recorded as `gecersiz_wf` (invalid: well-formedness).
    - In Step 5A 390/390 outputs, in total 620/620, without warning; 0 invalid runs.
19. **ProVerif second opinion:**
    - 15 variants of R1–R5, 20 security queries. Definite result 20/20, agreement with Tamarin 20/20; "cannot be proved" 0.
    - The 2/4 "unknown" of the pilot did not occur here. A difference in encoding is a possible reason [Y].
    - R6/R7 were not transferred to ProVerif: phases are weak at expressing τ.
20. **TSV check after the interruption.**
    - `varyantlar.tsv` matches the pre-registration digest; its first 38 rows are byte-for-byte identical to the Step 4 file; CR and `|` 0.
    - No format fix was needed. The "CRLF: 81" output of the first check was a shell quoting error.
21. **`degerlendir.py` was generalised.** The Step 4 results were reproduced exactly; the only difference is the label "bilgi-H3" → "bilgi" (information).
22. **Resource use:**
    - The Tamarin runs of Step 5A took about 18 min, 19:11:34–19:31:45.
    - Longest per lemma 3.58 s, median 1.03 s; memory at most 115.8 MiB.
    - The ladder was never needed.
    - Docker was left running; only containers named `pq-a04-*`, started with `--rm`, were used.
