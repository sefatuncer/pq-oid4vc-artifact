# experiment/environments — language environments and build pre-test (Step 9, task 4a)

**What it does.** Pins one official, digest-pinned build image per language and checks, for every
selected target library, that the pinned version installs or builds and that its module can be
imported or linked. This is a build pre-test only: no test vector is run and no signature is
verified. The images are the base of the C3 adapters (`experiment/runs/adapters/<target>/Dockerfile`
starts `FROM pq-a09-env-<language>:1.0`).

**Inputs.** The target list from `experiment/inventory/` (`SECIM.csv`, `CERCEVE.csv`,
`topla_kayit.json`; selection E2 with reserves).

**Outputs.** `derleme-sonuc.csv` (build results), per-target records in `hedefler/<id>/cikti/` and
`kayit/`, build logs in `loglar/`.

## Files

| Path | Content |
|---|---|
| `imajlar/<language>/Dockerfile` | Language images `pq-a09-env-<language>:1.0` (c, dart, dotnet, elixir, go, jvm, node, php, python, ruby, rust, swift); base images pinned by digest; no OS package repository used. `jvm/Yetenek.java` and `dotnet/yetenek/` are capability probes (which post-quantum algorithm names the runtime registers) |
| `betikler/kos.sh` | Runs the pre-test of one target in a container (`--rm`, `--memory=6g`, timeout; mounts only `hedefler/<id>` and `betikler/konteyner`) |
| `betikler/konteyner/*.sh`, `KontrolYukle.java` | In-container installers per ecosystem (npm, pip, go, maven, gradle-lib, nuget, composer, gem, cargo, swiftpm) and shared helpers (`ortak.sh`); they write the key/value record `cikti/sonuc.tsv` |
| `hedefler/<id>/kur.sh` (`kur-maven.sh`, `ek.sh`) | Install script of one target (package, version, extras) |
| `hedefler/<id>/ice_aktar.*` | Import smoke test: loads the module and lists API symbols, calls nothing |
| `hedefler/<id>/cikti*/` | Third-party build output: lock files, dependency lists, POMs, the import output and `sonuc.tsv`. Kept unchanged as records |
| `hedefler/_bilgi-*` | Informational builds outside the sample (for example the HEAD commit instead of the release, or an optional feature) |
| `betikler/hedef_listesi.py` | Target list (selected + reserves) with the reserve type re-derived from the selection rule → `kayit/hedef_listesi.csv` |
| `betikler/etiket_coz.py` | Resolves release tags to commits with anonymous `git ls-remote` → `kayit/surum_commit.csv`, `kayit/lsremote/` |
| `betikler/surum_dayanak.py`, `betikler/surum_ozet.py` | Effect of version pinning: does the evidence file of the inventory exist at the release tag? Installed commit vs. frame HEAD → `kayit/surum_dayanak.csv`, `kayit/surum_ozet.csv` |
| `betikler/topla_sonuc.py` | Builds `derleme-sonuc.csv` from the records (no number is written by hand) |
| `kayit/` | Run records (`<id>.kosu.json`, all attempts in `.kosu.jsonl`), target changes, notes, version evidence |
| `loglar/` | Build logs per target and per image |
| `_docker/` | Docker state before and after the work (images, containers, disk usage, new images) |
| `IMAGES.md` | The 12 images: base digest, tool versions, OpenSSL source, registries; OpenSSL 3.5+ requirements of the targets |
| `TARGET-CHANGES.md` | Target replacements under the replacement rule (JOSE-104 could not be built on Linux; reserves JOSE-031 and JOSE-017) |
| `DECISION-NOTES.md` | Notes and decisions: open items K1–K6, installation facts relevant to the treatment class and L4 form, licences, limitations |
| `STATUS.md` | Interim status record of 25.09.2026 |
| `SHA256SUMS` | Integrity list of this folder |

## How to run

```
docker build -t pq-a09-env-python:1.0 experiment/environments/imajlar/python    # one image per language
bash experiment/environments/betikler/kos.sh JOSE-083 pq-a09-env-python:1.0
python experiment/environments/betikler/topla_sonuc.py
```

`betikler/kos.sh` contains the absolute path of the working copy (`ORTAM`, `ORTAM_WIN`); adjust it
before running elsewhere.

## Results (from `derleme-sonuc.csv`)

- 34 targets of the sample (18 JOSE, 8 SD-JWT, 5 COSE, 3 reference verifiers): **33 built
  successfully**, 1 failed (JOSE-104).
- The two reserve candidates for JOSE-104 (JOSE-031, JOSE-017) both built successfully.
- 12 language images; six informational builds (`_bilgi-*`).

## Turkish names in this folder

`imajlar` images · `betikler` scripts · `konteyner` container · `hedefler` targets · `kur` install ·
`ice_aktar` import · `ek` extra · `cikti` output · `_bilgi` informational · `yetenek` capability ·
`kayit` records · `loglar` logs · `derleme-sonuc` build results · `hedef_listesi` target list ·
`etiket_coz` resolve tag · `surum_dayanak` version evidence · `surum_ozet` version summary ·
`topla_sonuc` collect results · `kos` run · `ortak` common · `KontrolYukle` check-load ·
`degisiklikler` changes · `notlar` notes · `deneme` attempt · `once`/`sonra` before/after ·
`yeni_imajlar` new images. Columns and values: `docs/DATA-DICTIONARY.md` §8.
