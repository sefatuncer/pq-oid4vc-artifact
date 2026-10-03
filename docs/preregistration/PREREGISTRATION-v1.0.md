# Pre-registration: *When Does Each Link Break?* (PQ-OID4VC, Paper 1)

| Field | Value |
|---|---|
| Status | FROZEN |
| Version | 1.0 |
| Freeze date | 2026-10-03 |
| Scope | Governs the library measurement (contribution C3, research question RQ3, hypothesis H6) and its analysis. The term "pre-registered" applies to this measurement only, from the public freeze of this document [Amendment 11 (2026-10-01)]. For the formal part (contributions C1 and C2, RQ1, RQ2, H0–H5) the document records the rules, predictions and falsification conditions. Their expected verdicts were fixed and hashed before the runs (internal record), and their results were known at freeze (Section 12) |
| Repository | https://github.com/sefatuncer/pq-oid4vc-artifact |
| Source draft | Draft v0.11 (2026-09-26, Turkish), repository history commit `47d5bbb`, path `00-on-kayit/ON-KAYIT-TASLAK.md` (removed from the working tree in commit `fa44c06`) |
| Draft anchors | Anchors 1–9, 2026-09-24 to 2026-09-26 (Appendix C) |
| Amendments after the draft | Amendment 10 (2026-10-01): control-arm fallback label ES384 and battery v1.4. Amendment 11 (2026-10-01): narrowing of the C3 analysis (T1 the only confirmatory test) and wording for the formal part. Both were written before any battery vector was run on a target and are integrated directly into this version |
| Pre-freeze decisions | `experiment/runs/DECISIONS-PREFREEZE.md`, decisions D1–D7 (2026-10-01), D8 and D9 (2026-10-03). Decision D4 is Amendment 10 |
| Repository snapshot | Paths refer to the repository at the freeze commit (tag `prereg-v1.0`). Older folder and file names, which some recorded hashes and commit messages still use, are mapped in `docs/PATHS.md` and `docs/PATHS.tsv` |
| Prepared by | The study team |

**How to read this document.**
- This version integrates the amendments of the draft (Amendments 1–9, draft Sections 2A–2I) and Amendments 10 and 11, made after the draft, into the main text. Where an amendment changed a rule, the rule appears in its amended form and carries a tag. Superseded wording is kept only where it is needed to understand a change.
- Tags:
  - **[Amendment n (date)]** or **[Amendment n, item k (date)]**: text integrated from draft amendment n. Items of Amendment 1 keep their original labels Ö1–Ö12, because repository files cite them.
  - **[Amendment 10 (2026-10-01)]**: the amendment made after the last draft version (decision D4 of `experiment/runs/DECISIONS-PREFREEZE.md`, commit `7143e8c`). It was written before any battery vector was run on a target.
  - **[Amendment 11 (2026-10-01)]**: decisions of the study lead after an internal methodological review: T1 stays the only confirmatory test, T2–T5 become descriptive, the historical baseline and the known-bug recall are removed, an interpretation note for L4c and a rule for incidental rejection are added, second attempts under the evidence rule are restricted, the reference verifiers and the end-to-end demonstration are removed, and the formal part is described as "expected verdicts fixed and hashed before the runs (internal record)". Written before any measurement data existed: only the pre-freeze validity gate had been run.
  - **[Decision Dk (2026-10-01)]**: pre-freeze decision k from `experiment/runs/DECISIONS-PREFREEZE.md`.
  - **post-result**: the text was written after the relevant formal results had been seen.
  - **[Design v3 §x]**: taken verbatim from version 3 of the study design document, the binding design from which RQ1–RQ3 and H0–H6 come.
  - **[Operational]**: operational definition of this document.
  - **[Draft parameter]**: a value that the draft left open until freeze. It is final in this version.
  - **[computed]**: computed by the study team with the Python standard library and re-verified by the statistics package (Section 7.18).
  - **estimate**: subjective estimate.
  - **[CHECK (keep): …]**: a point that the study team or the authors must settle before freezing. No such marker may remain in the frozen file.
- Appendix C lists every amendment with its date, anchor commit and what was known when it was written. Appendix D shows every change to the formal part (H0–H5) since draft anchor 1, as the draft's freeze procedure requires.

**Notation.** Several code families overlap. They are always written with a qualifier.
- "Attacker S1–S3" are the attacker classes of the threat model. "Strategy S0–S8" are the baseline strategies.
- The metamorphic relations M1–M3 of Design v3 §7.17 are written **MR1–MR3** (with MR4 added), because M1–M5 are the baseline metrics. Mechanism classes are written M-a to M-h.
- "Rule R1–R7" are the Tamarin rule schemas. The study plan's risk register R1–R24 is not used here.
- "Policy P0–P4" are verifier policies. The pilots of the external audit are written "pilot P1" to "pilot P5".
- "Treatment arm TK1–TK3" are treatment classes. "Test T1–T5" are the statistical analyses of C3: T1 is the only confirmatory test, T2–T5 are descriptive [Amendment 11 (2026-10-01)].
- "Battery case K1–K11" are cases of the test battery. "Inclusion criterion K1–K8" are the sample inclusion criteria.
- "Evidence component D1–D9" (Section 6.2), "exclusion reason D1–D9" (Section 7.2) and "pre-freeze decision D1–D9" are distinct families.

---

## 1. Purpose and scope

### 1.1 Purpose
This document fixes four things before the results they govern are seen:
1. the hypotheses and their falsification conditions,
2. the operational definitions,
3. the analysis plan,
4. the decision rules (gates and the interpretation of every outcome).

### 1.2 Two parts: expected verdicts fixed before the runs, and a pre-registered measurement
- **Formal part (RQ1, RQ2, H0–H5, contributions C1 and C2).** Deterministic. Its evidence standard is in Section 6. This part was executed **before** the freeze (Steps 3–8). Its predictions and falsification conditions were therefore fixed by the draft anchors: anchor 1 recorded them, and anchor 3 locked the gate criteria, the support and falsification rules of H0–H5, the pass criteria of the known-answer tests and the primary configuration [Amendment 3, item 1 (2026-09-24)]. Appendix D shows, as a difference, every change made to the H0–H5 rules since draft anchor 1. **Wording** [Amendment 11 (2026-10-01)]: for this part the document speaks of "expected verdicts fixed and hashed before the runs (internal record)". The record is the project's local version history (its commit messages were later rewritten, Section 13.8) and has no external timestamp, so the term "pre-registered" is not used for the formal part.
- **Empirical part (RQ3, H6, contribution C3).** Inferential, with one confirmatory test (T1) and descriptive analyses. It is frozen before the C3 measurements begin, and the frozen state is published as a tag of the public repository (Section 11). The term "pre-registered" applies to this part only, from that public freeze [Amendment 11 (2026-10-01)].

### 1.3 What this freeze governs
This freeze governs the library measurement (Step 10) and its analysis: the target list, the battery, the oracle, the adapters and their calling conventions, the outcome variables, the confirmatory test and the descriptive analyses, the thresholds, the sensitivity analyses and the reporting rules. For the formal part it records the rules under which the verdicts were reached. Those verdicts were known at freeze and are reported as such in Section 12.

**Guiding principle for the freeze** [Amendment 11 (2026-10-01)]: the only confirmatory element of C3 is T1/H6 and its computation chain: Y_L4 with its two forms L4m and L4c (Section 5.13), the evidence rule (Section 5.14), n_eff (Section 7.5), the thresholds of Appendix A, sensitivity analyses (i) and (ii), and the support and falsification rules (Sections 7.14 and 9.3). Everything else in C3 is descriptive. Descriptive outputs are computed by the frozen scripts as written and are labelled descriptive.

### 1.4 Work steps referred to in this document
| Step | Content |
|---|---|
| 1 | Specification corpus, traceability matrix (`traceability/`), threat model |
| 2 | Tool chain acceptance |
| 3 | ASP system model and z3 cross-check |
| 4 | Tamarin rules R1–R5 |
| 5A | Tamarin rules R6 and R7, ProVerif second opinion |
| 5B | Stratified ASP-to-Tamarin abstraction sample |
| 6 | Known-answer tests |
| 7 | Mechanism models |
| 8 | Strategy comparison, H0–H5 verdicts, scientific gate |
| 9 | C3 preparation: 9a inventory and selection, 9b test battery, oracles, adapters, statistics scripts |
| 10 | C3 measurement and H6 analysis |
| 11 | End-to-end emulator demonstration (removed by Amendment 11) |
| 12 | Deployment constraint table (M3 limits) |

### 1.5 Evidence principle
Only tool output counts as evidence. Every number reported in the paper comes from a script in the repository. A judgement that is not backed by tool output is at most a hypothesis to be checked.

### 1.6 Known limitations of the independent derivations [Amendment 11 (2026-10-01)]
Several checks are described in this document as independent: the z3 encoding that cross-checks the ASP model, the two oracle derivations A and B, the blind known-answer values, the novelty review and the internal methodological review behind Amendment 11. Each was produced in a separate session that did not see the outputs it was checked against. All of them, however, were produced by the same study team with the same working methods and tool chain. They are not independent in the sense of separate research teams, so common-mode errors are possible, for example the same misreading of a specification clause in both oracle derivations. The verdicts do not rest on these judgements. They rest on tool outputs (solver, prover and script results) that can be re-run from the repository, and every disagreement between derivations is reported.

---

## 2. Research questions [Design v3 §7.6, verbatim]

- **RQ1 (formal, time- and channel-resolved).** For each security goal (G1–G4), coexistence phase, CRQC regime (τ) and anchor assumption (fresh, pinned or cached TL):
  - What are the minimal PQ cut sets and the migration order?
  - Which pulled artefact can be substituted by PQ-authenticated transport?
  - Are the published orderings (S0–S6) sufficient and economical?
- **RQ2 (mechanism).** Which expectation-conveyance mechanisms (M-a…M-f) satisfy G5 under the threat model? Which is the minimal robust mechanism? Are its components (authentication, freshness, monotonicity, per-entity scope) necessary, and what do they cost?
- **RQ3 (feasibility).**
  - Can JOSE/COSE/SD-JWT libraries and reference verifiers express, and apply by default, the "required algorithm set" policy that the robust mechanism needs (L0–L5)?
  - Which failures are PQ-specific? Can they be exploited end to end under CRQC emulation?
  - How do deployment limits (headers, QR) constrain where the mechanism can be placed?

Note. The mechanism set of RQ2 was extended to M-a…M-h, M-b0 and M-e′ by Ö4 (Section 5.11). The text of RQ2 is kept verbatim. RQ3 is also kept verbatim, but Amendment 11 removed the reference verifiers and the end-to-end demonstration under CRQC emulation (decision of the study lead, not needed for any claim). RQ3 is therefore answered for libraries only, and exploitability is argued from the battery outcomes and the threat model.

---

## 3. Hypotheses [Design v3 §7.7, with the amendments marked]

| Code | Prediction | Falsification condition | Type |
|---|---|---|---|
| H0 | The model is executable. Under the "at least one valid" policy a stripping trace appears. When each protection is removed, a trace appears (mutation lemmas) | If no trace appears, the model is faulty | Health check, not a hypothesis |
| **H1** (channel substitution) | Pulled artefacts (TL/LoTE, status list, metadata) can drop out of the set of PQ object signatures only on one condition: they are fetched fresh from the authoritative source over a transport whose **server authentication is PQ**. Transferred artefacts (credential, `x5c`, KB-JWT, request object) admit no substitution. Hence the minimal set is a cut set and depends on the PQ status of the WebPKI | A transferred artefact admits substitution, or the substitution also holds with classical transport authentication | Formal |
| **H2′** (key exposure window) [Ö1, Amendment 1 (2026-09-24)] | The minimal PQ set and the order change with the relation between the exposure window of the signing key and τ. The exposure window is the time from Q-day (or from the observation of the public key) to the last moment at which the key is accepted. **The validity period of the artefact (token) alone is not decisive.** Short-lived tokens signed with a long-lived classical key can be forged fresh at will once the key has been extracted. Keys with a short exposure window can stay outside the minimal set in slow regimes and enter it in the fast regime. Such keys are either rotated, or ephemeral per token and bound to a long-lived PQ identity (the "transient" logic of Anchuri et al.). Variants for the status-list signing key: V1 long-lived, V2 daily rotation, V3 ephemeral per token with binding to a PQ identity. The same distinction applies to the issuer signing key and to the device key (H5). **Support:** for at least one goal, the set or the order changes between at least two τ regimes **and** the change is explained by the key window | Either (i) with the key window fixed, the token lifetime changes the set (prediction: it does not), or (ii) the key window changes the set in no τ regime | Formal and sensitivity |
| **H3** (expectation conveyance) | During coexistence, no verifier policy can satisfy G5 without an authenticated per-entity expectation. M-a and M-b yield downgrade traces. M-f is sufficient, and each of its components (authentication, freshness or pinning, monotonicity, per-entity scope) is necessary | An unauthenticated mechanism satisfies G5, or a component of M-f turns out to be unnecessary. In the second case the mechanism is simplified, and the result is still publishable | Formal |
| **H4** (limit of published orderings) | In at least one goal × phase × regime cell, the "root/device first" order (strategy S5) is **insufficient** or **wasteful** relative to the computed minimal order (strategy S7). Candidate cells: RP authentication in A.3.2.2, status-list delegation, WebPKI | S5 equals S7 in every cell. In that case the intuition is confirmed and reported, but the novelty weakens and the target journal changes (Design v3 §7.15) | Formal |
| **H5** (harvest-and-forge) | As long as the WSCD key stays classical, single-use batch issuance does not prevent presentation forgery after a CRQC. Only the validity period bounds it | Enforcing single use at the verifier prevents the forgery in the model | Formal |
| **H6** (expressiveness) | Among the n = 31 targets selected before the measurement [Amendment 2 (2026-09-24), Amendment 8, item 17 (2026-09-26)], of which 30 enter the primary analysis [Amendment 10 (2026-10-01)], the number of targets that can express the "required algorithm set" policy by default through their general API (L4) stays below the pre-announced threshold. Failures are split into the "at least one valid" and "all present valid" modes. The control–treatment comparison shows which of them are PQ-specific | X ≥ u(n_eff) targets satisfy L4 (one-sided binomial, α = 0.05, Section 7.17 and Appendix A). For the primary n_eff = 30 [Amendment 10 (2026-10-01)]: at least 20 of 30 | Empirical (the only confirmatory test, T1) |

**Notes [Design v3 §7.7].**
- Size thresholds are deterministic. They are reported as a table and are not a hypothesis (Design v3 §7.17).
- The negative outcome of every hypothesis is also publishable, but it changes the choice of journal (Design v3 §7.15).

**Superseded wording, kept for traceability.**
- **H2 (Design v3).** Prediction: "The minimal set and the order change with the τ regime and the acceptance windows. Short-lived pulled status tokens and short-lived device keys stay outside the set under a slow CRQC and enter among the first links to break under a fast CRQC." Falsification: "The order does not change across all regimes and windows." H2 was replaced by H2′ as a reasoned departure [Ö1, Amendment 1 (2026-09-24)], because the validity of a token is not decisive when a long-lived key signs it (Section 5.5).
- **H6 (Design v3).** "Among the pre-registered n≈30 targets …". Falsification: "At n = 30, at least 20 of 30 targets satisfy L4." The sample size became n = 31 through the quota rule of Amendment 2. Amendment 10 excludes one target (SDJWT-021) from the primary H6 analysis, so the primary n_eff is 30 before indeterminate targets are removed, and the thresholds are again ≤ 10 and ≥ 20. In every case the thresholds follow from the rule of Appendix A applied to n_eff.
- "By default" in H6 is read as: expressible through the library's own documented mechanism without changing code. Being enabled by default is reported separately as L5 [Ö10, item 2, Amendment 1 (2026-09-24)].

---

## 4. Operationalisation of the hypotheses [Operational]

For each hypothesis: what is computed, what kind of evidence it rests on, and the decision rule. Definitions are in Section 5. Interpretation and reporting are in Section 9.2.

### 4.1 H0 (health check)
- **Computed:**
  - (a) the `executable` (exists-trace) health lemmas in every Tamarin model,
  - (b) a stripping trace under policy P0 and coexistence (a violation in ASP, a concrete trace in Tamarin),
  - (c) the mutation score (Section 5.17).
- **Decision:** H0 holds if (a) is 100 % "verified", (b) a trace exists and (c) the score is at least 90 %. If (a) or (b) fails, the model is considered faulty and H1–H5 are not judged.
- **Frozen reading of (a)** (interpretation recorded in Section 13.9): the literal rule is "100 % verified". The variant plans (`models/tamarin/betik/varyantlar.tsv`, `models/mechanisms/on_kayit_varyantlar.tsv`) fixed four `executable_learn` lemmas as false before the runs, for variants without an expectation channel. Condition (a) is therefore read as "every health lemma has the verdict fixed before the runs": 554 of 554 as expected, of which 550 verified.

### 4.2 H1 (channel substitution)
- **Computed:** for each pulled artefact a ∈ {LOTL, TL/LoTE, signed issuer metadata, Type Metadata, status-list token} and each goal G that a supports, the minimal sets are compared under two transport regimes:
  - (i) fresh fetch from the authoritative source with PQ server authentication,
  - (ii) fresh fetch with classical server authentication (even with hybrid key exchange, for example X25519MLKEM768).
- **"Substitution holds"** means: under (i) there is at least one minimal set that does not contain `pq(a)`.
- **Transferred artefacts** (credential, `x5c`/CA, issuer certificate, KB-JWT, the by-value form of the request object, WUA, RP access certificate): the same query is asked under both regimes.
- **Support:** under (i) substitution holds for at least one pulled artefact, under (ii) it holds for none, and it holds for no transferred artefact.
- **Falsification:** one of the two conditions of Section 3 occurs.
- **Evidence:** ASP scan, rule R3 (Tamarin) and sampled instances [Design v3 §7.13]. The emulator demonstration of Design v3 (acceptance of a forged TL with a forged TLS certificate) was removed by Amendment 11.
- **Pre-specified design** [Amendment 3, item 2.4 (2026-09-24)]: WebPKI {classical, PQ} × channel labels. All other parameters at their primary values. All cells of this design are primary.

### 4.3 H2′ (key exposure window) [Ö1, Amendment 1 (2026-09-24)]
- **Computed:** minimal sets and optimal order over the A5 grid: key window × token lifetime × τ.
- **Support:** for at least one goal, the set or the order changes between at least two τ regimes **and** the change is explained by the key window.
- **Falsification:** either (i) with the key window fixed, the token lifetime changes the set, or (ii) the key window changes the set in no τ regime.
- **Evidence:** ASP A5 grid and rule R6 Tamarin instances.
- **Pre-specified design** [Amendment 3, item 2.4 (2026-09-24)]: key mode {V1, V2, V3} × nominal τ (3 values). The τ grid is reported as sensitivity. All cells of this design are primary.
- Superseded operationalisation of H2 (draft Section 3.3): minimal sets and optimal order over the τ grid and the window grid. Support required that the changing elements include a pulled status-token signer with a short trust window or a short-lived device key. Falsification: order and set identical across all regimes and windows.

### 4.4 H3 (expectation conveyance)
- **Computed:**
  - (a) in ASP, under policies P0–P3 (classical channel) and in the coexistence phases, the absence of a solution for G5 (UNSAT) or a Tamarin trace,
  - (b) a trace of the G5 lemma for M-a and M-b,
  - (c) an all-traces proof of the G5 lemma for M-f,
  - (d) ablation A3: a trace when each of the four components of M-f is removed.
- **Support:** all of (a)–(d).
- **Falsification:** one of the two conditions of Section 3. Under the second condition (an unnecessary component), M-f is simplified and (c) is proved again for the simplified mechanism.
- **Positioning** [Ö2, Amendment 1 (2026-09-24)]: the impossibility half of H3 is not presented as a new claim. It is reported as an instance of the statement "no policy can satisfy G5 without an authenticated expectation" as in Bkakria (2026), Theorem 1, and its counterpart in RFC 9955.
- **Outcome of the falsification rule** [Amendment 4, item 9 (2026-09-24), post-result, written after the Step 5A results]:
  - Observation: MONOTONE and SUNSET_CHECK were **unnecessary** in the online and pinned settings (`A_online_no_monotone`, `A_online_no_sunset`, `A_pinned_min`: V/V/V). In the offline setting both are necessary (`M_off_monotone`, `M_off_sunset`).
  - This triggers the second falsification condition of H3. Its consequence, fixed beforehand, applies: M-f is simplified.
  - **Simplified M-f.** Core: authoritative third party + PQ authentication + per-entity scope + current value (fresh or pinned). Offline extension: monotone verifier state + expiry of the classical key at sunset.
  - Re-proof of (c): the pinned core is covered by `A_pinned_min` (Step 5A, V/V/V). The expected verdicts of the online core were fixed at anchor 4: `models/tamarin/betik/on_kayit_h3_sadelestirme.tsv`, variant `S_online_core` (PQ_CHAN, FRESH, PER_ENTITY), SHA-256 `c8fe3ee5efcb7ec6dff77ed4ed2c55c5b25401413022d3c7ceec5ceef273a71f` (2026-09-24 19:53:06). Expectation: Gm = V, Gt = V, NR = V, FCD = F, M_rollback = F, M_after_sunset = F, health lemmas V.
  - **The text of H3 is not changed.** Reporting: (a) and (b) await Steps 3 and 7. (c) for the full and the simplified M-f. (d) context-dependent, falsification condition 2.
- **Qualifier** [Amendment 4, item 13 (2026-09-24)]: the R7 model of M-f has no certificate path. The claim "M-f is sufficient" is therefore read as "excluding the path dimension" until Step 7 concludes (Section 12.1 reports the Step 7 result).

### 4.5 H4 (limit of published orderings)
- **Computed:** strategy S5 against strategy S7 in the 36 main cells (G1–G4 × Φ1–Φ3 × 3 τ) and in the anchor variants.
- **Support:** at least one cell is "insufficient" or "wasteful" (Section 5.21, condition 2a), reproduced by at least one Tamarin instance.
- **Falsification:** S5 = S7 in every cell (both the secured goals and M2).
- **Pre-specified design** [Amendment 3, item 2.4 (2026-09-24)]: only the primary configuration, plus the named cells of Ö3 (Section 5.21).
- **Counting** [Amendment 8, item 3 (2026-09-26), post-result, written after the Step 3 results, strict reading]: see Section 5.21.

### 4.6 H5 (harvest-and-forge)
- **Model:** classical WSCD key. Single-use batch issuance (a separate `cnf` key per credential). At least two verifiers. No shared state between verifiers, as unlinkability requires. Attacker S3 records the presented credential and the `cnf` public key. Attacker S2 extracts the key τ later.
- **Support:** a forgery trace appears if and only if τ is shorter than the remaining validity of the credential. Single-use issuance does not block the trace.
- **Falsification [Design v3]:** enforcing single use at the verifier prevents the forgery in the model. Operational reading: at the enforcement level foreseen by the specifications, without shared state between verifiers.
- **Boundary case:** the variant with a replay cache at a single verifier is reported separately. It does not falsify H5 and is discussed as a boundary condition.
- **Pre-specified design** [Amendment 3, item 2.4 (2026-09-24)]: device key window {1 day, 30 days} × nominal τ (3 values). One day is the short-lifetime option of the ARF.
- **Qualifier** [Amendment 4, item 15 (2026-09-24), post-result, written after the Step 5A results]: the relevant window is the exposure window of the device key, that is validity × reuse. Single use does not prevent forgery (`M_single_fast` = F). Protection requires both a validity window shorter than τ **and** a device key per credential. The text of H5 is not changed.

### 4.7 H6 (expressiveness)
- **Primary outcome variable:** Y_i = 1 if and only if target i can express the "required algorithm set" semantics (L4) through its documented general API (Section 5.13).
  - Library code is not changed.
  - No custom verification loop is written.
  - L4 is measured in the **control arm** (second algorithm EdDSA, or the fallback label Ed25519 or ES384 of Section 7.7). This separates API capability from PQ support.
  - **Two forms of L4** [Amendment 2, item 6 (2026-09-24)]: Y_i = L4m if the target supports multi-signature objects, otherwise L4c. The form applied is reported per target. The same rule applies to COSE: a target that supports COSE_Sign uses L4m, a target that supports only COSE_Sign1 uses L4c [Amendment 9, item 3 (2026-09-26)].
- **Test:** one-sided exact binomial test on X = Σ Y_i (Section 7.10, T1).
- **Support:** X ≤ c(n_eff).
- **Falsification:** X ≥ u(n_eff).
- **Otherwise:** "inconclusive".
- **Primary n_eff = 30** before indeterminate targets are removed [Amendment 10 (2026-10-01)]: of the 31 targets, SDJWT-021 is excluded from the primary H6 analysis because no second classical algorithm passes its validity gate (Section 7.7).
- **For n_eff = 30:** c = 10, u = 20 [Appendix A, computed and verified, P(X ≤ 10) = 0.0494. These are also the thresholds of Design v3 §7.12].
- If n_eff changes (indeterminate targets, adapter invalidity), c and u are read from Appendix A for the final n_eff.
- Robustness rules for support and falsification: Section 7.14. Sensitivity analysis for SDJWT-021: Section 7.14.
- **Control arm** [Amendment 10 (2026-10-01)]: Y_i is determined in the control arm with the first label in the order EdDSA, Ed25519, ES384 that passes the target's validity gate (Section 7.7). This resolves the case of the 15 targets that support neither EdDSA nor Ed25519.

---

## 5. Definitions

### 5.1 Artefacts and channel classes [Design v3 §7.4 + Operational]
The channel class is assigned by **how the artefact reaches the verifier**:
- by value, brought by the presenting party: **transferred**,
- fetched by the verifier or the wallet from the authoritative source: **pulled**,
- provided through out-of-band configuration: **pinned**,
- a time-limited copy of an earlier fetch: **cached**.

If an artefact has several delivery forms (for example a request object by value or through `request_uri`), each form is modelled as a separate sub-case and H1 is evaluated for each sub-case. The assignments rest on the normative sentences of the Step 1 traceability matrix. If the matrix shows something different, the matrix prevails and the difference is recorded.

