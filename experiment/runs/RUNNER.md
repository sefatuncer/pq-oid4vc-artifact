# C3 runner interface (maintainers; updated 2026-10-03 for the pre-registration freeze)

Binding sources: pre-registration v1.0, Section 7.19 (measurement procedure), and
`experiment/oracle/oracle-A/adapter-contract.md` (contract 1.0, with the pre-freeze addendum). This file fixes the
shared **call format**, so that adapters written independently produce compatible output, and says which file is run
when. Decisions D1–D7 are in `DECISIONS-PREFREEZE.md`.

## 1. Input

- **Vectors:** measurement battery **v1.4**, `experiment/vector-generator/vectors/v1.4/`: 230 vectors = the 200
  vectors of v1.3 (byte-identical) + 30 ES384 counterparts of the control-arm vectors (Amendment 10). Hashes in
  `v1.4/SHA256SUMS`. v1.4 is mounted read-only at `/v/v1.3`, because it is a byte-identical superset of v1.3 and the
  adapters read `/v/v1.3/MANIFEST.json`; the whole `vectors/` folder is mounted read-only at `/v`.
  `BATTERY=v1.3` mounts the original v1.3 folder instead (used only for the pre-freeze v1.3 gate).
- **Verification inputs:** the MANIFEST row of each vector and `experiment/vector-generator/keys/` (JWKS and
  trust anchors), mounted read-only at `/anahtarlar`.
- **Job lists:** one JSON object per line with the fields `vektor_id`, `politika`, `kol`, `dosya` (relative to `/v`),
  `serilestirme`, `artefakt`, `algler`. No job list contains an oracle decision; the adapter does not see the oracle.

  | File | Rows | Use |
  |---|---|---|
  | `jobs-v1.4.jsonl` | 2,202 (the 1,845 rows of `jobs-v1.3.jsonl` + 357 rows of the `kontrol-ES384` arm; generator `make_jobs_v14.py`) | **Measurement.** Run only after the freeze, by `run_measurement.sh` |
  | `jobs-prefreeze-v1.4.jsonl` | 40 (V± and CMP00/CMP01 under `GEC` in the five arms of v1.4) | Pre-freeze validity gate (done; `outputs/prefreeze-v1.4/`) |
  | `jobs-prefreeze-v1.3.jsonl` | 32 (the same in the four arms of v1.3) | Pre-freeze validity gate (done; `outputs/prefreeze-v1.3/`) |
  | `vpm-sdjwt/jobs_prefreeze_V_sdjwt.jsonl` + `vpm-sdjwt/vectors/` | 16 SD-JWT-format vectors outside the battery | SD-JWT-format validity gate, Decision D1 (done; `outputs/prefreeze-sdjwt/`) |
  | `jobs-v1.3.jsonl` | 1,845 | Base of `jobs-v1.4.jsonl`; not run on its own |

- **Policy configuration:** the field `politika` of the job row (GEC, IZIN-A, IZIN-AX, L4, L4-S, L4-Y, P0, P1, L4-YOL,
  GEC@-19, L4@-19). Their meaning is in `experiment/oracle/oracle-A/METHOD.md` §2 and contract §2.2. A = ES256; X
  comes from the arm: `kontrol-EdDSA` → EdDSA, `kontrol-Ed25519` → Ed25519, `kontrol-ES384` → ES384 (Amendment 10),
  `tedavi-ML-DSA-65` → ML-DSA-65, `tedavi-composite` → ML-DSA-65-ES256. R = {X} (L4 family); W as in contract §2.2.
- **Per-target settings, fixed before the measurement:** control-arm label (`CONTROL-LABELS.csv`: first label in the
  order EdDSA, Ed25519, ES384 whose validity gate the target passes; EdDSA 17, ES384 13, none 1) and treatment class
  (`TK-ASSIGNMENT.csv`: TK1 or TK3 per arm, primary and sensitivity; TK2 is out of scope). The runner runs every job
  row for every target; the analysis selects the rows of the target's control label.

## 2. Call

**Measurement (after the freeze only):**

```
bash experiment/runs/run_measurement.sh [target ...]     # default: every target in CONTROL-LABELS.csv
```

The script first checks `docs/preregistration/FREEZE-SHA256SUMS` with `sha256sum -c` (battery, oracle, job list,
adapter sources, scripts). A missing manifest or any mismatch stops the run. It then runs `jobs-v1.4.jsonl` for every
target three times (r1, r2, r3), each run in a fresh container, and writes
`outputs/measurement/<target>.<r1|r2|r3>.jsonl` and `outputs/measurement/run-log.txt`.

**Single call** (used by the measurement script and for the pre-freeze gates):

```
bash experiment/runs/adapters/_tools/run.sh <job file> <run label> <output folder> [target ...]
```

It starts, per target, the image `a10-<target in lower case>:1` as

```
docker run --rm --network none --memory=4g \
    -v <vectors>:/v:ro -v <vectors/v1.4>:/v/v1.3:ro -v <keys>:/anahtarlar:ro \
    -v <experiment/runs>:/is:ro -v <output folder>:/c -e KOSU=<run label> \
    a10-<target>:1 <adapter call>
```

