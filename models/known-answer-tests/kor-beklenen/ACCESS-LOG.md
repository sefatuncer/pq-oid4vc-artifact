# Access log: blind derivation work (kat-kor, Step 6 task 0)

Every opened file is listed below with its path and the reason. Paths are relative to the project root (`PQ-OID4VC/`). File names are given as they were at the time; current names are added in brackets (see `docs/PATHS.md`).

| # | Path | How | Why |
|---|---|---|---|
| 1 | `models/known-answer-tests/kor-beklenen/` and `GIRDI/` | `ls` (directory listing only) | To find the output folder and the input files. No other directory under `models/` was listed |
| 2 | `models/known-answer-tests/kor-beklenen/GIRDI/OKUBENI.md` (now `GIRDI/README.md`) | full read | To learn how the input was prepared (permitted) |
| 3 | `models/known-answer-tests/kor-beklenen/GIRDI/KAT-KOR-GIRDI.md` (now `KAT-BLIND-INPUT.md`) | full read | Cell definitions, input dictionary, value dictionary (permitted) |
| 4 | Primary sources and `00-on-kayit/ON-KAYIT-TASLAK.md` | `wc -l` (line count only) | Size check. In the PR only the heading lines were scanned with `grep "^#"`, to find where §4.19 is |
| 5 | `00-on-kayit/ON-KAYIT-TASLAK.md` lines 830–840 | partial read | Only §4.19 (pass criterion). Other sections were not read |

**Files not opened:** `GIRDI/kat_redakte.py` and `GIRDI/GIRDI.sha256` appeared in the directory listing but were not opened. The redaction script is not on the permitted list; it might carry hints about the expected values.

## Session 1 (24.09.2026) continued: primary sources of KAT-1

| # | Path | How | Why |
|---|---|---|---|
| 6 | `spec-corpus/metin/RFC6840.txt` | `grep` of section headings; lines 430–709 and 985–1074 read | KAT-1: §5.4, §5.10, §5.11, §5.12, §6.2, Appendix C.2 |
| 7 | `spec-corpus/metin/RFC6781.txt` | `grep` of section headings; lines 1188–1332, 1460–1659, 1840–1989, 2133–2182 read | KAT-1: §4.1.2 Double-DS (Figure 5), §4.1.4 algorithm rollover (Figure 8), §4.2.1–4.2.3 key compromise, §4.3.4 DS signature validity period |
| 8 | `spec-corpus/metin/RFC9955.txt` | header (first 30 lines) + `grep` of section headings; lines 366–495 and 1105–1154 read | Separability and component skipping: §1.3.1, §1.3.3, §1.3.4, §6.2 |
| 9 | My own outputs: `BEKLENEN-KOR.tsv`, `TURETME.md` (now `DERIVATION.md`) | `ls`, `wc`, `tail`, `awk` | Status check after the interruption |
| 10 | Helper script `scratchpad/kat1.sh` (temporary session folder) | written and run | Only to append TSV rows with `printf`. Not a model or a tool |

## Session 2 (25.09.2026): resumed after an interruption (usage limit)

| # | Path | How | Why |
|---|---|---|---|
| 11 | My own outputs (`BEKLENEN-KOR.tsv`, `TURETME.md`, `BELIRSIZ.md`, `ERISIM-KAYDI.md`; now `DERIVATION.md`, `UNDETERMINED.md`, `ACCESS-LOG.md`) | `ls`, `wc`, `tail`, `awk` | Status check after the interruption |
| 12 | `literatur/metin/kim2026_x509_hybrid.txt` | full read (lines 1–577) | KAT-2: §II–VIII, Tables IV/V/VI/VII |
| 13 | `literatur/metin/lee2026_eprint1416.txt` | full read (lines 1–298) | KAT-2: §4.1, §4.3, §4.4, §4.5, §6 |
| 14 | `literatur/metin/han2026_nothing_breaks.txt` | first 3000 bytes + keyword `grep` (continuity, downgrade, strip, replay etc.) | Topic and relevance check. It concerns SSH/TLS key exchange and downgrades caused by deployments; it is the basis of no cell value |
| 15 | Helper script `scratchpad/kat2.sh` (temporary session folder) | written and run | Only to append TSV rows with `printf` |
| 16 | `literatur/metin/das2026_smime_eprint1374.txt` | `grep` of section headings; lines 120–235 read | KAT-3: §3 formal model, Equations (5)–(8), Proposition 1, §3.1 Stages 1–5, Table 1 |
| 17 | Helper script `scratchpad/kat3.sh` (temporary session folder) | written and run | Only to append TSV rows with `printf` |
| 18 | Helper script `scratchpad/alinti_denetle.py` (temporary session folder) | written, run with Python 3.11 | Quote audit. Reads only the 6 primary files above and my own TSV; compares text |
| 19 | `kim2026`, `das2026`, `RFC6781`, `RFC6840` | fixed-string search with `grep -n -F` | Sample check of the in-text line references in TURETME (now `DERIVATION.md`) |

## Files not opened and not read (independence statement)

None of the following was opened, listed or scanned with `grep`:
- `literatur/analiz/` (including KAT-SPEC.md),
- everything under `models/` outside `kor-beklenen/`,
- `gozden-gecirme/`, `referans/` (including the pilots), `experiment/`,
- `IS-PLANI.md`, the project notes file of the project, `KARAR-NOTLARI.md`.

In addition:
- `GIRDI/kat_redakte.py` and `GIRDI/GIRDI.sha256` were not opened.
- `spec-corpus/metin/RFC5280.txt` was touched only with `wc -l` for the line count; its content was not read (not needed).
- In `ON-KAYIT-TASLAK.md` only §4.19 (lines 830–840) was read. Heading lines were scanned with `grep "^#"` to find the section.
- No tool (clingo, Tamarin, z3, ProVerif) was run.
- No network, git or Docker was used. No data was sent to any external service.

| # | Path | How | Why |
|---|---|---|---|
| 20 | My own outputs | `awk` (dictionary consistency, counts), `sha256sum` | Final check and generation of `SHA256SUMS` |
