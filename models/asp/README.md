# models/asp — ASP system model and z3 cross-encoding (Step 3)

**What it does.** Encodes the threat model as an answer set program (clingo) and computes, for
every query (goal × coexistence phase × τ × anchor × policy, plus the hypothesis designs), the
subset-minimal sets of artefacts that must be post-quantum, together with the expectation carriers
they need. An independently written z3 encoding re-computes every query, and a third,
plain-Python fixed-point evaluator (Jacobi) checks random configurations. The model is layer 1 of
the proven abstraction; Tamarin (`models/tamarin/`) is layer 2.

**Inputs.** Definitions of the threat model (`threat-model/`) and the traceability matrix
(`traceability/`, mounted read-only as `/izlenebilirlik`); the LOTL snapshot statistics (`data/`,
mounted as `/veri`); Tamarin verdicts for the regression (`models/tamarin/sonuc/datalog_uyum.csv`,
mounted as `/tamarin`); the design-stage pilot P2 (mounted from `referans/` as `/referans`; the same
files are in `tools/regression-tests/p2/`).

**Outputs.** Minimal sets per query group (`sorgular/sonuc/`), ASP–z3 agreement (`z3/sonuc/`),
regression results (`regresyon/sonuc/`), the sampling frame for the technical gate (`sampling/`)
and the report numbers (`sorgular/sonuc/rapor_sayilari.json`). The core `cekirdek.lp` is also used,
unchanged and hash-pinned, by the known-answer tests.

## Files

| Path | Content |
|---|---|
| `olgular/*.lp` | Facts: `artefaktlar` (artefacts), `kenarlar` (edges: any-valid-path), `tasiyicilar` (expectation carriers and mechanism hooks), `pencereler` (time windows, key modes, τ), `hedefler` (goals G1–G5), `parametreler` (primary configuration) |
| `cekirdek.lp` | Core semantics: forgeability under every acceptance path, expectations, time |
| `secim.lp` | Decision atoms (17 decision nodes, carriers) and subset-minimal enumeration (`--heuristic=Domain --enum-mode=domRec`) |
| `sorgu.lp` | Query constraint: the queried goal must not be violated in any break scenario |
| `calistir.sh` | Runs a Python driver in `pq-a02-solver:1.0` (working directory `/work` = this folder) |
| `sorgular/` | `ortak.py` (driver), `katalog.py` (query catalogue), `kos.py` (run groups), `analiz.py` (tables), `stratejiler.py` (strategies S0–S8 × metrics M1–M5, preliminary), `h4.py`, `sira.py` (optimal migration orders), `rapor_sayilari.py` (report numbers), `stratejiler_taslak.json` and `beklenti_2x2.json` (fixed before the runs, with `.sha256`), `sonuc/` |
| `z3/` | `yapi.py` (fact reader), `z3_kodlama.py` (z3 encoding), `py_degerlendirici.py` (Jacobi evaluator), `capraz_kontrol.py` (ASP ↔ z3 on all groups), `uclu_rastgele.py` (three-way random check, seed 20260928), `sonuc/` |
| `regresyon/` | `tamarin_esdegerlik.py` (core vs. the 44 Tamarin R1–R5 verdicts; generated instances in `tamarin_datalog/ornekler/`), `p2_regresyon.py` (pilot P2, 48 queries; `p2_ornegi.lp`), `sonuc/` |
| `sampling/` | Export of the sampling frame (see [`sampling/README.md`](sampling/README.md)) |
| `REPORT.md` | Step 3 report: model definition, core rules and their rationale, query catalogue, result tables, ASP–z3 agreement, regression, preliminary hypothesis results, limitations |
| `DECISION-NOTES.md` | Interpretation questions N1–N15 and the decisions taken |

Generated: `sorgular/sonuc/analiz/tablolar.md` (Turkish tables written by `analiz.py`).

## How to run

Reproduction order (each command runs in the solver container):

```
cd models/asp
./calistir.sh sorgular/kos.py                 # all query groups → sorgular/sonuc/<group>.json
./calistir.sh z3/capraz_kontrol.py <groups>   # ASP ↔ z3 → z3/sonuc/uyum_*.csv
./calistir.sh z3/uclu_rastgele.py             # ASP, z3, Jacobi on random configurations
./calistir.sh regresyon/tamarin_esdegerlik.py
./calistir.sh regresyon/p2_regresyon.py
./calistir.sh sorgular/analiz.py; ./calistir.sh sorgular/stratejiler.py; ./calistir.sh sorgular/h4.py; ./calistir.sh sorgular/sira.py
./calistir.sh sampling/disa_aktar.py
./calistir.sh sorgular/rapor_sayilari.py
```

## Results (from `sorgular/sonuc/`, `z3/sonuc/`, `regresyon/sonuc/`)

- **52,693 queries solved** in 10 groups, 80,291 minimal sets; ASP wall time 224.8 s in total, longest
  query 2.01 s. Primary configuration D1′ (Q = 675): 189 SAT, 486 UNSAT, 279 minimal sets, wall
  time 1.95 s.
- **ASP–z3: 52,693/52,693 queries and 80,291/80,291 minimal sets identical.** Three-way random check
  (ASP, z3, Jacobi): 7,000/7,000.
- Regression: the core agrees with all 44 Tamarin R1–R5 verdicts (the naive "real parent only"
  reading disagrees only on `R1 X_alt_ca`); pilot P2 48/48.
- Sampling frame: 2,442 rows (`cerceve.jsonl`) and 8,442 exploratory rows (`kesif_2x2.jsonl`).
- Preliminary findings (to be confirmed at the scientific gate): in the primary configuration goal
  G4 and "all goals" cannot be met by any post-quantum set (135/135 G4 cells UNSAT); H1, H2′ and H5
  are supported; H4 has candidates only under the Ö3 interpretation (decision note N8).

## Turkish names in this folder

`olgular` facts · `cekirdek` core · `secim` selection · `sorgu`/`sorgular` query/queries ·
`katalog` catalogue · `kos` run · `ortak` common/driver · `analiz` analysis · `stratejiler`
strategies · `sira` order · `rapor_sayilari` report numbers · `beklenti_2x2` pre-registered
expectations of the 2×2 grid · `taslak` draft · `yapi` structure · `kodlama` encoding ·
`degerlendirici` evaluator · `capraz_kontrol` cross-check · `uclu_rastgele` three-way random ·
`uyum` agreement · `regresyon` regression · `esdegerlik` equivalence · `ornegi` instance ·
`tamarin_datalog/ornekler` generated Datalog instances. Query groups: `birincil` primary, `cab` CA
binding 2×2, `oat` one-at-a-time sensitivity, `tau` τ grid, `a5` window grid, `h` H0/H3/H5 extras.
