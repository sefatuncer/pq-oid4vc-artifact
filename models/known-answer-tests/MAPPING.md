# KAT mapping (Step 6): three ecosystems, one core

> **Status:** preparation document. The reading rules and the mapping were written before any KAT cell was run and pinned with SHA-256 (`SHA256SUMS`, "preparation" section; STEP06-REPORT §1). Every later change is reported with the label "after the result was seen".
> **Expected values:** only `nsurum/kat_nsurum.tsv` (column `ilk_ajan`, the first derivation; anchor 8, PR §2H.1). This document contains and defines no expected values.
> **Sources:** `literatur/analiz/KAT-SPEC.md` (specification), `models/asp/cekirdek.lp` (the single core), PR §4.19, work plan Step 6.
>
> (Translated from Turkish for this release. The original file, whose hash is recorded in `SHA256SUMS`, is listed in `docs/INTEGRITY.md`.)

## 0. Principle

1. **One core.** Every KAT cell is run only with `models/asp/cekirdek.lp` and the instance files in this folder.
   - `olgular/*.lp`, `secim.lp`, `sorgu.lp` are not loaded.
   - The `kat_core.lp` and `hon_decision.lp` proposed by KAT-SPEC are **not used** (work plan 6.1).
   - The SHA-256 of the core is taken before and after in every runner: `a32372a7…0b38` (commit `45cbd0f`).
2. **Content of the instance file.** The base file of each KAT (`dnssec/kat1_dnssec.lp`, `x509/kat2_x509.lp`, `smime/kat3a_smime.lp`, `smime/kat3b_auth.lp`) contains two things:
   - ecosystem facts, in the vocabulary of the core;
   - small ecosystem derivation rules: they derive the state of that ecosystem from the constants of a cell (`ornekler/*.lp`).

   There is no core rule. This is the same role as `olgular/pencereler.lp` (an ecosystem rule) in Step 3.
3. **Reading rule.** The output of the core is the atoms `ihlal(S,G)` (violation). The conversion into the cell value of each KAT is made with the fixed rules below (§2.5, §3.4, §4.4, §4.5).
   - In decision and classification cells the reading rule combines the security predicate computed by the core with the evidence state of the cell.
   - Which part is computed in the core is shown in a single table in §5.
4. **No fallback test.** All three mappings were built, S/MIME included (§4). No fallback known-answer test was selected (PR §2C item 1).

### 0.1 Core semantics (short)

| Rule | Meaning |
|---|---|
| K1 | A classical signer key breaks when τ < W + allowance; the artefact can be produced. |
| K2 (any-valid-path) | A can be produced if **any** accepted artefact that introduces A's signer can be forged (not if it is pinned/an anchor). |
| K3/K4 | If a classical alternative of a PQ-signed A is accepted (`klasik_alt`), the alternative key can be broken. An authenticated expectation (`tasi` + P4, the carrier cannot be forged) closes this. |
| M-f hook | If `mf_kapali(tazelik)` and `mf_kapali(tekduzelik)` hold together (freshness and monotonicity switched off), the old version of the carrier is replayed (`geri_alinir`, rolled back) and the expectation drops. |
| Channel | A fetched artefact is delivered only if its transport can be forged; a conveyed one always; a pinned one never. |
| G5 (untimed) | Violation if a migrated (PQ) entity on the target path has an open classical alternative and no authenticated expectation; no breaking is needed. |

### 0.2 Shared vocabulary: KAT-SPEC §1.1 → core

