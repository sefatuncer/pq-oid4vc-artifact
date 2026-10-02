# Path history

The working repository used Turkish folder names. The renames happened in two rounds:

1. For the first release the top two folder levels were renamed to English and the hand-written
   documents were translated and renamed (sections 1 and 2 below).
2. On 03.10.2026 the Turkish folder and file names under `experiment/` and `tools/` were renamed
   to English as well (section 2b). [`PATHS.tsv`](PATHS.tsv) lists every folder and file of this
   round, one per row, old path → new path (paths in the layout of round 1).

The Turkish names that remain are explained in [`GLOSSARY.md`](GLOSSARY.md).

**Recorded outputs keep the paths that were valid when they were produced.** Logs, manifests,
hash lists, result tables, JSON records and raw tool output were not rewritten. When such a file
mentions `deney/kosum/...`, `model/tamarin/...` or `experiment/vector-generator/vektorler/...`, read
it with the tables below and with `PATHS.tsv`. `tools/verify_anchors.py` resolves recorded paths in
the same way.

## 1. Folder renames

| Old path | Current path |
|---|---|
| `01-korpus/` | `spec-corpus/` |
| `02-izlenebilirlik/` | `traceability/` |
| `03-tehdit-modeli/` | `threat-model/` |
| `arac/` | `tools/` |
| `arac/test/` | `tools/regression-tests/` |
| `deney/` | `experiment/` |
| `deney/envanter/` | `experiment/inventory/` |
| `deney/imzalayici/` | `experiment/signer/` |
| `deney/istatistik/` | `experiment/statistics/` |
| `deney/kosum/` | `experiment/runs/` |
| `deney/ortam/` | `experiment/environments/` |
| `deney/uretec/` | `experiment/vector-generator/` |
| `deney/oracle/` | `experiment/oracle/` (unchanged name) |
| `veri/` | `data/` |
| `model/` | `models/` |
| `model/bilinen-cevap/` | `models/known-answer-tests/` |
| `model/karsilastirma/` | `models/comparison/` |
| `model/mekanizma/` | `models/mechanisms/` |
| `model/ornekleme/` | `models/sampling/` |
| `model/asp/ornekleme/` | `models/asp/sampling/` |
| `model/asp/`, `model/tamarin/` | `models/asp/`, `models/tamarin/` |

In round 1 only the top-level `veri/` became `data/`; the folder
`experiment/statistics/sentetik-testler/veri/` became `experiment/statistics/synthetic-tests/data/` in
round 2.

## 2. Document renames

Hand-written Markdown documents were translated to English and renamed. References in code
comments and in other documents were updated; recorded outputs still use the old names.

