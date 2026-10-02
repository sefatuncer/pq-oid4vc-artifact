# models/mechanisms/kesif — exploratory runs (outside the pre-registration)

**What it does.** Records exploratory Tamarin runs that were started by an observation of the
Step 7 runs. They are not part of the pre-registration and do not count for the gate or for the
H3 evaluation. Expectations were nevertheless written before each run.

| Path | Content |
|---|---|
| `kesif.tsv` | Exploration record X1: trigger, assumption, expected lemma verdicts (written before the runs) |
| `M_metaveri_x.spthy` | `../modeller/M_metaveri.spthy` (byte-identical prefix) plus two lemmas |
| `ortak_g5.spthy` | Byte-identical copy of `../modeller/ortak_g5.spthy` |
| `on_kayit.sha256` | Hashes of the files above, fixed before the runs and checked by `calistir.sh` |
| `calistir.sh` | Runs only the lemmas listed in `kesif.tsv` (same rules as `../betik/calistir.sh`) |
| `me_gocmus/` | Exploration "M-e, migrated entities only": `no_rollback` restricted to migrated entities (`no_rollback_migrated`). `M_metaveri.spthy` (copy of the main model), `ortak_g5.spthy` (G5 lemmas with the restricted lemma), raw outputs `ME.txt` and `MEP.txt` |

**Trigger.** In the Step 7 runs, `ME_signed_fresh` / `no_rollback` was falsified although verified
was expected (trace: `../sonuc/json/ME_signed_fresh__no_rollback.json`). The assumption tested
here is a lemma-scope effect, not a model error: `no_rollback` does not restrict the entity type,
and the metadata of a non-migrated issuer is signed with its own classical key.

**Result** (`me_gocmus/ME.txt`, `me_gocmus/MEP.txt`; reported in `../STEP07-REPORT.md` §3): restricted to
migrated entities, the lemma is verified for M-e (38 steps) and M-e′ (45 steps).

**Turkish names:** `kesif` exploration · `me_gocmus` M-e migrated · `on_kayit` fixed before the
run · `calistir` run.
