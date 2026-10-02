# experiment/oracle — expected decisions for the C3 battery (Step 9, tasks 6–8)

For every vector × policy configuration × arm, an oracle states the decision that a verifier
conforming to the specifications must reach: `accept-hybrid`, `accept-classical`, `reject` or
`indeterminate` (four-valued output, PR Ö6). The decisions are derived only from specification
clauses (quoted verbatim, with file and line) and from the construction facts recorded in the
vector manifest (`insa`); no cryptography is executed and no target library is used.

Two oracles were derived independently (N-version): neither read the other's folder, and B was
committed before A was finished. Their merged decision for battery v1.3 is the reference against
which the C3 measurements are compared.

| Folder / file | Content |
|---|---|
| [`oracle-A/`](oracle-A/) | Oracle A: eleven policy configurations, decision generator, adapter contract, divergence detector design |
| [`oracle-B/`](oracle-B/) | Oracle B: three policy configurations (L4, P2, P0) plus SD-JWT VC version suffixes |
| [`merged/`](merged/) | Merged oracle for battery v1.3 (rules of PR §2H items 7–10) |
| `AB-COMPARISON.md` | Comparison of A and B (25.09.2026) |

**Inputs.** Vector manifests `experiment/vector-generator/vectors/v1.2/` and `v1.3/`, the battery
mapping `experiment/vector-generator/BATTERY-MAPPING.md`, the corpus texts `spec-corpus/metin/`, and
the pre-registration (expected at `00-on-kayit/ON-KAYIT-TASLAK.md`; not part of this release).

**Used by.** `experiment/runs/` (comparison of each measured decision with the merged oracle) and
`experiment/statistics/` (deviation from the oracle defines F_K, F_T and `uyum`).

## A ↔ B comparison (`AB-COMPARISON.md`)

Common configurations L4 and P0, key (vector, policy, arm):

| Configuration | Scope | Common | Equal | At least one undetermined | Definitely different |
|---|---|---|---|---|---|
| L4 | primary in both | 53 | 48 | 4 | 1 |
| L4 | all | 138 | 102 | 40 | 1 |
| P0 | primary in both | 20 | 16 | 0 | 4 |
| P0 | all | 61 | 41 | 0 | 20 |

All definite differences come from points that both oracles had flagged as undefined in the
pre-registration (K8/K9 in the composite arm; the hybrid/classical distinction under P0; the
extra-signature case K5). These definitions were then added to the pre-registration (PR §2H
items 7–10) and applied in `merged/`.

## Names in this folder

The folder and file names were renamed to English on 03.10.2026 (`docs/PATHS.tsv`): `birlesik/` →
`merged/`, `karar*.tsv` → `decisions*.tsv`, `turet_*.py` → `derive_*.py`, `karar_uret.py` →
`make_decisions.py`, `maddeler.tsv` → `items.tsv`, `insa_denetimi.txt` → `construction_audit.txt`,
`karar_ozet.json` → `decisions_summary.json`, `OZET*.json` → `SUMMARY*.json`. Recorded files (the
SHA-256 records and the summaries) still use the old names. Column names and values (`karar`
decision, `kaynak` source, ...): `docs/DATA-DICTIONARY.md` §5.
