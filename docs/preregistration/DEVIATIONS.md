# Deviation log: pre-registration v1.0

This log is created at the freeze from Section 13 of `PREREGISTRATION-v1.0.md` (Section 11, step 5). Deviations after the freeze are added below the line at the end as dated entries. Each entry states the type (minor or major), the reason, when it was noticed, its effect on the results and, where possible, the analysis according to the original plan (Section 10). Entries above the line are not edited.

## Deviations recorded at the freeze (Section 13 of the pre-registration)
Each item states what departs from draft v0.11, why, and its effect.

### 13.1 Treatment class TK2 out of scope (2026-10-01)
- **Change:** TK2 (plug-in) is removed. A target without native ML-DSA support is TK3.
- **Reason:** no hypothesis depends on TK2. T2 was to be run on TK1 targets, or reported descriptively if the data were insufficient. Amendment 11 made it descriptive (Section 13.11).
- **Effect:** T2 and T3 are restricted to TK1. Targets with a documented plug-in point (pyjwt, jjwt, jose2go, go-cose, sd-jwt-payload and others) become TK3. With no composite support at all, T2 has no data in the main arm. Amendment 11 then made T2–T5 descriptive (Section 13.11).

### 13.2 Step 5B sample: instances outside the translator's scope
- **Change:** of the 200 instances selected under Section 5.18 (189 cells, seed 20260926), 13 instances (in 12 distinct cells) are outside the scope of the ASP-to-Tamarin translator. Every one of them involves the issuer metadata artefact a05: its unsigned variant (9 instances) or a05 as the target of an expectation carrier (4 instances). 187 instances were translated.
- **Effect:** the 13 instances are listed in `models/sampling/5b/ceviri_disi.tsv` and reported separately. They count neither as agreement nor as disagreement. For the allowance of at most 10 % not-closed instances (Section 5.18), they are counted together with the not-closed instances (conservative reading, decision of the study lead). Result: 13 + 4 = 17 of 200 = 8.5 %, within the allowance (Section 12.1).

### 13.3 Version pinning
- **Change:** the targets are pinned to the versions of the build pretest of 2026-09-25 (`experiment/environments/build-results.csv`), not to "the latest published release at freeze" (Amendment 8, item 14).
- **Reason:** the treatment classes, the API scans and the adapters were built against these versions.
- **Effect:** the pinned versions are listed in Appendix E. A target without a release is pinned to a commit (wolfCOSE `f907071b`).

### 13.4 Battery v1.3 and oracle v1.3 derived by case mapping
- **Change:** Amendment 8, item 11 required oracles A and B to re-derive with their own scripts, using the definitions of items 7–10, at least for the primary vectors and V±. Instead, the merged oracle `experiment/oracle/merged/decisions_v13.tsv` was produced by one script (`derive_v13.py`) that takes the v1.2 decisions of A (858 rows) and B (732 rows), applies items 7–10 as normalisation rules, maps the COSE vectors to the JOSE vector of the same case (COSE and L4c) and adds the L4c-3 rows from the quotation in the battery mapping.
- **Provenance of the 1,845 rows** [computed from the `kaynak` column]: A = B 152, single oracle 1,118, A ≠ B 10 (→ indeterminate), one of them indeterminate 3 (→ indeterminate), item 8 (B1 flag) 96, item 9 (arm-independent) 12, COSE case mapping 418, L4c-3 36. Decisions: accept-classical 460, accept-hybrid 255, reject 861, arm-independent 24, B1 flag 108, indeterminate 137.
- Among the rows that oracle A classifies as primary, only the `L4` rows (47) and the `P0` rows (20) rest on agreement of the two oracles. 229 primary rows rest on oracle A alone (`GEC` 39, `IZIN-A` 37, `IZIN-AX` 37, `L4-S` 47, `L4-Y` 47, `P1` 20, `L4-YOL` 2), and 82 primary `P2` rows on oracle B alone. Oracle A's `P1` and oracle B's `P2` are different configurations (W differs) and are not compared. On 61 shared keys they differ in 18 rows, all secondary [computed]. The V± rows agree between `GEC` (A) and `P2` (B) on all 14 shared keys.
- The merged file has no primary/secondary column. Primary status is read from the battery mapping.
- **Resolution** (decision of the study lead): the `L4` rows that determine Y_L4 and T1 rest on agreement of the two oracles, directly or through the case mapping of rows where they agree (COSE vectors, ES384 counterparts). The exception is the legacy-issuer row of L4c (L4c-3), which neither oracle derived because the legacy issuer was added in v1.3. It is taken from the quoted rule of the battery mapping (Amendment 2, item 6). The single-oracle rows feed only descriptive variables. This satisfies Amendment 8, item 11 for the confirmatory part [computed from the `kaynak` column of `decisions_v14.tsv`].

