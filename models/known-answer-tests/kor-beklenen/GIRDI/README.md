# Blind derivation input — how it was prepared (maintainers, 24.09.2026)

Source: `literatur/analiz/KAT-SPEC.md` (SHA-256 `f8ba9a51…8b80`). Output: `KAT-KOR-GIRDI.md`
(`1b0dac38…26f2`), now named `KAT-BLIND-INPUT.md` (translated to English for this release; see
`docs/INTEGRITY.md`).

**Steps:**
1. `kat_redakte.py`: from the tables of the (d) sections, the columns "Expected…", "Basis", "Note",
   "accept strict/transitional" and the attack/violation columns were removed. In columns of the
   form "Tamarin flags → result" only the left side of the arrow was kept.
2. Inline Python of the maintainers (the script is described in this file):
   - all code blocks of sections (a)–(c) were removed (draft ASP/Tamarin code);
   - pilot result notes were removed;
   - sections (d) and (e) and §5, §6 and §7 were not taken at all;
   - the cells of the KAT-2c table were set to "?";
   - the "Pilot Tamarin" column of KAT-3b was removed;
   - bold emphasis was removed;
   - the result summaries of Kim et al. Table IV and Table V were removed (pointer to the primary
     text instead);
   - the value dictionary was written by hand: the set of values is given, their mapping to cells
     is not.
3. Residual leakage scan: the only remaining matches are the general criterion sentence and
   verbatim quotes of published claims.

**Purpose:** the blind N-version derivation of expected values of PR §4.19 and KAT-SPEC §5.3.

## Files

| File | Content |
|---|---|
| `KAT-BLIND-INPUT.md` | The input given to the blind derivation (formerly `KAT-KOR-GIRDI.md`) |
| `kat_redakte.py` | Step 1 of the redaction (`python kat_redakte.py <KAT-SPEC.md>`; KAT-SPEC is not part of this release) |
| `GIRDI.sha256` | Hashes of the input, of the redaction script and of the source KAT-SPEC |

`kat_redakte.py` selects the columns to drop with a regular expression over the Turkish column
headings of KAT-SPEC (`Beklenen` expected, `Dayanak` basis, `Not` note, `sonuç`/`hüküm`
result/verdict); the expression is part of the recorded procedure and was not changed.
