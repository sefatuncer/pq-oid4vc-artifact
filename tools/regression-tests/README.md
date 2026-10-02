# tools/regression-tests — acceptance test of the tool images (Step 2)

**What it does.** Re-runs the design-stage feasibility pilots with the pinned tool images and
checks that the verdicts are unchanged. The pilot models and scripts are kept as they were written
during the design stage (they are in English).

**Inputs.** The pilot files in `p1/` (Tamarin), `p1b/` (ProVerif) and `p2/` (ASP + z3); the
images `pq-a02-tamarin:1.12.0`, `pq-a02-solver:1.0` and `pq-a02-proverif:2.05` (see `../README.md`).

**Outputs.** `results/` and the raw prover output next to each model.

## Contents

| Path | Content |
|---|---|
| `run.sh` | Runs P1 (eight Tamarin variants via `p1/run_p1.sh`, with `--memory=12g` and a timeout) and P2 (`p2/run_p2.py`) |
| `p1/weakest_link.spthy`, `p1/delegation_loop.spthy` | Pilot Tamarin models; `out_<variant>.txt` raw output per variant |
| `p1b/wl_*.pv` | Pilot ProVerif models (four variants); `out_wl_*.txt` raw output |
| `p2/trustchain_base.lp`, `p2/trustchain_mig.lp`, `p2/order.lp`, `p2/run_p2.py` | Pilot ASP program: minimal post-quantum migration sets (P2a), migration order (P2b), z3 cross-check (P2c); `p2a_results.json` |
| `results/run_log.txt`, `results/p1_summary.txt` | Run log and summary of P1 |
| `results/p2_stdout.txt` | Output of P2 |
| `results/proverif_build.txt` | Image id of the ProVerif build |

## How to run

```
sh tools/regression-tests/run.sh            # P1 and P2 (Git Bash; uses cygpath)
# P1b: one ProVerif run per model, for example
MSYS_NO_PATHCONV=1 docker run --rm -v "$(cygpath -m "$PWD/tools/regression-tests/p1b"):/work" -w /work pq-a02-proverif:2.05 proverif wl_TLpq_pq_required.pv
```

## Results (from `results/` and the raw outputs)

- P1: V1, V2, V3 and V6 `claims_unforgeability` falsified; V4 and V5 verified; L2 (with induction)
  verified in 20 steps; L1 (without induction) times out after 60 s at 1,975.5 MiB peak memory.
- P1b: `TLpq_pq_required` true; `TLpq_none` false; both `TLclassical` variants "cannot be proved".
- P2: 48 queries solved in 0.028 s; z3 and clingo agree on 48/48.

These are the expected pilot verdicts (see the table in `../README.md`). The pilot models produce
Tamarin well-formedness warnings, so their verdicts serve only as a regression check of the tools
and are not used as results of the study.

## Names in this folder

The folder and files were renamed on 03.10.2026 (`calistir.sh` → `run.sh`, `sonuc/` → `results/`,
`calistir_log.txt` → `run_log.txt`, `p1_ozet.txt` → `p1_summary.txt`; `docs/PATHS.tsv`). The recorded
outputs keep the old names. `p2_stdout` P2 standard output · `proverif_build` ProVerif build record.
