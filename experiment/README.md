# experiment — library capability measurement (contribution C3)

C3 measures what real JOSE, SD-JWT and COSE libraries can express when a verifier must require a
post-quantum signature from a migrated issuer: capability levels L0–L5 (L0 no algorithm constraint
can be configured; L1/L2 global / per-call allow-list; L3 per-key or per-issuer algorithm binding;
L4 "required algorithm set" semantics; L5 L3/L4 enabled by default), the multi-signature semantics, and the difference between a control arm (classical EdDSA/Ed25519) and two treatment arms
(ML-DSA-65 and the composite ML-DSA-65-ES256). Hypothesis H6 and its statistical tests were
pre-registered before any measurement.

| Folder | Step | Role |
|---|---|---|
| [`inventory/`](inventory/) | 9a | Sampling frame and selection of the target libraries (n = 31 + 3 reference verifiers) |
| [`signer/`](signer/) | 9b | `pqjose` signer/verifier and the local PQ verification service |
| [`vector-generator/`](vector-generator/) | 9b | Deterministic test battery: vector sets v1 → v1.3 (200 vectors) and v1.4 (230 vectors), keys, battery mapping |
| [`oracle/`](oracle/) | 9 | Two independent oracles and the merged four-valued oracle for battery v1.3 |
| [`environments/`](environments/) | 9 | One pinned build image per language; build pre-test of the targets |
| [`statistics/`](statistics/) | 9 | Pre-registered statistics (T1–T5, Holm, Wilson, Newcombe, bootstrap), validated on synthetic data |
| [`runs/`](runs/) | 10 | Adapters (one container per target, built on the language images), job lists, runner contract (`RUNNER.md`), raw outputs (`outputs/`) |

**Flow.** `inventory` selects the targets → `environments` pins and builds them → `signer` and
`vector-generator` produce the battery → `oracle` states the expected decision for every vector ×
policy × arm → `runs` executes every adapter three times in fresh containers and maps the raw outcome
to the four-valued decision → `statistics` computes H6 from the per-target results.

**Status of this release.** Steps 9 and 9b are complete. In `runs/`, the adapters of the first
targets and the pre-freeze V± outputs are present; the full measurement runs only after the
pre-registration freeze.

Field names and values of the data files (job lists, adapter output, oracle tables, manifests,
statistics input) are explained in [`docs/DATA-DICTIONARY.md`](../docs/DATA-DICTIONARY.md).
