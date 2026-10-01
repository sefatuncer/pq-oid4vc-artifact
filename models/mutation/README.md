# Mutation analysis

`score.py` aggregates the total mutation score defined in the pre-registration (section 4.17).

A mutant removes one protection from a model. It is **killed** when a security lemma that holds
(verified) for its base variant becomes falsified, or when the ASP property test reports the attack.

| Source | Mutants | Where they are defined | Where the verdicts are |
|---|---|---|---|
| Rule models R1-R7h (Tamarin) | 27 | `../tamarin/betik/varyantlar.tsv` (role `mutant:<protection>[(<base>)]`) | `../tamarin/sonuc/ozet.csv` |
| Known-answer tests (Tamarin) | 10 | `../known-answer-tests/*/` | `../known-answer-tests/*/sonuc/tamarin_mutasyon.csv` |
| Known-answer tests (ASP) | 21 | `../known-answer-tests/*/` | `../known-answer-tests/*/sonuc/asp_mutasyon.csv` |

Score = killed / (mutants - equivalent - base insecure).

- **Equivalent (11):** known-answer-test probes whose expected outcome is "no attack", because another protection makes the removed one redundant.
- **Base insecure (2):** `R7h/M_ca_classical` and `R7h/M_no_namebind`. Their protected base `P_ca_pq_alt_namebind` already violates its security lemmas: a same-name classical CA bypasses name binding, which is the R7h finding. Removing a protection from an insecure base cannot be detected, so these two mutants are reported but not scored.

Result: 45 of 45 scored mutants killed (score 1.0). The pre-registered threshold is 0.90. Per-group values are in `mutation-score.json`.

Run: `python score.py` (reads only; writes `mutation-score.json` and `mutation-score.csv`).
