# experiment/inventory — C3 sampling frame and target selection (Step 9a)

**What it does.** Builds, reproducibly, the sampling frame of the C3 library study and selects the
target libraries with pre-registered inclusion criteria and stratum quotas. It collects only the
frame and metadata (stars, last commit, last release, licence, downloads, dependants, documented
algorithm support); library *behaviour* is not measured here.

**Inputs.** jwt.io library data, GitHub topic searches, package-registry searches, organisation
lists and libraries named in the plan; public metadata APIs (deps.dev, ecosyste.ms, package
registries, `git ls-remote` and shallow clones). All requests are anonymous with a generic
User-Agent; GitHub's API is used only as a last resort, with waiting and caching.

**Outputs.** The frame `CERCEVE.csv` and the selection `SECIM.csv`; used by
`experiment/environments/` (build pre-test of the selected targets), `experiment/statistics/`
(strata, pilot flag) and `experiment/runs/`.

## Files

| File | Content |
|---|---|
| `topla.py` | The collector: identification → screening → metadata → criteria → output |
| `CERCEVE.csv` | Sampling frame (198 candidates incl. 23 reference verifiers) with metadata and popularity score |
| `TARAMA.csv` | Every search hit with its screening decision |
| `tarama_kararlari.csv` | Manual screening decisions used by `topla.py` |
| `SECIM.csv` | Eligibility, decision and reason per target under the threshold options E1–E5 |
| `ESIK-DUYARLILIK.csv` | Threshold sensitivity: eligible and selected counts per stratum under E1–E5 |
| `destek_kanitlari.csv` | Manually verified support evidence (repository, field, value, basis) |
| `elle_bayraklar.csv` | Manual flags for criteria K1, K3, K4, K6, K8 and notes |
| `jwtio_esleme.csv` | Mapping of jwt.io entries to canonical repositories and packages |
| `topla_kayit.json` | Collection log (sources, counts, timestamps) |
| `CRITERIA-DRAFT.md` | Inclusion criteria (draft that entered the pre-registration): unit, population and strata, frame sources, screening, criteria K1–K8, threshold options, quotas and selection rule, replacement rule, exclusion codes |
| `SUMMARY.md` | Summary: stratum counts, proposed final list (E2, n = 31) and reserves, post-quantum support landscape and its effect on the control–treatment design, multi-signature and policy inventory, inter-library dependencies, risks |
| `DECISION-NOTES.md` | Notes and decisions of the inventory work |

## How to run

```
python experiment/inventory/topla.py                  # use the cache; fetch only what is missing
python experiment/inventory/topla.py --cevrimdisi     # cache only, no network
python experiment/inventory/topla.py --tazele         # ignore the cache (the snapshot changes!)
python experiment/inventory/topla.py --desen-tara     # optional evidence scan in shallow clones
```

The frame date is fixed (`REF_TARIH` = 2026-09-23); "last 24 months" is computed from it. The
cache folder (`onbellek/`) is not part of the repository.

## Results (from `SUMMARY.md`, `SECIM.csv`)

| Stage | JOSE | SDJWT | COSE | n (libraries) | REF (outside n) |
|---|---|---|---|---|---|
| Frame candidates (198) | 109 | 29 | 37 | 175 | 23 |
| Meet the criteria (E2) | 41 | 15 | 17 | 73 | 14 |
| Selected (quota) | 18 | 8 | 5 | **31** | 3 |
| Reserve | 9 | 6 | 4 | 19 | 2 |

`SECIM.csv` under E2: 34 selected (31 libraries + 3 reference verifiers), 21 reserves, 111 excluded,
32 eligible but outside the quota.

## Turkish names in this folder

`topla` collect · `CERCEVE` frame · `TARAMA` screening · `tarama_kararlari` screening decisions ·
`SECIM` selection · `ESIK-DUYARLILIK` threshold sensitivity · `destek_kanitlari` support evidence ·
`elle_bayraklar` manual flags · `jwtio_esleme` jwt.io mapping · `topla_kayit` collection log ·
`onbellek` cache · `cevrimdisi` offline · `tazele` refresh · `desen-tara` pattern scan.
Columns and values: `docs/DATA-DICTIONARY.md` §8.
