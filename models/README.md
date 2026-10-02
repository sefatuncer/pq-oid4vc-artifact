# models — formal part of the study (contributions C1 and C2)

The formal part is a *proven abstraction*: a fast, exhaustive ASP model computes minimal
post-quantum sets for every query; symbolic Tamarin models check the rules on which the ASP
semantics rests; sampled ASP cells are re-checked in Tamarin; known-answer tests on other
ecosystems check that the same core reproduces published results.

| Folder | Step | Role | Main inputs | Main outputs |
|---|---|---|---|---|
| [`asp/`](asp/) | 3 | ASP system model, independent z3 encoding, query catalogue | `threat-model/`, `traceability/`, `data/` | minimal sets per query (`sorgular/sonuc/`), ASP–z3 agreement (`z3/sonuc/`), sampling frame (`sampling/`) |
| [`tamarin/`](tamarin/) | 4, 5A | Tamarin rule schemata R1–R7, Datalog counterparts, ProVerif second opinion | threat model, rule definitions of the pre-registration | verdicts per variant and lemma (`sonuc/`) |
| [`sampling/`](sampling/) | 5B | Technical gate: ASP frame rows translated into Tamarin instances and run | `asp/sampling/cerceve.jsonl`, `tamarin/modeller/` | `teknik-kapi/sonuc.csv` |
| [`known-answer-tests/`](known-answer-tests/) | 6 | DNSSEC, hybrid X.509 and S/MIME known-answer tests | `asp/cekirdek.lp` (hash-pinned), published results, blind expected values | `*/sonuc/`, `RESULTS.md` |
| [`mechanisms/`](mechanisms/) | 7 | Expectation-conveyance mechanisms M-a … M-h, proposed M-f | pre-registered expectations (`on_kayit_varyantlar.tsv`) | `sonuc/karsilastirma.csv`, `STEP07-REPORT.md` |
| [`comparison/`](comparison/) | 8 | Strategies S0–S8 × metrics M1–M5, ablations, figures | ASP queries, mechanism results | tables and figures |

All tools run in the images of [`tools/`](../tools/): `pq-a02-solver:1.0` (clingo, z3),
`pq-a02-tamarin:1.12.0` (Tamarin, Maude) and `pq-a02-proverif:2.05`. Every Tamarin run uses
`--memory=12g --memory-swap=12g`, a wall-clock timeout and the non-termination ladder (rung 1
`--prove=<lemma>`; then `[use_induction]`/`[reuse]`, `--auto-sources`, a tactic or oracle,
`--bound=40`; a lemma that still does not close is labelled "not closed"). A run with a Tamarin
well-formedness warning is invalid.

## Turkish names used in all model folders

`betik/` scripts · `modeller/` models · `sonuc/` results · `ham/` raw output · `json/` Tamarin JSON
output · `ornekler/` generated instances · `calistir.sh` run · `ic_kosum.sh` in-container run ·
`degerlendir.py` evaluate · `varyantlar.tsv` variants · `ozet.csv` summary · `izler.csv` attack
traces · `on_kayit*` pre-registration (fixed before the run) · `KARAR-NOTLARI` → `DECISION-NOTES.md`.
More in [`docs/GLOSSARY.md`](../docs/GLOSSARY.md).
