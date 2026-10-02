# Divergence detector — design (proposal of Oracle A; run in Step 10)

> **Basis:**
> - PR §4.20: "Cross-library results are used as a divergence detector, not as a majority vote."
> - Work plan Step 9 task 6: "list of targets that decide differently on the same case; no majority vote is used (run in Step 10)".
> - Work plan Step 10 task 10: `ayrisma.csv`.
>
> **This document is a design only.** No target was measured; the examples below are **format examples, not invented data**, and carry no real target name.
>
> (Quotations from the pre-registration and the work plan are translated from Turkish. Output values such as `kararsiz`, `evet`/`hayir` and the file names `ayrisma.csv` / `ayrisma_ozet.md` ("divergence") are kept as defined.)

## 1. Purpose and principle

- **Purpose:** to **list** the targets that decide differently in the same test cell. The list helps to bring forward:
  - possible implementation errors,
  - specification ambiguities,
  - PQ-specific divergences.
- **NO majority vote.** Group sizes are reported, but no decision is considered "correct because the majority says so". A target that stands alone is not marked "wrong".
- **Correctness comes only from the oracle** (the cells on which A and B agree; PR §4.15). The detector works independently of the oracle. The relation to the oracle is written only as **side information**.
- **Descriptive:** it does not enter the pre-registered tests (T1–T5) or the Holm family.

## 2. Inputs

| Input | Source |
|---|---|
| Target decisions | `experiment/runs/outputs/measurement/<target>.<r1|r2|r3>.jsonl` (`adapter-contract.md` §3; the original text named `kosu/r{1,2,3}/<target>.jsonl`) |
| Oracle A, Oracle B | `experiment/oracle/oracle-A/karar.tsv`, the decision file of Oracle B (configuration names aligned with a mapping table; decision notes N-12) |
| TK assignment, control label | `experiment/runs/tk-atamasi.csv` |
| L levels, L4 form | `experiment/runs/L-duzeyleri.csv` |
| Delegation clusters | `adapter-contract.md` §7 |
| Primary/secondary | column `sinif` of `karar.tsv` (PR §2G item 4) |

## 3. Cell and decision

- **Cell** h = (vector, policy, arm, sdjwtvc_version).
- **Label normalisation in the control arm:** the `…-ED25519` twins in arm `kontrol-Ed25519` are mapped to the same cell as the source vector in `kontrol-EdDSA`. The mapping uses the field `insa.v1_esi` or `insa.etiket_esi`. In this way a target that uses the fallback label can be compared with a target that uses `EdDSA`. The label used is shown separately in the cell row.
- **Cell decision of a target** k_t(h):
  - the value if it is the same in the three runs;
  - otherwise `kararsız` (unstable).
  - Targets with `uygulanamaz` (B6) and targets with an invalid adapter are removed from the cell and listed separately.

## 4. Algorithm

```
input: K[t][h] (stable 3/3 or "unstable"), ORACLE_A[h], ORACLE_B[h], TK[t][arm], DELEGATION = {cluster: {targets}}
output: ayrisma.csv, ayrisma_ozet.md

for h in sorted(all cells):                           # order: vector id, policy, arm; deterministic
    T = {t : K[t][h] ∉ {not applicable}, t adapter-valid}
    group_decision = split(T, key = K[t][h])            # 4 values + "unstable"
    group_accept   = split(T, key = coarse(K[t][h]))     # coarse: accept-* → "accept", reject, indeterminate, unstable
    if |keys of group_accept| ≥ 2:      type = "decision divergence"
    elif |keys of group_decision| ≥ 2:  type = "acceptance-type divergence"   # accept-classical ↔ accept-hybrid
    else: continue                                       # no divergence
    oracle = ORACLE_A[h] if ORACLE_A[h] == ORACLE_B[h] else "A≠B (undetermined)"
    for cluster in DELEGATION: if cluster ⊆ T and |{K[t][h] : t ∈ cluster}| ≥ 2: within_cluster = True
    pq_specific = (arm ∈ treatment) and (NO decision divergence in the twin control cell)   # §5
    write(h, group_decision, type, oracle, within_cluster, pq_specific, TK distribution, class)
```

- **Coarse decision:** the type is first determined at the decision level (accept ↔ reject). A difference in the kind of acceptance is a separate type. In this way the distinction between "accepting without verifying PQ" and "accepting with PQ verified" is not lost.
- **Delegation clusters:** targets are shown both individually and as a cluster.
  - A divergence inside a cluster means that two units sharing the same verification core decided differently. Example: WalletFramework ↔ IdentityModel. This points to an adapter or configuration difference and goes to the adapter check.
