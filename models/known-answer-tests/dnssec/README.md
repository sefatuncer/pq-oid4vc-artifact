# models/known-answer-tests/dnssec — KAT-1 DNSSEC

**What it does.** Reproduces the published behaviour of DNSSEC validators during an algorithm
rollover: validators accept "any single valid path" (RFC 6781, RFC 6840), so a zone that still
publishes a classical key or DS record remains forgeable after the classical key is broken, and a
stricter completeness rule changes this. 15 cells, each evaluated by the ASP core
(`models/asp/cekirdek.lp` + `kat1_dnssec.lp`) and by Tamarin (`KAT1_DNSSEC.spthy`, lemma
`a_rrset_authentic`), plus 5 mutations.

**Inputs.** `hucreler.tsv` (cells: ASP constants, Tamarin flags, lemma), `mutasyonlar.tsv`
(mutations), `alintilar.tsv` (quotes from RFC 6781/6840/7583 that justify each cell), expected
values from `../nsurum/kat_nsurum.tsv`. The mapping and reading rule are in `../MAPPING.md` §2.

**Outputs.** `sonuc/` (first run), `sonuc_v2/` (corrected Tamarin run), `tani/sonuc.csv`
(diagnosis), `iyi_bicim/` (well-formedness of every flag set).

| File | Content |
|---|---|
| `kat1_dnssec.lp` | ASP facts and reading rule of KAT-1 (loaded together with the unchanged core) |
| `KAT1_DNSSEC.spthy` | Tamarin model of the first run (kept unchanged) |
| `KAT1_DNSSEC_v2.spthy` | Corrected model: the RFC 6840 §5.11 completeness rule is also applied at the DNSKEY step (correction made after results were seen) |
| `tani/KAT1_DNSSEC_tani.spthy`, `tani/tani_kos.py`, `tani/sonuc.csv` | Diagnosis of cell K1-11 on the six cells that use the completeness test (not a gate value) |
| `uret.py`, `kos.py`, `tamarin_kos.py`, `tamarin_ic.sh`, `alinti_dogrula.py`, `degerlendir.py`, `calistir.sh` | Pipeline (see `../README.md`) |
| `tamarin_kos_v2.py`, `degerlendir_v2.py`, `yanyana_v1_v2.py` | Corrected run: imports the frozen runner unchanged, writes only to `sonuc_v2/`; side-by-side table `sonuc_v2/YANYANA.md` |
| `HAZIRLIK_SHA256SUMS` | Preparation freeze list written before the first run (see `docs/INTEGRITY.md`) |
| `iyi_bicim_kosu.log`, `tamarin_kosu.log` | Run logs |

**Results.** First run: ASP 15/15, Tamarin 14/15, ASP–Tamarin 14/15, mutations 5/5 → failed
(`sonuc/KAT_OZET.json`). Diagnosis model: 6/6 cells as expected, including K1-11. Corrected run:
Tamarin 15/15, ASP–Tamarin 15/15, mutations 5/5 → passed (`sonuc_v2/KAT_OZET.json`).

**Generated, not translated:** `sonuc/KAT_OZET.md`, `sonuc_v2/KAT_OZET.md`, `sonuc_v2/YANYANA.md`
(Turkish summaries written by the evaluation scripts; `GEÇTİ` = passed, `KALDI` = failed).
