# KAT blind derivation input (prepared by the maintainers)

> This file is `literatur/analiz/KAT-SPEC.md` **with the expected values, bases, draft code, mutation and implementation sections removed**. Purpose: a second, independent and blind derivation of the expected values as required by PR §4.19 and KAT-SPEC §5.3. The cell definitions (inputs) are kept verbatim.
>
> (Translated from Turkish for this release. Quotations from RFCs and papers are verbatim. The original Turkish file, whose hash is recorded in `GIRDI.sha256`, is listed in `docs/INTEGRITY.md`.)

# KAT-SPEC: Known-answer test specification (Step 6)

> **Prepared by:** the literature work · 23–24.09.2026
> **Status:** draft of an implementable specification. **The code fragments were not run.** The Step 6 work should first derive an independent table of expected values under the N-version principle (§5.3), and then run.
> **Basis:** design document §7.9 Layer 3/4, §7.12, §7.15 (week-6 gate: "all known-answer tests passed"), §7.14 (scope: 3 tests).
> **Source texts** (read only, not written):
> - `spec-corpus/metin/RFC6840.txt`, `RFC6781.txt`, `RFC7583.txt`, `RFC9955.txt`
> - `literatur/metin/kim2026_x509_hybrid.txt`, `lee2026_eprint1416.txt`, `das2026_smime_eprint1374.txt`
> - Pilot: `referans/pilot/p1/weakest_link.spthy`, `p2/*.lp`
>
> **RFC texts:** found in the corpus. Quotations were taken verbatim from the text ("text verified").
>
> **Labels:** L✓ (this work read it from the full text) · [Y] (own inference) · estimate.

---

## 0. Purpose and general pass criterion

**Purpose:** to show that the model (ASP core + Tamarin rule schemata) reproduces three results **published** for other layers. This tests model fidelity and generalisability. No contribution is claimed.

| KAT | Result to be reproduced | Model assumption tested (summary) |
|---|---|---|
| **KAT-1** DNSSEC | Under the "any single valid path" rule the weakest signalled algorithm determines security. Algorithm rollover and replay extend this window. A signature completeness test, a PQ-signed signal from above and monotonicity close this window | ∃-path policy semantics; key–artefact binding; expectation channel (signal ≠ enforcement); version, time and replay |
| **KAT-2** X.509 hybrid | "Classical acceptance ≠ hybrid authentication": on the default path, corrupting the PQ evidence does not change the decision. Composite binds structurally. Revocation of the bound PQ certificate does not enter the decision | Separable and atomic encoding; sensitivity of the decision to the PQ evidence; lifecycle coverage; distinction between withholding (M1) and forging (M2) |
| **KAT-3** S/MIME | "Every valid path to the CEK must satisfy the active migration policy" and its authentication dual | Completeness of path enumeration; ∀-quantifier; equivalence of static policy checking and dynamic attack search |

**General pass criterion** (all must hold together):
1. In every cell the ASP result equals the expected value **100%**.
2. In every logical cell the Tamarin result equals the expected value **100%**.
   - A logical cell is a cell whose time is represented only by a flag.
   - If "analysis incomplete" appears, the non-termination ladder of design document §7.9 is applied.
   - If it does not close after the ladder either, the cell is counted as **indeterminate** and the KAT **fails**.
3. ASP and Tamarin results agree **100%** in the shared cells.
4. **Mutation:** when each protection listed in §6 is removed, at least one "YOK" (no attack) cell must turn into "SALDIRI" (attack).
5. **Time:**
   - ASP cell under 10 s.
   - Tamarin lemma within 600 s and 12 GB (in the pilot, similar sizes were below 1 s).
   - Whole KAT package under 15 minutes (estimate).

**Reading the result in ASP:** the question "is there an attack?" is answered as follows:
- If core + instance + the constraint `:- not attack.` is **SAT**, there is an attack (clingo exit code 10 or 30).
- If **UNSAT**, there is no attack (exit code 20).

