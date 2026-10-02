# ACCESS LOG — Oracle B (Step 9, task 6)

> Evidence of independence. **Every** file and directory that Oracle B opened, listed or hashed is written here, in the order of access.
> Times are local time (+03:00). Project root: `C:\Users\tuncer\Desktop\Sefa\PQ-OID4VC` (`./` below). Folder names are given in their current form (see `docs/PATHS.md`); document names as they were at the time.
>
> **Never opened (statement):** `experiment/oracle/oracle-A/` (not listed, not read); other files in the root of `experiment/oracle/` (the directory was not listed; only `mkdir -p experiment/oracle/oracle-B` was run); `referans/` (none of its sub-directories was opened); `model/`; `gozden-gecirme/`; `IS-PLANI.md`. No network access. No target library was run. Docker and git were not used.

## 1. Directory listings (names only, not contents)

| # | Time | Command | Scope |
|---|---|---|---|
| 1 | 15:3x | `ls -la` | `./` (root: the names `.git/`, `00-on-kayit/`, `spec-corpus/`, `traceability/`, `threat-model/`, `project notes`, `IS-PLANI.md`, `tools/`, `experiment/`, `gozden-gecirme/`, `literatur/`, `model/`, `referans/`, `data/` were seen; their contents were not opened) |
| 2 | 15:3x | `ls -la` | `./00-on-kayit/` |
| 3 | 15:3x | `ls -la` | `./spec-corpus/` and `./spec-corpus/metin/` |
| 4 | 15:3x | `ls -la` | `./traceability/` |
| 5 | 15:3x | `ls -la` | `./experiment/` (sub-directory names: `inventory/`, `signer/`, `statistics/`, `environments/`, `generator/`; `experiment/oracle/` was not in the listing at that moment) |
| 6 | 15:3x | `ls -la` | `./experiment/vector-generator/` |
| 7 | 15:3x | `ls -la` | `./experiment/vector-generator/vectors/` and `./experiment/vector-generator/vectors/v1.2/` |

## 2. Files opened