| Old name | Current name |
|---|---|
| `spec-corpus/BULGULAR-VE-PLAN-ETKISI.md` | `spec-corpus/FINDINGS-AND-PLAN-IMPACT.md` |
| `traceability/OZET.md` | `traceability/SUMMARY.md` |
| `threat-model/TEHDIT-MODELI.md` | `threat-model/THREAT-MODEL.md` |
| `experiment/environments/DEGISIKLIKLER.md` | `experiment/environments/TARGET-CHANGES.md` |
| `experiment/environments/DURUM.md` | `experiment/environments/STATUS.md` |
| `experiment/environments/IMAJLAR.md` | `experiment/environments/IMAGES.md` |
| `experiment/environments/KARAR-NOTLARI.md` | `experiment/environments/DECISION-NOTES.md` |
| `experiment/inventory/KARAR-NOTLARI.md` | `experiment/inventory/DECISION-NOTES.md` |
| `experiment/inventory/KRITERLER-TASLAK.md` | `experiment/inventory/CRITERIA-DRAFT.md` |
| `experiment/inventory/OZET.md` | `experiment/inventory/SUMMARY.md` |
| `experiment/oracle/AB-KARSILASTIRMA.md` | `experiment/oracle/AB-COMPARISON.md` |
| `experiment/oracle/oracle-A/BELIRSIZ.md` | `experiment/oracle/oracle-A/UNDETERMINED.md` |
| `experiment/oracle/oracle-A/KARAR-NOTLARI.md` | `experiment/oracle/oracle-A/DECISION-NOTES.md` |
| `experiment/oracle/oracle-A/L4-TURETME.md` | `experiment/oracle/oracle-A/L4-DERIVATION.md` |
| `experiment/oracle/oracle-A/YONTEM.md` | `experiment/oracle/oracle-A/METHOD.md` |
| `experiment/oracle/oracle-A/adaptor-sozlesme.md` | `experiment/oracle/oracle-A/adapter-contract.md` |
| `experiment/oracle/oracle-A/ayrisma-dedektoru.md` | `experiment/oracle/oracle-A/divergence-detector.md` |
| `experiment/oracle/oracle-B/BELIRSIZ.md` | `experiment/oracle/oracle-B/UNDETERMINED.md` |
| `experiment/oracle/oracle-B/ERISIM-KAYDI.md` | `experiment/oracle/oracle-B/ACCESS-LOG.md` |
| `experiment/oracle/oracle-B/KARAR-NOTLARI.md` | `experiment/oracle/oracle-B/DECISION-NOTES.md` |
| `experiment/oracle/oracle-B/L4-TURETME-B.md` | `experiment/oracle/oracle-B/L4-DERIVATION-B.md` |
| `experiment/oracle/oracle-B/YONTEM.md` | `experiment/oracle/oracle-B/METHOD.md` |
| `experiment/signer/KARAR-NOTLARI.md` | `experiment/signer/DECISION-NOTES.md` |
| `experiment/statistics/DONDURMA-GIRDISI.md` | `experiment/statistics/FREEZE-INPUT.md` |
| `experiment/statistics/KARAR-NOTLARI.md` | `experiment/statistics/DECISION-NOTES.md` |
| `experiment/statistics/SEMA.md` | `experiment/statistics/SCHEMA.md` |
| `experiment/statistics/kaynak/NEWCOMBE-KAYNAK.md` | `experiment/statistics/sources/NEWCOMBE-SOURCE.md` |
| `models/asp/KARAR-NOTLARI.md` | `models/asp/DECISION-NOTES.md` |
| `models/asp/RAPOR.md` | `models/asp/REPORT.md` |
| `models/asp/sampling/SEMA.md` | `models/asp/sampling/SCHEMA.md` |
| `models/known-answer-tests/ADIM06-RAPOR.md` | `models/known-answer-tests/STEP06-REPORT.md` |
| `models/known-answer-tests/ESLEME.md` | `models/known-answer-tests/MAPPING.md` |
| `models/known-answer-tests/SONUC.md` | `models/known-answer-tests/RESULTS.md` |
| `models/known-answer-tests/kor-beklenen/BELIRSIZ.md` | `models/known-answer-tests/kor-beklenen/UNDETERMINED.md` |
| `models/known-answer-tests/kor-beklenen/ERISIM-KAYDI.md` | `models/known-answer-tests/kor-beklenen/ACCESS-LOG.md` |
| `models/known-answer-tests/kor-beklenen/TURETME.md` | `models/known-answer-tests/kor-beklenen/DERIVATION.md` |
| `models/known-answer-tests/kor-beklenen/GIRDI/KAT-KOR-GIRDI.md` | `models/known-answer-tests/kor-beklenen/GIRDI/KAT-BLIND-INPUT.md` |
| `models/known-answer-tests/kor-beklenen/GIRDI/OKUBENI.md` | `models/known-answer-tests/kor-beklenen/GIRDI/README.md` |
| `models/known-answer-tests/nsurum/NSURUM-KARSILASTIRMA.md` | `models/known-answer-tests/nsurum/N-VERSION-COMPARISON.md` |
| `models/mechanisms/ADIM07-RAPOR.md` | `models/mechanisms/STEP07-REPORT.md` |
| `models/mechanisms/KARAR-NOTLARI.md` | `models/mechanisms/DECISION-NOTES.md` |
| `models/mechanisms/M-f-TANIM.md` | `models/mechanisms/M-f-DEFINITION.md` |
| `models/mechanisms/ON-KAYIT-GEREKCE.md` | `models/mechanisms/PRE-REGISTRATION-RATIONALE.md` |
| `models/sampling/secim/OKUBENI.md` | `models/sampling/secim/README.md` |
| `models/tamarin/KARAR-NOTLARI.md` | `models/tamarin/DECISION-NOTES.md` |
| `models/tamarin/RAPOR.md` | `models/tamarin/REPORT.md` |

Documents in the working history were also called `NOTLAR.md` ("notes"); they are the files now
named `DECISION-NOTES.md`.

### Run area (`experiment/runs/`)

| Old name | Current name |
|---|---|
| `experiment/runs/KOSUCU.md` | `experiment/runs/RUNNER.md` |
| `experiment/runs/adaptorler/` | `experiment/runs/adapters/` |
| `experiment/runs/adaptorler/_belge/` | `experiment/runs/adapters/_tools/` |
| `adaptorler/<target>/ESLEME.md` | `adapters/<target>/MAPPING.md` |
| `adaptorler/<target>/NOTLAR.md` | `adapters/<target>/NOTES.md` |
| `adaptorler/<target>/kanit/` | `adapters/<target>/evidence/` |
| `experiment/runs/kosu/` | `experiment/runs/outputs/` |
| `experiment/runs/isler.jsonl`, `isler_dondurma_oncesi_V.jsonl` | `experiment/runs/jobs-v1.3.jsonl`, `jobs-prefreeze-v1.3.jsonl` (and the v1.4 job lists) |

