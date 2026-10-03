# SD-JWT-format validity gate, re-run after decision D9 (2026-10-03)

Re-run of the gate in `../prefreeze-sdjwt/` with the adapter images rebuilt after the corrections of decision D9
(`../../DECISIONS-PREFREEZE.md`), from `experiment/runs`:

```
EXTRA_MOUNT="<absolute path>/experiment/runs/vpm-sdjwt/vectors:/v/vpm-sdjwt:ro" \
  bash adapters/_tools/run.sh vpm-sdjwt/jobs_prefreeze_V_sdjwt.jsonl oncesi outputs/prefreeze-sdjwt-rerun-d9 \
  SDJWT-001 SDJWT-002 SDJWT-004 SDJWT-010 SDJWT-015 SDJWT-018 SDJWT-021 SDJWT-025
```

Result: 8 targets, 128 (vector, policy, arm) cells; `sonuc_ham` and `hata_sinifi` are identical to
`../prefreeze-sdjwt/` in every cell.
