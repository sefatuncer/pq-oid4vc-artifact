# experiment/statistics — pre-registered statistics for C3 / H6 (Step 9, task 9)

**What it does.** `c3istat` implements the pre-registered analysis of the library study: test T1
(primary test of H6, exact one-sided binomial with thresholds from PR Appendix A), T2–T5 (exact
McNemar, Fisher, binomial) with Holm correction over {T2…T5}, effect sizes (Wilson intervals,
Newcombe method 10, conditional exact odds ratios), the cluster bootstrap and the sensitivity
analyses, and it states the H6 verdict. Every quantity is computed by two independent
implementations — `kesin.py` (standard library only: `fractions`, `math.comb`, `decimal`) and
`referans.py` (scipy, statsmodels, numpy) — and compared within fixed tolerances. The scripts were
validated on **synthetic data only**; no target library was touched and no real measurement was
used.

**Inputs.** One input file in the schema `c3-istat-girdi/1.0` (JSON, or the equivalent CSV pair;
see `SCHEMA.md`), written by Step 10 from the C3 run results and the merged oracle.

**Outputs.** `sonuc.json` (all results; field meanings in `docs/DATA-DICTIONARY.md` §6),
`sonuc.md` (the same result as a Turkish report), `karsilastirma.json` (two-implementation
comparison).

## Files

| Path | Content |
|---|---|
| `scripts/c3istat/` | The package: `yapilandirma` (constants from the pre-registration: α, seed, B, families, tolerances), `kesin` (implementation A), `referans` (implementation B), `karsilastir` (comparison of A and B), `sema` (input schema loader and validator), `bootstrap` (cluster bootstrap, pure Python and numpy), `analiz` (T1–T5, Holm, effect sizes, Wilson, bootstrap, sensitivities, H6 verdict), `rapor` (Markdown report), `__main__` (command line) |
| `scripts/requirements.txt` | Pinned packages with SHA-256 (numpy 2.4.6, scipy 1.17.1, statsmodels 0.15.0 and their closure) |
| `synthetic-tests/` | Synthetic test suite: `run_tests.py` (runner), `test_ek_a` (PR Appendix A values), `test_iki_uygulama` (two implementations on generated sweeps), `test_sema` (invalid input must not reach the analysis), `test_sinir` (boundary cases), `test_uctan_uca` (end to end, CSV ≡ JSON), `test_yayimlanmis` (published values), `test_bootstrap`; `make_sample_data.py` writes the synthetic example input; `data/` holds the example input and the published values |
| `Dockerfile`, `.dockerignore` | Image `pq-a09-analiz:1.0`: digest-pinned base, `pip --require-hashes`, version gate, runs with `--network none` |
| `run_all.sh` | Builds the image, runs the test suite twice and the example analysis twice in fresh containers, compares the outputs byte by byte, writes `SHA256SUMS` |
| `results/` | Evidence of the validation: `test1/`, `test2/` (two test runs), `sample_input/` (synthetic example input), `sample_analysis1/`, `sample_analysis2/` (two analysis runs), `sample_analysis_csv/` (CSV input), `sample_analysis_sha256.txt` |
| `records/` | Docker image lists before and after, build log, image id, versions |
| `sources/NEWCOMBE-SOURCE.md` | Source of the published example values for Newcombe method 10 and Wilson (the primary papers were not accessible; an open-access secondary source was used) |
| `SCHEMA.md` | Input schema `c3-istat-girdi/1.0`, analysis sets and validator errors |
| `FREEZE-INPUT.md` | Freeze input: files and SHA-256, image, seeds, traceability from pre-registration item to implementation to test, how to run in Step 10, validation evidence |
| `DECISION-NOTES.md` | Interpretation questions N-1 … N-12 that required a decision, and information notes |
| `SHA256SUMS` | Integrity list of the files to be frozen |

## How to run

```
bash experiment/statistics/run_all.sh [--insa-yok]       # everything, in containers
# without Docker (host Python with numpy, scipy, statsmodels):
cd experiment/statistics && python synthetic-tests/run_tests.py --cikti <output folder>
# analysis of a real input (Step 10):
docker run --rm --memory=4g --network none -v <input>:/girdi:ro -v <output>:/cikti pq-a09-analiz:1.0 \
    python -m c3istat analiz --girdi /girdi/<file> --cikti /cikti
python -m c3istat dogrula --girdi <file>        # validate an input only (exit code 3 on error)
```

`synthetic-tests/run_tests.py` exits with 0 when every test passes. Note that `analiz.py` records
the SHA-256 of the analysis scripts in `sonuc.json` (`arac.betik_sha256`); see `docs/INTEGRITY.md`.

## Results (from `results/` and `FREEZE-INPUT.md` §6)

- Synthetic test suite in two fresh containers, identical `test_summary.json`: test methods
  **115/115**, sub-tests **729/729**, two implementations **56,269/56,269 cases** and
  **90,058/90,058 quantities**; largest deviations of the order 1e-16 (conditional OR: relative
  4.6e-11).
- PR Appendix A: all 21 rows n = 20…40 reproduced by both implementations; for n = 31: c = 10,
  u = 21, P(X ≤ 10) = 75973189/2147483648 = 0.035378.
- Published examples Y1–Y7 reproduced by both implementations.
- Example synthetic analysis (n = 31, synthetic): `sonuc.json`, `sonuc.md` and `karsilastirma.json`
  byte-identical in two containers; H6 verdict on the synthetic example: undetermined
  (`belirsiz`; X = 12, n_eff = 28, c < X < u).

**Generated, not translated:** `results/*/sonuc.md` (Turkish report written by `c3istat analiz`;
`BELİRSİZ` = undetermined).

## Names in this folder

The folders and the runner files were renamed to English on 03.10.2026 (`docs/PATHS.tsv`):
`betikler/` → `scripts/`, `sentetik-testler/` → `synthetic-tests/` (`veri/` → `data/`), `sonuclar/` →
`results/`, `kayit/` → `records/`, `kaynak/` → `sources/`, `tumunu_calistir.sh` → `run_all.sh`,
`calistir.py` → `run_tests.py`, `ornek_veri_uret.py` → `make_sample_data.py`, `ornek_*` → `sample_*`,
`test_ozeti.json` → `test_summary.json`, `calistirma_kaydi.json` → `run_record.json`, `konsol.log` →
`console.log`. The package `c3istat` keeps its Turkish module names: `analiz` analysis · `sema`
schema · `kesin` exact · `referans` reference implementation · `karsilastir` compare ·
`yapilandirma` configuration · `rapor` report; also the test modules (`test_ek_a` Appendix A,
`test_iki_uygulama` two implementations, `test_sinir` boundaries, `test_uctan_uca` end to end,
`test_yayimlanmis` published values) and the analysis outputs `sonuc.json`, `sonuc.md` (result) and
`karsilastirma.json` (comparison). Command words and options: `analiz` analysis · `dogrula` validate ·
`surum` version · `--insa-yok` skip the build · `--girdi` input · `--cikti` output (also the container
mount points `/girdi`, `/cikti`).
