# models/known-answer-tests/x509 — KAT-2 hybrid X.509

**What it does.** Reproduces published results on hybrid (composite and "catalyst"-style)
certificates: accepting a hybrid certificate under a classical validator is not hybrid
authentication. Sub-tables: K2a honest decision without attacker, K2b forgery with a CRQC, K2c
related certificates (`ignore`/`require`), K2d policies P0–P3 under an attacker that keeps a legacy
certificate (M1). 40 ASP cells, 8 Tamarin cells (`KAT2_X509.spthy`, lemmas `cert_authentic`,
`no_silent_promotion`), 4 mutations, plus extra sensitivity rows (`ek_tamarin.tsv`, not gate cells).

**Inputs.** `hucreler.tsv`, `mutasyonlar.tsv`, `ek_tamarin.tsv`, `alintilar.tsv`; expected values
from `../nsurum/kat_nsurum.tsv`. Mapping and the fixed decision reading rule (`kos.py: karar_oku`):
`../MAPPING.md` §3.

**Outputs.** `sonuc/` (`asp.csv`, `asp_mutasyon.csv`, `tamarin.csv`, `tamarin_mutasyon.csv`,
`tamarin_ek.csv`, `alinti_denetimi.tsv`, `KAT_OZET.json`), `iyi_bicim/`.

| File | Content |
|---|---|
| `kat2_x509.lp` | ASP facts and reading rules of KAT-2 |
| `KAT2_X509.spthy` | Tamarin model |
| `uret.py`, `kos.py`, `tamarin_kos.py`, `tamarin_ic.sh`, `alinti_dogrula.py`, `degerlendir.py`, `calistir.sh` | Pipeline (see `../README.md`) |

**Results** (`sonuc/KAT_OZET.json`): ASP 40/40, Tamarin 8/8, ASP–Tamarin 8/8, mutations 4/4 →
passed.

**Generated, not translated:** `sonuc/KAT_OZET.md`.