In the deterministic decision module (`hon_decision.lp`) the single answer set is read (`decision/2`).

---

## 1. Shared core

### 1.1 Input vocabulary (independent of the ecosystem)

| Fact | Meaning | KAT-1 | KAT-2 | KAT-3 |
|---|---|---|---|---|
| `key(K)`, `key_class(K,C)`, C ∈ {cl, pq, comp} | Key and its class. comp: breaking it requires breaking all components | KSK/ZSK, parent zone key | classical/PQ/composite key of the CA | issuer and TL keys |
| `comp_part(K,K1)` | composite component | — | ● | — |
| `exposure(K,T0)` | First moment at which the public key is visible to the attacker (see CRQC-TAKVIMI (CRQC timeline) §1) | ● | ● | ● |
| `art(A)`, `owner(A,E)`, `target(T)` | Artefact, its owner, the target to be forged | DS, DNSKEY, A RRset | EE certificate | credential, TL |
| `slot(A,S,K)` | Signature S on A (with K) | RRSIGs | base/alt/composite signature | TL and credential signatures |
| `intro_s(K,I)` / `intro_v(K,I,V)` | Artefact I introduces K (unversioned / in version V) | DS→KSK, DNSKEY→ZSK | — | TL→issuer keys |
| `introducer(I)`, `validates(I,X)` | Keys introduced by I can validate X (edge) | ds→dnskey, dnskey→a_rr | — | tl→cred |
| `anchor(K)`, `anchored(K,X)` | Trust anchor K validates X directly | kp→ds | CA→ee (end-entity coverage only; Kim's test coverage) | ktl→tl |
| `version(I,V,Inc,Exp)`, `versioned(I)`, `seen(I,V)` | Signed version, signature validity interval and the newest version seen by the verifier (monotonicity) | ● | — | — |
| `signal_s/3`, `signal_v/4`, `local_req/2` | Expectation: I makes class C required for E. Local policy P2 | algorithms signalled by the DS | local P2 or expectation from the TL | "pq_required" in the TL |

**Channel class** (design document §7.4):
- All artefacts in KAT-1 are of the **fetched** kind. The DNS transport is unauthenticated; therefore an H1-type substitution is not possible. This is a sanity cell for H1.
- The certificate in KAT-2 is of the **conveyed** kind.
- In KAT-3b the TL is **fetched** and the credential **conveyed**.

**Policy mapping:**

| Core `pol` | Design document §7.10(c) | Kim et al. | DNSSEC |
|---|---|---|---|
| `anyvalid` | P0 | P0 / default path | RFC 6840 default |
| `allpresent` | P1 | P1 (opportunistic: check if present) | — |
| `required` + `local_req` | P2 | P2 | "signature completeness" |
| `required` + `signal` from a signed source | P3 (classical source) / P4 (PQ source) | — (P3 state source left open) | DS signal + completeness test |
| `monotone=1` | monotonicity component of M-f | P3 (continuity) | refusing to go back within the RRSIG validity |

### 1.2 ASP core `kat_core.lp` (DRAFT; not run)

> [draft code block removed: the blind derivation is made from the primary source]

**Simplification note:** it is assumed that honest intermediate artefacts satisfy the policy. In the KATs the honest intermediate artefacts are signed with both algorithms, so this assumption does not change the result. In the main model it should be narrowed with a `hon_ok/1` condition [Y].

### 1.3 Honest decision module `hon_decision.lp` (KAT-2a/2c/2d; DRAFT)

There is no attacker. The verifier's decision on an honest object is computed depending on the state of the PQ evidence. This tests "decision sensitivity" (Kim's 27 cells).

> [draft code block removed: the blind derivation is made from the primary source]

### 1.4 Tamarin patterns (same style as the pilot `weakest_link.spthy`)