### Generated Markdown files that keep their content

The following Markdown files are written by scripts. Their content was not translated, so that
re-running the scripts reproduces them byte for byte and so that the scripts that read them keep
working. Their meaning is described in the README of their folder.

| File | Written by |
|---|---|
| `experiment/vector-generator/BATTERY-MAPPING.md` (old `BATARYA-ESLEME.md`; battery mapping; parsed by the oracles and by T11; SHA-256 pinned in `oracle-A/make_decisions.py` and in the pre-registration) | `generator/esleme.py` |
| `experiment/vector-generator/results/BATTERY-MAPPING_v1.2.md` | `generator/esleme.py` (v1.2 copy) |
| `experiment/statistics/results/*/sonuc.md` | `c3istat analiz` |
| `models/asp/sorgular/sonuc/analiz/tablolar.md` | `models/asp/sorgular/analiz.py` |
| `models/mechanisms/sonuc/tablolar.md` | `models/mechanisms/betik/tablolar.py` |
| `models/known-answer-tests/*/sonuc*/KAT_OZET.md` | `degerlendir.py`, `degerlendir_v2.py` |
| `models/known-answer-tests/dnssec/sonuc_v2/YANYANA.md` | `dnssec/yanyana_v1_v2.py` |
| `traceability/kapsama_tablolari.md` | `traceability/ozet_tablolari.py` |

## 2b. Renames of 03.10.2026 (`experiment/` and `tools/`)

All rows are in [`PATHS.tsv`](PATHS.tsv): 80 folders and 460 files. A folder row applies to
everything below it. The main folders:

| Old path | Current path |
|---|---|
| `experiment/vector-generator/vektorler/`, `anahtarlar/`, `uretec/`, `testler/`, `sonuclar/` | `experiment/vector-generator/vectors/`, `keys/`, `generator/`, `tests/`, `results/` |
| `experiment/signer/servis/` (`ornekler/`), `testler/`, `dis-vektorler/`, `sonuclar/`, `kayit/` | `experiment/signer/service/` (`examples/`), `tests/`, `external-vectors/`, `results/`, `records/` |
| `experiment/statistics/betikler/`, `sentetik-testler/` (`veri/`), `sonuclar/`, `kayit/`, `kaynak/` | `experiment/statistics/scripts/`, `synthetic-tests/` (`data/`), `results/`, `records/`, `sources/` |
| `experiment/statistics/sonuclar/ornek_girdi/`, `ornek_analiz1/`, `ornek_analiz2/`, `ornek_analiz_csv/` | `experiment/statistics/results/sample_input/`, `sample_analysis1/`, `sample_analysis2/`, `sample_analysis_csv/` |
| `experiment/oracle/birlesik/` | `experiment/oracle/merged/` |
| `experiment/environments/betikler/` (`konteyner/`), `hedefler/`, `imajlar/`, `kayit/`, `loglar/` | `experiment/environments/scripts/` (`container/`), `targets/`, `images/`, `records/`, `logs/` |
| `experiment/environments/hedefler/<id>/cikti/`, `cikti-maven/`; `hedefler/_bilgi-<id>-…/` | `experiment/environments/targets/<id>/output/`, `output-maven/`; `targets/_info-<id>-…/` |
| `tools/regression-tests/sonuc/` | `tools/regression-tests/results/` |

Files that were renamed: run and build scripts (`tumunu_calistir.sh` → `run_all.sh`,
`adapters/_tools/kur_hepsi.sh` → `build_all.sh`, `kur.sh` → `build_shared.sh`, `kos.sh` → `run.sh`,
`environments/betikler/kos.sh` → `scripts/run_target.sh`, `targets/<id>/kur.sh` → `install.sh`, ...),
entry scripts (`turet_v13.py` → `derive_v13.py`, `karar_uret.py` → `make_decisions.py`,
`topla.py` → `collect.py`, `t10_oz_dogrulama.py` → `t10_self_verification.py`, ...), hand-made inputs
(`CERCEVE.csv` → `FRAME.csv`, `elle_bayraklar.csv` → `manual_flags.csv`, ...) and the outputs that
these scripts write (`karar_v14.tsv` → `decisions_v14.tsv`, `OZET.json` → `SUMMARY.json`,
`derleme-sonuc.csv` → `build-results.csv`, `<id>.kosu.json` → `<id>.run.json`, `sonuc.tsv` →
`result.tsv`, ...). The scripts were changed only where they name a path; recorded outputs and the
SHA-256 records were not edited. Recorded test results keep their old test names in their `test`
field (for example `t10_oz_dogrulama_v1.3` in `results/t10_self_verification_v1.3.json`).

Names that were **not** changed:

- the vector and key files inside `vectors/v1*/` and `keys/v1*/` (`acik-jwks.json`, `ozel/`,
  `b-uyumlu/`, ...): they are named in the anchored manifests;
