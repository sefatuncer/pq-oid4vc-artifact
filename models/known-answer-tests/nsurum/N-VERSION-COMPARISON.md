# KAT expected values — N-version comparison (maintainers, 25.09.2026)

**Purpose:** PR §4.19 and KAT-SPEC §5.3. The expected-value tables of the first derivation (the (d) sections of `literatur/analiz/KAT-SPEC.md`; SHA-256 `f8ba9a51…8b80`) were compared with the independent derivation of the blind session (`kor-beklenen/BEKLENEN-KOR.tsv`, `180a655a…a4bb`, commit `f012841`).

**Timing:** The comparison and the resolution were done BEFORE any ASP or Tamarin run of Step 6. The core of Step 3 (`cekirdek.lp`) was not yet complete.

## Result (`kat_nsurum.py` → `kat_nsurum.tsv`)

| Status | Count |
|---|---|
| Keys compared (cell × column) | 141 |
| **Equal** | **138** |
| Different | **0** |
| Blind derivation "undetermined" | 3 (K2d-01/02/03, Tamarin column) |
| Present on one side only | 0 |

**Mapping notes (when the merged cells of the first derivation were expanded):**
- K2a-05/06 "same" → accept_classical / accept_classical (the same pattern as K2a-01/02; Kim Table IV).
- In KAT-3b the Tamarin expectation of the first derivation = the pilot column (SALDIRI ↔ falsified, YOK ↔ verified).
- The `qday=200` expectation comes from the prose "6/6 attack = YOK".

## Resolution of the undetermined cells by going back to the source (K2d Tamarin)

- **Why it was undetermined:** The maintainers' redaction dictionary did not name the Tamarin lemma of KAT-2d (an error of the maintainers; what was missing was a detail of the specification, not an expected value). The K2d flags contain no `CRQC`, i.e. the attacker is M1. The blind derivation gave three value patterns for three candidate lemmas (`UNDETERMINED.md` §A1).
- **Source:**
  - The KAT-SPEC §3(c) draft separates the lemmas explicitly: `cert_authentic` = "M2: certificate authentication" (the CRQC cells of K2b); `no_silent_promotion` = "M1: hybrid intent — every accepted key must have been issued as hybrid".
  - K2d reproduces Table VI of Kim et al. (P0–P3) under M1: "Under M1, P1 provides no more protection than P0: the adversary withholds the post-quantum evidence, P1 tolerates the absence, and the result is accept-classical".
- **Resolution:** K2d Tamarin lemma = `no_silent_promotion`. Expected: K2d-01 (V_IGNORE) **falsified**, K2d-02 (V_ENFORCE_IF_PRESENT) **falsified**, K2d-03 (V_REQUIRE) **verified**. This equals the values of the first derivation and reading (b), which the blind derivation considered most likely ("acceptance ⇒ PQ evidence / hybrid issuance").
- **Result:** there is an agreed expected value for 141/141 keys.

## Alternative readings recorded in advance (risk note)

The blind derivation wrote the cells whose value depends on an interpretation, together with the value under the alternative reading, to `kor-beklenen/UNDETERMINED.md` §B:
- time constants (K1-05, K1-07, K1-09, K1-13, K1-14);
- scope of the completeness test (K1-04, K1-06, K1-11);
- K1-14 extra anchor, K1-15 `allpresent`;
- K2a-10;
- K2d-05 (P3 first contact);
- KAT-3a o6, o8, o10;
- KAT-3b V4.

**Rule (PR §2C.1):**
- The gate decision is taken with the agreed values above. If a cell is run and comes out different, the test is not replaced by the alternative; the failure is reported and a model error is looked for.
- A pre-recorded alternative reading is used only in the diagnosis (model error or specification interpretation?) and is reported. It does not count as a later reinterpretation, because it was recorded before the run.

**Identities:**
- `kat_nsurum.py` and `kat_nsurum.tsv`: in this folder, `SHA256SUMS`.
- Single source of the agreed expected values: `kat_nsurum.tsv` (column `ilk_ajan`; the K2d Tamarin rows with the resolution above).
