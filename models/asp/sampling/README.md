# models/asp/sampling — sampling frame export (Step 3 → technical gate → Tamarin)

**What it does.** Exports the complete sampling frame of the technical gate from the ASP model.
The ASP step does **not** select samples (PR §2F item 2); the selection is made by a separate,
seeded script in `models/sampling/secim/`.

**Inputs.** The ASP model of the parent folder (`../cekirdek.lp`, `../olgular/`) and the query
driver (`../sorgular/`).

**Outputs.**

| File | Content |
|---|---|
| `cerceve.jsonl` | The gate frame: for every SAT cell of the primary configuration, each minimal set (`asgari`, expected Tamarin verdict *verified*) and each set with one element removed (`bir-eksik`, expected *falsified*, i.e. an attack trace) |
| `kesif_2x2.jsonl` | Exploratory 2×2 grid of PR §2D item 11 ({`ca_baglama`: name, key} × {`ayni_ad_klasik_ca`: no, yes}); additionally rows of type `birincil-kume` (verdict of the primary minimal sets in the grid cell). Not counted for the gate |
| `disa_aktarim_ozeti.json` | Row counts, SHA-256 and stratum counts of both files |
| `disa_aktar.py` | The export script; every `asp_tahmini` (ASP prediction) is computed by evaluating the set with `cekirdek.lp`, not assumed |
| `SCHEMA.md` | Row format: cell, set, prediction, witness, sub-graph per artefact, Tamarin template and `-D` flag mapping |

## How to run

```
cd models/asp && ./calistir.sh sampling/disa_aktar.py
```

## Results (from `disa_aktarim_ozeti.json`)

- `cerceve.jsonl`: **2,442 rows** from 189 cells (G1 81 minimal + 546 one-short; G2 117 + 1,071;
  G3 81 + 546); SHA-256 `0a9b10d169a2898b97a6463fc481385a359744a981c392560ad0355f01942d87`.
- `kesif_2x2.jsonl`: **8,442 rows** from 756 cells; SHA-256
  `c1e810c8c5f077790e9feb27ab6ddd8c0031ac3019a2d0c1503a4a2e5a3fb2ec`. In the cell "name binding,
  same-name classical CA present" all 279 primary minimal sets are falsified.
- No inconsistency: every minimal set is predicted *verified* and every one-short set *falsified*.

## Turkish names in this folder

`cerceve` frame · `kesif_2x2` exploratory 2×2 grid · `disa_aktar` export · `disa_aktarim_ozeti`
export summary. Field names: `docs/DATA-DICTIONARY.md` §7.2 and `SCHEMA.md`.
