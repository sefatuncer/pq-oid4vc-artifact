# Step 6: Known-answer tests (KAT), report

- **Date:** 26.09.2026 · **Work:** asp (Step 6)
- **Folder:** `models\known-answer-tests\`. Written only to: `ESLEME.md` (now `MAPPING.md`), `dnssec\`, `x509\`, `smime\`, `SONUC.md` (now `RESULTS.md`), `ADIM06-RAPOR.md` (this file, now `STEP06-REPORT.md`), `SHA256SUMS`. `kor-beklenen\` and `nsurum\` read-only (except the temporary accident of §2.4).
- **Single source of the expected values (FIXED, not changed):** `nsurum\kat_nsurum.tsv` (`3609f793…2aec`), column `ilk_ajan`. K2d Tamarin lemma `no_silent_promotion` (PR §2H.1). Anchor 8: commit `2d16592`.
- **Single core:** the KAT cells were run only with `models\asp\cekirdek.lp` and the instance files of this folder. SHA-256 of `cekirdek.lp` = `a32372a7c646274ce672c9586e25b34f75f4febb2f966596cc97e7afb89e0b38` (byte-identical with commit `45cbd0f`); the same before and after the run.
- **Result (details in `RESULTS.md`):**
  - **First run (commit `e4c1090`):**
    - V-d 2/3: KAT-2 and KAT-3 PASSED, **KAT-1 FAILED**.
    - 140 of the 141 `nsurum` keys at the expected value; ASP 109/109, Tamarin 31/32, ASP–Tamarin 31/32, mutations 12/12.
    - The only disagreement: K1-11 Tamarin. Diagnosis: a scope error of the completeness test in the Tamarin draft of KAT-SPEC §2(c) (§5).
  - **After the correction (maintainers' decision of 26.09.2026; §8):**
    - KAT-1 Tamarin re-run with v2; **KAT-1 PASSED**: Tamarin 15/15, ASP–Tamarin 15/15, mutations 5/5.
    - V-d **3/3**; `nsurum` 141/141.
    - Only K1-11 changed.
    - The two runs are presented together.

## 1. Preparation freeze (BEFORE the first run)
- `SHA256SUMS` (its state at that moment): 319 files. Scope:
  - ESLEME.md;
  - base and instance files, cell and mutation tables, Tamarin models, runners and evaluators;
  - well-formedness and quote evidence;
  - external references: `../asp/cekirdek.lp`, `nsurum/kat_nsurum.tsv`, the original pilot `b079cbbb…bd47`.
- **Preparation identity** = the SHA-256 of that file: `2d23e35b146d63856c9936c963cd6fffd7526b24008e579c5c8f3b951a85024b`, **2026-09-26T11:07:00Z**. Until that moment no KAT cell had been run.
- The frozen list is kept byte-identical as `dnssec\HAZIRLIK_SHA256SUMS`. It is in this folder because only `SHA256SUMS` could be written at the top level; it covers the three KATs.
- The final `SHA256SUMS` covers the final state of all files.

## 2. Preparation findings
1. **The pilot model is not well-formed (KAT-3b).**
   - Error: "Fact multiplicity issues". The name `Qday` is both an action and a persistent fact; seen in all six configurations.
   - The decision was taken before the run (MAPPING §4.5):
     - the gate cells were run with a well-formed copy that differs by one word (`smime/weakest_link_wf.spthy`; action name `Qday()` → `QdayOlayi()`; the action occurs in no lemma);
     - the original pilot was run in addition.
   - **Result:** the two models gave the same verdict and the same number of steps (6/6). The approval nevertheless lies with the maintainers.
2. **Tamarin well-formedness (no `--prove`):**
   - KAT-1 16/16;
   - KAT-2 12/12;
   - KAT-3a 4/4;
   - KAT-3b well-formed copy 6/6;
   - 0 warnings in all.

   The original pilot has warnings in 6/6. Every lemma call of the run re-checked well-formedness: 0 warnings in the gate models.
3. **Quotes:** 21/21 found verbatim.
   - 20 were found with whitespace normalisation only; A2-7 with the `tire_sil` (hyphen removal) step because of a hyphen lost in the PDF extraction.
   - The RFC text digests are identical to the MANIFEST. The digests of the paper texts were recorded during the preparation; the MANIFEST keeps only the PDF digests.
4. **Transparency (accident):**
   - What happened: during the syntax check the pattern `*/*.py` also compiled `nsurum/kat_nsurum.py` and created `nsurum/__pycache__/` (14:06).
   - What was done: it was deleted within the same minute. `nsurum/SHA256SUMS` OK on three files; git status clean. The expected values were not touched.
   - Similarly, a list file was accidentally written to `/tmp` and deleted.
5. **Tamarin waiting rule:**
   - Situation: the Step 7 jobs of the Tamarin work were running back to back.
   - Application: the runner waits only while a Tamarin container using ≥ 2 GiB of memory exists. The KAT jobs are small (at most 148 MiB) and can run at the same time as light jobs ("one HEAVY job at a time").

## 3. Run order
1. **ASP (after anchor 8):**
   - Results: KAT-1 15/15, KAT-2 40/40, KAT-3 54/54 cell values; all mutation runs in the expected direction; `kat3a_fail` empty, `model_gap` = {o8}.
   - Core: its digest in the three runners before and after `a32372a7…0b38`.
   - Time: longest cell 3.5 ms.
2. **Tamarin, first attempt:** stopped at the first call with a runner error; NO Tamarin result was produced (§4.1).
3. **Tamarin, re-run:**
   - KAT-1: 15 cells + 7 mutation rows;
   - KAT-2: 8 + 2 mutations + 3 extra;
   - KAT-3: 9 + 1 mutation + 6 extra (original pilot).

   In every row `executable` + the target lemma ran; all closed on the first rung of the ladder. Disagreement: only K1-11.
4. **Evaluation:** in each folder `degerlendir.py` produces `sonuc/KAT_OZET.{json,md}`; `RESULTS.md` is their combination.
5. **Diagnosis (AFTER RESULTS WERE SEEN; not a gate value):** `dnssec/tani/` (§5).

## 4. Post-freeze changes (label "after results were seen")
1. **`{dnssec,x509,smime}/tamarin_kos.py`, line 81.**
   - Problem: the output path inside the container was built with the Windows separator. `os.path.join('sonuc','tamarin_ham')` → `sonuc\tamarin_ham`, which is invalid as a Linux path. Therefore the first Tamarin call could not produce output.
   - Fix: `cikti_dizin` → `cikti_dizin.replace('\\', '/')`.
   - Effect: path format only; semantics, flags, lemmas and reading rule unchanged. At the time of the change there was no Tamarin result yet.
2. **`{dnssec,x509,smime}/degerlendir.py`, strict mutation criterion.**
   - Change: the first version counted a mutation row as flipped if "the mutated value is at the expected value". The new version also requires it to be "different from the observed value of the unmutated base run" (KAT-SPEC §6: "must flip").
   - Why: because of the Tamarin K1-11 row of MUT01. Since K1-11 is falsified in the unmutated state as well, the first version would wrongly count it as "flipped".
   - Effect: the change can only reduce the number of killed mutations. The result did not change: MUT01 is flipped by K1-04; 12/12.
3. **Added diagnosis files:** `dnssec/tani/KAT1_DNSSEC_tani.spthy`, `tani_kos.py`, `sonuc.csv` (§5). They touch no frozen file; `tani_kos.py` imports `tamarin_kos.py` without changing it.
4. **Added record:** `dnssec/HAZIRLIK_SHA256SUMS` (byte-identical copy of the frozen list).

All other preparation files (mapping, base and instance files, tables, models, the `kos.py` files) are identical to their frozen state. Verification: `sha256sum -c` with `dnssec/HAZIRLIK_SHA256SUMS`. The expected failures are only the six files of §4.1–4.2.

## 5. Diagnosis of the K1-11 disagreement
- **Observed:** Tamarin `a_rrset_authentic` = falsified (12 steps); verified expected. In the same cell ASP YOK (as expected).
- **Trace** (`dnssec/sonuc/tamarin_ham/K1-11.tam__a_rrset_authentic__b1.txt`):
  1. `Break_Zone_Classical` exposes the classical KSK and ZSK.
  2. The attacker builds a DNSKEY RRset with its own ZSKs and signs it with the classical KSK.
  3. `Validate_DNSKEY_via_KSKcl` accepts it through the real double DS.
  4. `Validate_A_complete_both` accepts the A RRset signed with the two attacker keys.
- **Diagnosis:** a model error, on the Tamarin side.
  - The KAT-SPEC §2(c) draft encodes the completeness test (COMPLETENESS) only at the A RRset step; the DNSKEY step stays "any single path".
  - When the DS signals two algorithms (DS_BOTH), the PQ requirement becomes void.
  - This contradicts the cell definition ("both algorithms required") and the reading written by the blind derivation in B2 ("on the whole chain").
  - The ASP mapping applies completeness to the whole chain and gives the expected value.
- **The B2 alternative (in the diagnosis only):** the reading "only at the DNSKEY" would make all three of K1-04, K1-06 and K1-11 falsified. Only K1-11 is observed. So it is not the B2 alternative; an implicit third scope ("only the leaf") entered the draft.
- **Diagnosis run:** `dnssec/tani/KAT1_DNSSEC_tani.spthy` applies completeness to the DNSKEY step as well. The six COMPLETENESS cells (K1-02, K1-04, K1-05, K1-06, K1-11, K1-12) are 6/6 at the expected value: K1-11 verified (28 steps), the others unchanged.
- **Rule:** no switch to an alternative test, the expected value was not touched. The KAT-1 gate result is FAILED. Adopting the corrected model is a decision of the maintainers (§7 N-KAT-1).

## 6. End-of-step review (work plan 6.10)
**1. Plan vs. actual.**
- All three tests were built and run.
- The S/MIME mapping was built as a CEK-based structure mapping (MAPPING §4); no alternative test was needed.
- KAT-2 and KAT-3 PASSED. KAT-1 FAILED (Tamarin K1-11).

**2. Quality check.**
- **Do the PASSED/FAILED verdicts rest on tool output?** Yes. Every value comes from `sonuc/*.csv`; the reading rules were fixed before the run (MAPPING §2.5, §3.4, §4.4, §4.5).
- **Did the core stay unchanged?** Yes; digest before = after.
- **Does the mapping go beyond the scope of the claim?**
  - In KAT-1 the version validity is in the ecosystem derivation rules.
  - In the KAT-2 decision cells the evidence validity is in the reading rule.
  - In KAT-3a the class labels are in the reading rule.
  - The policy/security logic is in the core (MAPPING §5).
  - The claims must be reported limited to this scope: the core does not classify; it computes the PQ-sensitive part of the classification.
- **Is the blind table independent and hashed in advance?** Yes (blind work, commit `f012841`; nsurum anchor 8).
- **Was V-d evaluated with the cell tables?** Yes (`nsurum` 141 keys + KAT-SPEC §6).

**3. Effect on other steps.**

| Affected step | Effect | Required change | Decision |
|---|---|---|---|
| Step 8 | V-d first run 2/3 (KAT-1 FAILED, Tamarin model); after the correction 3/3 | The two runs together into the gate report; the independent review evaluates | maintainers: v2 accepted (26.09) |
| Step 3 | NO core change was NEEDED (ASP 109/109) | none | – |
| Step 14 | Generalisability subsection | ASP core 109/109 in three ecosystems; the structure mapping of S/MIME and scope limits (MAPPING §4.2, §5) | maintainers |
| PR | The corrected K1-11 model and the pilot well-formedness decision | into §11 with the label "after results were seen"; no alternative test chosen | maintainers |

**4. Currency and scooping.** No web access in this step; the currency check is part of the maintainers' project notes routine.

**5. Decision.** Continue.
- The maintainers accepted the corrected Tamarin model with the label "correction after results were seen" (26.09.2026).
- KAT-1 PASSED with v2; the FAILED record of the first run is kept (§8).
- No switch to an alternative test.

## 7. Notes to the maintainers
- **N-KAT-1 (DECIDED, 26.09.2026):** KAT-1 K1-11 Tamarin disagreement.
  - Decision: the corrected Tamarin model was accepted with the label "correction after results were seen". The FAILED record of the first run is kept.
  - Implementation: `dnssec/KAT1_DNSSEC_v2.spthy`, all KAT-1 Tamarin cells and mutations → `dnssec/sonuc_v2/` (§8).
- **N-KAT-2 (DECIDED, 26.09.2026):** the well-formedness fix of the KAT-3b pilot was ACCEPTED. A model with warnings is invalid; the copy with the one-word fix is the gate cell. That the original gives the same verdict stays in the report.
- **N-KAT-3 (information):** the KAT-3a ASP–Tamarin correspondence (MIXED↔o4, PQ_ONLY↔o1, HYBRID_KEM↔o5; probe `klasik`) was not named in KAT-SPEC; it was defined in MAPPING §4.6 before the run.
- **N-KAT-4 (information):** the KAT-2 sensitivity lemmas and the KAT-3a `kat3a_fail`/`model_gap` are not in `nsurum`; they were reported as extras (all in the expected direction).
- **N-KAT-5 (information):** the `nsurum/__pycache__` accident (§2.4); cleaned, integrity verified.

## 8. Run after the correction (v2; CORRECTION AFTER RESULTS WERE SEEN, maintainers' decision of 26.09.2026)
- **Model:** `dnssec/KAT1_DNSSEC_v2.spthy` (`1df11c22…f21b`), the "corrected gate model". `KAT1_DNSSEC.spthy` was not touched (`0a77dc2e…19bd`; identical to the preparation list).
- **Difference v1 → v2** (excluding the header comment; `diff`):
  1. theory name `…_v2`;
  2. a `not COMPLETENESS` condition on the three old DNSKEY validator blocks (these blocks are active only in flag sets without the completeness test; their content is unchanged);
  3. three new blocks for `COMPLETENESS`:
     - validators with completeness (`Validate_DNSKEY_complete_{cl,pq,both}`); rule for rule identical to the unmutated block of the diagnosis model (digest `0c588cb9…`);
     - their `MUT_NO_DS_SIG` alternative (only the DS signature check removed);
     - their `MUT_NO_DS_KSK_MATCH` alternative (only the DS–KSK match removed).
  - Result: in every flag set without `COMPLETENESS`, v2 is identical to v1.
  - The only difference from the diagnosis model: the mutation alternatives are defined relative to the v2 validators. In the diagnosis model `COMPLETENESS` + `MUT_*` fell back to the old validators without completeness; that meant the mutation removed two protections at once.
- **Runners:**
  - `dnssec/tamarin_kos_v2.py` (`c19f6972…c429`): imports the frozen `tamarin_kos.py` without changing it; changes only the model and the output folder (`sonuc_v2/`). Cells, flags, lemmas, ladder and limits are the same as in the first run.
  - `dnssec/degerlendir_v2.py` (`b642fc44…03e3`): derived mechanically from `degerlendir.py` (6 path/label lines).
  - `dnssec/yanyana_v1_v2.py`: side-by-side table.
  - The digests of these three files and of the model were recorded before the run: 2026-09-26T11:25:04Z.
- **Result:**
  - Well-formedness: 16/16, 0 warnings.
  - Cells: 15/15 at the expected value; only K1-11 changed (falsified → verified, 28 steps), the verdicts of the other 14 cells are the same as v1. In the completeness cells the number of steps fell from 19 to 18 because the rule set changed; the verdicts are the same.
  - Mutations: 7/7 rows in the expected direction and different from the base cell; 5/5 mutations killed.
  - `executable` 22/22 verified; all on the first rung of the ladder (longest 3.33 s, at most 139.1 MiB).
  - **KAT-1 after the correction: PASSED** (`dnssec/sonuc_v2/KAT_OZET.{json,md}`, `YANYANA.md`).
- **Integrity:**
  - None of the files of the first run was affected by the v2 run: `SHA256SUMS` after the first run 580/580 OK. v2 wrote only to `sonuc_v2/`.
  - ASP and `cekirdek.lp` were not touched.
  - The final `SHA256SUMS` also covers the new files.

## Status
(last update 26.09.2026)
- [x] Preparation (mapping, instances, models, runners), well-formedness, quotes, freeze (`2d23e35b…`)
- [x] First run: ASP (109/109), Tamarin (31/32), mutations (12/12), extras; commit `e4c1090`
- [x] Diagnosis of K1-11 (trace + diagnosis model 6/6)
- [x] Maintainers' decisions: N-KAT-1 (v2 accepted), N-KAT-2 (pilot copy accepted)
- [x] Run after the correction (v2): KAT-1 Tamarin 15/15, mutations 5/5 → KAT-1 PASSED
- [x] SONUC.md (now RESULTS.md; the two runs side by side), ADIM06-RAPOR.md (this file), SHA256SUMS (final)

```yaml
work: "asp"
step: 6
core_sha256_before_after: "a32372a7c646274ce672c9586e25b34f75f4febb2f966596cc97e7afb89e0b38 (same; 45cbd0f; the correction did not touch ASP)"
preparation_identity: "2d23e35b146d63856c9936c963cd6fffd7526b24008e579c5c8f3b951a85024b (2026-09-26T11:07:00Z)"
first_run: {commit: "e4c1090", nsurum: "140/141", asp: "109/109", tamarin: "31/32", asp_tamarin: "31/32", mutations: "12/12", vd: "2/3", KAT-1: "FAILED (K1-11)", KAT-2: "PASSED", KAT-3: "PASSED"}
after_correction: {model: "dnssec/KAT1_DNSSEC_v2.spthy", KAT-1_tamarin: "15/15", KAT-1_asp_tamarin: "15/15", KAT-1_mutations: "5/5", changed_cells: ["K1-11"], KAT-1: "PASSED", nsurum: "141/141", vd: "3/3"}
pilot_kat3b: "well-formed copy is the gate cell (accepted); the original gives the same verdict"
quotes: "21/21"
alternative_test: "not chosen"
open_issues: []
```
