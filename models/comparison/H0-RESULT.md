# H0 verdict (model health)

Rule (pre-registration section 3.1). H0 is satisfied when all three conditions hold:
- (a) every health lemma has its pre-registered verdict;
- (b) under policy P0 and coexistence a stripping/downgrade attack exists;
- (c) the total mutation score is at least 0.90.

If (a) or (b) fails, H1–H5 are not judged.

Computed by `h0_verdict.py` → `H0-RESULT.json`.

| Condition | Value | Evidence |
|---|---|---|
| (a) Health lemmas (`executable*`, `attack_needs_crqc*`) | 554 of 554 as pre-registered. 550 verified. 4 are `executable_learn` lemmas that the plan expects to be **false**, because the variant has no expectation channel (R7 `M_per_entity`; mechanism baselines M-a, M-b0, M-b) | `../tamarin/sonuc/ozet.csv`, `../mechanisms/sonuc/ozet.csv`, plans `../tamarin/betik/varyantlar.tsv`, `../mechanisms/on_kayit_varyantlar.tsv` |
| (b) P0 + coexistence | ASP: 0 of 90 cells secured under P0 in phases Φ1/Φ2. Tamarin: downgrade trace `R2/M_expect_absent/S1_downgrade_trace` verified | `A2-politika.csv`, `../tamarin/sonuc/ozet.csv` |
| (c) Mutation score | 45 of 45 scored mutants killed (score 1.0; 11 equivalent probes and 2 base-insecure mutants reported separately) | `../mutation/mutation-score.json` |

**Verdict: H0 satisfied.** H1–H5 are judged in `HYPOTHESES-RESULT.md`.

## Pre-registered health question on strategies S1 and S2

The plan expected S1 and S2 to secure no cell after Q-day.
- S1 secures 0 cells.
- S2 secures 9 cells, all of them in phase Φ3 (G1–G3, every τ).

By definition, Φ3 accepts no classical alternative for migrated entities (pre-registration section 4.2), so no downgrade path exists there. In the coexistence phases Φ1 and Φ2, S1 and S2 both secure 0 cells.

The result is not changed. The expectation was worded too broadly and holds for Φ1 and Φ2. This explanation was written after the result was seen and is reported as such. Source: `sayilar.json` (`onceden_kayitli_sorular`).
