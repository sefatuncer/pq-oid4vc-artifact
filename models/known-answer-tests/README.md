# models/known-answer-tests — known-answer tests (Step 6)

**What it does.** Checks the modelling approach on three ecosystems whose behaviour under
algorithm migration is already published: DNSSEC ("any single valid path" and algorithm
downgrade), hybrid X.509 certificates ("classical acceptance ≠ hybrid authentication") and S/MIME
("every valid path to the CEK" and the authentication duality). Each ecosystem is encoded as
facts for the **unchanged** ASP core of the system model (`models/asp/cekirdek.lp`, SHA-256 pinned
in the run scripts) and as a small Tamarin model in the same style as `models/tamarin/`. The
expected values were derived twice, independently (N-version), before any run.

**Inputs.** `models/asp/cekirdek.lp` (mounted read-only as `/asp`); expected values
`nsurum/kat_nsurum.tsv` (mounted as `/nsurum`; column `ilk_ajan` is the single source of expected
values); corpus texts for the quote audit (`spec-corpus/metin` as `/korpus`, literature texts as
`/literatur`, not included).

**Outputs.** Per ecosystem `sonuc/` (ASP and Tamarin results, `KAT_OZET.json/.md`), the
corrected KAT-1 run in `dnssec/sonuc_v2/`, and the reports below.

## Contents

| Path | Content |
|---|---|
| [`dnssec/`](dnssec/) | KAT-1 DNSSEC (first run, diagnosis, corrected v2 run) |
| [`x509/`](x509/) | KAT-2 hybrid X.509 (sub-tables K2a–K2d) |
| [`smime/`](smime/) | KAT-3 S/MIME (KAT-3a CEK secrecy, KAT-3b authentication duality) |
| [`kor-beklenen/`](kor-beklenen/) | Blind derivation of the expected values (independent session) |
| [`nsurum/`](nsurum/) | N-version comparison of the two derivations; the expected-value table used by all runs |
| `MAPPING.md` | How each ecosystem is mapped onto the single core; reading rules (fixed before the runs); mutations; limits |
| `RESULTS.md` | Results: summary table, the K1-11 disagreement of the first run, its diagnosis and correction, side-by-side KAT-1 tables, KAT-2 and KAT-3 summaries |
| `STEP06-REPORT.md` | Step 6 report: preparation freeze, preparation findings, run order, post-freeze changes, diagnosis, end-of-step review |
| `SHA256SUMS` | Integrity list of this folder |

## How to run

Per ecosystem folder (`dnssec`, `x509`, `smime`):

```
cd models/known-answer-tests/<ecosystem>
python uret.py                          # write ornekler/<run>.lp from hucreler.tsv and mutasyonlar.tsv
./calistir.sh kos.py                    # ASP runs in pq-a02-solver:1.0 → sonuc/asp*.csv
python tamarin_kos.py iyi_bicim         # well-formedness check of every flag set
python tamarin_kos.py kos               # Tamarin runs (ladder, 12 GB, 600 s) → sonuc/tamarin*.csv
./calistir.sh alinti_dogrula.py         # verbatim quote audit → sonuc/alinti_denetimi.tsv
python degerlendir.py                   # pass criterion → sonuc/KAT_OZET.json, KAT_OZET.md
```

Corrected KAT-1 run: `dnssec/tamarin_kos_v2.py` → `dnssec/degerlendir_v2.py` →
`dnssec/yanyana_v1_v2.py`.

## Results (from `RESULTS.md` and `*/sonuc*/KAT_OZET.json`)

| KAT | Run | ASP cells | Tamarin cells | ASP–Tamarin | Mutations | Verdict |
|---|---|---|---|---|---|---|
| KAT-1 DNSSEC | first run (v1) | 15/15 | 14/15 | 14/15 | 5/5 | failed |
| KAT-1 DNSSEC | corrected run (v2) | 15/15 (first run) | 15/15 | 15/15 | 5/5 | passed |
| KAT-2 hybrid X.509 | first run | 40/40 | 8/8 | 8/8 | 4/4 | passed |
| KAT-3 S/MIME | first run | 54/54 | 9/9 | 9/9 | 3/3 | passed |

Acceptance criterion V-d: 2/3 in the first run, 3/3 after the correction. The only disagreement
of the first run (cell K1-11, Tamarin lemma `a_rrset_authentic`) came from the test model: the
completeness rule of RFC 6840 §5.11 was missing at the DNSKEY step. The ASP core gave the expected
value in all 109 ASP cells in the first run and was not changed. Both runs are reported; the
correction is labelled "after results were seen".

## Turkish names in this folder

`uret` generate · `kos` run · `calistir` run in container · `tamarin_kos` Tamarin runner ·
`tamarin_ic` in-container Tamarin call · `degerlendir` evaluate · `alinti_dogrula` verify quotes ·
`alintilar` quotes · `hucreler` cells · `mutasyonlar` mutations · `ek_tamarin` extra Tamarin rows
(not gate cells) · `ornekler` generated instances · `iyi_bicim` well-formedness · `sonuc` results ·
`sonuc_v2` results of the corrected run · `tamarin_ham` raw Tamarin output · `tani` diagnosis ·
`yanyana` side by side · `HAZIRLIK_SHA256SUMS` preparation hash list · `kor-beklenen` blind
expected values · `nsurum` N-version · `KAT_OZET` KAT summary. Columns and values:
`docs/DATA-DICTIONARY.md` §7.4.
