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
| `01-korpus/` | Specification corpus manifest: versions, URLs, SHA-256; `korpus_indir.py` re-downloads the texts |
| `02-izlenebilirlik/` | Traceability matrix: normative sentence → artefact → signer → algorithm → channel |
| `03-tehdit-modeli/` | Threat model |
| `model/asp/` | ASP (clingo) system model, z3 cross-encoding, query catalogue and results |
| `model/tamarin/` | Tamarin rule schemata (R1–R7) and run scripts |
| `model/ornekleme/` | Abstraction sampling: ASP verdicts vs. Tamarin on sampled cells (technical gate, step 5B) |
| `model/bilinen-cevap/` | Known-answer tests (DNSSEC, X.509, S/MIME) |
| `model/mekanizma/` | Expectation-conveyance mechanism models (M-a … M-h, M-f) |
| `model/karsilastirma/` | Strategy comparison (S0–S7), minimal sets, figures |
| `deney/uretec/` | Test-vector generator and vectors (JOSE, SD-JWT, COSE; classical, ML-DSA, composite) |
| `deney/oracle/` | Two independent oracles and the merged four-valued oracle |
| `deney/kosum/` | Library adapters (one container per target library), job lists, runner, raw outputs |
| `deney/istatistik/` | Pre-registered statistics scripts |
| `deney/envanter/`, `deney/ortam/` | Target inventory and pinned build environments |
| `arac/` | Tool containers: Tamarin 1.12.0 + Maude 3.5.1, clingo/z3, ProVerif |
| `veri/` | EU LOTL snapshot and trusted-list pilot data |

Directory and file names are Turkish (`model` = model, `deney` = experiment, `kosum` = run,
`sonuc` = result, `betik` = script, `ham` = raw, `ozet` = summary, `on-kayit` = pre-registration).

## Reproducing

All tools run in Linux containers (Docker). Tool images are built from `arac/*/Dockerfile` with
pinned, SHA-256-checked downloads. Each step directory contains its run script (`betik/`, `calistir*.sh`
or `*.py`) and the raw outputs it produced. Tamarin runs use `--memory=12g` and a wall-clock timeout.

## Licence

Code: MIT (see `LICENSE`). Data, models and documentation: CC BY 4.0.
Third-party specifications are not redistributed; they are referenced by URL and SHA-256.