### 13.5 Tamarin wall-time record of 7,024 s
- One Step 7 run (`MF_tas_federasyon_bayat` / `M_weak_path_forgery`) recorded 7,024 s of wall time on 2026-09-26, above the 10-minute limit per ladder step.
- On 2026-10-01 the same command was re-run under a 600 s limit: 78 s, same verdict (verified).
- The record is an artefact of the host machine being suspended. Memory never exceeded 5.4 GB.

### 13.6 Unexpected results for M-e and M-e′
- `no_rollback` was expected V and observed F for both (Section 12.1). The results are reported as they are and are not used to change any verdict.
- Exploratory, not among the expectations fixed beforehand: restricted to migrated issuers, the lemma is verified (M-e in 38 steps, M-e′ in 45 steps, `models/mechanisms/kesif/me_gocmus/`).
- Reading: an expectation carried by an object that is signed with the protected entity's own breakable key cannot protect that entity.
- The M-e′ result is a candidate under (2c′)(ii) (Section 5.21). The independent novelty assessment rated it obvious, as an instance of the first-contact limitation of host-learned policies (Section 12.1).

### 13.7 Pre-freeze decisions D1–D7 (2026-10-01)
- **D1, SD-JWT-format validity vectors.** SD-JWT targets are gated with 16 SD-JWT-format vectors (`experiment/runs/vpm-sdjwt/`), because the JWS-level pair is not a well-formed SD-JWT VC for libraries that require `_sd_alg` or a specific `typ`. SDJWT-021 is measured in its `vc+sd-jwt`/ES256 form. SDJWT-002 is kept although it accepts corrupted signatures, flagged `integrity-failure`, and every analysis is also reported without it. Recorded deviations with D1 as basis: vectors outside the battery are used for the validity gate (Section 7.8), and the adapter-invalid rule is not applied to SDJWT-002 (Section 5.15). SDJWT-002 is flagged and every analysis is reported without it.
- **D2, JOSE-102.** ML-DSA-65 only through `@_spi(PostQuantum)`. Primary TK3, sensitivity TK1.
- **D3, wolfCOSE.** Measured with the documented build flag `WOLFCOSE_ENABLE_DEPRECATED_ALGS`. Default build reported descriptively.
- **D4, control-arm label order and battery v1.4.** This decision is Amendment 10 (Section 13.10). Its first wording of 2026-10-01 (control-arm level `undetermined` for the 15 targets without EdDSA or Ed25519) was replaced before the freeze.
- **D5, documented caller patterns** count as the library's verification path (COSE-035, SDJWT-010, SDJWT-015, SDJWT-025).
- **D6, policy-name suffixes.** The suffixes split only the expected outcome. `P2` uses the library default. `L4-YOL` is not expressible for every target.
- **D7, calling conventions** of the two adapter families (Section 7.19).

