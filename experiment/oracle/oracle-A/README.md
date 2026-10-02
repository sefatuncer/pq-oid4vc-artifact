# experiment/oracle/oracle-A — Oracle A (Step 9, tasks 6 and 7)

**What it does.** Derives, for battery v1.2, the expected decision of every vector under eleven
policy configurations (`GEC`, `IZIN-A`, `IZIN-AX`, `L4`, `L4-S`, `L4-Y`, `P0`, `P1`, `L4-YOL`,
`GEC@-19`, `L4@-19`) and every arm. A decision is derived only from specification clauses plus the
construction facts of the manifest (`insa`) and header/claim facts read by base64url-decoding the
vector files. No cryptography, no target library, no network. Oracle A also wrote the adapter
contract that all C3 adapters follow, and the design of the divergence detector.

**Inputs.** `experiment/vector-generator/vectors/v1.2/` (`MANIFEST.json`, `SHA256SUMS`),
`experiment/vector-generator/BATTERY-MAPPING.md`, the corpus texts `spec-corpus/metin/`, the
pre-registration `00-on-kayit/ON-KAYIT-TASLAK.md` (not included). The script checks the SHA-256 of
these inputs against pinned values before it starts.

**Outputs.**

| File | Content |
|---|---|
| `decisions.tsv` | Decisions: `vektor_id, politika, kol, sinif, vaka, karar, dayanak, not` (858 rows) |
| `items.tsv` | Clause register: every clause used, with document, section, version, URL, file, line and verbatim quote (107 clauses) |
| `decisions_summary.json` | Distributions, coverage, number of construction checks, metamorphic self-checks, primary `indeterminate` rows |
| `construction_audit.txt` | Construction audit: 467 checks of the vector files against the manifest, all passed |
| `SHA256SUMS` | Integrity list of the outputs and documents |

Documents:

| File | Content |
|---|---|
| `METHOD.md` | Method: inputs, four-valued decision space, derivation of the policy configurations from PR §4.13, decision rule, primary/secondary rows, out-of-scope cells, production |
| `L4-DERIVATION.md` | Derivation of the L4 oracle (premises quoted verbatim, derivation, four-valued output, K1–K11 and V± decisions, L4m and L4c, time dimension of G5, metamorphic relations) |
| `UNDETERMINED.md` | Reasons of the `indeterminate` decisions (B-1 … B-6) |
| `adapter-contract.md` | C3 adapter contract 1.0: input, output schema, error classes, timeouts and repetitions, L-level protocol, treatment class assignment, comparison rule |
| `divergence-detector.md` | Design of the divergence detector (run in Step 10): cells, algorithm, divergence types, output schema |
| `DECISION-NOTES.md` | Notes N-0 … N-13 on gaps of the pre-registration (for example the missing COSE battery, the K5 reading, the meaning of the four values) |

## How to run

```
PYTHONIOENCODING=utf-8 python experiment/oracle/oracle-A/make_decisions.py "<repository root>"
sha256sum -c experiment/oracle/oracle-A/SHA256SUMS
```

The script uses no randomness, clock or network; two runs are byte-identical.

## Results (`decisions_summary.json`)

858 rows (316 primary): `reject` 409, `accept-classical` 215, `accept-hybrid` 159, `indeterminate`
75. Primary rows: `reject` 181, `accept-classical` 90, `accept-hybrid` 41, `indeterminate` 4
(the K5 vectors `T7*_plus_kayitsiz` under L4). 153 vectors covered, 107 clauses from 15 corpus
documents.

**Turkish names:** `karar_uret` generate decisions · `karar` decision · `maddeler` clauses ·
`karar_ozet` decision summary · `insa_denetimi` construction audit · `sinif` primary/secondary
class · `vaka` case · `dayanak` basis. Values: `docs/DATA-DICTIONARY.md` §2–§5.
