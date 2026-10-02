# experiment/environments — language environments and build pre-test (Step 9, task 4a)

**What it does.** Pins one official, digest-pinned build image per language and checks, for every
selected target library, that the pinned version installs or builds and that its module can be
imported or linked. This is a build pre-test only: no test vector is run and no signature is
verified. The images are the base of the C3 adapters (`experiment/runs/adapters/<target>/Dockerfile`
starts `FROM pq-a09-env-<language>:1.0`).

**Inputs.** The target list from `experiment/inventory/` (`SELECTION.csv`, `FRAME.csv`,
`collect_record.json`; selection E2 with reserves).

**Outputs.** `build-results.csv` (build results), per-target records in `targets/<id>/output/` and
`records/`, build logs in `logs/`.

## Files

| Path | Content |
|---|---|
| `images/<language>/Dockerfile` | Language images `pq-a09-env-<language>:1.0` (c, dart, dotnet, elixir, go, jvm, node, php, python, ruby, rust, swift); base images pinned by digest; no OS package repository used. `jvm/Yetenek.java` and `dotnet/capability/` are capability probes (which post-quantum algorithm names the runtime registers) |
| `scripts/run_target.sh` | Runs the pre-test of one target in a container (`--rm`, `--memory=6g`, timeout; mounts only `targets/<id>` and `scripts/container`) |
| `scripts/container/*.sh`, `KontrolYukle.java` | In-container installers per ecosystem (npm, pip, go, maven, gradle-lib, nuget, composer, gem, cargo, swiftpm) and shared helpers (`common.sh`); they write the key/value record `output/result.tsv` |
| `targets/<id>/install.sh` (`install-maven.sh`, `extra.sh`) | Install script of one target (package, version, extras) |
| `targets/<id>/import_check.*` | Import smoke test: loads the module and lists API symbols, calls nothing |
| `targets/<id>/output*/` | Third-party build output: lock files, dependency lists, POMs, the import output and `result.tsv`. Kept unchanged as records |
| `targets/_info-*` | Informational builds outside the sample (for example the HEAD commit instead of the release, or an optional feature) |
| `scripts/make_target_list.py` | Target list (selected + reserves) with the reserve type re-derived from the selection rule → `records/target_list.csv` |
| `scripts/resolve_tags.py` | Resolves release tags to commits with anonymous `git ls-remote` → `records/version_commit.csv`, `records/lsremote/` |
| `scripts/version_basis.py`, `scripts/version_summary.py` | Effect of version pinning: does the evidence file of the inventory exist at the release tag? Installed commit vs. frame HEAD → `records/version_basis.csv`, `records/version_summary.csv` |
| `scripts/collect_results.py` | Builds `build-results.csv` from the records (no number is written by hand) |
| `records/` | Run records (`<id>.run.json`, all attempts in `.run.jsonl`), target changes, notes, version evidence |
| `logs/` | Build logs per target and per image |
| `_docker/` | Docker state before and after the work (images, containers, disk usage, new images) |
| `IMAGES.md` | The 12 images: base digest, tool versions, OpenSSL source, registries; OpenSSL 3.5+ requirements of the targets |
| `TARGET-CHANGES.md` | Target replacements under the replacement rule (JOSE-104 could not be built on Linux; reserves JOSE-031 and JOSE-017) |
| `DECISION-NOTES.md` | Notes and decisions: open items K1–K6, installation facts relevant to the treatment class and L4 form, licences, limitations |
| `STATUS.md` | Interim status record of 25.09.2026 |
| `SHA256SUMS` | Integrity list of this folder |

## How to run

```
docker build -t pq-a09-env-python:1.0 experiment/environments/images/python    # one image per language
bash experiment/environments/scripts/run_target.sh JOSE-083 pq-a09-env-python:1.0
python experiment/environments/scripts/collect_results.py
```

`scripts/run_target.sh` contains the absolute path of the working copy (`ORTAM`, `ORTAM_WIN`); adjust it
before running elsewhere.

## Results (from `build-results.csv`)

- 34 targets of the sample (18 JOSE, 8 SD-JWT, 5 COSE, 3 reference verifiers): **33 built
  successfully**, 1 failed (JOSE-104).
- The two reserve candidates for JOSE-104 (JOSE-031, JOSE-017) both built successfully.
- 12 language images; six informational builds (`_info-*`).

## Names in this folder

The folders and files of this step were renamed to English on 03.10.2026 (`docs/PATHS.tsv`). The
recorded logs and build outputs still use the old names, for example `hedefler/` (now `targets/`),
`cikti/` (`output/`), `kur.sh` (`install.sh`), `ice_aktar` (`import_check`), `sonuc.tsv`
(`result.tsv`), `kayit/` (`records/`), `loglar/` (`logs/`), `betikler/kos.sh`
(`scripts/run_target.sh`), `_bilgi-` (`_info-`) and `<id>.kosu.json` (`<id>.run.json`). Names kept:
`KontrolYukle.java` (Java class, "check-load"), `images/jvm/Yetenek.java` and
`images/dotnet/capability/Yetenek.csproj` ("capability"; class and project names), the generated
project `Deneme.csproj` ("trial") in `output/`. Columns and values: `docs/DATA-DICTIONARY.md` §8.
