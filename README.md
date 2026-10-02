# PQ-OID4VC artifact

Research artifact for a study of the post-quantum transition of OpenID4VC credential ecosystems
(EUDI Wallet, SD-JWT VC, JOSE/COSE). The study asks two questions:

1. **Which signatures must become post-quantum, at which time and on which channel?** During the
   period in which classical and post-quantum artefacts coexist, the answer is a *minimal set* of
   artefacts that depends on the time a quantum attacker needs per key (τ) and on whether an
   artefact is conveyed by the presenter or fetched from an authoritative source.
2. **Can a verifier learn a per-entity post-quantum expectation without a downgrade path?** The
   study models existing expectation-conveyance mechanisms (M-a … M-h) and a proposed one (M-f), and
   measures what real JOSE, SD-JWT and COSE libraries can express.

The repository contains the specification corpus manifest, the traceability matrix, the threat
model, the formal models (ASP, z3, Tamarin, ProVerif), the test-vector generator, two independent
oracles, the statistics scripts, the library adapters and the raw outputs. Every tool runs in a
pinned Linux container. Numbers reported in the paper are taken from script outputs in this
repository. The paper itself is not part of this repository.

## Contents

- [Folder map](#folder-map)
- [How the parts fit together](#how-the-parts-fit-together)
- [What supports which part of the paper](#what-supports-which-part-of-the-paper)
- [Reproducing](#reproducing)
- [Language, names and integrity](#language-names-and-integrity)
- [Licence](#licence)

## Folder map

| Path | Role | Step |
|---|---|---|
| [`spec-corpus/`](spec-corpus/) | Manifest of the 58 specification documents (version, URL, SHA-256); download and verification scripts | 1 |
| [`traceability/`](traceability/) | Traceability matrix: 400 verbatim normative quotes mapped to artefact, signer, algorithm condition, channel and security goal | 1 |
| [`threat-model/`](threat-model/) | Threat model: 13 artefacts, channel classes, attacker classes, security goals G1–G5 | 1 |
| [`data/`](data/) | EU List of Trusted Lists (LOTL) snapshot and trusted-list pilot statistics | 1 |
| [`tools/`](tools/) | Tool containers (Tamarin 1.12.0 + Maude 3.5.1, clingo 5.8.2 + z3, ProVerif 2.05) and their regression tests | 2 |
| [`models/asp/`](models/asp/) | ASP system model (clingo) with an independent z3 encoding: minimal post-quantum sets for 52,693 queries | 3 |
| [`models/tamarin/`](models/tamarin/) | Tamarin rule schemata R1–R7, their Datalog counterparts and a ProVerif second opinion | 4, 5A |
| [`models/sampling/`](models/sampling/) | Abstraction sampling: ASP verdicts checked against Tamarin on sampled cells (technical gate; Step 5B) | 5B |
| [`models/known-answer-tests/`](models/known-answer-tests/) | Known-answer tests on DNSSEC, hybrid X.509 and S/MIME, with blind N-version expected values | 6 |
| [`models/mechanisms/`](models/mechanisms/) | Expectation-conveyance mechanism models M-a … M-h and the proposed M-f, with pre-registered expectations | 7 |
| [`models/comparison/`](models/comparison/) | Strategy comparison S0–S8 × metrics M1–M5, ablations, figures | 8 |
| [`experiment/inventory/`](experiment/inventory/) | Sampling frame and selection of the C3 target libraries (n = 31) | 9 |
| [`experiment/signer/`](experiment/signer/) | `pqjose`: post-quantum and composite JWS signer/verifier; local PQ verification service | 9 |
| [`experiment/vector-generator/`](experiment/vector-generator/) | Deterministic credential and test-vector generator; vector sets v1–v1.3 (200 vectors) | 9 |
| [`experiment/oracle/`](experiment/oracle/) | Two independently derived oracles (A, B) and the merged four-valued oracle for battery v1.3 | 9 |
| [`experiment/environments/`](experiment/environments/) | Pinned language environments and the build pre-test of the 34 targets | 9 |
| [`experiment/statistics/`](experiment/statistics/) | Pre-registered statistics for C3 / H6, validated on synthetic data only | 9 |
| [`experiment/runs/`](experiment/runs/) | Library adapters (one container per target), job lists, runner contract and raw outputs | 10 |
| [`docs/`](docs/) | Glossary, data dictionary, path history, integrity notes | — |

Each folder has its own `README.md` with inputs, outputs, commands and a summary of the results.

## How the parts fit together

The study follows one line: specification → model → minimal set → expectation mechanism →
library capability.

```
spec-corpus ──► traceability ──► threat-model
     │               │                │
     │               └───────┬────────┘
     │                       ▼
     │                 models/asp ──► models/sampling ◄── models/tamarin
     │                   │     │             (technical gate)    │
     │                   │     └─► models/known-answer-tests ◄───┘
     │                   ▼                                        │
     │             models/comparison ◄── models/mechanisms ◄──────┘
     │
     ├──► experiment/signer ──► experiment/vector-generator ──► experiment/oracle
     │                                         │                      │
experiment/inventory ──► experiment/environments ──► experiment/runs ◄┘
                                                          │
                                               experiment/statistics
```

- **Step 1.** `spec-corpus/` pins the specification texts. `traceability/` quotes them (every quote
  is checked verbatim against the corpus text) and assigns each normative sentence to an artefact
  and a channel. `threat-model/` builds on the matrix (rows `T001`–`T400`) and on the LOTL snapshot
  in `data/`.
- **Step 2.** `tools/` builds the solver and prover images that all model folders use.
- **Step 3.** `models/asp/` turns the threat model into ASP facts (artefacts, edges, channels,
  windows, carriers) and computes minimal post-quantum sets; z3 re-computes every query. It exports
  the sampling frame `models/asp/sampling/cerceve.jsonl`.
- **Steps 4–5A.** `models/tamarin/` proves or refutes the same rules symbolically (R1–R7). The
  Tamarin verdicts are compared with the Datalog/ASP core (`models/asp/regresyon/`).
- **Step 5B / technical gate.** `models/sampling/` selects rows of the ASP frame with a seeded,
  hash-ordered rule, translates them into Tamarin instances and checks that Tamarin agrees with the
  ASP prediction.
- **Step 6.** `models/known-answer-tests/` runs the same ASP core (its SHA-256 is pinned in the
  run scripts) and the same Tamarin style on three ecosystems with published results.
- **Step 7.** `models/mechanisms/` models the expectation-conveyance mechanisms; its expectations
  were fixed before the runs.
- **Step 8.** `models/comparison/` compares baseline strategies on top of the ASP queries and the
  mechanism results.
- **Step 9.** `experiment/inventory/` selects the target libraries. `experiment/signer/` provides the
  post-quantum signer, on which `experiment/vector-generator/` builds the test battery. The two
  oracles in `experiment/oracle/` derive the expected decision for every vector × policy × arm from
  the specification clauses; `experiment/environments/` pins one build environment per language;
  `experiment/statistics/` fixes the analysis before any measurement.
- **Step 10.** `experiment/runs/` runs every target adapter on the battery and compares the outcome
  with the merged oracle; the statistics scripts are applied to the result.

## What supports which part of the paper

| Part of the paper | Folders |
|---|---|
| Specification analysis, channel classification and threat model | `spec-corpus/`, `traceability/`, `threat-model/`, `data/` |
| C1 — proven abstraction: time- and channel-resolved minimal post-quantum sets (H0, H1, H2, H4, H5) | `models/asp/`, `models/tamarin/`, `models/sampling/`, `models/known-answer-tests/`, `models/comparison/` |
| C2 — expectation conveyance: mechanism classes M-a … M-h and the proposed M-f (H3) | `models/mechanisms/`, rule schema R7 in `models/tamarin/` |
| C3 — capability of JOSE, SD-JWT and COSE libraries, control vs. treatment arms (H6) | `experiment/` |
| Validity: abstraction sampling, mutation scores, known-answer tests, N-version oracles | `models/sampling/`, `models/tamarin/`, `models/known-answer-tests/`, `experiment/oracle/` |

## Reproducing

**Requirements.** Docker; a POSIX shell; Python 3.11 for the host-side scripts. The run scripts
were written for Git Bash on Windows: they set `MSYS_NO_PATHCONV=1` and convert mount paths with
`cygpath -m` (on Linux, use the plain path instead). No network access is needed after the images
are built, except for re-downloading the corpus.

1. **Specification corpus.** The texts are not redistributed.
   `python spec-corpus/korpus_indir.py` downloads them into `spec-corpus/kaynak/` and
   `spec-corpus/metin/`; `python spec-corpus/korpus_dogrula.py` checks every file against
   `MANIFEST.csv`. Several scripts (quote verification, oracles, vector self-verification) read
   `spec-corpus/metin/`.
2. **Tool images.** Place the pinned binaries in `tools/*/indir/` (file names and SHA-256 values
   in [`tools/README.md`](tools/README.md)), then run `sh tools/build.sh` and build
   `tools/proverif`. `sh tools/regression-tests/calistir.sh` re-runs the design-stage pilots as an
   acceptance test.
3. **Models.** Follow the README of each folder in step order: `models/asp/`, `models/tamarin/`,
   `models/sampling/`, `models/known-answer-tests/`, `models/mechanisms/`. Tamarin runs always use
   `--memory=12g --memory-swap=12g` and a wall-clock timeout.
4. **Experiment.** Build `experiment/signer` and `experiment/vector-generator` (the generator image
   is built `FROM` the signer image), regenerate and self-verify the vectors, derive the oracles,
   then build the language environments and adapters.

Quick checks that need only Python (no Docker):

```
python experiment/oracle/birlesik/turet_v13.py            # rewrites karar_v13.tsv identically
cd experiment/statistics && python sentetik-testler/calistir.py --cikti /tmp/c3istat-test
```

The battery-mapping audit (`experiment/vector-generator/testler/t11_esleme_denetim.py`) also needs
the pre-registration document, which is not part of this release.

## Language, names and integrity

- The study was run in Turkish. Documentation and the comments of hand-written scripts are in
  English. Folder names below the second level, file names, data fields and data values are still
  Turkish because recorded outputs refer to them. Model files (ASP `.lp`, Tamarin `.spthy`),
  generated samples and recorded outputs keep their Turkish comments and messages: they are inputs
  or outputs of recorded runs, and some of them are checked by hard-coded digests. See [`docs/GLOSSARY.md`](docs/GLOSSARY.md) and
  [`docs/DATA-DICTIONARY.md`](docs/DATA-DICTIONARY.md).
- Recorded outputs keep the paths that were valid when they were produced; the old and new folder
  and document names are in [`docs/PATHS.md`](docs/PATHS.md).
- Per-folder integrity lists (`SHA256SUMS`, `*.sha256`) are kept exactly as they were recorded
  before the runs. Where this release translated or renamed a listed file, the recorded bytes are
  kept in `archive/hash-anchored/`. [`docs/INTEGRITY.md`](docs/INTEGRITY.md) explains this, and
  `python tools/verify_anchors.py` checks every record.

## Licence

Code: MIT (see [`LICENSE`](LICENSE)). Data, models and documentation: CC BY 4.0.
Third-party specifications are not redistributed; they are referenced by URL and SHA-256.
Third-party build outputs under `experiment/environments/hedefler/*/cikti*/` (lock files,
dependency lists) are kept as records of the build environment and remain under the licences of
their projects.