### 13.8 Language edit of the repository (2026-10-01)
- Repository files were translated to English and process notes were reworded neutrally. Top-level and second-level folders were renamed (for example `deney/` → `experiment/`, `model/` → `models/`, `deney/uretec/` → `experiment/vector-generator/`, `deney/envanter/` → `experiment/inventory/`, `deney/istatistik/` → `experiment/statistics/`, `model/mekanizma/` → `models/mechanisms/`, `01-korpus/` → `spec-corpus/`, `02-izlenebilirlik/` → `traceability/`, `arac/` → `tools/`, `veri/` → `data/`).
- Internal project-management notes, design-process copies, literature full texts and third-party specification texts were removed from the repository (commit `fa44c06`), including the draft itself.
- The integrity lists (`SHA256SUMS`, `*.sha256`) were kept; no recorded digest was changed. The renaming rewrote the recorded path in six entries (a decision-note file name in two lists, and the folder `sentetik-testler/veri/` written as `sentetik-testler/data/` in four entries of `experiment/statistics/SHA256SUMS`, although the folder itself kept its name). Where the release translated or renamed a listed file, the recorded bytes are kept in `archive/hash-anchored/`; `tools/verify_anchors.py` checks every record and `docs/INTEGRITY.md` explains the classes (current, archived, noted). `experiment/statistics/SHA256SUMS` is regenerated at the freeze. Effects on anchored identities: Section 12.6.
- The same blanket rewrite had changed the two references to `sentetik-testler/veri/` in `experiment/statistics/run_all.sh` to `data/`, so the script could no longer write the statistics list. This was corrected on 2026-10-03 before the list was regenerated (script bug fix that does not change results, minor deviation in the sense of Section 10).
- Code comments and diagnostic messages of the hand-written scripts were translated on 2026-10-02/03; a comment-only check (`tools/verify_comment_only.py`) shows that no code changed. Model files (`.lp`, `.spthy`), generated samples and recorded outputs keep their Turkish comments.
- A message-only rewrite of the history on 2026-10-01 changed the commit identifiers of anchors 4–9 (trees and dates unchanged). Appendix C gives the current identifiers.
- The run files and folders under `experiment/runs/` were renamed to English names in commit `0ba930d` (for example `adaptorler/` → `adapters/`, `kosu/` → `outputs/`, `isler_v14.jsonl` → `jobs-v1.4.jsonl`, `KOSUCU.md` → `RUNNER.md`), and the oracle method files on the translation branch (`adaptor-sozlesme.md` → `adapter-contract.md`, `YONTEM.md` → `METHOD.md`).
- Paths in this document use the new names.

### 13.9 Interpretations and further deviations recorded at consolidation
- **Freeze date** earlier than the draft's target window (2026-11-04 to 2026-11-06), because the scientific gate decision was taken on 2026-10-01.
- **Strategy file** in JSON at `models/asp/sorgular/stratejiler_taslak.json` instead of YAML at the path named by Ö5 (Section 5.9). Its content was fixed before the comparison and Step 8 checks it by a canonical hash.
- **OJEU expectation hook** brought into the scope of M-f on 2026-10-01, after the formal results were known, contrary to Amendment 8, item 5 (Section 5.1). An addition after the results. It changes no verdict.
- **Fair-metric variant of H4** added on 2026-10-01, after the formal results were known, as a sensitivity analysis (Section 5.21). It changes no verdict.
- **H0 condition (a)** read as "every health lemma has the verdict fixed before the runs" (554 of 554 as expected, 550 verified, four `executable_learn` lemmas fixed as false before the runs). Explicit interpretation, accepted as the frozen reading (Section 4.1).
- **Mutation score** reported in both readings: 45/45 = 1.00 with the two base-insecure mutants excluded, as the score script does, and the literal 45/47 = 0.957. The threshold of 0.90 holds under both (Section 5.17).
- **V± configuration** run under `GEC` instead of `P2` (Section 5.20). Deviation. The decisions are identical on the 14 rows where both exist.
- **Known-answer tests:** first run 2 of 3, because KAT-1 failed in its own Tamarin encoding while the ASP core agreed in 109 of 109 cells. Corrected run 3 of 3, labelled post-result correction. Gate condition (1) holds with this documented deviation (Section 5.19).
- **H4 result file** changed on 2026-10-01 (commit `f143bdf`) from 10 candidate cells to the 6 τ-wasteful cells counted under Amendment 8, item 3, with the four G4 cells exploratory. The rule did not change. The earlier text of the result file did not apply it.
- **Public repository:** the draft's freeze procedure assumed a local repository only. The frozen state is published as the tag `prereg-v1.0` of the public repository (Section 11).
- **Statistics and analysis scripts** updated before the freeze for the rules of this version: symmetric fragile falsification (Amendment 8, item 17), sensitivity `gecersiz_y0` (Amendment 10), descriptive flag of T2–T5 (Amendment 11), incidental rejection, F_K and F_T against the `L4` rows, and the pilot set of both pilots (Sections 5.13, 7.14, 7.19).
- **Runner documentation:** `experiment/runs/RUNNER.md` and the adapter contract still describe earlier states (row counts of v1.3, battery v1.2, TK2). They are updated before the freeze (Section 11, step 1).

