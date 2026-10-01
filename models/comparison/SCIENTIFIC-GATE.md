# Scientific gate (week 6): evidence and decision

Rule (pre-registration section 8.1):
- **(1) Validity:** every criterion must hold.
- **(2) Non-obvious result:** at least one candidate must hold (definitions in section 4.21, narrowed by amendments Ö2 and 8).
- Decision: if (1) and (2) hold, IEEE TDSC is the target. If only (1) holds, the target is a systems or standards venue.

## Condition (1): validity

| Criterion | Threshold | Value | Evidence |
|---|---|---|---|
| ASP–z3 agreement | 100 % | 52,693 of 52,693 queries agree (minimal sets 80,291 of 80,291) | `../asp/sorgular/sonuc/rapor_sayilari.json` |
| Sampling agreement, technical gate | 100 % of closed samples, every difference explained | 10 of 10 gate samples agree (plus one exploratory sample) | `../sampling/teknik-kapi/sonuc.csv` |
| Sampling agreement, stratified sample (200 samples) | 100 % of closed samples, every difference explained | 183 of 183 closed samples agree; 177 of 177 when samples whose health lemma did not close are left out. 17 of 200 samples (8.5 %) are out of the translator's scope (13) or not closed at 12 GB (4) | `../sampling/5b/REPORT.md` |
| Mutation score | ≥ 0.90 | 1.0 (45 of 45 scored mutants; two base-insecure mutants excluded). Literal reading with the two counted as not killed: 45 of 47 = 0.957 | `../mutation/mutation-score.json` |
| Known-answer tests | all pass | First run: 2 of 3 (KAT-2 and KAT-3 passed; KAT-1 failed in one Tamarin cell because of an error in the KAT's own Tamarin encoding; the ASP core under validation agreed in 109 of 109 cells). The KAT-1 Tamarin encoding was corrected after that result was seen, and the rerun passed 15 of 15 cells: 3 of 3. Recorded as a post-result correction | `../known-answer-tests/ADIM06-RAPOR.md` |

**Reading.** Read literally, the known-answer criterion failed at the first run. The failure lies in a test encoding
written for the known-answer test, not in the model under validation, and both runs are reported. Condition (1) is
taken as met **with this documented deviation**.

## Condition (2): non-obvious result

Candidates follow the pre-registered definitions. Amendment Ö2 declares obvious, on their own: downgrade traces of
unauthenticated negotiation, of multi-signed requests with "one valid suffices", and of the unsigned-request fallback.

| Candidate | Definition | Observed | Evidence |
|---|---|---|---|
| (2a) H4: insufficient or wasteful "roots and devices first" ordering | at least one counted cell, reproduced in ASP and in Tamarin | 6 τ-wasteful cells (amendment 8, item 3), each with a Tamarin example | `HYPOTHESES-RESULT.md` (H4) |
| (2b) H1/H2 with operational significance | substitution only under PQ transport; set changes with τ | in the model (H1: 12 pulled artefact–goal pairs; H2′: 66 of 180 cell groups) | `HYPOTHESES-RESULT.md` (H1, H2′) |
| (2c)(i) commitment extensions bypassed | M-h commitment bypassed through a classical chain or an alternative classical CA | reddy- and vicente-type commitments do not protect when carried only in a classical chain; bypassed by a different-name CA, a same-name classical CA and a classical root with a PQ intermediate; path-class scoped per-entity expectation closes all three | `../mechanisms/ADIM07-RAPOR.md` §2.2, §2.4; `../tamarin/sonuc/ozet.csv` (R7h) |
| (2c)(ii) M-e′ result contrary to the recorded expectation | | rollback protection fails for non-migrated issuers whose metadata is self-signed | `HYPOTHESES-RESULT.md` |

### Novelty assessment

A first independent assessment rated (2c)(i) non-obvious. It had not been given the drafts' own statements below.
A second independent assessment and two internal reviews were then given this counter-evidence (local copies in the
study's literature folder; draft status from the IETF datatracker on 2026-10-01):
- draft-sheffer-tls-pqc-continuity-02, Section 3.2: "Post-quantum authentication requires signatures along the entire
  path to be resistant to quantum-capable adversaries; a PQC end-entity certificate paired with a classically signed
  intermediate does not provide this property."
- draft-vicente-lamps-pqchc-02, Sections 4.2 and 7: the commitment "is advisory and MUST NOT be treated as
  authentication of the committed post-quantum key".
- draft-reddy-lamps-x509-pq-commit-01, Section 3.1: the extension "does not modify path validation procedures as
  defined in [RFC5280]"; the draft expired on 2026-08-29.
- RFC 5280: trust in a path derives from the trust anchor's key, not from names.

| Candidate | Assessment after the counter-evidence | Basis |
|---|---|---|
| (2c)(i) classical-chain and alternative-CA bypass | **obvious** | the whole-path rule of sheffer-02 §3.2 anticipates it |
| (2c)(i) same-name CA defeating a CA-name binding | **obvious** | standard PKI reasoning (RFC 5280); the name binding was the study's own strawman variant |
| (2c)(i) path-class repair | rule obvious; the combination with a third-party, current, per-entity expectation **uncertain** | sheffer-02 states the rule and leaves trust-store policy open; closest precedents for the conveyance are TUF/Uptane, HSTS preload and DNSSEC DS |
| Online/offline component ablation | **uncertain** | freshness, monotone state and expiry are known ingredients (TUF/Uptane); the mode-specific minimality is new only under stated assumptions |
| (2a) H4 ordering limit | uncertain | role-based rules missing dependencies is foreseeable |
| (2b) time and channel resolution | uncertain | principles known; the artefact-level matrix is ecosystem-specific |
| (2c)(ii) self-signed expectation carrier | obvious | first-contact limitation of host-learned policies (HSTS) |
| H5 harvest-and-forge | obvious | batch issuance does not protect the holder key |

**Result.** No candidate is established as non-obvious. Condition (2) is **not met**.

## Gate decision (2026-10-01)

Only condition (1) holds (with the documented known-answer-test deviation). Under the pre-registered rule the target
is a systems or standards venue: **Computer Standards & Interfaces**. The paper presents the commitment attacks as
instances of known path reasoning and positions its contribution as the explicit statement and machine-checked
instances of the attack classes and conditions for conveying a post-quantum expectation, the standards analysis, a
verifier profile and the EUDI case study. Approval of the gate decision by the authors is pending.