| # | Artefact | Default channel class | Signer (draft) | Note |
|---|---|---|---|---|
| 1 | LOTL | pulled (pinned or cached according to the anchor assumption) | European Commission (pilot P5: RSA-4096) | Trust root |
| 2 | National TL/LoTE | pulled (pinned or cached variant) | TL operator (107 of 107 signers classical) | |
| 3 | CA (`x5c`) | transferred | CA listed in the TL | composite -04 §6.2 |
| 4 | Issuer certificate | transferred (inside `x5c`) | CA | |
| 5 | Signed issuer metadata | pulled | Issuer | M-e |
| 6 | Type Metadata | pulled | Issuer or type owner | |
| 7 | Credential (SD-JWT VC) | transferred | Issuer | G1 |
| 8 | Status-list token | pulled | Issuer or authorised status signer | G3, "status-list delegation" |
| 9 | Wallet attestation (WUA) | transferred (in the issuance flow, from wallet to issuer) | Wallet provider | Confirmed with the Step 1 matrix |
| 10 | WSCD device key and KB-JWT | transferred | WSCD | G2, H5 |
| 11 | RP access or registration certificate | transferred (in the request object). Pulled sub-case if fetched from a register | RP access certificate CA | G4, carrier of M-f |
| 12 | OID4VP request object | transferred (by value). Pulled sub-case if fetched through `request_uri` | RP | G4, M-a, A.3.2.2 |
| 13 | Transport layer (TLS/WebPKI) | transport (the channel of pulled artefacts) | WebPKI CAs | Hybrid key exchange gives PQ confidentiality. Server authentication is classical unless a PQ certificate is used [Design v3 §7.4] |