### 13.10 Amendment 10 (2026-10-01): control-arm fallback label ES384 and battery v1.4
- **Change:** the control-arm label order becomes EdDSA, then Ed25519, then ES384 (extends Amendment 4, item 2). The measurement battery becomes v1.4 = v1.3 (byte-identical) + 30 ES384 counterparts of the control-arm vectors. The oracle becomes v1.4 = v1.3 + 357 `kontrol-ES384` rows derived by case mapping. The measurement job list becomes `experiment/runs/jobs-v1.4.jsonl` (2,202 rows). Adapters see v1.4 at the path `/v/v1.3` (superset).
- **Reason:** 15 of the 31 targets support neither EdDSA nor Ed25519. The control arm exists to separate the expressibility of the policy from PQ support, and ES384, a second classical algorithm of the same family, serves that purpose. Under the first wording of decision D4 these 15 targets would have had no Y_L4 value and n_eff would have fallen to at most 16, below the inferential bound of Section 7.5.
- **Result:** control labels EdDSA 17, ES384 13, none 1 (`experiment/runs/CONTROL-LABELS.csv`). SDJWT-021 verifies only ES256, cannot express a two-algorithm required set, is excluded from the primary H6 analysis and counted as Y = 0 in a sensitivity analysis. SDJWT-002 keeps the label EdDSA and the flag of Decision D1.
- **Effect on H6:** the primary n_eff is 30 before indeterminate targets are removed. Thresholds for n_eff = 30: support X ≤ 10, falsification X ≥ 20 (Appendix A, P(X ≤ 10) = 0.0494). If n_eff changes, the thresholds are read from Appendix A (Section 9.3).
- **Known when written:** the validity gate results, including the ES384 gate (24 of 31 targets passed). **Not known:** any battery outcome.
- **Battery mapping:** each ES384 counterpart inherits the primary or secondary status of its EdDSA source vector, as the case mapping of the oracle does.
- **Nature:** a change of the battery before any battery vector was run on a target. Under the battery rule of Section 7.8 it requires a new identity, which is fixed by the freeze of this version.