- `builtins: signing` (in KAT-3a additionally `asymmetric-encryption`, `symmetric-encryption`).
- `restriction Eq`, `restriction NotEq` (when needed), `restriction Once`.
- `rule Qday` and `!Qday()`. `Break_*` rules that release a classical key after Q-day (S2 abstraction). τ is not modelled in Tamarin; time cells are represented by flags, and ASP carries τ.
- Policy and stage differences are selected with **preprocessor flags** (`-D=FLAG`). If a compound condition is needed, a single compound flag is defined (for example `DS_PQ`). Whether the Tamarin 1.12 preprocessor supports compound expressions was not verified by this work.
- Two lemmas in every file: `executable` (exists-trace, sanity) and the authentication lemma (all-traces). KAT-2 additionally has a sensitivity lemma (exists-trace).

### 1.5 Input format and run harness (proposal)

Ecosystem-independent YAML → ASP facts + Tamarin flags. Example (KAT-1, K1-03):

> [draft code block removed: the blind derivation is made from the primary source]

Report row (CSV):

`kat,cell,consts,flags,expected_asp,asp_result,asp_exit,expected_tamarin,tamarin_result,tamarin_s,agree,git_commit,image_digest`

---

## 2. KAT-1: DNSSEC "any single valid path" and algorithm downgrade

### (a) Published result to be reproduced (text verified)

**RFC 6840** (Weiler, Blacka, February 2013; Standards Track; updates RFC 4033/4034/4035/5155):

- **§5.11 "Mandatory Algorithm Rules"**, last paragraph:
  > "This requirement applies to servers, not validators. Validators SHOULD accept any single valid path. They SHOULD NOT insist that all algorithms signaled in the DS RRset work, and they MUST NOT insist that all algorithms signaled in the DNSKEY RRset work. A validator MAY have a configuration option to perform a signature completeness test to support troubleshooting."
- **§6.2 "Clarifications on DNSKEY Usage":**
  > "However, be aware that there is no way to tell resolvers what a particular DNSKEY is supposed to be used for -- any DNSKEY in the zone's signed DNSKEY RRset may be used to authenticate any RRset in the zone."
- **Appendix C.2 ("Accept Any Success"; §5.10 recommends it as the default):**
  > "This policy has the disadvantage of making the validator subject to the compromise of the weakest of these trust anchors, while making it relatively painless to keep old trust anchors configured in perpetuity."

**RFC 6781** (Kolkman, Mekking, Gieben, December 2012; DNSSEC Operational Practices v2):
- **§4.1.4 "Algorithm Rollovers":**
  - It defines conservative and liberal interpretations.
  - Stages (Figure 8): initial → new RRSIGs → new DNSKEY → new DS → DNSKEY removal → RRSIGs removal.
  > "When removing an old algorithm, the DS for the algorithm should be removed from the parent zone first, followed by the DNSKEY and the signatures (in the child zone)."
- **§4.3.4 "DS Signature Validity Period":**
  > "Since the DS can be replayed as long as it has a valid signature, a short signature validity period for the DS RRSIG minimizes the time that a child is vulnerable in the case of a compromise of the child's KSK(s)."

**RFC 7583** (Morris et al.; Key Rollover Timing):
- §1 scope: "Algorithm rollovers. Only the rolling of keys of the same algorithm is described here: not transitions between algorithms."
- Double-DS KSK timing: `Iret = DprpP + TTLds`, `Tdea(N) = Tret(N) + Iret`. We use this only for naming the time parameters; it is not normative for algorithm rollover.

**RFC 9955 §6.2** (general principle):
> "As such, if a system does skip a component signature, security does not rely on the security of all component signatures."

**Proposition to be reproduced** (direct logical consequence of the RFC texts):
- The phrase "algorithm downgrade" does **not occur** in RFC 6840; the result follows from the combination of the rules [Y].
- Under an RFC 6840 validator, if a zone is signed with classical (C) and PQ (Q) algorithms, the security of the validator equals that of the weakest reachable algorithm. An attacker who can forge classical keys (CRQC) gets forged RRsets accepted even when Q signatures exist.
- Even if the DS points only to Q, the attack continues as long as the C key stays in the DNSKEY RRset (§6.2).
- The window closes when all of these conditions hold: the old DS has been withdrawn, the old keys have been removed from the DNSKEY RRset, the signature validity of the old signed versions has expired (RFC 6781 §4.1.4, §4.3.4).
- Negative controls:
  - A signature completeness test + a PQ-signed parent zone signal (DS) removes the attack.
  - A monotone validator state removes replay.
  - If the parent zone key is classical, the signal is forged and the attack comes back.

