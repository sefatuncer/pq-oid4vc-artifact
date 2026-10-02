# Step 6: Known-answer tests (KAT), RESULT

- **Date:** 26.09.2026 · **Work:** asp (Step 6) · **Anchor 8:** commit `2d16592` (PR v0.9 §2H)
- **Two runs are presented together (maintainers' decision 26.09.2026):**
  - **first run:** commit `e4c1090`; the KAT-1 FAILED record is kept;
  - **post-correction run:** KAT-1 Tamarin only; `dnssec/KAT1_DNSSEC_v2.spthy`, "correction after the result was seen"; results in `dnssec/sonuc_v2/`.

  At the scientific gate, an independent review will assess V-d.
- **Expected values:** `nsurum/kat_nsurum.tsv` (`3609f793…2aec`), column `ilk_ajan` (single source; K2d Tamarin = `no_silent_promotion`). Not touched.
- **One core:** `models/asp/cekirdek.lp`. Its digest in the three ASP runners: before = after = `a32372a7…0b38` (commit `45cbd0f`). `kat_core.lp` and `hon_decision.lp` were not used.
  - ASP was run only in the first run; the correction does not touch ASP or the core.
- **Preparation identity (before the first run):** `2d23e35b…024b`, 2026-09-26T11:07:00Z (`dnssec/HAZIRLIK_SHA256SUMS`). Mapping and reading rules: `MAPPING.md`.
- **Tools:**
  - clingo 5.8.2: `pq-a02-solver:1.0` (`sha256:02c637eb…`);
  - Tamarin 1.12.0: `pq-a02-tamarin:1.12.0` (`sha256:59b648d6…`).
  - Container prefix `pq-a06-`. Tamarin limits: 12 GB, 600 s.
- **Run measurements:**
  - First run: all Tamarin rows (42 gate and mutation + 9 additional) closed at the first step of the ladder. Longest lemma 2.66 s, peak memory at most 148.2 MiB.
  - Post-correction: 22 rows, all at the first step. Longest 3.33 s, at most 139.1 MiB.
  - Longest ASP cell 3.5 ms.

(Translated from Turkish for this release. The original file, whose hash is recorded in `SHA256SUMS`, is listed in `docs/INTEGRITY.md`. The tables from the section "KAT-1 DNSSEC: first run and post-correction run" onwards are copies of the generated summaries `*/sonuc*/KAT_OZET.md` and `dnssec/sonuc_v2/YANYANA.md`; here their labels are translated, while the generated originals stay as recorded. Data values such as `SALDIRI` (attack), `YOK` (no attack), cell keys and column keys are kept verbatim.)

## Summary (V-d; PR §4.19, work plan 6.6)

| KAT | Run | ASP cells | Tamarin cells | ASP–Tamarin | Mutations (KAT-SPEC §6) | executable / well-formedness | V-d |
|---|---|---|---|---|---|---|---|
| KAT-1 DNSSEC | first run (v1) | 15/15 | **14/15** | **14/15** | 5/5 | all verified / warnings 0 | **FAILED** |
| KAT-1 DNSSEC | post-correction (v2) | 15/15 (first run) | 15/15 | 15/15 | 5/5 | all verified / warnings 0 | **PASSED** |
| KAT-2 X.509 hybrid | first run | 40/40 | 8/8 | 8/8 | 4/4 | all verified / warnings 0 | PASSED |
| KAT-3 S/MIME | first run | 54/54 | 9/9 | 9/9 | 3/3 | all verified / warnings 0 | PASSED |

**V-d:**
- first run: **2/3** (KAT-1 FAILED);
- post-correction: **3/3**.

**Details:**
- `nsurum` 141 keys. In the first run 140 of them at the expected value; the single mismatch is K1-11, Tamarin `a_rrset_authentic`. Post-correction 141/141.
- All 109 ASP values at the expected value in the first run.
- The correction changed only K1-11 (falsified → verified). The verdicts of the other 14 KAT-1 Tamarin cells and of the 7 Tamarin mutation rows are the same as in the first run. Table: the KAT-1 section below.
- Mutations were counted with the "strict turn" criterion: the mutated value is in the expected direction and differs from the unmutated base run.

## K1-11: the mismatch in the first run (trace, diagnosis) and the correction
- **Observed (first run):** falsified, 12 steps (`dnssec/sonuc/tamarin_ham/K1-11.tam__a_rrset_authentic__b1.txt`). In the same cell ASP gave the expected value: YOK.
- **Trace:**
  1. `Break_Zone_Classical`: the classical KSK `~kc` and the ZSK are exposed.
  2. The attacker builds the DNSKEY RRset with its own ZSKs (`pk(x)`, `pk(x.1)`) and signs it with `~kc`.
  3. `Validate_DNSKEY_via_KSKcl`: accepted because the real double DS lists `pk(kc)`.
  4. `DKok` → `Validate_A_complete_both`: the A RRset is signed with two attacker keys.
  5. `AcceptA` happens without `SignedA`.
- **Diagnosis:** a coding error of the test model, on the Tamarin side. The maintainers confirmed it by running two models independently.
  - The draft of KAT-SPEC §2(c) applies `COMPLETENESS` only at the A RRset step; the DNSKEY step remains "any single path".
  - The rule "insist that all algorithms signaled in the DS RRset work" of RFC 6840 §5.11 was not applied at the DNSKEY step.
  - The ASP mapping applies completeness along the whole chain (`tasi(ds,dnskey)`, `tasi(ds,a_rr)`); ASP was correct in the first run.
- **Alternative reading B2 (used only in the diagnosis):** the reading "test only on the DNSKEY RRset" would have made all three of K1-04, K1-06 and K1-11 falsified. Only K1-11 was observed; therefore the difference is not the B2 alternative.
- **Correction (maintainers' decision):** `dnssec/KAT1_DNSSEC_v2.spthy` = the rules of the diagnosis model (`dnssec/tani/`), "corrected gate model".
  - **Single extension:** the §6 mutation alternatives were defined for the v2 validators; under `COMPLETENESS` completeness is kept and only the named check is removed. In the diagnosis model the old validators came into play in this case.
  - In every flag set without `COMPLETENESS`, v2 is the same as v1 (diff: STEP06-REPORT §8).
  - `KAT1_DNSSEC.spthy` was left untouched.
- **Post-correction run:**
  - All 15 cells and 7 mutation rows were rerun with v2.
  - Only K1-11 changed (verified, 28 steps); the verdict of the other 21 rows is the same as with v1.
  - Well-formedness: 16/16 flag sets, warnings 0.
- **Rule (PR §2C.1):** no switch to a fallback test; the expected value was not touched. The FAILED record of the first run is kept; the two runs are presented together.

## Additional items (not in `nsurum`; reported separately)
- **KAT-2 Tamarin sensitivity lemmas** (`accept_with_invalid_pq`, KAT-SPEC §3(d)): 3/3 in the expected direction. V_IGNORE verified: acceptance with corrupted PQ evidence is reachable (Kim's finding). V_ENFORCE_IF_PRESENT and V_REQUIRE falsified.
- **KAT-3a (KAT-SPEC §4(d)):** `kat3a_fail` empty; `model_gap` only o8 (reading note; not attributed to the authors).
- **KAT-3b pilot well-formedness correction — ACCEPTED by the maintainers (26.09.2026):**
  - The model with the warning (the original pilot) is invalid; the copy with the one-word correction (`smime/weakest_link_wf.spthy`) is the gate cell.
  - The original pilot gave the same verdict and the same number of steps 6/6 (`smime/sonuc/tamarin_ek.csv`); this remains as information.

## Step 6 acceptance criteria (work plan 6.6)
1. **V-d:**
   - first run: 2/3 KAT PASSED (KAT-1 FAILED; Tamarin K1-11);
   - post-correction: 3/3.

   The independent review will assess both together.
2. **The blind table of expected values was hashed before the first run:** yes. `kor-beklenen/BEKLENEN-KOR.tsv` `180a655a…` (commit `f012841`); the agreed table `nsurum/kat_nsurum.tsv` at anchor 8.
3. **The digest of the core (`cekirdek.lp`) is the same before and after the tests:** yes (the correction did not touch ASP).
4. **Verbatim quotations found by script in the pinned text:** 21/21 (`*/sonuc/alinti_denetimi.tsv`).

## How it was produced
- **Each folder:** `uret.py` (instance files) → `kos.py` (ASP; container) → `tamarin_kos.py kos` (Tamarin; with the ladder) → `degerlendir.py` (runs nothing) → `sonuc/KAT_OZET.{json,md}`.
- **Post-correction (KAT-1 Tamarin only):** `dnssec/tamarin_kos_v2.py` → `dnssec/degerlendir_v2.py` → `dnssec/sonuc_v2/KAT_OZET.{json,md}` → `dnssec/yanyana_v1_v2.py` → `dnssec/sonuc_v2/YANYANA.md`.
  - `tamarin_kos_v2.py` imports the frozen runner without changing it.
  - `degerlendir_v2.py` was derived mechanically from `degerlendir.py` by changing only path and label lines.
- **The sections below:**
  - KAT-1: `YANYANA.md`;
  - KAT-2 and KAT-3: verbatim copies of the `KAT_OZET.md` files of the first run;
  - the KAT-1 summary of the first run stays as it is in `dnssec/sonuc/KAT_OZET.md`.

---

## KAT-1 DNSSEC: first run and post-correction run (side by side)

**KAT decision:**

- first run (v1, `KAT1_DNSSEC.spthy`, commit `e4c1090`): **FAILED**
- post-correction (v2, `KAT1_DNSSEC_v2.spthy`; "correction after the result was seen"): **PASSED**

| Condition | First run (v1) | Post-correction (v2) |
|---|---|---|
| ASP cells | 15/15 | 15/15 |
| Tamarin cells | 14/15 | 15/15 |
| ASP–Tamarin agreement | 14/15 | 15/15 |
| Mutations (KAT-SPEC §6) | 5/5 | 5/5 |
| executable all verified | yes | yes |
| Well-formedness (warnings 0) | yes | yes |
| Core digest before = after = 45cbd0f | yes | yes |

ASP is the first run; it was not rerun and `cekirdek.lp` was not touched. v2 changes only the Tamarin side.

| Cell | ASP expected | ASP observed | Tamarin expected | Tamarin first run (v1) | Tamarin post-correction (v2) | v2 steps | v1→v2 |
|---|---|---|---|---|---|---|---|
| K1-01 | SALDIRI | SALDIRI | falsified | falsified | falsified | 12 | same |
| K1-02 | SALDIRI | SALDIRI | falsified | falsified | falsified | 12 | same |
| K1-03 | SALDIRI | SALDIRI | falsified | falsified | falsified | 12 | same |
| K1-04 | YOK | YOK | verified | verified | verified | 18 | same |
| K1-05 | SALDIRI | SALDIRI | falsified | falsified | falsified | 12 | same |
| K1-06 | YOK | YOK | verified | verified | verified | 18 | same |
| K1-07 | SALDIRI | SALDIRI | falsified | falsified | falsified | 12 | same |
| K1-08 | YOK | YOK | verified | verified | verified | 21 | same |
| K1-09 | YOK | YOK | verified | verified | verified | 19 | same |
| K1-10 | SALDIRI | SALDIRI | falsified | falsified | falsified | 12 | same |
| K1-11 | YOK | YOK | verified | falsified ✗ | verified | 28 | **changed** |
| K1-12 | SALDIRI | SALDIRI | falsified | falsified | falsified | 14 | same |
| K1-13 | YOK | YOK | verified | verified | verified | 22 | same |
| K1-14 | SALDIRI | SALDIRI | falsified | falsified | falsified | 8 | same |
| K1-15 | SALDIRI | SALDIRI | falsified | falsified | falsified | 12 | same |

| Mutation run | Expected | ASP (first run) | Tamarin v1 | Tamarin v2 | v2 differs from the base cell |
|---|---|---|---|---|---|
| MUT01.K1-04.tam | falsified | SALDIRI | falsified | falsified | yes |
| MUT01.K1-11.tam | falsified | SALDIRI | falsified | falsified | yes |
| MUT02.K1-04.tam | falsified | SALDIRI | falsified | falsified | yes |
| MUT03.K1-04.tam | falsified | SALDIRI | falsified | falsified | yes |
| MUT04.K1-06.tam | falsified | SALDIRI | falsified | falsified | yes |
| MUT04.K1-08.tam | falsified | SALDIRI | falsified | falsified | yes |
| MUT05.K1-09.tam | falsified | SALDIRI | falsified | falsified | yes |

| Mutation | First run (engine: turned?) | Post-correction (engine: turned?) |
|---|---|---|
| MUT01 | asp: yes, tamarin: yes | asp: yes, tamarin: yes |
| MUT02 | asp: yes, tamarin: yes | asp: yes, tamarin: yes |
| MUT03 | asp: yes, tamarin: yes | asp: yes, tamarin: yes |
| MUT04 | asp: yes, tamarin: yes | asp: yes, tamarin: yes |
| MUT05 | asp: yes, tamarin: yes | asp: yes, tamarin: yes |

## KAT-2 X.509 hybrid — PASSED

| Condition | Result |
|---|---|
| ASP cells | 40/40 |
| Tamarin cells | 8/8 |
| executable (every Tamarin run) | all verified |
| Well-formedness (warnings 0) | yes |
| ASP–Tamarin agreement | 8/8 |
| Mutations (KAT-SPEC §6) | 4/4 |
| Core digest before = after = 45cbd0f | yes |
| Verbatim quotations | 9/9 |

| Cell | Column | Expected | Observed | Core basis |
|---|---|---|---|---|
| K2a-01 | decision(pqev=valid) | accept_classical | accept_classical | G5 |
| K2a-02 | decision(pqev=invalid) | accept_classical | accept_classical | G5 |
| K2a-03 | decision(pqev=valid) | accept_classical | accept_classical | G5 |
| K2a-04 | decision(pqev=invalid) | accept_classical | accept_classical | G5 |
| K2a-05 | decision(pqev=valid) | accept_classical | accept_classical | G5 |
| K2a-06 | decision(pqev=invalid) | accept_classical | accept_classical | G5 |
| K2a-07 | decision(leafb=valid) | accept_classical | accept_classical | G5 |
| K2a-08 | decision(leafb=revoked) | accept_classical | accept_classical | G5 |
| K2a-09 | decision(pqev=valid) | accept_hybrid | accept_hybrid | not G5 |
| K2a-10 | decision(pqev=invalid) | reject | reject | not G5 |
| K2a-11 | decision(pqev=absent) | accept_classical | accept_classical | G5 |
| K2a-12 | decision(pqev=valid) | accept_hybrid | accept_hybrid | not G5 |
| K2a-13 | decision(pqev=invalid) | reject | reject | not G5 |
| K2a-14 | decision(pqev=absent) | reject | reject | not G5 |
| K2a-15 | decision(pqev=valid) | accept_hybrid | accept_hybrid | not G5 |
| K2a-16 | decision(pqev=invalid) | reject | reject | not G5 |
| K2a-17 | decision(pqev=valid) | reject | reject | not G5 |
| K2b-01 | ASP | SALDIRI | SALDIRI | g1 |
| K2b-02 | ASP | SALDIRI | SALDIRI | g1 |
| K2b-03 | ASP | YOK | YOK | g1 |
| K2b-04 | ASP | SALDIRI | SALDIRI | g1 |
| K2b-05 | ASP | YOK | YOK | g1 |
| K2b-06 | ASP | YOK | YOK | g1 |
| K2b-07 | ASP | SALDIRI | SALDIRI | g1 |
| K2b-08 | ASP | YOK | YOK | g1 |
| K2c-revoked | karar(vb=ignore) | accept_classical | accept_classical | G5 |
| K2c-revoked | karar(vb=require) | reject | reject | not G5 |
| K2c-expired | karar(vb=ignore) | accept_classical | accept_classical | G5 |
| K2c-expired | karar(vb=require) | reject | reject | not G5 |
| K2c-unknown | karar(vb=ignore) | accept_classical | accept_classical | G5 |
| K2c-unknown | karar(vb=require) | indeterminate | indeterminate | not G5 |
| K2c-absent | karar(vb=ignore) | accept_classical | accept_classical | G5 |
| K2c-absent | karar(vb=require) | reject | reject | not G5 |
| K2c-valid | karar(vb=ignore) | accept_classical | accept_classical | G5 |
| K2c-valid | karar(vb=require) | accept_hybrid | accept_hybrid | not G5 |
| K2d-01 | ASP:karar | accept_classical | accept_classical | G5 |
| K2d-02 | ASP:karar | accept_classical | accept_classical | G5 |
| K2d-03 | ASP:karar | reject | reject | not G5 |
| K2d-04 | ASP:karar | reject | reject | not G5 |
| K2d-05 | ASP:karar | accept_classical | accept_classical | G5 |
| K2b-01 | Tamarin:cert_authentic | falsified | falsified | Tamarin (CRQC,V_IGNORE) |
| K2b-02 | Tamarin:cert_authentic | falsified | falsified | Tamarin (CRQC,V_ENFORCE_IF_PRESENT) |
| K2b-03 | Tamarin:cert_authentic | verified | verified | Tamarin (CRQC,V_REQUIRE) |
| K2b-06 | Tamarin:cert_authentic | verified | verified | Tamarin (CRQC,COMPOSITE) |
| K2b-07 | Tamarin:cert_authentic | falsified | falsified | Tamarin (CRQC,COMPOSITE,COEXIST_CLASSICAL) |
| K2d-01 | Tamarin | falsified | falsified | Tamarin (M1_LEGACY,V_IGNORE) |
| K2d-02 | Tamarin | falsified | falsified | Tamarin (M1_LEGACY,V_ENFORCE_IF_PRESENT) |
| K2d-03 | Tamarin | verified | verified | Tamarin (M1_LEGACY,V_REQUIRE) |

| Mutation | Engine: turned? |
|---|---|
| MUT06 | asp: yes, tamarin: yes |
| MUT07 | asp: yes, tamarin: yes |
| MUT08 | asp: yes |
| MUT09 | asp: yes |

Additional (not a gate cell; KAT-SPEC §3(d) sensitivity lemmas):

| Run | Expected (KAT-SPEC) | Observed | Well-formed |
|---|---|---|---|
| EK.duy-ignore.tam | verified | verified | YES |
| EK.duy-enforce.tam | falsified | falsified | YES |
| EK.duy-require.tam | falsified | falsified | YES |

## KAT-3 S/MIME — PASSED

| Condition | Result |
|---|---|
| ASP cell values (3a: 36, 3b: 18) | 54/54 |
| Tamarin cells | 9/9 |
| executable (every Tamarin run) | all verified |
| Well-formedness (warnings 0; gate models) | yes |
| ASP–Tamarin agreement | 9/9 |
| Mutations (KAT-SPEC §6) | 3/3 |
| Core digest before = after = 45cbd0f | yes |
| KAT-SPEC §4(d) additional: kat3a_fail empty / model_gap only o8 | yes / yes |
| Verbatim quotations | 5/5 |

| Cell | Column | Expected | Observed | Basis |
|---|---|---|---|---|
| V1 | attack(qday=0) | SALDIRI | SALDIRI | V1.qday0.asp |
| V1 | attack(qday=200) | YOK | YOK | V1.qday200.asp |
| V1 | violation(qday=0) | 1 | 1 | V1.statik.asp |
| V2 | attack(qday=0) | SALDIRI | SALDIRI | V2.qday0.asp |
| V2 | attack(qday=200) | YOK | YOK | V2.qday200.asp |
| V2 | violation(qday=0) | 1 | 1 | V2.statik.asp |
| V3 | attack(qday=0) | SALDIRI | SALDIRI | V3.qday0.asp |
| V3 | attack(qday=200) | YOK | YOK | V3.qday200.asp |
| V3 | violation(qday=0) | 1 | 1 | V3.statik.asp |
| V4 | attack(qday=0) | YOK | YOK | V4.qday0.asp |
| V4 | attack(qday=200) | YOK | YOK | V4.qday200.asp |
| V4 | violation(qday=0) | 0 | 0 | V4.statik.asp |
| V5 | attack(qday=0) | YOK | YOK | V5.qday0.asp |
| V5 | attack(qday=200) | YOK | YOK | V5.qday200.asp |
| V5 | violation(qday=0) | 0 | 0 | V5.statik.asp |
| V6 | attack(qday=0) | SALDIRI | SALDIRI | V6.qday0.asp |
| V6 | attack(qday=200) | YOK | YOK | V6.qday200.asp |
| V6 | violation(qday=0) | 1 | 1 | V6.statik.asp |
| o1 | out | pqc_protected | pqc_protected | bilinmeyen=0 gecersiz=0 gecis=0 kati=0 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o1 | accept_strict | 1 | 1 | bilinmeyen=0 gecersiz=0 gecis=0 kati=0 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o1 | accept_transitional | 1 | 1 | bilinmeyen=0 gecersiz=0 gecis=0 kati=0 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o2 | out | pqc_protected | pqc_protected | bilinmeyen=0 gecersiz=0 gecis=0 kati=0 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o2 | accept_strict | 1 | 1 | bilinmeyen=0 gecersiz=0 gecis=0 kati=0 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o2 | accept_transitional | 1 | 1 | bilinmeyen=0 gecersiz=0 gecis=0 kati=0 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o3 | out | classical_only | classical_only | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=0 tum_klasik_yol=1 |
| o3 | accept_strict | 0 | 0 | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=0 tum_klasik_yol=1 |
| o3 | accept_transitional | 0 | 0 | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=0 tum_klasik_yol=1 |
| o4 | out | unsafe_mixed | unsafe_mixed | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=1 tum_klasik_yol=1 |
| o4 | accept_strict | 0 | 0 | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=1 tum_klasik_yol=1 |
| o4 | accept_transitional | 0 | 0 | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=1 tum_klasik_yol=1 |
| o5 | out | hybrid_protected | hybrid_protected | bilinmeyen=0 gecersiz=0 gecis=0 kati=1 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o5 | accept_strict | 0 | 0 | bilinmeyen=0 gecersiz=0 gecis=0 kati=1 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o5 | accept_transitional | 1 | 1 | bilinmeyen=0 gecersiz=0 gecis=0 kati=1 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o6 | out | unsafe_mixed | unsafe_mixed | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=1 tum_klasik_yol=1 |
| o6 | accept_strict | 0 | 0 | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=1 tum_klasik_yol=1 |
| o6 | accept_transitional | 0 | 0 | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=1 tum_klasik_yol=1 |
| o7 | out | unknown | unknown | bilinmeyen=1 gecersiz=0 gecis=1 kati=1 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o7 | accept_strict | 0 | 0 | bilinmeyen=1 gecersiz=0 gecis=1 kati=1 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o7 | accept_transitional | 0 | 0 | bilinmeyen=1 gecersiz=0 gecis=1 kati=1 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o8 | out | pqc_protected | pqc_protected | bilinmeyen=0 gecersiz=0 gecis=0 kati=0 klasik=0 pq_hibrit=1 tum_klasik_yol=1 |
| o8 | accept_strict | 1 | 1 | bilinmeyen=0 gecersiz=0 gecis=0 kati=0 klasik=0 pq_hibrit=1 tum_klasik_yol=1 |
| o8 | accept_transitional | 1 | 1 | bilinmeyen=0 gecersiz=0 gecis=0 kati=0 klasik=0 pq_hibrit=1 tum_klasik_yol=1 |
| o9 | out | invalid | invalid | bilinmeyen=0 gecersiz=1 gecis=1 kati=1 klasik=0 pq_hibrit=0 tum_klasik_yol=0 |
| o9 | accept_strict | 0 | 0 | bilinmeyen=0 gecersiz=1 gecis=1 kati=1 klasik=0 pq_hibrit=0 tum_klasik_yol=0 |
| o9 | accept_transitional | 0 | 0 | bilinmeyen=0 gecersiz=1 gecis=1 kati=1 klasik=0 pq_hibrit=0 tum_klasik_yol=0 |
| o10 | out | unknown | unknown | bilinmeyen=1 gecersiz=0 gecis=1 kati=1 klasik=0 pq_hibrit=0 tum_klasik_yol=0 |
| o10 | accept_strict | 0 | 0 | bilinmeyen=1 gecersiz=0 gecis=1 kati=1 klasik=0 pq_hibrit=0 tum_klasik_yol=0 |
| o10 | accept_transitional | 0 | 0 | bilinmeyen=1 gecersiz=0 gecis=1 kati=1 klasik=0 pq_hibrit=0 tum_klasik_yol=0 |
| o11 | out | hybrid_protected | hybrid_protected | bilinmeyen=0 gecersiz=0 gecis=0 kati=1 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o11 | accept_strict | 0 | 0 | bilinmeyen=0 gecersiz=0 gecis=0 kati=1 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o11 | accept_transitional | 1 | 1 | bilinmeyen=0 gecersiz=0 gecis=0 kati=1 klasik=0 pq_hibrit=1 tum_klasik_yol=0 |
| o12 | out | classical_only | classical_only | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=0 tum_klasik_yol=1 |
| o12 | accept_strict | 0 | 0 | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=0 tum_klasik_yol=1 |
| o12 | accept_transitional | 0 | 0 | bilinmeyen=0 gecersiz=0 gecis=1 kati=1 klasik=1 pq_hibrit=0 tum_klasik_yol=1 |
| MIXED | Tamarin:cek_secrecy | falsified | falsified | Tamarin (MIXED; KAT3_SMIME.spthy) |
| PQ_ONLY | Tamarin:cek_secrecy | verified | verified | Tamarin (PQ_ONLY; KAT3_SMIME.spthy) |
| HYBRID_KEM | Tamarin:cek_secrecy | verified | verified | Tamarin (HYBRID_KEM; KAT3_SMIME.spthy) |
| V1 | Tamarin:claims_unforgeability | falsified | falsified | Tamarin (-; weakest_link_wf.spthy) |
| V2 | Tamarin:claims_unforgeability | falsified | falsified | Tamarin (EXPECT_IN_TL; weakest_link_wf.spthy) |
| V3 | Tamarin:claims_unforgeability | falsified | falsified | Tamarin (TL_PQ; weakest_link_wf.spthy) |
| V4 | Tamarin:claims_unforgeability | verified | verified | Tamarin (TL_PQ,EXPECT_IN_TL; weakest_link_wf.spthy) |
| V5 | Tamarin:claims_unforgeability | verified | verified | Tamarin (TL_PQ,NO_COEXIST; weakest_link_wf.spthy) |
| V6 | Tamarin:claims_unforgeability | falsified | falsified | Tamarin (NO_COEXIST; weakest_link_wf.spthy) |

| ASP–Tamarin shared cell | ASP (in Tamarin terms) | Tamarin |
|---|---|---|
| MIXED<->o4 | falsified | falsified |
| PQ_ONLY<->o1 | verified | verified |
| HYBRID_KEM<->o5 | verified | verified |
| V1 | falsified | falsified |
| V2 | falsified | falsified |
| V3 | falsified | falsified |
| V4 | verified | verified |
| V5 | verified | verified |
| V6 | falsified | falsified |

| Mutation | Engine: turned? |
|---|---|
| MUT10 | tamarin: yes |
| MUT11 | asp: yes |
| MUT12 | asp: yes |

Additional (not a gate cell): KAT-3b Tamarin with the ORIGINAL pilot (with a well-formedness warning):

| Run | Expected (nsurum) | Observed (raw) | Well-formed |
|---|---|---|---|
| EK.V1.pilot_asli.tam | falsified | falsified | NO |
| EK.V2.pilot_asli.tam | falsified | falsified | NO |
| EK.V3.pilot_asli.tam | falsified | falsified | NO |
| EK.V4.pilot_asli.tam | verified | verified | NO |
| EK.V5.pilot_asli.tam | verified | verified | NO |
| EK.V6.pilot_asli.tam | falsified | falsified | NO |

## Details of the diagnosis run (dnssec/tani/sonuc.csv; AFTER THE RESULT WAS SEEN; precursor of the v2 correction, NOT a gate value)

| Cell | Flags | Expected | Diagnosis model | Steps | Well-formed | executable |
|---|---|---|---|---|---|---|
| K1-02 | DS_CL,DK3_USABLE,COMPLETENESS | falsified | falsified | 12 | YES | verified |
| K1-04 | DS_PQ,DK3_USABLE,COMPLETENESS | verified | verified | 18 | YES | verified |
| K1-05 | DS_PQ,OLD_DS_REPLAY,DK3_USABLE,COMPLETENESS | falsified | falsified | 12 | YES | verified |
| K1-06 | DS_PQ,DK3_USABLE,COMPLETENESS | verified | verified | 18 | YES | verified |
| K1-11 | DS_BOTH,DK3_USABLE,COMPLETENESS | verified | verified | 28 | YES | verified |
| K1-12 | DS_PQ,DK3_USABLE,COMPLETENESS,PARENT_CL | falsified | falsified | 14 | YES | verified |
