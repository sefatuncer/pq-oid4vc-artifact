# traceability — traceability matrix (Step 1)

**What it does.** Maps normative sentences of the specification corpus to the artefact they
govern, the signer role, the algorithm condition, the channel class and the security goal. Each row
carries a verbatim quote (at most 300 characters) that is checked against the extracted corpus text.
The threat model, the ASP facts and the oracles cite the rows by their id (`T001`–`T400`).

**Inputs.** `spec-corpus/metin/<document id>.txt` (extracted texts; see `spec-corpus/`) and
`spec-corpus/korpus_kaynaklari.json` (document groups).

**Outputs.** `izlenebilirlik.csv` (the matrix), `alinti_dogrulama.txt` (quote verification),
`kapsama_tablolari.md` (coverage tables, generated).

## Files

| File | Content |
|---|---|
| `matris_olustur.py` | The matrix rows, written by hand from the primary texts. The script only assigns the ids, checks the quote length and writes `izlenebilirlik.csv` (UTF-8) |
| `izlenebilirlik.csv` | The matrix: `id, belge_id, bolum, birebir_alinti, anahtar_sozcuk, artefakt, imzalayan_rol, algoritma_kosulu, kanal, hedef, kategori, not` (field meanings in `docs/DATA-DICTIONARY.md` §9) |
| `alinti_dogrula.py` → `alinti_dogrulama.txt` | Checks that every quote occurs verbatim in `spec-corpus/metin/<belge_id>.txt`. Normalisation is whitespace only: D1 collapses whitespace; D2 additionally joins words hyphenated at a line break |
| `ozet_tablolari.py` → `kapsama_tablolari.md` | Coverage tables T1–T4 (artefact × document group, artefact × channel, categories, documents per artefact). Generated; Turkish headings; do not edit by hand |
| `SUMMARY.md` | Summary and findings of Step 1 (written when the matrix had 395 rows): no normative channel carries a per-entity algorithm *expectation*; channel classification of the artefacts; validity windows; multi-signature semantics; undetermined clauses |

## How to run

```
python traceability/matris_olustur.py     # rewrite izlenebilirlik.csv
python traceability/alinti_dogrula.py     # needs spec-corpus/metin/; writes alinti_dogrulama.txt
python traceability/ozet_tablolari.py     # writes kapsama_tablolari.md
```

## Results (from the files in this folder)

- `alinti_dogrulama.txt`: **400/400** quotes found verbatim (396 with D1, 4 with D2); 0 quotes
  over 300 characters; no missing text file.
- `izlenebilirlik.csv`: 400 rows from 39 documents. Rows per artefact: A01 7, A02 29, A03 17,
  A04 16, A05 21, A06 11, A07 31, A08 36, A09 42, A10 31, A11 29, A12 37, A13 14, general 79.
  Channel classes: conveyed (`aktarilan`) 186, fetched (`cekilen`) 113, pinned (`sabitlenmis`) 10,
  undetermined (`belirsiz`) 91.

## Turkish names in this folder

`izlenebilirlik` traceability · `matris_olustur` build matrix · `alinti_dogrula`/`alinti_dogrulama`
verify quotes / quote verification · `ozet_tablolari` summary tables · `kapsama_tablolari` coverage
tables. Column names and values: `docs/DATA-DICTIONARY.md` §9.
