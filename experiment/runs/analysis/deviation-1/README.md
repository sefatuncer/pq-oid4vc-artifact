# Deviation 1: incidental-rejection rule applied as its rule text states (analysis after the measurement)

Record: `docs/preregistration/DEVIATIONS.md`, deviation 1. The registered analysis is `../results/` and stays the
primary analysis (decision of the corresponding author, 2026-10-03).

**What differs.** Pre-registration Section 5.13 (Amendment 11) codes a control-arm rejection as *not supported* when
its error class shows that **the control-label algorithm itself** is not supported on that API path. The frozen script
`../analyze_c3.py` (and the implementation bullet of Section 5.13) applies the coding to every control-arm rejection
with `hata_sinifi = alg-desteklenmiyor`, whatever the algorithm of the rejected object. `analyze_c3_deviation1.py` is
the frozen script with one change: the coding applies only if every signature of the vector uses the control-label
algorithm (`diff ../analyze_c3.py analyze_c3_deviation1.py`).

**Why it matters.** JOSE-034 (jose2go) and JOSE-055 (jjwt) implement their allowlist as a restricted algorithm
registry. Under `L4` (allowlist {X} for the migrated issuer) they reject `VPLUS_ES256` with "Unknown algorithm: 'ES256'"
and "Unsupported signature algorithm 'ES256'", which the adapters class as `alg-desteklenmiyor`. Both libraries accept
the same object under `GEC` and `IZIN-A` and pass the ES256 validity gate, so the rejection is the configured policy.
The frozen script codes it as not supported, which sets Y_L4 = 0 for both targets.

```
python analysis/deviation-1/analyze_c3_deviation1.py --runs outputs/measurement --out analysis/deviation-1/results
# statistics as for ../results (pq-a09-analiz:1.0, c3istat analiz), outputs in results/statistics/<input>/
```

**Effect.** Per-target variables change only for JOSE-034 and JOSE-055 (Y_L4 0 → 1, L level 0 → 4); 1,176 decision
cells change from `desteklenmiyor` to `reject`, all other variables are equal.

| | Registered (`../results/`) | Deviation 1 (`results/`) |
|---|---|---|
| T1 primary: X / n_eff | 19 / 30 (0.633) | 21 / 30 (0.700) |
| One-sided p (upper) | 0.100 | 0.021 |
| H6 verdict (thresholds 10 / 20) | inconclusive | falsification: the majority can express the policy |
| Without SDJWT-002 (D1) | 19 / 29, inconclusive | 21 / 29, falsification |
| Pilot targets excluded | 13 / 23, inconclusive | 14 / 23, inconclusive |
| Y_L4 = 1 by form | L4c 17 / 24, L4m 2 / 6 | L4c 19 / 24, L4m 2 / 6 |

Under neither analysis is H6 supported. Following the interpretation note of Section 5.13, the high share comes from
L4c targets, which in effect measure a per-issuer allowlist; the required-set semantics over several signatures (L4m)
is expressible in 2 of 6 targets.