| KAT-SPEC (`kat_core.lp`) | Core (input of `cekirdek.lp`) |
|---|---|
| `key_class(K,cl)` | its signer is classical: `not pq(A)` |
| `key_class(K,pq)`, `comp` | `pq(A)` (the PQ component of composite does not break; therefore like PQ) |
| classical and PQ `slot` on the same artefact | `pq(A)` + `klasik_alt(A)` (∃-path: either one is enough) |
| `intro`/`validates` | `kenar(E,X,I)` (OR edge) |
| `anchor(K)`, `anchored(K,X)` | `sabit(X)` |
| `exposure`, `qday`, `tau`, `now` | `pencere(A, now − max(T0,qday))`, `p_sayi(tau,τ)`, `saat_payi = 0`. Core τ < W; KAT-SPEC τ ≤ W. No cell lies on the equality boundary. |
| `signal_*` + `pol=required` | `tasi(C,X)` + `p(politika,p4)`; C a signed source (M-f class) |
| `local_req` (P2) | `tasi(yerel_politika,X)`, carrier pinned (M-d class) |
| `allpresent` / `enforce_if_present` (P1) | self-signal carrier: the **presence** of the PQ evidence carries the expectation. Its strength is the strength of the signature that protects the presence: the DNS RRSIG set is protected by no signature (unauthenticated), whereas the Catalyst extension is protected by the classical base signature. |
| `continuity` (P3) | local continuity state (M-g class; pinned); exists only after the first contact |
| `version`, `valid_v`, `seen`, `monotone` | ecosystem derivation: versions accepted at time 'now' → `pq`/`klasik_alt`. Old version at the expectation carrier → `mf_kapali` → `geri_alinir`. |
| `attack` | `ihlal(tum,g1)` (S2, k unbounded) |

## 1. General pass criterion and how it is computed (PR §4.19, work plan 6.6, KAT-SPEC §0)

For each KAT all four conditions must hold; a single "indeterminate" cell already fails that KAT:
1. **ASP cells 100%.** All `nsurum` keys (the ASP part of the 141 keys) equal the expected value under the reading rule.
2. **Tamarin cells 100%.** The Tamarin keys in `nsurum` have the expected value; `executable` verified in every run; well-formedness warnings 0.
3. **ASP–Tamarin agreement 100%** in the shared cells. Correspondence table per KAT in §2.5, §3.5, §4.6.
4. **KAT-SPEC §6 mutations 100%.** Each of the 12 mutations, in every engine where it is defined (ASP and/or Tamarin), must turn at least one of the listed cells in the stated direction.

**Additional items (reported separately for the gate count, not in `nsurum`):**
- KAT-2 Tamarin sensitivity lemmas (`x509/ek_tamarin.tsv`, KAT-SPEC §3(d));
- KAT-3a `kat3a_fail` empty and `model_gap` only in o8 (KAT-SPEC §4(d) "Pass (KAT-3a)");
- KAT-3b Tamarin with the original pilot (`smime/ek_tamarin.tsv`; §4.5).

**Computation:** the `degerlendir.py` of each folder (runs nothing; only reads the `sonuc/` outputs) → `sonuc/KAT_OZET.{json,md}`. `RESULTS.md` is the combination of these three summaries.

Whether they count for the gate is the maintainers' decision.

## 2. KAT-1 DNSSEC (`dnssec/`)

**Result reproduced** (RFC 6840 §5.11 + §6.2 + Appendix C.2; RFC 6781 §4.1.4, §4.3.4):
- In an "any single valid path" validator the weakest signalled algorithm determines security.
- Algorithm rollover and replay extend this window.
- A completeness test, a PQ-signed signal from above and monotonicity close the window.

### 2.1 Artefacts, edges, channel
- **`ds`:** signed with the parent zone key; the parent key is a trust anchor → `sabit(ds)`. `pq(ds)` ⇔ the parent key is PQ (`kat_ust_sinif`).
- **`dnskey`:** its signer is the KSK pointed to by the DS → `kenar(e_ds_ksk, dnskey, ds)`.
- **`a_rr`:** the target; its signer is a key in the DNSKEY RRset → `kenar(e_dnskey_anahtar, a_rr, dnskey)`.
- **Channel:** all three FETCHED. The DNS transport is not authenticated (`dns_yaniti`: unsigned, unauthenticated), so the transport can always be forged. The H1 sanity note of KAT-SPEC §1.1: no channel substitution in DNS.
- **Edge semantics of RFC 6840 §6.2:** "any DNSKEY in the zone's signed DNSKEY RRset may be used to authenticate any RRset in the zone". The PQ path and the classical alternative of the A RRset are derived from **any** key of that class being listed in the accepted DNSKEY version (`listeli(dnskey,C)`). The key is not bound to the artefact type (V2).
- The "root → TLD → zone" chain of KAT-SPEC is reduced to the parent zone key, which is a trust anchor (the same as KAT-SPEC §2(b)).

