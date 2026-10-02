# models/known-answer-tests/kor-beklenen — blind derivation of the expected values

**What it does.** An independent derivation session (the "blind" session, independent derivation
session B of the N-version scheme, PR §4.19) derived the expected value of every KAT cell only from
the cell definitions in `GIRDI/KAT-BLIND-INPUT.md` and from the primary sources (RFCs and published
papers). It did not see the models, the draft code or the first derivation's table, and it ran no
tool. Its values are compared with the first derivation in `../nsurum/`.

**Inputs.** `GIRDI/` (the redacted cell definitions, prepared by the maintainers; see
[`GIRDI/README.md`](GIRDI/README.md)) and the primary sources (line numbers are recorded per value).

**Outputs.**

| File | Content |
|---|---|
| `BEKLENEN-KOR.tsv` | Blind expected values: `kat`, `hucre` (cell), `turetilen_sutun` (derived column), `deger` (value), `kaynak` (source), `alinti` (quote), `satir` (lines) — 141 rows |
| `DERIVATION.md` | The derivation: common interpretation decisions (time constants, value mapping, attacker), cell-by-cell derivation for KAT-1, KAT-2 (2a–2d) and KAT-3 (3a, `cek_secrecy`, 3b), summary counts, interruption and audit note |
| `UNDETERMINED.md` | The three cells left undetermined (K2d-01/02/03, Tamarin column) and the values that depend on an interpretation, each with the alternative reading |
| `ACCESS-LOG.md` | Which files were opened and which were not (independence statement) |
| `SHA256SUMS` | Integrity list of this folder |

**Results** (`DERIVATION.md` §4): 141 data rows — KAT-1 15 cells / 30 rows, KAT-2 40 cells / 48 rows,
KAT-3 21 cells / 63 rows; 3 rows undetermined (K2d-01/02/03 Tamarin).

## Turkish names in this folder

`kor-beklenen` blind expected values · `BEKLENEN-KOR` blind expected · `GIRDI` input ·
`hucre` cell · `deger` value · `kaynak` source · `alinti` quote · `satir` line(s).
