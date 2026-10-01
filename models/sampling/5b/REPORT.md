# Stratified abstraction sample (Step 5B): report

Purpose: check that the ASP abstraction predicts the Tamarin verdict on a stratified sample of model cells
(pre-registration section 4.18; validity condition (1) of the scientific gate). Every number below is read from the
files named in the last column.

## Design

| Item | Value | Source |
|---|---|---|
| Frame | 2,442 rows in 189 cells (SHA-256 `0a9b10d1…942d87`) | `secim.json` (`cerceve`) |
| Selection | 200 samples, at least one per cell, seed 20260926 | `secim.json`, `secim_5b.py` |
| Sample types | 34 "minimal" (ASP: the minimal set secures the goal, expected verified), 166 "one missing" (one node of the minimal set left classical, expected falsified) | `secim.json` (`tur_dagilimi`) |
| Translation to Tamarin | 187 translated, 13 outside the translator's scope | `ceviri_plani.tsv`, `ceviri_disi.tsv` |
| Runs | one Tamarin container at a time, `--memory=12g --memory-swap=12g`, timeout 600 s, non-termination ladder 1 `--prove`, 3 `--auto-sources`, 5 `--bound=40`, 6 "not closed" | `betik/calistir.sh` |
| Health lemma | `executable` (exists-trace) for every sample | `saglik.csv` |

The ASP prediction is not read by the runner; the comparison is made afterwards by `karsilastir.py`.

## Results

| Measure | Value | Source |
|---|---|---|
| Closed samples | 183 of 187 translated | `sonuc.csv` |
| Agreement on closed samples | **183 of 183** (149 one-missing: falsified as predicted; 34 minimal: verified as predicted) | `sonuc.csv`, `karsilastir.py` output |
| Differences | 0 (`farklar.csv` not written) | `karsilastir.py` |
| Not closed | 4 samples, all one-missing G2 cells (CERCEVE-000671, -000724, -000869, -000938); every ladder step reached the 12 GB limit | `tamarin_ham.csv`, `calistir_log.txt` |
| Not closed or out of scope | 17 of 200 = 8.5 % (13 out of scope + 4 not closed; counted together, conservatively), within the 10 % allowance | — |
| Health lemma closed | 178 of 187 verified; 9 not closed (memory limit at every ladder step) | `saglik.csv` |
| Agreement restricted to samples whose health lemma closed | **177 of 177** | `sonuc.csv`, `saglik.csv` |
| Well-formedness | every translated model passes the well-formedness check (separate listing run per model) | `ham/*__liste.txt` |

Three verified "minimal" samples (CERCEVE-001004, -001064, -001108) have a health lemma that did not close, so the
possibility that their verified verdict is vacuous is not excluded; the restricted agreement figure above leaves them out.

## Scope limits

- **Out of scope (13 samples):** every excluded sample involves the issuer metadata artefact `a05_meta`, either as an
  unsigned variant (9) or as the target of an expectation carrier (4). The translator does not support these, so the
  ASP results for unsigned issuer metadata and for carriers aimed at it are not checked by this sample.
- **Frame:** the frame contains the cells for which the ASP model returns a minimal set; queries without any solution
  are not sampled.
- **Memory:** the four not-closed samples are G2 cells whose state space exceeds 12 GB in every ladder step. ASP
  predicts an attack trace in all four.

## Procedure record

1. The first runs used four parallel workers with 4 GB each; samples that ran out of memory were re-run at the
   pre-registered 12 GB limit, one container at a time (`tamarin_ham_4g_paralel.csv`, `ham_4g_oom/`).
2. **Runner defect, found and corrected on 2026-10-01 after the runs:** a run killed at the memory limit (rc = 137)
   produces no summary, so `calistir.sh` recorded it as a well-formedness failure (`gecersiz_wf`) and did not try
   ladder steps 3 and 5. Well-formedness is checked by the separate listing run of each model, and all affected
   models pass it. The runner now records such runs as `bellek` (or `timeout`) and continues the ladder. Steps 3 and 5
   were then run for the 13 affected lemmas (4 target lemmas, 9 health lemmas); none closed. The defect changed no
   verdict of a closed sample. The same check exists in the runners of the technical gate and of the mechanism
   models, where no run was killed (0 `gecersiz_wf` rows), so their results are unaffected.
3. One run (CERCEVE-001108, G2) shows a wall time of 10,202 s. The laptop was in standby from 19:00:37 to 21:48:32
   (Windows Kernel-Power events 506 and 507), so about 127 s of the run were computation; the verdict stands.

## Verdict for the scientific gate

Criterion "sampling agreement, stratified sample: 100 % of closed samples, every difference explained": **met**
(183/183; 177/177 when samples without a closed health lemma are left out). Coverage: 183 of 200 selected samples
closed (91.5 %).