- manifest values such as `anahtarlar/v1/acik-jwks.json` and the keys `vektorler/v1/MANIFEST.json`
  in the manifests: they are recorded content, and they are paths inside the run containers (the
  mount point `/anahtarlar` is `experiment/vector-generator/keys/`). The generator still writes them
  unchanged, so regeneration stays byte-identical;
- Python module names (`c3istat` and its modules, the modules of `generator/` such as
  `vektorler.py` and `esleme.py`, `pqjose`, `pqdogrula`, the test helpers `ortak.py`/`_ortak.py` and the
  statistics test modules `test_*.py`);
- adapter sources (`adaptor.*`, `Adaptor.*`, `ortak.*`, `Ortak.*`, `kopru.c`): their file names enter
  `adaptor_sha256`, which every output row records;
- Java and C# type and project names (`KontrolYukle.java`, `Yetenek.java`, `Yetenek.csproj`) and the
  generated project `Deneme.csproj` in `targets/<id>/output/`;
- container mount points (`/v`, `/anahtarlar`, `/is`, `/c`, `/a`, `/w`, `/b`, `/girdi`, `/cikti`, `/work`,
  `/korpus`, `/onkayit`) and image names (`pq-a09-*`, `a10-*`);
- the analysis outputs of `c3istat` (`sonuc.json`, `sonuc.md`, `karsilastirma.json`);
- the run label `oncesi` (pre-freeze) and all data fields and values;
- the folders of `models/`, `archive/`, `spec-corpus/`, `traceability/`, `threat-model/` and `data/`;
- the local cache folder `experiment/inventory/onbellek/` and the download folders `tools/*/indir/`
  (not in the repository).

**Image layouts.** The paths inside the images built from this repository follow the folder names:
`/opt/pq/{pqjose,service,tests,external-vectors}` (signer), `/opt/vector-generator/{generator,tests}`
(generator), `/opt/c3istat/{c3istat,synthetic-tests}` (statistics), `/opt/pq/capability` (.NET
environment). Images built before 03.10.2026 have `/opt/pq/servis`, `/opt/pq/testler`,
`/opt/pq/dis-vektorler`, `/opt/uretec/uretec`, `/opt/uretec/testler`, `/opt/c3istat/sentetik-testler` and
`/opt/pq/yetenek`; the image ids recorded in the READMEs are those builds.

## 3. Paths that appear in records but are not part of this release

| Path | What it was |
|---|---|
| `00-on-kayit/ON-KAYIT-TASLAK.md` | The pre-registration draft (PR). Scripts that parse it (`oracle-A/make_decisions.py`, `oracle-B/derive_decisions.py`, `vector-generator/generator/esleme.py`, `vector-generator/tests/t11_mapping_audit.py`) expect it at this path or take it as an argument |
| `spec-corpus/kaynak/`, `spec-corpus/metin/` (old `01-korpus/kaynak/`, `01-korpus/metin/`) | Downloaded specification files and their extracted text. Not redistributed; `spec-corpus/korpus_indir.py` downloads them again and `korpus_dogrula.py` checks them against `MANIFEST.csv` |
| `referans/` | Read-only copies used during the study (design documents, the design-stage pilots, earlier corpus copies) |
| `literatur/` | Literature notes and the known-answer-test specification `KAT-SPEC.md` |
| `gozden-gecirme/` | End-of-step review notes |
| `IS-PLANI.md` | The internal work plan |
| `tools/*/indir/` | Downloaded tool binaries (pinned by SHA-256 in the Dockerfiles). The folder name was kept: it is not part of the repository and the Dockerfiles copy from it |
| `/c/Users/.../PQ-OID4VC/model/...` | Absolute paths of the working copy recorded by `sha256sum` |

## 4. Container mount points

Scripts mount folders into containers under fixed names. They appear in logs.

| Mount point | Host folder |
|---|---|
| `/work` | the folder of the running step (for example `models/asp`, `models/tamarin`) |
| `/tamarin` | `models/tamarin` |
| `/izlenebilirlik` | `traceability` |
| `/veri` | `data` (old `veri/`) |
| `/referans` | `referans/` (not included) |
| `/korpus` | `spec-corpus/metin` |
| `/onkayit` | folder that holds the pre-registration draft |
| `/nsurum` | `models/known-answer-tests/nsurum` |
| `/v`, `/anahtarlar`, `/is`, `/c` | C3 runs: `experiment/vector-generator/vectors` (battery at `/v/v1.3`), `experiment/vector-generator/keys`, `experiment/runs` (job list), output folder |
| `/girdi`, `/cikti` | statistics runs: input, output |
| `/w`, `/b` | build pre-test of the environments: `experiment/environments/targets/<id>`, `experiment/environments/scripts/container` |