### (b) ASP counterpart

**Required model elements:**

| Element | DNSSEC | Our counterpart (OpenID4VC) |
|---|---|---|
| Artefact | `ds` (parent zone DS RRset), `dnskey` (zone DNSKEY RRset), `a_rr` (target RRset) | TL/LoTE entry, `x5c` or issuer metadata `jwks`, credential or status list |
| Edge (introduction) | DS→KSK (`validates(ds,dnskey)`); DNSKEY RRset→every key (`validates(dnskey,a_rr)`) | TL→issuer key; `x5c`→signing key |
| Signature edge | RRSIGs (`slot`) | JWS/COSE signatures |
| Channel | all fetched; transport unauthenticated | fetched (TL, status) / conveyed (credential) |
| Expectation | algorithms signalled by the DS (`signal_v`) | per-entity expectation in the TL/LoTE (M-f) |
| Policy | `anyvalid` (RFC 6840 default), `required` (completeness test), `allpresent` | P0, P3/P4, P1 |
| Time | versions, signature validity intervals, `seen` (monotonicity) | TL `nextUpdate`, status `ttl`, sunset |

**Instance file `kat1_dnssec.lp`** (together with the core; DRAFT):

> [draft code block removed: the blind derivation is made from the primary source]

### (c) Tamarin counterpart (minimal rules and lemma; DRAFT)

> [draft code block removed: the blind derivation is made from the primary source]

**Note:**
- In the cell `MONOTONE` + `OLD_DS_REPLAY` (K1-06) the return to the old DS is prevented by a separate restriction. In practice the flag `OLD_DS_REPLAY` is never given for K1-06; this is equivalent to a monotone validator not accepting the old DS [Y].
- The attacker can generate its own key. For example it builds a forged DS and DNSKEY with `pk('k')`. K1-12 arises this way.

## 3. KAT-2: X.509 hybrid, "classical acceptance ≠ hybrid authentication"

### (a) Published results to be reproduced (L✓)

**Kim et al. 2026** (arXiv:2607.20800v3):
- **§VI-A:**
  > "We ran the invalidated variant of Section V-B beside its valid counterpart in every one of the 27 cells formed by the three separable schemes and the nine configurations. In all 27 the two verdicts were identical."

  Two cells are not informative: the Catalyst encoding divergence in the wolfSSL enforcing build, and NSS not recognising the ML-DSA key in Chameleon. The remaining 25 are acceptance cells.
- **Table IV (composite):** [result removed — read it from the primary text: `literatur/metin/kim2026_x509_hybrid.txt`]
- **§VII, Table V (Related, certA valid):** leafB state revoked / expired / OCSP unknown / absent / valid. [Results removed — read them from the primary text.]
- **§VIII-A, Table VI (P0–P3):**
  > "Under M1, P1 provides no more protection than P0: the adversary withholds the post-quantum evidence, P1 tolerates the absence, and the result is accept-classical, which the policy permits."

  On P3: "a later accept-classical for an identity recorded as hybrid-required is itself non-accepting". Table note: "P3 presupposes an external continuity state keyed by the relying party's identity notion; we model only the verifier-side implication, not how it is stored or populated".

**Lee et al. 2026** (IACR ePrint 2026/1416):
- **§4.3:** nine standard verifiers accept a Catalyst certificate that carries a valid ECDSA base signature and an invalid PQC alternative signature.
  > "With Composite, corrupting either the ML-DSA or the classical component of the composite signature is rejected with a signature-verification failure".

  This result was seen in three independent verifiers and three OID families.