| # | Time | File | Scope | Tool |
|---|---|---|---|---|
| 1 | 15:3x | `00-on-kayit/ON-KAYIT-TASLAK.md` | `grep -n "^#"` (headings) | grep |
| 2 | 15:3x | same | lines 1–210 (header block, §0–§2, §2A Ö1–Ö12; including Ö6) | read |
| 3 | 15:3x | same | lines 211–272 (§2B) | read |
| 4 | 15:3x | same | lines 368–489 (§2D; part A items 1–8 **and** part B items 9–17 appeared in the same chunk — part B contains results of the formal part and was not used in the oracle derivation; only the names of the G5 forms in item 10 were noted, see `L4-DERIVATION-B.md` §0) | read |
| 5 | 15:3x | same | lines 490–669 (§2E, §2F, §2G, §3.1–§3.7; §3.2–§3.6 appeared in the same chunk) | read |
| 6 | 15:3x | same | lines 758–781 (§4.7 G1–G5, §4.8 P0–P4) | read |
| 7 | 15:3x | same | lines 836–883 (§4.13, §4.14, §4.15) | read |
| 8 | 15:3x | same | lines 939–948 (§4.20) | read |
| 9 | 15:3x | same | lines 1039–1118 (§6.4, §6.5, §6.6–§6.11) | read |
| 10 | 15:3x | same | `grep -n -i "MR4\|L4c\|L4m\|oracle\|..."` — matching lines (364 = name correction of §2C item 4; 888, 1232, 1259, 1270, 1307 as single lines) | grep |
| 11 | 15:3x | `experiment/vector-generator/BATTERY-MAPPING.md` | complete | read |
| 12 | 15:3x | `experiment/vector-generator/vectors/v1.2/MANIFEST.json` | complete, with Python `json` (top-level fields + 153 vectors) | python |
| 13 | 15:3x | SHA-256: `v1.2/MANIFEST.json`, `v1.2/SHA256SUMS`, `BATTERY-MAPPING.md`, `ON-KAYIT-TASLAK.md` | digest only | sha256sum |
| 14 | 15:4x | working dumps (scratchpad, outside the project): `manifest_dokum.txt`, `manifest_sikisik.txt` | readable dumps produced from MANIFEST.json with Python; not written to the project folder | python |
| 15 | 15:4x | `spec-corpus/metin/JWTBCP.txt` (draft-ietf-oauth-rfc8725bis-10) | head (1–60), section list, lines 239–907 (§1.2–§6.1) | read/grep |
| 16 | 15:4x | `spec-corpus/metin/JOSECOMP.txt` (draft-ietf-jose-pq-composite-sigs-04) | head, section list, lines 136–1183 (§1–§7.1.3) | read/grep |
| 17 | 15:4x | `spec-corpus/metin/RFC9964.txt` | head, section list, lines 82–341 (§1–§8.1) | read/grep |
| 18 | 15:4x | `spec-corpus/metin/RFC7515.txt` | section list, lines 464–743, 753–1142, 1500–1559 | read/grep |
| 19 | 15:4x | `spec-corpus/metin/RFC9864.txt` | head, section list, lines 97–246, 332–376, 514–583, 629–672 | read/grep |
| 20 | 15:5x | `spec-corpus/metin/RFC9901.txt` | section list, lines 484–553, 904–977, 1642–2095, 2263–2337 | read/grep |
| 21 | 15:5x | `spec-corpus/metin/SDJWTVC.txt` (-19) | head, section list, lines 293–352, 978–1067; `grep typ`; change log lines 3608–3625 | read/grep |
| 22 | 15:5x | `spec-corpus/metin/SDJWTVC13.txt` (-13) | head, section list, lines 278–347, 694–783 | read/grep |
| 23 | 15:5x | `spec-corpus/metin/HAIP.txt` (1.0 Final) | section list, lines 186–633 | read/grep |
| 24 | 15:5x | `spec-corpus/metin/OID4VP.txt` (1.0 Final) | section list, Appendix A lines 2434–2683; with `grep` lines 605, 862, 882–894, 945–947 | read/grep |
| 25 | 15:5x | `traceability/` | `head -c 3000 izlenebilirlik.csv`; summary of columns and distributions with Python; rows of selected documents (id, document, section, keyword, first 200–230 characters of the quote). **Correction:** the output of `head -c 3000` also showed the `not` column of T001–T008 (on LOTL/TL; unrelated to the oracle); apart from that the `not` column was not listed. `OZET.md`, `kapsama_tablolari.md` and the scripts were not opened | head/python |
| 26 | 16:0x | `spec-corpus/metin/RFC9449.txt` | lines 393–527 (§4.2–§4.3) | read/grep |
| 27 | 16:0x | `spec-corpus/metin/TSL.txt` (draft-ietf-oauth-status-list-21) | head, lines 747–794 (§5.1) | read/grep |
| 28 | 16:0x | `spec-corpus/metin/RFC9101.txt` | `grep`, lines 925–946 | read/grep |
| 29 | 16:0x | `spec-corpus/metin/ACM2.txt` | `grep` (Note 50/51, lines 944–946) | grep |
| 30 | 16:0x | `spec-corpus/metin/LAMPSCOMP.txt` (draft-ietf-lamps-pq-composite-sigs-19) | `grep`, lines 1256–1365 (§4.3), 3405–3444 (Appendix A) | read/grep |
| 31 | 16:0x | SHA-256: the 15 cited corpus files + `izlenebilirlik.csv` | digest only (written to YONTEM.md §8, now `METHOD.md`) | sha256sum |
| 32 | 16:1x–16:4x | runs of `derive_decisions.py` (9 times including debugging: syntax/quote range fixes, cumulative generation for 4 arms, the last two runs byte-identical output) | The script reads **programmatically**: `MANIFEST.json` (complete); for the quote check, the PR and the complete text of 14 corpus documents (JWTBCP, JOSECOMP, LAMPSCOMP, RFC9964, RFC7515, RFC9864, RFC9901, SDJWTVC, SDJWTVC13, HAIP, OID4VP, RFC9449, TSL, ACM2). It opens no vector file | python |
| 33 | 16:4x | quote-verification snippets of `L4-TURETME-B.md` and `BELIRSIZ.md` | full-text substring search in the same 12 documents | python |
| 34 | 16:4x | `decisions.tsv` | check of its own output (key uniqueness, value sets, basis format, coverage of 153 vectors; comparison with the manifest) | python |

## 3. Not opened (additional statement)

- **No vector file** under `experiment/vector-generator/vectors/v1.2/` (`T/`, `CMP/`, `X5C/`, `VC/`, `VP/`, `REQ/`, `TSL/`, `DPOP/`, `CRIT/`, `UNK/`, `K10/`, `V/`, `b-uyumlu/`) was opened; `MANIFEST.csv` and `keys/` were not opened.
- `experiment/vector-generator/README.md`, `generator/`, `tests/`, `results/`, `Dockerfile` were not opened.
- `experiment/inventory/`, `experiment/signer/`, `experiment/statistics/`, `experiment/environments/` were not opened (only their names appeared in the output of `ls deney`).
- Under `spec-corpus/`, files other than `metin/` were not opened; `threat-model/`, `literatur/`, `data/`, `tools/` and the `project notes` (project root) were not opened.

## 4. Files written (only `experiment/oracle/oracle-B/`)

`ERISIM-KAYDI.md`, `YONTEM.md`, `derive_decisions.py`, `decisions.tsv`, `L4-TURETME-B.md`, `BELIRSIZ.md`, `KARAR-NOTLARI.md`, `SHA256SUMS` (the documents are now `ACCESS-LOG.md`, `METHOD.md`, `L4-DERIVATION-B.md`, `UNDETERMINED.md`, `DECISION-NOTES.md`). Temporary dumps in the scratchpad folder of the session (outside the project).