**Extensions** [Ö7, Amendment 1 (2026-09-24)]:
- A09 is split into A09a WIA (< 24 h) and A09b KA (long-lived). Both are presented only to the issuer.
- Three edge artefacts are added: Access CA CRL/OCSP, JWT VC Issuer Metadata or JWK Set, and AS metadata.
- Channel labels are added: `sunan-ucundan-cekilen` (pulled from the presenter's endpoint) and `yalniz-tasima` (transport only).

**Decision nodes** [Amendment 3, item 2.1 (2026-09-24)]: 13 core artefacts. With A09 split this gives 14 nodes. With the three edge artefacts the model has **17 decision nodes**. The 36 cells of M1 (G1–G4 × Φ (3) × τ (3)) are computed in this 17-node model.

**ASP operational mapping** [Amendment 8, item 5 (2026-09-26), post-result, written after the Step 3 results]:
- A09a is the wallet instance key bound by the WIA. A09b is the wallet provider signing key.
- A13 is PQ server authentication on the transport of pulled artefacts together with rejection of the classical chain.
- For unsigned edge artefacts, "PQ" means object-level PQ binding. E_CRL is a separate node.
- The OJEU-to-LOTL channel is anchor pinning (rule R5) and is **outside the scope of M-f**.
- **Addition after the results were known** (2026-10-01, recorded in Section 13.9): the OJEU expectation hook (the ASP note of 2026-09-25) was brought into the scope of M-f, contrary to the last bullet. The primary results do not change. The effect appears only in the one-at-a-time sensitivity run `webpki_pq_birlikte`. No verdict changes.

### 5.2 Coexistence phase Φ [Ö10, item 1, Amendment 1 (2026-09-24): approved]
The phase states **in which artefact classes the classical alternative is still accepted**. It extends the `coexist`/`post` pair of pilot P2.
- **Φ1, full coexistence:** the classical alternative is accepted in all signed artefact classes (legacy windows open).
- **Φ2, partial coexistence:** the classical alternative is not accepted in the anchor and PKI classes (LOTL, TL/LoTE, CA). It is accepted for leaf artefacts (credential, metadata, Type Metadata, status list, WUA, KB-JWT, RP certificate, request object).
- **Φ3, post-coexistence (sunset complete):** no classical alternative is accepted for any migrated entity. Artefacts that have not migrated stay classical.

In analyses of attacker S2, Q-day is assumed to have occurred. Attacker S1 is independent of the phase.

### 5.3 Attacker classes S1–S3 [Design v3 §7.4 + Operational]

| Code | Attacker | Capability (operational) | Capabilities not given |
|---|---|---|---|
| S1 | Network attacker (Dolev–Yao) | Reads, deletes, modifies and replays messages. Strips signatures and changes negotiation headers. Cannot inject content into an authenticated transport channel unless the server key is compromised. Has no quantum capability | Keys of honest parties, physical access |
| S2 | CRQC(τ, k) | Everything S1 can do. After Q-day, for every classical public key K it observes, it obtains sk(K) τ after the observation. At most k keys per window | PQ keys (EUF-CMA assumption for ML-DSA and SLH-DSA), hash functions |
| S3 | Harvest-then-forge | Records public keys (including `cnf`) and artefacts today. After S2 has extracted the key, forges with the recorded context | Same as S2 |

**k grid** [Draft parameter, Ö8, Amendment 1 (2026-09-24)]: k ∈ {1, 3, unbounded}. Primary analysis: k = unbounded (worst case). k = 1 and k = 3 are sensitivity analyses.

**Assumptions [Design v3 §7.4, verbatim]:**
- ML-DSA and SLH-DSA are EUF-CMA secure against a quantum attacker. Hash functions are secure.
- The secure element is not physically compromised.
- TL/LoTE operators, issuers and RPs are honest. Insider attackers are out of scope.
- The verifier works correctly apart from the policy under test. Its deviations from policy are what C3 measures.
- The verifier's clock is correct. The opposite case is modelled separately as a relaxation.
- Hybrid key exchange (X25519MLKEM768) gives PQ confidentiality. Server authentication, however, is classical unless a PQ certificate is used. The WebPKI dependency comes from this.

**Out of scope [Design v3 §7.4, verbatim]:**
- harvest-now-decrypt-later confidentiality of presentations (mentioned only as motivation),
- unlinkability and privacy,
- availability and DoS,
- side channels,
- a malicious issuer or TL operator,
- mdoc (ISO/IEC 18013-5 is not freely available, only the note "COSE_Sign1, single signer" remains),
- physical BLE/NFC tests.

### 5.4 τ regimes [Design v3 §7.4 + Draft parameter]

| Regime | Basis [Design v3] | Nominal value | Sensitivity grid |
|---|---|---|---|
| fast | Babbush et al. 2026: 256-bit ECDLP in "minutes" | 10 minutes | {1, 10, 60} min |
| medium | Cain et al. 2026: P-256 in "a few days" | 3 days | {1, 3, 7, 10} days [Ö8, Amendment 1 (2026-09-24), adds the 10-day value from the body of Cain et al.] |
| slow | Häner et al. 2026: secp256k1 in about 25.7 days | 26 days | {14, 26, 60} days |

- τ is scanned as a single parameter per key. No separate τ is defined per algorithm family.
- For RSA keys, Gidney 2025's estimate for RSA-2048 ("less than a week") falls into the medium regime (estimate). There is no separate estimate for RSA-3072/4096. They are scanned with the same grid, and this is reported as a limitation.
- The lower end of τ_fast is set by the clock skew allowance (minutes) [Ö8, Amendment 1 (2026-09-24)].

### 5.5 Windows [Operational]
- **W_trust(K):** the time during which verifiers treat the classical key K as trusted. From the first publication of the public key to the end of trust (certificate expiry, removal from the TL, revocation).
- **W_accept(a):** the time during which artefact a is accepted (validity, TTL, cache, freshness definition).
- **Forgeability rule (the core of rule R6):** attacker S2 can forge an artefact signed with the classical key K only if τ < W_trust(K). In the worst case the attacker observes K at the start of its trust window.
- **Key lifetime versus token lifetime:** if a short-lived token (for example a status-list token) is signed with a long-lived key, W_trust(K) is decisive, not the token's TTL. The "short-lived status token" of the original H2 therefore means, operationally, "a status signer with a short trust window (for example an authorised signer with a short-lived certificate)".
- **Device key (H5):** W_trust(K_cnf) is the remaining validity of the credential that binds the key.
- **Source of window values:** normative or documented values from the traceability matrix. A known value: LOTL sequence 394, published 2026-09-10, next update 2027-03-10 (6 months, pilot P5). Where the matrix gives no value, a logarithmic grid is used [Draft parameter]: {1 hour, 1 day, 7 days, 30 days, 180 days, 1 year, 5 years}.
- **Fixed windows** [Ö8, Amendment 1 (2026-09-24)]: three windows are fixed: TL/LoTE ≤ 6 months, WIA < 24 h, the short-lived credential option ≤ 24 h. All other windows are parametric (Section 6.3, primary configuration).

### 5.6 Anchor assumptions [Design v3 §7.6 + Operational]
- **Fresh:** the TL/LoTE is fetched from the authoritative source at verification time (or within its TTL). At fetch time it is subject to the rules for transport authentication and object signatures.
- **Pinned:** the anchor key is configured out of band and the attacker cannot change it. This cuts the chain (rule R5).
- **Cached:** the last fetched copy is used for W_cache. The copy is subject to the transport and signature rules that held when it was fetched. A copy fetched before Q-day is authentic for the lifetime of the cache.

Main analysis: fresh. The pinned and cached variants are reported separately.

### 5.7 Security goals G1–G5 [Design v3 §7.4 + Operational lemma form]

| Goal | Definition [Design v3] | Operational lemma | ASP counterpart |
|---|---|---|---|
| G1 | claims unforgeability | ∀ I c #j. Accept(I, c)@j ⇒ ∃ #i. Issued(I, c)@i ∧ i < j | `ihlal(g1)`: active forgery in the credential or in the chain that validates it |
| G2 | presentation unforgeability (holder binding) | ∀ H c n aud #j. AcceptPresentation(H, c, n, aud)@j ⇒ ∃ #i. HolderSigned(H, c, n, aud)@i ∧ i < j | `ihlal(g2)`: active forgery of the KB-JWT |
| G3 | revocation soundness | ∀ c #j #r. Accept(c)@j ∧ Revoked(c)@r ∧ r + W_propagation < j ⇒ ⊥ | `ihlal(g3)`: active forgery of the status-list token |
| G4 | RP authentication (wallet side) | ∀ R q #j. WalletAcceptsRequest(R, q)@j ⇒ ∃ #i. RPCreated(R, q)@i ∧ i < j | `ihlal(g4)`: active forgery of the request object or of the RP certificate chain |
| G5 | downgrade resistance: "A migrated entity cannot be accepted with classical evidence only outside the legacy window it has announced." | ∀ E #j #m. AcceptClassicalOnly(E)@j ∧ Migrated(E)@m ∧ m < j ⇒ LegacyWindowOpen(E) at j | `ihlal(g5)`: classical-only acceptance of a migrated entity outside its window |

"Active forgery" means: the artefact can be forged **and** the forged artefact can be delivered to the verifier. In the substitution case defined by rule R3, the forged artefact cannot be delivered.

**Three forms of G5** [Ö11, Amendment 1 (2026-09-24), extended by Amendment 4, item 10 (2026-09-24)]:
- **G5-untimed:** classical evidence is never accepted (rules R2, R3, R7h).
- **G5-timed:** no classical acceptance after sunset (R7 `G5_timed`). Versioned expectation `none → pq_required → sunset`, lemmas `G5_timed` and `no_rollback`.
- **G5-migrated:** after migration, including first contact, no acceptance with classical evidence only (R7 `G5_migrated`).
- These lemmas were already in the Step 5A expectation file fixed before the runs. The 36 cells of M1 (G1–G4) are not affected. The freshness part of H1 is tested in R7 with the versioned expectation.

### 5.8 Policies P0–P4 [Design v3 §7.10(c) + Operational]

| Policy | Definition [Design v3] | Counterpart [Design v3] | Acceptance rule (operational) |
|---|---|---|---|
| P0 | any-valid | minimum of RFC 7515 §5.2 | Accept if at least one signature is valid |
| P1 | all-present-valid | ECCG AND | Accept if all present signatures are valid. Deletion of a signature (stripping) is not noticed |
| P2 | P1 + key–alg binding | RFC 8725 §3.1 | P1, and each signature is verified with the algorithm bound to its key |
| P3 | P2 + per-issuer set, from a classical channel | 8725bis §3.1, HAIP metadata | P2 + a per-issuer required set R_I. R_I is learned over a classically authenticated channel |
| P4 | P3, but from a PQ channel | M-f | P3 + R_I is learned over a PQ-authenticated, fresh or pinned, monotone channel |

**Policy parameters** [Ö9, Amendment 1 (2026-09-24)]: `iptal_denetimi` (revocation check), `cihaz_bagi` (device binding), `rp_auth_fail_open`, `wrprc_dogrulama ∈ {faz0, faz1}` (WRPRC validation phase), `ad_baglama ∈ {var, yok}` (replaced by `ca_baglama`, Section 6.3), `sdjwtvc_surum ∈ {-13, -19}`.
- Label of scenario (d): "Optional in the HAIP 1.0 profile (SD-JWT VC -13, MAY). Out of scope in -19. Ambiguous with the OID4VCI delivery format."
- Scope of `sdjwtvc_surum` [Amendment 4, item 7 (2026-09-24)]: the difference between -13 and -19 touches two places in practice: the scenario (d) vectors (status of the JSON serialisation) and VC11 (the `vc+sd-jwt` transition). The parameter is defined with this scope.

### 5.9 Strategies S0–S8 [Design v3 §7.10(a) + Operational]
Each strategy defines, for each phase, a set of PQ artefacts, a policy and an expectation channel. The exact assignments are written to the strategy file **before any comparison is run**. Every later change enters the deviation record.

| Code | Strategy [Design v3] | Source [Design v3] | Operational assignment |
|---|---|---|---|
| S0 | Status quo: all links ES256/P-256 | HAIP 1.0 | PQ set ∅, policy P0/P1, no expectation channel. Redefined [Ö5, Amendment 1 (2026-09-24)]: the HAIP minimum plus the classical suites that the ecosystem selects out of band (T123) |
| S1 | Naive credential first: only the issuer signature is PQ/composite | Implicit scenario of PQ-VC performance studies | PQ = {credential}, no expectation channel |
| S2 | ECCG AND, no expectation channel | ECCG ACM v2 | All signed artefacts dual-signed (classical + PQ), policy P1, no expectation channel |
| S3 | RFC 9955 composite, expectation out of band | RFC 9955 | All signed artefacts composite, expectation as an out-of-band pinned configuration |
| S4 | 8725bis: per-issuer local configuration | 8725bis-10 §3.1 | Policy P3, R_I from a classical channel (the source that feeds the local configuration is classical) |
| S5 | Root and device first | Mulder 2026, NCSC 2025 | Φ1: {LOTL, TL/LoTE, CA, WSCD/KB-JWT} PQ. Φ2: + issuer certificate, credential. Φ3: all. No expectation channel |
| S6 | Big bang: everything at once | Cost upper bound | All 13 artefacts + PQ transport, policy P4 |
| S7 | Computed minimal order | C1 | For each cell, the minimal set and optimal order computed by ASP |
| S8 | Transient resistance rule [Ö5, Amendment 1 (2026-09-24)] | Anchuri et al., ePrint 2026/1660 | Classical key with bounded lifetime + long-lived PQ identity |

- Strategy file: the draft named `model\karsilastirma\stratejiler.yaml` [Ö5]. The assignment actually fixed before the comparison is `models/asp/sorgular/stratejiler_taslak.json` (version 2, SHA-256 `11b05877…`, 2026-09-25 12:34:31Z), and Step 8 checks the assignment by a canonical hash. The file name and format differ from the draft (deviation, Section 13.9).

### 5.10 Metrics M1–M5 [Design v3 §7.10 + Operational]
- **M1 coverage:** secured cells / 36. Cell = G1–G4 × Φ1–Φ3 × 3 τ regimes. Anchor variants are reported separately. Computed in the 17-node model [Amendment 3, item 2.1 (2026-09-24)].
- **M2 cost:** number of migrated artefact classes.
  - Weighted version with the real counts of the LOTL: 43 pointers and 107 TL signer certificates for the TL/LoTE class.
  - The unweighted and weighted versions are reported together.
- **M3 broken transport paths:** number of (artefact, transport path) pairs in which the strategy's PQ artefacts exceed default server limits. Limits: nginx 1.31.6 ≤ 8,182 B and Node 24.15 ≤ 16,348 B header value, and QR capacity. Source: pilot P4, reproduced in Step 12.
  - DPoP size is reported **with its claim set** [Amendment 4, item 6 (2026-09-24)]: minimal (token request), `+ath`, `+ath+nonce` (resource access).
  - For composite signatures of variable length the upper bound is used: 3,381 B for ML-DSA-65-ES256.
  - The Design v3 statement "ML-DSA-65 DPoP ≈ 8,192 B, 10 B above the limit" depends on the claim set: 8,128 B with minimal claims (below), 8,244 B with `ath` and `nonce` (above).
- **M4:** rate of rejected legacy (classical-only) issuers. The primary analysis is unweighted.
- **M5:** whether WSCD replacement is needed (yes/no).
- **Pareto:** M1 (largest) against M2 (smallest). M3–M5 are reported alongside.
- **Three questions fixed before the comparison [Design v3]:**
  1. Does S5 secure every cell that S7 secures?
  2. Does S5 require extra artefacts?
  3. How many cells do S1 and S2 secure after Q-day? This is a health check. Expected: 0.
- **Outcome of question 3** [Amendment 8, item 4 (2026-09-26), post-result]: the expectation did not hold for S2 in Φ3 (9 cells), because Φ3 has class-level sunset and accepts no classical alternative. The result is not changed. That the expectation holds only for Φ1 and Φ2 is written as an explanation given after the result was seen.

### 5.11 Mechanism classes [Ö4, Amendment 1 (2026-09-24), replaces draft Section 4.11]
- **M-a:** unauthenticated capability negotiation (example: `Accept-Signature-Algorithms` when fetching `request_uri`).
- **M-b:** multi-signature request, "one suffices" verification (OID4VP A.3.2.2, DC API).
- **M-b0 (baseline):** removal of the signature. Basis: HAIP forces support of unsigned requests, and in the DC API signature verification is at the wallet's discretion.
- **M-c:** multiple requests (classical + PQ).
- **M-d:** out-of-band static configuration (DCR, CIMD). Normative basis: HAIP §7, "Verifiers are assumed to determine in advance…".
- **M-e:** PQ-signed issuer metadata ("supported" algorithms). **M-e′ (variant):** `*_alg_values_required` in the metadata.
- **M-f (proposed):**
  - The expectation comes from an authoritative **third party** (TL/LoTE governance) and is PQ-authenticated.
  - It is fresh or pinned, monotone, scoped per entity, carries sunset semantics and **also protects at first contact**.
  - Carrier order: TL/LoTE service extension, then WRPRC, then OpenID Federation.
- **M-g:** self-declared continuity / trust on first use (draft-sheffer-tls-pqc-continuity).
- **M-h:** PQ commitment extension embedded in the certificate (draft-reddy-lamps-x509-pq-commit, draft-vicente-lamps-pqchc).
- **Components of M-f for A3 [Design v3 §7.11]:** 1. authentication (PQ), 2. freshness or pinning, 3. monotonicity, 4. per-entity scope. The sunset marker counts as part of monotonicity.
- **A3 ablation dimensions [Ö4]:** authentication, freshness or pinning, monotonicity, per-entity scope, carrier, **source (third party versus self-declaration)**, **protection at first contact**. The carrier dimension is defined as "substitution", not "removal" [Amendment 3, item 3 (2026-09-24)].
- **Positioning [Ö4]:** policy P3 of Kim et al. ("an identity previously established as hybrid may not silently regress") leaves the source of the continuity state open. The contribution of M-f is **where this state comes from and how it arrives authenticated.**
- **Simplified M-f** [Amendment 4, item 9 (2026-09-24), post-result]: Section 4.4.
- **Scope of the expectation** [Amendment 4, item 13 (2026-09-24), post-result]: new dimension `beklenti_kapsami ∈ {yaprak_alg, yol_sinifi, anahtar}` (leaf algorithm, path class, key).
  - **The proposed scope of M-f is `yol_sinifi` (path class):** every edge of the accepted path, from the anchor listed in the TL/LoTE to the credential, must be PQ. Alternative: `anahtar`. Ablation: `yaprak_alg`.
  - Attacks to be tested: an alternative classical CA with a different name, a classical CA with the same name, and an attacker's PQ intermediate CA under a classical root.
  - M-h is modelled in two variants: reddy type (SAN + leaf algorithm) and vicente type (key digest).
- **Reductions** [Amendment 8, item 2 (2026-09-26), before the Step 7 runs]: no separate models for M-c (reduced to M-b), A.3.2.2 (M-b rules), M-e′ (the "required" parameter of M-e), and the A3 dimensions already tested in Step 5A (reference to the R7 variants).
- **M-d** [Amendment 8, item 2]: the expectation recorded in the file (`MD_reg_pq`: G5_migrated = F, PQ-signed register updates can be replayed) prevails over the plan text "from the PQ channel, proof".

### 5.12 Rule schemas R1–R7 [Design v3 §7.9 + Operational]
- **R1 chain:** a classical upper link makes the lower link forgeable.
- **R2 downgrade:** while coexistence lasts, forgery is possible without an authenticated expectation.
- **R3 channel:** two sub-rules.
  - R3a, transport substitution (H1): if a pulled artefact is fetched fresh from the authoritative source with PQ server authentication, its forged version does not reach the verifier, even if the object signature is forgeable.
  - R3b, expectation channel: an expectation is safe if it was authenticated over a PQ channel.
- **R4 WSCD:** a classical device key leads to presentation forgery.
- **R5 anchor:** out-of-band pinning cuts the chain.
- **R6 time window:** the condition τ < W_trust(K) (Section 5.5). In Tamarin it is encoded by ordering: if τ ≥ W, the event `Break(K)` can happen only after the event `WindowClose(K)`.
- **R7 monotone expectation:** a learned "PQ required" expectation cannot be withdrawn, except within an announced legacy window or under the sunset rule.
- **R1 qualifier** [Amendment 4, item 12 (2026-09-24), post-result]: the result `X_alt_ca_namebind` = V in R1 holds under the assumption "CA names are unique" (`Unique(<'ca', name>)`).

### 5.13 Capability levels L0–L5 and flags [Design v3 §7.17 + Operational]

| Level | Definition [Design v3] | Kind [Design v3] | Behavioural criterion (operational) |
|---|---|---|---|
| L0 | No algorithm restriction | General BCP | No algorithm restriction can be configured |
| L1 | Global allowlist | General BCP | Verifier-wide allowlist, non-allowed algorithm rejected |
| L2 | Per-call allowlist | General BCP | Allowlist per verification call |
| L3 | Per-key or per-issuer binding (8725bis §3.1) | General BCP | Algorithm binding per key or per issuer, battery case K10 (alg–key mismatch) rejected |
| L4 | "Required algorithm set" semantics: reject if the PQ component is missing | PQ-specific | In the configured state K1 ACCEPT, K2 REJECT, K3 REJECT (Section 7.8) |
| L5 | L3/L4 enabled by default | | L3 or L4 behaviour without configuration |

**Determination rule:**
- The target's L level is the **highest** level reachable through the documented general API. Library code is not changed.
- If a level is not in the API but can be achieved with custom code (a verification loop written with the general API primitives), the flag "expressible with custom code" is set and the line count is recorded. The target's L level is not raised to that level.
- The primary variable of H6, Y_i, is the presence of L4 semantics in the API (by configuration, or by default as L5).

**Interpretation note** [Ö10, item 2, Amendment 1 (2026-09-24): approved]: "can express by default through its general API" in H6 is read as "can express with the library's own mechanism, without changing code". Being enabled by default is reported separately as L5.

**Two forms of L4** [Amendment 2, item 6 (2026-09-24), Amendment 9, item 3 (2026-09-26)]:
- **L4m (multi-signature):** "required algorithm set" semantics through the documented API, without code change. Reject if the PQ component is missing.
- **L4c (targets that support only compact serialisation, or only COSE_Sign1):** in the same verifier instance, through the documented API, a **per-issuer** "PQ/composite required" policy. A classical-only document of a migrated issuer is rejected, and a classically signed document of a legacy issuer is accepted. This is the library-level counterpart of G5 during coexistence. Multi-signature cases are "not applicable" for such targets.
- **Y_i** = L4m if the target supports multi-signature objects, otherwise L4c.

**Measurement protocol for L levels** (adapter contract `experiment/oracle/oracle-A/adapter-contract.md` §5, frozen with this document). Levels are determined in the control arm, where X is the target's control label (EdDSA, Ed25519 or ES384, Section 7.7) and `VPLUS_EdDSA` stands for the twin vector carrying that label. Success means identity with the oracle rows:
- **L1:** global allowlist. Under `IZIN-A` (W = {ES256}), `VPLUS_EdDSA` is rejected and `VPLUS_ES256` is accepted. Under `IZIN-AX`, both are accepted.
- **L2:** two calls on the same verifier instance, `IZIN-A` and `IZIN-AX`, with decisions equal to the oracle rows.
- **L3:** `IZIN-AX` with documented per-key or per-issuer binding. Both directions of K10 are rejected and the `VPLUS_*` vectors are accepted. Additional condition: API evidence must show that the rejection comes from the binding mechanism. An incidental rejection caused by a key-type mismatch does not count as L3 (RFC 7515 §5.2 step 8 already rejects).
- **L4m:** under `L4` (R = {X}, W = {A, X}): T1K accepted (accept-classical), T2K rejected, T3 rejected, T5K accepted. Then Y_i = 1.
- **L4c:** two issuer policy records in the same verifier instance: migrated issuer (R = {X}) and legacy issuer (R = ∅). The legacy issuer has its own identity and key in battery v1.3 (`https://legacy-issuer.example`, vectors `L4C-JOSE_eski_ES256` and `L4C-COSE_eski_ES256`). Migrated issuer: `VPLUS_ES256` rejected, `VPLUS_X` accepted. Legacy issuer: its ES256 document accepted. All three decisions equal to the oracle: Y_i = 1.
- **"Same verifier instance" for L4c** [Decision D9 (2026-10-03)]: the adapter holds both issuer records and selects the record by the `iss` of the object, read before the library call; the library enforces the selected record through its own mechanism (allowlist or key binding). This is "L4c (consecutive)" of the adapter contract §5.3. It is the reading for every target, as the shared adapters implemented it before the conformance review of Decision D9. The selection is not custom code (B4): it chooses a configuration and checks nothing. A policy check that the caller writes inside a callback while the library enforces no algorithm policy is custom code, and the level is not raised (Decision D8).
- **L5:** default configuration (only the key is given). The L3 and L4 vectors are run. L5 if the decisions equal the `IZIN-AX` rows for L3 and the `L4` rows for L4.

**Interpretation note for L4c** [Amendment 11 (2026-10-01)]:
- For targets that support only compact serialisation (or only COSE_Sign1), every object carries one signature. L4c then checks whether a per-issuer policy can require X for a migrated issuer while a legacy issuer is still accepted with ES256. In effect this is a **per-issuer algorithm allowlist**, a capability of the kind that 8725bis §3.1 recommends in general and that L2/L3 measure. It is not the PQ-specific "required algorithm set" semantics over several signatures, which only L4m measures.
- L4m and L4c are therefore reported separately, and for each L4c target the mechanism used (per-issuer allowlist, per-key algorithm binding, or a required-set rule) is recorded from the adapter's `MAPPING.md`.
- If H6 is falsified mainly through L4c targets, this is reported as evidence of a general per-issuer allowlist capability, not of PQ-specific required-set semantics. This reading is fixed before any battery result.

**Incidental rejection in the control arm** [Amendment 11 (2026-10-01)]:
- Existing rules: L3 does not count an incidental rejection caused by a key-type mismatch (above, and adapter contract §5.2). Amendment 10 assigns a control label only after the target has passed the validity gate for that algorithm, which excludes missing support on the plain verification path but not on the configured policy path. Amendment 10 has no rule for incidental rejections under L4m or L4c.
- Rule: in the control arm, a rejection whose recorded error class shows that the control-label algorithm itself is not supported on that API path (`hata_sinifi = alg-desteklenmiyor` for the label algorithm, in particular ES384) is coded as **not supported**, not as policy enforcement. Such a rejection never counts as agreement with an oracle `reject`. For Y_i the case counts as not satisfied, because the policy was not shown.
- Implementation: the analysis script (`experiment/runs/analysis/analyze_c3.py`) codes a control-arm rejection with `hata_sinifi = alg-desteklenmiyor` as `desteklenmiyor` (not supported). It never counts as agreement with an oracle `reject`, and it makes the case not satisfied.

**Status of the L ladder** [Amendment 11 (2026-10-01)]: only Y_L4 (L4m or L4c) is confirmatory. The levels L0–L3 and L5 and the flags B1–B6 are descriptive. In the analysis script L2 is inferred from the API path string, and L3 does not check the API-evidence condition stated above. Both are computed as written and reported as approximations.

**Flags [Design v3 §7.17 + Operational]:**
- **B1 unknown composite `alg`:** reject, ignore, or the whole verification fails.
- **B2 mixed `x5c` chain policy:** can it be expressed?
- **B3 unprotected `x5c`:** is it processed?
- **B4 custom-code line count:** for the "expressible with custom code" case, blank lines and comments excluded. In the pilot about 20 lines for `jose`.
- **B5 semantic class:** at-least-one-valid, all-present-valid, required-set, or other.
- **B6 unsupported format:** for example General JSON not supported. This is not a failure but a "not applicable" record. It is decided beforehand by API review.
- **B1 for battery case K5** [Amendment 8, item 8 (2026-09-26), before C3]: K5 has no single oracle decision (Section 7.8: "according to policy"). The target's behaviour is classified in B1 as **S** (strict: an extra signature outside the allowed set causes rejection), **Y** (ignore: the extra signature is ignored once the required set is satisfied) or **other** (for example acceptance without X). Only "other" counts as a deviation. K5 does not enter F_K and F_T (Section 7.9: K1–K3).

### 5.14 "Not expressible" evidence rule [Design v3 §7.17, verbatim + Operational]
The verdict "not expressible" is given only if all three conditions hold:
- there is no hook in the API,
- at least two independent attempts have failed,
- there is a source-code line reference.

Otherwise the result is "indeterminate".

**Operational detail:**
- **"No hook in the API":** documented options, type definitions and public exports are scanned (for example with `rg`). The scan commands and their outputs are recorded.
- **"Two independent attempts":** made in different sessions. The second attempt does not see the code or notes of the first. It receives only the target and the adapter contract. Each attempt is time-boxed to at most 45 minutes [Draft parameter]. No third attempt is made.
- **"Line reference":** repository + commit SHA + file path + line range.
- **Scope of the second attempt** [Amendment 11 (2026-10-01)]: the second independent attempt is made only for targets whose "not expressible" verdict enters T1, that is, when the configuration that determines Y_i (L4m or L4c) is recorded as not expressible. For all other levels and flags (L1–L3, L5, B2 under `L4-YOL`), a "not expressible" record rests on the API scan, one attempt and the line reference. It is reported descriptively as "not expressible (single attempt)" and is not used in any inferential claim.
- **Outcome of the second attempts** [Decisions D8 and D9 (2026-10-03)]: 9 targets, records in `experiment/runs/evidence-rule/` and `experiment/runs/analysis/evidence-rule.csv` (read by the analysis script).
  - Not expressible, rule satisfied: COSE-001 (L4c), COSE-034, COSE-035, COSE-036 and JOSE-089 (L4m), SDJWT-025 (L4c).
  - Expressible only with caller code in a documented callback, so Y_i = 0 with B4 (8 lines each): SDJWT-001, SDJWT-018.
  - Expressible: COSE-014, through the documented designated-signer verification; its adapter was corrected before the freeze.
  - The form of every target follows the rule above (L4m if the library accepts multi-signature objects) and is the form the analysis script derives. COSE-035 and COSE-036 were added by Decision D9, when the conformance review showed that both are L4m with the Y-determining configuration recorded as not expressible.

### 5.15 "Indeterminate" and "adapter invalid" classes [Operational]
- **Indeterminate:** one of the following:
  - oracle A and oracle B disagree,
  - the evidence rule is not met,
  - instability across three repetitions (the cell value is not identical 3 of 3 times),
  - independent attempts contradict each other.
- **Adapter invalid:** if the adapter still fails the validity checks after two correction attempts (V+: a single valid classical signature → ACCEPT, V−: a corrupted signature → REJECT), the target leaves n_eff and is listed with the reason.
- **Exception** [Decision D1 (2026-10-01)]: SDJWT-002 accepts objects with a corrupted issuer signature (V− accepted) because the library computes the signature check but does not use its result. The adapter is treated as valid, the target is measured as is, its outcomes are flagged `integrity-failure`, and every analysis is also reported without it. This departs from the adapter-invalid rule above, with Decision D1 as basis (deviation, Section 13.7).
- **Exclusion from the primary H6 analysis** [Amendment 10 (2026-10-01)]: SDJWT-021 verifies only ES256, so no second classical algorithm passes its validity gate and it cannot express a two-algorithm required set. It is excluded from the primary H6 analysis and counted as Y = 0 in a sensitivity analysis (Section 7.14). In the statistics input the exclusion is recorded as `adaptor_gecersiz = 1` with the reason "no second classical algorithm passes the validity gate (amendment 10)". The target passes its own validity gate (ES256 with `vc+sd-jwt`), so this is a recording device for the exclusion, not an application of the adapter-invalid rule above.

### 5.16 "Not closed" label and the non-termination ladder [Design v3 §7.9]
Ladder steps (each with a 10-minute and 12 GB limit):
1. `--prove`
2. `[use_induction]` or `[reuse]` helper lemmas
3. `--auto-sources`
4. a proof-search tactic or a Tamarin oracle (heuristic)
5. bounded model or `--bound`
6. ProVerif
7. "not closed" label + exists-trace attack search + policy truth table

**Operational:**
- A lemma that gives a result at steps 1–5 is reported as "closed with Tamarin (step k)".
- If ProVerif gives a definite result at step 6, it is reported as "closed with ProVerif".
- ProVerif's "cannot be proved" counts as "unknown".
- Otherwise "not closed".
- **Well-formedness** [Ö12, Amendment 1 (2026-09-24)]: every Tamarin run must have 0 well-formedness warnings.
- **Run rule** [Amendment 8, item 2 (2026-09-26)]: if the derivation check times out, `--derivcheck-timeout=60` is used. The check is not disabled, and the well-formedness warnings must still be 0.
- **ProVerif scope** [Amendment 4, item 16 (2026-09-24)]: the second opinion covers only R1–R5. R6 and R7 were not transferred, because phases express τ poorly. This is reported as a limitation.

### 5.17 Mutation operators and score [Operational, target from Design v3]
**Operators:**
- MUT-01: remove signature verification
- MUT-02: remove key–alg binding
- MUT-03: remove the expectation check
- MUT-04: remove freshness (allow replay or a stale copy)
- MUT-05: remove transport authentication
- MUT-06: allow reuse of a component key
- MUT-07: remove monotonicity (allow withdrawal of the expectation)
- MUT-08: remove per-entity scope (global expectation)
- MUT-09: remove anchor pinning
- MUT-10: remove nonce/aud binding (KB-JWT)

**Score:** killed / (total − equivalent).
- A mutant counts as killed when the relevant security lemma turns from "verified" to "falsified" (Tamarin trace) or when the ASP property test catches the change.
- Equivalent mutants are listed with their reasons, and their share is reported.

**Target:** at least 90 % [Design v3, estimate]. The score per rule is also reported.

**Both readings are reported** (interpretation recorded in Section 13.9): the aggregator `models/mutation/score.py` excludes two "base insecure" mutants whose protected base already violates its lemmas, which gives 45/45 = 1.00. Under the literal formula above, counting these two as not killed, the score is 45/47 = 0.957 [computed]. The threshold of 0.90 holds under both readings.

### 5.18 Abstraction sampling [Design v3 §7.9 + Operational]
- **Frame:** all (cell, minimal set) pairs and all sets that lack one element of a minimal set.
- **Expectation:** "verified" for the minimal set, a trace for the reduced set.
- **Sample size:** if the frame has at most 200 instances, all of them. Otherwise a cell-stratified random sample [Draft parameter]: at least 1 instance per cell, 200 in total, seed 20260926.
- **Agreement:** closed instances where the Tamarin decision equals the ASP prediction, divided by closed instances.
- **"Not closed"** instances are reported separately. Extra assurance [Draft parameter, added to Design v3]: the share of not-closed instances is at most 10 %. Otherwise the validity criterion counts as not met.
- **Reading of the agreement condition** [Amendment 6, item 1 (2026-09-25)]. It applies to the technical gate condition "ASP and Tamarin agree on at least 10 instances", to evidence component D3 and to the validity condition (1) of the scientific gate ("sample agreement 100 % and every difference explained"):
  - agreement on closed instances must be 100 %,
  - a difference classified as an **error** (ASP error or Tamarin model error) is corrected, and all affected instances are re-run. The correction is written to the discrepancy log `models/sampling/UYUSMAZLIK-KAYDI.csv`, which is created at the freeze as an empty file with its header and filled when a difference is classified,
  - a difference classified as a **documented abstraction gap** does not count as agreement and is reported separately,
  - the classification is verified blind by a second, independent derivation session, not by the one that produced the difference. That session sees the rule expressions of both models but not which result was expected,
  - if an abstraction gap remains after one week of correction, the condition counts as not met and the rule of Section 9.1 for an unmet validity condition applies.
- **Technical gate sample rule** [Amendment 6, item 2 (2026-09-25)]:
  - Frame: the frame of this section in the primary configuration, taken from the ASP export. The ASP work package does not select instances, it exports the whole frame. The frame file is fixed by SHA-256 before selection.
  - Selection by the study team's script. Strata: goal {G1, G2, G3, G4, all} × kind {minimal, reduced}. One instance from each non-empty stratum, 10 in total. If fewer than 10 strata are non-empty, the rest is filled from the whole frame with the same seed. If more than 10, the strata are ordered by the seed and the first 10 are taken. Seed 20260926 (Appendix B).
  - Extra mandatory instance: 1 instance from the exploratory 2 × 2 grid of Section 6.3 (`ca_baglama=ad`, `ayni_ad_klasik_ca=var`). It does **not** enter the gate count and is reported separately.
  - The Step 5B sample is selected separately under this section. Overlap with the technical gate instances is allowed and reported.

### 5.19 Known-answer tests [Design v3 §7.9]
The three tests are encoded from the same ecosystem with an independent input format. Only example files are added. The core code does not change.

| Test | Published result (verbatim, Design v3) | Pass criterion (operational) |
|---|---|---|
| DNSSEC | RFC 6840 §5.11: "Validators SHOULD accept any single valid path." That is, algorithm downgrade | The tool produces that, under the "any valid path" policy, security falls to the weakest algorithm (trace or violation) and does not fall under the policy that requires all algorithms |
| X.509 hybrid binding | Kim et al. (arXiv:2607.20800): corrupting the PQ evidence changes the decision in none of the 27 cells. Lee et al. (ePrint 2026/1416): "no stack can mandate the binding" | The tool produces that, under a policy that does not require the PQ component, corrupting the PQ evidence changes the decision in no cell ("classical acceptance ≠ hybrid authentication") |
| S/MIME | Das and Chattopadhyay (ePrint 2026/1374): "every valid path to the CEK must satisfy the active migration policy" | The tool produces that, in an example with alternative paths, the target is protected only when every valid path satisfies the policy |

- All tests must pass. The S/MIME test is about confidentiality (CEK), while the model is about authentication. The mapping ("path-based policy satisfaction") is therefore documented as a structural mapping.
- If the mapping cannot be built, this is recorded as a deviation before freeze and a backup known-answer test is chosen (Step 6).
- **Backup rule** [Amendment 3, item 1 (2026-09-24)]: a backup test is chosen **only when a mapping cannot be built**. A test that ran and failed is not replaced by a backup. The failure is reported and a model error is searched for.
- **Expectations** [Amendment 8, item 1 (2026-09-26), before the Step 6 runs]:
  - The single source of expected values is `models/known-answer-tests/nsurum/kat_nsurum.tsv` (SHA-256 `3609f7931bdb0112d2273812b4d4787204c4bbd91e0092aca22d6d6369c62aec`), the column with the first derivation's values.
  - For the K2d Tamarin rows the lemma `no_silent_promotion` (M1) is used (`models/known-answer-tests/nsurum/N-VERSION-COMPARISON.md`).
  - Blind table: `models/known-answer-tests/kor-beklenen/BEKLENEN-KOR.tsv` (`180a655a…`). N-version result: 138 of 138 equal, 3 indeterminate cases resolved by returning to the source.
  - Pass criteria as above. Alternative readings recorded beforehand (`models/known-answer-tests/kor-beklenen/UNDETERMINED.md` §B) are used only for diagnosis.
- **Correction of the KAT-1 test model** [draft change log v0.11 (2026-09-26), post-result]: in the first run, case K1-11 failed. Cause: the draft test specification did not apply the integrity rule of RFC 6840 §5.11 at the DNSKEY step (a coding error in the test model, while the ASP core was correct). Corrected model `KAT1_DNSSEC_v2.spthy`: 15/15, mutations 5/5. Expected values and the pass criterion did not change, and no backup test was used. At the scientific gate the known-answer criterion is presented with two readings: first run 2 of 3, after correction 3 of 3. In the first run the ASP core agreed with the expected values in 109 of 109 cells. The failure lay only in the Tamarin encoding of KAT-1 itself. Gate condition (1) holds with this documented post-result correction (Section 13.9).

### 5.20 Oracle [Design v3 §7.17 + Operational]
- **Clause-bound generator:** verbatim quotation + URL + version → expected decision. The oracle is the combination of 8725bis §3.1 with PQ/composite.
- **N-version:** two independent derivations write the oracle (A and B). Disagreement enters the "indeterminate" class and is reported.
- **Metamorphic relations [Design v3 §7.17, written there as M1–M3]:**
  - MR1: if the required set is not met, stripping must not increase acceptance.
  - MR2: the effect of adding an unknown alg must be predictable from the policy.
  - MR3: if the decision changes when the version changes, it is flagged.
  - **MR4** [Amendment 2, item 8, renamed by Amendment 3, item 4, placed here by Amendment 6, item 5]: a permutation of the signature order must not change the decision. A violation is reported as a separate flag.
- Results across libraries are used as a divergence detector, not as a majority vote.

**Four-valued output** [Ö6, Amendment 1 (2026-09-24), defined by Amendment 8, item 7 (2026-09-26), before C3] (policy-parametric contract of Kim et al.): `accept-classical`, `accept-hybrid`, `reject`, `indeterminate`.
- **`accept-hybrid`:** the acceptance **rests on** PQ (or composite) evidence. The PQ evidence is decisive: if it is removed or invalidated, the decision becomes reject.
- **`accept-classical`:** the acceptance stays the same with classical evidence only.
- Examples: under P0 with both signatures valid → `accept-classical`. Under L4 → `accept-hybrid`. Acceptance with only a PQ signature present → `accept-hybrid`.

**Derivation of the L4 oracle** [Ö6]: no normative clause gives L4 directly. The oracle is derived from 8725bis §3.1 + composite AND + the definition of G5. Each of the two derivations performed it independently (`experiment/oracle/oracle-A/L4-DERIVATION.md`, `experiment/oracle/oracle-B/L4-DERIVATION-B.md`). Summary of the derivation:
1. Content of the requirement (8725bis §3.1 "MUST determine which algorithms are permitted for itself and that issuer", together with G5): for a migrated issuer I, at least one PQ-carrying algorithm X must be present and valid. Hence R_I ⊇ {X}, fixed as R = {X} by the battery policy.
2. Allowed set (8725bis §3.1 "MUST NOT employ any algorithms outside this configured set"): W_I = {A, X}.
3. Key–alg binding (8725bis §3.1, RFC 7515 §5.2 step 8, RFC 9864 §7): every signature is verified with the alg in its header and the key bound to that alg. A mismatch invalidates that signature (K10).
4. Composite AND (composite -04 §4.3 "MUST validate a signature only if all component signatures were successfully validated"): if X = ML-DSA-65-ES256, "X valid" means both components valid (K6, K7).
5. Which signatures must validate (RFC 7515 §5.2 leaves it to the application): for every algorithm in R_I a present and valid signature must exist. Hence K1 accept, K2 reject, K3 reject, K4 accept, which is exactly the behavioural criterion of L4.
6. Other signatures: signatures inside W that are used must be valid. For extra signatures outside W the sources allow two readings, strict (S) and ignore (Y).

Decision function, for the signature set Σ with alg(σ) and validity g(σ):
- L4-S(Σ) = ACCEPT if and only if every σ ∈ Σ has alg(σ) ∈ W, every σ ∈ Σ is valid, and for every x ∈ R there is a σ ∈ Σ with alg(σ) = x that is valid.
- L4-Y(Σ) = L4-S(Σ restricted to the signatures with alg in W). REJECT if that restriction is empty (RFC 7515 §5.2 "at least one").
- L4(Σ) = L4-S(Σ) if L4-S(Σ) = L4-Y(Σ), otherwise indeterminate. The two readings diverge only when an extra signature outside W is present (K5), and for K5 the oracle carries the B1 flag instead (Section 5.13).
- Validity is three-valued (valid, invalid, indeterminate). A definite failure is always a rejection. Without a definite failure, a decision that depends on an indeterminate validity is `indeterminate`.

**Policy configurations of the oracle and the job list.** A = ES256 in every arm. X depends on the arm: `kontrol-EdDSA` → EdDSA, `kontrol-Ed25519` → Ed25519, `kontrol-ES384` → ES384 [Amendment 10 (2026-10-01)], `tedavi-ML-DSA-65` → ML-DSA-65, `tedavi-composite` → ML-DSA-65-ES256. Key–alg binding is on in every configuration.

| Identifier | W | R | Multi-signature rule | Purpose |
|---|---|---|---|---|
| `GEC` (validity) | all algorithms supported in the battery | ∅ | single-signature objects only | V± adapter validity gate, plain validity baseline |
| `IZIN-A` (allowlist A) | {A} | ∅ | single-signature | L1, L2 |
| `IZIN-AX` (allowlist A, X) | {A, X} | ∅ | single-signature | L1, L2, L3 (K10 reject), legacy issuer of L4c |
| `L4` | {A, X} | {X} | indeterminate where S and Y diverge | L4, migrated issuer of L4c, oracle of F_K and F_T |
| `L4-S` | {A, X} | {X} | every present signature in W and valid | strict reading, B1, B5 |
| `L4-Y` | {A, X} | {X} | signatures outside W ignored | ignore reading, B1, B5 |
| `P0` | supported algorithms | ∅ | at least one valid | B5 class at-least-one-valid |
| `P1` | supported algorithms | ∅ | all present valid | B5 class all-present-valid |
| `P2` | {A, X} | ∅ | all present valid | oracle B's counterpart of P1/P2 and of the legacy half of L4c |
| `L4-YOL` (path) | {A, X} | {X} | + every certificate signature on the `x5c` path PQ | B2, X5C vectors only |
| `GEC@-19`, `L4@-19` | as `GEC`, `L4` | | | `sdjwtvc_surum` sensitivity, MR3 |

- Version suffixes: in the scope of `sdjwtvc_surum` (scenario (d) vectors and VC11), configurations are split into rows with the suffixes "|sdjwtvc=-13" and "|sdjwtvc=-19". The suffixes and "@-19" split only the expected outcome. They do not change the library configuration [Decision D6 (2026-10-01)].
- `P2` uses the library default, the same as `GEC`, `P0` and `P1` [Decision D6].
- `L4-YOL` is "not expressible" for every target, because no target exposes a path-class policy [Decision D6]. See Section 12.3.
- K5 rows under `L4`, `L4-S` and `L4-Y` carry the value `B1-bayragi` (B1 flag) [Amendment 8, item 8].
- K8 and K9 are arm-independent flag cases (B2, B3). They are measured once per target with R = {ML-DSA-65} and the ML-DSA-65 X5C vectors. The composite-arm rows carry the value `kol-bagimsiz` (arm-independent) and are not a result of the composite arm [Amendment 8, item 9 (2026-09-26)]. The composite cell of K8/K9 in the battery mapping is "not applicable", the vectors are unchanged [Amendment 9, item 5 (2026-09-26)].
- V± (adapter validity checks) are run in the P2 configuration (allowed set {ES256, X}, no required set) and not under L4 [Amendment 8, item 10 (2026-09-26)]. Deviation (Section 13.9): the job lists and the merged oracle run V± under `GEC`, not `P2`. On the 14 V± rows where both exist, the decisions are identical [computed].
- **Re-derivation of the oracles** [Amendment 8, item 11 (2026-09-26)]: oracles A and B re-derive with their own scripts using the definitions of items 7–10 (this section). This is mandatory only for the primary vectors and V±. Remaining disagreement counts as `indeterminate`. How the v1.3 oracle was actually derived is a deviation (Section 13.4).
- **Merged oracle v1.3** (`experiment/oracle/merged/decisions_v13.tsv`, produced by `experiment/oracle/merged/derive_v13.py`): 1,845 rows, one per job of `experiment/runs/jobs-v1.3.jsonl`. Rules applied by the script:
  - item 7: under `P0`, an `accept-hybrid` decision for T1, T7, VC07, VC08 or VC09 is normalised to `accept-classical`,
  - item 8: K5 vectors (T7, T4, T6, UNK04, UNK05) under the L4 family → `B1-bayragi`,
  - item 9: X5C04 and X5C07 in the composite arm → `kol-bagimsiz`,
  - A = B → that value. Present in only one oracle → that oracle's value. A ≠ B, or one of them `indeterminate` → `indeterminate`,
  - COSE vectors take the decision of the JOSE vector of the same case and arm (battery mapping §3 "COSE Kn" ↔ §1 "Kn"),
  - L4c-3 (legacy issuer, ES256 only) → `accept-classical` under `GEC`, `IZIN-A`, `IZIN-AX`, `L4`, `L4-S`, `L4-Y`, from the quotation in battery mapping §4 ("a classically signed document of a legacy issuer is accepted").
- **Merged oracle v1.4, the oracle of the measurement** [Amendment 10 (2026-10-01)] (`experiment/oracle/merged/decisions_v14.tsv`, produced by `experiment/oracle/merged/derive_v14.py`): the 1,845 rows of v1.3 unchanged, plus 357 `kontrol-ES384` rows, 2,202 rows in total, one per job of `experiment/runs/jobs-v1.4.jsonl`.
  - The expected decision depends on the case, not on which classical algorithm plays X. Every `kontrol-EdDSA` row of v1.3 is therefore copied to the `kontrol-ES384` arm with the ES384 counterpart vector (case mapping). Vectors that carry no X signature (for example `VPLUS_ES256` or the legacy-issuer vectors) keep their identifier.
  - Rows of the DPoP proof `DPOP02_EdDSA` (4 rows) have no counterpart and are not copied.
  - Decisions of the new rows [from `SUMMARY_v14.json`]: reject 162, accept-classical 147, B1 flag 30, indeterminate 12, accept-hybrid 6 (the hybrid rows are the secondary K5 vectors T4K and T6, which carry an additional ML-DSA-65 or composite signature, under `P1`).
- The adapter never sees the oracle. The runner, not the adapter, maps observations to the four-valued decision (Section 7.19).

### 5.21 "Non-obvious result" (scientific gate, condition 2) [Design v3 §7.15 + Operational]
At least **one** of the following is required.

**(2a) H4: insufficient or wasteful S5.** For at least one cell c = (G ∈ {G1, …, G4}, Φ, τ), under the fresh anchor assumption (or another anchor assumption named explicitly):
- **Insufficient:** the PQ set of strategy S5 in Φ does not secure G, while that of strategy S7 does.
- **Wasteful:** both secure the same goals, but S5 migrates at least one extra artefact class (M2 difference ≥ 1).
- **Additional condition:** the difference is reproduced in the ASP scan and in at least one Tamarin instance.
- **Candidate cells** [Ö3, Amendment 1 (2026-09-24)]: long-lived keys break in every τ regime, and such cells are not counted as (2a) differences. Priority cells: keys with a short exposure window, G4 (RP authentication) and WebPKI dependencies. The `X_alt_ca` observation (alternative classical CA path) is **evidence of model fidelity**: it matches RFC 6840 §6.2, Kim et al. M2 and the cross-signature contexts of Bkakria. It does not count as (2a) on its own. Its effect on M-h is assessed under Ö2 (i).
- **Counting** [Amendment 8, item 3 (2026-09-26), post-result, written after the Step 3 results, strict reading]:
  - Primary 36 cells: in the 12 "insufficient (node)" cells the missing nodes are long-lived (V1 or a CA key) and are **not counted** under Ö3. The 6 "insufficient (expectation)" cells belong to H3 and are assessed under (2c). **The 9 "wasteful" cells in Φ3 are not counted**, because the surplus comes from the Φ3 definition of S5 ("all") and from the goal-specific cell definition. The same difference exists for S2, S3, S4 and S6, and the extra nodes are not on the goal's path. They meet the letter of (2a), but counting them would make the condition trivial. The literal reading is reported as **sensitivity**.
  - Ö3 cells: τ-wasteful cells inside the pre-specified designs are (2a) candidates: `G2_cnf1g_{orta,yavas}` (a10) in the H5 design and `G3_durum_{gunluk,gecici}_{orta,yavas}` (a08) in the H2′ design. Each needs at least one Tamarin instance (additional condition above).
  - The 4 G4 cells redefined afterwards with `wrprc_dogrulama = faz1` do **not** pass the gate. They are reported as exploratory (Section 1.2, Amendment 3, item 1).
  - For transparency: the H4 filter was made "regime-aware" after the results were seen. The model rules did not change.
  - A fair-metric variant (union over the goal vector) is reported as sensitivity. It was added on 2026-10-01, after the formal results were known, and changes no verdict (Section 13.9).

**(2b) H1/H2′: substitution or phase change of operational importance.**
- **H1:** the object signature of at least one pulled artefact drops out of the minimal set with fresh PQ-server-authenticated transport. The same artefact does not drop out with classical server authentication.
- **H2:** the minimal set or optimal order changes between at least two τ regimes.
- **"Operational importance":** the relevant window, freshness or transport parameters come from normative or documented values of the traceability matrix (not only from the synthetic grid), and the result changes a real configuration decision of a verifier or TL operator (which artefact or channel becomes PQ).

**(2c) H3: downgrade trace.** For M-a, M-b or the OID4VP A.3.2.2 scenario, the G5 lemma (all-traces) is falsified in Tamarin with a concrete trace. The emulator reproduction of Design v3 (Step 11) was supportive only and was removed by Amendment 11.
- **Narrowing (2c′)** [Ö2, Amendment 1 (2026-09-24)]: the following count as obvious and do **not** satisfy condition (2) on their own: the downgrade traces found for M-a, M-b or M-b0. Reason: they are predictable from Bhargavan et al. 2016, RFC 9955 and Kim/Lee.
- **Results that can satisfy condition (2):**
  - (i) the M-h commitment being bypassed through the classical chain, or through an alternative classical CA without name binding,
  - (ii) a result about M-e′ that contradicts the expectation recorded beforehand,
  - (iii) a result in the M-f component ablation (A3) that contradicts the expectation recorded beforehand,
  - (iv) a trace specific to OID4VP A.3.2.2, with a normative basis, that cannot be derived from known results.
- **Qualifier of (i)** [Amendment 3, item 3 (2026-09-24)]: bypassing the M-h commitment satisfies condition (2) only if (a) it contradicts the expectation recorded beforehand, or (b) it appears under a condition that **cannot be derived** from `X_alt_ca`, RFC 6840 §6.2 and Kim et al. M2 (example: the protection claimed by the draft falls under the draft's own processing rules and assumptions).
- **Expectations recorded beforehand** [Amendment 3, item 3]: the Step 5A expectations were recorded before the runs in column 7 of `models/tamarin/betik/varyantlar.tsv` (SHA-256 `a88d972ea6fd445eb7021b7072f4bf368e8ff3ede3f56e0d9f8aad8f088bf1f9`, 2026-09-24 12:45:40), covering R6 (H2′, key mode × regime), R6h5 (H5), R7 (A3 ablation of M-f, and M-g) and R7h (M-h, combined with `X_alt_ca`). Expectations are read only from this file. The Step 7 expectations were written in task 0 of Step 7, before any mechanism run (`models/mechanisms/on_kayit_varyantlar.tsv`), and fixed by a separate anchor. They cover the G5 expectation for M-a…M-h, M-b0 and M-e′, the 7 A3 dimensions and the expected answers to questions (i)–(iii) about M-h. A result whose expectation was not recorded beforehand cannot count as "unexpected" under (ii) or (iii) of (2c′).
- **Note on condition (2)** [Amendment 4, item 14 (2026-09-24), post-result]: in R7h the expectation for the protected `P_ca_pq_alt_namebind` was V and the observation was F. This satisfies Ö2 (i)(a) **formally**. The (b) candidate (the protection failing under the reddy-01 draft's own processing rules) does not count as evidence until it is modelled in Step 7. The decision on condition (2) is taken in Step 8 by an independent novelty review. Presentation: the principle (binding at key or path level) is known in the literature (sheffer-02 §3.2, vicente-02). The contribution is not presented as a new attack class.

**Counted as obvious [Design v3 §1].** The following do not satisfy condition (2) on their own:
- the chain rule,
- migrating the trust anchor and device keys first (Mulder, NCSC),
- the `x5c` certificate being composite-signed (composite -04 §6.2),
- stripping under the "at least one valid" policy (RFC 9955, RFC 6840 §5.11),
- hybrid X.509 stacks being unable to mandate the binding (Kim et al., Lee et al.).

### 5.22 "Vulnerability" (trigger for responsible disclosure) [Operational]
A target's behaviour counts as a "vulnerability" only if all three conditions hold:
- (a) it violates a MUST/SHALL provision of a specification that the target declares to implement, or the target's own documented security contract,
- (b) attacker S1 or S2 could exploit it so that one of G1–G5 is violated, argued from the battery outcome and the threat model (the emulator demonstration was removed by Amendment 11),
- (c) it is not merely an unimplemented optional feature.

**Example:** the absence of L4 alone is a **capability gap**, not a vulnerability, and is reported without embargo. Borderline cases are handled cautiously as vulnerabilities and referred to the corresponding author for a decision (human step İ2). No external disclosure is made without that decision.

### 5.23 Identifiers used by the repository
| Identifier | Meaning |
|---|---|
| `kontrol-EdDSA`, `kontrol-Ed25519`, `kontrol-ES384` | control arm with X = EdDSA, or with the fallback label Ed25519 or ES384 (Section 7.7) |
| `tedavi-ML-DSA-65`, `tedavi-composite` | treatment arms with X = ML-DSA-65 (secondary) and X = ML-DSA-65-ES256 (main) |
| `kapsam-pq`, `kapsam-hibrit`, `klasik-taban`, `yok` | arm values of descriptive scope vectors, evaluated under `GEC` only |
| `kabul`, `red`, `istisna`, `zaman-asimi`, `cokme` | raw outcomes: accept, reject, exception, timeout, crash |
| `uygulanamaz` | not applicable (B6, unsupported format) |
| `ifade-edilemedi` | not expressible through the API (input to the evidence rule of Section 5.14) |
| `sinif = birincil` / `ikincil` | primary or secondary vector for the (vector, arm) pair |
| `D_soy` | stripped-document acceptance in the default configuration |

---

## 6. Analysis plan: deterministic part [Design v3 §7.12 + Operational]

### 6.1 Principle [Design v3 §7.12, verbatim]
- For a deterministic result a p-value is meaningless. Evidence is given by full enumeration, independent re-derivation and robustness.
- A sampled population (libraries) requires inferential statistics.
- This distinction is stated explicitly in the methods section.

### 6.2 Evidence standard

| # | Component | Definition (operational) | Threshold |
|---|---|---|---|
| D1′ | Full enumeration | See the query space below [Amendment 3, item 2 (2026-09-24), replaces D1] | Reported |
| D2 | ASP–z3 agreement | For every query in Q, the subset-minimal solution sets of ASP and z3 are equal after normalisation. In addition, 1,000 random configurations per query class with three-way agreement of ASP, z3 and an independent Python fixed-point evaluator (seed 20260928) | 100 % |
| D3 | ASP-to-Tamarin sample agreement | Section 5.18, with the reading of Amendment 6, item 1 | 100 % (on closed instances), every difference explained in `models/sampling/UYUSMAZLIK-KAYDI.csv`, not closed ≤ 10 % |
| D4 | Mutation score | Section 5.17 | ≥ 90 % |
| D5 | Known-answer tests | Section 5.19 | 3 of 3 passed |
| D6 | Sensitivity grid | ML-DSA parameter (44/65/87) × number of intermediate CAs (1–3) × τ grid × window grid. "Robust region" = the parameter region in which the minimal set and the order do not change | Reported |
| D7 | Version robustness (C3) | **Removed** [Amendment 11 (2026-10-01)], together with the historical baseline (Section 7.16). Originally: share of decisions that do not change across the last 3–5 releases | not applicable |
| D8 | Emulator agreement | **Removed** [Amendment 11 (2026-10-01)] with the end-to-end demonstration. Originally: model prediction against the decision observed in the emulator, every mismatch explained | not applicable |
| D9 | Well-formedness | Well-formedness warnings in all Tamarin models. Note: all 6 outputs of pilot P1 had a "fact multiplicity" warning | 0 warnings |

Superseded D1 (draft): |Q| = 675 [computed], and a scan of 2^13 = 8,192 PQ subsets × 540 (Φ × τ × anchor × policy × G1–G4) = 4,423,680 decisions.

### 6.3 Query space and primary configuration [Amendment 3, item 2 (2026-09-24)]
**Query space.**
- **Q** = goal {G1, G2, G3, G4, all} × Φ {Φ1, Φ2, Φ3} × τ {10 min, 3 days, 26 days} × anchor {fresh, pinned, cached} × policy {P0…P4}.
- **|Q| = 675.** Q is evaluated in the **primary configuration** below.
- "Full enumeration": for every query in Q, the minimal PQ sets over the 17 nodes are enumerated with `domRec` with respect to all subsets. Completeness is guaranteed by the solver.
- Explicit enumeration of the 2^17 subsets is **not** required.
- The "< 10 min" criterion applies only to this `domRec` enumeration in the primary configuration.

**Primary and sensitivity values.**

| Parameter | Primary | Sensitivity | Rationale and basis |
|---|---|---|---|
| WebPKI (TLS server authentication) | classical | PQ | Current state: X25519MLKEM768 makes only the key exchange PQ. **Design factor for H1**, both values are primary |
| k (keys breakable per window) | unbounded | 1, 3 | Worst case, in the attacker's favour |
| `iptal_denetimi` (revocation check) | on | off | The definition of G3 assumes revocation checking. The specification says "recommended" (T178) |
| `cihaz_bagi` (device binding) | on | off | The definition of G2 assumes device binding. The specification says "recommended" |
| `rp_auth_fail_open` | off | on | Conservative choice. The specification lets the user "present anyway" (T247, T253) |
| `wrprc_dogrulama` | faz0 (no validation) | faz1 | Current ecosystem: validation deferred by 24 months (T254) |
| `ca_baglama` (formerly `ad_baglama`) [Amendment 4, item 11 (2026-09-24)] | `yok` (none) | `ad` (name), `anahtar` (key) | Default of path validation. Per-issuer CA binding is not mandatory (name constraints are optional, RFC 5280 §4.2.1.10) |
| `ayni_ad_klasik_ca` [Amendment 4, item 11] | `yok` | `var` | Structural flag: under the same anchor, a classical CA certificate with the same name as the legitimate CA is valid (key changeover period) |
| `sdjwtvc_surum` | -13 | -19 | HAIP 1.0 pins -13 (T113–T115) |
| Mode of the status-list signing key (H2′) | V1 long-lived | V2 daily rotation, V3 per token | Default: issuer or authorised long-lived key (T159–T161). **Design factor for H2′** |
| W_trust: LOTL/TL signer | 5 years | 1 year | TL signer certificates are multi-year (pilot P5 LOTL data) |
| W_trust: CA | 5 years | 1 year | Logarithmic grid |
| W_trust: issuer (`x5c` leaf) | 1 year | 30 days, 180 days | Logarithmic grid |
| W_trust: RP access certificate | 1 year | 180 days | WRPAC is not short-lived (T261) |
| W_trust: TLS server certificate | 1 year | 47 days | Current 398-day upper bound. The CA/B Forum reduction as sensitivity |
| W_trust: WIA | 1 day | | < 24 h (T204–T208) |
| W_trust: KA | 1 year | 180 days | Long-lived (T204–T208) |
| W_trust: device key (`cnf`) = credential validity | 30 days | 1 day (ARF ≤ 24 h option), 180 days, 1 year | The specification gives no value. Middle of the logarithmic grid |
| W_accept: TL/LoTE | 6 months | | Fixed (T021–T025) |
| W_accept: KB-JWT `iat` and DPoP | 10 min | 1 min, 60 min | Clock skew of "a few minutes" (T392) |
| W_accept: status-list TTL, metadata cache | 1 day | 1 hour, 7 days | Logarithmic grid |
| τ sensitivity grids | | fast {1, 10, 60} min, medium {1, 3, 7, 10} days, slow {14, 26, 60} days | Ö8 |

Tnnn are row identifiers of the traceability matrix (`traceability/`).

**`ca_baglama` and `ayni_ad_klasik_ca`** [Amendment 4, item 11 (2026-09-24), post-result]: the results of the primary configuration do not change: with `ca_baglama = yok` the flag has no effect, which ASP verifies as a health check. In addition to the one-at-a-time analysis, the 2 × 2 grid {`ad`, `anahtar`} × {`yok`, `var`} is reported as **exploratory** and does not pass the gate.

**Hypothesis-specific pre-specified designs** [Amendment 3, item 2.4]: Sections 4.2, 4.3, 4.5 and 4.6. All cells of these designs are primary.

**Counting rule** [Amendment 3, item 2.5 (2026-09-24)]:
- (2a) and (2b) are counted only in the primary configuration or in the pre-specified designs.
- Differences found in other configurations are reported as "sensitivity / exploratory" and do not pass the gate.
- Sensitivity analysis departs from the primary configuration in **one parameter at a time** (OAT).

**Boundary conditions** [Amendment 8, item 6 (2026-09-26), post-result]: G3 being satisfied without migration at k = 1, and the boundaries `w_tls` 47 days with τ ≥ 47 days, are reported in the paper as boundary conditions.

---

## 7. Analysis plan: sample part (C3) [Design v3 §7.12 + Operational]

### 7.1 Population and frame
- Draft frame sources: JOSE/JWT from the jwt.io library list (an independent auditor counted 106 unique repositories), SD-JWT from a GitHub search for "sd-jwt" (estimate: 15–18 libraries), COSE (estimate: 10–12 libraries).
- **Frame** [Amendment 2, item 1 (2026-09-24)]: unit, population and strata as defined in `experiment/inventory/CRITERIA-DRAFT.md` §0–§2. 198 candidates: JOSE 109, SD-JWT 29, COSE 37, reference 23 (the reference stratum is not measured after Amendment 11, Section 7.4). Frame file `experiment/inventory/FRAME.csv`.
- The frame date is the inventory day of Step 9a. All queries were anonymous.
- **Limitation** [Amendment 2, item 10]: the JOSE part of the frame comes only from jwt.io. Libraries such as fast-jwt and josekit stayed outside. This is reported in the paper as frame bias.

### 7.2 Inclusion and exclusion [Amendment 2, item 2 (2026-09-24), replaces the draft thresholds]
- A candidate is eligible only if it meets all of inclusion criteria K1–K8 (`experiment/inventory/CRITERIA-DRAFT.md` §3):
  - K1 asymmetric verification (verifies JWS/COSE/SD-JWT signatures with at least one asymmetric algorithm),
  - K2 activity (HEAD commit of the default branch on or after 2024-09-23, the reference date minus 24 months),
  - K3 maintenance status (not archived, no "deprecated / not maintained / moved / legacy" statement),
  - K4 open licence (OSI-approved, SPDX),
  - K5 popularity threshold E2 (below),
  - K6 builds and runs in a Linux x86_64 container (final test: Section 7.3),
  - K7 scope (a library or an RP verifier),
  - K8 uniqueness (one unit per code base, forks and repackagings excluded).
- **Popularity threshold E2**, scaled per stratum, indicators joined with "or":
  - **JOSE:** ≥ 200 stars or ≥ 100k monthly downloads or ≥ 100 dependent packages.
  - **SD-JWT and COSE:** ≥ 20 stars or ≥ 1k monthly downloads or ≥ 10 dependent packages.
  - **Reference:** ≥ 20 stars, with the official reference exception.
- **Exclusion reasons D1–D9** (`CRITERIA-DRAFT.md` §6): D1 symmetric only (K1), D2 no commit in 24 months (K2), D3 archived, abandoned or handed to a successor (K3), D4 open licence not verifiable (K4), D5 below threshold (K5), D6 platform-bound (K6), D7 out of scope (K7), D8 duplicate or fork (K8), D9 eligible but outside the quota.
- Superseded draft criteria: JOSE/JWT ≥ 50 GitHub stars or ≥ 5,000 downloads in the last 30 days, SD-JWT and COSE ≥ 10 stars or ≥ 500 downloads, with exclusion of archived repositories, libraries bound to platform-specific cryptography only, sign-only libraries and wrappers sharing a verification core.

### 7.3 Quotas and selection [Amendment 2, item 3 (2026-09-24)]
- Quotas: JOSE 18, SD-JWT 8, COSE 5. Hence **n = 31**.
- Selection is deterministic (`experiment/inventory/collect.py` → `secim()`, `CRITERIA-DRAFT.md` §5.3):
  - JOSE: the 2 most popular targets from each of the 9 language groups.
  - SD-JWT and COSE: at most 2 targets per language group until the quota is full.
- If the Linux build fails, the target is replaced under the pre-registered replacement rule (`CRITERIA-DRAFT.md` §5.4: first the backup of the same language group, otherwise the general backup of the stratum). The replacement is reported. A behavioural result can never justify a replacement.
- **Replacement made** [Amendment 8, item 13 (2026-09-26)]: JOSE-104 (Swift-JWT) did not build on Linux (BlueRSA incompatible with OpenSSL 3, a fix would require a code change). Under §5.4 the first candidate of the general backup order, **JOSE-031 (guardian, Elixir)**, replaces it. JOSE-017 stays as a backup.
- The selected targets are listed in Appendix E.
- Superseded draft strata: JOSE/JWT general ≈ 15, SD-JWT-specific ≈ 9, COSE ≈ 6, at least 4 language families.

### 7.4 Reference verifiers: removed [Amendment 11 (2026-10-01)]
- The reference verifiers and the end-to-end demonstration are removed from this document (decision of the study lead, not needed for any claim). No reference verifier is measured.
- Superseded: reference verifiers were outside n and reported separately [Ö10, item 3, Amendment 1, and Amendment 2, item 4 (2026-09-24)]. The selection file `experiment/inventory/SELECTION.csv` still lists the selected reference candidates (stratum REF), and Amendment 8, item 19 had reduced them to one reference verifier with 1–2 end-to-end traces.

### 7.5 Sample size
- **Target:** n ≈ 30, accepted range 25–40 [Design v3]. Fixed at **n = 31** by the quotas.
- **n_eff** = included − adapter invalid − (in the primary analysis) indeterminate.
- **Primary n_eff before indeterminate targets are removed: 30** [Amendment 10 (2026-10-01)]. SDJWT-021 is excluded from the primary H6 analysis (Section 7.7). Thresholds for n_eff = 30: support X ≤ 10, falsification X ≥ 20 (Appendix A).
- **Inferential lower bound:** if n_eff ≥ 20, T1 is inferential. If n_eff < 20, only a descriptive result (Wilson CI) is given, and no claim of "majority" or "absence of a majority" is made.

### 7.6 Treatment arms and treatment classes
- **Arms** [Ö6, Amendment 1 (2026-09-24)]: main arm composite -04 (ML-DSA-65 + ES256), secondary arm pure ML-DSA-65 (RFC 9964).
- **Treatment classes, per arm** [Amendment 2, item 7 (2026-09-24)]:
  - **TK1 native:** the library verifies the PQ signature itself.
  - **TK2 plug-in:** our PQ verifier (`experiment/signer`) is attached to a public API, while the policy layer stays the library's.
  - **TK3 unknown-alg:** only the "unknown alg" behaviour is observed.
  - Amendment 2 restricted T2 (McNemar) to TK1 and TK2 targets and reported TK3 separately and descriptively. After the removal of the plug-in class (below) and Amendment 11, T2 is a descriptive analysis of TK1 targets (Section 7.10).
  - The names "T1-yerel / T2-eklenti / T3-bilinmeyen-alg" in `CRITERIA-DRAFT.md` §5.5 correspond to TK1–TK3.
- **TK2 out of scope** [decision of 2026-10-01, deviation, Section 13.1]: a target without native ML-DSA support is TK3. No hypothesis depends on the plug-in class. T2 covers TK1 targets only and is descriptive [Amendment 11 (2026-10-01)].
- **Composite arm:** if no target supports composite -04 natively, all targets are TK3 in that arm.
- **Assignment rule** (adapter contract §6, without the plug-in class): TK1 requires a documented general API at the pinned version that verifies the algorithm natively, and the validity gate of that arm must pass (`VPLUS_ML-DSA-65` / `VMINUS_ML-DSA-65`, or `CMP00` / `CMP01`). Otherwise TK3. The assignment is made before measurement, by API review and the validity gate only, and recorded per target with a reason.
- **Version pinning and treatment class** [Amendment 8, item 14 (2026-09-26)]: the treatment class is assigned on the pinned version. Example: cose-lib 4.8.2 has no ML-DSA, so it is not TK1. Capabilities present only at HEAD (cose-lib, go-cose) are reported descriptively. On the pinned versions: Section 13.3.
- **JOSE-102** [Decision D2 (2026-10-01)]: jwt-kit 5.3.0 verifies ML-DSA-65 only through `@_spi(PostQuantum)`, which is not public API. Primary analysis: TK3. Sensitivity analysis: TK1.
- **Assignment file:** `experiment/runs/TK-ASSIGNMENT.csv` (written before measurement, commit `ebeded0`). ML-DSA-65 arm, primary: TK1 for COSE-036, JOSE-001, JOSE-009, SDJWT-015 (application-supplied verifier callback with the policy in the library, Decision D5) and SDJWT-018 (verification delegated to jwcrypto), TK3 for all other targets. ML-DSA-65 arm, sensitivity: as primary, plus JOSE-102 as TK1 (Decision D2). Composite arm: TK3 for every target. Appendix E lists the classes per target.

### 7.7 Key resolution and control-arm label [Amendment 4, items 1–2 (2026-09-24), Amendment 5, item 3 (2026-09-24)]
- In L-level measurements the verification key is given in **every arm** through the target's documented API (JWK/JWKS or a direct key, for COSE a COSE_Key or a direct key). The same path is used across arms, so key resolution does not confound the arms. A target that uses different paths across arms has an invalid control–treatment comparison.
- `x5c` and chain behaviour are measured only in the X5C vectors, with classical and ML-DSA chains.
- Composite X.509 is out of scope and labelled "**HAIP §6.1.1 deviation**". Composite objects are resolved through kid/JWKS.
- **Control-arm label:** the primary label is `EdDSA`. **Fallback rule:** if the target does not support `EdDSA` but documents support for `Ed25519` of RFC 9864, the control arm is run with the `Ed25519`-labelled twin vectors. If it supports both, `EdDSA` is used. The label used is recorded per target. Using the fallback does not change the definition of Y_L4.
- Label sensitivity (a tool fact, not a target measurement): an allowlist that contains only `EdDSA` rejects an `Ed25519`-labelled signature, and vice versa. Recording the label used is therefore mandatory, and the allowed set W is always built with the label used.
- **Label order EdDSA → Ed25519 → ES384** [Amendment 10 (2026-10-01), decision D4, extends Amendment 4, item 2]:
  - Reason: at the JWS/COSE-level gate, 15 targets support neither EdDSA nor Ed25519 (COSE-001, COSE-014, JOSE-001, JOSE-002, JOSE-034, JOSE-052, JOSE-065, JOSE-084, JOSE-087, JOSE-089, JOSE-091, SDJWT-001, SDJWT-002, SDJWT-004, SDJWT-021). The purpose of the control arm is to separate the expressibility of the policy from PQ support. A second classical algorithm of the same family, ES384, signed with the battery's deterministic `issuer/ES384` key, serves this purpose.
  - Rule: the control label of a target is the first label in the order EdDSA, Ed25519, ES384 whose validity gate the target passes. The label used is recorded per target, the allowed set W is built with it, and using a fallback label does not change the definition of Y_L4 (Amendment 4, item 2, applied to the extended order).
  - Result, from the validity gate on battery v1.4 (`experiment/runs/CONTROL-LABELS.csv`): **EdDSA 17, ES384 13, no label 1.** No target needs the Ed25519 label, because every target that passes Ed25519 also passes EdDSA.
  - **SDJWT-021** verifies only ES256, so it cannot express a two-algorithm required set. It is excluded from the primary H6 analysis and counted as Y = 0 in a sensitivity analysis (Sections 5.15 and 7.14).
  - **SDJWT-002** keeps the label EdDSA (the algorithm it claims) together with the `integrity-failure` flag of Decision D1.
  - Effect on the H6 sample: the primary n_eff is 30 before indeterminate targets are removed (Section 7.5).
- Superseded pre-freeze wording of decision D4 (first version of 2026-10-01): targets without EdDSA or Ed25519 would have had an `undetermined` control-arm level and would have been excluded from paired analyses. Under that wording Y_L4 would have been missing for 15 targets and n_eff would have fallen to at most 16.

### 7.8 Test battery
**Measurement battery v1.4** [Amendment 10 (2026-10-01)]: `experiment/vector-generator/vectors/v1.4/`, **230 vectors (200 of v1.3 + 30 ES384 counterparts)**. The v1.3 vectors are byte-identical, and the counterparts are ES384 versions of the control-arm vectors.
- Every EdDSA signature of a control-arm vector is re-made with ES384 under the deterministic key `issuer/ES384`. Recorded corruptions are reproduced, and the meaning of the K10 alg–key mismatch is kept. The DPoP proof has no counterpart.
- Generator: `experiment/vector-generator/generator/v14.py`. Independent check: `experiment/vector-generator/tests/t14_es384.py`, 357 of 357 passed (`experiment/vector-generator/results/t14_es384.txt`). The first generation of v1.4 carried the kid of the Ed25519 key in the unprotected header of 9 COSE counterparts; the generator was corrected and v1.4 generated again before the freeze, and T14 now also checks every kid (Decision D9, Section 13.13).
- The 200 vector files of v1.3 are byte-identical in v1.4, and only the two manifest files differ [computed from the two `SHA256SUMS` files]. The manifest of v1.4 records the anchored hashes of the v1.3 manifest and `SHA256SUMS`. The manifest field `vektor_sayisi` gives 230 (the generator is corrected and the manifest regenerated before the freeze, with the vector bytes unchanged).
- v1.4 is mounted for the adapters at the path `/v/v1.3`. It is a byte-identical superset, so no adapter reads a different file for a v1.3 vector.
- The hashes of the v1.4 `MANIFEST.json` and `SHA256SUMS` are computed and recorded at freeze (Section 11).

**Base battery v1.3** [Amendment 9 (2026-09-26), anchor 9]: `experiment/vector-generator/vectors/v1.3/`, **200 vectors** (204 files).
- The 153 vectors of v1.2 are byte-identical (v1.2 = v1.1 + 53 vectors: 24 MR4 permutations with Ed25519 twins, a genuinely unregistered third signature for K5 (`T7K`/`T7P`/`T7C_plus_kayitsiz`, `X-KAYITSIZ-1`), both directions of alg–key mismatch per arm for K10, V+/V− vectors, and a descriptive order twin of VP05 that changes its `sd_hash` binding, outside MR4) [Amendment 7 (2026-09-25)]. v1.1 = v1 (93 vectors) + 7 `Ed25519`-labelled control twins [Amendment 5 (2026-09-24)].
- 45 COSE vectors were added: COSE_Sign for K1–K5 and MR4, COSE_Sign1 for K6–K10 and V±, and Ed25519 twins in the control arm.
- 2 L4c vectors were added: a legacy issuer with its own identity, `https://legacy-issuer.example`, in JOSE compact and in COSE_Sign1.
- COSE algorithm identifiers, taken from corpus lines: ES256 −7, EdDSA −8, Ed25519 −19 (RFC 9864), ML-DSA-65 −49 (RFC 9964), composite ML-DSA-65-ES256 −55 ("requested, not registered", composite -04 §7.2).
- Anchored identity (verified at anchor 9 by an independent regeneration in an empty directory, 204 files byte-identical):
  - `vectors/v1.3/MANIFEST.json`: `a81424470cf2b773c346795aa1b1880aecd841b77254ebb0c077432bc3c5390a`
  - `vectors/v1.3/SHA256SUMS`: `a5b678d60ff474f1991168a694f52acb6d1c8a42b9648b4e8e63913042768812`
  - `keys/v1/SHA256SUMS` (unchanged): `c941feb5ee70de6adbd2f3f9468ae8f9a2d265897db232c34d4dfda8f7ccfc1a`
  - `keys/v1.3/SHA256SUMS`: `5d0ccf6bc8cf5de3061ecab1a6c55f8d1165fe10235f366ecd4807b830bb160c`
  - `experiment/vector-generator/BATTERY-MAPPING.md` at anchor 9: `6795ee65f5161b4db90942f7058924061273e5d1eb1546dce444cabb2c7cb982` (the current file differs only in a path string after the renaming of 2026-10-01, Section 13.8)
  - Tests: T10 v1.3 1440/1440, T11 592/592, T12 138/138. Generator image `pq-a09-credgen:1.3`.
- The generator is fully deterministic: keys are derived with HKDF-SHA256 from fixed IKM, salt and labels (`experiment/vector-generator/README.md`). The credential generator seed of Appendix B was not used [Amendment 6, item 6 (2026-09-25)].
- **Rule** [Amendment 5, item 4, Amendment 7, item 5, Amendment 9, item 6]: no vector outside the battery is used in C3. Any change to the battery requires a new anchor and re-measurement of already measured targets. Amendment 10 is such a change. It was made before any target was measured with battery vectors, and battery v1.4 is the battery of the measurement. Deviation with Decision D1 as basis (Section 13.7): the validity gate of the SD-JWT targets uses 16 SD-JWT-format vectors outside the battery (`experiment/runs/vpm-sdjwt/`). They serve only the adapter validity gate and no outcome variable.

**Policy:** first signature A = ES256. Second component X: EdDSA in the control arm (or the fallback label of Section 7.7), ML-DSA-65 (RFC 9964) or composite -04 in the treatment arms. If the target does not support X, the treatment arm is still run. The observed behaviour is then unknown-alg behaviour, which is itself the PQ-specific failure. Per-issuer required set R = {X}, allowed set {A, X}.

| Case | Content | Oracle decision |
|---|---|---|
| K1 | Dual signature (A + X), both valid | ACCEPT |
| K2 | X signature corrupted | REJECT |
| K3 | X stripped (A only) | REJECT |
| K4 | X only | ACCEPT |
| K5 | K1 + a third signature with an unrecognised algorithm | According to policy (MR2), flag B1 |
| K6 | Composite single signature, valid (on supporting targets) | ACCEPT |
| K7 | Composite-labelled, one component corrupted | REJECT |
| K8 | Mixed `x5c` chain: realised as leaf ML-DSA-65, intermediate CA classical (vector X5C04) [Amendment 6, item 4 (2026-09-25)] | Flag B2 |
| K9 | `x5c` in an unprotected header | Flag B3 |
| K10 | Alg–key mismatch | REJECT (L2/L3) |
| K11 | Dual issuance: classical-only credential from a migrated issuer | REJECT (G5) |
| V+ / V− | Adapter validity checks | ACCEPT / REJECT |

- K8 in the draft read "leaf composite, intermediate CA classical". It is realised with an ML-DSA-65 leaf because composite X.509 is out of scope. The oracle decision (flag B2) is unchanged [Amendment 6, item 4].
- **Scenario labels [Design v3 §7.5]:** (a) composite (K6, K7). (b) dual issuance (K11). (d) General JSON multi-signature (K1–K5), outside the specification and labelled as such. (c) A.3.2.2 is on the wallet side. It is covered by the mechanism models (M-b, Step 7). The library battery does not test it, and its end-to-end test (Step 11) was removed by Amendment 11.
- **KB binding and multi-signature** [Amendment 4, item 4 (2026-09-24)]: by RFC 9901 §8.1 and §8.3, when General JSON serialisation carries several signatures, which signature `sd_hash` binds is undefined. A **descriptive** sub-cell "KB binding does not protect the multi-signature set" is added for scenario (d) and H5 (vectors VP05–VP07). Which signature the targets digest is reported descriptively. This is not a new hypothesis.
- **Implementer error class** [Amendment 4, item 5]: "wrong pre-hash" (vector CMP10) is recorded as a descriptive error class. A target that accepts CMP10 is written into the taxonomy as "wrong pre-hash implementer error".
- **COSE −7** [Amendment 9, item 4 (2026-09-26)]: ES256 (−7) is primary. RFC 9864 deprecates −7, and HAIP says "−7 or −9". Support for −7 is checked on the pinned versions during adapter preparation, before freeze. If a target supports only −9, ESP256 (−9) twins are generated before freeze and a new anchor is taken.
  - **wolfCOSE** [Decision D3 (2026-10-01)]: the default build rejects ES256 (−7) and EdDSA (−8). The library documents the build flag `WOLFCOSE_ENABLE_DEPRECATED_ALGS`, which enables them. The target therefore supports −7 through a documented configuration and is measured with that build. The default-build behaviour is reported descriptively. The rule for targets that support only −9 does not apply.
- **Battery mapping:** `experiment/vector-generator/BATTERY-MAPPING.md` maps every case and arm to its vectors and marks each (vector, arm) pair as primary or secondary. JOSE and SD-JWT targets are measured with the vectors of its §1–§2, COSE targets with those of §3, the L4c form with §4. The mapping was written for v1.3. **Each ES384 counterpart of v1.4 inherits the primary or secondary status of its EdDSA source vector**, as the case mapping of the oracle does [Amendment 10, Amendment 11 (2026-10-01)].
- **Before freeze** only validity checks were run on the target libraries: the pre-freeze job lists `experiment/runs/jobs-prefreeze-v1.3.jsonl` (32 rows: V± and CMP00/CMP01 under `GEC` in the four arms of v1.3) and `experiment/runs/jobs-prefreeze-v1.4.jsonl` (40 rows, the same in the five arms of v1.4), and the SD-JWT-format gate (Decision D1). In addition, the conformance test of Decision D9 ran objects outside the battery (acceptance rows only; Sections 12.4 and 12.5).
- **Validity threats** [Amendment 4, item 8 (2026-09-24)]: the ML-DSA vectors were produced with the deterministic variant. The cross-verifier comes from the same OpenSSL family as some libraries, which dilithium-py and external test vectors mitigate. v1 had no COSE/mdoc, JWE or WIA/KA (COSE was added in v1.3).

### 7.9 Outcome variables
- **Y_L4:** the primary variable of H6 (Sections 4.7 and 5.13).
- **L level:** ordinal (L0–L5).
- **B1–B6:** flags (Section 5.13).
- **F_K, F_T:** 1 if, in the target's best reachable configuration (highest L through the API), at least one of K1–K3 deviates from the oracle. K = control arm, T = treatment arm. The comparison is made against the `L4` rows. The target's S or Y semantics do not change K1–K3. Composite is the main arm. The ML-DSA-65 secondary arm is reported separately.
- **D_soy:** acceptance of the stripped document (K3) in the default configuration.
- **Case level:** oracle agreement per battery case.
- **Primary and secondary vectors** [Amendment 7, item 4 (2026-09-25)]: the pre-registered outcome variables (the battery part of Y_L4, F_K, F_T, D_soy, B1–B6) are computed only from the vectors marked **primary** in the battery mapping. **Secondary** vectors are descriptive, reported separately, and do not enter the pre-registered tests. Reason: adding secondary vectors would inflate "deviation in at least one" variables through multiple comparisons.
- **Comparison with the oracle** (adapter contract §9):
  - unit: (target, vector, policy, arm, cell stable in 3 of 3 runs),
  - not compared: cells where oracles A and B disagree (indeterminate), oracle `indeterminate` cells (reported but not counted as deviations), and target `uygulanamaz` cells (B6),
  - deviation types: **decision deviation** (accept-* ↔ reject), **acceptance without PQ verification** (oracle `accept-hybrid`, target `accept-classical`, a deviation in the L4 family because R was not applied), **harmless acceptance-type difference** (oracle `accept-classical`, target `accept-hybrid`, recorded but not counted as a deviation).

### 7.10 Confirmatory test and descriptive analyses [Amendment 11 (2026-10-01)]

**T1 is the only confirmatory test. T2–T5 are descriptive.** For T2–T5 no p-value, no test decision and no multiplicity correction is reported, and no inferential claim is made. They are reported as counts and Wilson 95 % confidence intervals.

| Code | Question | Analysis | Status |
|---|---|---|---|
| **T1 (H6)** | Is the L4 rate below 0.5? | Exact binomial, X = Σ Y_L4, H0: p ≥ 0.5, one-sided (lower), α = 0.05, uncorrected. Decision rule: Sections 4.7 and 9.3 | **Confirmatory, unchanged** |
| T2 | How often is a failure PQ-specific? | Paired table of (F_K, F_T) on TK1 targets of the ML-DSA-65 arm: the four cell counts and the number of targets with F_T = 1 ∧ F_K = 0, with a Wilson 95 % interval for that proportion | Descriptive |
| T3 | Does PQ-specific failure differ between SD-JWT-specific and general JOSE targets? | Number of targets with F_T = 1 ∧ F_K = 0 among the TK1 targets of each stratum (COSE outside), each proportion with a Wilson 95 % interval | Descriptive |
| T4 | Does the rate of L ≥ 3 differ between targets that released after 8725bis-10 (2026-08-21) and those that did not? | Number of targets with L ≥ 3 in each release group, each proportion with a Wilson 95 % interval | Descriptive |
| T5 | How many targets accept the stripped document in the default configuration? | Number of targets with D_soy = 1, the proportion with a Wilson 95 % interval | Descriptive |

- Intervals: Wilson 95 % intervals, computed by both implementations of the statistics package (Section 7.18). The package still computes the tests T2–T5 and the Holm correction, but flags them as descriptive in its output (`betimleyici_testler`). These outputs are not reported as inferential results.
- **Reason** (decision of the study lead, recorded before any measurement data existed): after the removal of the plug-in class TK2 (Section 13.1), every target is TK3 in the composite arm and the ML-DSA-65 arm has 5 TK1 targets (COSE-036, JOSE-001, JOSE-009, SDJWT-015, SDJWT-018). With 5 discordant pairs, all in the same direction, the exact two-sided McNemar test cannot go below p = 2 · 0.5^5 = 0.0625 > 0.05 [computed]. With JOSE-102 in the sensitivity analysis of Decision D2 (6 pairs) the floor is p = 0.031, which still cannot pass the first Holm threshold 0.0125. In T3, the TK1 targets are 2 SD-JWT and 2 JOSE targets, and the smallest attainable two-sided Fisher p is 0.33 [computed]. T2 and T3 therefore had no power by design. T4 and T5 are made descriptive with them, and the Holm family is removed.
- **What stays unchanged:** the primary variable Y_L4, the confirmatory test T1, its thresholds (n_eff = 30: support X ≤ 10, falsification X ≥ 20, Appendix A), the robustness rules of Section 7.14 and the measurement run itself.
- **T1 outside any correction.** The threshold table of Design v3 §7.12 (n = 30: ≤ 10 / ≥ 20) is for uncorrected α = 0.05. T1 is the single confirmatory test, so no correction applies.
- **Superseded plan** [Design v3, Ö6 of Amendment 1, Amendment 6, item 3, Amendment 8, item 17]: T2 (exact McNemar, two-sided), T3 and T4 (Fisher exact, two-sided) and T5 (exact binomial, one-sided upper) formed a Holm family (m = 4, α = 0.05, p = 1 for a test without data). T2 was to be presented as the main empirical finding, and Holm was applied in order of p-values with T2 first only in presentation order. T1 stayed outside the family. At most 2 pre-specified strata were allowed for Fisher tests (T3, T4).
- **T3 scope** [Amendment 8, item 17]: TK1 targets only (Amendment 8 named TK1 and TK2). COSE targets are outside T3, because the question compares SD-JWT and JOSE. The statistics configuration (`experiment/statistics/scripts/c3istat/yapilandirma.py`) still sets `T3_TK_KAPSAMI = ("TK1", "TK2", "TK3")`. This is harmless for the analysis of the treatment classes, because no target is TK2, and T3 is descriptive. The descriptive report states the classes that enter T3.
- **T4 flag** [Amendment 8, item 17]: 1 for a target that published a release strictly after 2026-08-21 and up to the freeze date. A target without a release history is not applicable in T4. The analysis script reads the latest release date recorded in `experiment/inventory/FRAME.csv` at the frame date. A release published between the frame date and the freeze is therefore not seen, which can only lower the count. T4 is descriptive.
- **Analysis sets of T2–T5** [statistics note N-1]: each analysis uses the targets whose own variables are determined (not null) and whose adapter is valid: T2 F_K and F_T determined and TK1, T3 F_K and F_T determined and SD-JWT/JOSE, T4 L and the release flag determined, T5 D_soy determined. The set of every analysis is reported with its target list.
- **Arms.** No target supports composite -04 (Section 12.2), so the composite arm (main arm) has no TK1 target and T2 has no data there. The analysis script (`experiment/runs/analysis/analyze_c3.py`) writes one statistics input for the composite arm (primary) and one for the ML-DSA-65 arm (secondary). T2 and T3 are reported for the ML-DSA-65 arm.
- **Additional descriptive measures** [Ö6]: fail-open, Kim-style contrast pairs (PQ evidence intact versus destroyed), and corruption of each composite component separately.

### 7.11 Effect sizes [Design v3, with Amendment 11]
- **T1:** proportion + Wilson 95 % CI + difference from 0.5.
- **T2–T5:** counts and Wilson intervals as in Section 7.10. No effect size is reported with an inferential reading.
- Superseded [Amendment 8, item 17]: for T2 the paired risk difference with a Newcombe interval (paired, method 10, with Newcombe's corrected correlation φ\*), for T3 and T4 the conditional maximum likelihood odds ratio with its conditional exact interval and the risk difference with a Newcombe interval (independent, method 10), for T5 a Wilson interval. The package still computes them (Section 7.18).

### 7.12 Wilson confidence intervals [Design v3]
A Wilson 95 % CI is reported for every L level and every flag (B1–B6). Reading adopted as part of the frozen package (statistics note N-12, [Amendment 11 (2026-10-01)]): "every L level" means the rate of L = k, with the rates of L ≥ k given as a labelled descriptive addition. B1 and B5 are reported per category. B4 is the rate of "expressible with custom code", with the line count reported as median and range. B6 is the rate of "not applicable". All of these are descriptive.

### 7.13 Cluster bootstrap [Design v3]
- **Use:** case-level rates within libraries (for example the rate of cases that disagree with the oracle).
- **Unit:** library.
- **Settings:** B = 10,000, percentile CI, seed 20260927.
- **Specification** [Amendment 8, item 17, by reference to `experiment/statistics/FREEZE-INPUT.md` §3]:
  - statistic: pooled proportion θ\* = Σ x / Σ m over cases with a determinate agreement value,
  - clusters ordered lexicographically by `hedef_id`, clusters with 0 determinate cases excluded, k = number of remaining clusters,
  - random stream: `rng = random.Random(20260927)` (Mersenne Twister), for r = 1…B and j = 1…k, `index = floor(rng.random() · k)` (replication-first order),
  - percentile CI of Hyndman–Fan type 7 at q = 1/40 and 39/40,
  - scopes: all cases, control arm K, treatment arm T. Each scope restarts with the same seed.

### 7.14 Missing data, indeterminacy and sensitivity analyses
- **Primary analysis:** indeterminate targets are outside n_eff.
- **Sensitivity (i), conservative:** indeterminate targets count as Y = 1 (against H6).
- **Sensitivity (ii):** indeterminate targets count as Y = 0.
- **H6 support rule:** H6 is supported if the primary analysis **and** (i) both give X ≤ c. If only the primary analysis does, the result is reported as "fragile support".
- **Symmetric rule** [Amendment 8, item 17 (2026-09-26)]: H6 is falsified if the primary analysis **and** (ii) both give X ≥ u. If only the primary analysis does, the result is reported as "fragile falsification". The statistics package implements the rule in the function `h6_hukmu` of `experiment/statistics/scripts/c3istat/analiz.py` (verdict `kirilgan_yanlislama`).
- **Thresholds of the sensitivity analyses:** each sensitivity analysis uses the thresholds of its own sample size, computed by the rule of Appendix A (statistics note N-2, adopted with [Amendment 11 (2026-10-01)]). Example: n_eff = 28 with 2 indeterminate targets and X = 9 gives primary support (c = 9). Under (i), X = 11 of 30 > c = 10 gives "fragile support".
- **Pilot sensitivity:** T1 is repeated without the targets in n that were seen in either pilot: JOSE-009 and SDJWT-015 (pilot P3) and JOSE-033, JOSE-034, JOSE-065, JOSE-083 and JOSE-084 (second pilot, Section 12.5) [Amendment 11 (2026-10-01)]. Superseded: the draft excluded only the libraries of pilot P3.
- **Delegation sensitivity** [Amendment 2, item 9 (2026-09-24), Amendment 8, item 16 (2026-09-26)]: targets that inherit the verification of another target are recorded: vck (SDJWT-001) → Signum (COSE-001, same project), WalletFramework (SDJWT-021) → IdentityModel (JOSE-001). T1 is recomputed and the T2 counts are reported without the delegating targets, regardless of version (version differences are noted). This analysis is descriptive.
- **Integrity-failure sensitivity** [Decision D1 (2026-10-01)]: every analysis is also reported without SDJWT-002.
- **SDJWT-021 sensitivity** [Amendment 10 (2026-10-01)]: T1 is repeated with the adapter-invalid targets, that is SDJWT-021, counted as Y = 0 (n_eff + 1), with the thresholds of that sample size from Appendix A (statistics package: sensitivity `gecersiz_y0`). SDJWT-021 does not enter sensitivity analyses (i) and (ii), which concern indeterminate targets only.
- **JOSE-102 sensitivity** [Decision D2 (2026-10-01)]: the analyses involving treatment classes are repeated with JOSE-102 as TK1.
- T2–T5: targets with indeterminate or not-applicable values for an analysis's variables are outside that analysis, and n is reported per analysis (Section 7.10).

### 7.15 Repetitions and determinism [Design v3]
- The battery is run 3 times, each time in fresh containers (runs r1–r3).
- A cell value is valid if it is identical 3 of 3 times. Otherwise it is "unstable" and enters the indeterminate class. The number of unstable cells is reported.
- Timeouts (adapter contract §4): 60 s per vector (hard), 30 min per target and run. A timeout gives `zaman-asimi` and the decision `indeterminate`. Network is off (`--network none`).
- Before the first measurement the battery and the oracle are checked with `sha256sum -c`. On a mismatch the measurement does not start.

### 7.16 Historical baseline and recall of known bugs: removed [Amendment 11 (2026-10-01)]
- Both analyses are removed. Neither serves a hypothesis or the confirmatory test, and both would need adapters for older releases. Evidence component D7 (version robustness) is removed with them.
- Superseded plan [Design v3 §7.10(d)]: the last 3–5 releases of each target, limited to releases that need no adapter change, with the coverage rate reported, and recall of patched old vulnerabilities by the harness (example: a version of `sd-jwt-js` before #388/#389), target recall 100 %.

### 7.17 Binomial threshold table and power [Design v3 §7.12, computed and verified]
p0 = 0.5, α = 0.05, one-sided exact binomial.

| n | For a majority claim | For the absence of a majority | Width of the Wilson 95 % CI (at about 70 %) |
|---|---|---|---|
| 25 | ≥ 18/25 | ≤ 7/25 | ≈ 33 points |
| **30 (this study, primary n_eff)** | **≥ 20/30** | **≤ 10/30** | **≈ 31 points** |
| 40 | ≥ 26/40 | ≤ 14/40 | ≈ 27 points |

- If the final n_eff differs from 30, the thresholds are read from the full table of Appendix A (n = 20–40) [Amendment 2, item 5, Amendment 10].
- Interpretation for H6: X ≤ c ⇒ support, X ≥ u ⇒ falsification, c < X < u ⇒ inconclusive.
- **Power** [computed]: for n_eff = 30 and the threshold X ≤ 10, the probability of support is 0.9744 if the true L4 rate is 0.2, 0.7304 if it is 0.3, and 0.2915 if it is 0.4. For the falsification threshold X ≥ 20, the probability is 0.7304 if the true rate is 0.7.

### 7.18 Statistical software
- Package `c3istat` 1.0.0 (`experiment/statistics/scripts/c3istat/`), input schema `c3-istat-girdi/1.0` (`experiment/statistics/SCHEMA.md`). Validated only on synthetic data before freeze.
- Two implementations: A (`kesin.py`, exact fractions and Decimal, Python standard library) is the reference. B (`referans.py`, scipy/statsmodels/numpy) is the check. Tolerances: absolute 1e-10 for p-values and CIs, relative 1e-8 for odds ratios. A decision difference counts as "borderline" only if the reference value is within 1e-12 of the threshold, and is then reported with A prevailing. Any other difference invalidates the analysis (exit code 2). These tolerances (statistics note N-8) are part of the frozen package [Amendment 11 (2026-10-01)].
- Image `pq-a09-analiz:1.0`: base `python:3.11-slim@sha256:9534e5a8…` (Python 3.11.16), numpy 2.4.6, scipy 1.17.1, statsmodels 0.15.0 and their pinned dependency closure, installed with `--require-hashes`. At freeze the study team builds the image once and records its identifier in the freeze record.
- Run: `sha256sum -c SHA256SUMS` in `experiment/statistics/` first, then `python -m c3istat analiz --girdi <file> --cikti <dir>` in the image, with `--network none`. Exit codes: 0 complete, 2 the two implementations disagree, 3 input not valid.
- The input file with `veri_turu = "olcum"` (measurement) is produced only after the freeze, in Step 10.

### 7.19 Measurement procedure
- **Job list:** `experiment/runs/jobs-v1.4.jsonl`, 2,202 rows [Amendment 10 (2026-10-01)]: the 1,845 rows of the v1.3 job list `experiment/runs/jobs-v1.3.jsonl` plus 357 rows of the `kontrol-ES384` arm (generator `experiment/runs/make_jobs_v14.py`). One JSON object per row with the fields `vektor_id`, `politika`, `kol`, `dosya`, `serilestirme`, `artefakt`, `algler`. It contains no oracle decision. The adapter does not see the oracle.
- **Run script:** `experiment/runs/run_measurement.sh` runs the job list for every target three times (r1–r3), each run in a fresh container. Before the first run it checks the frozen hashes of the battery, the oracle, the job list and the adapter sources against `docs/preregistration/FREEZE-SHA256SUMS`. A missing manifest or any mismatch stops the run.
- **Analysis script:** `experiment/runs/analysis/analyze_c3.py`, written before any measurement (commit `ebeded0`). It maps the outputs to four-valued decisions, takes the stable decision of the three runs, compares it with the oracle v1.4, derives the per-target variables with the reason for every null value, and writes the statistics inputs (composite arm primary, ML-DSA-65 arm secondary). As frozen it:
  - codes a control-arm rejection with `hata_sinifi = alg-desteklenmiyor` as `desteklenmiyor` (Section 5.13),
  - computes F_K and F_T against the `L4` rows (Section 7.9, adapter contract §9.4). They are descriptive,
  - computes the L ladder with the approximations of Section 5.13 (L2 from the API path string, L3 without the API-evidence check). It is descriptive,
  - uses the pilot set of both pilots (Section 7.14),
  - decides a conjunction of checks (Y_L4, the L ladder, F_K and F_T) as 0 as soon as one check deviates; it is indeterminate only if no check deviates and at least one cannot be judged,
  - writes, besides the primary and the secondary input, the inputs of the sensitivity analyses without SDJWT-002 (Decision D1) and with the sensitivity treatment-class assignment (Decision D2),
  - reads the evidence-rule table `experiment/runs/analysis/evidence-rule.csv` to decide whether a "not expressible" verdict on the Y-determining configuration is determined (Section 5.14) and to record B4 (Decision D8),
  - corrections of 2026-10-03 before the freeze: Section 13.12.
- **Call** [Decision D7 (2026-10-01)]: adapters with their own folder and Dockerfile take `adaptor <jobs> <out>`. The shared adapters (`_py`, `_node`, `_go`, `_jvm`, `_kt`, `_rs`) take `<target> <jobs> <out> <run>`. `experiment/runs/adapters/_tools/run.sh` handles both. Containers run with `--network none` and read-only mounts of the vectors, keys and jobs. `run.sh` stops a run after 30 minutes per target (adapter contract §4); rows that a stopped run did not write are missing in that run, so their cells are unstable and count as `indeterminate`.
- **Output** per row (subset of adapter contract §3): `hedef_id`, `hedef_surum`, `adaptor_sha256`, `kosu`, `vektor_id`, `politika`, `kol`, `sonuc_ham`, `hata_sinifi` (closed list of contract §3.2, or null), `hata_ozeti`, `dogrulanan_algoritmalar`, `api_yolu`, `sure_ms`.
- **Mapping to the four-valued decision** (by the runner, contract §3.1): accepted and at least one PQ signature shown to be verified (library result object) → `accept-hybrid`. Accepted without shown PQ verification (for example TK3, or acceptance resting only on the classical signature) → `accept-classical`. Rejected or a verification exception of a listed class → `reject`. Timeout, crash or instability across 3 runs → `indeterminate`. Format not supported by the documented API (B6, decided beforehand) → `uygulanamaz`, not compared.
- **B6 versus reject:** B6 is decided beforehand by API review and recorded in the target's `MAPPING.md`. If the API exists, the vector is run and a parse error is a rejection (`hata_sinifi = ayristirma`). By 8725bis §3.14, a JWT library rejecting JSON input is B6, not a deviation.
- **Libraries that do not verify signatures themselves** [Amendment 8, item 15 (2026-09-26)]: authlete `sd-jwt` and `sd-jwt-payload` are measured through the verification path they document (the JOSE layer they recommend). Without a documented path the target is L0, under the evidence rule of Section 5.14. The configurations are fixed in the adapter contract.
- **Documented caller patterns** [Decision D5 (2026-10-01)] count as the library's verification path:
  - COSE-035 (cose-lib): the algorithm and `crit` checks are in the caller pattern given in the README.
  - SDJWT-010 (sd-jwt-payload): signature verification goes through josekit, as in the crate's own example and tests.
  - SDJWT-015 (@sd-jwt/core): the library is crypto-agnostic. The verifier callback answers only whether a signature is valid under a key. The algorithm policy stays in the library option `allowedIssuerAlgorithms`.
  - SDJWT-025 (ssi-sd-jwt): plain compact JWS objects are verified with ssi-jwt from the same project and the same locked versions.
- **SD-JWT targets** [Decision D1 (2026-10-01)]: SD-JWT targets are gated with SD-JWT-format vectors. SDJWT-021 accepts only the legacy `typ` value `vc+sd-jwt` and only ES256. It passes the gate in that form and is measured as is. Battery objects with `dc+sd-jwt` are expected to be rejected by this library, which is its documented behaviour.
- **ES384 arm in the adapters** [Amendment 10 (2026-10-01)]: every adapter maps the arm `kontrol-ES384` to X = ES384 (commit `7143e8c`).
- **Adapter conventions:** the rules are the calling conventions (Decision D7) and the documented caller patterns (Decision D5) above. The following conventions of the adapter helper report are descriptive notes on how the adapters present inputs, not rules of this document: in single-signature objects the effective allowlist under the L4 family is R for a migrated issuer and W = {A, X} for the legacy issuer of L4c (Decision D9, Section 5.13), in multi-signature objects without a documented rule the row is `ifade-edilemedi`, SD-JWT targets receive compact `jws-cekirdek` vectors as `"<jws>~"`, and for an OID4VCI batch response `credentials[0]` is used.

---

## 8. Overhead measurement (M-f and baselines) [Design v3 §7.12 + Operational]
- **Quantities:** bytes (deterministic, reported as a table) and number of extra fetches (deterministic), per mechanism.
- **Scope reduction** [Amendment 8, item 18 (2026-09-26), approved by the corresponding author before any measurement]: the stochastic measurement of verification time (30 runs × 3 repetitions, 9,000 observations per mechanism) is **removed**. Overhead is reported **deterministically** per mechanism, as bytes and number of extra fetches. Reason: no hypothesis or claim rests on time, time is specific to the environment, and the cost of M-f is fully determined by extra fetches and bytes.
- **Comparison:** M-f against M-a…M-e and the "no expectation" baseline.
- Superseded design (draft Section 7): 30 runs × 3 repetitions per mechanism, each run a new process with 10 discarded warm-up operations and 100 measured operations, mechanism order shuffled per repetition (seed 20260929), median, P95, P99, run-level cluster bootstrap CI (B = 10,000, seed 20260927) and coefficient of variation, with an environment record.

---

## 9. Decision rules

### 9.1 Gates [Design v3 §7.15, verbatim + Operational]
**Week 2, technical gate.** Conditions [Design v3]:
- the tool containers work,
- the ASP model is built with the 13 artefacts, channels, windows and τ,
- ASP and z3 agree 100 %,
- Tamarin R1–R5 closed through the ladder,
- ASP and Tamarin agree on at least 10 instances.

If not met, the model is narrowed (3 τ regimes, fresh TL). If that also fails, a policy truth table and a trace reproduction are made, and the target becomes CSI/FGCS. The agreement condition is read as in Section 5.18, and the instances are selected by the rule of Section 5.18 [Amendment 6, items 1–2 (2026-09-25)].

**Week 6, scientific gate.** Two conditions [Design v3]:
- **(1) Validity** (all required): ASP–z3 agreement 100 %, sample agreement 100 % with every difference explained, mutation score ≥ 90 %, all known-answer tests passed.
- **(2) Non-obvious result** (at least one, operational definition in Section 5.21): a. H4, b. H1/H2′, c. H3.

Decision:
- (1) and (2) met → TDSC. If (2c) arises in a final specification (A.3.2.2) → TIFS is considered.
- Only (1) met → CSI or FGCS.
- (1) not met → policy truth table and repetition in the test environment → CSI.

**Lock and readings:**
- The gate criteria were locked at anchor 3 [Amendment 3, item 1 (2026-09-24)]. The gate decision uses the anchor-3 criteria. A result obtained with a changed criterion is reported only as sensitivity.
- The clarifications of Amendment 6 tighten the criteria. In the gate decision the literal reading of anchor 3 is also reported. If the two readings decide differently, this is stated explicitly and the strict reading prevails [Amendment 6 (2026-09-25)].
- The decision on condition (2) is taken in Step 8 by an independent novelty review [Amendment 4, item 14 (2026-09-24)]. The decision taken on 2026-10-01 is recorded in Section 12.1.
- The known-answer criterion is presented with two readings: first run 2 of 3, after the correction of the KAT-1 test model 3 of 3 (Section 5.19).

**Week 8.** Reference verifier check: removed with the reference verifiers [Amendment 11 (2026-10-01)].

**Week 10.** C3 check: at least 25 adapters must work, and the overhead must have been measured. The emulator condition (1–2 verifiers) was removed by Amendment 11.
- The thresholds for H6 are always read from Appendix A for the final n_eff (Section 9.3). In particular, if n_eff < 25, the thresholds are read from Appendix A.
- If n_eff < 20, the descriptive rule of Section 7.5 applies.

### 9.2 Interpretation and reporting of positive and negative outcomes
**Rule:** every outcome whose expected verdict or decision rule was fixed beforehand (H0–H5) and the pre-registered outcome of H6 are reported, whatever their direction. Negative outcomes are reported too [Design v3 §7.7, §15].

| Hypothesis | If the prediction holds | If falsified | Inconclusive / not closed | Effect on the venue |
|---|---|---|---|---|
| H0 | The model is valid and is reported as fidelity evidence in the methods section | The model is faulty: H1–H5 are not reported, the model is corrected, the fault and the correction are reported | Unclosed health lemmas are listed. H1–H5 are not reported until the health lemmas close | Part of condition (1) |
| H1 | "The minimal set is a cut set and depends on the PQ status of the WebPKI." Operational consequence: for an online verifier, a PQ TLS server certificate is a precondition | If a transferred artefact admits substitution, the classification and the model are first checked for errors. If it is confirmed, the limit of the classification is reported as a new finding. If substitution also holds with classical transport, the WebPKI dependency claim is dropped and this is reported | If rule R3 does not close, the ASP result is reported with the label "unproven rule" | Candidate for condition (2b) |
| H2′ | Phase-change map and robust region (A5) | If the order changes in no regime, the negative finding "time resolution does not change the order" is reported, and the time claim in the title is softened | | Candidate for condition (2b) |
| H3 | M-f sufficient and minimal, M-a/M-b traces, text proposals for HAIP, ARF and TS 119 612 | If an unauthenticated mechanism satisfies G5, the limit of the attacker model is examined and reported. If a component of M-f is unnecessary, the mechanism is simplified, and the result is still publishable [Design v3] | Without an M-a/M-b trace, (2c) is not met | (2c). If the trace is in a final specification (A.3.2.2), TIFS is considered |
| H4 | Cells where the root-first order is insufficient or wasteful | If S5 equals S7 in every cell, the intuition is confirmed and reported, the novelty weakens and the target journal changes [Design v3] | | Condition (2a) |
| H5 | Harvest-and-forge: single-use issuance does not protect, only the validity period bounds the forgery | If enforcement at the verifier prevents forgery, this is reported and the condition of enforcement (shared state and its cost in unlinkability) is discussed | | Supporting |
| H6 | X ≤ c: claim "the software cannot express the policy at API level", with n, Wilson CI, p and effect size | X ≥ u: the majority can express it, the claim is dropped, and C3 is reported in the "feasible" direction. If the majority is reached mainly through L4c, it is reported as a general per-issuer allowlist capability, not as PQ-specific required-set semantics (Section 5.13) [Amendment 11 (2026-10-01)] | c < X < u: "inconclusive", descriptive report only | Weight of C3. Does not change the venue decision on its own |

**Language rule:** every exploratory analysis (not fixed before the runs or before the freeze) is labelled "exploratory" in the text and in the tables.

### 9.3 Decision rule for H6 [Amendment 10 (2026-10-01), Amendment 11 (2026-10-01)]
- **Sample.** Of the n = 31 targets, 30 have a control label (EdDSA 17, ES384 13). SDJWT-021 has none and is excluded from the primary H6 analysis. The primary n_eff is 30 before indeterminate targets are removed.
- **Thresholds for n_eff = 30** (Appendix A, one-sided exact binomial, p0 = 0.5, α = 0.05, uncorrected):
  - X ≤ 10: H6 supported (P(X ≤ 10) = 0.0494),
  - X ≥ 20: H6 falsified,
  - 11 ≤ X ≤ 19: inconclusive.
- **If n_eff changes** (indeterminate targets under Section 5.15, adapter invalidity), c and u are read from Appendix A for the final n_eff. If n_eff falls below 20, only the descriptive rule of Section 7.5 applies, and this is a major deviation (Section 10).
- **Robustness.** Support requires the primary analysis and sensitivity (i) to agree, and falsification requires the primary analysis and sensitivity (ii) to agree. Otherwise the result is reported as "fragile" (Section 7.14). The SDJWT-021 sensitivity analysis (Y = 0) is reported alongside.
- **Control labels.** The label used is recorded per target and reported descriptively (Amendment 4, item 2, and the `kontrol_etiketi` field of the statistics input).
- **Only confirmatory test** [Amendment 11 (2026-10-01)]: H6 is decided by T1 alone. T2–T5 are descriptive and never change the H6 decision (Section 7.10).
- **L4m and L4c** are reported separately, with the L4c interpretation note of Section 5.13. A rejection that shows only missing support for the control-label algorithm is not counted as policy enforcement (Section 5.13).

---

## 10. Deviation policy
- **Before freeze:** changes were allowed, but every change was recorded in the draft change log with date, what changed, why, and which results had been seen when it was changed. The git history remains traceable. This freedom applied only to the C3 items (draft Sections 6–7). It did not apply to the formal part after anchor 3, where every later change was recorded with the label "after the result was seen" [Amendment 3, item 1 (2026-09-24)].
- **After freeze:** the frozen file does not change. Every deviation is added as a dated entry to the deviation log `docs/preregistration/DEVIATIONS.md`, which is created from Section 13 at the freeze (the draft named `00-on-kayit\SAPMALAR.md`). Entries are written only by the study team member who maintains the record. Each entry states:
  - the type of deviation (minor or major),
  - its reason,
  - when it was noticed,
  - its effect on the results,
  - where possible, the analysis according to the original plan as well.
- **Major deviation:** a change of the primary outcome variable, a test, α, the inclusion criteria or the test battery, or n_eff falling below 20. A major deviation requires the approval of the corresponding author (human step İ7) and is reported in the paper in a separate paragraph.
- **Minor deviation:** script bug fixes that do not change results, file paths, formatting.
- **Exploratory analysis:** every analysis added after the data have been seen is labelled "exploratory".

---

## 11. Freeze procedure
1. **Preparation:** the translation branch is merged, `experiment/statistics/SHA256SUMS` is regenerated, the adapter translations are final, the v1.4 manifest is regenerated with `vektor_sayisi` = 230, the discrepancy log `models/sampling/UYUSMAZLIK-KAYDI.csv` is created with its header, and the lists of Section 12.6 are re-verified by diff, with the result written to the freeze record. `experiment/runs/RUNNER.md` (runner interface) and `experiment/oracle/oracle-A/adapter-contract.md` (pre-freeze addendum, its Section 0) were brought in line with this document on 2026-10-03.
2. **When:** after the scientific gate decision (Section 12.1) and before Step 10 starts. The draft's target window was 2026-11-04 to 2026-11-06. The freeze takes place on the date in the header (Section 13.9).
3. **Freeze package:** the files listed in the section "Freeze package" at the end of this document, and this document at `docs/preregistration/PREREGISTRATION-v1.0.md`.
4. **Hashes:** the study team places the package and produces the hash list `docs/preregistration/FREEZE-SHA256SUMS` with `sha256sum`. The run script refuses to run without it (Section 7.19).
5. **Deviation log:** `docs/preregistration/DEVIATIONS.md` is created from Section 13 (Section 10). It is not in the hash list, because entries are added after the freeze and the run script checks the list before every run; its initial content is Section 13 of this document.
6. **Commit and public tag:** git commit and tag `prereg-v1.0`. The commit identity is a placeholder and no personal e-mail address is used. The tagged frozen state is published on the public repository. The publication of the tag is the public timestamp of the freeze, and the term "pre-registered" applies to C3 from that moment (decision of the study lead, recorded with Amendment 11). The draft had assumed a local repository without remote.
7. **Additional external timestamp (only with approval):** for example OpenTimestamps for the hash of the hash list (only the hash leaves the machine), or an archive deposit. This is an external action and an author decision. **Author decision (2026-10-03): OpenTimestamps.** After the freeze commit, the SHA-256 digest of `docs/preregistration/FREEZE-SHA256SUMS` is submitted to the public OpenTimestamps calendars (only the digest leaves the machine). The proof `docs/preregistration/FREEZE-SHA256SUMS.ots` is added in a follow-up commit, because it cannot be part of the list it timestamps, and is upgraded to its complete Bitcoin attestation once that is available. Verification: `ots verify docs/preregistration/FREEZE-SHA256SUMS.ots`.
8. **Record:** the commit SHA, the tag, the hash of `FREEZE-SHA256SUMS` and, if any, the external timestamp proof are recorded in the project log.
9. **Verification:** at the start of Step 10, `sha256sum -c` is run (the run script does this before the first run). If there is a mismatch, Step 10 does not start.
10. **In the paper:** the commit SHA, the tag, the SHA-256 and, if any, the external timestamp proof are reported [Design v3 §15]. The paper uses "pre-registered" only for C3, and "expected verdicts fixed and hashed before the runs (internal record)" for the formal part [Amendment 11 (2026-10-01)].

The draft required the frozen version to show, in its header, the word FROZEN, the date and the difference of H0–H5 since the draft anchor. The header table carries the status and the date. The difference is in Appendix D.

---

## 12. What was known at freeze

This section is a statement of what the study team knew when this version was frozen. The freeze governs the library measurement (H6, C3) and its analysis. The formal results below were obtained before the freeze and are known. Their rules and expected verdicts were fixed and hashed before the runs (internal record, Appendices C and D).

### 12.1 Results of the formal part (H0–H5): known
Source: `models/comparison/H0-RESULT.md`, `models/comparison/HYPOTHESES-RESULT.md`, `models/mutation/README.md`, `models/mechanisms/STEP07-REPORT.md`.
- **H0: satisfied.** (a) Health lemmas: 554 of 554 as expected, of which 550 verified and 4 `executable_learn` lemmas false as the plans expected (Section 4.1). (b) ASP: 0 of 90 cells secured under P0 in Φ1/Φ2, and the Tamarin downgrade trace `R2/M_expect_absent/S1_downgrade_trace` verified. (c) Mutation: 45 of 45 scored mutants killed, score 1.00 (11 equivalent probes and 2 base-insecure mutants reported separately). Literal reading 45 of 47 = 0.957. Both exceed 0.90 (Section 5.17).
- **H1: supported.** Under PQ-authenticated fresh transport, substitution holds for 12 pulled artefact–goal pairs. Under classical transport at nominal τ, none. Transferred artefacts: none, in all 8 channel variants. Tamarin R3 consistent.
- **H2′: supported.** For the rotated and per-token status keys (V2/V3), a08 is needed at fast τ (21 of 21 satisfiable cells) and unnecessary at medium and slow τ (33 of 33). The long-lived variant V1 needs a08 at every τ. Falsification test (i): token lifetime changed the set in 0 of 32 fixed-window cells. Falsification test (ii): the window changed the set in 66 of 180 V2/V3 cell groups. ASP window classes agree with Tamarin R6 in 588 of 588 compared cells.
- **H3: supported.** (a) Without an authenticated per-entity expectation, G5 fails in coexistence. (b) M-a, M-b (OID4VP A.3.2.2) and M-b0 violate all three G5 forms. (c) The simplified M-f with path-class scope is verified for every G5 form and every path form against the different-name CA, same-name CA and classical-root attacks. (d) Each component is necessary.
- **H4: supported (strict counting).** Primary 36 cells: insufficient 18 (12 missing node, 6 missing expectation), wasteful 9, neither secures 9. Under the counting rule of Amendment 8, item 3, the counted candidates are the **6 τ-wasteful cells** of the pre-specified designs, each with a Tamarin instance. The four G4 cells with an unsigned request and WRPRC phase 1 are exploratory (commit `f143bdf`. An earlier version of the result file listed 10 candidate cells, including the four G4 cells).
- **H5: supported.** A trace exists exactly when τ is shorter than the remaining validity. Enforcing single use at the verifier changes nothing. A PQ device key prevents the forgery.
- **Agreement figures:** ASP and z3 agree on all 52,693 queries. Step 7: 762 lemma runs, all closed at ladder step 1, well-formedness 762 of 762 clean, 760 of 762 matched the expectations recorded before the runs.
- **Results that contradict an expectation fixed before the runs** (reported as they are, not used to change any verdict):
  1. M-e and M-e′, `no_rollback`: expected V, observed F. The metadata of a non-migrated issuer is signed with that issuer's own classical key. After the key is extracted, the attacker can show a forged "PQ required" answer and then a forged "none" answer. Restricted to migrated issuers, the lemma is verified (exploratory).
  2. R7h, same-name classical CA: expected V, observed F. A classical CA with the same name bypasses name binding. M-f with path-class scope closes these attacks.
  3. Health question on S1/S2: S2 secures the 9 Φ3 cells, as the Φ3 definition implies (Section 5.10).
- **Exploratory extension (not among the expectations fixed beforehand):** H5 with encrypted responses. Under classical response encryption (ECDH-ES P-256), harvest-now-decrypt-later supplies what the forgery needs. With PQ response encryption, G2 is verified even with a classical device key. All six variants matched the expectations recorded before the runs.
- **Technical gate:** passed, 10 of 10 instances (plus 1 exploratory instance outside the count).
- **Known-answer tests:** first run 2 of 3 (KAT-1 failed because of its own Tamarin encoding, while the ASP core agreed in 109 of 109 cells), after the post-result correction of the KAT-1 test model 3 of 3 (Section 5.19).
- **Scientific gate evidence** (`models/comparison/SCIENTIFIC-GATE.md`, commit `4f8410a`):
  - Condition (1): ASP–z3 52,693 of 52,693, technical gate sample 10 of 10, mutation 1.00 (literal 0.957), known-answer tests 3 of 3 after the documented post-result correction (first run 2 of 3). Condition (1) holds with this documented deviation. Stratified Step 5B sample (`models/sampling/5b/REPORT.md`): agreement on closed samples 183 of 183 (149 one-missing falsified and 34 minimal verified, as predicted), 0 differences; 177 of 177 when the samples whose health lemma did not close are left out. For the 10 % allowance, the 13 instances outside the translator's scope and the 4 not-closed instances are counted together (conservative, Section 13.2): 17 of 200 = 8.5 %, within the allowance.
  - Condition (2): candidates (2a) (6 τ-wasteful cells), (2b), (2c)(i) (commitment extensions of reddy and vicente type bypassed when carried only in a classical chain, closed by the path-class expectation) and (2c)(ii) (M-e′) hold in the model. A first novelty assessment rated (2c)(i) non-obvious, (2a) and (2b) uncertain, and (2c)(ii) and H5 obvious.
  - The internal methodological review of 2026-10-01 found that part of the (2c)(i) result is stated in the drafts' own text. The novelty assessment was repeated with this counter-evidence (sheffer-02 §3.2, which requires the whole path to be PQ, vicente-02 §4.2 and §7, which declare the commitment advisory, reddy-01 §3.1, which does not change path validation and has expired, and RFC 5280). Result: the commitment-bypass candidate (2c)(i) is obvious or partially anticipated, (2a) and (2b) are uncertain, and (2c)(ii) is obvious.
  - **Gate decision** (recorded by the study lead on 2026-10-01): **condition (2) is not met.** Under the rule of Section 9.1 only condition (1) holds, so the target is a systems or standards venue: Computer Standards & Interfaces (Elsevier). The authors confirmed the gate decision on 2026-10-03 (human step İ7).
  - Step 5B (completed 2026-10-01): 200 instances selected, 187 translated, 13 outside the translator's scope (all involve the issuer metadata artefact `a05_meta`), 183 closed, 4 not closed (G2 cells at the 12 GB limit in every ladder step). Instances that ran out of memory at 4 GB were re-run at the pre-registered 12 GB limit. A runner defect (a run killed at the memory limit was recorded as a well-formedness failure and the ladder stopped) was found after the runs and corrected; ladder steps 3 and 5 were then run for the 13 affected lemmas, none closed, and no verdict of a closed sample changed (`models/sampling/5b/REPORT.md`, procedure record).

### 12.2 Results of the pre-freeze validity gate: known
The validity gate checks that an adapter drives its library correctly: per algorithm, a valid object is accepted and an object with a corrupted signature is rejected. It is not part of the measurement. Sources: `experiment/runs/outputs/prefreeze-v1.3/GATE-SUMMARY.csv` (JWS/COSE level, 31 targets) and `experiment/runs/outputs/prefreeze-sdjwt/GATE-SUMMARY-SDJWT.csv` (SD-JWT format, 8 targets).
- **Targets passing per algorithm (JWS/COSE level):** ES256 29, EdDSA 16, Ed25519 7, **ES384 27** (gate on battery v1.4 after the correction of Decision D9, `experiment/runs/outputs/prefreeze-v1.4/`, Amendment 10), ML-DSA-65 6, composite ML-DSA-65-ES256 0.
- **The ES384 validity gate results were known before the freeze:** 27 of 31 targets pass the ES384 gate (24 on the first generation of v1.4; COSE-034, COSE-035 and COSE-036 failed it there only because of the wrong kid, Section 13.13, and keep the label EdDSA). They determined the control labels (`experiment/runs/CONTROL-LABELS.csv`: EdDSA 17, ES384 13, no label 1, Section 7.7). No battery result in the ES384 arm is known.
- Passing ML-DSA-65: COSE-036, JOSE-001, JOSE-009, JOSE-102, SDJWT-015, SDJWT-018.
- Passing EdDSA: COSE-034, COSE-035, COSE-036, JOSE-009, JOSE-031, JOSE-033, JOSE-055, JOSE-070, JOSE-071, JOSE-083, JOSE-092, JOSE-102, SDJWT-010, SDJWT-015, SDJWT-018, SDJWT-025. Every target that passes Ed25519 also passes EdDSA, so no target needs the Ed25519 fallback label.
- No target passes the composite gate.
- SD-JWT format gate: SDJWT-015 and SDJWT-018 pass all algorithms in both `typ` forms. SDJWT-010 and SDJWT-025 pass ES256 and EdDSA. SDJWT-001 and SDJWT-004 pass ES256 only. SDJWT-021 passes only ES256 with `vc+sd-jwt`. SDJWT-002 accepts the corrupted objects for ES256 and EdDSA.
- Consequences known at freeze: which targets are TK1 in the ML-DSA-65 arm (`experiment/runs/TK-ASSIGNMENT.csv`), that all targets are TK3 in the composite arm, which 15 targets support neither EdDSA nor Ed25519, the control label of every target, and that SDJWT-021 has no control label (Amendment 10). Per-target details: Appendix E.

### 12.3 Observations made during adapter construction (API review and smoke tests, not battery vectors): known
These observations come from documentation, API scans, source reading and synthetic smoke tests made while the adapters were written. No battery vector other than the validity vectors was run.
- No target exposes a path-class certificate policy. `L4-YOL` is therefore not expressible for every target [Decision D6], which determines the B2 flag in advance.
- SDJWT-002 computes the issuer signature check but does not use its result, so objects with corrupted signatures verify (source and evidence in `experiment/runs/adapters/SDJWT-002/evidence/`) [Decision D1]. Its header alg is checked only for support and the verification uses the key's algorithm.
- JOSE-102 does not compare the header alg with the signer. JOSE-089 verifies only the first signature of a General JSON object. JOSE-002 reduces the allowlist to the key type. SDJWT-021 hard-codes `typ = vc+sd-jwt` and ES256. COSE-036 rejects −7 and −8 in its default build.
- B6 (format support) and the custom-code line estimates (B4) of some targets were recorded in the adapter notes, as the contract requires B6 to be decided beforehand.
- **Adapter conformance test** [Decision D9 (2026-10-03)]: 38 objects outside the battery, 258 job rows, acceptance rows only, run on all 31 adapters (`experiment/runs/conformance/`). After the corrections of Decision D9 every expected acceptance holds, except 37 rows of library behaviour of SDJWT-002, SDJWT-010, SDJWT-018 and SDJWT-021. Its bearing on the outcome variables is stated in Section 12.5.
- The complete record of these observations is in the `NOTES.md` and `evidence/` files of `experiment/runs/adapters/`, which are part of the freeze package. The list above gives the observations that bear on the outcome variables.

### 12.4 Not known at freeze
- When Amendments 10 and 11 were written, only the pre-freeze validity gate had been run on the targets.
- No outcome of the measurement battery (battery cases K1–K11 and the secondary vectors) on any target.
- No outcome of the ES384 control arm, beyond its validity gate.
- Only validity vectors were run on the targets: V± and CMP00/CMP01 (`experiment/runs/jobs-prefreeze-v1.3.jsonl`, and `experiment/runs/jobs-prefreeze-v1.4.jsonl` with the ES384 arm) and the 16 SD-JWT-format gate vectors (`experiment/runs/vpm-sdjwt/`), and, outside the battery, the conformance objects of Decision D9 (acceptance rows only, Section 12.5).
- Not run in any form, including the conformance test: the rejection rows on which Y_L4, D_soy, B5 and L1 separate targets (T2K, T3, `VPLUS_ES256` under the L4 family, `VPLUS_X` under `IZIN-A`), K5, K10 and all secondary vectors.

### 12.5 Prior knowledge
- **Pilot P3 (external audit, 5 libraries):** `jose` 6.2.12, `@sd-jwt/core` 0.21.0, `jwcrypto` 1.6.1, `Authlib` 1.8.0, `joserfc` 1.7.5.
  - In none of them was a "required algorithm set" option observed.
  - All 5 accepted the stripped document (with classical proxies, General JSON).
  - Of these, `jose` (JOSE-009) and `@sd-jwt/core` (SDJWT-015) are in n, at the same versions. `jwcrypto` is the verification delegate of SDJWT-018. Authlib was excluded and joserfc is a backup. They are measured again, flagged "seen in the pilot", and the pilot sensitivity analysis applies (Section 7.14).
- **Second pilot (2026-10-01):** in a separate working copy of the study, a pilot measurement was made on 12 libraries, with vectors **different** from this battery, before this pre-registration was frozen:
  - pyjwt, python-jose, jwcrypto, authlib, joserfc,
  - jose, jsonwebtoken (Node.js, 9.0.3),
  - golang-jwt, jose2go, jwx, cristalhq/jwt, kataras/jwt.
  - Qualitative observations: jose and jwcrypto use "at least one valid" semantics, and an allowlist containing only the PQ algorithm can make the PQ signature mandatory. authlib and joserfc use "all present valid" semantics and reject the whole JWS when they do not recognise the PQ signature. joserfc rejects signatures longer than 1,024 bytes (ML-DSA-65 has 3,309 bytes). jwx rejects parsing on an unknown algorithm. Most libraries have no JSON serialisation.
  - Six of these libraries are in n: JOSE-009, JOSE-033, JOSE-034, JOSE-065, JOSE-083, JOSE-084. jwcrypto is the delegate of SDJWT-018.
  - **Effect:** this information was **not used** to change the hypotheses or thresholds. The H6 threshold, the battery and the target list were fixed at the anchors of 2026-09-24 to 2026-09-26. The raw outputs of this pilot are not evidence.
- **Other pilots of the external audit:** pilots P1 (Tamarin, 6 variants), P1b (ProVerif, 4 variants) and P2 (ASP/z3, 48 queries): results known. They are toy models, not the paper's models, and their verdicts are not evidence (Ö12: the pilot Tamarin model gives a well-formedness warning). Pilots P4 (sizes and thresholds) and P5 (LOTL) are deterministic measurements, not hypotheses. P5: 43 pointers, 107 of 107 TL signer certificates classical, LOTL signature RSA-4096.
- **Internal methodological review (2026-10-01)** [Amendment 11 (2026-10-01)]: it saw no measurement data. It estimated that many compact-only targets may reach L4c through a per-issuer allowlist, so that H6 may be falsified or remain inconclusive (an estimate, not data). This estimate motivated the L4c interpretation note. It did not change the primary variable, the thresholds or the decision rule of H6.
- **Conformance test of Decision D9 (2026-10-03):** its objects mirror battery vectors (same headers, keys and signature order, a different payload), so a mirrored acceptance row predicts the battery row. Known from it:
  - the L4 form of every target, and which targets record their Y-determining configuration as not expressible (all covered by the evidence rule, Section 5.14);
  - every target accepts the mirrored acceptance rows of its Y-determining configuration where that configuration is expressible (L4m: T1K and T5K; L4c: `VPLUS_X` and the legacy issuer under `L4`), except SDJWT-002, whose library cannot parse JWS-level objects as SD-JWT (it reads `_sd_alg` as required, while RFC 9901 §4.1.1 makes the claim optional). For the L4c targets, Y_L4 therefore depends at freeze only on the rejection of `VPLUS_ES256` under `L4`, which was not run;
  - **Effect:** no hypothesis, threshold, decision rule or reading was changed. The corrections of Decision D9 were made only where an adapter departed from the adapter contract or this document, and the code review that found the L4c defect used no outcome. This pre-knowledge is one-sided: no rejection row was run.
- **Direction of the literature:** the conclusions of Mulder 2026, NCSC 2025, RFC 9955, composite -04 §6.2, Kim et al. 2026 and Lee et al. 2026 are known. They count as "obvious" (Section 5.21).

### 12.6 Integrity of anchored identities at freeze
The renaming and translation of 2026-10-01 (Section 13.8) changed the bytes of several anchored files without changing their content.
- Unchanged since their anchors: `vectors/v1.3/MANIFEST.json`, `vectors/v1.3/SHA256SUMS`, `keys/v1/SHA256SUMS`, `keys/v1.3/SHA256SUMS`, `experiment/inventory/SELECTION.csv`, `experiment/inventory/FRAME.csv`, `models/known-answer-tests/nsurum/kat_nsurum.tsv`, and the oracle inputs `oracle-A/decisions.tsv` and `oracle-B/decisions.tsv` (the hashes recorded in `experiment/oracle/merged/SUMMARY.json`).
- Changed in bytes: `experiment/vector-generator/BATTERY-MAPPING.md` (one path string), `models/mechanisms/on_kayit_varyantlar.tsv` and `models/tamarin/betik/on_kayit_h3_sadelestirme.tsv` (wording of comment lines only), `models/tamarin/betik/varyantlar.tsv` (the anchored content followed by the exploratory R7hx rows of 2026-09-24, as recorded in Appendix D), `experiment/inventory/CRITERIA-DRAFT.md` (translated, formerly `KRITERLER-TASLAK.md`), and `experiment/statistics/SHA256SUMS` (regenerated).
- The anchored hashes cited in this document refer to the file versions at the anchor commits of Appendix C.
- Both lists are re-verified by diff at the freeze (Section 11, step 1).

---

## 13. Deviations from the draft
Each item states what departs from draft v0.11, why, and its effect.

### 13.1 Treatment class TK2 out of scope (2026-10-01)
- **Change:** TK2 (plug-in) is removed. A target without native ML-DSA support is TK3.
- **Reason:** no hypothesis depends on TK2. T2 was to be run on TK1 targets, or reported descriptively if the data were insufficient. Amendment 11 made it descriptive (Section 13.11).
- **Effect:** T2 and T3 are restricted to TK1. Targets with a documented plug-in point (pyjwt, jjwt, jose2go, go-cose, sd-jwt-payload and others) become TK3. With no composite support at all, T2 has no data in the main arm. Amendment 11 then made T2–T5 descriptive (Section 13.11).

### 13.2 Step 5B sample: instances outside the translator's scope
- **Change:** of the 200 instances selected under Section 5.18 (189 cells, seed 20260926), 13 instances (in 12 distinct cells) are outside the scope of the ASP-to-Tamarin translator. Every one of them involves the issuer metadata artefact a05: its unsigned variant (9 instances) or a05 as the target of an expectation carrier (4 instances). 187 instances were translated.
- **Effect:** the 13 instances are listed in `models/sampling/5b/ceviri_disi.tsv` and reported separately. They count neither as agreement nor as disagreement. For the allowance of at most 10 % not-closed instances (Section 5.18), they are counted together with the not-closed instances (conservative reading, decision of the study lead). Result: 13 + 4 = 17 of 200 = 8.5 %, within the allowance (Section 12.1).

### 13.3 Version pinning
- **Change:** the targets are pinned to the versions of the build pretest of 2026-09-25 (`experiment/environments/build-results.csv`), not to "the latest published release at freeze" (Amendment 8, item 14).
- **Reason:** the treatment classes, the API scans and the adapters were built against these versions.
- **Effect:** the pinned versions are listed in Appendix E. A target without a release is pinned to a commit (wolfCOSE `f907071b`).

### 13.4 Battery v1.3 and oracle v1.3 derived by case mapping
- **Change:** Amendment 8, item 11 required oracles A and B to re-derive with their own scripts, using the definitions of items 7–10, at least for the primary vectors and V±. Instead, the merged oracle `experiment/oracle/merged/decisions_v13.tsv` was produced by one script (`derive_v13.py`) that takes the v1.2 decisions of A (858 rows) and B (732 rows), applies items 7–10 as normalisation rules, maps the COSE vectors to the JOSE vector of the same case (COSE and L4c) and adds the L4c-3 rows from the quotation in the battery mapping.
- **Provenance of the 1,845 rows** [computed from the `kaynak` column]: A = B 152, single oracle 1,118, A ≠ B 10 (→ indeterminate), one of them indeterminate 3 (→ indeterminate), item 8 (B1 flag) 96, item 9 (arm-independent) 12, COSE case mapping 418, L4c-3 36. Decisions: accept-classical 460, accept-hybrid 255, reject 861, arm-independent 24, B1 flag 108, indeterminate 137.
- Among the rows that oracle A classifies as primary, only the `L4` rows (47) and the `P0` rows (20) rest on agreement of the two oracles. 229 primary rows rest on oracle A alone (`GEC` 39, `IZIN-A` 37, `IZIN-AX` 37, `L4-S` 47, `L4-Y` 47, `P1` 20, `L4-YOL` 2), and 82 primary `P2` rows on oracle B alone. Oracle A's `P1` and oracle B's `P2` are different configurations (W differs) and are not compared. On 61 shared keys they differ in 18 rows, all secondary [computed]. The V± rows agree between `GEC` (A) and `P2` (B) on all 14 shared keys.
- The merged file has no primary/secondary column. Primary status is read from the battery mapping.
- **Resolution** (decision of the study lead): the `L4` rows that determine Y_L4 and T1 rest on agreement of the two oracles, directly or through the case mapping of rows where they agree (COSE vectors, ES384 counterparts). The exception is the legacy-issuer row of L4c (L4c-3), which neither oracle derived because the legacy issuer was added in v1.3. It is taken from the quoted rule of the battery mapping (Amendment 2, item 6). The single-oracle rows feed only descriptive variables. This satisfies Amendment 8, item 11 for the confirmatory part [computed from the `kaynak` column of `decisions_v14.tsv`].

### 13.5 Tamarin wall-time record of 7,024 s
- One Step 7 run (`MF_tas_federasyon_bayat` / `M_weak_path_forgery`) recorded 7,024 s of wall time on 2026-09-26, above the 10-minute limit per ladder step.
- On 2026-10-01 the same command was re-run under a 600 s limit: 78 s, same verdict (verified).
- The record is an artefact of the host machine being suspended. Memory never exceeded 5.4 GB.

### 13.6 Unexpected results for M-e and M-e′
- `no_rollback` was expected V and observed F for both (Section 12.1). The results are reported as they are and are not used to change any verdict.
- Exploratory, not among the expectations fixed beforehand: restricted to migrated issuers, the lemma is verified (M-e in 38 steps, M-e′ in 45 steps, `models/mechanisms/kesif/me_gocmus/`).
- Reading: an expectation carried by an object that is signed with the protected entity's own breakable key cannot protect that entity.
- The M-e′ result is a candidate under (2c′)(ii) (Section 5.21). The independent novelty assessment rated it obvious, as an instance of the first-contact limitation of host-learned policies (Section 12.1).

### 13.7 Pre-freeze decisions D1–D7 (2026-10-01)
- **D1, SD-JWT-format validity vectors.** SD-JWT targets are gated with 16 SD-JWT-format vectors (`experiment/runs/vpm-sdjwt/`), because the JWS-level pair is not a well-formed SD-JWT VC for libraries that require `_sd_alg` or a specific `typ`. SDJWT-021 is measured in its `vc+sd-jwt`/ES256 form. SDJWT-002 is kept although it accepts corrupted signatures, flagged `integrity-failure`, and every analysis is also reported without it. Recorded deviations with D1 as basis: vectors outside the battery are used for the validity gate (Section 7.8), and the adapter-invalid rule is not applied to SDJWT-002 (Section 5.15). SDJWT-002 is flagged and every analysis is reported without it.
- **D2, JOSE-102.** ML-DSA-65 only through `@_spi(PostQuantum)`. Primary TK3, sensitivity TK1.
- **D3, wolfCOSE.** Measured with the documented build flag `WOLFCOSE_ENABLE_DEPRECATED_ALGS`. Default build reported descriptively.
- **D4, control-arm label order and battery v1.4.** This decision is Amendment 10 (Section 13.10). Its first wording of 2026-10-01 (control-arm level `undetermined` for the 15 targets without EdDSA or Ed25519) was replaced before the freeze.
- **D5, documented caller patterns** count as the library's verification path (COSE-035, SDJWT-010, SDJWT-015, SDJWT-025).
- **D6, policy-name suffixes.** The suffixes split only the expected outcome. `P2` uses the library default. `L4-YOL` is not expressible for every target.
- **D7, calling conventions** of the two adapter families (Section 7.19).

### 13.8 Language edit of the repository (2026-10-01)
- Repository files were translated to English and process notes were reworded neutrally. Top-level and second-level folders were renamed (for example `deney/` → `experiment/`, `model/` → `models/`, `deney/uretec/` → `experiment/vector-generator/`, `deney/envanter/` → `experiment/inventory/`, `deney/istatistik/` → `experiment/statistics/`, `model/mekanizma/` → `models/mechanisms/`, `01-korpus/` → `spec-corpus/`, `02-izlenebilirlik/` → `traceability/`, `arac/` → `tools/`, `veri/` → `data/`).
- Internal project-management notes, design-process copies, literature full texts and third-party specification texts were removed from the repository (commit `fa44c06`), including the draft itself.
- The integrity lists (`SHA256SUMS`, `*.sha256`) were kept; no recorded digest was changed. The renaming rewrote the recorded path in six entries (a decision-note file name in two lists, and the folder `sentetik-testler/veri/` written as `sentetik-testler/data/` in four entries of `experiment/statistics/SHA256SUMS`, although the folder itself kept its name). Where the release translated or renamed a listed file, the recorded bytes are kept in `archive/hash-anchored/`; `tools/verify_anchors.py` checks every record and `docs/INTEGRITY.md` explains the classes (current, archived, noted). `experiment/statistics/SHA256SUMS` is regenerated at the freeze. Effects on anchored identities: Section 12.6.
- The same blanket rewrite had changed the two references to `sentetik-testler/veri/` in `experiment/statistics/run_all.sh` to `data/`, so the script could no longer write the statistics list. This was corrected on 2026-10-03 before the list was regenerated (script bug fix that does not change results, minor deviation in the sense of Section 10).
- Code comments and diagnostic messages of the hand-written scripts were translated on 2026-10-02/03; a comment-only check (`tools/verify_comment_only.py`) shows that no code changed. Model files (`.lp`, `.spthy`), generated samples and recorded outputs keep their Turkish comments.
- A message-only rewrite of the history on 2026-10-01 changed the commit identifiers of anchors 4–9 (trees and dates unchanged). Appendix C gives the current identifiers.
- The run files and folders under `experiment/runs/` were renamed to English names in commit `0ba930d` (for example `adaptorler/` → `adapters/`, `kosu/` → `outputs/`, `isler_v14.jsonl` → `jobs-v1.4.jsonl`, `KOSUCU.md` → `RUNNER.md`), and the oracle method files on the translation branch (`adaptor-sozlesme.md` → `adapter-contract.md`, `YONTEM.md` → `METHOD.md`).
- Paths in this document use the new names.

### 13.9 Interpretations and further deviations recorded at consolidation
- **Freeze date** earlier than the draft's target window (2026-11-04 to 2026-11-06), because the scientific gate decision was taken on 2026-10-01.
- **Strategy file** in JSON at `models/asp/sorgular/stratejiler_taslak.json` instead of YAML at the path named by Ö5 (Section 5.9). Its content was fixed before the comparison and Step 8 checks it by a canonical hash.
- **OJEU expectation hook** brought into the scope of M-f on 2026-10-01, after the formal results were known, contrary to Amendment 8, item 5 (Section 5.1). An addition after the results. It changes no verdict.
- **Fair-metric variant of H4** added on 2026-10-01, after the formal results were known, as a sensitivity analysis (Section 5.21). It changes no verdict.
- **H0 condition (a)** read as "every health lemma has the verdict fixed before the runs" (554 of 554 as expected, 550 verified, four `executable_learn` lemmas fixed as false before the runs). Explicit interpretation, accepted as the frozen reading (Section 4.1).
- **Mutation score** reported in both readings: 45/45 = 1.00 with the two base-insecure mutants excluded, as the score script does, and the literal 45/47 = 0.957. The threshold of 0.90 holds under both (Section 5.17).
- **V± configuration** run under `GEC` instead of `P2` (Section 5.20). Deviation. The decisions are identical on the 14 rows where both exist.
- **Known-answer tests:** first run 2 of 3, because KAT-1 failed in its own Tamarin encoding while the ASP core agreed in 109 of 109 cells. Corrected run 3 of 3, labelled post-result correction. Gate condition (1) holds with this documented deviation (Section 5.19).
- **H4 result file** changed on 2026-10-01 (commit `f143bdf`) from 10 candidate cells to the 6 τ-wasteful cells counted under Amendment 8, item 3, with the four G4 cells exploratory. The rule did not change. The earlier text of the result file did not apply it.
- **Public repository:** the draft's freeze procedure assumed a local repository only. The frozen state is published as the tag `prereg-v1.0` of the public repository (Section 11).
- **Statistics and analysis scripts** updated before the freeze for the rules of this version: symmetric fragile falsification (Amendment 8, item 17), sensitivity `gecersiz_y0` (Amendment 10), descriptive flag of T2–T5 (Amendment 11), incidental rejection, F_K and F_T against the `L4` rows, and the pilot set of both pilots (Sections 5.13, 7.14, 7.19).
- **Runner documentation:** `experiment/runs/RUNNER.md` and the adapter contract still describe earlier states (row counts of v1.3, battery v1.2, TK2). They are updated before the freeze (Section 11, step 1).

### 13.10 Amendment 10 (2026-10-01): control-arm fallback label ES384 and battery v1.4
- **Change:** the control-arm label order becomes EdDSA, then Ed25519, then ES384 (extends Amendment 4, item 2). The measurement battery becomes v1.4 = v1.3 (byte-identical) + 30 ES384 counterparts of the control-arm vectors. The oracle becomes v1.4 = v1.3 + 357 `kontrol-ES384` rows derived by case mapping. The measurement job list becomes `experiment/runs/jobs-v1.4.jsonl` (2,202 rows). Adapters see v1.4 at the path `/v/v1.3` (superset).
- **Reason:** 15 of the 31 targets support neither EdDSA nor Ed25519. The control arm exists to separate the expressibility of the policy from PQ support, and ES384, a second classical algorithm of the same family, serves that purpose. Under the first wording of decision D4 these 15 targets would have had no Y_L4 value and n_eff would have fallen to at most 16, below the inferential bound of Section 7.5.
- **Result:** control labels EdDSA 17, ES384 13, none 1 (`experiment/runs/CONTROL-LABELS.csv`). SDJWT-021 verifies only ES256, cannot express a two-algorithm required set, is excluded from the primary H6 analysis and counted as Y = 0 in a sensitivity analysis. SDJWT-002 keeps the label EdDSA and the flag of Decision D1.
- **Effect on H6:** the primary n_eff is 30 before indeterminate targets are removed. Thresholds for n_eff = 30: support X ≤ 10, falsification X ≥ 20 (Appendix A, P(X ≤ 10) = 0.0494). If n_eff changes, the thresholds are read from Appendix A (Section 9.3).
- **Known when written:** the validity gate results, including the ES384 gate (24 of 31 targets passed). **Not known:** any battery outcome.
- **Battery mapping:** each ES384 counterpart inherits the primary or secondary status of its EdDSA source vector, as the case mapping of the oracle does.
- **Nature:** a change of the battery before any battery vector was run on a target. Under the battery rule of Section 7.8 it requires a new identity, which is fixed by the freeze of this version.

### 13.11 Amendment 11 (2026-10-01): narrowing of the C3 analysis and wording of the formal part
Decisions of the study lead after an internal methodological review. Recorded before any measurement data existed: only the pre-freeze validity gate had been run.
- **H6 and T1 unchanged:** primary variable Y_L4, n_eff = 30, support X ≤ 10, falsification X ≥ 20, robustness rules. T1 is the only confirmatory test.
- **T2–T5 descriptive** (Section 7.10). Reason: with the plug-in class removed, the ML-DSA-65 arm has 5 TK1 targets, so the exact McNemar test cannot go below p = 0.0625, and T3 cannot go below p = 0.33. T2 and T3 had no power. No p-value, test decision or Holm correction is reported for T2–T5. Original plan: Section 7.10, superseded plan.
- **Historical baseline and known-bug recall removed**, with evidence component D7 (Sections 6.2, 7.16).
- **L4c interpretation note** added: for compact-only targets L4c in effect measures a per-issuer algorithm allowlist (Section 5.13).
- **Incidental rejection rule** added for the control arm: a rejection caused by missing support of the control-label algorithm (in particular ES384) is coded as not supported, not as policy enforcement (Section 5.13). Amendment 10 did not contain such a rule. The adapter contract has one only for L3.
- **Evidence rule:** second independent attempts only for targets whose "not expressible" verdict enters T1 (Section 5.14).
- **Wording:** the formal part (C1, C2) is described as "expected verdicts fixed and hashed before the runs (internal record)". "Pre-registered" applies to the C3 measurement only, from the public freeze of this document (Sections 1.2, 11).
- **Known limitations** of the independent derivations stated (Section 1.6).
- **Reference verifiers and the end-to-end demonstration (Step 11) removed** (decision of the study lead, not needed for any claim): evidence component D8, the reference verifiers of Section 7.4, the week 8 check and the emulator condition of week 10 (Section 9.1), and the emulator references in Sections 4.2, 5.21 and 5.22.
- **Guiding principle** stated (Section 1.3): T1/H6 and its computation chain are the only confirmatory element of C3. All other C3 outputs are descriptive.
- **Adopted into the frozen package:** sensitivity thresholds from their own sample size (statistics note N-2), the reading of Section 7.12 (N-12) and the tolerances of the two implementations (N-8). The pilot sensitivity excludes the targets of both pilots. SDJWT-021 enters only the sensitivity `gecersiz_y0` (Section 7.14).
- **ES384 counterparts** inherit the primary or secondary status of their EdDSA source vectors (Section 7.8).
- **Unchanged:** the measurement run, the battery v1.4 (apart from the corrected manifest count), the oracle v1.4, the job list and the decision logic of the adapters.

---

### 13.12 Corrections of the analysis chain before the freeze (2026-10-03)
- **Change:** a review of the analysis chain found defects in the analysis script written before any measurement (commit `ebeded0`) and in the statistics package. They were corrected before the freeze and tested on synthetic outputs only: (1) a conjunction of checks became indeterminate when one cell was unstable although another cell deviated stably, so a target with a determined Y_L4 = 0 would have left n_eff (and counted as Y = 1 in sensitivity (i)); (2) the inputs of the sensitivity analyses of Decisions D1 and D2 were not written; (3) the statistics schema did not accept the control label ES384 of Amendment 10, so the statistics package rejected every input that contains an ES384 target; (4) a target without a published release (COSE-036) had no reason for its missing `surum_8725bis_sonrasi`; (5) B2 counted rows of an unsupported format; (6) the adapter run script had CRLF line ends, which break it on Linux, and the measurement script did not stop when its directory could not be entered.
- **Effect:** no rule of this document changes; the scripts now implement the rules as written. No battery vector had been run on a target. Public record: issue #5 and pull request #6 of the repository.

### 13.13 Pre-freeze decisions D8 and D9 (2026-10-03)
- **D8, evidence rule.** Second attempts for the 7 targets whose Y-determining configuration was recorded as not expressible, made in a separate session without access to the adapters. Reconciliation rule: L4 is expressible when the library enforces the policy that the caller configures; a check written by the caller inside a callback while the library enforces no algorithm policy is custom code (B4). Results in Section 5.14. COSE-014 was found expressible through designated-signer verification, and two defects of its adapter (kid passed as text, kid read only from the protected header) were corrected.
- **D9, adapter conformance review.** A review of all 31 adapters against the adapter contract and Section 5.13, without any battery outcome, and a conformance test on objects outside the battery (acceptance rows only). Changes:
  1. **Legacy-issuer record of L4c:** 11 per-target adapters (JOSE-001, JOSE-002, JOSE-031, JOSE-070, JOSE-071, JOSE-087, JOSE-089, JOSE-102, COSE-035, COSE-036, SDJWT-002) applied R = {X} to every issuer, so the legacy-issuer rows would have been rejected by the adapter. All adapters now select the record by the `iss` of the object (Section 5.13). Only the L4-family rows of the two L4C vectors change.
  2. **Issuer identification:** COSE-014 and COSE-034 identified the legacy issuer from the vector id; they now read the `iss` of the COSE payload. No row changes.
  3. **Battery v1.4:** 9 COSE ES384 counterparts carried the kid of the Ed25519 key in the unprotected header. The generator was corrected and v1.4 generated again; only these 9 files and the manifest files changed. This is a deviation from "battery v1.4 unchanged" in Section 13.11. Gate re-run: COSE-034, COSE-035 and COSE-036 now pass ES384; no control label changes.
  4. **Defects found by the conformance test:** COSE-001 (kid decoded as text), COSE-014 (COSE_Sign key without an ES256 signer), SDJWT-015 (multi-signature L4/L4-S configured as the single-signature allowlist; now `ifade-edilemedi`), and the error class of a `KeyError` in the shared Python adapter.
  5. **Evidence rule:** second attempts for COSE-035 and COSE-036 (Section 5.14).
- **Deviations recorded:** objects outside the battery other than the validity vectors were run on the targets before the freeze (Section 12.4), with the pre-knowledge stated in Section 12.5; battery v1.4 changed in 9 files after Amendment 10; the operational reading of "same verifier instance" for L4c is fixed by Decision D9.
- **Effect:** no hypothesis, threshold or decision rule changes. The analysis script is unchanged. Public record: pull request #8 of the repository.

## Appendix A. One-sided exact binomial critical values (p0 = 0.5, α = 0.05) [computed and verified]
- c: the largest value with P(X ≤ c) ≤ 0.05 ("absence of a majority").
- u = n − c ("majority", by symmetry).

| n | c (≤) | P(X ≤ c) | u (≥) | n | c (≤) | P(X ≤ c) | u (≥) |
|---|---|---|---|---|---|---|---|
| 20 | 5 | 0.0207 | 15 | 31 | 10 | 0.0354 | 21 |
| 21 | 6 | 0.0392 | 15 | 32 | 10 | 0.0251 | 22 |
| 22 | 6 | 0.0262 | 16 | 33 | 11 | 0.0401 | 22 |
| 23 | 7 | 0.0466 | 16 | 34 | 11 | 0.0288 | 23 |
| 24 | 7 | 0.0320 | 17 | 35 | 12 | 0.0448 | 23 |
| 25 | 7 | 0.0216 | 18 | 36 | 12 | 0.0326 | 24 |
| 26 | 8 | 0.0378 | 18 | 37 | 13 | 0.0494 | 24 |
| 27 | 8 | 0.0261 | 19 | 38 | 13 | 0.0365 | 25 |
| 28 | 9 | 0.0436 | 19 | 39 | 13 | 0.0266 | 26 |
| 29 | 9 | 0.0307 | 20 | 40 | 14 | 0.0403 | 26 |
| 30 | 10 | 0.0494 | 20 | | | | |

- The rows n = 25, 30 and 40 match Design v3 §7.12 exactly.
- For the primary n_eff = 30: P(X ≤ 10) = 26504551/536870912 = 0.049369 [computed]. All 21 rows were reproduced by both implementations of the statistics package.
- Rule for any other n_eff: the same definition applied to n_eff.

**Widths of the Wilson 95 % CI [computed]:** n = 25, k = 18: 33.3 points. n = 30, k = 21: 31.2 points. n = 40, k = 28: 27.4 points.

## Appendix B. Seeds

| Use | Seed | Status |
|---|---|---|
| Credential generator | 20260924 | Not used. The generator is fully deterministic (HKDF-SHA256 from fixed IKM, salt and labels). Kept for historical traceability [Amendment 6, item 6 (2026-09-25)] |
| Mutation | 20260925 | |
| Sampling (Step 5B, technical gate selection) | 20260926 | The technical gate selection orders by `sha256("20260926|<context>|<identifier>")` (`models/sampling/secim/teknik_kapi_secim.py`) |
| Cluster bootstrap | 20260927 | Section 7.13 |
| Random differential test (D2) | 20260928 | |
| Overhead order shuffling | 20260929 | No longer used after the removal of the timing measurement [Amendment 8, item 18] |
| Synthetic statistics tests | 910001–910005, 910010 | Synthetic test data only, not analysis seeds |

## Appendix C. Amendment register

Commit identifiers refer to the current repository history. The draft recorded identifiers from before the message-only rewrite of 2026-10-01: `6f55589` → `f80232b`, `facbf26` → `2c70536`, `998276a` → `68e0478`, `2182528` → `19706ff`, `2d16592` → `97d6e3a`, `7737bb7` → `e0b83fa`. Trees and dates are unchanged.

| Amendment | Date | Draft version, anchor, commit | Content | Known when written | Not known when written |
|---|---|---|---|---|---|
| 1 (Ö1–Ö12) | 2026-09-24 | v0.2, anchor 1, `af02c6b` | H2′, narrowing of gate condition (2c), H4 candidate cells, mechanism classes, strategies S0/S8, H6 test framing and four-valued oracle, artefact set, windows and grids, policy parameters, decisions on open questions, two forms of G5, exclusion of pilot evidence | Step 1 corpus and matrix, Step 2 tool acceptance, Step 4 Tamarin R1–R5 results (196 of 196 expected, mutation 11 of 11, Datalog↔Tamarin 44 of 44, `X_alt_ca`, early signals for H3 and H5), literature analysis, pilot results (not evidence) | Step 3 ASP results, Step 5A R6/R7 and ProVerif, Step 7, C3 |
| 2 | 2026-09-24 | v0.3, anchor 2, `eaa8037` | C3 sample (E2, quotas 18/8/5, n = 31), thresholds for n = 31 (replaced by the n_eff = 30 thresholds ≤ 10 and ≥ 20 after Amendment 10), L4m/L4c, TK1–TK3, MR4, delegation sensitivity. Fixed files: `SELECTION.csv` `616f8e81…`, `FRAME.csv` `d89b2328…`, `KRITERLER-TASLAK.md` (now `experiment/inventory/CRITERIA-DRAFT.md`) `f9f2f7be…` | Inventory metadata (support evidence from documents and code lines, for example 4 targets in n with native ML-DSA, 0 with composite) | Behaviour of any target, Steps 3, 5A, 7 |
| 3 | 2026-09-24 | v0.4, anchor 3, `42cd8e9` | Lock of the formal part, D1′ (17 nodes, \|Q\| = 675, primary configuration, designs, counting rule), qualifier of Ö2 (i), binding of the Step 5A expectations (`a88d972e…`), Step 7 expectation rule, MR4 name | Amendments 1–2 known, Step 5A variant expectations (not results), signer tests t01–t04 | Step 3, Step 5A results, Step 7, C3. Note: Step 5A runs had started (first run 19:11:34) when the anchor was committed (19:28:52), its content is exactly the pre-run hash |
| 4 | 2026-09-24 | v0.5, anchor 4, `f80232b` | Part A (C3): key resolution, control label, battery v1.1, KB/multi-signature sub-cell, wrong pre-hash class, M3 claim sets, `sdjwtvc_surum` scope, validity threats. Part B (formal, post-result): H3 simplification, `S_online_core` (`c8fe3ee5…`), three forms of G5, `ca_baglama`, R1 qualifier, expectation scope, note on condition (2), H5 qualifier, ProVerif scope, timestamp note | Step 9b tool tests, all Step 5A results (R6, R6h5, R7, R7h, R7hx, ProVerif), IETF draft texts | Step 3, Step 7, C3, `S_online_core` result |
| 5 | 2026-09-24 | v0.6, anchor 5, `2c70536` | Battery v1.1 (100 vectors, historical) | v1.1 tool tests | C3, Steps 3 and 7 |
| 6 | 2026-09-25 | v0.7, anchor 6, `68e0478` | Reading of sample agreement, technical gate sample rule, Holm presentation order, K8 adaptation, MR4 in Section 5.20, generator seed note, anchor numbering note | Step 5A results, v1.1 tests, v1.2 generated but not verified | Step 3 and its export, sampling, Steps 5B, 6, 7, C3 |
| 7 | 2026-09-25 | v0.8, anchor 7, `19706ff` | Battery v1.2 (153 vectors), independent regeneration, primary/secondary vector rule | v1.2 tool tests | C3, Steps 3, 5B, 6, 7 |
| 8 | 2026-09-26 | v0.9, anchor 8, `97d6e3a` | Part A: KAT and mechanism expectations bound before the runs. Part B (post-result, Step 3): H4 counting, S2 health note, ASP mapping, boundary conditions. Part C (before C3): four-valued oracle, K5, K8/K9, V±, oracle re-derivation, v1.3 decision, JOSE-104 → JOSE-031, version pinning, delegations, statistics clarifications. Part D: scope reduction (timing measurement removed, one reference verifier), approved by the corresponding author | Step 3 results, oracles A and B and their comparison, build pretest, N-version KAT expectations. The text was written before the technical gate results, the commit was made after them (10 of 10), and no item depends on them | Steps 6 and 7 results, Step 5B, C3 |
| 9 | 2026-09-26 | v0.10, anchor 9, `e0b83fa` | Battery v1.3 (200 vectors, COSE and L4c), L4c rule for COSE_Sign1, −7 note. A first commit attempt lacked this section because of a script error, anchor 9 is the correction | v1.3 tool tests, technical gate result | C3, Steps 6 and 7 |
| Change log v0.11 | 2026-09-26 | v0.11, `47d5bbb` | Correction of the KAT-1 test model (post-result) | First Step 6 run | C3 |
| Decisions D1–D7 | 2026-10-01 | `8e77a31` (`DECISIONS-PREFREEZE.md`) | Pre-freeze decisions for C3 | Validity gate results, API review observations (Section 12.3) | Battery outcomes |
| TK2 out of scope | 2026-10-01 | `a0965b4` | Section 13.1 | Steps 3–7 results | Battery outcomes |
| **10** | 2026-10-01 | integrated in v1.0, commit `7143e8c` (decision D4) | Control-arm label order EdDSA → Ed25519 → ES384, battery v1.4 (v1.3 + 30 ES384 counterparts), oracle v1.4 (+ 357 `kontrol-ES384` rows by case mapping), job list `jobs-v1.4.jsonl` (2,202 rows), control labels (EdDSA 17, ES384 13, none 1), exclusion of SDJWT-021 from the primary H6 analysis, primary n_eff 30 | Validity gate results including ES384 (24 of 31 passed), the formal results | Battery outcomes |
| Decision D8 | 2026-10-03 | `793b5e6` | Evidence rule: second attempts for 7 targets and their reconciliation (custom code in a callback does not raise the level), COSE-014 adapter corrected | Validity gate results, API review observations, second-attempt records | Battery outcomes |
| Decision D9 | 2026-10-03 | `36beee2` | Adapter conformance review: legacy-issuer record of L4c in 11 adapters, issuer from the payload in COSE-014/COSE-034, kid correction of 9 COSE files of battery v1.4, conformance test (acceptance rows only) and 4 adapter corrections, second attempts for COSE-035 and COSE-036, gates re-run | Validity gate results, conformance outputs (acceptance rows only), Section 12.5 | Battery outcomes, every rejection row |
| Treatment-class file, analysis script | 2026-10-01 | `ebeded0` | `experiment/runs/TK-ASSIGNMENT.csv`, `experiment/runs/analysis/analyze_c3.py`, written before measurement | Validity gate results | Battery outcomes |
| Run script | 2026-10-01 | `e915c20` | `experiment/runs/run_measurement.sh` with the freeze-hash check | as above | Battery outcomes |
| H4 result file, scientific gate evidence | 2026-10-01 | `f143bdf`, `4f8410a` | Counting rule of Amendment 8, item 3 applied in the result file (6 counted cells), `models/comparison/SCIENTIFIC-GATE.md` | Formal results | Step 5B agreement, battery outcomes |
| English names of the run files | 2026-10-01 | `0ba930d` | Section 13.8 | | |
| **11** | 2026-10-01 | integrated in v1.0 | T1 the only confirmatory test (unchanged), T2–T5 descriptive, historical baseline and known-bug recall removed, L4c interpretation note, incidental-rejection rule for the control arm, second attempts under the evidence rule only for T1, wording "expected verdicts fixed and hashed before the runs (internal record)" for the formal part, known limitations of the independent derivations, reference verifiers and end-to-end demonstration (Step 11, D8) removed, sensitivity thresholds from their own n, pilot sensitivity over both pilots | Validity gate results including ES384, the formal results, the internal methodological review (no measurement data) | Battery outcomes |

## Appendix D. Changes to the formal part (H0–H5) since draft anchor 1

Baseline: draft anchor 1 (v0.2, 2026-09-24), which already contained Amendment 1. Relative to Design v3, Amendment 1 replaced H2 by H2′, narrowed condition (2c), named the H4 candidate cells, extended the mechanism classes, added strategy S8, introduced the two forms of G5 and excluded the pilot evidence.

| When | Change | Results seen when written |
|---|---|---|
| Anchor 3, 2026-09-24 | Formal part locked (gate criteria, support and falsification rules of H0–H5, KAT pass criteria, primary configuration). D1′ query space and primary configuration. Pre-specified designs for H1, H2′, H4, H5. Counting rule for (2a)/(2b) and OAT sensitivity. Qualifier of Ö2 (i). Step 5A expectations bound. Step 7 expectation rule | Step 4. Not Step 3, 5A, 7 |
| Anchor 4, 2026-09-24 | H3 falsification condition 2 triggered, M-f simplified, expected verdicts of `S_online_core` fixed before its run. G5 three forms. `ad_baglama` → `ca_baglama ∈ {yok, ad, anahtar}` and `ayni_ad_klasik_ca` (primary values unchanged, 2 × 2 grid exploratory). R1 qualifier. Expectation scope dimension for Step 7. Note on condition (2). H5 qualifier. ProVerif scope. Timestamp note on the Step 5A expectations | **After** the Step 5A results |
| 2026-09-24 | Exploratory R7hx variants appended to `varyantlar.tsv` with expectations written before their runs (19:28:54, runs 19:29–19:31) | After the R7h result |
| Anchor 6, 2026-09-25 | Strict reading of the sample agreement condition (technical gate, D3, scientific gate (1)). Technical gate sample rule (frame hashed before selection, seeded selection by the study team, exploratory instance outside the count). Clarifications that tighten the criteria, with the literal reading also reported | After Step 5A, before sampling and before Step 3 results |
| Anchor 8, 2026-09-26 | KAT and mechanism expectations bound before the runs. H4 (2a) counting, strict reading. S2 health note. ASP operational mapping. Boundary conditions | Part A before the runs. Part B **after** the Step 3 results |
| v0.11, 2026-09-26 | KAT-1 test model corrected (expected values and pass criterion unchanged, gate presented with both readings) | **After** the first Step 6 run |
| 2026-10-01 | OJEU expectation hook brought into the scope of M-f. Fair-metric variant of H4 as sensitivity. Both are additions after the results were known (Section 13.9) and change no verdict | **After** the formal results |
| Amendment 11, 2026-10-01 | Wording only: the formal part is described as "expected verdicts fixed and hashed before the runs (internal record)" instead of "pre-registered". No rule, prediction or verdict of H0–H5 changed | After the formal results |

## Appendix E. Targets (n = 31)

Gate passes: algorithms passing the JWS/COSE-level validity gate (Section 12.2), with ES384 from the gate on battery v1.4. TK columns: `experiment/runs/TK-ASSIGNMENT.csv`. Control label: `experiment/runs/CONTROL-LABELS.csv` (Amendment 10).

| ID | Library | Language group | Pinned version | Gate passes | TK ML-DSA-65 | TK composite | Control label | Notes |
|---|---|---|---|---|---|---|---|---|
| JOSE-001 | IdentityModel (azure-activedirectory-identitymodel-extensions-for-dotnet) | .NET | 8.23.0 | ES256, ES384, ML-DSA-65 | TK1 | TK3 | ES384 | Delegate of SDJWT-021 |
| JOSE-002 | JWT.NET (jwt) | .NET | 11.1.0 | ES256, ES384 | TK3 | TK3 | ES384 |  |
| JOSE-009 | jose (panva) | JS/TS | 6.2.12 | ES256, EdDSA, Ed25519, ES384, ML-DSA-65 | TK1 | TK3 | EdDSA | Pilot P3, second pilot |
| JOSE-031 | guardian | Other (Elixir) | 2.5.0 | ES256, EdDSA, Ed25519, ES384 | TK3 | TK3 | EdDSA | Replaces JOSE-104. Delegates to erlang-jose 1.11.12 |
| JOSE-033 | golang-jwt (jwt) | Go | v5.3.1 | ES256, EdDSA, ES384 | TK3 | TK3 | EdDSA | Second pilot |
| JOSE-034 | jose2go | Go | v1.11.0 | ES256, ES384 | TK3 | TK3 | ES384 | Second pilot |
| JOSE-052 | java-jwt | JVM | 4.6.1 | ES256, ES384 | TK3 | TK3 | ES384 |  |
| JOSE-055 | jjwt | JVM | 0.13.0 | ES256, EdDSA, ES384 | TK3 | TK3 | EdDSA |  |
| JOSE-065 | node-jsonwebtoken | JS/TS | 9.0.3 | ES256, ES384 | TK3 | TK3 | ES384 | Second pilot |
| JOSE-070 | php-jwt | PHP | 7.2.0 | ES256, EdDSA, ES384 | TK3 | TK3 | EdDSA |  |
| JOSE-071 | lcobucci/jwt | PHP | 5.6.0 | ES256, EdDSA, ES384 | TK3 | TK3 | EdDSA |  |
| JOSE-083 | pyjwt | Python | 2.15.0 | ES256, EdDSA, ES384 | TK3 | TK3 | EdDSA | Second pilot |
| JOSE-084 | python-jose | Python | 3.5.0 | ES256, ES384 | TK3 | TK3 | ES384 | Second pilot |
| JOSE-087 | ruby-jwt | Ruby | 3.3.0 | ES256, ES384 | TK3 | TK3 | ES384 |  |
| JOSE-089 | json-jwt | Ruby | 1.17.2 | ES256, ES384 | TK3 | TK3 | ES384 |  |
| JOSE-091 | frank_jwt (listed in the frame as rust-jwt) | Rust | 3.1.4 | ES256, ES384 | TK3 | TK3 | ES384 |  |
| JOSE-092 | jsonwebtoken | Rust | 11.1.0 | ES256, EdDSA, ES384 | TK3 | TK3 | EdDSA |  |
| JOSE-102 | jwt-kit | Swift/ObjC | 5.3.0 | ES256, EdDSA, Ed25519, ES384, ML-DSA-65 | TK3 (primary), TK1 (sensitivity) | TK3 | EdDSA | Decision D2 |
| SDJWT-001 | vck | JVM | 7.0.1 (indispensable-josef 3.24.0, supreme 0.15.0) | ES256, ES384 | TK3 | TK3 | ES384 | Delegates to Signum (COSE-001 project) |
| SDJWT-002 | selective_disclosure_jwt (affinidi) | Other (Dart) | 1.1.1 | none (V− accepted, Decision D1) | TK3 | TK3 | EdDSA (claimed, Decision D1) | Decision D1, `integrity-failure` |
| SDJWT-004 | authlete/sd-jwt | JVM | 1.9 (+ nimbus-jose-jwt 10.10) | ES256, ES384 | TK3 | TK3 | ES384 | Verification through the documented JOSE layer |
| SDJWT-010 | sd-jwt-payload | Rust | 0.5.1 | ES256, EdDSA, ES384 | TK3 | TK3 | EdDSA | Decision D5 (josekit) |
| SDJWT-015 | identity-common-ts (@sd-jwt/core) | JS/TS | 0.21.0 | ES256, EdDSA, Ed25519, ML-DSA-65 | TK1 | TK3 | EdDSA | Pilot P3. Decision D5 (verifier callback) |
| SDJWT-018 | sd-jwt-python | Python | 0.10.4 | ES256, EdDSA, Ed25519, ES384, ML-DSA-65 | TK1 | TK3 | EdDSA | Delegates to jwcrypto |
| SDJWT-021 | wallet-framework-dotnet (WalletFramework.SdJwtVc) | .NET | 3.1.0 | SD-JWT gate: ES256 with `vc+sd-jwt` only | TK3 | TK3 | none | Decision D1. Delegates to IdentityModel. Excluded from the primary H6 analysis (Amendment 10) |
| SDJWT-025 | spruceid/ssi (ssi-sd-jwt) | Rust | 0.6.0 | ES256, EdDSA | TK3 | TK3 | EdDSA | Decision D5 (ssi-jwt) |
| COSE-001 | Signum (indispensable-cosef) | JVM | indispensable-cosef 3.26.0 / supreme 0.16.0 | ES256, ES384 | TK3 | TK3 | ES384 |  |
| COSE-014 | cose-js | JS/TS | 0.9.0 | ES256, ES384 | TK3 | TK3 | ES384 |  |
| COSE-034 | go-cose (veraison) | Go | v1.3.0 | ES256, EdDSA | TK3 | TK3 | EdDSA |  |
| COSE-035 | web-auth/cose-lib | PHP | 4.8.2 | ES256, EdDSA, Ed25519 | TK3 | TK3 | EdDSA | ML-DSA only at HEAD (descriptive). Decision D5 |
| COSE-036 | wolfCOSE | C/C++ | git `f907071b` (+ wolfSSL v5.9.2) | ES256, EdDSA, Ed25519, ML-DSA-65 | TK1 | TK3 | EdDSA | Decision D3 |

---

## Freeze package
Paths are relative to the repository root. The study team computes the hashes at freeze (Section 11).

**Core files**
- This document: `docs/preregistration/PREREGISTRATION-v1.0.md` (hash list `docs/preregistration/FREEZE-SHA256SUMS`, deviation log `docs/preregistration/DEVIATIONS.md`)
- Measurement battery v1.4 [Amendment 10]: `experiment/vector-generator/vectors/v1.4/` (all vector files), with `experiment/vector-generator/vectors/v1.4/SHA256SUMS` and `experiment/vector-generator/vectors/v1.4/MANIFEST.json`
- Oracle v1.4: `experiment/oracle/merged/decisions_v14.tsv`
- Measurement job list: `experiment/runs/jobs-v1.4.jsonl`
- Statistics scripts: every file listed in `experiment/statistics/SHA256SUMS` (`Dockerfile`, `.dockerignore`, `run_all.sh`, `SCHEMA.md`, `scripts/requirements.txt`, `scripts/c3istat/*.py`, `synthetic-tests/` with its data, `sources/NEWCOMBE-SOURCE.md`), and `experiment/statistics/SHA256SUMS` itself, regenerated after the translation merge
- Adapter sources, listed by folder until their translation is final: `experiment/runs/adapters/` (per-target folders with `Dockerfile`, adapter source, `MAPPING.md`, `NOTES.md` and `evidence/`, the shared adapters `_go`, `_jvm`, `_kt`, `_node`, `_py`, `_rs`, and the helpers in `_tools/`)
- Decision file: `experiment/runs/DECISIONS-PREFREEZE.md`
- Measurement and analysis scripts: `experiment/runs/run_measurement.sh`, `experiment/runs/analysis/analyze_c3.py`
- Treatment classes and control labels: `experiment/runs/TK-ASSIGNMENT.csv`, `experiment/runs/CONTROL-LABELS.csv`
- Evidence-rule table read by the analysis script: `experiment/runs/analysis/evidence-rule.csv` [Decisions D8 and D9]

**Supporting files** (each is needed to verify or reproduce a frozen rule)
- Base battery v1.3 (byte-identical subset of v1.4, anchored at anchor 9): `experiment/vector-generator/vectors/v1.3/SHA256SUMS`, `experiment/vector-generator/vectors/v1.3/MANIFEST.json`
- Keys: `experiment/vector-generator/keys/v1/SHA256SUMS`, `experiment/vector-generator/keys/v1.3/SHA256SUMS`
- Battery v1.4 generator and check: `experiment/vector-generator/generator/v14.py`, `experiment/vector-generator/tests/t14_es384.py`, `experiment/vector-generator/results/t14_es384.txt`
- `experiment/vector-generator/BATTERY-MAPPING.md` (battery definition and primary/secondary status)
- Oracle derivation and inputs: `experiment/oracle/merged/derive_v14.py`, `experiment/oracle/merged/SUMMARY_v14.json`, `experiment/oracle/merged/decisions_v13.tsv`, `experiment/oracle/merged/derive_v13.py`, `experiment/oracle/merged/SUMMARY.json`, `experiment/oracle/oracle-A/decisions.tsv`, `experiment/oracle/oracle-B/decisions.tsv`
- `experiment/oracle/oracle-A/adapter-contract.md` (adapter contract) and `experiment/runs/RUNNER.md` (runner interface), after their update (Section 11, step 1)
- Job lists and their generator: `experiment/runs/jobs-v1.3.jsonl`, `experiment/runs/make_jobs_v14.py`
- Pre-freeze validity jobs and SD-JWT-format gate vectors: `experiment/runs/jobs-prefreeze-v1.3.jsonl`, `experiment/runs/jobs-prefreeze-v1.4.jsonl`, `experiment/runs/vpm-sdjwt/`
- Pre-freeze gate outputs and summaries: `experiment/runs/outputs/prefreeze-v1.3/`, `experiment/runs/outputs/prefreeze-v1.4/`, `experiment/runs/outputs/prefreeze-sdjwt/`, and the records of Decision D9: `experiment/runs/outputs/prefreeze-v1.4-first-generation/`, `experiment/runs/outputs/prefreeze-sdjwt-rerun-d9/`
- Evidence-rule second attempts: `experiment/runs/evidence-rule/` [Decisions D8 and D9]
- Adapter conformance test: `experiment/runs/conformance/` (generator, objects, job list, expected acceptances, outputs, comparison) [Decision D9]
- Frame, selection, inclusion and exclusion: `experiment/inventory/SELECTION.csv`, `experiment/inventory/FRAME.csv`, `experiment/inventory/CRITERIA-DRAFT.md`
- Pinned versions: `experiment/environments/build-results.csv`
- Strategy assignment of the formal part: `models/asp/sorgular/stratejiler_taslak.json`
- Scientific gate evidence: `models/comparison/SCIENTIFIC-GATE.md` (with the gate decision, Section 12.1)
- Discrepancy log of the abstraction sample: `models/sampling/UYUSMAZLIK-KAYDI.csv` (header only at freeze)
- Seed list: Appendix B of this document
