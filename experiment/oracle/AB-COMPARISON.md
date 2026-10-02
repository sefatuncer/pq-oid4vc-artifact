# Comparison of Oracle A ↔ B (maintainers, 25.09.2026)

**Inputs:**
- `oracle-A/decisions.tsv` `dd21fdba…` (858 rows; 11 configurations).
- `oracle-B/decisions.tsv` `2cca1295…` (732 rows; L4/P0/P2 and version suffixes).
- B was committed before A was finished (`037e468` < `be1904f`). Both stated that they did not read the other's folder.

**Key:** (vektor_id, politika, kol). Common configurations: L4 and P0.

| Configuration | Scope | Common | Equal | At least one undetermined | Definitely different |
|---|---|---|---|---|---|
| L4 | primary in both oracles | 53 | 48 | 4 (K5: A undetermined in the base L4) | **1** |
| L4 | all | 138 | 102 | 40 | 1 |
| P0 | primary in both oracles | 20 | 16 | 0 | **4** |
| P0 | all | 61 | 41 | 0 | 20 |

**All definite differences come from points that both oracles flagged as undefined in the PR:**
1. **X5C04 (K8), composite arm, L4:** A = accept-hybrid, B = reject. The policy of K8/K9 in the composite arm is undefined (A N-3, B N3). The adapted vector is signed with ML-DSA-65; this algorithm is not in the allowed set of the composite arm.
2. **T1P, T1C, T7P, T7C, P0:** A = accept-classical, B = accept-hybrid. There is no definition of the distinction "accept-hybrid / accept-classical" (A N-5, B N1). Under P0, when the PQ signature is also valid, the class of the acceptance is undetermined.
3. **K5 (extra signature):** A said undetermined in the base L4 and added the S/Y sub-configurations. B said reject with the strict reading (A N-1, B N4).

**Result:**
- No random error was seen. The disagreements concentrate on three definition gaps in the PR.
- Under PR §4.20 these cells fall into the "undetermined" class. They close if the definitions are written into the PR (BEFORE the freeze) and both oracles are re-derived with the same definition.
- Items for the oracles to decide jointly: `DECISION-NOTES.md` (A: N-0…N-12; B: N1…N17).
