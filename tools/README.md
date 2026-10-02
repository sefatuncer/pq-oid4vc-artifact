# tools — Step 2: tool chain (containers)

All formal tools run in Linux containers. (On the Windows host used for the study, Windows
Application Control blocked clingo's native DLL, so nothing runs on the host directly.)

**Used by.** `models/asp/`, `models/tamarin/`, `models/sampling/`, `models/known-answer-tests/`,
`models/mechanisms/` and `models/comparison/` run their scripts in these images.

## Images

| Image | Content | Image id (23.09.2026) |
|---|---|---|
| `pq-a02-tamarin:1.12.0` | Tamarin 1.12.0 (official linux64 binary) + Maude 3.5.1 (official) | `sha256:7dd7a72d…` |
| `pq-a02-solver:1.0` | clingo 5.8.2 + z3-solver 5.1.0.0 (PyPI) | `sha256:5909c48b…` |
| `pq-a02-proverif:2.05` | ProVerif 2.05, built from source without the GUI (≈51 MB) | `sha256:9d15c7a7…` |

**Base image** (pinned by digest in every Dockerfile):
`python:3.11-slim@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534`

**Downloaded binaries** (checked against the GitHub release digests; expected values in
`tamarin/indir/beklenen.sha256`). Place them in `tamarin/indir/` before building; `indir/` is not
part of the repository (`indir` = download).

| File | SHA-256 |
|---|---|
| `tamarin-prover-1.12.0-linux64-ubuntu.tar.gz` | `201be06f469e47cff554df6ca93db8366fc2c69d70c61fcbd1370a1074b469c6` |
| `Maude-3.5.1-linux-x86_64.zip` | `72ed1ca87e3b3d0dfc6ee1436baf154bf04c45ff97d521bec040c5e8dfc8f92c` |
| Extracted `tamarin-prover` (→ `indir/tamarin/tamarin-prover`) | `9d3fcbaa65aeea244cff5b8074338d129427161cc8b02e5aee72d30ee072acc9` |
| Extracted `maude` (→ `indir/maude/`) | `9dd4044e693944aae97ad72086bc70275fa34bf635f9b377a5b2100bf3ed8655` |

**ProVerif 2.05** (`proverif/Dockerfile`, multi-stage build):
- Built from the official source archive **without the interactive GUI** (`./build -nointeract`).
- Source archive `proverif2.05.tar.gz` (→ `proverif/indir/`), SHA-256
  `4871f53c32ab4a04669a060c4886ba5d9080496963fb980a9a62d2c429ceabc4`. Source:
  `https://bblanche.gitlabpages.inria.fr/proverif/`.
- The opam route was not used: the opam package depends on `lablgtk`, so a build with
  `--no-depexts` fails, and the default build pulls unapproved GTK packages and produces a 3.2 GB
  image.

## Usage (Git Bash)

Build:
```
sh tools/build.sh                                            # tamarin and solver images, prints versions
docker build -t pq-a02-proverif:2.05 tools/proverif
```

Run Tamarin with a memory limit (mandatory for every heavy job):
```
MSYS_NO_PATHCONV=1 docker run --rm --memory=12g --memory-swap=12g -v "$(cygpath -m "$PWD/models/tamarin"):/work" pq-a02-tamarin:1.12.0 tamarin-prover --prove /work/<file>.spthy
```

Run the solvers:
```
MSYS_NO_PATHCONV=1 docker run --rm -v "$(cygpath -m "$PWD/models/asp"):/work" -w /work pq-a02-solver:1.0 python <script>.py
```

## Acceptance test (`regression-tests/run.sh`)

The test reproduces the design-stage pilots P1 (Tamarin), P1b (ProVerif) and P2 (ASP + z3) with the
new images. Result (23.09.2026): **identical**. Details in
[`regression-tests/README.md`](regression-tests/README.md).

| Test | Expected (pilot) | Observed |
|---|---|---|
| V1 base | falsified (8) | falsified (8), 1.2 s, 108 MiB |
| V2 expectTL | falsified (8) | falsified (8) |
| V3 tlPQ | falsified (9) | falsified (9) |
| V4 tlPQ + expectTL | verified (12) | verified (12) |
| V5 tlPQ + nocoexist | verified (7) | verified (7) |
| V6 tlClassical + nocoexist | falsified (8) | falsified (8) |
| L2 `[use_induction]` | verified (20) | verified (20), 0.27 s |
| L1 without induction | timeout | timeout after 60 s, 1,976 MiB (the memory limit works) |
| P2 ASP + z3 | 48 queries, 48/48 agreement, single optimal order | 48 queries in 0.028 s; z3–clingo **48/48**; optimal order 1 |
| P1b ProVerif, 4 variants | 1 true, 1 false, 2 "cannot be proved" | the same (TLpq+required: true; TLpq+none: false; TLclassical: 2× cannot be proved) |

Raw outputs: `regression-tests/results/`, `regression-tests/p1/out_*.txt`, `regression-tests/p2/`.

## Integrity check (`verify_anchors.py`)

`python tools/verify_anchors.py` checks every SHA-256 record of the repository (`SHA256SUMS`,
`*.sha256`, `SHA256-ON-KAYIT.txt`, `models/tamarin/sonuc/sha256*.txt`, ...) against the current
files, the archived copies in `archive/hash-anchored/` and the notes in
`archive/hash-anchored/ANCHOR-NOTES.tsv`. Standard library only; exit code 0 means that every
entry is accounted for. Background and the last output: [`../docs/INTEGRITY.md`](../docs/INTEGRITY.md).

## Docker protocol

- The image and container lists are recorded at the start of a session. Images and containers that
  existed before are never touched.
- The project's images carry the prefix `pq-`. When the project ends they are removed by name:
  ```
  docker rmi $(docker images --format '{{.Repository}}:{{.Tag}}' | grep '^pq-')
  ```
- `docker image prune`, `docker system prune` and bulk deletion are not used.

## Turkish names in this folder

`indir/` downloads (not in the repository; the Dockerfiles copy from it) · `beklenen.sha256`
expected hashes. Recorded outputs under `regression-tests/results/` still mention the old names
`calistir.sh` (now `run.sh`) and `sonuc/` (now `results/`); see `docs/PATHS.tsv`.
