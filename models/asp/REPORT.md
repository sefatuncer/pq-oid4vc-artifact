# Step 3 — ASP system model (Layer 1 of the proven abstraction)

- **Date:** 24–25.09.2026 · **Work:** asp (Step 3) · **Folder:** `models/asp/` (written only to this folder)
- **Tools:** clingo 5.8.2 + z3 5.1.0, image `pq-a02-solver:1.0` (container names `pq-a03-…`; `calistir.sh`). Tamarin was not run.
- **Binding inputs:** pre-registration §2A (Ö1–Ö12), §2C (D1′: 17 nodes, primary configuration), §2D (item 11 `ca_baglama`, `ayni_ad_klasik_ca`), §2F (item 2 frame rule); `gozden-gecirme/adim-01.md`, `adim-04.md`, `literatur.md`; Tamarin R1–R7 (`models/tamarin/`).
- **Evidence rule:** every number in the report was compiled by script from the files under `sorgular/sonuc/`, `z3/sonuc/`, `regresyon/sonuc/`, `sampling/` (`sorgular/rapor_sayilari.py` → `sorgular/sonuc/rapor_sayilari.json`). A verdict given by hand is not evidence.

(Translated from Turkish for this release; numbers are written in English notation. File, predicate and parameter names are kept as in the code; `docs/GLOSSARY.md` translates them.)

## 0. Summary

| Acceptance criterion (ASP part of the technical gate) | Result |
|---|---|
| All queries are solved; times are reported | **52,693 queries solved** (10 groups); 80,291 minimal sets. Total ASP wall time 224.8 s (CPU 2,106.8 s); longest single query 2.01 s (k=3). **D1′ primary count (Q = 675): wall 1.95 s, longest query 0.088 s** (criterion <10 min) |
| ASP–z3 agreement 100% | **52,693/52,693 queries, 80,291/80,291 minimal sets identical.** The z3 encoding was written independently; a different method for finite k (CEGAR, 4,705 counterexamples). Additionally: three-way random check (ASP, z3, Jacobi) **7,000/7,000** (seed 20260928) |
| Pilot P2 regression | The pilot's record was reproduced **48/48**; the new core and z3 gave the pilot's 82 minimal sets identically in **48/48** queries; P2b order identical |
| Any-valid-path / key class; Tamarin datalog 44 verdicts | The system core agrees with **44/44** Tamarin verdicts (ASP = z3 = Jacobi 44/44). The naive reading (real parent only) again fails only at `R1 X_alt_ca` |
| ≥10 sampling exports | As required by §2F **no sample was selected; the whole frame** was exported: `sampling/cerceve.jsonl` **2,442 rows** (SHA-256 `0a9b10d1…42d87`), `sampling/kesif_2x2.jsonl` **8,442 rows** (SHA-256 `c1e810c8…fb2ec`); the expected verdicts were computed in ASP (minimal → verified 279/279; one-less → falsified 2,163/2,163) |
| PRELIMINARY results for H1/H2/H4/H5 | Tabulated (§8). **All "preliminary"; to be verified at the scientific gate** |

**Additional checks:** `ca_baglama` sanity check 675/675 + 675/675; the 2×2 grid matched the 6/6 expectations written in advance (same direction as Tamarin R7hx); R6 window-class mapping 588/588 within the scope of R6; strategy evaluations three-way 648/648, H4 comparisons 109/109; in the optimal orders ASP-DP = Jacobi-DP 36/36.

**Main (preliminary) findings:**
1. **In the primary configuration G4 (and "all") cannot be satisfied with any PQ set** (135/135 G4 cells UNSAT): the unsigned request is accepted as required by HAIP (T281), its origin is verified by the classical WebPKI (T282), WRPRC verification is postponed (faz0, T254) → there is no authenticated per-RP expectation carrier. In the `wrprc_faz1` OAT, the G4/all P4 cells turn SAT (54 cells).
2. **H1 (preliminary): supported.** When the WebPKI is PQ, the nodes in the fetched context (A01, A02, A06, A08, E_JVI, the A03/A04 chain inside the status token) can drop out of the minimal set; in the conveyed context no node drops; at nominal τ there is no substitution with classical transport.
3. **H2′ (preliminary): supported.** With the status signing key in mode V2/V3, A08 leaves the set between fast → medium τ; in V1 it does not leave at any τ. Falsification (i) (effect of the token lifetime with a fixed key window) 0/32; (ii) in 66/180 groups the set changes with τ.
4. **H5 (preliminary): supported.** Single use (wallet / verifier) changes the set in no cell; at medium/slow τ only the cnf window (1 day) drops A10. The exception is the boundary variant that needs shared state (global single use + passive collector).
5. **H4 (preliminary): there are candidates.** The differences in the 36 primary cells come from long-lived keys, missing expectations or, in Φ3, off-path nodes; they were not counted under the Ö3 interpretation (awaiting approval, DECISION-NOTES N8). 10 candidates in the Ö3 cells: G4 (no A11/A12 in the Φ1/Φ2 set of S5) and τ-induced waste (A10 at cnf 1 d; A08 in V2/V3).

## 1. Model definition

### 1.1 Artefacts, edge artefacts and decision nodes (§2C D1′)

**Convention** (Tamarin R1–R5, same as pilot P2): `pq(A)` ⇔ the **key that signs** A is PQ (or composite). For unsigned artefacts (A06, E_JVI, E_AS) `pq(A)` = PQ binding at object level (digest or PQ-signed representation); if bound, its forgeability reduces to that of the artefact it is bound to (`pq_baglar/2`).

**17 decision nodes** (`pqd/1`; instances in the same node migrate together; `olgular/artefaktlar.lp`). The last column lists the T-rows assigned to that artefact in `traceability/izlenebilirlik.csv` (extracted from the matrix by script; rows in parentheses are assigned to another artefact but determine the interpretation of this node):