### 13.11 Amendment 11 (2026-10-01): narrowing of the C3 analysis and wording of the formal part
Decisions of the study lead after an internal methodological review. Recorded before any measurement data existed: only the pre-freeze validity gate had been run.
- **H6 and T1 unchanged:** primary variable Y_L4, n_eff = 30, support X ≤ 10, falsification X ≥ 20, robustness rules. T1 is the only confirmatory test.
- **T2–T5 descriptive** (Section 7.10). Reason: with the plug-in class removed, the ML-DSA-65 arm has 5 TK1 targets, so the exact McNemar test cannot go below p = 0.0625, and T3 cannot go below p = 0.33. T2 and T3 had no power. No p-value, test decision or Holm correction is reported for T2–T5. Original plan: Section 7.10, superseded plan.
- **Historical baseline and known-bug recall removed**, with evidence component D7 (Sections 6.2, 7.16).
- **L4c interpretation note** added: for compact-only targets L4c in effect measures a per-issuer algorithm allowlist (Section 5.13).
- **Incidental rejection rule** added for the control arm: a rejection caused by missing support of the control-label algorithm (in particular ES384) is coded as not supported, not as policy enforcement (Section 5.13). Amendment 10 did not contain such a rule. The adapter contract has one only for L3.
- **Evidence rule:** second independent attempts only for targets whose "not expressible" verdict enters T1 (Section 5.14).
- **Wording:** the formal part (C1, C2) is described as "expected verdicts fixed and hashed before the runs (internal record)". "Pre-registered" applies to the C3 measurement only, from the public freeze of this document (Sections 1.2, 11).
- **Known limitations** of the independent derivations stated (Section 1.6).
- **Reference verifiers and the end-to-end demonstration (Step 11) removed** (decision of the study lead, not needed for any claim): evidence component D8, the reference verifiers of Section 7.4, the week 8 check and the emulator condition of week 10 (Section 9.1), and the emulator references in Sections 4.2, 5.21 and 5.22.
- **Guiding principle** stated (Section 1.3): T1/H6 and its computation chain are the only confirmatory element of C3. All other C3 outputs are descriptive.
- **Adopted into the frozen package:** sensitivity thresholds from their own sample size (statistics note N-2), the reading of Section 7.12 (N-12) and the tolerances of the two implementations (N-8). The pilot sensitivity excludes the targets of both pilots. SDJWT-021 enters only the sensitivity `gecersiz_y0` (Section 7.14).
- **ES384 counterparts** inherit the primary or secondary status of their EdDSA source vectors (Section 7.8).
- **Unchanged:** the measurement run, the battery v1.4 (apart from the corrected manifest count), the oracle v1.4, the job list and the decision logic of the adapters.

---

### 13.12 Corrections of the analysis chain before the freeze (2026-10-03)
- **Change:** a review of the analysis chain found defects in the analysis script written before any measurement (commit `ebeded0`) and in the statistics package. They were corrected before the freeze and tested on synthetic outputs only: (1) a conjunction of checks became indeterminate when one cell was unstable although another cell deviated stably, so a target with a determined Y_L4 = 0 would have left n_eff (and counted as Y = 1 in sensitivity (i)); (2) the inputs of the sensitivity analyses of Decisions D1 and D2 were not written; (3) the statistics schema did not accept the control label ES384 of Amendment 10, so the statistics package rejected every input that contains an ES384 target; (4) a target without a published release (COSE-036) had no reason for its missing `surum_8725bis_sonrasi`; (5) B2 counted rows of an unsupported format; (6) the adapter run script had CRLF line ends, which break it on Linux, and the measurement script did not stop when its directory could not be entered.
- **Effect:** no rule of this document changes; the scripts now implement the rules as written. No battery vector had been run on a target. Public record: issue #5 and pull request #6 of the repository.

