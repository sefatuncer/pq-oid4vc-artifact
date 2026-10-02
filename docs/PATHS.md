# Path history

The working repository used Turkish folder names. For this release the top two folder levels were
renamed to English and the hand-written documents were translated and renamed. Deeper Turkish
folder and file names were kept, because they are part of recorded paths (see
[`GLOSSARY.md`](GLOSSARY.md) for their meaning).

**Recorded outputs keep the paths that were valid when they were produced.** Logs, manifests,
hash lists, result tables, JSON records and raw tool output were not rewritten. When such a file
mentions `deney/kosum/...` or `model/tamarin/...`, read it with the tables below.

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

Only the top-level `veri/` became `data/`. The folder `experiment/statistics/sentetik-testler/veri/`
kept its name.

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
| `experiment/statistics/kaynak/NEWCOMBE-KAYNAK.md` | `experiment/statistics/kaynak/NEWCOMBE-SOURCE.md` |
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

### Generated Markdown files that keep their names

The following Markdown files are written by scripts. They were not translated or renamed, so that
re-running the scripts reproduces them byte for byte and so that the scripts that read them keep
working. Their meaning is described in the README of their folder.

| File | Written by |
|---|---|
| `experiment/vector-generator/BATARYA-ESLEME.md` (battery mapping; parsed by the oracles and by T11; SHA-256 pinned in `oracle-A/karar_uret.py`) | `uretec/esleme.py` |
| `experiment/vector-generator/sonuclar/BATARYA-ESLEME_v1.2.md` | `uretec/esleme.py` (v1.2 copy) |
| `experiment/statistics/sonuclar/*/sonuc.md` | `c3istat analiz` |
| `models/asp/sorgular/sonuc/analiz/tablolar.md` | `models/asp/sorgular/analiz.py` |
| `models/mechanisms/sonuc/tablolar.md` | `models/mechanisms/betik/tablolar.py` |
| `models/known-answer-tests/*/sonuc*/KAT_OZET.md` | `degerlendir.py`, `degerlendir_v2.py` |
| `models/known-answer-tests/dnssec/sonuc_v2/YANYANA.md` | `dnssec/yanyana_v1_v2.py` |
| `traceability/kapsama_tablolari.md` | `traceability/ozet_tablolari.py` |

## 3. Paths that appear in records but are not part of this release

| Path | What it was |
|---|---|
| `00-on-kayit/ON-KAYIT-TASLAK.md` | The pre-registration draft (PR). Scripts that parse it (`oracle-A/karar_uret.py`, `oracle-B/turet_karar.py`, `vector-generator/uretec/esleme.py`, `testler/t11_esleme_denetim.py`) expect it at this path or take it as an argument |
| `spec-corpus/kaynak/`, `spec-corpus/metin/` (old `01-korpus/kaynak/`, `01-korpus/metin/`) | Downloaded specification files and their extracted text. Not redistributed; `spec-corpus/korpus_indir.py` downloads them again and `korpus_dogrula.py` checks them against `MANIFEST.csv` |
| `referans/` | Read-only copies used during the study (design documents, the design-stage pilots, earlier corpus copies) |
| `literatur/` | Literature notes and the known-answer-test specification `KAT-SPEC.md` |
| `gozden-gecirme/` | End-of-step review notes |
| `IS-PLANI.md` | The internal work plan |
| `tools/*/indir/` | Downloaded tool binaries (pinned by SHA-256 in the Dockerfiles) |
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
| `/v`, `/anahtarlar`, `/is`, `/c` | C3 runs: vector set, keys, job list, output |
| `/girdi`, `/cikti` | statistics runs: input, output |