| Node | Model instances | Signing key / meaning | W_trust (primary) | Basis |
|---|---|---|---|---|
| a01 | a01_lotl | LOTL signer (pinned in the OJEU) | 5 yr | T001–T007 |
| a02 | a02_tl, a02_lote_pid, _cuzdan, _erisim, _kayit | TL signers (listed in the LOTL, OR T018); LoTE signers (pinned in the OJEU T029) | 5 yr | T008–T025, T027–T037 |
| a03 | a03_ca, a08_ca | Provider anchor key (listed in the TL/LoTE; forbidden in x5c T043); external status CA (T180, T026) | 5 yr | T038, T043, T063, T069 |
| a04 | a04_ihr | CA key (issuer, status and metadata signer certificates; T160, T161, T084) | 5 yr | T039, T041–T042, T044–T047 |
| a05 | a05_meta (+ unsigned variant) | Metadata signing key; unsigned form is the default (T071, T086) | 1 yr | T070–T087, T393–T394 |
| a06 | a06_tip | Type Metadata digest binding (vct#integrity) | — | T090–T099, T101 |
| a07 | a07_kimlik | Issuer signing key (mode V1/V2/V3) | 1 yr (V1) | T102–T110, T112–T121, T175 |
| a08 | a08_durum | Status signing key (mode V1/V2/V3) | 1 yr (V1) | T026, T145–T174, T176–T180 |
| a09a | a09c_ornek | Instance key bound by the WIA (PoP; T187) | 1 d | T204 |
| a09b | a09a_wia, a09b_ka | Wallet provider signing key (WIA and KA) | 1 yr | T199, T203, T204, T208, T399, T400 |
| a10 | a10_kbjwt | Device (cnf) key; W = credential validity | 30 d | T209–T214, T216–T239 |
| a11 | a11_erisim, a11_kayit | Access CA and WRPRC provider keys | 5 yr | T088–T089, T240–T247, T249–T267 |
| a12 | a12_istek (+ unsigned variant) | RP key (with the WRPAC; not short-lived T261) | 1 yr | T248, T268–T274, T276–T281, T283–T300 |
| a13 | a13_webpki, a13_lotl_kanal | TLS server authentication PQ (cannot be selected while the WebPKI is classical) + OJEU-pinned LOTL download channel (T002) | 1 yr | T275, T282, T302–T309, T311–T313 |
| ecrl | e_crl | Access CA CRL/OCSP signing key | 5 yr | T255, T256 |
| ejvi | e_jvi | JWT VC Issuer Metadata/JWKS: HTTPS only (T309–T311); pq = PQ binding | — | T309–T311 |
| eas | e_asmeta | AS metadata: capability only (M-a; T188, T381); pq = signed form | — | T188, T381 |

The model has 36 artefact atoms (26 signed, 10 unsigned); 29 of them are present in the primary configuration, and 25 decision artefacts are bound to the 17 nodes. Helpers: the OJEU source (`a00_ojeu`), unsigned variants, named cell artefacts (alternative classical CA `a03_diger/a04_diger`, `a11_erisim_diger`, second trust framework `a11_erisim_f2`) and mechanism hooks (`m_d_cfg`, `m_g_oz`, `m_a_alan`).

### 1.2 Edges: any-valid-path (`olgular/kenarlar.lp`)

- `kenar(E,A,B)`: an artefact of class B introduces the key that signs A (binds it via certificates/lists/cnf). **Every introducer accepted by the verifier is a separate OR edge;** A can be forged if any of its accepted introducers can be forged. Basis (with corpus ids; texts verified under `spec-corpus/metin/`): [RFC5280] §6.2 "A system may provide any one of its trusted CAs as the trust anchor for a particular path"; [RFC6840] §5.11 "Validators SHOULD accept any single valid path" (T364) and §6.2 "any DNSKEY in the zone's signed DNSKEY RRset may be used to authenticate any RRset in the zone"; Tamarin R1 `X_alt_ca` (key-class semantics).
- 37 edge facts, 24 edge conditions. **28 of the 28 edges** of `guven-bagimliligi.dot` were mapped (`dot_kenar/4`; in the fact file, not in an appendix of the REPORT).
- Examples of OR edges: in the combined trust store the CA anchor is both in the PID LoTE and in the national TL (T033, T034); the status signer is the same CA or an external CA (both under loose binding); the JVI alternative key path; the alternative classical CA (depending on the binding); the A.3.2.2 second trust framework.
- **`ca_baglama` (§2D item 11):** the edge of the alternative classical CA is a copy with two conditions: `ca_baglama = yok` (none) **or** (`ca_baglama = ad` (name) ∧ `ayni_ad_klasik_ca = var`). Under `anahtar` (key) binding it is never active (same structure as Tamarin R7hx).

### 1.3 Channel classes and transport

| Channel | Delivery rule | Example |
|---|---|---|
| `aktarilan` (conveyed) | Always (brought by the presenter/attacker) | credential, x5c, KB-JWT, request (DC API), WRPAC |
| `sunan_uc` (presenter endpoint) | Always (the source is the party to be authenticated itself; T284) | `request_uri` |
| `cekilen` (fetched) | Only if the server authentication of the transport can be forged | LOTL, TL/LoTE, status list (online), metadata, CRL |
| `yalniz_tasima` (transport only) | The same (no object signature; the only protection is transport) | unsigned metadata, unsigned request (origin), JVI, Type Metadata without a digest |
| `sabitlenmis` (pinned) | Never | OJEU, out-of-band configuration (M-d) |
| `kimliksiz` (unauthenticated) | Always (even S1 changes it) | M-a field |

The forgeability of the transport is the effective forgeability of the artefact that represents the transport (`a13_webpki`, `a13_lotl_kanal`).

### 1.4 Time: windows, key modes, τ (`olgular/pencereler.lp`)

- **exposure(K)** = `maruziyet(A,0)` (worst case: the public key is observed at the start of the window); **last_accept(K)** = `son_kabul(A,L)`; **W_trust = L − E**. S2 can forge an artefact signed with a classical K only if **τ < W_trust + clock allowance**. The rule in pre-registration §4.5 is τ < W_trust(K) (strict inequality); the clock allowance (300 s; T392) is an addition of the model and changes no cell in the OAT (0, 60, 600 s).
- **Window classes** (with Tamarin R6): `uzun_omurlu` ↔ LONG (V1 or KEY_REUSE), `donem` ↔ ROTATED (V2: W = 1 d + token/credential validity), `belirtec` ↔ PER_TOKEN (V3: W = validity; cnf per credential). The V2/V3 keys are bound by short-lived certificates issued by the CA: **identity = CA chain (R6 `ID_PQ`)**; `anahtar_yeniden_kullanim = var` = R6 `KEY_REUSE`.
- **The token lifetime alone is not decisive (Ö1):** it enters W only when the mode binds it to the key. Fixed windows such as TL/LoTE ≤6 months and WIA <24 h are W_accept.
- **τ:** nominal 600 s / 3 d / 26 d; sensitivity fast {1, 10, 60} min, medium {1, 3, 7, 10} d, slow {14, 26, 60} d (§2C 2.3); A5 wide grid 11 values: 84 s … 1,000 d and "∞" (represented by 2.1·10⁹ s ≈ 66.5 yr).
- **k (Ö8):** unbounded (primary) = single scenario `tum`; S1 = scenario `bos`; k ∈ {1, 3} = all subsets with min(k, n) elements of the relevant keys (sufficient, because violation grows monotonically in the set of broken keys). Key ids: A (signer), alt(A) (classical alternative key), `p3_kanal` (classical configuration channel of P3).

### 1.5 Phase, anchor, WebPKI, policy and parameters (primary configuration)

- **Φ (§4.2; Ö10#1):** Φ1 classical alternative in all decision artefacts; Φ2 only in the leaf classes (a05–a12, e_jvi, e_asmeta); Φ3 in none. PKI: a01–a04, a13, e_crl.
- **Anchor (§4.6):** `taze` (fresh); `sabit` (pinned) = TL signing key out of band (R5); `onbellek` (cache) = a time-limited copy of an earlier fetch. In the steady state `onbellek` ≡ `taze` (225/225 cache cells the same in the primary); `onbellek_ufku = ilk_pencere` additionally models the first window of a copy filled before Q-day (OAT).
- **Policy (§4.8):** P0–P2 use no expectation (all three are equivalent in this abstraction: a single signature with the broken classical key is enough); P3 learns the expectation from a classical channel (robust under S1; under k = 1 only when a single target is considered, not together with untimed G5; DECISION-NOTES N9); P4 from a PQ-verified carrier.

| Parameter | Primary | Source |
|---|---|---|
| WebPKI | classical (A13 PQ cannot be selected) | §2C 2.3 |
| k | unbounded | §2C 2.3 |
| iptal_denetimi / cihaz_bagi / rp_auth_fail_open | var / var / yok (yes / yes / no) | §2C 2.3 (T178, T228, T247) |
| wrprc_dogrulama | faz0 | §2C 2.3 (T254) |
| ca_baglama / ayni_ad_klasik_ca | yok / yok | §2D item 11 |
| sdjwtvc_surum | -13 | §2C 2.3 |
| durum_anahtari / ihracci_anahtari / cihaz_anahtari | V1 long / V1 long / per credential | §2C 2.3, Ö1 |
| W_trust: w_kok, w_ca, w_ihracci, w_rp, w_tls, w_wia, w_ka | 5 yr, 5 yr, 1 yr, 1 yr, 1 yr, 1 d, 1 yr | §2C 2.3 |
| kimlik_gecerlilik (cnf), durum_ttl, kbjwt_iat, clock allowance | 30 d, 1 d, 10 min, 5 min | §2C 2.3; clock allowance not in the table (T392 "a few minutes") |
| Model-specific (not in the table; DECISION-NOTES N13): kimlik_turu pid, guven_deposu combined, anahtar_cozumleme x5c, lotl_indirme OJEU-pinned (T002), durum_imzaci same CA, durum_baglama strict, durum_kanali fetched, istek_iletimi DC API, acceptance of unsigned request/metadata yes (T281, T086), tmd_isleme no (T096), durum_listesi yes, tek_kullanim wallet (T230), wscd_pq yes, diger_ca no, coklu_cerceve no, mechanism hooks off | conservative or specification default | DECISION-NOTES N13 |

### 1.6 Goals (`olgular/hedefler.lp`)

G1 credential (+ processed Type Metadata); G2 KB-JWT; G3 status token (if a status list exists); G4 request object (+ accepted unsigned variant); policy violations (`cihaz_bagi = yok` → G2; `iptal_denetimi = yok` → G3; `rp_auth_fail_open = var` → G4). **G5-untimed (Ö11):** violation when a migrated entity on the target path has an open classical alternative and no expectation, or when its unsigned form is accepted. **G2i (exploratory):** issuance-side WIA/KA assurance.

### 1.7 Expectation carriers and mechanism hooks (`olgular/tasiyicilar.lp`)

`tasi(C,X)` (= the `convey/2` hook): C carries a "PQ required" expectation for the entity that signs X; it is a decision variable (it enters the minimal set). 61 carrier facts: **M-f** (OJEU, LOTL pointer, TL/LoTE entry; WRPRC only in faz1), **M-e′** ("required" in signed metadata), **M-h** (certificate extension; hook: effective only if C dominates all acceptance paths and lies on the path of the classical alternative — an alternative CA/JVI path breaks the dominance), **M-g** (self-declaration/TOFU; hook: authentic if the first contact is before Q-day), **M-d** (out-of-band configuration; hook), **M-a** (unauthenticated field; hook). The A3 component hooks (`mf_kapali(tazelik|tekduzelik|kapsam)`) are ready. The expectation closes only K4 and the unsigned variants; it does not close alternative introducer paths (another CA, JVI, second framework) — the binding parameters close those. The `kenar/3` ids are ready for building the Step 7 check `beklenti_kapsami ∈ {yaprak_alg, yol_sinifi, anahtar}` (§2D item 13) over the edge classes of the accepted path.

## 2. Core rules (`cekirdek.lp`) and semantic rationale

Generalisation of pilot/Tamarin K1–K4 (S = breaking scenario):

| Rule | ASP | Rationale |
|---|---|---|
| K1 (timed) | `basar(S,A) :- kirilir(S,A).` `kirilir` = classical ∧ breakable in the scenario ∧ τ < W + allowance | R1, R4, R6 |
| K2 (any-valid-path) | `basar(S,A) :- kabul_alti(A,B), etkin_sahte(S,B), not sabit_etkin(A).` | R1 X_alt_ca; RFC 5280 §6.2; `sahte(B)` = an arbitrary accepted instance of class B can be produced |
| K3 (expectation) | `beklenir(S,X) :- tasi(C,X), mekanizma_uygun(C,X), p(politika,p4), not etkin_sahte(S,C), ...` (P3: additionally `not p3_kirik(S)`) | R2, R3 |
| K4 (timed) | `basar(S,A) :- kirilir_alt(S,A), not beklenir(S,A).` | R2 (coexistence) |
| Unsigned | always minted if not bound; if PQ-bound, its forgeability is that of what it is bound to | T071, T090, T309 |
| Channel | `sahte = basar ∧ ulasir ∧ ¬ozgun`; fetched/transport-only is delivered only if the transport is forged | R3a, H1 |
| Variant | `etkin_sahte(A)` = sahte(A) ∨ (accepted unsigned form ∧ ¬beklenir(A) ∧ sahte(form)) | M-b0 (T281) |

(`basar` = can be produced, `kirilir` = breaks, `kabul_alti` = accepted below, `etkin_sahte` = effectively forged, `beklenir` = is expected, `ulasir` = is delivered, `ozgun` = authentic.)

The semantics is stratified for every scenario; the dependency graph is acyclic (the z3 encoder raises an error on a cycle; Jacobi converges in at most 8 rounds). The family of secure sets is upward closed (adding PQ or a carrier adds no attack), so the subset-minimal sets of `domRec` and the single-element reduction of z3 give the same sets.

## 3. Query catalogue (`sorgular/katalog.py`; §2C distinction)

| Group | Kind | Definition | Queries |
|---|---|---|---|
| birincil | **primary** | Q = goal{G1–G4, all} × Φ × τ{3} × anchor{3} × policy{5} | 675 |
| h1 | **2.4 design** | WebPKI{cl, pq} × 8 channel-label variants × Q ((cl, primary) = primary) | 10,125 |
| h2 | **2.4 design** | {status, issuer} key × mode{V2, V3} × Q (V1 = primary) | 2,700 |
| h5 | **2.4 design** | cnf window 1 d × Q (30 d = primary) | 675 |
| h4 | **2.4 design** | Ö3 named cells + fidelity cell | 89 |
| cab | exploratory | §2D item 11 2×2 × Q (2,700) + `ca_baglama = yok` sanity check × Q (3 configurations: alternative CA present × flag {yok, var}; no alternative CA × flag var; 2,025) | 4,725 |
| oat | sensitivity | one-parameter deviation from the primary (46 deviations) × Q | 31,050 |
| tau | sensitivity | τ sensitivity values × Q (without τ) | 1,575 |
| a5 | additional (Ö1 evidence grid) | key mode × token lifetime × wide τ; clock allowance boundary | 964 |
| h | named | H0, H3-preliminary, H5 single use, R6 KEY_REUSE, M-g/M-h/M-d/M-a hooks | 115 |
| **Total** | | | **52,693** |

Every query: `asgari_kumeler()` (clingo `--heuristic=Domain --enum-mode=domRec`, decision atoms `pqd/1` and `tasi/2`). Times (summary in `sorgular/sonuc/<group>.json`):

| Group | Queries | SAT | UNSAT | Minimal sets | ASP wall (s) | ASP longest (s) | z3 equal | z3 wall (s) | z3 longest (s) | CEGAR |
|---|---|---|---|---|---|---|---|---|---|---|
| birincil | 675 | 189 | 486 | 279 | 1.95 | 0.088 | 675/675 | 0.46 | 0.069 | 0 |
| h1 | 10,125 | 3,897 | 6,228 | 7,434 | 32.93 | 0.127 | 10,125/10,125 | 10.70 | 0.194 | 0 |
| h2 | 2,700 | 804 | 1,896 | 1,140 | 9.13 | 0.160 | 2,700/2,700 | 2.48 | 0.091 | 0 |
| h5 | 675 | 189 | 486 | 255 | 2.10 | 0.052 | 675/675 | 0.68 | 0.080 | 0 |
| h4 | 89 | 58 | 31 | 73 | 0.73 | 0.091 | 89/89 | 0.20 | 0.051 | 0 |
| cab | 4,725 | 756 | 3,969 | 1,116 | 16.30 | 0.099 | 4,725/4,725 | 4.14 | 0.199 | 0 |
| oat | 31,050 | 8,604 | 22,446 | 68,142 | 151.85 | 2.007 | 31,050/31,050 | 252.46 | 201.848 | 4,668 |
| tau | 1,575 | 441 | 1,134 | 639 | 5.70 | 0.124 | 1,575/1,575 | 1.70 | 0.155 | 0 |
| a5 | 964 | 964 | 0 | 964 | 3.69 | 0.076 | 964/964 | 0.93 | 0.056 | 0 |
| h | 115 | 89 | 26 | 249 | 0.44 | 0.048 | 115/115 | 1.42 | 1.236 | 37 |

(10 parallel processes; WSL2 container with 12 vCPUs. The longest z3 query is `oat|md_kanca_acik|tum|f1|hizli|taze|p4`: with the out-of-band configuration hook open, the carrier combinations explode and the cell has **5,888** minimal sets; single-element reduction and blocking grow linearly with this number. ASP counts the same cell in 0.52 s: grounding 0.04 s, solving 0.48 s.)

## 4. Result tables

### 4.1 Primary configuration (Q = 675)

Number of SAT cells (over τ × anchor = 9 cells; `sorgular/sonuc/analiz/birincil.csv`):

| goal | Φ | P0 | P1 | P2 | P3 | P4 |
|---|---|---|---|---|---|---|
| G1, G2, G3 | Φ1 | 0/9 | 0/9 | 0/9 | 0/9 | 9/9 |
| G1, G2, G3 | Φ2 | 0/9 | 0/9 | 0/9 | 0/9 | 9/9 |
| G1, G2, G3 | Φ3 | 9/9 | 9/9 | 9/9 | 9/9 | 9/9 |
| G4, all | Φ1–Φ3 | 0/9 | 0/9 | 0/9 | 0/9 | 0/9 |

Minimal sets (nodes; fresh anchor; the same for the three values of τ):

| Goal | Φ3 (P0–P4) | Φ2, P4 | Φ1, P4 |
|---|---|---|---|
| G1 | {a01, a02, a03, a04, a07} | the same nodes + `tasi(a02_lote_pid, a07_kimlik)` or {+a05} + `tasi(a02_lote_pid, a05_meta)`, `tasi(a05_meta, a07_kimlik)` | the Φ2 sets + 5 PKI carriers: `tasi(a00_ojeu, a01_lotl)`, `tasi(a00_ojeu, a02_lote_pid)`, `tasi(a01_lotl, a02_tl)`, `tasi(a02_lote_pid, a03_ca)`, `tasi(a02_lote_pid, a04_ihr)` |
| G2 | G1 ∪ {a10} | the G1 sets ∪ {a10} + a carrier for a10 (PID LoTE or metadata): 4 sets | the same + 5 PKI carriers: 4 sets |
| G3 | {a01, a02, a03, a04, a08} | the same + `tasi(a02_lote_pid, a08_durum)` or {+a05} + metadata path | the same + 5 PKI carriers |
| G4, all | UNSAT | UNSAT | UNSAT |

- **Anchor:** `sabit` drops a01 in 54 cells (R5): 9 in Φ2-P4, 45 in Φ3. It does not drop it in Φ1-P4 (9 cells), because in coexistence the classical alternative of the TL is closed only by the expectation carried by the LOTL (`tasi(a01_lotl, a02_tl)`). **225/225** of the `onbellek` cells are the same as their `taze` counterpart (steady state).
- **Policy:** in Φ1/Φ2, P0–P3 are UNSAT (no expectation, or the classical channel of P3 is forged under S2): the preliminary signal of H3. In Φ3, P0–P4 give the same sets.
- **Why G4 is UNSAT:** unsigned request (M-b0) → origin → classical WebPKI. The only authenticated per-RP carrier is the WRPRC and it is active only in faz1; out-of-band configuration (M-d hook) also opens G4 (OAT). This is the G4 face of H1 and the formal trace of M-b0 (DECISION-NOTES N7).

### 4.2 Strategies S0–S8 × M1–M5 (PRELIMINARY; `sorgular/stratejiler.py`)

Draft assignment: `sorgular/stratejiler_taslak.json` version 2 (SHA-256 `11b05877…`; before the comparison). M1 = 36 cells (G1–G4 × Φ × τ; fresh); 648 evaluations, three-way 648/648.

| Strategy | M1 (cl) | M1 (pq) | M2 nodes Φ1/Φ2/Φ3 (weighted), cl | M3 proxy | M4 structural | M5 (WSCD) |
|---|---|---|---|---|---|---|
| S0 status quo (HAIP + out-of-band classical; Ö5) | 0/36 | 0/36 | 0/0/0 | 0 | 0 | no |
| S1 credential first | 0/36 | 0/36 | 1/1/1 | 0 | 1 | no |
| S2 ECCG AND, without expectation (P1) | 9/36 | 15/36 | 16/16/16 (122) | 2 | 1 | yes |
| S3 composite + out of band (M-d) | 36/36 | 36/36 | 16/16/16 (122) | 2 | 0 | yes |
| S4 8725bis local, classical source (P3) | 9/36 | 15/36 | 16/16/16 (122) | 2 | 0 | yes |
| S5 root and device first (P1) | 9/36 | 12/36 | 4/6/16 (110/112/122) | 2 | 1 | yes |
| S5e (exploratory: S5 + P4 + M-f) | 15/36 | 18/36 | 4/6/16 | 2 | 0 | yes |
| S6 big-bang (P4 + M-f) | 27/36 | 30/36 | 16/16/16 (cl), 17 (pq) | 2 | 0 | yes |
| S7 computed (P4) | 27/36 | 33/36 | 5–6 per cell (pq: 1–7) | — | — | 9/27 cells (cl); 12/33 (pq) |
| S8 temporary resistance (Anchuri) | 6/36 | 11/36 | 13/13/13 (119) | 2 | 0 | no |

- **Pre-registered questions (cl):** (1) Does S5 satisfy every cell that S7 satisfies? **No:** S7 satisfies 27 cells, S5 9 cells; the 18 cells where S5 falls short are the G1–G3 cells of Φ1/Φ2. (2) Does S5 require extra artefacts? **Yes, in 9 cells:** in Φ3, S5 migrates all 16 nodes, and those not on the target path are surplus. (3) How many cells do S1 and S2 satisfy after Q-day? **S1: 0; S2: 9.** The expected 0 held only for S1. S2 (P1, without expectation) satisfies the G1–G3 cells of Φ3, because Φ3 has no classical alternative: a class-level sunset is enough even without an expectation channel (DECISION-NOTES N6).
- **S3 36/36:** because the out-of-band (M-d) expectation is assumed pinned and authentic; the operating cost (per-entity configuration at every verifier) is not in the model (limitation).
- **S8** (draft definition: V3 issuer and status key, cnf per credential, long-lived identities PQ, P4 + M-f): under cl it satisfies **only G3, at medium and slow τ** (6 cells). The window of the status key is 1 d TTL < τ. In G1 the V3 window of the issuer key (30 d validity) and in G2 the cnf window (30 d) are longer than the nominal τ values; therefore it does not satisfy them. No WSCD change is needed (M5 = no).
- M3 and M4 are **structural proxies** (byte measurement in Step 12; no entity-level population model).

### 4.3 ca_baglama 2×2 and sanity check (§2D item 11; exploratory)

The expectations were written before the run: `sorgular/beklenti_2x2.json` (SHA-256 `c0899c5f…`; a single-cell smoke test had been run earlier — DECISION-NOTES N2). Configuration: alternative classical CA present (outside the strategy), Q = 675.

| Combination | Result | Expectation | Tamarin R7hx |
|---|---|---|---|
| ad / yok | 675/675 cells the same as the primary | protects ✓ | X_namebind_unique = V |
| ad / var | G1–G4 and all: 675/675 UNSAT; 279/279 of the primary minimal sets are falsified in this cell | bypassed ✓ | X_namebind_samename = F |
| anahtar / yok | 675/675 the same as the primary | protects ✓ | X_keybind_distinct = V |
| anahtar / var | 675/675 the same as the primary | protects ✓ | X_keybind_samename = V |
| sanity: yok, alternative CA present | flag yok and var: 675/675 UNSAT in both (all 189 SAT cells of the primary drop); the two flag values are the same 675/675 | flag has no effect ✓ | M_no_namebind = F |
| sanity: yok, primary (no alternative CA) | flag var: 675/675 the same as the primary | flag has no effect ✓ | — |

(Tamarin column: the G1/G5 verdicts in the R7h/R7hx table of `models/tamarin/REPORT.md`; V = verified (protects), F = falsified (bypassed). The lemma names were read from there.)

Fidelity cells (Ö3: "evidence of model fidelity", RFC 6840 §6.2, Kim et al. M2; (2a) not counted; SADAKAT rows of `h4.json`, P4): if the alternative classical CA cannot be migrated (`klasik_sabit`) and `ca_baglama = yok`, G1 is UNSAT in Φ1–Φ3; if `ca_baglama = ad` (CA with a different name), it is SAT with the primary sets. If the alternative CA migrates with the same node (`karar`), G1 is SAT in Φ2/Φ3 and UNSAT in Φ1.

### 4.4 Tamarin R6 window-class mapping (A5 G1/G3; `analiz/r6_esleme.csv`)

The regimes of R6 are symbolic; numerical reading: FAST τ ≤ token window; MEDIUM token < τ ≤ period window; SLOW τ > period window (below the long-lived window). Of the 672 G1/G3 cells of the A5 grid, in the 588 cells within the scope of R6 (class counts: long/LONG 196; V2 FAST 140, MEDIUM 4, SLOW 52; V3 the same) ASP and the R6 condition (G3 V ⇔ ID_PQ ∧ ¬KEY_REUSE ∧ ((PER_TOKEN ∧ (MEDIUM ∨ SLOW)) ∨ (ROTATED ∧ SLOW))) **agree 588/588**; the identity (CA chain) is required in every compared cell. 84 cells out of scope: 42 `TASIMA_KORUR` (τ > TLS window: the fetched status token is also protected by classical transport — R6 has no transport), 42 `UZUN_OTESI` (τ > long-lived window). In the named KEY_REUSE cells (`h|R6_reuse_*`: V2/V3 + reuse × 3 nominal τ) A08 is required in six of the six cells (same direction as R6 `M_rot_reuse`: G3 = F, `M_long_key` = V).

**Numerical mapping (not a difference, a reading note):** with the §2C primary values (TTL 1 d; V2 window 2 d) the nominal "medium" τ = 3 d falls into the **SLOW** class of R6 for V2; therefore in ASP the rotated status key is protected in the medium and slow nominal regimes. For the credential (30 d), however, all nominal τ values are in the FAST class. MEDIUM appears only in A5: with TTL 1 h, in the cells τ ∈ {14 h, 1 d} V3 is protected and V2 is not (R6 L-D3 grid: `E_rot_medium` = F, `P_tok_medium` = V). Eight of the eight MEDIUM rows agree.

### 4.5 OAT sensitivity (Q × 46 deviations; `analiz/oat.json`)

| Deviation | Changed cells (/675) | SAT→UNSAT | UNSAT→SAT | Goals |
|---|---|---|---|---|
| k1 | 297 | 0 | 108 | G1 81, G2 81, G3 135. With a single break a fetched artefact cannot be forged (signature + transport = 2 breaks): G1/G2 set {a03, a04, a07 (+a10)}, a01/a02 drop; **for G3 ∅ is enough** (the status token is fetched). UNSAT→SAT: Φ1/Φ2-P3 in G1/G2 (36), Φ1/Φ2-P0…P3 in G3 (72) |
| k3 | 9 | 0 | 0 | G1–G3, only pinned anchor + Φ1 + P4: a01 drops. Dropping the TL expectation via the LOTL needs 4 breaks: {a01_lotl, a13_lotl_kanal, alt(a02_tl), a13_webpki}. Verified in evaluation mode: against the k3 set these four keys together violate G1, none of the four triples does |
| diger_ca_var (ca_baglama yok) | 189 | 189 | 0 | G1–G3 (fidelity cell: alternative classical CA path) |
| guven_deposu_liste_bagli | 135 | 0 | 0 | G1–G3: a01 drops (anchor only in the OJEU-pinned PID LoTE; no national TL path) |
| durum_listesi_yok | 135 | 0 | 72 | G3 (revocation by expiry; no status list path) |
| md_kanca_acik | 108 | 0 | 54 | in G1–G3 Φ1/Φ2-P4 the set family grows (e.g. G2 Φ1: 4 → 448, G1/G3 Φ1: 2 → 128); in G4/all P4 UNSAT→SAT (out-of-band expectation) |
| cihaz_bagi_yok / iptal_denetimi_yok / wscd_pq_yok | 63 / 63 / 63 | 63 / 63 / 63 | 0 | G2 / G3 / G2 (policy violation, or a10 cannot be selected) |
| durum_imzaci_farkli_capa | 63 | 0 | 0 | G3: a minimal set without a04 appears (the external status CA certifies the status signer) |
| onbellek_ufku_ilk_pencere | 63 | 0 | 0 | G1–G3 cache cells: a01/a02 drop (a copy filled before Q-day cannot be forged in the first window) |
| webpki_pq_birlikte | 63 | 0 | 0 | G1–G3 P4: node sets the same; an alternative set {a13 + `tasi(a00_ojeu, a13_lotl_kanal)`} is added instead of a01. The OJEU-pinned LOTL download channel can be locked to PQ by the expectation carried by the OJEU; for the general WebPKI there is no per-entity expectation carrier, so `pq_birlikte` is equivalent to classical |
| kimlik_turu_qeaa | 54 | 0 | 0 | G1–G3 Φ1/Φ2-P4: nodes the same, carrier the national TL (`tasi(a02_tl, …)`) instead of the PID LoTE |
| wrprc_faz1 | 54 | 0 | 54 | G4/all P4: UNSAT→SAT. G4 set {a02, a11, a12} + WRPRC carrier `tasi(a11_kayit, a12_istek)` (needed even in Φ3: only this expectation closes the unsigned request variant; in Φ1 + 4 LoTE/OJEU carriers) |
| tek_kullanim_kuresel_pasif | 42 | 0 | 0 | G2 medium/slow: a10 drops (passive collector + global single use: W = iat window 10 min) |
| mekanizma_kancalari_acik | 36 | 0 | 0 | G1/G2 Φ1/Φ2-P4: the M-h alternative is added (`tasi(a03_ca, a07_kimlik)`) |
| durum_baglama_gevsek | 9 | 0 | 0 | G3 Φ1-P4: an additional carrier for the external status CA (`tasi(a02_lote_pid, a08_ca)`) |
| **No effect (0 cells):** anahtar_yeniden_kullanim, ayni_ad_klasik_ca, ca_baglama ad/anahtar (when there is no alternative CA), cihaz_anahtari_kalici, cnf 180 d / 1 yr, coklu_cerceve, durum_ttl 1 h / 7 d, gun_batimi_iptal, kbjwt_iat 1/60 min, ma_kanca, rp_auth_fail_open (G4 already UNSAT), clock allowance 0/60/600, sdjwtvc_s19, tek_kullanim none/verifier, w_ca/w_kok 1 yr, w_ihracci 30/180 d, w_ka/w_rp 180 d, w_tls 47 d, wia_anahtari_kalici | | | | |

τ sensitivity (Q × τ value): only slow 60 d (5,184,000 s) makes a difference, in 21 cells. All of them are G2, and in all of them only a10 drops (cnf 30 d < τ). The other six τ values change 0 cells.

### 4.6 A1 necessity and optimal orders

- **A1:** **all** 2,163 one-less sets in the primary frame violate the goal of the cell (a direct consequence of minimality; verified in evaluation mode). When a carrier is removed, G5 also falls (G1: 144/144, G2: 342/342, G3: 144/144 rows). Row counts per node in `rapor_sayilari.json` → `a1`.
- **Orders** (`sorgular/sira.py`; goal of pilot P2b; DP, 36 cells): ASP-DP = Jacobi-DP **36/36**; a single best order in 27 cells. The best orders go from root to leaf (a01 → a02 → a03 → a04 → leaf; in Φ1 free between a02–a04, 6 orders) — under Ö3 and item 18 of the design document's "do not enter" list this is not a contribution. The pilot P2b order (lotl → tl_pid → ca_iss → iss_cert → cred) is identical with the new core.

## 5. ASP–z3 agreement and three-way check

- **Independence:** the z3 side (`z3/yapi.py`, `z3/z3_kodlama.py`) does not read the ASP core; it reads only the ground fact files and interprets the conditions, windows, phase and M-h dominance with its own code; it builds the formulas by memoised recursion over the dependency graph. Minimal sets: model → single-element reduction → blocking of supersets. Finite k: CEGAR (a method different from the scenario enumeration of ASP).
- **Result:** 52,693/52,693 queries, 80,291/80,291 minimal sets (`z3/sonuc/uyum_*.csv`, `uyum_ozet.json`).
- **Three-way random check (additional; seed 20260928):** 7 query classes (g1, g2, g2i, g3, g4, g5, all) × 1,000 configurations (all categorical parameters, window and τ grids, breaking mode {k unbounded, S1, random broken set}, random PQ/carrier assignment): ASP = z3 = Jacobi **7,000/7,000** (violation and forged sets; `z3/sonuc/uclu_rastgele.json`).
- **Bug caught (transparency):** in the Tamarin instances, a fixed PQ assignment given to non-decision artefacts was not read in the z3/Jacobi evaluation mode (it was invisible in the ecosystem because all PQ-capable artefacts are decision variables); fixed, and all checks were rerun.

## 6. Regression

- **Tamarin datalog (44 verdicts; `regresyon/tamarin_esdegerlik.py`):** the 34 flag configurations of R1–R5 were translated into the fact format of the system core (`regresyon/tamarin_datalog/ornekler/*.lp`; τ = 600 s, window infinite, Dolev–Yao = conveyed). Agrees with **44/44** Tamarin verdicts; ASP = z3 = Jacobi 44/44. The naive reading fails only at `R1 X_alt_ca` (a renewed demonstration of the need for any-valid-path).
- **Pilot P2 (48 queries; `regresyon/p2_regresyon.py`):** the pilot's own program was rerun and its record (count, minimal cardinality, first ≤6 sets) was reproduced **48/48**; the pilot topology was run in the fact format of the new core (`regresyon/p2_ornegi.lp`): new core **48/48**, z3 **48/48**, all 82 sets the same. P2b order the same.
- **Deliberate model differences from the pilot:** the LoTEs are pinned in the OJEU (T029; in the pilot they were under the LOTL); A09 was split in two; channel/transport, time, policy, variant and 17 nodes were added. When these are neutralised in the pilot instance, the results are identical.

## 7. Sampling export (technical gate; §2F item 2)

- **The ASP work selected no sample.** The whole frame: `sampling/cerceve.jsonl` (2,442 rows; SHA-256 `0a9b10d169a2898b97a6463fc481385a359744a981c392560ad0355f01942d87`).
  - Strata (goal × kind): G1 81/546, G2 117/1,071, G3 81/546; **G4 and all empty** (UNSAT in the primary) → 6 filled strata.
  - Every row: cell, set (PQ nodes + carriers), ASP prediction (computed in evaluation mode), witness (forged artefacts), subgraph of the target path, flat Boolean flag mapping for R1–R7 and a `.spthy` template proposal.
- `sampling/kesif_2x2.jsonl` (8,442 rows; SHA-256 `c1e810c8c5f077790e9feb27ab6ddd8c0031ac3019a2d0c1503a4a2e5a3fb2ec`): minimal + one-less in the SAT cells of the 2×2; in every cell the verdict of the primary sets ("birincil-kume"). **All 279 "birincil-kume" rows of the cell `ca_baglama = ad, ayni_ad_klasik_ca = var` are falsified** (the mandatory additional sample is of this kind; template `R7_mh_x.spthy`, flags CA_PQ, ALT_CA, NAME_BIND, ALT_SAME_NAME).
- Format: `sampling/SCHEMA.md`; summary: `sampling/disa_aktarim_ozeti.json`.

## 8. PRELIMINARY results (to be verified at the scientific gate)

> All verdicts are **preliminary**: they are output of the ASP model. The Tamarin sampling of these results (technical gate), the abstraction mutations and the KATs have not been done yet. (2a)/(2b) candidacy is counted only from the primary configuration and the 2.4 designs (§2C item 2, 2.5 "Counting rule"); OAT and exploratory differences do not pass the gate.

| Hypothesis | Pre-registered criterion | PRELIMINARY result | Basis |
|---|---|---|---|
| **H1** channel substitution | (i) substitution for at least one fetched artefact with PQ transport; (ii) none with classical transport; none in the conveyed context | **Supported (preliminary).** (i) When the WebPKI is PQ (with A13), these nodes can drop out of the minimal set: a01 @G1–G3 (45/45 cells), a02 @G1–G3 (54/63), a03/a04 inside the status token @G3 (54/63), a08 @G3 (54/63), a06 @G1 (while Type Metadata is processed, 54/63), e_jvi @G1 (54/63); a02 @G4 only in the variant where the unsigned request is rejected (45/45). (ii) At nominal τ there is no substitution with classical transport. In the conveyed context (a03/a04/a07 @G1–G2, a10 @G2, a11/a12 @G4) substitution 0: the falsification condition arose in none of the 8 channel variants. Sub-cases: with an offline conveyed status list, substitution of a03/a04/a08 @G3 is 0; when the LOTL is fetched over the WebPKI, substitution of a01 36/45. **Limits:** if τ > W_trust(TLS), classical transport also protects (42 `TASIMA_KORUR` cells in A5; none in the nominal grid). Under k = 1 a fetched artefact cannot be forged with a single break, so substitution also appears while the WebPKI is classical (OAT k1) | `analiz/tablolar.md` (h1_md), `analiz/ozet.json` h1; H1 design 10,125 queries |
| **H2′** key window (Ö1) | Support: in ≥1 goal the set changes between ≥2 τ regimes and is explained by the window. Falsification: (i) effect of the token lifetime with a fixed key window; (ii) the window having no effect at all | **Supported (preliminary).** G3: with the status key in V2/V3, a08 is required in 21/21 SAT cells at fast τ and not required in 33/33 SAT cells at medium and slow τ; in V1 it is required at every τ in 21/21. (i) 0/32 (A5: in V1 the token lifetime does not change the set); (ii) in 66/180 V2/V3 groups the set changes with τ. With the issuer key in V2/V3 there is no change, because the window (1 d + 30 d validity) is longer than all nominal τ values. Numerical mapping with R6 588/588 | `h2_md`, `r6_esleme.csv` |
| **H4** limit of the published order | S5 insufficient or wasteful in ≥1 cell (+ a Tamarin instance) | **Candidates exist (preliminary).** 36 primary cells: insufficient(node) 12, insufficient(expectation) 6, wasteful(other) 9, neither satisfies 9 — not counted under Ö3 (long-lived key / expectation / off-path). **10 candidates in the Ö3 cells:** G4 WRPRC-faz1 unsigned-request cells (cl and pq; Φ1/Φ2): no a11/a12 in the set of S5 → insufficient; cnf 1 d (G2) and V2/V3 status key (G3) at medium/slow τ: S5 migrates a10/a08 needlessly → wasteful(τ). No Tamarin instance yet. The classification is an interpretation and awaits approval (DECISION-NOTES N8) | `sorgular/sonuc/h4_karsilastirma.json` |
| **H5** harvest-and-forge | Forgery trace ⇔ τ < remaining validity; single use does not prevent the trace | **Supported (preliminary).** Single use {none, wallet, verifier} changes the set in no cell; a10 is required at every τ with cnf 30 d, and only at fast τ with cnf 1 d. Falsification test (single use at the verifier, no shared state): no effect, H5 not falsified. The boundary variant (passive collector + global single use: W = iat 10 min) drops a10 at medium/slow τ; since this variant needs state shared between verifiers, it is outside the operational reading of pre-registration §3.6 and is reported as a boundary condition | `h5_md`, `h5_tek_kullanim_md` |
| H0 (sanity) | Trace under P0 + coexistence; ∅ at τ = ∞ | At τ = ∞, "all" (Φ1, P0) is satisfied by ∅; under S1 (no breaking) "all" is satisfied by ∅ in Φ1–Φ3; under S2, P0 + Φ1/Φ2 UNSAT (trace). The system core agrees with the 44 verdicts of Tamarin (§6) | H0/H3 rows of `h.json` |
| H3 (preliminary signal) | No G5 in coexistence without a verified expectation | G1+G5 cells: in Φ1/Φ2 P0–P3 UNSAT under S2 and under k = 1; P4 SAT; all SAT with ∅ under S1. Looking at G1 alone, P3 becomes SAT under k = 1 (OAT k1): the classical channel of P3 does not by itself open a forgery, but it violates untimed G5. In G4, M-b0 (unsigned request) does not close without the WRPRC expectation (faz0 UNSAT, faz1 {a02, a11, a12}). Under Ö2 the M-a/M-b/M-b0 traces count as obvious | H3 rows of `h.json` |

## 9. Limitations

1. **Class-level abstraction:** the decision is on 17 nodes; entity-level partial migration is represented only by named cells (alternative CA, second framework). M4 is therefore a structural proxy.
2. **Time is a steady state:** in the worst case the key is observed at the start of the window; the transition between Q-day and the first window is modelled only by `onbellek_ufku`. A success probability < 1 (Häner) and the relation of k to the number of machines are not modelled.
3. **P0/P1/P2 are equivalent in this abstraction** (the same set family in all 10,305 cell groups of the 7 result groups): the differences of stripping and key–alg binding are at implementation level (C3; DECISION-NOTES N9).
4. **k budget:** the primary k is unbounded. Under k = 1 the results change markedly because a fetched artefact needs two breaks (297 cells; G3 is satisfied by ∅). The H1 condition "no substitution with classical transport" depends on the assumption of unbounded k (DECISION-NOTES N10).
5. **Transport is a single node:** the WebPKI CA chain is reduced to a single key (its window is the TLS server certificate, 1 yr). The CA/B Forum reduction (47 d) is only in the sensitivity analysis; the combination w_tls 47 d + τ ≥ 47 d is not in the OAT (DECISION-NOTES N11).
6. **M-a…M-h are only hooks;** the M-f component ablation (A3), the reddy/vicente variants of M-h and `beklenti_kapsami` are the job of Step 7. M-d (S3) is assumed authentic; its operating cost is not in the model.
7. **sdjwtvc_surum** has no effect in the formal model (OAT 0); the differences in §2D item 7 belong to the C3 vectors.
8. **The KATs (optional) were not implemented:** the drafts of `literatur/analiz/KAT-SPEC.md` were left to Step 6; the core (any-valid-path, expectation, version/time hooks) is ready to take the KAT-1/KAT-3 instance files as facts.
9. **Single model author:** ASP, z3 and Jacobi came from the same work; the independence is at method and code level. The real independent verification is the Tamarin sampling (DECISION-NOTES N15).

## 10. Recommendations for Steps 5–7

- **Step 5 (sampling):** the frame is ready; the flag mapping of the samples to be selected and of the additional ad/var sample is in the rows. The G4 stratum is empty in the primary (DECISION-NOTES N7): if the sampling wants a G4 frame labelled exploratory from the `wrprc_faz1` or H1 (WebPKI PQ) designs, it can be produced in the same format.
- **H4 interpretation (DECISION-NOTES N8):** not counting the 9 wasteful(other) cells of Φ3 as (2a) awaits approval. Under the additional condition of (2a), a Tamarin instance is needed for each of the 10 candidates.
- **R6:** the numerical classes are exported with `pencere_sinifi/2`; in the Tamarin instances the FAST/MEDIUM/SLOW flag should be derived from `R6.tau_pencereden_uzun` in the row.
- **Step 7:** for M-h the dominance hook (`baskin/2`) and the `ortak_ata` assumption are ready; `beklenti_kapsami = yol_sinifi` can be added over the `kenar/3` classes of the accepted path. The dependence of M-e′ on the WebPKI (unsigned metadata variant) is visible in ASP: the metadata carrier is secure only with PQ transport or with rejection of the unsigned form.
- **H4 Tamarin instance:** the strongest candidates are `G2_cnf1g_orta` (wasteful; a10) and `G4_imzasiz_istek_cl_faz1_f1_p4` (insufficient; a11/a12).

## 11. Status
(last updated: 25.09.2026, session 2)
- [x] Skeleton, facts, core, driver, z3 encoding
- [x] §2C adaptation (17 nodes, primary windows, A13, edge-artefact nodes, PQ-bound unsigned artefacts)
- [x] §2D adaptation (ca_baglama, ayni_ad_klasik_ca, window classes, KEY_REUSE)
- [x] 52,693 queries; ASP–z3 100%; three-way 7,000/7,000; Tamarin 44/44; P2 48/48
- [x] 2×2 + sanity 6/6; R6 588/588; strategies; H4; A1; orders
- [x] Frame export + SHA-256 + strata; SCHEMA.md
- [x] Report and notes (DECISION-NOTES N1–N15; the `pq_birlikte` phrase in N1 corrected)
- [x] Final check: the numbers and narrative claims in the report were rechecked against the result files. Corrections: cache comparison 225/225; T-references according to the artefact assignments of the matrix; S8, k1/k3, OAT explanations, H1 sub-cases
- [ ] KATs → Step 6 (deliberate postponement)

## 12. Files

| Path | Content |
|---|---|
| `olgular/*.lp` | artefacts, edges, carriers, windows, goals, parameters |
| `cekirdek.lp`, `secim.lp`, `sorgu.lp` | semantics; decision nodes and domRec; query constraint |
| `calistir.sh` | container runner (read-only mounts: models/tamarin, referans, veri, 02-izlenebilirlik) |
| `sorgular/` | `ortak.py` (driver), `katalog.py`, `kos.py`, `analiz.py`, `stratejiler.py`, `h4.py`, `sira.py`, `rapor_sayilari.py`, `stratejiler_taslak.json`(+`.sha256`), `beklenti_2x2.json`(+`.sha256`), `sonuc/` |
| `z3/` | `yapi.py`, `z3_kodlama.py`, `py_degerlendirici.py`, `capraz_kontrol.py`, `uclu_rastgele.py`, `sonuc/` |
| `regresyon/` | `tamarin_esdegerlik.py`, `p2_regresyon.py`, `p2_ornegi.lp`, `tamarin_datalog/ornekler/`, `sonuc/` |
| `sampling/` | `disa_aktar.py`, `cerceve.jsonl`, `kesif_2x2.jsonl`, `SCHEMA.md`, `disa_aktarim_ozeti.json` |
| `kat/` | empty placeholder (the KATs were postponed to Step 6) |

**Reproduction:** `./calistir.sh sorgular/kos.py` → `./calistir.sh z3/capraz_kontrol.py <groups>` → `z3/uclu_rastgele.py` → `regresyon/*.py` → `sorgular/analiz.py`, `stratejiler.py`, `h4.py`, `sira.py` → `sampling/disa_aktar.py` → `sorgular/rapor_sayilari.py`.
