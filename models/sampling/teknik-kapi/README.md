# models/sampling/teknik-kapi — technical gate: ASP rows checked in Tamarin

**What it does.** Translates the 11 selected rows of the ASP sampling frame (10 gate samples,
1 exploratory sample) into stand-alone Tamarin theories, runs them, and compares the Tamarin
verdict with the ASP prediction (PR §2F).

**Blindness rule.** The translation (`cevir.py`) reads only the *inputs* of the ASP model: the
assignment (post-quantum nodes, selected carriers), the model structure (introducers, pinning,
channel, classical alternatives, window breakability, policy) and the target lemma name. It never
reads the ASP outputs (`asp_tahmini`, `ihlal_edilen`, `tanik_sahte_artefaktlar`, the `sahte` and
`beklenti_var` fields). The run script does not read the prediction either; the comparison is done
afterwards by `karsilastir.py`. The translation was fixed by hash (`on_ceviri.sha256`) before the
runs.

**Inputs.** `../secim/secim.json` (the selection; not modified), the rule templates of
`models/tamarin/modeller/` (R1–R7 patterns are compiled into one theory per row).

**Outputs.**

| File | Content |
|---|---|
| `cevir.py` → `ornekler/<row id>.spthy`, `ceviri_plani.tsv` | Generated Tamarin theories (one per row; not translated) and the translation plan (target lemma, artefacts, keys, edges, carriers) |
| `on_ceviri.sha256` | Hashes of `secim.json`, `cevir.py`, `ceviri_plani.tsv` and the generated theories, fixed before the runs; checked by `betik/calistir.sh` |
| `betik/calistir.sh`, `betik/ic_kosum.sh` | Runs the theories (one container per lemma, `--memory=12g`, 600 s timeout, `--derivcheck-timeout=60`, ladder rungs 1 → 3 → 5 → 6) |
| `tamarin_ham.csv`, `ham/`, `json/`, `calistir_log.txt` | Raw results per lemma, raw Tamarin output, traces, run log |
| `karsilastir.py` → `sonuc.csv`, `saglik.csv`, `izler.csv` | Comparison with the ASP prediction, sanity lemma per row, rules and broken keys of the attack traces (a `farklar.csv` is written only when there is a disagreement) |
| `SHA256SUMS` | Integrity list of this folder |

## How to run

```
python models/sampling/teknik-kapi/cevir.py                  # regenerate ornekler/ and ceviri_plani.tsv
bash models/sampling/teknik-kapi/betik/calistir.sh            # all rows (or give one row id)
python models/sampling/teknik-kapi/karsilastir.py
```

## Results (`sonuc.csv`, `saglik.csv`)

| Row | Goal | Type | ASP | Tamarin |
|---|---|---|---|---|
| CERCEVE-000588 | G1 | minimal | verified | verified |
| CERCEVE-000046 | G1 | one-short | falsified | falsified |
| CERCEVE-001695 | G2 | minimal | verified | verified |
| CERCEVE-001103 | G2 | one-short | falsified | falsified |
| CERCEVE-002105 | G3 | minimal | verified | verified |
| CERCEVE-002239 | G3 | one-short | falsified | falsified |
| CERCEVE-001666 | G2 | one-short | falsified | falsified |
| CERCEVE-002338 | G3 | one-short | falsified | falsified |
| CERCEVE-001715 | G2 | one-short | falsified | falsified |
| CERCEVE-000317 | G1 | one-short | falsified | falsified |
| KESIF_2X2-002862 (exploratory) | G2 | primary set | falsified | falsified |

Agreement **10/10** on the gate samples and 1/1 on the exploratory sample. The sanity lemma
`executable` is verified in all 11 theories; every run closed on rung 1 and is well-formed
(`temiz`). Longest lemma run 40.21 s, peak memory 1,009.1 MiB (sanity lemma of CERCEVE-001103).

## Turkish names in this folder

`teknik-kapi` technical gate · `cevir` translate · `ceviri_plani` translation plan · `on_ceviri`
fixed before the runs · `ornekler` generated instances · `ham` raw · `tamarin_ham` raw Tamarin
results · `karsilastir` compare · `sonuc` result · `saglik` sanity · `izler` traces · `farklar`
differences · `calistir`/`ic_kosum` run / in-container run.
