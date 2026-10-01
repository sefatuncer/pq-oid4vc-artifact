# Scientific gate (week 6): evidence

Rule (pre-registration section 8.1):
- **(1) Validity:** every criterion must hold.
- **(2) Non-obvious result:** at least one candidate must hold (definitions in section 4.21, narrowed by amendments Ö2 and 8).
- Decision: if (1) and (2) hold, IEEE TDSC is the target. If only (1) holds, the target is a systems or standards venue.

## Condition (1): validity

| Criterion | Threshold | Value | Evidence |
|---|---|---|---|
| ASP–z3 agreement | 100 % | 52,693 of 52,693 queries agree (minimal sets 80,291 of 80,291) | `../asp/sorgular/sonuc/rapor_sayilari.json` |
| Sampling agreement, technical gate | 100 % of closed samples, every difference explained | 10 of 10 gate samples agree (plus one exploratory sample) | `../sampling/teknik-kapi/sonuc.csv` |
| Sampling agreement, stratified sample (200 samples) | 100 % of closed samples, every difference explained | TODO after the remaining 12 GB reruns | `../sampling/5b/` |
| Mutation score | ≥ 0.90 | 1.0 (45 of 45 scored mutants) | `../mutation/mutation-score.json` |
| Known-answer tests | all pass | 3 of 3 pass (DNSSEC, X.509, S/MIME). The first run gave 2 of 3: KAT-1 failed. The KAT-1 Tamarin model was corrected after that result was seen, then passed 15 of 15 cells. This is recorded as a post-result correction | `../known-answer-tests/STEP06-REPORT.md` (ADIM06) |

## Condition (2): non-obvious result

Candidates follow the pre-registered definitions. Amendment Ö2 declares obvious, on their own: downgrade traces of
unauthenticated negotiation, of multi-signed requests with "one valid suffices", and of the unsigned-request fallback.

| Candidate | Definition | Status | Evidence |
|---|---|---|---|
| (2a) H4: insufficient or wasteful "roots and devices first" ordering | at least one counted cell, reproduced in ASP and in Tamarin | **holds**: 6 τ-wasteful cells (amendment 8, item 3), each with a Tamarin example | `HYPOTHESES-RESULT.md` (H4) |
| (2b) H1/H2 with operational significance | substitution only under PQ transport; set changes with τ | holds in the model (H1: 12 pulled artefact–goal pairs; H2′: 66 of 180 cell groups) | `HYPOTHESES-RESULT.md` (H1, H2′) |
| (2c)(i) commitment extensions bypassed | M-h commitment bypassed through a classical chain or an alternative classical CA | **holds**: reddy- and vicente-type commitments do not protect when carried only in a classical chain. They are bypassed by a different-name CA, a same-name classical CA and a classical root with a PQ intermediate. Path-class scoped per-entity expectation closes all three | `../mechanisms/STEP07-REPORT.md` §2.2, §2.4; `../tamarin/sonuc/ozet.csv` (R7h) |
| (2c)(ii) M-e′ result contrary to the recorded expectation | | holds (rollback protection fails for non-migrated issuers whose metadata is self-signed) | `HYPOTHESES-RESULT.md` |

## Novelty assessment

An independent novelty assessment compared the candidates with the literature and standards available in October 2026.

| Candidate | Assessment | Basis |
|---|---|---|
| Commitment bypass and path-class repair ((2c)(i)) | **non-obvious** | The continuity drafts describe advisory commitments that are verified after path validation. Studies of hybrid certificate validation show that PQ evidence can be left out of the decision. Neither states this set of path substitutions against the commitments, nor the path-class repair |
| H4 ordering limit ((2a)) | uncertain | Published migration guidance does not give a cell-level minimal ordering. The general point that a role-based rule misses dependencies is foreseeable |
| Time and channel resolution ((2b)) | uncertain | The principles (channel against signed object, key lifetime) are known; the artefact-level matrix for this ecosystem is new |
| Self-signed expectation carrier ((2c)(ii)) | obvious | An instance of the first-contact limitation of host-learned policies (HSTS) |
| Harvest-and-forge (H5) | obvious | Batch issuance does not protect the holder key |

**Result.** Condition (2) holds through (2c)(i). The paper states the general need to enforce PQ evidence as known. Its claim is narrowly the path substitutions against continuity commitments and the path-class repair. (2a) and (2b) are reported as ecosystem-specific results.

**Gate decision:** pending the stratified-sample agreement in condition (1).