- **Two calling conventions** (Decision D7): adapters with their own folder and `Dockerfile` take
  `adaptor /is/<job file> /c/<target>.<run>.jsonl`; the shared adapters (`_py`, `_node`, `_go`, `_jvm`, `_kt`, `_rs`)
  take `<target> /is/<job file> /c/<target>.<run>.jsonl <run>`. `_tools/run.sh` chooses the convention. With the run label
  `oncesi` (pre-freeze) the output file is `<target>.jsonl`.
- `EXTRA_MOUNT` (optional) adds one read-only mount, e.g. the SD-JWT-format gate vectors at `/v/vpm-sdjwt`.
- Network off (`--network none`); everything is installed when the image is built (`adapters/_tools/build_all.sh`,
  which calls `_tools/build_shared.sh` and `_rs/build.sh` and builds every per-target `Dockerfile`).
- The adapter processes all job rows in sequence in one process. Where the adapter implements it, there is a limit of
  60 s per vector; when it is exceeded, `zaman-asimi` (timeout) is written. `_tools/run.sh` stops a run after 30 min per
  target (`C3_TARGET_TIMEOUT`, seconds, default 1800); rows that the stopped run did not write are missing in that
  run, so their cells are unstable and become `indeterminate`.
- For a format that cannot be represented with the target's documented API, `sonuc_ham = uygulanamaz` and
  `hata_sinifi = bicim-desteklenmiyor` (B6) are written. This decision is made **in advance** by API review and written
  into the target's `MAPPING.md`.
- For a policy that the API cannot express, `sonuc_ham = ifade-edilemedi` is written (example: the R set, L4m on a
  compact-only target).
- Documented caller patterns that count as the library's verification path (Decision D5): COSE-035, SDJWT-010,
  SDJWT-015, SDJWT-025; details in pre-registration Section 7.19 and in the targets' `MAPPING.md`.

## 3. Output (per row; a subset of contract §3, mandatory fields)

`hedef_id`, `hedef_surum`, `adaptor_sha256`, `kosu`, `vektor_id`, `politika`, `kol`, `sonuc_ham` (kabul | red |
istisna | zaman-asimi | cokme | uygulanamaz | ifade-edilemedi), `hata_sinifi` (closed list of contract §3.2, or null),
`hata_ozeti` (first 200 characters), `dogrulanan_algoritmalar` (if the library can show them; otherwise []),
`api_yolu`, `sure_ms`.

The adapter reports what the library did; it does not decide. The mapping to the decision values (accept-hybrid /
accept-classical / reject / indeterminate, and `uygulanamaz`, not compared) is made by the analysis script
`analysis/analyze_c3.py`, frozen before any measurement. Its inputs are `sonuc_ham`, the algorithms of the vector,
`dogrulanan_algoritmalar` and the TK assignment; it takes the stable decision of r1–r3 and compares it with the merged
oracle `experiment/oracle/merged/decisions_v14.tsv` (pre-registration Sections 7.9 and 7.19).

(Field names and values are explained in `docs/DATA-DICTIONARY.md`.)

## 4. Target folder (`experiment/runs/adapters/<target>/`)

- `Dockerfile`: `FROM pq-a09-env-<language>:1.0`. The target is installed with the same version or commit as in the
  installation record in `experiment/environments/targets/<target>/`.
- adapter source.
- `MAPPING.md`: policy → API call mapping, B6 decisions, exception → `hata_sinifi` mapping.
- `evidence/api-scan.txt`: the scan command of contract §5.1 and its output.
- `NOTES.md`: treatment class with reason, validity-gate result, issues.

**Shared adapters.** The 15 targets served by `_py`, `_node`, `_go`, `_jvm` and `_kt` (list in `adapters/README.md`)
have a target folder with `evidence/` only. Their policy → API mapping, the B6 format decisions (`formats()` of the
target's entry) and the exception mapping are fixed in the target's entry of the shared adapter source, which is part
of the freeze package; their treatment class is in `TK-ASSIGNMENT.csv` and their validity-gate result in
`outputs/prefreeze-*/GATE-SUMMARY*.csv`. The four `_rs` targets have `MAPPING.md` and `NOTES.md` in
`_rs/<target>/`.

## 5. Decisions (maintainers)

- **TK2 out of scope** (2026-10-01). A target without native ML-DSA support is TK3. No hypothesis relies on TK2; T2
  covers TK1 targets only and is descriptive (Amendment 11). Recorded as a deviation in the pre-registration
  (Section 13.1).
- **Composite arm:** no target supports composite -04 natively, so every target is TK3 in that arm.
- **Repetition:** 3 runs (r1–r3), each in a fresh container (contract §4). A cell whose decision differs across the
  three runs is `indeterminate`.
- **Order of work:** the measurement job list is run only after the freeze; until then only the pre-freeze gates of
  Section 1 were run. Decisions D1–D7 (SD-JWT-format gate, JOSE-102 treatment class, wolfCOSE build flag, control
  label order, documented caller patterns, calling conventions) are in `DECISIONS-PREFREEZE.md`.
