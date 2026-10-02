# models/mechanisms — expectation-conveyance mechanisms (Step 7, contribution C2)

**What it does.** Models, in Tamarin, the classes of mechanisms by which a verifier could learn that
an entity has migrated to post-quantum signatures, and checks the three forms of goal G5 (no
classical acceptance after migration: untimed, timed, migrated) for each class:

| Class | Mechanism | Model |
|---|---|---|
| M-b0 | Unsigned request (baseline: HAIP and the DC API leave request signing to the wallet) | `modeller/M_istek.spthy` |
| M-a | Unauthenticated algorithm negotiation (OID4VP issue #791) | `modeller/M_istek.spthy` |
| M-b / A.3.2.2 | Multi-signed request object of OID4VP A.3.2.2 ("one is enough") | `modeller/M_istek.spthy` |
| M-d | Post-quantum registration channel | `modeller/M_metaveri.spthy` |
| M-e, M-e′ | Issuer metadata declaring "supported" (M-e) or "required" (M-e′) algorithms | `modeller/M_metaveri.spthy` |
| M-f | Proposed: authenticated, monotone, per-entity expectation with sunset, carried in a trusted list / LoTE entry or an RP certificate; expectation scope `yaprak_alg` (leaf algorithm), `anahtar` (key) or `yol_sinifi` (path class) | `modeller/Mf_yol.spthy`, `modeller/Mf_ek.spthy` (offline annex) |
| M-g | Certificate-chain continuity policy (draft-sheffer) | `modeller/Mg_yol.spthy` |
| M-h | Commitment extensions in X.509 (draft-reddy, draft-vicente) | `modeller/M_h.spthy` |

All models share the goal lemmas of `modeller/ortak_g5.spthy`. Expected verdicts for every
variant and lemma were fixed before the runs (`on_kayit_varyantlar.tsv`, PR anchor 8 = `2d16592`)
and the anchor is checked at the start of every run (`SHA256-ON-KAYIT.txt`).

**Inputs.** `on_kayit_varyantlar.tsv` (pre-registered expectations; not modified),
`modeller/*.spthy`, the image `pq-a02-tamarin:1.12.0`.

**Outputs.** `sonuc/` (results) → used by the strategy comparison (`models/comparison/`) and the
paper's C2 section.

## Files

| Path | Content |
|---|---|
| `on_kayit_varyantlar.tsv` | Pre-registered variant table: rule, variant, role, model, flags, expected lemma verdicts. 73 rows (63, plus 10 added by Amendment 8); 43 variants are run (roles mechanism, condition, carrier, ablation, 3a, 3b), the others are covered by Step 5A (18), reduced (11) or descriptive (1) |
| `SHA256-ON-KAYIT.txt` | Hash list of the anchored files (variant table and models), checked by `betik/calistir.sh` |
| `iyi_bicimlilik_on_kayit.txt` | Well-formedness check without `--prove` of the 33 rows to run before Amendment 8: 33/33 clean |
| `EK-HAZIR.txt` | Hash and time of the variant table when the extra rows (amendment 8) were added |
| `betik/calistir.sh`, `betik/ic_kosum.sh` | Runs (one container per lemma; resumes where it stopped) |
| `betik/iyi_bicimlilik.sh` | Well-formedness check only (no `--prove`) |
| `betik/karsilastir.py` | Expected vs. observed → `sonuc/karsilastirma.csv`, `beklenmeyen.csv`, `izler.csv`, `varyant_ozeti.csv` |
| `betik/tablolar.py` | Result tables → `sonuc/tablolar.md` (generated, Turkish) |
| `betik/ek_yuk.py` | Deterministic overhead per mechanism (bytes on the wire, extra fetches) from encoding rules → `sonuc/ek_yuk.csv` |
| `sonuc/ozet.csv`, `sonuc/ham/`, `sonuc/json/`, `sonuc/calistir_log.txt` | Results per lemma, raw Tamarin output, traces, run log |
| `sonuc/kosum_tamamla_0110.txt`, `sonuc/yeniden_kosum_0110/` | Completion of the interrupted run on 01.10.2026 and the independent re-run of the two unexpected verdicts |
| `kesif/` | Exploratory runs outside the pre-registration (see [`kesif/README.md`](kesif/README.md)) |
| `tau_israf/` | Tamarin instances for the τ-waste cells of H4 (see [`tau_israf/README.md`](tau_israf/README.md)) |
| `STEP07-REPORT.md` | Step 7 report: acceptance criteria, results per class, the two unexpected verdicts, consequences for H3 |
| `PRE-REGISTRATION-RATIONALE.md` | Rationale of the pre-registered expectations, per mechanism |
| `M-f-DEFINITION.md` | Simplified definition of M-f: fields of the per-entity record, verification rule, proof status, limits |
| `DECISION-NOTES.md` | Notes and decisions of Step 7 |

## How to run

```
bash models/mechanisms/betik/calistir.sh              # all rows to run (resumes)
bash models/mechanisms/betik/calistir.sh <variant>    # one row
python models/mechanisms/betik/karsilastir.py
python models/mechanisms/betik/tablolar.py
python models/mechanisms/betik/ek_yuk.py
```

Every call: `--rm --memory=12g --memory-swap=12g`, 600 s timeout, `--derivcheck-timeout=60`, ladder
rungs 1 → 3 → 5 → 6; a run with a well-formedness warning is invalid.

## Results (from `sonuc/karsilastirma.csv` and `STEP07-REPORT.md`)

- **762 lemma runs**, all closed on rung 1, all well-formed; expected = observed **760/762**.
- M-b0, M-a and M-b / A.3.2.2: all three G5 forms falsified (attack traces). M-d: migrated form
  falsified, as pre-registered. M-e: untimed and migrated falsified, timed verified; M-e′: all three
  verified.
- The two unexpected verdicts: `no_rollback` is falsified for `ME_signed_fresh` and
  `MEP_signed_fresh` (verified was expected). The re-run on 01.10 gave the same verdict; the trace
  shows that metadata signed with the classical key of a *non-migrated* issuer can be forged after
  the key is broken. Restricted to migrated entities (exploration `kesif/me_gocmus/`) the lemma is
  verified for M-e (38 steps) and M-e′ (45 steps).
- Simplified M-f with scope `yol_sinifi` (path class): every G5 form and every path form verified
  against all three attacks (alternative CA with another name, CA with the same name, classical
  root + post-quantum intermediate); scope `anahtar`: path forms falsified; scope `yaprak_alg`: G1
  falsified.
- M-h (reddy, vicente) on a classical chain: all three G5 forms falsified.

## Turkish names in this folder

`betik` scripts · `modeller` models · `sonuc` results · `ham` raw · `on_kayit` pre-registration ·
`varyantlar` variants · `iyi_bicimlilik` well-formedness · `karsilastir`/`karsilastirma`
compare/comparison · `beklenmeyen` unexpected · `izler` traces · `varyant_ozeti` variant summary ·
`tablolar` tables · `ek_yuk` overhead · `kosum_tamamla` run completion · `yeniden_kosum` re-run ·
`EK-HAZIR` extra rows ready · `kesif` exploration · `tau_israf` τ-waste. Model names: `M_istek`
request, `M_metaveri` metadata, `Mf_yol` M-f path, `Mf_ek` M-f annex, `Mg_yol` M-g path, `ortak_g5`
common G5 lemmas. Roles in the tables: `mekanizma` mechanism, `kosul` condition, `tasiyici` carrier,
`ablasyon` ablation, `3a`/`3b` task 3a/3b.
