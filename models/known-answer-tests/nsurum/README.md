# models/known-answer-tests/nsurum — N-version comparison of the expected values

**What it does.** Compares the expected values of the first derivation (the (d) tables of
KAT-SPEC) with the blind derivation (`../kor-beklenen/BEKLENEN-KOR.tsv`), cell by cell. The
comparison and the resolution of the open cells were done before any ASP or Tamarin run of Step 6.
The resulting table is the single source of expected values for all KAT runs (mounted read-only as
`/nsurum`; column `ilk_ajan`).

| File | Content |
|---|---|
| `kat_nsurum.py` | The comparison (`python kat_nsurum.py <KAT-SPEC.md> ../kor-beklenen/BEKLENEN-KOR.tsv`) |
| `kat_nsurum.tsv` | Result: `hucre`, `sutun`, value of the first derivation (`ilk_ajan`), value of the blind derivation (`kor_ajan`), `durum` (`ESIT` equal, `FARKLI` different, `KOR-BELIRSIZ` blind undetermined) |
| `N-VERSION-COMPARISON.md` | Result, resolution of the undetermined K2d cells from the primary source, alternative readings recorded in advance (risk note) |
| `SHA256SUMS` | Integrity list of this folder |

**Results** (`kat_nsurum.tsv`): 141 keys compared; **138 equal**, 0 different, 3 undetermined in the
blind derivation (K2d-01/02/03, Tamarin column), 0 present on one side only.

The column names `ilk_ajan` and `kor_ajan` are historical field names ("first" and "blind"
derivation); they are read by the KAT runners and were kept.
