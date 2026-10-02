# models/tamarin — Tamarin rule schemata R1–R7 (Steps 4 and 5A)

**What it does.** Layer 2 of the proven abstraction. Each rule schema isolates one way in which a
classical link lets a quantum attacker (CRQC with time τ per key) forge an accepted object:

| Schema | Model | Question |
|---|---|---|
| R1 chain | `modeller/R1_chain.spthy` | Trust anchor → CA → leaf: which keys must be post-quantum? |
| R2 downgrade | `modeller/R2_downgrade.spthy` | Coexistence of classical and post-quantum keys; does an expectation stop the downgrade? |
| R3 channel | `modeller/R3_channel.spthy` | Fetched artefacts carried over a classical or post-quantum transport |
| R4 WSCD | `modeller/R4_wscd.spthy` | Device key and key-binding JWT |
| R5 anchor | `modeller/R5_anchor.spthy` | Out-of-band pinned anchors (OJEU) |
| R6 time window | `modeller/R6_time.spthy`, `modeller/R6_h5.spthy` | Short-lived keys: does τ exceed the key window? (H2, H5) |
| R7 monotone expectation | `modeller/R7_monotone.spthy`, `modeller/R7_mh.spthy`, `modeller/R7_mh_x.spthy` | Per-entity expectation with sunset (M-f), commitment-chain mechanisms (M-h), alternative CA with the same name (exploratory) |

Every model has *protected* variants (all relevant keys post-quantum, expectation present) and
*mutants* (one protection removed); expected verdicts were written to `betik/varyantlar.tsv`
before the runs. Sanity lemmas (`executable…`) check that the honest protocol run exists.

**Inputs.** The threat model and the rule definitions of the pre-registration; the image
`pq-a02-tamarin:1.12.0` (and `pq-a02-solver:1.0` for the evaluation, `pq-a02-proverif:2.05` for
the second opinion).

**Outputs.** `sonuc/` (results). `models/asp/regresyon/` compares the R1–R5 verdicts with the ASP
core; `models/sampling/` and `models/mechanisms/` reuse the models as templates.

## Files

| Path | Content |
|---|---|
| `modeller/*.spthy` | Tamarin models R1–R7; variants are selected with `-D` flags |
| `modeller/datalog/*.lp` | Datalog (clingo) counterpart of R1–R5 (`core.lp` + one file per rule) |
| `modeller/proverif/*.pvt` | ProVerif templates of R1–R5 (preprocessed with `betik/pp.awk`) |
| `betik/calistir.sh` | Runs every variant and lemma (one container per lemma; non-termination ladder rungs 1 → 3 → 5 → 6 applied automatically) |
| `betik/ic_kosum.sh`, `betik/ic_kosum_pv.sh` | In-container run helpers (Tamarin, ProVerif) |
| `betik/degerlendir.py` | Evaluation: expected vs. observed, Datalog agreement, traces, variant summary, metrics |
| `betik/varyantlar.tsv` | Variant table (rule, variant, role, file, flags, expected goal verdict), written before the runs |
| `betik/proverif_calistir.sh`, `betik/proverif_degerlendir.py`, `betik/proverif_varyantlar.tsv` | ProVerif second opinion and its comparison with Tamarin |
| `betik/on_kayit_h3_sadelestirme.tsv` | Pre-registered expectations of the simplified M-f core (`S_online_core`, H3 simplification) |
| `sonuc/ozet.csv` | One row per lemma run: verdict, steps, time, memory, ladder rung |
| `sonuc/degerlendirme.csv`, `sonuc/varyant_ozeti.csv`, `sonuc/datalog_uyum.csv`, `sonuc/izler.csv` | Evaluation per lemma, per variant, Datalog agreement, attack traces |
| `sonuc/metrikler.txt`, `sonuc/uyarilar.txt` | Metrics (generated, Turkish) and well-formedness warnings (empty) |
| `sonuc/ham/`, `sonuc/json/` | Raw Tamarin output (`.txt`, `.meta`) and traces (`--output-json`) |
| `sonuc/proverif/` | ProVerif: `uretilen/` generated models, `ham/` raw output, `ozet.csv`, `karsilastirma.csv`, `metrikler.txt` |
| `sonuc/h3_sadelestirme/` | Result of the `S_online_core` run (11 lemmas) |
| `sonuc/sha256.txt`, `sonuc/sha256_adim5a.txt`, `sonuc/on_kayit_adim5a_*.sha256.txt` | Hashes of the models and variant tables used for the runs (see `docs/INTEGRITY.md`) |
| `sonuc/calistir_log.txt`, `sonuc/calistir_stdout*.txt` | Run logs |
| `REPORT.md` | Step 4 report (R1–R5) and Step 5A additions |
| `DECISION-NOTES.md` | Notes and decisions of Steps 4 and 5A |

## How to run

```
bash models/tamarin/betik/calistir.sh            # all variants (rewrites sonuc/ozet.csv)
bash models/tamarin/betik/calistir.sh R3         # one rule only
MSYS_NO_PATHCONV=1 docker run --rm -v "$(cygpath -m "$PWD/models/tamarin"):/work" -w /work pq-a02-solver:1.0 python betik/degerlendir.py
bash models/tamarin/betik/proverif_calistir.sh   # ProVerif second opinion
```

Only one Tamarin container runs at a time; every call uses `--rm --memory=12g --memory-swap=12g`
and a 600 s timeout per ladder rung.

## Results (from `sonuc/metrikler.txt`, `sonuc/ozet.csv`, `sonuc/proverif/metrikler.txt`)

- **Step 4 (R1–R5):** 34 variants, 196 lemma runs, expected = observed **196/196**; all five rules
  pass the acceptance criterion; mutation score **11/11**; Datalog prediction = Tamarin verdict on
  44/44 security lemmas.
- **Step 5A (R6, R6h5, R7, R7h; R7hx exploratory):** 41 variants, 349 lemma runs, expected = observed
  **347/349**. The two deviations are the finding of R7h: in `P_ca_pq_alt_namebind` a classical
  second CA with the same name still allows forgery (G1 and G5 falsified although verified was
  expected). Mutation score **16/16**.
- All 545 runs closed on rung 1 of the ladder; no well-formedness warning (390 raw files checked).
- **ProVerif second opinion:** 15 models, 20 security queries, all decided, **20/20** agree with
  Tamarin; sanity queries 15/15.
- **H3 simplification** (`S_online_core`): 11/11 lemmas as pre-registered.

## Turkish names in this folder

`betik` scripts · `modeller` models · `sonuc` results · `ham` raw · `calistir` run · `ic_kosum`
in-container run · `degerlendir`/`degerlendirme` evaluate/evaluation · `varyantlar` variants ·
`ozet` summary · `izler` traces · `metrikler` metrics · `uyarilar` warnings · `datalog_uyum`
Datalog agreement · `uretilen` generated · `karsilastirma` comparison · `h3_sadelestirme` H3
simplification · `on_kayit` pre-registration · `adim5a` Step 5A. Role values in the tables:
`korumali` protected, `mutant:<protection removed>`, `ek` extra, `ek-sinir` abstraction boundary.
