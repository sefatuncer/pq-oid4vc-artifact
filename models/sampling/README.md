# models/sampling — abstraction sampling (technical gate and Step 5B)

The ASP model (`models/asp/`) is fast and exhaustive but abstract. This folder checks the
abstraction: rows of the ASP sampling frame are translated into stand-alone Tamarin theories, run,
and the Tamarin verdict is compared with the ASP prediction. The translation reads only the inputs
of the ASP model (the assignment and the model structure), never its outputs.

| Folder | Content |
|---|---|
| [`secim/`](secim/) | Seeded, hash-ordered selection of the technical-gate samples (10 gate samples + 1 exploratory sample) |
| [`teknik-kapi/`](teknik-kapi/) | Technical gate: translation of the selected rows into Tamarin, runs, comparison with ASP |
| `5b/` | Step 5B (larger sample and total mutation score); work in progress, documented in that folder |

**Inputs.** `models/asp/sampling/cerceve.jsonl` and `kesif_2x2.jsonl` (frame), the rule templates
of `models/tamarin/modeller/`, the image `pq-a02-tamarin:1.12.0`.

**Gate rule (PR §2F, P-16).** On closed samples the agreement must be 100 %; differences are neither
classified nor corrected. The gate count uses only the 10 gate samples.

**Result.** `teknik-kapi/sonuc.csv`: ASP prediction = Tamarin verdict on **10/10** gate samples
(3 verified, 7 falsified) and on the exploratory sample (falsified); every run well-formed.

## Turkish names in this folder

`secim` selection · `teknik-kapi` technical gate · `cevir` translate · `ceviri_plani` translation
plan · `on_ceviri` pre-run translation hash · `karsilastir` compare · `saglik` sanity ·
`tamarin_ham` raw Tamarin results · `ornekler` generated instances · `sonuc` result.
