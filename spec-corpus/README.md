# spec-corpus — specification corpus (Step 1)

**What it does.** Pins the 58 normative and guidance documents the study relies on (OpenID4VC,
SD-JWT VC, JOSE/COSE, ARF v3.0.0, ETSI trusted-list and certificate specifications, EU
post-quantum guidance, DNSSEC sources for the known-answer tests). For every document the manifest
records the version, URL, access time and the SHA-256 of both the downloaded file and the extracted
text. The texts themselves are not redistributed.

**Used by.** `traceability/` (every quote is checked against `metin/<id>.txt`), the two oracles in
`experiment/oracle/` (clauses are cited with file and line), the vector self-verification
(`experiment/vector-generator/tests/t10_self_verification.py`, corpus mounted read-only), the signer's
external test vectors (`experiment/signer/tests/external_vectors.py`) and the known-answer tests.

## Files

| File | Content |
|---|---|
| `korpus_kaynaklari.json` | Source list: id, group, title, version and date, status, URL, file name, type, note (58 documents) |
| `MANIFEST.csv` | The manifest: `id, baslik, surum_tarih, durum, url, erisim_utc, sha256_orijinal, sha256_metin, boyut_bayt, not` (58 rows) |
| `korpus_kaynaklari.adim1.json`, `MANIFEST.adim1.csv` | The Step 1 versions of the two files (51 documents), kept for traceability |
| `indirme_kaydi.json` | Download log per document |
| `korpus_indir.py` | Downloads the documents into `kaynak/`, converts them to UTF-8 text in `metin/` and writes `MANIFEST.csv` |
| `korpus_dogrula.py` → `korpus_dogrulama.txt` | Recomputes every SHA-256 and size and checks it against the manifest |
| `korpus_on_karsilastir.py` → `korpus_on_karsilastirma.csv/.txt` | Compares six documents with copies obtained earlier in the study (folder `referans/korpus_on/`, not included) |
| `terim_sayimi.py` → `terim_sayimi.csv/.txt` | Counts post-quantum related terms (quantum, ML-DSA, hybrid, composite, downgrade, …) per document |
| `FINDINGS-AND-PLAN-IMPACT.md` | Step 1 findings: new versions after 23.09.2026, findings that confirm or contradict the design assumptions, and their impact on the later steps |

Not included (see `.gitignore`): `kaynak/` (downloaded originals) and `metin/` (extracted text).

## How to run

```
python spec-corpus/korpus_indir.py                 # download missing files, rebuild metin/ and MANIFEST.csv
python spec-corpus/korpus_indir.py --sadece-metin  # no download; rebuild metin/ and MANIFEST.csv only
python spec-corpus/korpus_indir.py --yeniden ID…   # download the given ids again
python spec-corpus/korpus_dogrula.py               # verify against MANIFEST.csv; exit code 1 on mismatch
python spec-corpus/terim_sayimi.py
```

Requests are anonymous: the only HTTP header is a generic User-Agent. A document behind an access
restriction is recorded as not accessible; the restriction is not bypassed. Text extraction uses
`html.parser`, `pdftotext -layout` or `pypdf`, as recorded per document in the `not` column.

## Results (from the files in this folder)

- `korpus_dogrulama.txt` (2026-09-24T09:16:03Z): 58 manifest rows, 0 errors, **58/58 verified**.
- `korpus_on_karsilastirma.txt`: three documents are byte-identical to the earlier copies; for the
  three PDF-derived ones the earlier text was reproduced from the fresh PDF (byte-identical twice,
  text-identical once).
- `terim_sayimi.txt`: the ARF v3.0.0 documents (13 files) contain no occurrence of "quantum" or
  "ML-DSA" and 8 of "hybrid"; ETSI TS 119 312 is the only ETSI document that names post-quantum
  algorithms (ML-DSA 72, SLH-DSA 95).

## Document groups (`grup`)

`OIDF`, `IETF-OAuth`, `IETF-JOSE`, `IETF-COSE`, `IETF-PQUIP`, `IETF-LAMPS`, `IETF` (other IETF),
`ARF` (EUDI Architecture and Reference Framework v3.0.0), `ETSI`, `AB-rehber` (EU guidance; *AB* =
European Union, *rehber* = guidance), `BCT` (sources of the known-answer tests; *bilinen-cevap
testi*), `Akademik` (academic). Status values (`durum`): `RFC`, `final`, `taslak` (draft), `rehber`
(guidance).

## Turkish names in this folder

`korpus` corpus · `kaynaklari` sources · `indir` download · `indirme_kaydi` download log ·
`dogrula`/`dogrulama` verify/verification · `on` earlier (copies obtained before Step 1) ·
`karsilastir`/`karsilastirma` compare/comparison · `terim_sayimi` term count · `adim1` Step 1 ·
`kaynak/` downloaded originals · `metin/` extracted text.