- **§4.4:** "None of the 15 stacks we tested provides a working default – or even readily configurable – way to require the binding". wolfSSL "does verify a present alt-signature (…) yet there is no mechanism to mark an alt-signature as required, so a stripped classical-only leaf (…) is accepted".
- **§6:** "(…) paired with a require-PQC policy, since no encoding alone defeats a full classical downgrade."

### (b) ASP counterpart

**Required model elements and mapping:**

| Element | X.509 | Our counterpart |
|---|---|---|
| Artefact | EE certificate (`ee`); in Related `certA` + `leafB` | credential + `x5c`; double issuance |
| Signature slot | Catalyst: `s_base` (classical, critical) + `s_alt` (PQ, non-critical); Composite: a single `s_comp` (comp) | Scenario (a) composite `alg`; (b)/(d) separable (double issuance, General JSON) |
| Channel | conveyed | conveyed (`x5c`, credential) |
| Policy | `vb` ∈ {ignore, parse_no_enforce, enforce_if_present, require, continuity, legacy_oid} | P0 / P0 / P1 / P2 / monotonicity / — |
| Lifecycle | `bound(certA,leafB)`, `status(leafB,St)` | whether the status list / TL enters the scope of the decision |

**KAT-2a/2c/2d**, together with `hon_decision.lp` (§1.3) (DRAFT):

> [draft code block removed: the blind derivation is made from the primary source]

**KAT-2b** (M2, forgery with a CRQC), together with `kat_core.lp` (DRAFT):

> [draft code block removed: the blind derivation is made from the primary source]

### (c) Tamarin counterpart (minimal rules and lemmas; DRAFT)

> [draft code block removed: the blind derivation is made from the primary source]

## 4. KAT-3: S/MIME "every valid path to the CEK" and the authentication dual

### (a) Published result to be reproduced (L✓)

**Das and Chattopadhyay 2026** (IACR ePrint 2026/1374; received 04.07.2026, revised 21.09.2026; "Published elsewhere. ICDSNE 2026"):
- **Abstract:**
  > "We model encrypted S/MIME as a multi-recipient CMS object with certificate-bound paths to a shared CEK and show that post-quantum confidentiality is a universal message-level property: every valid path to the CEK must satisfy the active migration policy."
- **§3, Equation (8):** Accept(ED, P_t) = 1 ⟺ ∀i ∈ R, V_i(t) = 1 ⇒ χ_i(t) ∈ A_t. Here V_i(t) is certificate validity, χ_i(t) ∈ {PQC, Hybrid, Classical, Unknown, Invalid} the path class, and A_t the classes permitted by the policy.
- **Proposition 1:**
  > "Therefore, the confidentiality level of ED is bounded by the weakest valid recipient path protecting K."
- **§3.1 Stages 3–5 and Table 1:**
  - Six message classes: pqc-protected, hybrid-protected, classical-only, unsafe-mixed-mode, invalid, unknown.
  - Order of precedence: malformed → invalid; "unsafe mixed-mode exposure is reported before weaker uncertainty labels"; "Unknown mechanisms fail closed".
  - Modes: strict-PQC, transitional-hybrid, legacy-audit.

**Reading note [Y]:**
- The rule is conditional on V_i(t)=1. For confidentiality, an attacker with a CRQC can extract the CEK from a classical recipient path (RI) even if the certificate is invalid. This vector is o8 in the table below.
- The authors do not discuss this case.
- **In the authentication dual** this condition is natural: a path that the verifier rejects cannot lead to acceptance.
- KAT-3a reproduces Das's rule **as written**; o8 is additionally reported as a "model difference".

### (b) ASP counterpart

**KAT-3a: literal CMS confidentiality classification** (DRAFT):

> [draft code block removed: the blind derivation is made from the primary source]

**KAT-3b: authentication dual** (`kat_core.lp` + the following; the same 6 configurations as the pilot `weakest_link.spthy`):

> [draft code block removed: the blind derivation is made from the primary source]

