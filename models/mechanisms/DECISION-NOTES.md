# Step 7 task 0 (Tamarin work) → notes to the maintainers

- **Date:** 25.09.2026
- **Folder:** `models\mechanisms\` (owner: the Tamarin work). `models\tamarin\` was not changed.
- **Run rule (binding):**
  - No `--prove`. Only the well-formedness check was done (`tamarin-prover file.spthy -D=…`, 0 warnings).
  - No run before the SHA-256 of the expectation file and of the models is anchored and before the technical-gate decision.
- **The scope economy (decision of 25.09) was applied.** Details: `PRE-REGISTRATION-RATIONALE.md` §0.1.

## Status

- [x] Skeleton files: `on_kayit_varyantlar.tsv`, `ON-KAYIT-GEREKCE.md` (now `PRE-REGISTRATION-RATIONALE.md`), this file.
- [x] Expectations. 63 rows:
  - 33 to be run;
  - 18 `5A-kapsandi` (covered in 5A; reference to R7);
  - 11 `indirgendi` (reduced);
  - 1 `betimsel` (descriptive; KB 3c, no model).
- [x] Model drafts (`modeller\`):
  - `ortak_g5.spthy` (the three forms of G5, `#include`);
  - `M_istek.spthy`: M-b0, M-a, M-b / A.3.2.2; M-c reduced;
  - `M_metaveri.spthy`: M-e, M-e′, M-d; a one-parameter family;
  - `Mf_yol.spthy`: M-f core including the path, 3b, carriers;
  - `M_h.spthy`: reddy and vicente types, 3a/3b.
  - `M_g.spthy` and `KB_coklu.spthy` were not written (covered in 5A / descriptive).
- [x] Well-formedness: 33/33 run rows `wf_ok=1`, 0 warnings. Record: `iyi_bicimlilik_on_kayit.txt`.
- [x] SHA-256 list: `SHA256-ON-KAYIT.txt` (also below). → STOP.

## The 33 rows to run

| Model | Rows |
|---|---|
| `M_istek` (3) | `MB0_taban`, `MA_taban`, `MB_taban` (= M-b / A.3.2.2) |
| `M_metaveri` (4) | `ME_signed_fresh` (M-e), `MEP_signed_fresh` (M-e′, conditional proof), `MEP_tls_classical` (M-e′, fetched channel), `MD_reg_pq` (M-d) |
| `Mf_yol` (17) | `MF_cekirdek` (acceptance criterion 2); the 9 cells of 3b; carriers: `MF_tas_tl_onbellek`, `MF_tas_wrprc_faz0`, `MF_tas_wrprc_faz1`, `MF_tas_federasyon_pq`, `MF_tas_federasyon_klasik_ara`, `MF_tas_federasyon_bayat`, `MF_tas_crit_baslik` |
| `M_h` (9) | reddy × {classical chain, 3 attacks, name binding + different name}; vicente × {classical chain, 3 attacks} |

- The flags and expectations of the 23 run rows written before the scope decision did not change (compared by script). There are 10 new run rows: `MF_tas_tl_onbellek` and the 9 rows of M-h.
- There is no lemma without a written expectation (checked by script). The only exception is `executable_learn` in the `M_metaveri` rows; this lemma falls under the header rule "executable* default V".

## Warnings for the run work

1. **Derivation-check timeout.** For models of the size of `Mf_yol` and `M_h`, Tamarin's default derivation check times out. In that case the well-formedness warning "Derivation checks timed out" appears; under the 5A rule this invalidates the run.
   - Therefore `--derivcheck-timeout=60` was added to `betik\iyi_bicimlilik.sh` (environment variable `DCT`). The check was not switched off, only its time was extended; with 60 s every model passed clean in about 7 s.
   - **The actual runs must use the same flag.** Otherwise the warning appears in the `--prove` output.