### 13.13 Pre-freeze decisions D8 and D9 (2026-10-03)
- **D8, evidence rule.** Second attempts for the 7 targets whose Y-determining configuration was recorded as not expressible, made in a separate session without access to the adapters. Reconciliation rule: L4 is expressible when the library enforces the policy that the caller configures; a check written by the caller inside a callback while the library enforces no algorithm policy is custom code (B4). Results in Section 5.14. COSE-014 was found expressible through designated-signer verification, and two defects of its adapter (kid passed as text, kid read only from the protected header) were corrected.
- **D9, adapter conformance review.** A review of all 31 adapters against the adapter contract and Section 5.13, without any battery outcome, and a conformance test on objects outside the battery (acceptance rows only). Changes:
  1. **Legacy-issuer record of L4c:** 11 per-target adapters (JOSE-001, JOSE-002, JOSE-031, JOSE-070, JOSE-071, JOSE-087, JOSE-089, JOSE-102, COSE-035, COSE-036, SDJWT-002) applied R = {X} to every issuer, so the legacy-issuer rows would have been rejected by the adapter. All adapters now select the record by the `iss` of the object (Section 5.13). Only the L4-family rows of the two L4C vectors change.
  2. **Issuer identification:** COSE-014 and COSE-034 identified the legacy issuer from the vector id; they now read the `iss` of the COSE payload. No row changes.
  3. **Battery v1.4:** 9 COSE ES384 counterparts carried the kid of the Ed25519 key in the unprotected header. The generator was corrected and v1.4 generated again; only these 9 files and the manifest files changed. This is a deviation from "battery v1.4 unchanged" in Section 13.11. Gate re-run: COSE-034, COSE-035 and COSE-036 now pass ES384; no control label changes.
  4. **Defects found by the conformance test:** COSE-001 (kid decoded as text), COSE-014 (COSE_Sign key without an ES256 signer), SDJWT-015 (multi-signature L4/L4-S configured as the single-signature allowlist; now `ifade-edilemedi`), and the error class of a `KeyError` in the shared Python adapter.
  5. **Evidence rule:** second attempts for COSE-035 and COSE-036 (Section 5.14).
- **Deviations recorded:** objects outside the battery other than the validity vectors were run on the targets before the freeze (Section 12.4), with the pre-knowledge stated in Section 12.5; battery v1.4 changed in 9 files after Amendment 10; the operational reading of "same verifier instance" for L4c is fixed by Decision D9.
- **Effect:** no hypothesis, threshold or decision rule changes. The analysis script is unchanged. Public record: pull request #8 of the repository.

---

## Deviations after the freeze

### Deviation 1 (2026-10-03): incidental-rejection rule of Section 5.13
- **Type:** major (it changes the result of the confirmatory test T1).
- **When noticed:** 2026-10-03, after the measurement and after the registered analysis had been run and published (`experiment/runs/analysis/results/`), while checking why two L4c targets had Y_L4 = 0.
- **What:** Section 5.13 (Amendment 11) codes a control-arm rejection as not supported when its error class shows that the control-label algorithm itself is not supported on that API path. The frozen analysis script, and the implementation bullet of the same section, apply this coding to every control-arm rejection with `hata_sinifi = alg-desteklenmiyor`, whatever algorithm was rejected. JOSE-034 (jose2go) and JOSE-055 (jjwt) implement their allowlist as a restricted algorithm registry and reject `VPLUS_ES256` under `L4` with "unknown/unsupported algorithm ES256" (class `alg-desteklenmiyor`), although both accept the same object under `GEC` and `IZIN-A`. The frozen script codes these policy rejections as not supported and sets Y_L4 = 0 for both targets.
- **Reason for the deviation analysis:** the rule text restricts the coding to the control-label algorithm; the two rejections concern ES256.
- **Analysis according to the original plan (registered, primary):** X = 19 of n_eff = 30, one-sided p (upper) = 0.100: H6 inconclusive (`experiment/runs/analysis/results/`).
- **Deviation analysis:** the frozen script with the coding restricted to vectors signed only with the control-label algorithm (`experiment/runs/analysis/deviation-1/`): X = 21 of 30, p = 0.021: falsification region; only JOSE-034 and JOSE-055 change (Y_L4 0 to 1). Pilot targets excluded: 14 of 23, inconclusive.
- **Effect on the conclusions:** H6 is not supported under either analysis. The registered result stays primary and the deviation analysis is reported beside it (decision of the corresponding author, human step İ7, 2026-10-03).