### (c) Tamarin counterpart

**KAT-3a: CEK confidentiality** (DRAFT):

> [draft code block removed: the blind derivation is made from the primary source]

**KAT-3b:** the pilot `referans/pilot/p1/weakest_link.spthy` is run **unchanged** with six flag combinations.
- KAT-3b matches these results with the ASP dual.
- Lemma: `claims_unforgeability`.



---

# CELL DEFINITIONS (expected columns removed)

## 2. KAT-1: DNSSEC "any single valid path" and algorithm downgrade

| Cell | ASP constants | Tamarin flags |
|---|---|---|
| K1-01 | stage=r2, pol=anyvalid | DS_CL, DK3_USABLE, ANYVALID |
| K1-02 | stage=r2, pol=required | DS_CL, DK3_USABLE, COMPLETENESS |
| K1-03 | stage=r3, pol=anyvalid | DS_PQ, DK3_USABLE, ANYVALID |
| K1-04 | stage=r3, pol=required | DS_PQ, DK3_USABLE, COMPLETENESS |
| K1-05 | stage=r3, pol=required, now=50 | DS_PQ, OLD_DS_REPLAY, DK3_USABLE, COMPLETENESS |
| K1-06 | K1-05 + monotone=1 | DS_PQ, DK3_USABLE, COMPLETENESS (no old DS) |
| K1-07 | stage=r5, pol=anyvalid | DS_PQ, DK3_USABLE, DK5, ANYVALID |
| K1-08 | K1-07 + monotone=1 | DS_PQ, DK3_USABLE, DK5, ANYVALID, MONOTONE |
| K1-09 | stage=r5, pol=anyvalid, now=150 | DS_PQ, DK5, ANYVALID |
| K1-10 | stage=dds, pol=anyvalid | DS_BOTH, DK3_USABLE, ANYVALID |
| K1-11 | stage=dds, pol=required | DS_BOTH, DK3_USABLE, COMPLETENESS |
| K1-12 | stage=r3, pol=required, parent_class=cl | DS_PQ, DK3_USABLE, COMPLETENESS, PARENT_CL |
| K1-13 | stage=r3, pol=anyvalid, qday=200 | DS_PQ, DK3_USABLE, ANYVALID, NO_QDAY |
| K1-14 | stage=r5, pol=anyvalid, now=150, extra_ta=1 | DS_PQ, DK5, ANYVALID, EXTRA_TA |
| K1-15 | stage=r3, pol=allpresent | DS_PQ, DK3_USABLE, ALLPRESENT |


## 3. KAT-2: X.509 hybrid, "classical acceptance ≠ hybrid authentication"

| Cell | scheme | vb | pqev |
|---|---|---|---|
| K2a-01/02 | catalyst | ignore | valid / invalid |
| K2a-03/04 | catalyst | parse_no_enforce | valid / invalid |
| K2a-05/06 | chameleon | ignore | valid / invalid |
| K2a-07/08 | related | ignore | leafb=valid / revoked |
| K2a-09…11 | catalyst | enforce_if_present | valid / invalid / absent |
| K2a-12…14 | catalyst | require | valid / invalid / absent |
| K2a-15/16 | composite | require (recognising composite) | valid / invalid |
| K2a-17 | composite | legacy_oid | valid |

| Cell | scheme | pol | expect_src | coexist_cl | Tamarin flags |
|---|---|---|---|---|---|
| K2b-01 | catalyst | anyvalid | none | 0 | CRQC, V_IGNORE |
| K2b-02 | catalyst | allpresent | none | 0 | CRQC, V_ENFORCE_IF_PRESENT |
| K2b-03 | catalyst | required | local | 0 | CRQC, V_REQUIRE |
| K2b-04 | catalyst | required | tl_cl | 0 | (ASP only) |
| K2b-05 | catalyst | required | tl_pq | 0 | (ASP only) |
| K2b-06 | composite | anyvalid | none | 0 | CRQC, COMPOSITE |
| K2b-07 | composite | anyvalid | none | 1 | CRQC, COMPOSITE, COEXIST_CLASSICAL |
| K2b-08 | composite | required | local | 1 | (ASP only) |

