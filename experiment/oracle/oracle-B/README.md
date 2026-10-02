# experiment/oracle/oracle-B — Oracle B (Step 9, task 6)

**What it does.** The second, independent oracle of the N-version scheme (PR §4.20). For battery
v1.2 it derives the policy-parametric, four-valued expected decision of every vector × policy
configuration × arm. Configurations: `L4` (required set R = {X}, allowed set {ES256, X}),
`P2` (all present signatures valid) and `P0` (at least one valid signature), each also with the
SD-JWT VC draft version fixed explicitly (`|sdjwtvc=-13`, `|sdjwtvc=-19`). Decisions are taken
only from primary specification clauses and from the `insa` and `dogrulama_girdileri` facts of the
manifest; vector files are not opened.

**Independence.** Oracle B did not list or read `experiment/oracle/oracle-A/` or anything else in
`experiment/oracle/`; every opened file is recorded in `ACCESS-LOG.md`. No network, Docker or git
was used.

**Inputs.** `experiment/vector-generator/vectors/v1.2/MANIFEST.json` (SHA-256 `bb17aaa7…`),
`experiment/vector-generator/BATTERY-MAPPING.md` (case roles), `spec-corpus/metin/` (quotes), the
pre-registration (`00-on-kayit/ON-KAYIT-TASLAK.md`, v0.8; not included — the script looks for the
folders `00-on-kayit` and `spec-corpus` to find the repository root).

**Outputs.** `decisions.tsv` (`vektor_id, politika, kol, birincil_mi, karar, dayanak, not`; 732 rows)
and `SHA256SUMS`.

| Document | Content |
|---|---|
| `METHOD.md` | Purpose, independence protocol, fixed inputs, derivation of the configurations, arms and arm assignment, decision rule, special cases and version dimension, quote verification, primary/secondary rows, output format, limitations, result summary |
| `L4-DERIVATION-B.md` | Independent derivation of the L4 oracle from the clauses (L4m multi-signature form, L4c compact form, time dimension, cases not determined by the clauses) |
| `UNDETERMINED.md` | The `indeterminate` decisions B1–B9 and their reasons |
| `ACCESS-LOG.md` | Directory listings, opened files, files not opened, files written |
| `DECISION-NOTES.md` | Notes N1–N17: items that may affect pre-registered variables (Y), descriptive output (O) and disclosure (D) |

## How to run

```
cd experiment/oracle/oracle-B
PYTHONIOENCODING=utf-8 python derive_decisions.py [--kollar k1,k2,...]
```

The script checks every quoted clause against the source text (whitespace-normalised, within the
recorded line range) and stops if one is not found; it cross-checks the hand-written fact tables
against the manifest. Two independent runs gave the same `decisions.tsv` hash.

## Results (`METHOD.md` §13)

732 rows covering all 153 vectors; 159 primary rows (53 primary vector–arm pairs × 3
configurations). All rows: `reject` 373, `accept-classical` 169, `accept-hybrid` 101,
`indeterminate` 89. Primary rows: `reject` 88, `accept-classical` 48, `accept-hybrid` 23,
`indeterminate` 0. All 116 clauses of the script were found in their source line range.

**Turkish names:** `turet_karar` derive decisions · `birincil_mi` primary? (`evet`/`hayır`) ·
`kollar` arms. Values: `docs/DATA-DICTIONARY.md` §3, §5.
