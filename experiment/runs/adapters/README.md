# adapters — C3 library adapters

An adapter verifies one test vector under one policy configuration through the **documented public
API** of one target library and writes one JSON line per job. Adapters never see the oracle and never
modify the library. The binding rules are in the adapter contract
[`experiment/oracle/oracle-A/adapter-contract.md`](../../oracle/oracle-A/adapter-contract.md) (contract
version `adaptor-sozlesme/1.0`) and the call format in [`../RUNNER.md`](../RUNNER.md).

## Layout

| Path | Content |
|---|---|
| `<target>/` (for example `JOSE-001/`, `COSE-036/`, `SDJWT-021/`) | An adapter with its own image: `Dockerfile`, adapter source, `MAPPING.md` (policy → API mapping, B6 decisions, exception → `hata_sinifi`), `NOTES.md` (version pinning, TK proposal, V± result, open questions) and `evidence/` (API scan and smoke tests) |
| `_py/` | Shared Python adapter: JOSE-083 pyjwt, JOSE-084 python-jose, SDJWT-018 sd-jwt-python |
| `_node/` | Shared Node.js adapter: JOSE-009 jose, JOSE-065 jsonwebtoken, COSE-014 cose-js, SDJWT-015 @sd-jwt/core |
| `_go/` | Shared Go adapter (one binary): JOSE-033 golang-jwt, JOSE-034 jose2go, COSE-034 go-cose |
| `_jvm/` | Shared Java adapter: JOSE-052 java-jwt, JOSE-055 jjwt, SDJWT-004 authlete sd-jwt (+ Nimbus) |
| `_kt/` | Kotlin adapters: COSE-001 Signum, SDJWT-001 vck (`derle.sh` builds them in a container) |
| `_rs/` | Rust adapters: JOSE-091, JOSE-092, SDJWT-010, SDJWT-025 (shared runner in `common/`, smoke tests in `smoke/`) |
| `_tools/` | Build, run and scan scripts (below), `gate_summary.py` (validity-gate summary), `control_labels.py` |

Each image is named `a10-<target>:1` (lower case) and is built `FROM` the language image
`pq-a09-env-<language>:1.0` of `experiment/environments/`, with the same library version or commit as the
installation record there.

## Build

From `experiment/runs/adapters`:

```
bash _tools/kur_hepsi.sh          # all 31 adapter images: _tools/kur.sh, _rs/build.sh and every <target>/Dockerfile
bash _tools/kur.sh JOSE-083       # one shared-adapter target only
```

Network access is needed only while the images are built (package registries, anonymous). The
adapters themselves run with `--network none`.

## Run

```
bash _tools/kos.sh <job_file> <run_label> <output_folder> [target ...]
# e.g. bash _tools/kos.sh jobs-prefreeze-v1.3.jsonl oncesi outputs/prefreeze-v1.3 JOSE-009 JOSE-083
```

- Paths are relative to `experiment/runs/`. The vectors and keys of `experiment/vector-generator/` are
  mounted read-only (`/v`, `/anahtarlar`); the job list is mounted at `/is`.
- Adapters with their own folder are called as `adaptor <jobs> <out>`; the shared adapters take
  `<target> <jobs> <out> <run>`.
- Before the pre-registration is frozen, only the pre-freeze job files (validity gate) may be run.
  The measurement run after the freeze is `../run_measurement.sh`.

## API scan

`bash _tools/api_tarama.sh [target]` scans the pinned library source (or, for the JVM, the bytecode of
the public API) inside each image and writes `<target>/evidence/api-tarama.txt` (contract §5.1).
`_rs/api_scan.sh` does the same for the Rust targets.

## Names

Field names and values in the output (`sonuc_ham`, `hata_sinifi`, `dogrulanan_algoritmalar`, ...) are
explained in [`docs/DATA-DICTIONARY.md`](../../../docs/DATA-DICTIONARY.md). Turkish words in file names:
`adaptor` adapter, `ortak` shared, `kopru` bridge, `kur` build, `kos` run, `derle` compile,
`api_tarama` API scan.
