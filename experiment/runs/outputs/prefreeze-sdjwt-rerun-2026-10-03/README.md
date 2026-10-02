# SD-JWT-format validity gate, re-run of 2026-10-03

Re-run of the gate in `../prefreeze-sdjwt/` after the folders and files under `experiment/` were renamed
to English (`docs/PATHS.tsv`), with the rebuilt adapter images, from `experiment/runs`:

```
EXTRA_MOUNT="<absolute path>/experiment/runs/vpm-sdjwt/vectors:/v/vpm-sdjwt:ro" \
  bash adapters/_tools/run.sh vpm-sdjwt/jobs_prefreeze_V_sdjwt.jsonl oncesi outputs/prefreeze-sdjwt-rerun-2026-10-03 \
  SDJWT-001 SDJWT-002 SDJWT-004 SDJWT-010 SDJWT-015 SDJWT-018 SDJWT-021 SDJWT-025
```

The extra mount needs an empty folder `experiment/vector-generator/vectors/vpm-sdjwt/` as mount point,
because `vectors/` is mounted read-only at `/v` (git does not keep empty folders).

Result: 8 targets, 128 (vector, policy, arm) cells; `sonuc_ham` and `hata_sinifi` are identical to
`../prefreeze-sdjwt/` in every cell.
