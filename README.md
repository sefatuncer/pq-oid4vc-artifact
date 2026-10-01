# PQ-OID4VC artifact

Research artifact for a study of the post-quantum transition of OpenID4VC credential ecosystems
(EUDI Wallet, SD-JWT VC, JOSE/COSE): which signatures must become post-quantum, at which time and on
which channel, and whether a verifier can learn a per-entity post-quantum expectation without a
downgrade path.

Everything here is produced by scripts in containers; every number in the accompanying paper comes
from a script output in this repository. The paper itself is not part of this repository.

## Layout

| Path | Contents |
|---|---|
| `00-on-kayit/` | Pre-registration (frozen version and freeze package with `SHA256SUMS`) |
| `spec-corpus/` | Specification corpus manifest: versions, URLs, SHA-256; `korpus_indir.py` re-downloads the texts |
| `traceability/` | Traceability matrix: normative sentence → artefact → signer → algorithm → channel |
| `threat-model/` | Threat model |
| `models/asp/` | ASP (clingo) system model, z3 cross-encoding, query catalogue and results |
| `models/tamarin/` | Tamarin rule schemata (R1–R7) and run scripts |
| `model/sampling/` | Abstraction sampling: ASP verdicts vs. Tamarin on sampled cells (technical gate, step 5B) |
| `model/known-answer-tests/` | Known-answer tests (DNSSEC, X.509, S/MIME) |
| `model/mechanisms/` | Expectation-conveyance mechanism models (M-a … M-h, M-f) |
| `model/comparison/` | Strategy comparison (S0–S7), minimal sets, figures |
| `experiment/vector-generator/` | Test-vector generator and vectors (JOSE, SD-JWT, COSE; classical, ML-DSA, composite) |
| `experiment/oracle/` | Two independent oracles and the merged four-valued oracle |
| `experiment/runs/` | Library adapters (one container per target library), job lists, runner, raw outputs |
| `experiment/statistics/` | Pre-registered statistics scripts |
| `experiment/inventory/`, `experiment/environments/` | Target inventory and pinned build environments |
| `tools/` | Tool containers: Tamarin 1.12.0 + Maude 3.5.1, clingo/z3, ProVerif |
| `data/` | EU LOTL snapshot and trusted-list pilot data |

Directory and file names are Turkish (`model` = model, `deney` = experiment, `kosum` = run,
`sonuc` = result, `betik` = script, `ham` = raw, `ozet` = summary, `on-kayit` = pre-registration).

## Reproducing

All tools run in Linux containers (Docker). Tool images are built from `tools/*/Dockerfile` with
pinned, SHA-256-checked downloads. Each step directory contains its run script (`betik/`, `calistir*.sh`
or `*.py`) and the raw outputs it produced. Tamarin runs use `--memory=12g` and a wall-clock timeout.

## Licence

Code: MIT (see `LICENSE`). Data, models and documentation: CC BY 4.0.
Third-party specifications are not redistributed; they are referenced by URL and SHA-256.
