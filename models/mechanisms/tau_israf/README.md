# models/mechanisms/tau_israf — Tamarin instances for the τ-waste cells (H4)

**What it does.** Prepares the Tamarin instances required by PR §2H item 3 for the "wasteful under
τ" (τ-waste) candidates of H4: cells in which the published strategy S5 migrates the device key
(a10, goal G2) or the status key (a08, goal G3) although the ASP minimal set of S7 meets the goal
without it, because τ exceeds the key window. The contrasting fast-τ case (600 s), in which the
same node is required, is included.

| Path | Content |
|---|---|
| `ornekler.tsv` | The instances: source cells in `models/asp/sorgular/sonuc/h4_karsilastirma.json`, mapping to R6/R6h5 flags, expected verdicts (written before the runs) |
| `modeller/R6_time.spthy`, `modeller/R6_h5.spthy` | Byte-identical copies of the templates in `models/tamarin/modeller/` |
| `on_kayit.sha256` | Hashes of `ornekler.tsv` and the two models, fixed before the runs and checked by `calistir.sh` |
| `calistir.sh` | Runs the instances (same rules as `../betik/calistir.sh`); writes `sonuc/` |

Run outputs (`sonuc/`) are not part of this folder in this release.

**Turkish names:** `tau_israf` τ-waste · `ornekler` instances · `modeller` models · `on_kayit` fixed
before the run.