2. **Row filter.** The runner must run only the rows with `rol` ∈ {mekanizma, kosul, tasiyici, ablasyon, 3b, 3a}. The `dosya` / `bayraklar` columns of the `5A-kapsandi` rows refer to an R7 variant (`models\tamarin\`); they are not run.
3. **Resource estimate.** The rows of `Mf_yol` with three attacks (`MF_cekirdek` and the carriers) contain a depth-2 path and three breakable anchors; they are the heaviest rows. The ladder applies: `--memory=12g`, a time limit per lemma.
4. **Consistency check.** `ATK_*` only adds set-up rules. The V verdicts of `MF_cekirdek` imply the V verdicts of the three `MF_3b_yol_*` cells; a contradiction would be a model error.

## Model assumptions (to be stated explicitly in the report)

- **`M_istek` `RequestSamePhase`:** an honest request is accepted in the phase in which it was created. Requests are short-lived, so an artificial migration race is excluded. It does not apply to forged requests.
- **`M_metaveri`:** no "same phase" restriction (credentials are long-lived).
- **`Mf_yol`:**
  - `Freshness`: the response is current until the moment of use; delay is the subject of R6.
  - `SCOPE_KEY`: the bound PQ key comes from the same verified view as the expectation.
  - `FED`: the resolution response is bound to the query and current.
- **`M_h`:**
  - R1: reddy's "SHOULD terminate" rule is applied.
  - V1: in vicente a commitment error is rejected; the draft does not define the outcome.
  - V2: the verifier keeps the first commitment per subject.
  - Window and expiry were not modelled. That there is no protection after the window follows from the draft text.
- **M-c:** the preference "PQ first if present" cannot be expressed in the symbolic model (no negative premise). The reduction is therefore to M-b.
- **A.3.2.2:** the semantics is undefined (T273). The reading "the wallet verifies with any framework it trusts" is an assumption.

## Candidate findings and points awaiting a decision

1. **A pre-registration that contradicts the plan text for M-d.** Work plan 7.4: "via the PQ channel → proof". Pre-registration: `MD_reg_pq` G5_migrated = F. Reason: the update messages are PQ-signed but replayable; the pre-migration `'none'` entry is replayed after the migration (S1). Recorded this way on purpose.
2. **reddy: candidate for qualifier (b).** Under the draft's own rules (§3.1 path validation unchanged; §3.3 cache SAN + algorithm), a forged PQC certificate from any classical CA goes unnoticed.
   - **Caution:** sheffer-02 §3.2 (co-authored by Reddy) anticipates the fact; the condition "not derivable" is debatable. RATIONALE §6.3.
3. **Limit of name binding (refinement of R7h/R7hx).** Once intermediate CAs are modelled, the attacker issues an intermediate CA that carries the name of the legitimate CA. Name binding fails even against an alternative CA with a different name; pre-registered F (`MH_reddy_adbag_farkli_ad`).
4. **Not pre-registered, awaiting a decision: the ambiguity of the chain policy of sheffer-02.** The definition "not traditional-only" of §3.1 and the rule "every CertificateEntry" of §3.2 are open to a key reading.
   - Under the key reading the 3b attacks pass even after the cache is filled.
   - In addition, the cache can be forced to clear with `algorithm_validity_period = 0` (§3.6).
   - It can be pre-registered as an addition of 2–4 rows on the `M_h` infrastructure. RATIONALE §5.
5. **Not pre-registered, awaiting a decision: path-sensitive M-f definitions** (for M-f-DEFINITION). `MONOTONE` = "the 'none' expectation is never used"; the sunset must be at expectation level.
   - A key-level sunset closes only the classical leaf. After the sunset, a stale `'none'` lets a PQ path with a classical edge be accepted.
   - The flags are in `Mf_yol`; if wanted, they are recorded as separate rows. RATIONALE §3.4.
6. **KB 3c:** no model was written; the expected answer comes from the text of RFC 9901 §8.1/§8.3 (RATIONALE §7). If tool evidence is wanted, a small model can be added.

## Working environment

- **Docker:** only well-formedness containers named `pq-a07-wf<pid>`, `--rm`, limited to 4 GB, were run. No new image, no `prune`, no other container touched. Docker was left running.
- **No outward-facing action;** no e-mail or personal data was sent anywhere. No git commit was made.

## SHA-256 (`SHA256-ON-KAYIT.txt`)

```
16fae232503d525c804b1ab6742df7eb1972c804a39dfa3851840dda8d4cfccd  on_kayit_varyantlar.tsv
42e79bd0ca472808d288c4f089ec608d45c745b3c9c68bb92162af9c3e30b750  modeller/ortak_g5.spthy
74b0e4407e390b3c548c11d73f603ab647d279ff6c9a7611b8fb8377baf41cf5  modeller/M_istek.spthy
f56fb4ce22c9a269384e55d35432d7cf853ae7a3094f3c87b7cd3d54f8ad72f7  modeller/M_metaveri.spthy
00c1b35d7dda7db5740b46c189f87cd6384e15059daf15659fb31cf06f4dcfa4  modeller/Mf_yol.spthy
1fb460cf9820f0f285a8238f971e688db33477ee776f9c1cf8bf164e56f543d5  modeller/M_h.spthy
64f72f8ce0b005078968c8ed92de09b818daabc08c1f646165db63fa67d06dab  ON-KAYIT-GEREKCE.md
fdb8bf9b41b69f02607a98be92c47fa60665382554208d6b8e1492da0b7a5cf7  betik/iyi_bicimlilik.sh
423938ce2447c63cd027eb7fc564707d6124e2577ff5d50d6390b9101a283c05  iyi_bicimlilik_on_kayit.txt
516f01bea8329ca0af778590b42156c7566bb258002f3f68a1f55ac5860e170a  SHA256-ON-KAYIT.txt
```

(These are the anchor values of 25.09.2026, before the files were translated for this release; see `docs/INTEGRITY.md`.)

## ANNEX — Amendment 8 (26.09.2026)

- Two candidate groups were pre-registered; 10 rows were appended to the expectation file (the previous 63 rows byte-for-byte identical).
  - [8a] `modeller\Mg_yol.spthy`: sheffer-02 chain policy, key / signature reading × 3 attacks (6 rows).
  - [8b] `modeller\Mf_ek.spthy`: path-sensitive definitions of the offline annex, monotonicity {narrow, broad} × sunset {key, expectation} (4 rows).
- The previous model files did not change (same digests); two new files were written for the new rows.
- Well-formedness 10/10 clean. Rationale: `PRE-REGISTRATION-RATIONALE.md` §9. Rows to run: 43.
- SHA-256 of `on_kayit_varyantlar.tsv`: `ebb87d64216d81e927d9d117f792b99f59e83b1d72ea964d92bb440412f3a5e2` (`EK-HAZIR.txt`). Current list: `SHA256-ON-KAYIT.txt`.
