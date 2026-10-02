# Notes from the ASP work to the maintainers (Step 3)

> Everything that may require a change of the plan or the pre-registration is here. Each item: what, why, proposed decision, affected document.
> Status: COMPLETED (25.09.2026). Item numbers are permanent. Source of the numbers: `sorgular/sonuc/rapor_sayilari.json` and the result files named in REPORT.md.

## N1. Adaptation of §2C D1′: 17 decision nodes (applied)
- **What:** The decision variables are at node level (`pqd/1`): a01 a02 a03 a04 a05 a06 a07 a08 a09a a09b a10 a11 a12 a13 ecrl ejvi eas. In the model some classes are represented by several instances (A02 = national TL + 4 EUDI LoTEs; A03 = provider CA + external status CA; A11 = WRPAC + WRPRC; A13 = WebPKI + the OJEU-pinned LOTL download channel); instances in the same node migrate together.
- **Interpretation decisions (approval needed):**
  - Node A09a = the wallet instance key bound by the WIA (§2C W_trust WIA = 1 day); node A09b = the wallet provider signing key (KA and WIA signatures; W_trust KA = 1 year). Rationale: according to H2′ the <24 h validity of the WIA is a token window; a 1-day W_trust can only belong to an instance key renewed per WIA.
  - A13 = the decision "TLS server authentication of fetched artefacts is PQ and classical chains are rejected". While WebPKI is classical (primary) it cannot be selected as PQ (`pq_yasak`); while WebPKI is PQ it is a selectable migration decision.
  - **CORRECTION (25.09):** The earlier version of this item said "`pq_birlikte` (PQ certificate present, classical also accepted) is equivalent to classical under any-valid-path (verified in the OAT)". **This was wrong.** The OAT `webpki_pq_birlikte` changes the family of sets in 63 cells (G1–G3, P4). The node sets stay the same, but the alternative {a13 + `tasi(a00_ojeu, a13_lotl_kanal)`} is added in place of a01. Reason: the certificate of the OJEU-pinned LOTL download channel is published in the OJEU (T002); in the model the OJEU can carry a "PQ required" expectation for this channel (M-f hook), and this closes the classical acceptance under `pq_birlikte`. For the general WebPKI (`a13_webpki`) there is no authenticated per-entity expectation carrier; there `pq_birlikte` really is equivalent to classical. **Decision needed:** will the assumption that the OJEU can carry a PQ expectation for the LOTL channel be taken into the scope of M-f? If not, the fact `tasiyabilir(a00_ojeu, a13_lotl_kanal, m_f)` is removed; the primary results do not change (in the primary configuration WebPKI is classical and A13 cannot be selected).
  - For the unsigned edge artefacts (A06, E_JVI, E_AS), "PQ" = PQ binding at object level (A06: vct#integrity digest; E_JVI: binding of the JWKS to the CA chain with a PQ signature; E_AS: signed AS metadata). If bound, its forgeability reduces to that of the artefact it is bound to; during coexistence the acceptance of the unbound form is the classical alternative.
  - E_CRL is a separate node with its own signing key (CA-class window, 5 y).
- **Affected:** these interpretations are not in the text of pre-registration §2C 2.1; adding them to the frozen version as an "operational mapping" is recommended.

## N2. §2D item 11: ca_baglama and ayni_ad_klasik_ca (applied)
- `ca_baglama ∈ {yok, ad, anahtar}` (primary yok), `ayni_ad_klasik_ca ∈ {yok, var}` (primary yok).
- **Mapping (the same structure as Tamarin R7hx):** "same-name classical CA" is the name relation of the alternative classical CA (ALT_CA) under the same anchor. In ASP the existence of the alternative CA is `diger_ca`, the name relation `ayni_ad_klasik_ca`. Acceptance: `yok` (none) → the alternative always; `ad` (name) → only if it has the same name; `anahtar` (key) → never.
- **Result:** the four combinations of the 2×2 grid and the two sanity configurations matched the expectations written in advance **6/6**. ad/var: 675/675 UNSAT (all 279 minimal sets of the primary configuration falsified); ad/yok, anahtar/yok, anahtar/var: 675/675 identical to the primary configuration. "The flag has no effect while ca_baglama = yok" of §2D item 11 held in two configurations (diger_ca var/yok) with 675/675 + 675/675. The direction is the same as Tamarin R7hx (`X_namebind_unique` V, `X_namebind_samename` F, `X_keybind_distinct` V, `X_keybind_samename` V; `M_no_namebind` F).
- **Expectations before the run:** `sorgular/beklenti_2x2.json`, SHA-256 `c0899c5f3f0d587b62d94ecff1fdd2e4dd6f2c1bafa2c656d067fc93fa895546` (2026-09-25T12:33:27Z). **Transparency:** before the expectation file, the six combinations were run in a single cell (g1, Φ3, P0, fresh, fast) as an implementation smoke test; the expectations were written without seeing any result of the full grid.
- **G5 note:** in Tamarin R7hx G5 and G1 give the same verdict; in ASP the alternative CA path is an introducer (K2) path and appears as a G1 violation. The comparison is via G1.

## N3. Window classes and Tamarin R6 (applied; no rule difference, a mapping note)
- `pencere_sinifi/2` ∈ {uzun_omurlu, donem, belirtec} (long-lived, period, token); `maruziyet/2` (exposure, 0 in the worst case) and `son_kabul/2` (last_accept); W_trust = son_kabul − maruziyet.
- V2/V3 keys are bound with a short-lived certificate issued by the CA (identity = CA chain = R6 `ID_PQ`); `anahtar_yeniden_kullanim = var` = R6 `KEY_REUSE` (the window returns to long-lived). The separate `a07_sert`/`a08_sert` nodes of the earlier draft were removed: with the 17-node binding, the identity and the ephemeral key fell into the same decision and V3 became meaningless.
- The FAST/MEDIUM/SLOW regimes of R6 are symbolic; numerical reading: FAST τ ≤ token window; MEDIUM token < τ ≤ period window; SLOW τ > period window. With the primary values of §2C (TTL 1 d; V2 window 1 d + 1 d) **the nominal "medium" τ = 3 days falls into the SLOW class of R6 for V2.** This is not a rule difference but a numerical mapping: a rotated key is protected in ASP under the medium and slow nominal regimes; in R6 terms these two cells are SLOW. The MEDIUM class appears only in the A5 grid (TTL 1 h; τ 14 h and 1 d; 8 of 8 rows agree: V2 not protected = `E_rot_medium` F, V3 protected = `P_tok_medium` V).
- **Result:** 588/588 cells within the scope of R6 agree; in the KEY_REUSE cells A08 is required 6/6 (same direction as `M_rot_reuse`). **The ASP rules were not changed in response to the R6 results.**
- **Transparency (after results were seen, only in the comparison script):** the first comparison showed two classification errors, fixed in `analiz.py`. (a) The window of the V1 key was read wrongly in the classification. (b) When τ exceeds the TLS window, the fetched status token is also protected by classical transport; R6 has no transport. These 42 cells (`TASIMA_KORUR`) and the 42 cells in which τ also exceeds the long-lived window (`UZUN_OTESI`) were left out of scope and reported separately (`analiz/r6_esleme.csv`).

## N4. Path of the strategy file (Ö5)
- According to Ö5 the frozen file is `model\comparison\stratejiler.yaml`. The ASP work has no write permission there. Draft: `models\asp\sorgular\stratejiler_taslak.json` (version 2, SHA-256 `11b05877024f49e01df19ec906468ba7b59240cf8ba9c1ee8c76df788c131e41`, 2026-09-25T12:34:31Z). Version 1 (`b749dd47…`, 24.09) belonged to the artefact-level model before §2C; it was changed before any comparison was run. Moving it into the YAML and freezing it in Step 8 is recommended.
- S5e (S5 sets + P4 + M-f) is **exploratory**: added to separate the effect of the order from the effect of the expectation; not in the pre-registration.

## N5. Sampling frame of the technical gate (§2F item 2): exported, NO SAMPLE SELECTED
- **`models/asp/sampling/cerceve.jsonl`**: in the primary configuration, every minimal set ("asgari") of every cell of Q (675 cells) and every set with one element of a minimal set removed ("bir-eksik"; if the same set arises from several sources in the same cell, one row, sources listed).
  - **Rows: 2,442** · **SHA-256: `0a9b10d169a2898b97a6463fc481385a359744a981c392560ad0355f01942d87`**
  - Strata (goal × type): G1 minimal 81 / one-short 546; G2 117 / 1,071; G3 81 / 546; **G4 and all: 0 rows.** Cells with rows: 189.
  - Why G4/all are empty: see N7. For the selection script the number of non-empty strata is 6 (§2F: the remaining samples are completed from the whole frame with the seed).
  - Consistency check: all 279 "minimal" rows are `verified`, all 2,163 "one-short" rows are `falsified` (computed in the evaluation mode, not assumed).
- **`models/asp/sampling/kesif_2x2.jsonl`**: the exploratory grid of §2D item 11 {ca_baglama: ad, anahtar} × {ayni_ad_klasik_ca: yok, var} (diger_ca = var, klasik_sabit): minimal + one-short in the SAT cells; in addition, in every cell the verdict of the primary minimal sets in that cell ("birincil-kume").
  - **Rows: 8,442** · **SHA-256: `c1e810c8c5f077790e9feb27ab6ddd8c0031ac3019a2d0c1503a4a2e5a3fb2ec`**
  - Strata (goal × type): G1 minimal 243 / one-short 1,638 / primary set 324; G2 351 / 3,213 / 468; G3 243 / 1,638 / 324. Cells with rows: 756.
  - Combination × type: ad/yok 279 + 2,163 + 279; anahtar/yok and anahtar/var the same; **ad/var: only 279 "birincil-kume" rows, all `falsified`** (name binding is circumvented by a same-name classical CA; since all G1–G3 cells in ad/var are UNSAT there are no minimal/one-short rows). The mandatory extra sample of §2F can be chosen from this type (template `R7_mh_x.spthy`: CA_PQ, ALT_CA, NAME_BIND, ALT_SAME_NAME).
- Format: `sampling/SCHEMA.md`; summary: `sampling/disa_aktarim_ozeti.json`.

## N6. The pre-registered expectation of S2 did not hold (0 expected, 9 observed)
- **What:** the 3rd pre-registered question of the strategy comparison is "How many cells do S1 and S2 satisfy after Q-day? (expected 0; sanity)". S1: 0 (held). **S2 (ECCG AND, P1, no expectation): 9 cells** (cl; G1–G3 × Φ3 × 3 τ). 15 while WebPKI is PQ.
- **Why:** in Φ3 no entity's classical alternative is accepted (class-level sunset). Then no expectation channel is needed: if all nodes are PQ, G1–G3 are satisfied. "Expected 0" did not take into account the sunset reading of Φ3. In the 24 cells of Φ1/Φ2, S2 is 0/24 (consistent with the expectation).
- **Proposed decision:** read the expectation as "0 in Φ1/Φ2", and write the difference into §11 after the results were seen. The result was not changed.
- **Affected:** pre-registration strategy comparison (sanity question), REPORT §4.2.

## N7. G4 and "all" cannot be satisfied in the primary configuration (135 + 135 cells UNSAT)
- **What:** in the primary configuration G4 cannot be satisfied with any PQ set: an unsigned request is accepted under HAIP (T281), its origin is authenticated by the classical WebPKI (T282), the WRPRC verification is postponed (phase 0, T254); hence there is no authenticated per-RP expectation carrier. "All" contains G4, so it is UNSAT as well.
- **Consequences:**
  - The G4/all strata of the gate frame are empty (N5).
  - Denominator of M1 is 36 cells: no strategy except S3 (M-d, out of band) can satisfy the 9 cells of G4 while WebPKI is classical.
  - In the primary configuration of H4, the G4 cells are "neither satisfies" (9).
- **This is a finding** (the formal counterpart of the M-b0 trace and of the G4 side of H1), not a model error. The OAT `wrprc_faz1` makes the G4/all P4 cells SAT (54 cells; G4 set {a02, a11, a12} + `tasi(a11_kayit, a12_istek)`). `md_kanca_acik` also makes the same 54 cells SAT.
- **Proposed decision:** (a) whether a separate exploratory stratum for G4 (e.g. from `wrprc_faz1` or from the WebPKI-PQ cells of the H1 design) is added to the technical-gate sample. This is the maintainers' choice, not the ASP work's; if wanted, a second frame file can be produced in the same format. (b) Report the primary result of G4 in the paper as "unless WRPRC verification is mandatory, the RP identity cannot be carried into PQ".

## N8. Interpretation of the H4 (2a) classification (approval needed)
- **What:** `sorgular/h4.py` compares S5 with S7 per cell and classifies the difference as follows:
  - **insufficient (expectation):** S5 + P4 + M-f (S5e) satisfies it. This stems from H3 (Ö2); it does not count as (2a).
  - **insufficient (node):** if the missing node is in G4 or A13 or is a short-window key, a (2a) candidate. If the missing nodes are long-lived (Ö3), it does not count.
  - **wasteful (τ):** the excess of S5 is a short-window key that is required in the fast-τ counterpart of the same cell. This is a (2a) candidate.
  - **wasteful (other):** the excess is off-path or long-lived nodes; does not count.
- **Primary 36 cells:**
  - insufficient (node) 12: in G1/G2 Φ1 missing {a04, a07}, in G3 Φ1 {a04, a08}, in G3 Φ2 {a08}. All are V1 or the CA key, i.e. long-lived; not counted under Ö3.
  - insufficient (expectation) 6: G1/G2 Φ2.
  - wasteful (other) 9: G1–G3 in Φ3.
  - neither satisfies 9: G4.
- **Interpretation question:** the 9 wasteful cells in Φ3 fit the letter of (2a) ("S5 migrates at least one artefact class too many, M2 difference ≥ 1"). But the excess comes from the Φ3 definition of S5 ("ALL") and from the goal-specific cell definition. The same difference exists in S2, S3, S4 and S6; the excess nodes (10–11 nodes) are not on the goal path. Counting them as (2a) would trivialise the condition (contradicts DO-NOT #18). **I did not count them; the decision is the maintainers'.**
- **10 candidates in the Ö3 cells:**
  - G4 unsigned request + WRPRC phase 1 (cl/pq × Φ1/Φ2), 4 cells: a11/a12 missing in S5 → insufficient (node).
  - `G2_cnf1g_{orta,yavas}`: a10 in excess → wasteful (τ).
  - `G3_durum_{gunluk,gecici}_{orta,yavas}`: a08 in excess → wasteful (τ).
  - The additional condition of (2a) requires at least one Tamarin instance for each of them; none yet.
- **Transparency (definitions changed after the results were seen):**
  - The H4 filter at first also counted long-lived V1 keys; it was made regime-aware.
  - In the named A.3.2.2 cells, M-b0 (unsigned request) masked the difference; these cells were redefined with `wrprc_dogrulama = faz1`.
  - The model rules did not change.

## N9. Policy equivalence and P3
- P0, P1 and P2 give the same result in this abstraction: in all 10,305 cell groups of the groups birincil, h1, h2, h5, cab, oat and tau the family of minimal sets of the three policies is identical. Reason: one signature with a broken classical key is enough. The differences of stripping and key–alg binding are at implementation level and belong to C3.
- **P3** (expectation via the classical channel):
  - in S2 with unbounded k, UNSAT in Φ1/Φ2.
  - with k = 1, SAT if only G1 is considered (OAT k1): the classical channel alone does not open a forgery.
  - G1+G5 together are UNSAT also with k = 1, because the untimed G5 is violated.
  - in S1 (no break), G1+G5 and "all" are satisfied with ∅.
- **Proposed decision:** the H3 evaluation should state explicitly that the untimed definition of G5 (Ö11) drops P3 independently of k.

## N10. Sensitivity to the k budget: a fetched artefact = two breaks
- The OAT `k1` changes 297 cells (108 of them UNSAT→SAT). Since forging a fetched artefact with k = 1 requires breaking both the signing and the transport key:
  - the G1/G2 set becomes {a03, a04, a07 (+a10)}; a01/a02 drop out.
  - **G3 is satisfied with ∅**, because the status token is fetched.
- `k3` changes only 9 cells: a01 drops out with a pinned anchor + Φ1 + P4. Dropping the TL expectation via the LOTL needs 4 breaks: {a01_lotl, a13_lotl_kanal, alt(a02_tl), a13_webpki}. Verified in the evaluation mode: these four keys together violate G1; none of the four triples does.
- **Proposed decision:** report k in the paper as an OAT (the primary k stays unbounded). It should be written that the condition "no substitution with classical transport" of H1 depends on the assumption of **unbounded k**.

## N11. The time limit of H1: τ > TLS window
- In 42 cells of the A5 grid (`TASIMA_KORUR`) τ exceeds the window of the TLS server key. The fetched status token is also protected by classical transport: condition (ii) of H1 does not hold for these τ.
- Since the primary w_tls = 1 y and the nominal τ ≤ 26 d, this limit does not show in the primary and 2.4 designs.
- The OAT `w_tls_47g` alone has no effect (0 cells), because nominally τ ≤ 26 d < 47 d.
- The combination **w_tls 47 d + τ ≥ 47 d** (the shortening TLS certificate lifetime of the CA/B Forum + a slow CRQC) has two deviations, so it is not in the OAT.
- **Proposed decision:** report this combination in the paper with an exploratory cell as "the scope limit of H1". If wanted, it can be added with a single query.

## N12. Cached anchor, sdjwtvc and what stays outside the model
- In the steady state `onbellek` (cached) is the same as `taze` (fresh) (225/225 cells). The first window of a copy filled before Q-day was modelled with the OAT `onbellek_ufku = ilk_pencere`: in all 63 cached SAT cells a01 and a02 drop out.
- `sdjwtvc_surum` has no effect in the formal model (OAT 0 cells). The -13/-19 differences of §2D item 7 belong to the C3 test vectors.
- **The KATs (optional) were not implemented; left to Step 6.** The drafts in `literatur\analiz\KAT-SPEC.md` are in a form that can be given directly to the core as fact files.
- M3 (bytes) and M4 (rejected old issuer) are **structural proxies**; the real measurements are in Step 12 and C3.

## N13. Model-specific defaults (parameters not in the §2C table)
- Parameters not in the §2C 2.3 table were kept conservative or at the specification default:
  - kimlik_turu pid, guven_deposu combined (T033, T034), anahtar_cozumleme x5c, lotl_indirme OJEU-pinned (T002), durum_imzaci same CA, durum_baglama strict, durum_kanali fetched;
  - istek_iletimi DC API, acceptance of unsigned requests/metadata present (T281, T086), tmd_isleme none (T096), durum_listesi present, tek_kullanim wallet (T230);
  - wscd_pq present, diger_ca none, coklu_cerceve none, mechanism hooks off;
  - clock skew 300 s (T392).
- Their OAT effects are in REPORT §4.5. The most influential: `diger_ca` (189 cells SAT→UNSAT), `guven_deposu_liste_bagli` (135; a01 drops out), `durum_listesi_yok` (135).
- **Proposed decision:** write these defaults into the frozen pre-registration with an "operational mapping" annex (together with N1).

## N14. Looking ahead: beklenti_kapsami and A1
- `beklenti_kapsami ∈ {yaprak_alg, yol_sinifi, anahtar}` of §2D item 13 is not yet a parameter in the model. The `kenar/3` ids and the `tasi/2` hook are ready for adding it via the edge classes of the accepted path (Step 7).
- The A1 necessity matrix was derived from the frame. 2,163/2,163 of the one-short rows violate the goal of their cell. Violations of other goals carry no information, because the sets are goal-specific.

## N15. Limitation: a single model author
- ASP, z3 and the Jacobi evaluator came from the same work. The independence is at method and code level: z3 does not read the ASP core and uses CEGAR at finite k. The real independent verification is the Tamarin sampling of the technical gate.
- **Proposed decision:** state this limitation explicitly in the technical-gate report.
