# Undetermined and interpretation-dependent cells (kat-kor, Step 6 task 0)

This file has two parts:
- **§A:** rows whose value is written as `belirsiz` (undetermined) in `BEKLENEN-KOR.tsv`. The source or the cell definition does not determine the value.
- **§B:** cells with a written value that rests on an interpretation decision. For each, the alternative reading and its value are also given.

If a disagreement with the table of the first derivation appears, look here first: most disagreements should coincide with an interpretation choice in §B.

(ASP values in this file: `SALDIRI` = attack exists, `YOK` = no attack.)

---

## §A. `belirsiz` rows (3)

### A1. K2d-01, K2d-02, K2d-03: column `Tamarin`

**Why undetermined:**
- The value dictionary names the lemma for KAT-2b ("if Tamarin flags are given, `cert_authentic`") but not for KAT-2d ("if Tamarin is given ∈ {verified, falsified}").
- According to input §1.4 the KAT-2 Tamarin file contains an authentication lemma (all-traces) and a sensitivity lemma (exists-trace).
- The K2d flags contain no `CRQC`, i.e. the attacker is M1. The three candidate lemmas give three different results:

| Candidate lemma | K2d-01 (V_IGNORE) | K2d-02 (V_ENFORCE_IF_PRESENT) | K2d-03 (V_REQUIRE) | Basis |
|---|---|---|---|---|
| (a) `cert_authentic`: the accepted certificate is the one issued by the CA | verified | verified | verified | Kim p. 60: M1 "cannot forge a classical signature … so every certificate it presents was issued by a real authority" |
| (b) hybrid authentication (all-traces): acceptance ⇒ PQ evidence was verified | falsified | falsified | verified | Kim §III-D security goal; p. 445: "Under M1, P1 provides no more protection than P0" |
| (c) sensitivity (exists-trace): there is a trace that accepts while the PQ evidence is absent or invalid | verified | verified | falsified | Input §1.4 "sensitivity lemma (exists-trace)"; Lee p. 121 |

**Ranking of this work (not evidence):**
- (b) is the most likely. Input §0 criterion 3 requires ASP–Tamarin agreement in the shared cells. The ASP decision of K2d is accept_classical under P0/P1 and reject under P2; only (b) or (c) reflects this difference.
- (a) is possible in that it uses the same lemma name as K2b. In that case the K2d Tamarin column shows the M1/M2 distinction: no forgery under M1.

**Resolution:** the lemma definition in the Tamarin file must be checked.

---

## §B. Interpretation-dependent values (value written; alternative reading given)

### B1. Time constants (KAT-1, KAT-2b; general)

The input does not contain: the default `now`, `qday`, `tau` (τ), `exposure` and the signature intervals of the versions. I derived the values from the logical state that the Tamarin flags encode (DERIVATION §0.1). If the numerical conditions below do not hold, the ASP value changes:

| Cell | Written | Assumed condition [Y] | If the condition does not hold |
|---|---|---|---|
| K1-05 | SALDIRI | The signature of the old DS is valid at now=50 and max(qday, exposure(K_1 or Z_10)) + τ ≤ 50 | YOK |
| K1-07 | SALDIRI | The K_2 signature of the old DK3 is valid at the default `now`; classical Z_10 broken | YOK |
| K1-09 | YOK | The signatures of DK3 and of the old DS expired at 150 | SALDIRI |
| K1-14 | SALDIRI | The K1-09 condition + the extra anchor is classical and broken | (see B3) |
| K1-13 | YOK | Default `now` < 200 | SALDIRI |
| KAT-1, KAT-2b other CRQC cells | SALDIRI | Default qday ≤ now, τ does not push the break past `now` | YOK |

### B2. K1-04, K1-06, K1-11: scope of the completeness test

- **Written:** YOK / verified. The test requires the algorithms signalled by the DS along the whole chain, including the A RRset.
- **Alternative:** The test is done only on the DNSKEY RRset (RFC 6840 §5.11: "insist that all algorithms signaled in the DS RRset work"). Then Z_10 in DK3 verifies the forged A (§6.2) → **SALDIRI / falsified**.
- **Rationale:** "work" expresses that the algorithm works on the validation path. Input §0 also names "does not fall under the policy that requires all algorithms" as the expected result (PR §4.19).

### B3. K1-14: the class of `extra_ta`