| leafB | vb=ignore (default path) | vb=require (P2 reference) |
|---|---|---|
| revoked | ? | ? |
| expired | ? | ? |
| unknown (OCSP) | ? | ? |
| absent | ? | ? |
| valid (control) | ? | ? |

| Cell | Policy | seen_hybrid | Tamarin |
|---|---|---|---|
| K2d-01 | P0 (ignore) | 0 | V_IGNORE |
| K2d-02 | P1 (enforce_if_present) | 0 | V_ENFORCE_IF_PRESENT |
| K2d-03 | P2 (require) | 0 | V_REQUIRE |
| K2d-04 | P3 (continuity) | 1 | (ASP only) |
| K2d-05 | P3 (continuity) | 0 (first contact) | (ASP only) |


## 4. KAT-3: S/MIME "every valid path to the CEK" and the authentication dual

| Vector | Recipient paths (type, certificate valid?) |
|---|---|
| o1 | mlkem ✓ |
| o2 | mlkem ✓, mlkem ✓ |
| o3 | rsa_kt ✓ |
| o4 | mlkem ✓, rsa_kt ✓ |
| o5 | hybrid_kem ✓ (approved) |
| o6 | hybrid_kem ✓, ecdh_ka ✓ |
| o7 | mlkem ✓, unknown_oid ✓ |
| o8 | mlkem ✓, rsa_kt ✗ (certificate invalid) |
| o9 | malformed |
| o10 | hybrid_kem ✓ (not approved) |
| o11 | mlkem ✓, hybrid_kem ✓ (approved) |
| o12 | ecdh_ka ✓, rsa_kt ✓ |

| Flag |
|---|
| MIXED |
| PQ_ONLY |
| HYBRID_KEM |

| Pilot counterpart | tl_class | expect | coexist |
| --- | --- | --- | --- |
| V1 base | cl | 0 | 1 |
| V2 expectTL | cl | 1 | 1 |
| V3 tlPQ | pq | 0 | 1 |
| V4 tlPQ_expectTL | pq | 1 | 1 |
| V5 tlPQ_nocoexist | pq | 0 | 0 |
| V6 tlClassical_nocoexist | cl | 0 | 0 |




## Values to be derived (vocabulary; the mapping is NOT given)

- **KAT-1 (every cell):** ASP ∈ {SALDIRI, YOK} (attack, no attack); Tamarin `a_rrset_authentic` ∈ {verified, falsified}.
- **KAT-2a (every row, separately for each value in `pqev`):** `decision(ee,·)` ∈ {accept_classical, accept_hybrid, reject, indeterminate}.
- **KAT-2b (every cell):** ASP ∈ {SALDIRI, YOK}; if Tamarin flags are given, `cert_authentic` ∈ {verified, falsified}.
- **KAT-2c (leafB × {vb=ignore, vb=require}):** decision ∈ {accept_classical, accept_hybrid, reject, indeterminate}.
- **KAT-2d (every cell):** ASP decision ∈ {accept_classical, accept_hybrid, reject}; if Tamarin is given, ∈ {verified, falsified}.
- **KAT-3a (o1…o12):** `out` ∈ {pqc_protected, hybrid_protected, classical_only, unsafe_mixed, unknown, invalid}; accept strict ∈ {0,1}; accept transitional ∈ {0,1}.
- **KAT-3 Tamarin `cek_secrecy` (flags MIXED, PQ_ONLY, HYBRID_KEM):** ∈ {verified, falsified}.
- **KAT-3b (V1…V6):** under `qday=0` (all classical keys broken) the dynamic `attack` ∈ {SALDIRI, YOK} and the static `violation` ∈ {0,1}; in addition the dynamic `attack` under `qday=200` (no CRQC); Tamarin `claims_unforgeability` ∈ {verified, falsified}.
