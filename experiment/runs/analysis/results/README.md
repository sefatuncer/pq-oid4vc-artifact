# C3 analysis as registered (2026-10-03)

Frozen analysis script and statistics package, applied to `../../outputs/measurement/`, from `experiment/runs`:

```
python analysis/analyze_c3.py --runs outputs/measurement --out analysis/results
docker run --rm --memory=4g --network none -v <analysis/results>:/girdi:ro -v <analysis/results/statistics/<input>>:/cikti     pq-a09-analiz:1.0 python -m c3istat analiz --girdi /girdi/<input>.json --cikti /cikti
```

- Inputs checked against `docs/preregistration/FREEZE-SHA256SUMS`: `analyze_c3.py`, `evidence-rule.csv`,
  `CONTROL-LABELS.csv`, `TK-ASSIGNMENT.csv`, `decisions_v14.tsv`. The statistics image (`pq-a09-analiz:1.0`,
  id `85d48a772ccc`) records the SHA-256 of its 10 scripts in `sonuc.json`; all equal `experiment/statistics/SHA256SUMS`.
  Versions: c3istat 1.0.0, Python 3.11.16, numpy 2.4.6, scipy 1.17.1, statsmodels 0.15.0.
- Files: `decisions.csv` (decision per cell, r1–r3, stable decision, oracle, match), `targets.csv` (per-target
  variables with the reason for every null value), `c3-input-*.json` (statistics inputs), `statistics/<input>/`
  (`sonuc.json`, `sonuc.md`, `karsilastirma.json` of the two implementations).

## Confirmatory test T1 (H6), as registered

| Input | n_eff | X (Y_L4 = 1) | Thresholds c / u | One-sided p (upper) | Verdict |
|---|---|---|---|---|---|
| primary | 30 | 19 (0.633) | 10 / 20 | 0.100 | **inconclusive** (c < X < u) |

Sensitivity analyses of the primary input: unstable cells as Y = 1 and as Y = 0 (19/30, inconclusive), SDJWT-021 as
Y = 0 (19/31, inconclusive), delegating targets excluded (19/29, inconclusive), pilot targets excluded (13/23,
inconclusive). Without SDJWT-002 (decision D1): 19/29, inconclusive; with delegating targets also excluded, 19/28,
falsification region. Descriptive: Y_L4 = 1 in 17 of 24 L4c targets and in 2 of 6 L4m targets (COSE-014, JOSE-009).

## Post-hoc descriptive intervals by stratum (2026-10-28)

The frozen analysis reports Wilson intervals for the two L4 forms but not for the strata. After the review
of the paper, `analysis/subgroup_wilson.py` computed them for the registered analysis and for deviation 1,
with the Wilson function of the frozen statistics package (`c3istat.kesin.wilson`). The output is
`subgroup-wilson.json`. These intervals are descriptive and were not pre-registered. The rows for the
L4 forms and for all 30 targets reproduce the intervals of the frozen outputs.

```
cd experiment/runs
python -I analysis/subgroup_wilson.py
```

| Group | Registered | Deviation 1 |
|---|---|---|
| all | 19/30, 45.5 % to 78.1 % | 21/30, 52.1 % to 83.3 % |
| L4c | 17/24, 50.8 % to 85.1 % | 19/24, 59.5 % to 90.8 % |
| L4m | 2/6, 9.7 % to 70.0 % | 2/6, 9.7 % to 70.0 % |
| JOSE | 15/18, 60.8 % to 94.2 % | 17/18, 74.2 % to 99.0 % |
| SD-JWT | 3/7, 15.8 % to 75.0 % | 3/7, 15.8 % to 75.0 % |
| COSE | 1/5, 3.6 % to 62.4 % | 1/5, 3.6 % to 62.4 % |
