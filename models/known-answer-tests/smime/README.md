# models/known-answer-tests/smime — KAT-3 S/MIME

**What it does.** Reproduces published results on S/MIME with hybrid key establishment: KAT-3a
classifies CMS objects o1–o12 by "every valid path to the content-encryption key (CEK)" and checks
CEK secrecy in Tamarin (`KAT3_SMIME.spthy`, lemma `cek_secrecy`); KAT-3b checks the
authentication duality on the design-stage pilot model (variants V1–V6). 54 ASP cells, 9 Tamarin
cells, 3 mutations.

**Inputs.** `hucreler.tsv`, `mutasyonlar.tsv`, `ek_tamarin.tsv`, `alintilar.tsv`; expected values
from `../nsurum/kat_nsurum.tsv`. Mapping (CEK-based structure mapping and reading rules):
`../MAPPING.md` §4.

**Outputs.** `sonuc/` (ASP probes, Tamarin results, `KAT_OZET.json`), `iyi_bicim/`.

| File | Content |
|---|---|
| `kat3a_smime.lp` | ASP facts of KAT-3a (seven probes per object; labels derived only from probe results) |
| `kat3b_auth.lp` | ASP facts of KAT-3b (six flag combinations V1–V6) |
| `KAT3_SMIME.spthy` | Tamarin model of KAT-3a |
| `weakest_link_wf.spthy` | Well-formed version of the design-stage pilot model used by KAT-3b (the unchanged pilot produces well-formedness warnings and is used only in the extra rows) |
| `uret.py`, `kos.py`, `tamarin_kos.py`, `tamarin_ic.sh`, `alinti_dogrula.py`, `degerlendir.py`, `calistir.sh` | Pipeline (see `../README.md`) |

**Results** (`sonuc/KAT_OZET.json`): ASP 54/54, Tamarin 9/9, ASP–Tamarin 9/9, mutations 3/3 →
passed.

**Generated, not translated:** `sonuc/KAT_OZET.md`.