- **Unstable targets:** listed as a separate group in the cell (PR §6.11 "unstable → undetermined").

## 5. Divergence types and priority (triage order; not a vote)

This order only determines which divergence is examined first. It changes no target's decision.

1. **Oracle determined, at least one target deviates.** The cell has oracle A = B and determined; at least one group differs from the oracle. Possible implementation error. Primary cells come first.
   - The decision is independent of the group sizes: even if the group that agrees with the oracle is small, that group is "correct".
2. **PQ-specific divergence.** The treatment-arm cell has a decision divergence, but the control-arm cell of the same case has none. Example: in K1 all targets decide the same in the control arm, while the groups diverge in the composite arm. This is the cell-level counterpart of T2 (F_T = 1 ∧ F_K = 0). Reported together with the TK1/TK2/TK3 distribution.
3. **Oracle undetermined, targets diverge.** **Empirical evidence** of a specification ambiguity (`UNDETERMINED.md` B-1…B-6). Examples:
   - K5 (S/Y),
   - VP05/VP07 (`sd_hash`),
   - CMP05/CMP06 (DER strictness),
   - X5C10 (kid ↔ x5c).

   Linked to the external notification candidates (DB-1, DB-2).
4. **Acceptance-type divergence.** All targets accept, but some accept without verifying the PQ signature. Typically the TK3 vs. TK1/TK2 distinction; reported descriptively.
5. **MR4 within-target divergence.** Not a divergence between targets, but shown in the same table: a target decides differently on the source vector and on its permutation twin. This is the separate MR4 flag of PR §2B item 8. VP05-SIRA-ters is outside the MR4 scope.

## 6. Output schema

### `ayrisma.csv` (one row per cell; diverging cells only)

| Column | Description |
|---|---|
| `hucre` | `<vektor_id>|<politika>|<kol>|<sdjwtvc_surum>` (label-normalised) |
| `vektor_id`, `politika`, `kol`, `sinif`, `vaka` | from `karar.tsv` |
| `tur` | `karar-ayrismasi` (decision divergence) / `kabul-turu-ayrismasi` (acceptance-type divergence) |
| `oncelik` | 1–5 of §5 (priority) |
| `oracle_A`, `oracle_B`, `oracle_uzlasi` | if there is no agreement, `A≠B (belirsiz)` |
| `gruplar` | JSON: `{"reject": ["JOSE-…", …], "accept-classical": […], "kararsiz": […]}` |
| `grup_boyutlari` | JSON: `{"reject": 7, "accept-classical": 3}`. Information only, not a vote |
| `tk_dagilimi` | JSON: number of TK1/TK2/TK3 per group |
| `l4_bicimi` | L4m/L4c per group |
| `devir_kume_ici` | `evet`/`hayir` (yes/no) + cluster name |
| `kontrol_etiketi` | EdDSA/Ed25519 distribution per group (control arm) |
| `hariç` | not applicable (B6) and adapter-invalid targets (excluded) |
| `not` | free text; e.g. "BELIRSIZ B-2" |

### `ayrisma_ozet.md`

- Number of cells per type and priority.
- Primary vs. secondary.
- List of PQ-specific divergences.
- Divergences inside delegation clusters.
- Cells where oracle undeterminedness and divergence coincide.

### Format example (not invented; placeholder names)

```
hucre=T7P_plus_kayitsiz|L4|tedavi-ML-DSA-65|-13  tur=karar-ayrismasi  oncelik=3
oracle_A=indeterminate  oracle_B=<B>  gruplar={"reject":["<hedef-1>"],"accept-hybrid":["<hedef-2>"],"accept-classical":["<hedef-3>"]}
not: BELIRSIZ B-1 (S/Y). The accept-classical group is an MR2 violation candidate (accepted without verifying the PQ signature)
```

## 7. Validation (together with Step 9 task 8; without libraries)

The detector script is tested with **synthetic** target decisions before Step 10. No target is run. Test cases:
1. All targets the same → 0 rows.
2. Two targets, accept-classical ↔ reject in K3 → 1 row, `karar-ayrismasi`, priority 1.
3. All targets accept, one accept-classical → `kabul-turu-ayrismasi`.
4. No divergence in the control arm, divergence in the treatment arm → the `pq_ozgu` mark (PQ-specific).
5. Two members of a delegation cluster differ → `devir_kume_ici = evet`.
6. The `-ED25519` twins fall into the same cell after normalisation.
7. A B6 target is removed from the cell.
8. Two runs with the same input give byte-identical output.

**Determinism:** the ordering is fixed, there is no randomness. The script digest enters the freeze package (PR §10).