### 2.2 Time and version
The version table has the same numbers as KAT-SPEC §2(b) (DS v1/v2/v12; DNSKEY v3/v5; `goruldu` = `seen`). Ecosystem derivation:
- `gecerli(I,V)`: the signature is valid at time 'now'.
- `kabul_surum(I,V)`: valid and the monotone validator has not seen a newer one.

It enters the core in two ways:
1. **Structural path (versions):**
   - `pq(dnskey)` ⇔ an accepted DS version lists the PQ KSK.
   - `klasik_alt(dnskey)` ⇔ a DS version that lists the classical KSK is also accepted, **or** the old classical KSK is an extra trust anchor (Appendix C.2).
   - The same for `a_rr`, with the DNSKEY versions.
   - The replay of the old DNSKEY v3 (K1-07) and monotonicity cutting it off (K1-08) enter this way.
2. **Expectation carrier (DS):**
   - If the signature of an old DS version that does not signal PQ is still valid at time 'now', `mf_kapali(tazelik)`.
   - If the validator is not monotone, `mf_kapali(tekduzelik)`.
   - The M-f hook of the core rolls back the expectation of the DS when both hold. This is how K1-05 (replay) and K1-06 (monotonicity) differ.

**Time:**
- `pencere(A) = now − max(T0, qday)`, T0 = 0 (KAT-SPEC §2(d), static keys); `saat_payi = 0`; τ = `kat_tau`.
- In K1-13, where Q-day is after 'now', the window is negative and the core breaks no key.

### 2.3 Policy

| KAT-SPEC `pol` | Core |
|---|---|
| `anyvalid` (RFC 6840 default) | P0; no expectation |
| `allpresent` | P4 + self-signal carriers (`pqvar_dnskey`, `pqvar_a_rr`): unsigned, **unauthenticated**. The presence of the PQ RRSIG is protected by no signature; the attacker strips it (RFC 9955 §6.2). |
| `required` (completeness test, §5.11 MAY) | P4 + `tasi(ds, dnskey)`, `tasi(ds, a_rr)`, if the currently accepted DS signals the PQ algorithm (M-f class: signed parent source). If the DS signals only classical, the completeness test requires only classical: no PQ expectation (K1-02). |

In K1-12 the parent key is classical; the DS can be forged, so the expectation drops (V3: "as strong as the signal channel applied").

### 2.4 Tamarin (`dnssec/KAT1_DNSSEC.spthy`)
The draft of KAT-SPEC §2(c); same meaning. Changes are in the file header:
- `#ifdef not`;
- with NO_QDAY the Break rules are removed too;
- NotEq only in the flag where it is used;
- the §6 mutations at whole-rule level (`MUT_NO_DS_SIG`, `MUT_NO_DS_KSK_MATCH`).

In the preparation, 16 of the 16 distinct flag sets were well-formed, warnings 0 (`dnssec/iyi_bicim/ozet.tsv`; no `--prove`).

