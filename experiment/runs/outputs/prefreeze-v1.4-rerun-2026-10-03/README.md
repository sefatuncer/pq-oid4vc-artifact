# Pre-freeze validity gate v1.4, re-run of 2026-10-03

Re-run of the gate in `../prefreeze-v1.4/` after the folders and files under `experiment/` were renamed
to English (`docs/PATHS.tsv`). The adapter images were rebuilt with `adapters/_tools/build_all.sh`
(adapter sources unchanged by the rename) and the gate was run from `experiment/runs`:

```
bash adapters/_tools/run.sh jobs-prefreeze-v1.4.jsonl oncesi outputs/prefreeze-v1.4-rerun-2026-10-03 <the 31 targets of CONTROL-LABELS.csv>
python adapters/_tools/gate_summary.py outputs/prefreeze-v1.4-rerun-2026-10-03
```

Result: 31 targets, 1,240 (vector, policy, arm) cells; `sonuc_ham` and `hata_sinifi` are identical to
`../prefreeze-v1.4/` in every cell, and `GATE-SUMMARY.csv` is byte-identical. `adaptor_sha256` differs
from the recorded rows because the comments of the adapter sources were translated after the recorded
run (2026-10-02); the source files are the same as on the base revision of the rename.
