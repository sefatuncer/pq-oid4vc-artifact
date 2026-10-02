# models/sampling/secim — sample selection for the technical gate (maintainers)

- Rule: PR §2F item 2 (Amendment 6, anchor 6 = `998276a`).
- Script: `teknik_kapi_secim.py`. It was written and committed BEFORE the ASP frame
  (`models/asp/sampling/cerceve.jsonl`) and the exploration grid (`kesif_2x2.jsonl`) were available.
- The selection is deterministic: rows are ordered by `sha256("20260926|<context>|<id>")`. The
  ordering does not depend on the Python version and can be checked by hand.
- Output: `secim.json` (SHA-256 of the frame and of the exploration file, stratum counts, 10 gate
  samples and 1 exploratory sample outside the gate).
- Only the maintainers write to this folder. The sample generator of Step 5B
  (`models/sampling/uretec/`, Tamarin work) is separate.

## Rule in detail

- Strata: goal {G1, G2, G3, G4, all} × type {minimal, one-short}; one sample from each non-empty
  stratum, 10 in total. If fewer than 10 strata are non-empty, the missing samples are taken from
  the whole frame in hash order. Seed 20260926 (PR Appendix C).
- Extra mandatory sample (not counted for the gate): the row of the exploration grid with
  `ca_baglama = ad` (name binding) and `ayni_ad_klasik_ca = var` (same-name classical CA present)
  that has the smallest key `sha256("20260926|kesif|<id>")`.
- The script expects the fields `kimlik` (or `id`/`satir_id`), `hedef`, `tur` and, in the
  exploration file, `ca_baglama` and `ayni_ad_klasik_ca`; it stops instead of guessing when a field
  is missing.

## How to run

```
python models/sampling/secim/teknik_kapi_secim.py models/asp/sampling/cerceve.jsonl models/asp/sampling/kesif_2x2.jsonl models/sampling/secim/secim.json
```

## Result (`secim.json`)

Frame: 2,442 rows (SHA-256 `0a9b10d1…42d87`); exploration grid: 8,442 rows (`c1e810c8…fb2ec`),
279 of them in the name-binding/same-name cell. Non-empty strata: G1, G2 and G3 × {minimal,
one-short} (G4 and "all" are UNSAT in the primary configuration). Selected:
`CERCEVE-000588`, `-000046`, `-001695`, `-001103`, `-002105`, `-002239`, completed from the whole
frame with `-001666`, `-002338`, `-001715`, `-000317`; exploratory sample `KESIF_2X2-002862`.
The paths inside `secim.json` are those of the working copy (`model\asp\ornekleme\…`, now
`models/asp/sampling/`).

## Turkish names in this folder

`secim` selection · `teknik_kapi_secim` technical-gate selection · `tohum` seed · `cerceve` frame ·
`kesif` exploration · `katmanlar` strata · `aday` candidates · `secilen` selected · `tamamlama`
completion · `kapi_ornekleri` gate samples · `kesif_ornegi` exploratory sample.
