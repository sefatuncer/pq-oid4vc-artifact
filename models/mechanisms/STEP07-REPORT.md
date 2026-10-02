# Step 7 report: mechanism models (closed by the maintainers, 01.10.2026)

**Run:** Tamarin work, from 26.09.2026 13:43. Anchor 8 (`2d16592`, 13:39) fixed the expectations before the run; the SHA-256 of `on_kayit_varyantlar.tsv` `ebb87d64…` was checked at the start of every run.
**Closure:** Maintainers, 01.10.2026. The 26.09 run had been interrupted in the last few extra rows. `betik/calistir.sh` was resumed where it stopped (same image, same model files).
**Tables:** `sonuc/tablolar.md` (from the script); raw data `sonuc/ozet.csv`, `sonuc/karsilastirma.csv`, `sonuc/ham/`.

## 1. Acceptance criteria

| Criterion (work plan 7.6) | Result |
|---|---|
| 1. A definite result for every class | ✓ M-a, M-b/A.3.2.2, M-b0, M-d, M-e, M-e′, M-f (core, 3b, carriers), M-g (sheffer; ANNEX [8a]), M-h (reddy, vicente). **All 762 lemma runs closed on rung 1**; no "not closed" |
| 2. The three forms of G5 for the simplified M-f, including the path | ✓ `MF_cekirdek`: G5_untimed / G5_migrated / G5_timed / no_rollback and all G5_path_* forms **verified** |
| 2a. Expectations anchored before the run | ✓ anchor 8 at 13:39 < first run at 13:43 |
| 2b. Task 3b: 3 scopes × 3 attacks; the two variants of M-h | ✓ (§2.2, §2.4) |
| 3. A3 dimensions | ✓ Carrier substitution (A3-7), offline annex 2×2 (ANNEX [8b]); the rule-level dimensions in 5A |
| 4. The three questions of task 3a | ✓ (§2.4) |
| 6. Well-formedness 0; ≤10 min; ≤12 GB | Well-formedness **762/762 clean**; memory at most 5.4 GB. Time: one run recorded a wall time of 7,024 s on 26.09 (`MF_tas_federasyon_bayat` / `M_weak_path_forgery`). On 01.10 it was re-run with the same command under the 600 s limit: **78 s, same verdict (verified)**. The record was judged a wall-clock artefact caused by the local machine being suspended (deviation note) |
| Agreement with the expectations | **760/762** (§3) |

## 2. Results (G5 forms; F = trace, V = proof)

### 2.1 Request direction and metadata

| Mechanism | Result | Interpretation |
|---|---|---|
| M-b0 unsigned requests (HAIP + DC API discretion) | the three G5 forms F | Baseline: as long as an unsigned request is accepted, the RP expectation cannot be conveyed |
| M-a unauthenticated negotiation (#791) | three forms F; `M_downgrade_s1` V | The network attacker drops the capability header; the CRQC forges with the classical legacy key |
| M-b / OID4VP A.3.2.2 multi-signature ("one is enough") | three forms F | The weakest trust framework decides. In the **final specification** (OID4VP 1.0) the verification semantics is undefined (T273) |
| M-d PQ registration channel | migrated F (pre-registered expectation F) | PQ-signed registration updates can be replayed; the "none" entry from before the migration is replayed after the migration |
| M-e "supported" (PQ-signed, fresh) | untimed and migrated F; timed V; no_rollback **F (expected V)** | "Supported ≠ required" |
| M-e′ "required" (PQ-signed, fresh) | untimed, migrated, timed V; no_rollback **F (expected V)** | Conditional proof |

### 2.2 M-f and the expectation scope (task 3b)
- **`yol_sinifi` (path class):** all G5 and path forms V against the three attacks. The attacks: alternative CA with a different name, CA with the same name, classical root + PQ intermediate.
- **`anahtar` (key):** G5 V, path forms F.
- **`yaprak_alg` (leaf algorithm):** G1 F.
- **Result:** The expectation must be bound at the **path class** level, not at the leaf or key level. This shows that name or leaf binding is circumvented during a key change (consistent with 5A R7h).

### 2.3 Carrier substitution (A3-7)

| Carrier | Result |
|---|---|
| TL/LoTE, fetched and current | all V |
| OpenID Federation, PQ intermediate | all V |
| TL cache | migrated and timed forms F |
| WRPRC phase 0 | all F |
| WRPRC phase 1 | untimed V; the others F |
| Federation, classical intermediate | all F |
| Federation, stale `trust_chain` | untimed V; the others F |
| `crit` header | all F |

### 2.4 M-h and task 3a
- **reddy-type and vicente-type commitment extensions:** on a classical chain and under all three attacks, the three G5 forms F.
  - (i) A commitment carried only on the classical chain does not protect.
  - (ii) With an alternative CA or a CA with the same name, a certificate without commitment is accepted; reddy + name binding is also F against a CA with a different name.
  - (iii) The per-entity `yol_sinifi` expectation of M-f closes these attacks (§2.2).
- **M-g / sheffer chain policy [8a]:**
  - Under the "key is PQ" reading, all three attacks F.
  - Under the "signature is PQ" reading, no_rollback and G1_learned V, but G5 untimed, migrated and timed F.
  - `M_cache_cleared` (forcing the cache to be cleared) V under the "key" reading.

### 2.5 Offline annex (ANNEX [8b], 2×2)
- In all four definitions, untimed and timed V, migrated F.
- Path no_rollback V only with **broad monotonicity**.
- Path-timed V only with **sunset at expectation level**.
- Both together (`EK_mf_yola_duyarli`) make all three path forms V. This is the rationale of the path-sensitive definition in M-f-DEFINITION.

## 3. The two unexpected results (2/762) — explained

`no_rollback` for `ME_signed_fresh` and `MEP_signed_fresh`: expected V, observed F (15 steps).
- On 01.10 an independent re-run gave the same verdict and number of steps (`sonuc/yeniden_kosum_0110/`).
- **Trace:** The metadata of the non-migrated (legacy) issuer is signed with its own classical key (`Issuer_Setup_Legacy`: `!MetaSk($L, ~kc)`). Once the CRQC extracts this key, the attacker first produces a forged "retired"/"pq_required" response (the verifier "sees" the expectation), then a forged "none" response; classical acceptance takes place.
- **Exploratory check (outside the pre-registration; `kesif/me_gocmus/`):** The lemma was restricted to migrated entities (`no_rollback_migrated`). Result: **verified for M-e (38 steps), verified for M-e′ (45 steps).**
- **Interpretation:** If the object that carries the expectation is signed with the (breakable) key of the very entity the expectation protects, the expectation gives no protection. This is the circularity of a self-declared carrier.
  - The work that wrote the pre-registered expectation had assumed PQ-signed metadata for every issuer. The model, however, also covers the non-migrated issuer.
  - The verdict is **a scope difference, not a model defect.** Independent confirmation: `..\Yeni\makale1` b4 (a different model, the same fact).
- **In the paper:** reported for M-e and M-e′ as "conditional proof only for a migrated issuer; self-signed metadata cannot carry the expectation for a non-migrated entity".

## 4. Consequences for H3 and the scientific gate
- The prediction of H3 held: M-a, M-b (A.3.2.2) and M-b0 gave traces. Under Ö2 these traces alone do not count as (2c′). For (2c) it matters that A.3.2.2 is in the **final** specification.
- The simplified M-f was proven in all G5 forms with the `yol_sinifi` scope. The scope dimension is a candidate non-obvious result (circumvention of name or leaf binding; the reddy and vicente commitment extensions do not protect on a classical chain).