- **Written:** SALDIRI / falsified. The extra anchor is the old classical anchor (RFC 6840 Appendix C.2: "old trust anchors configured in perpetuity", "weakest of these trust anchors").
- **Alternative:** If the extra anchor is PQ, the cell becomes the twin of K1-09 → **YOK / verified**.

### B4. K1-15: `allpresent`

- **Written:** SALDIRI / falsified. The RRSIGs present in the response are checked; the attacker does not send the Q signature.
- **Alternative:** "every algorithm in the DNSKEY RRset is required"; this is the "conservative approach" of RFC 6781 §4.1.4. Under that reading **YOK / verified**.
- **Why rejected:** The input mapping defines this policy as "opportunistic: check if present" and gives "—" as its DNSSEC counterpart. RFC 6840 §5.11 also says "MUST NOT insist that all algorithms signaled in the DNSKEY RRset work".

### B5. K1-08 (and K1-06): "seen version" under monotonicity

- **Written:** YOK / verified. The validator has seen the newest version (DS_K_2 or DK5).
- **Alternative:** At first contact `seen` is empty; K1-08 becomes **SALDIRI**.

### B6. K2a-10: catalyst, `enforce_if_present`, invalid PQ

- **Written:** reject. Basis: Lee p. 121 (wolfSSL "a leaf with a forged ML-DSA alternative signature is rejected"), Kim p. 306 and p. 97 ("outcome-bearing").
- **Alternative:** Kim Table VI, row P1, column "invalid, absent, or unsupported": "accept-classical permitted; never accept-hybrid" → **accept_classical**.

### B7. K2d-05: P3, first contact

- **Written:** accept_classical. P3 only forbids going back (Kim p. 90); the input mapping binds P3 to `monotone=1`.
- **Alternative:** The heading "P3 (hybrid + continuity)" in Kim Table VI can be read as P3 including P2 → **reject**.

### B8. Evidence state of K2d

- **Written:** the PQ evidence was withheld (absent; M1). This is the only state in which `seen_hybrid` can affect the decision.
- **Alternative:** The evidence is valid (honest hybrid presentation). Then K2d-01 is accept_classical and K2d-02/03/04/05 are **accept_hybrid**.

### B9. K2b-04 / K2b-05: removal of the TL expectation

- **Written:** tl_cl → SALDIRI, tl_pq → YOK. The signal can be removed only by forging its source.
- **Alternative:** If the attacker can drop the TL and the validator continues without a TL and accepts without expectation, K2b-05 also becomes **SALDIRI**. The input does not define this behaviour.

### B10. K2c: dictionary mapping

The default-path column of Kim Table V uses the observational vocabulary (p. 396: "Default-path cells use the observational vocabulary"). The mapping "classical-accept" → `accept_classical` rests on Kim p. 130 and Figure 1. The value does not change, only the label mapping.

### B11. o6: approval status of the hybrid

- **Written:** unsafe_mixed. The hybrid was counted as approved.
- **Alternative:** If it is not approved, the path set becomes {Unknown, Classical} → `out` = **unknown**.
- The acceptance values (0, 0) are the same under both readings.

### B12. o10: unapproved hybrid

- **Written:** unknown. Stage 3: "Unsupported … Unknown"; "fail closed".
- **Alternative:** If an unapproved structure counts as a violation of an "algorithm-profile requirement" (Table 1) → **invalid**.
- The acceptance values (0, 0) are the same under both readings.

### B13. o8: as written, and the model difference

- **Written:** pqc_protected, 1, 1. Das's literal rule: a path with V_i = 0 is out of scope.
- **Model difference (to be reported separately, input reading note):** an attacker with a CRQC extracts the CEK from the RSA path independently of certificate validity. From the confidentiality point of view this vector would be unsafe_mixed and 0/0.

### B14. The HYBRID_KEM flag

- **Written:** verified. The flag alone, hybrid recipient only.
- **Alternative:** If the flag is run together with a classical recipient (like o6) → **falsified**.

### B15. V4: static violation

- **Written:** 0. The static check takes the expectation into account as the "policy constraints" component of V_i (Das p. 142).
- **Alternative:** If the check counts only the structural paths (the TL also introduces the C key) → **1**. In that case the static/dynamic equivalence breaks in V4, and that would be a model finding.

### B16. KAT-3b: verifier policy

With `expect=0` the verifier was assumed to be anyvalid. The input does not give `pol`. If the verifier carried a local P2, the dynamic attacks V1/V3 would open only via the TL: V1 would still be SALDIRI, **V3 would be YOK**.
