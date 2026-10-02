# experiment/oracle/merged — merged oracle for battery v1.3

**What it does.** `derive_v13.py` merges the decisions of Oracle A and Oracle B (both derived on
battery v1.2) and extends them to the vectors that are new in v1.3 (COSE and the L4c "old issuer"),
using the rules fixed in PR §2H items 7–10 before the freeze:

- item 7: `accept-hybrid` ⇔ the acceptance rests on post-quantum evidence (rejected when the
  post-quantum signature is removed); under P0, acceptance of an object whose two signatures are both
  valid is `accept-classical`;
- item 8: case K5 (extra signature with an unrecognised algorithm) carries no single oracle decision
  → `B1-bayragi` (B1 flag);
- item 9: K8/K9 are arm-independent flags; rows of the composite arm are not measured →
  `kol-bagimsiz`;
- item 10: V± only under `GEC`;
- COSE vectors take the decision of the JOSE twin with the same case and arm; L4c-3 (old issuer, ES256
  only) is `accept-classical` under `IZIN-AX`, the L4 family, `IZIN-A` and `GEC`;
- final value: A = B → that value; only one oracle has the row → that value (`tek-oracle`); A ≠ B →
  `indeterminate`.

**Inputs.** `../oracle-A/decisions.tsv`, `../oracle-B/decisions.tsv`,
`experiment/vector-generator/vectors/v1.3/MANIFEST.csv`.

**Outputs.** `decisions_v13.tsv` (`vektor_id, politika, kol, karar, A, B, kaynak`) and `SUMMARY.json`
(distributions and the SHA-256 of the two input tables).

## How to run

```
python experiment/oracle/merged/derive_v13.py        # set PYTHONIOENCODING=utf-8 on a non-UTF-8 console
```

Re-running reproduces `decisions_v13.tsv` byte for byte; `SUMMARY.json` is reproduced up to the order of
JSON keys.

## Results (`SUMMARY.json`)

1,845 rows. Decisions: `reject` 861, `accept-classical` 460, `accept-hybrid` 255, `indeterminate` 137,
`B1-bayragi` 108, `kol-bagimsiz` 24. Sources: `tek-oracle` 1,118, `COSE-esleme` 418, `A=B` 152,
`madde-8` 96, `L4c-3` 36, `madde-9` 12, `A≠B` 10, `A|B` 3. No COSE vector without a JOSE twin.

**Names:** renamed on 03.10.2026 (`docs/PATHS.tsv`): `birlesik/` → `merged/`, `turet_v13.py` →
`derive_v13.py`, `karar_v13.tsv` → `decisions_v13.tsv`, `OZET.json` → `SUMMARY.json` (and the v14
files). `SUMMARY*.json` record the SHA-256 of the input tables under their old file names. Column
names and values (`karar` decision, `kaynak` source): `docs/DATA-DICTIONARY.md` §5.
