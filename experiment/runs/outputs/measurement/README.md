# C3 measurement run (2026-10-03, after the freeze)

Run of `experiment/runs/run_measurement.sh` after the freeze of pre-registration v1.0 (tag `prereg-v1.0`). The
script checked `docs/preregistration/FREEZE-SHA256SUMS` with `sha256sum -c` before the first run.

- **Run:** 2026-10-03T10:21:13Z to 10:31:59Z (`run-log.txt`, `console.log`). 31 targets × 3 runs (r1, r2, r3), each
  run in a fresh container, job list `jobs-v1.4.jsonl` (2,202 rows), battery v1.4.
- **Images:** all 31 adapter images were rebuilt from the frozen tree with `adapters/_tools/build_all.sh` just before
  the run. A run of the validity-gate jobs on the rebuilt images gave the same `sonuc_ham` and `hata_sinifi` as
  `../prefreeze-v1.4/` in all 1,240 cells.
- **Integrity of the outputs:** 93 files, 204,786 rows, every run complete (2,202 rows); no timeout, no crash, no run
  stopped. Run labels and target ids match the file names in every row. Each target has one `adaptor_sha256` in all
  its rows; for the Node.js, Python and JVM adapters it equals the SHA-256 of the frozen adapter source. All 68,262
  (target, vector, policy, arm) cells have the same raw outcome in r1, r2 and r3.
- Raw outcomes over all rows: `uygulanamaz` 140,673, `red` 42,834, `kabul` 10,359, `ifade-edilemedi` 10,326,
  `istisna` 594.