**After the result was seen (26.09.2026, maintainers' decision):**
- In the first run K1-11 came out falsified in Tamarin. The draft applied the completeness test only at the A RRset step; the rule "all algorithms signaled in the DS RRset" of RFC 6840 §5.11 was missing at the DNSKEY step.
- The corrected gate model `dnssec/KAT1_DNSSEC_v2.spthy`: under `COMPLETENESS` completeness is applied at the DNSKEY step too; the mutation alternatives are defined accordingly.
- The mapping and the reading rules in this document did NOT change. Details: STEP06-REPORT §5, §8.

### 2.5 Reading rule and ASP–Tamarin correspondence
- **ASP:** SALDIRI (attack) ⇔ `ihlal(tum,g1)`; otherwise YOK (no attack).
- **Tamarin:** `a_rrset_authentic`.
- **Shared cells:** K1-01…K1-15 (15); SALDIRI ↔ falsified, YOK ↔ verified.

### 2.6 Mutations (KAT-SPEC §6, KAT-1 rows; `dnssec/mutasyonlar.tsv`)

| Mutation | ASP (variant of the instance file; core unchanged) | Tamarin | Expected turn |
|---|---|---|---|
| MUT01 COMPLETENESS → ANYVALID | `kat_politika(anyvalid)` | flag change | K1-04, K1-11 → SALDIRI/falsified |
| MUT02 DS signature check removed | `ds` counted as unsigned (`kat_mutasyon(ds_imza_denetimi_yok)`) | `MUT_NO_DS_SIG` | K1-04 → SALDIRI/falsified |
| MUT03 DS–KSK match removed | `dnskey` accepted with any KSK → counted as unsigned | `MUT_NO_DS_KSK_MATCH` | K1-04 → SALDIRI/falsified |
| MUT04 monotonicity removed | `kat_tekduze(0)` | K1-06: `OLD_DS_REPLAY` is added (KAT-SPEC note: in K1-06 monotonicity = not giving the old DS); K1-08: `MONOTONE` is removed | K1-06, K1-08 → SALDIRI/falsified |
| MUT05 validity of the old version ∞ | `kat_mutasyon(eski_surum_suresiz)` | K1-09 + `DK3_USABLE` | K1-09 → SALDIRI/falsified |

### 2.7 Limits
- The validity of the version signatures at time 'now' and the exclusion of the old version by monotonicity are computed by the ecosystem derivation rules (base file). The core computes the consequences of this state: K1/K2/K4, expectation, M-f rollback, time.
- The core's own time model is a steady state (τ < W). The time 'now' is reflected in the window (W = now − max(T0, qday)) and in the accepted versions.

## 3. KAT-2 X.509 hybrid (`x509/`)

**Result reproduced** (PR §4.19): "under a policy that does not make the PQ component required, corrupting the PQ evidence does not change the decision" (Kim §VI-A: 27/27; Lee §4.4: "no stack can mandate the binding"). Composite binds structurally (Lee §4.3). The state of the bound PQ certificate enters the decision only if the policy covers it (Kim Table V). P0–P3 under M1 (Kim Table VI).

### 3.1 Model
- **`ee`:** the target; the CA keys are anchors → `sabit(ee)`; conveyed.
- **Hybrid issuance:** `pq(ee)`.
- **In the separable schemes (Catalyst, Chameleon, Related):** the classical base signature is accepted on its own on the default path → `klasik_alt(ee)`.
- **Composite:** a single signature. A classical path exists only in coexistence (a plain classical certificate of the same CA is also accepted: `coexist_cl`).

### 3.2 Verifier policy → expectation carrier (mechanism classes of the core)

| `vb` | Core |
|---|---|
| `ignore`, `parse_no_enforce`, `legacy_oid` | P0 (the PQ evidence does not enter the decision) |
| `enforce_if_present` (P1, "check if present") | self-signal `pq_kanit_varligi`: exists only if PQ evidence is **present** (valid or invalid). Its presence is bound to the **classical** base signature through the extension in the TBS: the carrier is classically signed. If a CRQC breaks the classical key, the attacker strips it (Lee §4.4). |
| `require` (P2, local "require-PQC") | `yerel_politika` (local policy): pinned (M-d); forged in no scenario |
| `require_tl` (K2b-04/05) | signed TL (M-f); the TL key is classical or PQ |
| `continuity` (P3) | `sureklilik_durumu` (continuity state): a pinned local state; exists only when `seen_hybrid = 1`. Kim: "P3 presupposes an external continuity state" |

### 3.3 Two modes
- **`saldiri` (attack; K2b; Kim M2 = CRQC):** scenario `tum`.
- **`karar` (decision; K2a/K2c/K2d; Kim M1 = no CRQC, honest object):** scenario `bos` (S1).

### 3.4 Decision reading rule (FIXED; `x509/kos.py: karar_oku`)

The core computes **whether the verifier makes the PQ evidence required for this object**:
- G5 := `ihlal(bos,g5)`: the classical evidence of a migrated (hybrid-issued) entity is accepted without an authenticated PQ expectation.
- This is the counterpart of Kim's notion of "classical acceptance" (silent promotion) and of the Tamarin `no_silent_promotion`.

| Core | Evidence state of the object (cell input) | Label |
|---|---|---|
| G5 | any | `accept_classical` |
| not G5, Related | bound PQ certificate valid / `unknown` / other | `accept_hybrid` / `indeterminate` / `reject` |
| not G5, other | PQ evidence valid in the verifier's eyes and the algorithm recognised / not | `accept_hybrid` / `reject` |

- "Valid in the verifier's eyes": `kat_pqev = valid`. In MUT07 the PQ component of composite is seen as valid because it is not checked.
- "Recognised": `vb ≠ legacy_oid` (Kim Table IV "loud-fail").

**Why this reading tests the published claim:** the core of the claim is the **sensitivity** of the decision to the PQ evidence. This sensitivity lies entirely in G5:
- If G5 is true, the label is independent of the evidence state: in the `ignore` / `parse_no_enforce` cells valid and invalid come out the same (Kim 27/27).
- If G5 is false, the label depends on the evidence.

G5 is computed by the core. The part of the reading rule that uses the evidence state (valid → hybrid, not valid → reject) is the validity of the object's own signature; it is not policy logic.

### 3.5 ASP–Tamarin correspondence
- **K2b** (`cert_authentic`; K2b-01/02/03/06/07): SALDIRI ↔ falsified.
- **K2d** (`no_silent_promotion`; K2d-01/02/03): `accept_classical` ↔ falsified, `reject` ↔ verified. G5 and `no_silent_promotion` are the same notion.
- **K2b-04/05/08, K2a, K2c:** ASP only (KAT-SPEC).

### 3.6 Mutations (`x509/mutasyonlar.tsv`)

| Mutation | ASP | Tamarin | Expected |
|---|---|---|---|
| MUT06 V_REQUIRE → V_ENFORCE_IF_PRESENT | `vb = enforce_if_present` in K2b-03 | flag change | K2b-03 → SALDIRI/falsified |
| MUT07 composite PQ component check removed | `comp_pq_denetimi_yok`: the assurance of composite falls to the classical component (no `pq(ee)`); the PQ evidence is seen as valid | `MUT_COMP_NO_PQ` | K2b-06 → SALDIRI/falsified; K2a-16 → accept |
| MUT08 status check of the bound certificate removed in P2 | in Related, `require` does not cover the bound PQ certificate (no carrier; V9) | – | KAT-2c P2 column → `accept_classical` |
| MUT09 `hybrid_seen` ignored | no continuity state carrier | – | K2d-04 → `accept_classical` |

### 3.7 Limits
- The decision labels are the verifier's classification; the core does not classify. The core computes the PQ-sensitive part of the classification (G5).
- Composite algorithm recognition (`legacy_oid`) and the "seen as valid" of MUT07 are in the reading rule.
- The evidence state of K2d is `absent` (legacy certificate; M1; reading B8 of the blind work).

## 4. KAT-3 S/MIME (`smime/`): CEK-based structural mapping and its rationale

### 4.1 Problem
Das and Chattopadhyay (ePrint 2026/1374) say: "every valid path to the CEK must satisfy the active migration policy" and "the confidentiality level of ED is bounded by the weakest valid recipient path protecting K". This is a **confidentiality** result. The core, however, is built on **authentication** (forgery): it has no semantics of confidentiality, decryption or key recovery. PR §4.19 requires that in this case the mapping be documented as a structural mapping of "path-based policy satisfaction".

### 4.2 Structural mapping (duality)

| Das (CMS confidentiality) | Core (authentication) | Why the same structure |
|---|---|---|
| CEK K (single, shared) | target artefact `cek` | The single protected object |
| Recipient structure RI_i: a recovery path to K | artefact `yol(i)` and `kenar(e(i), cek, yol(i))` | Every path is an independent access path |
| If the attacker recovers K from any valid RI_j, M is exposed (Proposition 1) | K2 (any-valid-path): if ANY accepted introducer can be forged, the target is violated | Both are ∃-path weakness / ∀-path assurance; the assurance is that of the weakest path |
| V_i(t) = 1 (recipient certificate valid) | edge present (`ri(…, gecerli)`); a path with an invalid certificate has no edge | Das's rule as written |
| Active migration policy A_t (strict: {PQC}; transitional: {PQC, approved hybrid}) | **probe:** paths of classes outside A_t can be broken (classical), those inside are PQ | Policy satisfaction = no attack while every non-permitted key is broken |
| Universal acceptance (Eq. 8): ∀ valid path, χ_i ∈ A_t | no `ihlal` in the core | ∀-path ⇔ no path can be forged |
| "Unknown mechanisms fail closed" | unknown is in no A_t (can be broken) | fail closed = not permitted |
| malformed → invalid | the invalid class is in no A_t | |
| Approved hybrid KEM (both components needed) | counts as PQ in transitional; not permitted in strict | Das Stage 4 |

**Preserved:** completeness of path enumeration and the ∀-quantifier (V12); the distinction between "valid path" and "class", and fail-closed for unknown (V13); the weakest-path principle.

**Not preserved (explicitly):**
- The core computes the "forgeability" of the CEK, not its "recovery". The mapping is a **structural** mapping, not a security-semantic one; it tests the path structure of policy satisfaction.
- The class labels of Das's Table 1 are a reporting function. The labels are read from the probe results with a fixed precedence (§4.4).
- `model_gap` (o8): an attacker with a CRQC still recovers the CEK for confidentiality via a classical path with an invalid certificate. Das's rule leaves this out of scope. It is reported with a separate probe as a reading note and not attributed to the authors (KAT-SPEC §7.4).

### 4.3 KAT-3a probes (`smime/kat3a_smime.lp`)

| Probe | Breakable (non-permitted) classes | Meaning |
|---|---|---|
| `kati` | hybrid, classical, unknown, invalid | strict-PQC policy (A = {pqc}) |
| `gecis` | classical, unknown, invalid | transitional-hybrid (A = {pqc, hybrid}) |
| `klasik` | classical | is there a valid classical path |
| `bilinmeyen` | unknown | is there a valid unknown path |
| `gecersiz` | invalid | is there a malformed structure |
| `pq_hibrit` | pqc, hybrid | is there a valid PQ or hybrid path |
| `tum_klasik_yol` | classical; paths with an invalid certificate are counted too | model difference (o8) |

- Time: CRQC present (now 100, qday 0, τ 10).
- MUT11 ("fail-closed: unknown permitted"): in the policy probes, unknown is removed from the breakable set.

### 4.4 KAT-3a reading rule (FIXED; `smime/kos.py: etiket_3a`)
E(probe) := `ihlal(tum,g1)`.
- `accept_strict = 1 − E(kati)`, `accept_transitional = 1 − E(gecis)`.
- `out` (Das Stage 5 precedence: malformed → invalid; unsafe mixed-mode before weaker uncertainty labels; unknown fail-closed):
  1. E(gecersiz) → `invalid`;
  2. otherwise E(klasik) ∧ E(pq_hibrit) → `unsafe_mixed`;
  3. otherwise E(bilinmeyen) → `unknown`;
  4. otherwise E(klasik) → `classical_only`;
  5. otherwise ¬E(kati) → `pqc_protected`;
  6. otherwise ¬E(gecis) → `hybrid_protected`.
- In addition: `kat3a_fail = accept_strict ∧ E(klasik)`; `model_gap = accept_strict ∧ E(tum_klasik_yol)`.

### 4.5 KAT-3b authentication dual (`smime/kat3b_auth.lp`)
- **Model:**
  - TL: anchor-signed (`sabit`), FETCHED from the network, transport unauthenticated; it introduces the issuer's keys (`kenar(e_tl_ihracci, cred, tl)`).
  - Credential: PQ-signed; in coexistence it has a classical alternative.
  - The TL entry can carry "pq_required" (M-f); pol = required.
- **Time modes:**
  - dynamic `qday0`;
  - dynamic `qday200` (no CRQC);
  - **static** (time constraint removed: now large, τ = 0; all classical keys broken).
- **V14 (static ≡ dynamic):** in the single-core design, the static policy check is the same attack search with the time constraint removed. `violation(qday=0) = attack(qday=0)` holds by construction; this is a design property, not an independent test. The divergence at `qday=200` comes only from the time rule of the core (no `zaman_uygun`).
- **Reading:** dynamic SALDIRI ⇔ E; static violation = 1 ⇔ E.
- **Pilot counterparts:** KAT-SPEC §4(d) and the flags of `tools/regression-tests/calistir.sh` (V1 without flags … V6 `NO_COEXIST`).

**Well-formedness of the pilot model (preparation finding; decided BEFORE the run).**
- **Problem:** KAT-SPEC §4(c) requires the pilot (`referans/pilot/p1/weakest_link.spthy`, `b079cbbb…bd47`) to be run "unchanged". But in six of the six configurations the pilot does not pass the Tamarin 1.12 well-formedness check: "Fact multiplicity issues". The name `Qday` is used both as an action (`--[ Qday() ]->`) and as a persistent fact (`!Qday()`).
- **Why it cannot affect the lemma verdict:** the action `Qday()` occurs in no lemma or restriction; the lemmas use only `Issued` and `Accept`.
- **Conflict:** the project's evidence rule "well-formedness warnings 0" (PR §2H.2; the 24.09 rule of the Tamarin work) versus the letter of KAT-SPEC, "unchanged".
- **Decision:**
  - The gate cells are run with `smime/weakest_link_wf.spthy` (`90aa0a4d…a883`). Its only difference from the pilot is the name of the action in line 24: `Qday()` → `QdayOlayi()` (`diff`: 1 line, 1 word).
  - The original pilot is also run with the same six configurations and reported separately in `smime/ek_tamarin.tsv` (not a gate cell).
  - If the two results diverge, this is reported as a finding; which one counts is the maintainers' decision.
- **Result and decision (26.09.2026):** the two models gave the same verdict and the same number of steps 6/6. Maintainers' decision: the model with the warning is invalid; the corrected copy is the gate cell.

### 4.6 ASP–Tamarin correspondence
- **KAT-3b:** `attack(qday=0)` ↔ `claims_unforgeability` (V1–V6; well-formed pilot copy, §4.5); SALDIRI ↔ falsified.
- **KAT-3a:** the Tamarin `cek_secrecy` flags are the counterparts of KAT-3a vectors:
  - MIXED ↔ o4 (mlkem + rsa);
  - PQ_ONLY ↔ o1;
  - HYBRID_KEM ↔ o5 (approved hybrid).

  The ASP value is read from the probe with the same threat model as Tamarin: `klasik` (only the classical key is broken). E ↔ falsified. KAT-SPEC does not give this correspondence by name; the definition belongs to this document (pinned before the gate).

### 4.7 Mutations (`smime/mutasyonlar.tsv`)

| Mutation | Engine | Expected |
|---|---|---|
| MUT10 second component removed in the approved hybrid (`h(<ssc,ssq>) → h(ssc)`) | Tamarin `MUT_HYBRID_ONE` | HYBRID_KEM `cek_secrecy` → falsified |
| MUT11 fail-closed: unknown permitted | ASP (o7, o10; probes kati and gecis) | accept → 1 |
| MUT12 TL expectation check removed | ASP (V4, qday0) | SALDIRI |

## 5. Which part is computed where (coverage check; work plan 6.10 item 2)

| KAT / cell family | The core computes | The mapping/instance file fixes | The reading rule adds |
|---|---|---|---|
| KAT-1 (15) | breaking (time), any-valid-path, classical alternative, expectation and its forgeability, M-f rollback, channel | version validity at 'now', exclusion of the old version by monotonicity | nothing (SALDIRI ⇔ ihlal) |
| KAT-2b (8) | the same | policy → carrier class | nothing |
| KAT-2a/2c/2d (32) | G5: is the PQ evidence required (policy, self-signal, local/continuity state) | policy → carrier class; evidence state | evidence validity → hybrid / reject / indeterminate |
| KAT-3a (36 values) | does ∀ valid path satisfy the policy; presence of classes (probes) | vectors, classification, policy → breakable classes | Table 1 precedence |
| KAT-3b (18) | attack (timed), static = untimed attack | pilot configurations | nothing |

## 6. Immutability
- This document, the base and instance files, the cell and mutation tables, the Tamarin models and the runners were pinned in `SHA256SUMS` ("preparation" section) before the first run.
- If one of them is touched after the run, the difference, its justification and its impact are written into STEP06-REPORT with the label "after the result was seen". The expected values (`nsurum/`) are never touched.
