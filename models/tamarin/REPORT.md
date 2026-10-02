# Step 4 — Tamarin rule schemata R1–R5 (Layer 2 of the proven abstraction)

- **Date:** 24.09.2026
- **Work:** tamarin (Step 4)
- **Folder:** `models/tamarin/`
- **Tools:**
  - Tamarin 1.12.0 + Maude 3.5.1. Image `pq-a02-tamarin:1.12.0`, id `sha256:59b648d6…`. Version lines in the file `sonuc/calistir_log.txt`.
  - clingo 5.8.2 for the Datalog comparison (`pq-a02-solver:1.0`). This is a light, separate evaluation step; it is not a Tamarin result.
- **Evidence rule:** every number in the report was taken from the files under `sonuc/`. The source file of each table is written under the table. The tables were produced from these files by script, not copied by hand.
- **Step 5A addendum (24.09.2026):** in §12. Content:
  - R6 time window and the formal form of H5,
  - R7 monotone expectation, M-f/M-g/M-h comparison,
  - ProVerif second opinion.

  §0–§11 belong to Step 4 and did not change.

(Translated from Turkish for this release; numbers are written in English notation. Variant, flag, rule and lemma names are kept as in the models. In §2 each rule is given as an English statement followed by a paraphrase that was originally written in Turkish.)

## 0. Summary

- **Scope:** 5 rule schemata, 34 variants, 196 lemma runs.
  - 230 containers ran in total: 34 listing runs and 196 lemma runs.
  - Every lemma ran in a separate container (`metrikler.txt`, `calistir_log.txt`).
- **Agreement with the expectation:** expected and observed results agree 196/196. The expectations were written to the file `betik/varyantlar.tsv` before the run.
- **Acceptance criterion:** all five of R1–R5 PASSED.
  - In the protected variant the security lemma is verified.
  - In the mutant the security lemma is falsified.
  - `executable` is verified in all variants.
- **Mutation score:** 11/11 (100%).
  - Removing each protection gave a trace.
  - Each trace goes through the path opened by the removed protection.
    - For key protections (R1, R3, R4, R5) that key is broken with the CRQC.
    - For expectation protections (R2) the verifier opens the classical path without an expectation or with the value `'none'` supplied by the attacker; then the issuer's classical key is broken.
- **Layer 1↔2 link:** the Datalog (clingo) prediction and the Tamarin verdict are the same in 44/44 security lemmas. The agreement holds across the whole flag space (34 configurations).
- **Resource use:**
  - Longest run 1.58 s; highest memory 95.7 MiB.
  - All runs closed at step 1 of the ladder (`--prove`); none failed to close.
  - No well-formedness warnings (`uyarilar.txt` empty).
- **Finding that affects the plan (abstraction boundary):**
  - In the additional R1 variant `X_alt_ca` the issuer's own chain is entirely PQ. Still, a second CA that stayed classical under the same root allows forgery in the name of the honest issuer (G1 falsified).
  - A naive Datalog that reads `pq(L)` by looking only at the real parent says "secure" in this variant. This is the only disagreement in the 44 rows.
  - What makes the prediction correct is the semantics "all accepted signers" (key class).
  - Details in §6.5; its effect on ASP in the file `DECISION-NOTES.md`.

## 1. Scope, threat model and shared structure

### 1.1 Threat model (mapping to design document §7.4)

| §7.4 | Counterpart in the model |
|---|---|
| S1: Dolev–Yao network attacker | Tamarin's built-in attacker. It sees, drops, modifies and replays every message on the network. |
| S2: CRQC(τ, k) | A one-time rule `Qday` produces the fact `!CRQC()`. There is a restriction `Unique('qday')`; Q-day may also never happen. After Q-day the `CRQC_Break_*` rules reveal the private key of a classical public key **observed** by the attacker (`In(pk(sk))`). τ=0 and k is unbounded; this is the strongest form of S2. τ and k are the subject of R6. |
| S3: harvest-then-forge | Partly modelled. In R4 the device public key is visible only in a presentation. The attacker must first observe a presentation and can extract the key only afterwards. |
| ML-DSA/SLH-DSA EUF-CMA secure | There is **no** breaking rule for PQ keys. |
| Operators and issuers honest | The setup rules run without the attacker and with fresh keys. No insider attacker. |
| The verifier follows the tested policy | The verifier rules are the policy itself. Examples: P0 (at least one valid), a classical path gated by the expectation. |

Signatures are symbolic (`builtins: signing`). Verification is done with the restriction `Eq(verify(sig, m, pk), true)`.

### 1.2 Shared model structure

**Flags.** If a flag is defined, the protection is present.
- **Protected variant:** all protections on.
- **Mutant:** exactly one protection removed.
- **Additional:** the rest of the flag space. Run to test the Datalog agreement over the whole space.
- **Additional-boundary:** abstraction boundary test (`ALT_CA` and `NAME_BIND` in R1).
- **Additional-H5:** H5 preliminary signal (`SINGLE_USE` in R4).

**Lemma families** (in every model):
- **Sanity:** `executable`, `executable_post_qday`, `attack_needs_crqc`. The rule-specific `executable_legacy`, `attack_needs_crqc_G5` and `executable_single_use_enforced` are added to these.
- **Security:** `G1_claims_unforgeability`, `G2_presentation_unforgeability`, `G5_no_classical_acceptance`.
- **Mutation:** `M_*` (exists-trace).
  - Enters the model only if the relevant protection is removed.
  - Requires a trace in which the goal is violated. In the same trace it also requires the event tied to the removed protection:
    - for key protections, the `Broken(...)` event of that key,
    - in R2, acceptance of the migrated issuer via the classical path (`AcceptVia(…,'classical')` or `UsedExpectation(I,'none')`) and breaking of the issuer's classical key.
- **Information and boundary:**
  - `S1_downgrade_trace` (R2): downgrade trace without Q-day.
  - `X_alt_ca_forges_honest_issuer` (R1).

**Preprocessor limit.** In Tamarin 1.12 a nested `#ifdef` gives a parse error in the skipped branch; this was tried. The form `not (A | B)` is not parsed either. Therefore the models use only flat Boolean conditions (e.g. `#ifdef A & not B`).

**Run layout.**
- Every lemma runs in a separate container: `--rm`, `--memory=12g --memory-swap=12g`, `timeout 600`.
- Only one Tamarin container runs at a time. If another Tamarin container exists, the script waits.
- `betik/calistir.sh` applies steps 1→3→5→6 of the non-termination ladder automatically. Steps 2 and 4 are at model level and done by hand; none of them was needed (§7).

## 2. Formal statement, model and finding per rule

For each rule the following are given in order:
- English statement and a paraphrase (originally in Turkish).
- Tamarin lemma.
- Condition verified by Tamarin over the flag space. Source: `datalog_uyum.csv` and `varyant_ozeti.csv`.
- Trace content. Source: `izler.csv`; the protocol rules in the trace were read from the JSON traces.

### 2.1 R1 — chain (`modeller/R1_chain.spthy`)

**EN.** Let a verifier with a pinned anchor key accept credential `c` of issuer `I` iff it validates the chain anchor → `ca_cert` → `iss_cert` → `cred`. Under S1+S2, claims unforgeability (G1) holds iff the root, CA and issuer signing keys are all PQ. For every classical key `k` on the chain there is a trace in which `k` is extracted after Q-day and a never-issued credential is accepted, even when every link below `k` carries a PQ signature.

**Paraphrase.** Let the verifier's anchor key be pinned. Let the verifier accept credential `c` of issuer `I` only if it validates the chain anchor → `ca_cert` → `iss_cert` → `cred`. Under S1+S2, G1 holds if and only if all three of the root, CA and issuer signing keys are PQ. For every classical key `k` in the chain there is a trace: `k` is extracted after Q-day and a never-issued credential is accepted. This trace exists even if the links below `k` are PQ-signed.

**Lemma:**
```
lemma G1_claims_unforgeability:
  "All I c #j. Accept(I, c) @ #j ==> (Ex #i. Issued(I, c) @ #i & #i < #j)"
lemma M_<k>_classical:   /* k ∈ {root, ca, issuer}; only if k is classical */
  exists-trace "Ex I c #j #b. Accept(I, c) @ #j & Broken('<k>') @ #b & not (Ex #i. Issued(I, c) @ #i)"
```

**Condition verified by Tamarin:** G1 verified ⇔ `ROOT_PQ ∧ CA_PQ ∧ ISS_PQ`. This holds in 8 of the 8 flag configurations.

**Datalog mapping:**
- `ROOT_PQ ⇔ pq(ca_cert)`, `CA_PQ ⇔ pq(iss_cert)`, `ISS_PQ ⇔ pq(cred)`.
- `anchored(ca_cert)`, because `ca_cert` is signed by the pinned root key.

**Traces:**
- **`M_root`:** rules in the trace `Root_Setup, Qday, CRQC_Break_Root, Verify`.
  - The attacker extracts the root key and produces the CA certificate, the issuer certificate and the credential itself.
  - The rules of the honest CA and issuer are absent from the trace. The forgery propagates two levels down.
- **`M_ca`:** `CA_Setup, Qday, CRQC_Break_CA, Verify`.
- **`M_iss`:** `CA_Setup, Issuer_Setup, Qday, CRQC_Break_Issuer, Verify`.

**Additional-boundary variants:**
- **`X_alt_ca`:** a second CA under the same root stayed classical.
  - Result: G1 falsified.
  - Trace: `AltCA_Setup, Qday, CRQC_Break_AltCA, Verify`.
  - `X_alt_ca_forges_honest_issuer` verified: the name of an established honest issuer can be forged.
- **`X_alt_ca_namebind`:** the verifier binds the issuer name to its own CA. Result: G1 verified.

### 2.2 R2 — downgrade (`modeller/R2_downgrade.spthy`)

**EN.** Consider a migrated issuer holding a PQ key and a verifier whose default policy is any-valid (P0). G1 and G5 hold iff the classical key has been retired (no coexistence) or the verifier holds an *authenticated* per-issuer "PQ required" expectation. If the expectation is absent or unauthenticated, G5 is violated without any Q-day (S1 suffices), and G1 is violated after Q-day (S1+S2).

**Paraphrase.** Consider a migrated issuer with a PQ key and a verifier whose default policy is "at least one valid" (P0). G1 and G5 hold if one of these two conditions holds, and do not hold otherwise:
- the classical key has been retired (no coexistence),
- the verifier has an **authenticated** per-issuer "PQ required" expectation.

If the expectation is absent or unauthenticated, G5 is violated even without Q-day; S1 is enough. G1 is violated after Q-day (S1+S2).

**Lemma:**
```
lemma G1_claims_unforgeability:
  "All I c #m #j. Migrated(I) @ #m & Accept(I, c) @ #j ==> (Ex #i. Issued(I, c) @ #i & #i < #j)"
lemma G5_no_classical_acceptance:
  "All I c #m #j. Migrated(I) @ #m & AcceptVia(I, c, 'classical') @ #j ==> F"
lemma S1_downgrade_trace:   /* information: downgrade without Q-day */
  exists-trace "Ex I c #m #j. Migrated(I) @ #m & AcceptVia(I, c, 'classical') @ #j & not (Ex #q. QdayEv() @ #q)"
```

**Condition verified by Tamarin:** G1 and G5 verified ⇔ `NO_COEXIST ∨ EXPECT_AUTH`. This holds in 6 of the 6 configurations. `S1_downgrade_trace` is verified only in `M_expect_unauth` and `M_expect_absent`; falsified in the other 4 configurations (`ozet.csv`).

**Datalog mapping:**
- `coexist(cred) ⇔ ¬NO_COEXIST`.
- `EXPECT_AUTH ⇔ convey(cfg,cred)`; `cfg` cannot be forged.
- `EXPECT_UNAUTH ⇔ convey(net,cred)`; `net` can be forged.

**Traces:**
- **G5 violation (both mutants):** `Migrated_Issuer_Setup, Issue_Migrated, Verify_Classical`.
  - The trace has neither Q-day nor a break: the classical copy of an honest double issuance is accepted via the classical path.
  - In the variant `M_expect_unauth` the expectation value other than `pq_required` is supplied from the network by the attacker, because the honest announcement rule is absent from the trace.
- **G1 violation:** `Migrated_Issuer_Setup, Qday, CRQC_Break_Issuer_Classical, Verify_Classical`.

**Scope check (per entity):** `executable_legacy` is verified in 6 of the 6 variants. The classical path works for the old issuer in every variant. So the protection comes from the per-entity expectation, not from closing the classical path wholesale.

### 2.3 R3 — channel (`modeller/R3_channel.spthy`)

**EN.** Under coexistence, let the per-issuer expectation reach the verifier over a channel authenticated by key `k_ch`. The channel is either an object signature (TL/LoTE entry, signed metadata) or a nonce-bound transport session with the authoritative source. G1 and G5 hold iff `k_ch` is PQ. If `k_ch` is classical, every downgrade of a migrated issuer requires a CRQC break, so the channel is sound before Q-day. After Q-day there is a trace that forges "PQ not required" and then accepts classical-only evidence (G5) or a forged classical credential (G1).

**Paraphrase.** During coexistence, let the per-issuer expectation reach the verifier over a channel authenticated with the key `k_ch`. The channel can take two forms:
- an object signature (TL/LoTE entry, signed metadata),
- a nonce-bound transport session with the authoritative source.

G1 and G5 hold if and only if `k_ch` is PQ. If `k_ch` is classical, every downgrade of a migrated issuer requires a CRQC break; the channel is sound until Q-day. After Q-day there is a trace that forges the expectation "PQ not required". In the continuation of this trace either classical-only evidence is accepted (G5) or a forged classical credential is accepted (G1).

**Lemma:** G1 and G5 as in R2. Additional sanity lemma:
```
lemma attack_needs_crqc_G5:
  "All I c #m #j. Migrated(I) @ #m & AcceptVia(I, c, 'classical') @ #j ==> (Ex k #b. Broken(k) @ #b & #b < #j)"
```

**Condition verified by Tamarin:**
- G1 and G5 verified ⇔ `CHAN_PQ`. This holds for both channel kinds, in 4 of the 4 configurations.
- `attack_needs_crqc_G5` verified in 4 of the 4 configurations.

**Datalog mapping:** `CHAN_PQ ⇔ pq(chan)`, `anchored(chan)`, `convey(chan,cred)`. `VIA_TLS` has no Datalog counterpart.

**Traces:**
- **`M_obj_classical`, G5:** `Channel_Setup, Qday, CRQC_Break_Channel, Migrated_Issuer_Setup, Issue_Migrated, Verify_Classical`.
  - Only the channel key is broken; the honest classical copy is accepted.
- **`M_obj_classical`, G1:** the channel key and the issuer's classical key are broken together.
- **`M_tls_classical`:** the same traces, plus `Verifier_Fetch`.

**H1 note:**
- As long as the expectation is static, object signature and transport layer give the same verdict. A difference in freshness appears only when the expectation changes over time (R7).
- A conveyed artefact has no authenticated session with the authoritative source. This case corresponds to the `EXPECT_UNAUTH` variant of R2.

### 2.4 R4 — WSCD device key (`modeller/R4_wscd.spthy`)

**EN.** Presentation unforgeability / holder binding (G2) holds iff both keys are PQ: the device key bound as `cnf` and exercised in the KB-JWT, and the issuer key. With a classical device key there is a trace in which a genuinely issued, PQ-signed credential is presented with a KB-JWT forged for a fresh verifier nonce. In that trace the device key is extracted from its observed `cnf` public key. Wallet-side one-time use combined with global verifier-side single use does not remove this trace.

**Paraphrase.** Presentation unforgeability / holder binding (G2) holds if and only if both keys are PQ: the device key that is bound as `cnf` and signs the KB-JWT, and the issuer key. If the device key is classical, there is a trace like this:
- the device key is extracted from the observed `cnf` public key,
- a genuinely issued, PQ-signed credential is presented with a forged KB-JWT for a fresh verifier nonce.

This trace does not disappear even if single use on the wallet side and global single use on the verifier side are applied together.

**Lemma:**
```
lemma G2_presentation_unforgeability:
  "All I c pkd n #j. AcceptPres(I, c, pkd, n) @ #j ==> (Ex #p. Presented(pkd, n) @ #p & #p < #j)"
```

**Condition verified by Tamarin:** G2 verified ⇔ `DEV_PQ ∧ ISS_PQ`. This holds in 4 of the 4 configurations and in the 2 `SINGLE_USE` variants.

**Datalog mapping:** `DEV_PQ ⇔ pq(kb)`, `ISS_PQ ⇔ pq(cred)`, `signed_under(kb,cred)`, `anchored(cred)`.

**Traces:**
- **`M_dev`:** `Issuer_Setup, Issue, Holder_Present, Qday, CRQC_Break_Device, Verifier_Challenge, Verifier_Accept`.
  - The credential is seen once; this is the moment of harvesting.
  - Then it is accepted with a forged KB-JWT.
- **`M_iss`:** `Issuer_Setup, Qday, CRQC_Break_Issuer, Verifier_Challenge, Verifier_Accept`.
  - The trace has no `Issue` and no `Holder_Present`: the attacker itself forges a credential that binds its own device key.

**H5 preliminary signal:**
- In the variant `H5_single_use_dev_classical` G2 is falsified and `M_device_key_classical` verified.
- `executable_single_use_enforced` shows that the single-use restrictions really take effect (2/2 verified).

### 2.5 R5 — anchor (`modeller/R5_anchor.spthy`)

**EN.** With a PQ issuer key and the chain LOTL → TL → `cred`, G1 holds iff the TL signing key is PQ and either the TL key is pinned out of band or the LOTL key is PQ. In particular, a pinned PQ TL key makes G1 independent of the LOTL key type, whereas pinning a classical TL key does not help.

**Paraphrase.** Let the issuer key be PQ and the chain LOTL → TL → `cred`. G1 holds if and only if these two conditions hold together:
- the TL signing key is PQ,
- the TL key is pinned out of band or the LOTL key is PQ.

As a result, a pinned PQ TL key makes G1 independent of the type of the LOTL key. Pinning a classical TL key, however, does not help.

**Lemma:** G1 as in R1. Mutation lemmas:
- `M_pin_removed`: TL not pinned and LOTL classical; the trace contains `Broken('lotl')`.
- `M_anchor_classical`: TL key classical; the trace contains `Broken('tl')`.

**Condition verified by Tamarin:** G1 verified ⇔ `TL_PQ ∧ (PIN_TL ∨ LOTL_PQ)`. This holds in 8 of the 8 configurations.

**Datalog mapping:**
- `PIN_TL ⇔ anchored(tl)`, `TL_PQ ⇔ pq(tl)`, `LOTL_PQ ⇔ pq(lotl)`.
- `anchored(lotl)`, `signed_under(tl,lotl)`, `signed_under(cred,tl)`, `pq(cred)`.

**Traces:**
- **`M_pin`:** `LOTL_Setup, Qday, CRQC_Break_LOTL, Verify_via_LOTL`.
  - The attacker points the LOTL pointer at its own TL key. `TL_Setup` is absent from the trace.
- **`M_tl`:** `LOTL_Setup, TL_Setup, Pin_TL_Out_Of_Band, Qday, CRQC_Break_TL, Verify_Pinned_TL`.

## 3. Result table (34 variants)

**Abbreviations and columns:**
- **V** means verified, **F** falsified. For an exists-trace lemma, V means "trace found" and F "no trace".
- **Sanity:** how many of the sanity lemmas of the variant came out verified.
- **Lemmas:** number of lemmas run in the variant.
- **Time:** the longest of the lemma runs of the variant. Measured with wall-clock time inside the container; Tamarin start-up and Maude included, container start-up excluded.
- **Memory:** cgroup `memory.peak` value; Maude included.
| Rule | Variant | Role | Flags (`-D`) | Security | Mutation / additional lemma | Sanity | Lemmas | Max. time (s) | Max. memory (MiB) | As expected |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | `P_all_pq` | protected | ROOT_PQ, CA_PQ, ISS_PQ | G1 V | - | 3/3 | 4 | 1.32 | 75.5 | YES |
| R1 | `M_root` | mutant | CA_PQ, ISS_PQ | G1 F | M_root_classical V | 3/3 | 5 | 1.47 | 84.4 | YES |
| R1 | `M_ca` | mutant | ROOT_PQ, ISS_PQ | G1 F | M_ca_classical V | 3/3 | 5 | 1.38 | 84.9 | YES |
| R1 | `M_iss` | mutant | ROOT_PQ, CA_PQ | G1 F | M_issuer_classical V | 3/3 | 5 | 1.35 | 77.7 | YES |
| R1 | `E_iss_only` | additional | ISS_PQ | G1 F | M_root_classical V · M_ca_classical V | 3/3 | 6 | 1.58 | 94.2 | YES |
| R1 | `E_ca_only` | additional | CA_PQ | G1 F | M_root_classical V · M_issuer_classical V | 3/3 | 6 | 1.55 | 93.6 | YES |
| R1 | `E_root_only` | additional | ROOT_PQ | G1 F | M_ca_classical V · M_issuer_classical V | 3/3 | 6 | 1.48 | 89.4 | YES |
| R1 | `E_none` | additional | - | G1 F | M_root_classical V · M_ca_classical V · M_issuer_classical V | 3/3 | 7 | 1.58 | 95.7 | YES |
| R1 | `X_alt_ca` | additional-boundary | ROOT_PQ, CA_PQ, ISS_PQ, ALT_CA | G1 F | X_alt_ca_forges_honest_issuer V | 3/3 | 5 | 1.47 | 89.8 | YES |
| R1 | `X_alt_ca_namebind` | additional-boundary | ROOT_PQ, CA_PQ, ISS_PQ, ALT_CA, NAME_BIND | G1 V | - | 3/3 | 4 | 1.52 | 76.1 | YES |
| R2 | `P_expect_auth` | protected | EXPECT_AUTH | G1 V · G5 V | - | 4/4 | 7 | 0.96 | 78.1 | YES |
| R2 | `M_expect_unauth` | mutant | EXPECT_UNAUTH | G1 F · G5 F | M_expectation_unauthenticated V | 4/4 | 8 | 0.97 | 76.3 | YES |
| R2 | `M_expect_absent` | mutant | - | G1 F · G5 F | M_expectation_absent V | 4/4 | 8 | 0.88 | 76.6 | YES |
| R2 | `E_nocoexist_auth` | additional | NO_COEXIST, EXPECT_AUTH | G1 V · G5 V | - | 4/4 | 7 | 0.84 | 75.8 | YES |
| R2 | `E_nocoexist_unauth` | additional | NO_COEXIST, EXPECT_UNAUTH | G1 V · G5 V | - | 4/4 | 7 | 0.87 | 75.8 | YES |
| R2 | `E_nocoexist_none` | additional | NO_COEXIST | G1 V · G5 V | - | 4/4 | 7 | 0.81 | 75.6 | YES |
| R3 | `P_obj_pq` | protected | CHAN_PQ | G1 V · G5 V | - | 5/5 | 7 | 1.29 | 78.0 | YES |
| R3 | `P_tls_pq` | protected | CHAN_PQ, VIA_TLS | G1 V · G5 V | - | 5/5 | 7 | 1.44 | 80.0 | YES |
| R3 | `M_obj_classical` | mutant | - | G1 F · G5 F | M_channel_classical V | 5/5 | 8 | 1.27 | 78.6 | YES |
| R3 | `M_tls_classical` | mutant | VIA_TLS | G1 F · G5 F | M_channel_classical V | 5/5 | 8 | 1.56 | 78.4 | YES |
| R4 | `P_dev_iss_pq` | protected | DEV_PQ, ISS_PQ | G2 V | - | 3/3 | 4 | 1.5 | 80.2 | YES |
| R4 | `M_dev` | mutant | ISS_PQ | G2 F | M_device_key_classical V | 3/3 | 5 | 1.46 | 81.7 | YES |
| R4 | `M_iss` | mutant | DEV_PQ | G2 F | M_issuer_classical V | 3/3 | 5 | 1.4 | 81.7 | YES |
| R4 | `E_none` | additional | - | G2 F | M_device_key_classical V · M_issuer_classical V | 3/3 | 6 | 1.57 | 84.9 | YES |
| R4 | `H5_single_use_dev_classical` | additional-H5 | ISS_PQ, SINGLE_USE | G2 F | M_device_key_classical V | 4/4 | 6 | 1.46 | 83.7 | YES |
| R4 | `H5_single_use_protected` | additional-H5 | DEV_PQ, ISS_PQ, SINGLE_USE | G2 V | - | 4/4 | 5 | 1.41 | 76.8 | YES |
| R5 | `P_pin_tlpq` | protected | PIN_TL, TL_PQ | G1 V | - | 3/3 | 4 | 1.0 | 75.0 | YES |
| R5 | `M_pin` | mutant | TL_PQ | G1 F | M_pin_removed V | 3/3 | 5 | 1.48 | 84.6 | YES |
| R5 | `M_tl` | mutant | PIN_TL | G1 F | M_anchor_classical V | 3/3 | 5 | 1.08 | 75.1 | YES |
| R5 | `E_none` | additional | - | G1 F | M_pin_removed V · M_anchor_classical V | 3/3 | 6 | 1.56 | 92.5 | YES |
| R5 | `E_lotlpq` | additional | LOTL_PQ | G1 F | M_anchor_classical V | 3/3 | 5 | 1.4 | 84.1 | YES |
| R5 | `E_lotlpq_tlpq` | additional | LOTL_PQ, TL_PQ | G1 V | - | 3/3 | 4 | 1.32 | 73.8 | YES |
| R5 | `E_pin_lotlpq` | additional | PIN_TL, LOTL_PQ | G1 F | M_anchor_classical V | 3/3 | 5 | 0.98 | 76.0 | YES |
| R5 | `E_all_pq_pin` | additional | PIN_TL, TL_PQ, LOTL_PQ | G1 V | - | 3/3 | 4 | 0.89 | 74.4 | YES |

Source: `sonuc/varyant_ozeti.csv`. Per-lemma details in the files `sonuc/ozet.csv` and `sonuc/degerlendirme.csv`.

**Overall distribution** (`ozet.csv`, `degerlendirme.csv`):
- **Results:** of the 196 lemma runs, 167 verified, 29 falsified.
- **Kinds:** 118 sanity, 44 security, 27 mutation, 6 information (`S1_downgrade_trace`), 1 boundary (`X_alt_ca_forges_honest_issuer`).
- **Time per lemma:** minimum 0.64 s, median 1.22 s, maximum 1.58 s. Total 228.4 s.
- **Memory:** minimum 69.0 MiB, median 75.8 MiB, maximum 95.7 MiB.
- **Proof/trace step count:** between 2 and 19.
- **Batch run time:** including 230 container start-ups, it ran from 00:02:33 to 00:12:34 (`calistir_log.txt`).

## 4. Mutation score

**Definition** (`betik/degerlendir.py`). A protection counts as "killed" if, in the single-mutant variant where it is removed, these two conditions hold together:
- all security lemmas falsified,
- the `M_` lemma verified; that is, the attack trace goes through the event tied to the removed protection (§1.2):
  - for key protections, breaking of that key,
  - in R2, acceptance via the classical path without an expectation or with the expectation `'none'`.

**Score: 11/11 = 100%** (`metrikler.txt`).

| Rule | Removed protection | Mutant | Security | Mutation lemma | CRQC break in the security trace | Result |
|---|---|---|---|---|---|---|
| R1 | root key PQ | `M_root` | G1 F | M_root_classical V | G1: CRQC_Break_Root | KILLED |
| R1 | CA key PQ | `M_ca` | G1 F | M_ca_classical V | G1: CRQC_Break_CA | KILLED |
| R1 | issuer signature PQ | `M_iss` | G1 F | M_issuer_classical V | G1: CRQC_Break_Issuer | KILLED |
| R2 | authentication of the expectation | `M_expect_unauth` | G1 F · G5 F | M_expectation_unauthenticated V | G1: CRQC_Break_Issuer_Classical; G5: - | KILLED |
| R2 | expectation | `M_expect_absent` | G1 F · G5 F | M_expectation_absent V | G1: CRQC_Break_Issuer_Classical; G5: - | KILLED |
| R3 | PQ channel (object signature) | `M_obj_classical` | G1 F · G5 F | M_channel_classical V | G1: CRQC_Break_Channel+CRQC_Break_Issuer_Classical; G5: CRQC_Break_Channel | KILLED |
| R3 | PQ channel (transport) | `M_tls_classical` | G1 F · G5 F | M_channel_classical V | G1: CRQC_Break_Channel+CRQC_Break_Issuer_Classical; G5: CRQC_Break_Channel | KILLED |
| R4 | PQ device key | `M_dev` | G2 F | M_device_key_classical V | G2: CRQC_Break_Device | KILLED |
| R4 | PQ issuer signature | `M_iss` | G2 F | M_issuer_classical V | G2: CRQC_Break_Issuer | KILLED |
| R5 | pinning | `M_pin` | G1 F | M_pin_removed V | G1: CRQC_Break_LOTL | KILLED |
| R5 | anchor key PQ | `M_tl` | G1 F | M_anchor_classical V | G1: CRQC_Break_TL | KILLED |

Source: `sonuc/metrikler.txt`, `sonuc/varyant_ozeti.csv`, `sonuc/izler.csv`.

**Reading the table:**
- **"G5: -":** there is no break in the G5 trace. The downgrade happens without Q-day, with S1 (§2.2).
- **R2/R3 G1 traces:** these traces also contain breaking of the issuer's classical key. This key is not a protection but the premise of coexistence (`coexist`).
- **Keys broken in single-mutant traces:** the key of the removed protection and (if present) only this premise. The key of no other protection is broken.
- **Beyond single mutants:** in the additional variants every `M_` lemma is verified too. In total 27/27 (`ozet.csv`). So every remaining classical key is sufficient for an attack on its own; this is consistent with K1/K2 (§6).

## 5. Sanity lemmas

| Lemma | Verified / runs |
|---|---|
| `executable` | 34/34 |
| `executable_post_qday` | 34/34 |
| `attack_needs_crqc` | 34/34 |
| `executable_legacy` | 10/10 |
| `attack_needs_crqc_G5` | 4/4 |
| `executable_single_use_enforced` | 2/2 |
| **Total** | **118/118** |

Source: `sonuc/ozet.csv`. All sanity lemmas verified: 118/118.

| Lemma | What it shows |
|---|---|
| `executable` (exists-trace) | Honest issuance → acceptance (in R4 issuance → presentation → acceptance) is reachable in every variant. The restrictions (`Eq`, `Unique`, single use) do not empty the model. This is the item "the model is executable" of H0. |
| `executable_post_qday` | Honest acceptance is also possible **after** Q-day. The "verified" in the protected variants is not vacuous due to acceptance after Q-day being impossible. |
| `attack_needs_crqc` (all-traces) | Every violation of the G1/G2 form is preceded by a `Broken(k)`. The model is sound before Q-day; classical cryptography is not broken artificially. The cause of every falsified result is the CRQC. |
| `executable_legacy` (R2, R3) | The classical path of the old issuer works in every variant. In R3 this path really consumes the channel (`UsedExpectation(L,'none')`). The protection is per entity; the classical path is not closed wholesale. |
| `attack_needs_crqc_G5` (R3) | With an authenticated channel (even a classical one), every downgrade of a migrated issuer needs a break. The channel is sound until Q-day. |
| `executable_single_use_enforced` (R4, `SINGLE_USE`) | The single-use restrictions really work; a credential is accepted at most once. The H5 trace does not come from an empty restriction. |

**Other sanity checks at model level** (from the raw outputs):
- **Well-formedness:** "All wellformedness checks were successful" in 34 of the 34 listing runs (`sonuc/ham/*__liste.txt`; `uyarilar.txt` empty).
  - The pilot `weakest_link.spthy` gave a "Fact multiplicity" warning in Tamarin 1.12 because it used the name `Qday` both as an action and as a state fact.
  - In these models the names were separated: action `QdayEv()`, state fact `!CRQC()`.
- **Source saturation:**
  - In all 194 lemma runs that entered source saturation, saturation ended at step 1 ("Saturating Sources … Step 1 (Max 5) … Done").
  - The remaining 2 runs (`executable_single_use_enforced`) closed directly from the restriction in 2 steps.
  - No raw output contains the phrase "partial deconstruction" (0/230).
- **Exit codes:** `rc=0` in all 230 runs (`sonuc/ham/*.meta`).
- **Link with H0:** H0 additionally requires "a stripping trace under the at-least-one-valid policy". Its counterpart in the model is `S1_downgrade_trace = V` in the variant `R2 M_expect_absent`.
  - This is acceptance of the classical copy in double issuance under P0; the symbolic counterpart of stripping the PQ signature from a multi-signed object.
  - It is a trace without Q-day.

## 6. Datalog counterpart and the abstraction link

### 6.1 Core rules (`modeller/datalog/core.lp`)

The core is identical to the four rules of pilot P2 (review B §3.3). The meaning is for after Q-day:

| Predicate | Meaning |
|---|---|
| `pq(L)` | the key that **signs** `L` is PQ |
| `classical(L)` | the key that signs `L` is classical |
| `signed_under(L,P)` | `P` binds the key that signs `L` |
| `anchored(L)` | the key that signs `L` is pinned out of band |
| `convey(C,X)` | the expectation about `X` is carried by channel `C` |
| `coexist(L)` | the classical and the PQ form of `L` are valid together |

```
K1  forgeable(L) :- classical(L).
K2  forgeable(L) :- signed_under(L,P), forgeable(P), not anchored(L).
K3  expected(X)  :- convey(C,X), not forgeable(C).
K4  forgeable(L) :- pq(L), coexist(L), not expected(L).
G5 counterpart (in the instance files):  violated(g5) :- coexist(X), not expected(X).
```

**Instance files.**
- The files `R1_chain.lp` … `R5_anchor.lp` take the Tamarin `-D` flags with the same names, in lower case, as `flag/1` facts.
- `betik/degerlendir.py` runs clingo for every variant and expects a single stable model. This held in 34 of the 34 configurations; otherwise the script would have raised an error.

### 6.2 Rule → Datalog mapping

The closed forms in the last column [Y]: derived by hand from the rules. The predictions produced by clingo in 34 configurations are the same as these closed forms (`datalog_uyum.csv`).

| Rule | Datalog rules | Violation atom | Closed form of the violation [Y] |
|---|---|---|---|
| R1 | K1 + K2 | `violated(g1) :- forgeable(cred)` | `¬pq(cred) ∨ ¬pq(iss_cert) ∨ ¬pq(ca_cert)` |
| R2 | K3 + K4 | g1: `forgeable(cred)`; g5: `coexist ∧ ¬expected` | `coexist(cred) ∧ ¬convey(cfg,cred)`; since `net` can be forged, `EXPECT_UNAUTH` provides no expectation |
| R3 | K3 + K4 | as in R2 | `¬pq(chan)`; the same for both channel kinds |
| R4 | K1 + K2 | `violated(g2) :- forgeable(kb)` | `¬pq(kb) ∨ ¬pq(cred)` |
| R5 | K1 + K2 (`not anchored` protection) | `violated(g1) :- forgeable(cred)` | `¬pq(tl) ∨ (¬anchored(tl) ∧ ¬pq(lotl))` |

### 6.3 Agreement: clingo prediction ↔ Tamarin verdict

| Rule | Configurations | Security lemma rows | `sem=class` agreement | `sem=naive` agreement |
|---|---|---|---|---|
| R1 | 10 | 10 | 10/10 | 9/10 |
| R2 | 6 | 12 | 12/12 | 12/12 |
| R3 | 4 | 8 | 8/8 | 8/8 |
| R4 | 6 | 6 | 6/6 | 6/6 |
| R5 | 8 | 8 | 8/8 | 8/8 |
| **Total** | **34** | **44** | **44/44** | **43/44** |

Source: `sonuc/datalog_uyum.csv`, `sonuc/metrikler.txt`.
- The comparison was made as follows: if Datalog derives `violated(g)`, `falsified` was expected from Tamarin, otherwise `verified`.
- `SINGLE_USE` has no Datalog counterpart. The prediction did not change, and Tamarin also gave an unchanged verdict. This is consistent with H5.

### 6.4 Why do the Tamarin results support the Datalog rules?

The link of the "proven abstraction" was established in both directions for every instance.

**(⇒) If a rule fires, there is an attack.** In every configuration where Datalog derives a violation, Tamarin found a concrete trace. Each rule firing on its own is witnessed by a separate `M_` lemma:
- **K1 (a classical link can be forged):**
  - `M_issuer_classical` (R1): the link's own signing key is classical.
  - `M_device_key_classical` (R4): the key of the KB-JWT is classical; the credential is genuine.
  - `M_anchor_classical` (R5): the pinned anchor itself is classical.
- **K2 (forgeability propagates downwards):**
  - `M_ca_classical` (R1): propagation by one level.
  - `M_root_classical` (R1): propagation by two levels; the trace has no honest CA or issuer rule (§2.1).
  - `M_issuer_classical` (R4): propagation to `kb` via a forged `cred`, i.e. cnf substitution.
  - `M_pin_removed` (R5): lotl → tl → cred propagation.
- **K3 (the expectation is carried only by a channel that cannot be forged):**
  - `M_channel_classical` (R3): `forgeable(chan)` drops the expectation.
  - `M_expectation_unauthenticated` (R2): the `net` channel drops the expectation.
- **K4 (a PQ-signed link can be forged in coexistence without an expectation):**
  - `M_expectation_absent` and `M_expectation_unauthenticated` (R2): a credential that has a PQ path is forged via the classical path.

**(⇐) If no rule fires, there is no attack.** In every configuration where Datalog derives no violation, Tamarin proved the all-traces lemma. The proofs are unbounded (no `--bound`). So in these instances there is no attack outside K1–K4. The protective conditions of the rules are also witnessed by verified results:
- **`not anchored(L)` in K2:** `R5 P_pin_tlpq` verified. Although `forgeable(lotl)` is true in Datalog (LOTL classical), forgeability does not pass to the pinned TL.
- **`coexist(L)` in K4:** `R2 E_nocoexist_none` verified without any expectation.
- **`not forgeable(C)` in K3:** `R3 P_obj_pq` and `P_tls_pq` and `R2 P_expect_auth` verified.

**Conclusion.** In every schema instance the set of insecure configurations is the same in Datalog and in Tamarin (44/44). Every firing of the Layer 1 rules is justified by a Tamarin trace. The Tamarin proofs also show that in these instances the rules cover the attacks completely.

**What the link does not show:**
- Generalisation to the full model with 13 artefacts. This is the job of the composability argument and of the abstraction sampling in Layer 3.
- Time and τ (R6), rollback and monotonicity (R7).
- Reading over all members of a class (below, §6.5).

### 6.5 `X_alt_ca`: the naive edge semantics misses the alternative-path attack

**Setup** (`R1 X_alt_ca`):
- Flags: `ROOT_PQ, CA_PQ, ISS_PQ` and `ALT_CA`.
- The issuer's own chain (root → CA → issuer) is entirely PQ.
- There is a second CA under the same root and its key is classical: the CA class has partly migrated.
- The verifier accepts an `iss_cert` signed by **any** CA certified by the root. There is no name constraint.

**Tamarin** (`izler.csv`, `varyant_ozeti.csv`):
- **`X_alt_ca`:** `G1 = F`. Trace: `AltCA_Setup, Qday, CRQC_Break_AltCA, Verify` (+ `Root_Setup`).
- **`X_alt_ca_forges_honest_issuer = V`:** in the trace the honest issuer is set up with its own PQ CA (`CA_Setup, Issuer_Setup`). The attacker still forges a credential in that issuer's name, because it breaks the classical key of the alternative CA.
- **`X_alt_ca_namebind`:** the verifier binds the issuer to its own CA (`NAME_BIND`). Result: `G1 = V`.

**Datalog** (`metrikler.txt`):
- **`sem=naive` (the implicit reading of the pilot):** looks only at the real parent (`signed_under(iss_cert, ca_cert)`, `pq(iss_cert) ⇔ CA_PQ`). It says "no violation". This is the **only** disagreement in the 44 rows: `R1 X_alt_ca g1: naive=verified tamarin=falsified`.
- **`sem=class`:** `pq(iss_cert)` is true only if **all** CA keys that the verifier **accepts** as signers for this issuer's certificate are PQ. Rule: `alt_acceptable :- flag(alt_ca), not flag(name_bind)`. This semantics predicts the violation correctly. Under `NAME_BIND` both semantics say "secure" and agree with Tamarin.

**Meaning.** The forgeability of a link is not determined by the key that **actually** signs that link. It is determined by the weakest of the keys that the verifier **would accept** as signers for that link. The naive edge semantics follows only the real signature edge and therefore cannot see the alternative-path attack. The key-class ("set of accepted signers") semantics is therefore necessary.

**Counterpart in DNSSEC.** This has the same structure as DNSSEC's "any valid path" rule. The primary source was opened: `spec-corpus/metin/RFC6840.txt`.
- **RFC 6840 §5.11:** *"This requirement applies to servers, not validators. Validators SHOULD accept any single valid path."*
- **RFC 6840 §6.2:** *"… there is no way to tell resolvers what a particular DNSKEY is supposed to be used for -- any DNSKEY in the zone's signed DNSKEY RRset may be used to authenticate any RRset in the zone. For example, if a weaker or less trusted DNSKEY is being used to authenticate NSEC RRsets or all dynamically updated records, that same DNSKEY can also be used to sign any other RRsets from the zone."*
- **RFC 6840 Appendix C.2 ("Accept Any Success"):** *"… making the validator subject to the compromise of the weakest of these trust anchors …"*

**Mapping** [Y]:
- "Any DNSKEY validates any RRset" ↔ "any CA certified by the root certifies any issuer".
- "Weak DNSKEY" ↔ "CA that stayed classical".
- Name constraint or issuer→CA binding (`NAME_BIND`) ↔ an authenticated signal that tells the verifier which key may sign what. DNSSEC has no such signal (§6.2).

`X_alt_ca` reproduces this structure symbolically in the credential chain. The KAT-1 known-answer test itself is the job of Layer 3.

**Consequence for Layer 1 (ASP):**
- `pq(L)` must be read over an artefact class: "every signer that the verifier accepts for `L` is PQ".
- Or `signed_under` must count every acceptable parent as an edge.
- Or a name-binding predicate that narrows the accepted set must be added.

Otherwise ASP undercounts the attacks and the minimal sets come out smaller than they should; this would not be sound for a security claim. In the M2 cost as well, a class should count as "migrated" only when all its members are PQ (or name-constrained). Details and proposal: `DECISION-NOTES.md`.

## 7. Non-termination ladder

| Step | Application | Runs where used |
|---|---|---|
| 1 `--prove=<lemma>` | Automatic | **196/196** |
| 2 `[use_induction]` / `[reuse]` | At model level, by hand | 0 (not needed) |
| 3 `--auto-sources` | Automatic (if 1 does not close) | 0 |
| 4 tactic / oracle | At model level, by hand | 0 |
| 5 `--bound=40` | Automatic (if 3 does not close) | 0 |
| 6 label "did not close" | Automatic | 0 |

Source: `sonuc/ozet.csv` (column `merdiven_basamagi`) and `sonuc/metrikler.txt`.
- Longest time per run 1.58 s, highest memory 95.7 MiB. Far below the limits of 10 min and 12 GB.

**Why so fast?** [Y]
- The models have no unbounded loops. The chains have fixed length; a single instance of each role is ensured with the restriction `Unique`.
- The pilot's `delegation_loop.spthy` was different: the unbounded delegation loop timed out without help and closed with `[use_induction]` (`tools/README.md`).
- In R6/R7 repeating structures such as counters, versions or epochs will come. There, step 2 (an induction lemma) will most likely be needed (estimate).

## 8. Limitations

1. **Symbolic model.**
   - Signatures are ideal. Algorithm confusion, weak non-separability (WNS) of the hybrid/composite combiner, encoding and length attacks are out of scope.
   - The only difference between "classical" and "PQ" is that the key can be extracted after Q-day.
2. **CRQC abstraction.**
   - Q-day is a single global event. Extraction is instantaneous (τ=0), with no per-window key limit (k=∞).
   - Time per key and the regimes (fast/medium/slow) were not modelled. This is the subject of R6.
3. **No time dimension.**
   - Validity periods, acceptance and exposure windows, the old-version window and the sunset were not modelled.
   - Therefore G5 is in the **untimed** form: "a migrated entity is never accepted with classical evidence only".
   - The phrase "outside its announced old-version window" in the design document (§7.4) will be modelled in R6/R7.
4. **No key reuse.**
   - Use of the same key in several roles (e.g. TLS and object signature) or in several windows was not modelled.
   - The device key is fresh per credential. This topic will be addressed in R6/R7.
5. **Small instances.**
   - There is a single instance of each role (`Unique` restrictions). Only the additional-boundary variant of R1 has a second CA.
   - The Datalog–Tamarin agreement was shown on these instances. It is not a general theorem.
   - Generalisation to the full model with 13 artefacts will be built with the Layer 3 sampling and the composability argument.
6. **Transport abstraction in R3.**
   - TLS was reduced to a single nonce-bound server authentication signature. The WebPKI chain was folded into a single key; chain effects are in R1.
   - Handshake details and hybrid KEM confidentiality were not modelled; the network attacker sees everything.
   - Since the expectation is static, the freshness difference was not tested (R7).
7. **Assumptions in R4.**
   - Relaying a live presentation was not counted as a G2 violation; this is the standard assumption for a KB-JWT without channel binding.
   - The issuance channel was assumed confidential.
   - The global verifier state in the variant `SINGLE_USE` is idealised and deliberately in its strongest form; real verifiers do not share state. The trace of this variant is a **preliminary signal**; the formal test of H5 will be done with the R6 windows.
8. **Protected variants of R1 and R4.**
   - These two variants have no classical key at all; security against the CRQC is therefore an easy result.
   - Their content is carried by the mutants and the whole flag space.
   - In the protected variants of R2, R3, R5 and in the variant `X_alt_ca_namebind` of R1 the CRQC is active: there is a breakable classical key. There, what prevents the attack is the protection itself.
9. **Honest parties.** A malicious issuer or TL operator is out of scope (§7.4).
10. **Number of verifiers.** Each model has a single verifier logic. The coexistence of verifiers with different policies was not modelled.
11. **Nature of the Datalog comparison.** The comparison is clingo output, not Tamarin output. The instance files were written in this step; they are not identical to the ASP model of Step 3. The link was built at the level of the core rules (K1–K4).

## 9. Contribution to the technical gate (Tamarin part)

| Criterion (task definition) | Result | Source |
|---|---|---|
| In each of R1–R5 the protected variant verified, the unprotected variant falsified, `executable` verified | R1–R5 **PASSED** (5/5) | `metrikler.txt` |
| Mutation score 100% | **11/11 = 100%** | `metrikler.txt` |
| Every run ≤10 min and ≤12 GB | Longest 1.58 s; highest 95.7 MiB | `ozet.csv` |
| Runs that do not close are reported with the ladder | 0 not closed; all at step 1 | `ozet.csv` |

**Additional assurance** (beyond the acceptance criterion):
- Expected/observed agreement 196/196.
- Layer 1↔2 (Datalog↔Tamarin) agreement 44/44.
- Sanity lemmas 118/118 verified.
- No well-formedness warnings.

**Time estimate for Layer 3** (estimate): median time per lemma 1.22 s, about 3 s per row including container start-up. On this basis an abstraction sampling of 50–200 instances, with ~5 lemmas per instance, finishes in the order of minutes.

**Verdict:** the Tamarin part of the technical gate **passed**.

**What the gate leaves open:**
- R6 and R7.
- The decision on the class semantics of ASP (§6.5).
- Layer 3: abstraction sampling, known-answer tests, ProVerif second opinion.

## 10. Recommendations for Step 5

The designs below are proposals; they have not been run yet. The expected results are estimates. The structure will be the same as R1–R5:
- flag = protection,
- single-mutant variants,
- `M_` lemmas,
- sanity lemmas,
- Datalog counterpart and the `betik/` layout (container per lemma, ladder, JSON trace).

### 10.1 R6 — time window (H2, H5; §7.13 "Tamarin R6 instances")

**Proposed rule statement:**
- A classical link `L` can be forged only if the CRQC can finish extracting the key that signs `L` before the verifier stops accepting that key for `L`.
- For short-lived artefacts signed with a long-lived key, the decisive window is the window of the **key**, not of the artefact (key reuse).

**Model sketch.** No numerical time; only event order is used, because Tamarin supports it directly.
- **Key window:**
  - `Activate(k)` produces a linear fact `Window(k)`; `Close(k)` consumes it.
  - The verifier's acceptance rule reads `Window(k)` (consume and reproduce). After `Close(k)` acceptance with `k` becomes impossible.
- **Two-phase CRQC:**
  - After Q-day `CRQC_Start(k)` runs (requires `In(pk(k))`) and produces the fact `Extracting(k)`.
  - `CRQC_Done(k)` consumes this fact and releases `sk`.
  - Today's single-phase `CRQC_Break_*` is the τ=0 form of this.
- **τ regime, as a restriction:**
  - `SLOW` (τ > window): `All k #a #d. Activate(k)@a & CRQC_Done(k)@d ==> (Ex #c. Close(k)@c & #c < #d)`.
  - `FAST`: this restriction is absent.
  - Optional: a counter-based window can be built with the natural-number support of Tamarin 1.12. The syntax must be checked against the manual before use.
- **Flags:**
  - `SLOW`,
  - `SHORT_KEY_WINDOW`: the key rotates in a short window. E.g. a device key tied to a credential with short validity, or a short-lived status signing key.
  - `KEY_REUSE`: the signing key continues to be used beyond the artefact windows.
- **Expected result** (estimate): there is no trace only in the case `SLOW ∧ SHORT_KEY_WINDOW ∧ ¬KEY_REUSE`.
- **Mutants:**
  - `SLOW` removed, i.e. `FAST` → trace.
  - `SHORT_KEY_WINDOW` removed → trace.
  - `KEY_REUSE` added → trace.
- **Lemma:** `G_window` (all-traces): for every accepted forged artefact, `CRQC_Done(k) < Close(k)` held for the relevant key `k`.
- **H5 link:** the combination R4 × R6. Let the device key be classical, together with `SINGLE_USE` and a short credential validity:
  - G2 verified under `SLOW`,
  - a trace under `FAST`.

  This is the formal test of the part "only the validity period limits" of H5.
- **Datalog/ASP counterpart (numerical):** `forgeable(L) :- classical(L), key_of(L,K), tau(T), window(K,W), T < W.` ASP sweeps the A5 grid; Tamarin verifies the order-based version of each regime cell.
- **Ladder risk:** no loops, only linear facts; therefore low. If the window is built with a counter, step 2 (`[use_induction]`) may be needed.

### 10.2 R7 — monotone expectation (M-f and the A3 component ablation; H3, the timed form of G5)

**Proposed rule statement:**
- A verifier resists downgrade and rollback against the expectation of a migrated issuer only under these four conditions:
  - the expectation it uses is PQ-authenticated,
  - it is fresh or pinned,
  - it is monotone at the verifier: once "PQ required" has been learned, it is not replaced by a weaker value,
  - it is scoped per entity.
- After the announced sunset, classical-only evidence is never accepted. This is the timed form of G5.

**Model sketch:**
- **Issuer lifecycle:**
  - `Setup(I)`: record `'none'`, version v0.
  - `Migrate(I)`: record `'pq_required'`, version v1.
  - `Sunset(I)`: end of the old-version window; the classical key is retired.
- **Channel (from R3):**
  - The source signs versioned objects: `<'expect', I, e, v>`.
  - The attacker records the old v0 object and replays it after migration. It can do this even if the channel key is PQ.
- **Verifier options (flag = component):**
  - `PQ_CHAN`: channel key PQ.
  - `FRESH`: nonce-bound transport, or an object tied to the R6 window.
  - `PINNED`: provided out of band, updated only by an authenticated event.
  - `MONOTONE`: persistent `!Sticky(I)`.
  - `PER_ENTITY`: per-issuer expectation instead of a global switch.
  - `SUNSET_CHECK`.
- **Protected variant (M-f):** `PQ_CHAN ∧ (FRESH ∨ PINNED) ∧ MONOTONE ∧ PER_ENTITY ∧ SUNSET_CHECK`. Expected: verified.
- **Ablation (A3) mutants and their expected traces** (estimate):

| Removed component | Expected trace | Mechanism class counterpart |
|---|---|---|
| Authentication | S1 downgrade. R2 `EXPECT_UNAUTH` already shows this | M-a (unauthenticated negotiation) |
| PQ channel | Forgery of the expectation after Q-day (R3) | M-d (registration over a classical channel) |
| Freshness or pinning | **Rollback**: replay of the PQ-signed old v0 `'none'` object | M-e (difference between "supported" and "required") and static metadata |
| Monotonicity | A verifier that has once seen `'pq_required'` later accepting `'none'` | — |
| Per-entity scope | Global "PQ only": the old issuer breaks, `executable_legacy` falsified. Global "any-valid": downgrade for everyone | M-b / M-c (one is enough; the attacker chooses) |
| Sunset check | Classical acceptance after the sunset (timed G5 falsified) | — |

- **Lemmas:**
  - `G5_timed`: `All I c #s #j. Sunset(I)@s & AcceptVia(I,c,'classical')@j & #s < #j ==> F`.
  - `no_rollback`: `All V I c #k #j. SeenPQReq(V,I)@k & AcceptVia(V,I,c,'classical')@j & #k < #j ==> F`.
  - In addition G1 and `M_*` lemmas per component.
- **Datalog counterpart:** extends K3.
  - `expected(X) :- convey(C,X), not forgeable(C), fresh_or_pinned(C,X), monotone(X).`
  - `rollback(X) :- migrated(X), convey(C,X), not fresh_or_pinned(C,X).`
  - G5 violation: `coexist(X), not expected(X)`; in addition classical acceptance after the sunset.
- **Ladder risk:** the number of versions is finite (v0, v1) and there is persistent state; therefore low. If a multi-version or counter-based setup is chosen, step 2 may be needed.

### 10.3 Other recommendations

1. **ASP class semantics (§6.5).**
   - A relation `accepted_signer(L,K)` or a class-level definition of `pq(L)` should be added. A name-binding predicate should be added as well.
   - Multi-member tests R1b and R5b should be made:
     - several CAs per TL,
     - several TLs in the LOTL (the LOTL has 43 pointers; partial TL migration).
   - The decision should be made before the ASP results are frozen.
2. **Layer 3 sampling generator.**
   - It should generate flag files from the minimal sets of ASP.
   - Because of the preprocessor limit of Tamarin 1.12 it should use only flat Boolean `#ifdef` or generate a separate file per instance.
   - The layout of `betik/calistir.sh` and `betik/degerlendir.py` can be reused directly.
3. **KAT-1 (DNSSEC).** The edge semantics "any DNSKEY validates any RRset" of RFC 6840 §6.2 should be added to the instance `dnssec.yaml`. This is the mirror of `X_alt_ca`.
4. **Strictness.** `--quit-on-warning` can be added to the run scripts of the later steps. Tamarin 1.12 has such an option; it stops on a well-formedness warning.
5. **ProVerif second opinion (Layer 3.3).** The 11 mutants and 5 protected variants of R1–R5 can be transferred to ProVerif. The result "cannot be proved" should count as "unknown".

## 11. Files and reproduction

```
models/tamarin/
  modeller/R1_chain.spthy  R2_downgrade.spthy  R3_channel.spthy  R4_wscd.spthy  R5_anchor.spthy
  modeller/datalog/core.lp  R1_chain.lp … R5_anchor.lp        (Datalog/ASP counterparts)
  betik/calistir.sh        batch run (Git Bash); then degerlendir.py
  betik/ic_kosum.sh        single call inside the container: time + cgroup memory peak
  betik/varyantlar.tsv     34 variants; expectations written before the run
  betik/degerlendir.py     expected/observed, mutation score, clingo comparison, trace contents
  sonuc/ozet.csv           kural,varyant,lemma,sonuc,adim,sure_s,bellek_MiB,merdiven_basamagi
  sonuc/degerlendirme.csv  sonuc/datalog_uyum.csv  sonuc/izler.csv  sonuc/varyant_ozeti.csv
  sonuc/metrikler.txt      sonuc/calistir_log.txt  sonuc/uyarilar.txt (empty)  sonuc/sha256.txt
  sonuc/ham/               230 × (.txt full Tamarin output, including the text trace; .meta rc/time/memory)
  sonuc/json/              196 × --output-json (traces found)
```

**Reproduction** (Git Bash, Docker running):
```
bash models/tamarin/betik/calistir.sh        # all variants, ~10 min (230 containers)
bash models/tamarin/betik/calistir.sh R3     # a single rule only
```

**Integrity:**
- `sonuc/sha256.txt` contains the SHA-256 digests of the model, Datalog and script files used in the run.
- Re-checked with `sha256sum -c`: 15/15 OK.

**Docker:**
- Only the containers of this step, named `pq-a04-*` and started with `--rm`, were used.
- No other image or container was touched. Docker was left running.

---

## 12. Step 5A — R6 time window, R7 monotone expectation, M-g/M-h, ProVerif second opinion

- **Date:** 24.09.2026.
- **Task:** the maintainers' Step 5A brief. Bases:
  - the R6/R7 proposals in §10,
  - the literature decisions L-D1 (M-g, M-h, first contact) and L-D3 (exposure window of the key),
  - new rule: well-formedness warnings must be 0.
- **Evidence rule:** the numbers in this section were taken by script from these files, not copied by hand:
  - `sonuc/metrikler.txt` (Step 5A section), `sonuc/ozet.csv`, `sonuc/degerlendirme.csv`, `sonuc/izler.csv`,
  - `sonuc/proverif/metrikler.txt`, `sonuc/proverif/karsilastirma.csv`.

### 12.0 Summary

- **Scope:**
  - 4 new models: `R6_time`, `R6_h5`, `R7_monotone`, `R7_mh`.
  - 1 exploration model: `R7_mh_x`, after the pre-registration.
  - In total 41 variants and 349 lemma runs: R6 105, R6h5 46, R7 130, R7h 33, R7hx 35.
- **Pre-registration:** the expectations were written to `betik/varyantlar.tsv` **before** the run and hashed:
  - main variants: `sonuc/on_kayit_adim5a_varyantlar.sha256.txt`, 12:45:40,
  - exploration variants: `sonuc/on_kayit_adim5a_kesif.sha256.txt`, 19:28:54.
- **Expected/observed agreement: 347/349.**
  - The only deviation is in the protected variant of R7h (`P_ca_pq_alt_namebind`): G5 and G1 falsified, contrary to the expectation.
  - **Reason:** name binding looks only at the CA **name**. The root can certify the alternative classical CA with the **same name** as the legitimate CA.
  - The exploration model (R7hx) came out as expected 35/35: if CA names are unique or the issuer is bound to the CA **key**, the protection comes back (§12.5).
- **Acceptance criterion:**
  - R6, R6h5, R7: **PASSED**.
  - R7h: **FAILED** in its pre-registered form. This is not a model error but a finding (§12.5).
  - R7hx (exploration): as expected.
- **Mutation score (Step 5A): 16/16 = 100%.**
- **Well-formedness:**
  - "All wellformedness checks were successful" in 390 of the 390 raw Tamarin outputs of Step 5A, warnings 0.
  - 620/620 together with Step 4.
  - `gecersiz_wf` runs 0.
- **ProVerif 2.05 second opinion:**
  - 15 models, 20 security queries.
  - Definite result 20/20, agreement with Tamarin **20/20**, "cannot be proved" 0.
  - 15/15 in the sanity queries.
- **Resource use:**
  - Longest Tamarin run 3.58 s, highest memory 115.8 MiB.
  - All runs closed at step 1 of the ladder; none failed to close.
- **Preliminary results for the hypotheses** (details in §12.2–12.6):
  - **H2:** what is decisive is not the token lifetime but the exposure window of the key. A long-lived key can be forged in every regime.
  - **H5:** with a classical device key, single use does not prevent forgery even when applied together at the wallet and at the verifier. Only "validity window < τ" and a key per credential protect.
  - **H3:** not every component of M-f is needed **in every setup**.
    - In the online (fresh) or pinned setup, MONOTONE and SUNSET_CHECK are unnecessary.
    - Offline both are needed.
    - M-g gives a downgrade trace at first contact; M-f does not.
- **M-h:**
  - The commitment is forged after Q-day in a classical chain.
  - In a PQ chain, but without name binding or with binding to the name only, it is bypassed with an alternative classical CA.
  - It holds only with key binding.

### 12.1 Pre-registration, post-interruption check and script changes

**Pre-registration.**
- 36 rows were added to `betik/varyantlar.tsv`: R6 12, R6h5 6, R7 13, R7h 5.
- The expectations are per lemma, in a new 7th column (`lemma_beklenen`).
- Digest `a88d972e…`, time 24.09.2026 12:45:40. This time is before all Tamarin runs:
  - smoke test before 19:11,
  - batch run 19:11:34–19:26:39 (R6–R7h),
  - exploration run 19:29:00–19:31:45 (`sonuc/calistir_log.txt`).

**Post-interruption check** (the session had been interrupted):
- The digest of the file is the same as at pre-registration.
- The first 38 rows (R1–R5) are byte-identical to the Step 4 file (`b3165669…`).
- CR bytes in the file 0, `|` in the data rows 0.
- A format correction was **not needed**; the expectations were not touched.
- The output "CRLF: 81" seen in the first check was a query error: `$'\r'` is not interpreted inside double quotes. Counted by bytes, the correct value is 0.

**Exploration rows.**
- 5 rows for R7hx were added after the R7h result was seen but **before** the R7hx runs.
- Digest `5ebd5b42…`, time 19:28:54.
- The pre-registered `R7_mh.spthy` was not changed (`2077b45a…`). The exploration model is in a separate file: `R7_mh_x.spthy` (`62ba0c38…`).

**Script changes.**
- `calistir.sh`:
  - reads the 7-column table.
  - performs a well-formedness check in every lemma run; a run with a warning is recorded as `gecersiz_wf` (invalid well-formedness) and does not enter the evaluation.
- `degerlendir.py`:
  - expectation per lemma,
  - prefix-based kind classification,
  - Datalog comparison only for rules that have a `.lp` counterpart,
  - metrics per group,
  - raw output scan.
- **The Step 4 outputs were reproduced.** The only difference is one kind label: "bilgi-H3" is now "bilgi" (information). With line endings and the label normalised, `degerlendirme.csv` is byte-identical; the Step 4 metrics did not change.
- **Smoke test.** Before the batch run, 6 representative variants were run with a 120 s limit to check termination; each took 1–3 s. The official record is the batch run.

### 12.2 R6 — time window (`modeller/R6_time.spthy`; H2, L-D3)

**EN.** A classical signing key k may stay outside the minimal PQ set iff the CRQC cannot finish extracting k before the verifier stops accepting signatures under k, i.e. iff τ exceeds k's exposure window (public key visible → last acceptance). The window that matters is the key's, not the artefact's. A short-window key is protected only if all three hold:
- τ exceeds its window,
- it is bound to an identity the CRQC cannot break (PQ identity),
- the key itself is not reused beyond the window.

**Paraphrase.** A classical signing key k can stay outside the minimal PQ set only if the CRQC cannot extract k before the verifier stops accepting signatures under k. That is, τ must be longer than the exposure window of k; this window lasts from the moment the public key becomes visible until the last acceptance. What is decisive is the window of the key, not of the artefact. A key with a short window is protected only if three conditions hold together:
- τ is longer than its window,
- it is bound to an identity that the CRQC cannot break (PQ),
- the key itself is not reused beyond the window.

**Model.**
- **Scenario:** Token Status List. The long-term identity key of the status provider is pinned at the verifier.
- **Certificate and token:** the status signing key is bound by the certificate `<'stkey', S, pk(k), ep>`. The token has the form `<'status', S, c, 'valid'>`.
- **Verifier:** accepts if the window `ep` of the certificate has not closed. The windows are encoded with restrictions; there is no linear state loop.
- **Two-phase CRQC:** `CRQC_Start` requires Q-day and the observed public key; `CRQC_Done` releases the private key. τ is the time between the two.
- **Key modes:**
  - LONG: a single key,
  - ROTATED: a fresh key per window,
  - PER_TOKEN: a fresh key per token,
  - KEY_REUSE: the certificate rotates, the key does not.
- **Regimes:**
  - FAST: no restriction,
  - MEDIUM: the token key is extracted only after its window has closed,
  - SLOW: token and period keys are extracted only after their windows have closed.

  Long-lived and identity keys are not restricted in any regime.
- **Identity key:** PQ with `ID_PQ`.

**Lemma:**
```
lemma G3_status_unforgeability:
  "All S c st #j. AcceptStatus(S, c, st) @ #j ==> (Ex #i. StatusIssued(S, c, st) @ #i & #i < #j)"
```

**L-D3 grid** (G3; `ID_PQ`, no KEY_REUSE):

| Key mode \ regime | FAST | MEDIUM | SLOW |
|---|---|---|---|
| LONG (long-lived) | **F** `E_long_fast` | **F** `M_long_medium` | **F** `M_long_slow` |
| ROTATED (rotated) | **F** `M_rot_fast` | **F** `E_rot_medium` | **V** `P_rot_slow` |
| PER_TOKEN (per token) | **F** `M_tok_fast` | **V** `P_tok_medium` | **V** `E_tok_slow` |

**Additional and mutant variants:**

| Variant | Flags | G3 | M_ lemma that gives a trace |
|---|---|---|---|
| `M_rot_id` | ROTATED, SLOW (identity classical) | F | `M_identity_key` |
| `M_rot_reuse` | ROTATED, ID_PQ, SLOW, KEY_REUSE | F | `M_long_key` |
| `M_tok_id` | PER_TOKEN, MEDIUM (identity classical) | F | `M_identity_key` |

Source: `sonuc/ozet.csv`, `sonuc/varyant_ozeti.csv`.
- In every variant exactly one M_ lemma gives a trace, and it is the expected attack class. In the protected variants no M_ lemma gives a trace.
- The sanity lemmas are verified in every variant. Since `executable_after_window_end` is verified, the windows really close and the service continues.

**Condition verified by Tamarin in 12 configurations:**

G3 verified ⇔ `ID_PQ ∧ ¬KEY_REUSE ∧ ((PER_TOKEN ∧ (MEDIUM ∨ SLOW)) ∨ (ROTATED ∧ SLOW))`

**Traces** (`sonuc/izler.csv`):
- **LONG:** `Provider_Setup, Long_Key, Qday, CRQC_Start, CRQC_Done, Verify_Status`. A fresh token is produced with the extracted long-lived key. The lifetime of the token does not matter.
- **ROTATED + FAST:** the period key set up with `Epoch_Start` is extracted while its window is open.
- **Classical identity:** the trace has no `Epoch_Start` and no `Issue_Status_PerToken`. The attacker extracts the identity key and certifies its own status key; this is the chain rule of R1.
- **KEY_REUSE:** `Reused_Key, Epoch_Start_Reuse`. Even though the window closes in the certificate, the exposure window of the key stays long.

**H2 preliminary result.**
- L-D3 was confirmed in the symbolic model. What is decisive is not the lifetime of the token but the window of the signing key. A long-lived key is in the minimal set in every regime.
- The difference between rotated and per-token keys appears only when τ falls between the two window classes (MEDIUM).
- The numerical mapping is the job of ASP (estimate). Which cell is MEDIUM or SLOW will be decided by comparing the values of the CRQC timeline (fast 10 min, medium 3 days, slow 26 days) with the window lengths.

### 12.3 R6h5 — the formal form of H5 (`modeller/R6_h5.spthy`; R4 × R6)

**EN.** With a classical device (WSCD) key, one-time use enforced both in the wallet and, globally, at verifiers does not prevent CRQC-era presentation forgery. The only remaining protection is time: τ must exceed the credential's validity window, and the device key must not be reused across credentials.

**Paraphrase.** If the device key is classical, presentation forgery in the CRQC era is not prevented even if single use is applied both in the wallet and (globally) at the verifiers. The only remaining protection is time: τ must be longer than the validity window of the credential, and the device key must not be reused across credentials.

| Variant | Flags | G2 | M_ lemma that gives a trace | Meaning |
|---|---|---|---|---|
| `P_single_slow` | SINGLE_USE, SLOW | **V** | — | Window < τ: the classical device key is protected |
| `E_nosingle_slow` | SLOW | **V** | — | Protected even without single use: the window protects |
| `M_single_fast` | SINGLE_USE | **F** | `M_device_key_in_window` | **H5:** single use does not prevent forgery |
| `M_single_slow_reuse` | SINGLE_USE, SLOW, KEY_REUSE | **F** | `M_device_key_reused` | If the key is reused, the window does not protect |
| `E_nosingle_fast` | — | **F** | `M_device_key_in_window` | — |
| `E_devpq_single_fast` | DEV_PQ, SINGLE_USE | **V** | — | PQ device key |

Source: `sonuc/ozet.csv`.
- `executable_single_use_enforced` 4/4 verified: the single-use restrictions really work.
- `executable_after_expiry` 6/6 verified: the credentials expire and the service continues.

**Trace** (`M_single_fast`): `Issue, Holder_Present, Qday, CRQC_Start_Device, CRQC_Done, Verifier_Challenge, Verifier_Accept`.
- The credential and the cnf key are visible in a presentation; this is the moment of harvesting.
- The device key is extracted within the window.
- A forged KB-JWT for a fresh nonce is accepted.

**H5 preliminary result.** The pre-registered H5 prediction holds in the symbolic model: single-use batch issuance provides no protection, only the validity period limits. A device key per credential is a necessary condition. The falsification condition ("forgery prevented by single use at the verifier") did not occur: `M_single_fast` = F.

### 12.4 R7 — monotone expectation (`modeller/R7_monotone.spthy`; H3, M-f component ablation A3, M-g, L-D1/L-D2)

**EN.** A PQ-capable verifier resists downgrade and rollback of a migrating issuer's expectation iff the value it relies on at decision time is authentic, current and per entity. That means it comes from an authoritative third party over a PQ-authenticated channel and is either fresh (online) or pinned. Offline, the verifier additionally needs sticky (monotone) state and key expiry at the announced sunset. A self-declared expectation learned on first contact (TOFU, M-g) cannot protect the first contact.

**Paraphrase.** A PQ-capable verifier resists downgrade and rollback against the expectation of a migrating issuer only if the value it relies on at decision time is authentic, current and per entity. That is, the value comes from an authoritative third party over a PQ-authenticated channel and is either fresh (online) or pinned. Offline, the verifier additionally needs sticky (monotone) state and expiry of the key at the announced sunset. A self-declared expectation learned at first contact (TOFU, M-g) cannot protect the first contact.

**Model.**
- **Lifecycle:** for the migrating issuer `'none'` → `Migrate` → `'pq_required'` → `Sunset` → `'retired'`. Encoded with event order and restrictions.
- **Issuance:** classical until the sunset, PQ after Migrate; double issuance in between.
- **Old issuer:** never migrates. It keeps the classical path alive and makes the per-entity scope meaningful.
- **Verifiers (`$V`):** PQ-capable. Classical evidence can pass only through the gate of the mechanism.
- **Mechanisms:**
  - M-f: authoritative third party.
  - `MG`: M-g, self-declaration; the PQ credential carries the declaration.
- **M-f modes:**
  - `PINNED`: synchronous pinning,
  - `FRESH`: nonce-bound online query; the value is current at the moment of use (restriction `Freshness`),
  - if neither, offline signed objects: authentic but replayable.
- **Components:** `PQ_CHAN`, `PER_ENTITY`, `MONOTONE` (sticky state), `SUNSET_CHECK` (the certified lifetime of the classical key ends at the sunset).

**Lemmas:**
- **G5_migrated (Gm):** no acceptance with classical evidence only after migration; also covers first contact.
- **G5_timed (Gt):** the timed form of G5; no classical acceptance after the sunset.
- **no_rollback (NR):** no classical acceptance once `pq_required` has been seen.
- **first_contact_downgrade (FCD):** for information, exists-trace. Does a verifier that has never seen the expectation accept classically after migration?

| Variant | Role | Flags | Gm | Gt | NR | FCD trace | M_ lemmas | Sanity |
|---|---|---|---|---|---|---|---|---|
| `P_mf_online` | protected | PQ_CHAN, FRESH, MONOTONE, PER_ENTITY, SUNSET_CHECK | V | V | V | no | - | 5/5 |
| `P_mf_pinned` | protected | PINNED, MONOTONE, PER_ENTITY, SUNSET_CHECK | V | V | V | no | - | 5/5 |
| `M_pq_chan` | mutant: PQ channel | FRESH, MONOTONE, PER_ENTITY, SUNSET_CHECK | F | V | V | yes | M_source_key_broken=V | 5/5 |
| `M_fresh` | mutant: freshness or pinning | PQ_CHAN, MONOTONE, PER_ENTITY, SUNSET_CHECK | F | V | V | yes | M_stale_object=V | 5/5 |
| `M_per_entity` | mutant: per-entity scope | PQ_CHAN, FRESH, MONOTONE, SUNSET_CHECK | F | V | V | yes | M_global_expectation=V | 4/5 |
| `A_online_no_monotone` | additional-ablation | PQ_CHAN, FRESH, PER_ENTITY, SUNSET_CHECK | V | V | V | no | M_rollback=F | 5/5 |
| `A_online_no_sunset` | additional-ablation | PQ_CHAN, FRESH, MONOTONE, PER_ENTITY | V | V | V | no | M_after_sunset=F | 5/5 |
| `A_pinned_min` | additional-ablation | PINNED, PER_ENTITY | V | V | V | no | M_rollback=F, M_after_sunset=F | 5/5 |
| `M_off_monotone` | mutant: monotonicity (offline) | PQ_CHAN, PER_ENTITY, SUNSET_CHECK | F | V | F | yes | M_stale_object=V, M_rollback=V | 5/5 |
| `M_off_sunset` | mutant: sunset check (offline) | PQ_CHAN, MONOTONE, PER_ENTITY | F | F | V | yes | M_stale_object=V, M_after_sunset=V | 5/5 |
| `G_mg` | additional-mechanism | MG, MONOTONE, SUNSET_CHECK | F | V | V | yes | - | 5/5 |
| `G_mg_no_sunset` | additional-mechanism | MG, MONOTONE | F | F | V | yes | M_after_sunset=V | 5/5 |
| `G_mg_no_cache` | additional-mechanism | MG, SUNSET_CHECK | F | V | F | yes | M_rollback=V | 5/5 |

Source: `sonuc/ozet.csv`, `sonuc/metrikler.txt`.
- 13 of the 13 variants are the same as all pre-registered expectations.
- Sanity 4/5 in `M_per_entity`: `executable_learn` = F. This was written in advance: with a global expectation there is no learning rule. Therefore NR = V there is vacuously true.

**Findings:**
1. **Online and pinned M-f protect all three goals and the first contact.** `P_mf_online` and `P_mf_pinned`: Gm, Gt, NR = V; no FCD trace.
2. **Components needed in the online setup** (each one alone drops Gm):
   - **PQ_CHAN** (`M_pq_chan`): the source key is broken after Q-day and a fresh "none" response is forged. The trace contains `CRQC_Break_Source`.
   - **FRESH|PINNED** (`M_fresh`): an old but authentic "none" object is replayed. The trace contains no break: S1 is enough.
   - **PER_ENTITY** (`M_per_entity`): the global value "none" also opens the migrated issuer as long as an old issuer exists.
3. **Components unnecessary in the online and pinned setup:**
   - `A_online_no_monotone` and `A_online_no_sunset` V/V/V; no `M_rollback` and `M_after_sunset` traces.
   - `A_pinned_min` (PINNED and PER_ENTITY only) V/V/V.
   - Reason: if the value is current at every decision, the source's own monotone lifecycle already carries monotonicity and the sunset.
4. **Components needed in the offline setup:**
   - Offline, Gm falls structurally: stale object, first contact.
   - When MONOTONE is removed, NR falls (`M_off_monotone`).
   - When SUNSET_CHECK is removed, Gt falls (`M_off_sunset`).
5. **M-g (self-declaration, TOFU) gives Gm = F and an FCD trace in all three variants.**
   - Trace: `Migrating_Issuer_Setup, Migrate, Issue_Classical, Verify_Classical`. No Q-day and no break: the classical copy of the double issuance is accepted at first contact.
   - The cache (MONOTONE) provides NR, SUNSET_CHECK provides Gt. Neither closes the first contact.

**H3 preliminary result.**
- The part "an unauthenticated expectation does not provide G5" was shown in Step 4 (R2). The part "self-declaration does not protect the first contact" was shown here with a Tamarin trace.
- The proposition "M-f is sufficient and **every component is necessary**" turned out to be **context-dependent**. MONOTONE and SUNSET_CHECK are needed only in verification that uses an offline or stale value.
- This is the second branch of the pre-registered falsification condition ("a component turning out unnecessary → the mechanism is simplified").
- Simplified M-f proposal:
  - **core:** third party + PQ authentication + per entity + current (fresh or pinned),
  - **offline add-on:** monotone verifier state + key expiry at the sunset.
- These unnecessity results were not interpreted after the fact: the V expectations of the `A_*` rows were written in the pre-registration.

### 12.5 R7h — M-h certificate commitment (`modeller/R7_mh.spthy`) and exploration R7hx (`modeller/R7_mh_x.spthy`)

**EN.** A PQ commitment carried inside the issuer certificate protects the committed issuer only as far as the certification path does. It also requires the verifier to bind the issuer to its CA's **key**. If the same CA name can also be certified with a classical key, binding to the CA **name** does not exclude that key.

**Paraphrase.** A PQ commitment embedded in the issuer certificate protects the committing issuer only as far as the certificate path does. In addition, the verifier must bind the issuer to the **key** of its CA. If the same CA name can also be certified with a classical key, binding to the CA **name** does not exclude that key.

| Rule | Variant | Role | Flags | G5 | G1 | M_/X_ lemmas |
|---|---|---|---|---|---|---|
| R7h | `P_ca_pq_alt_namebind` | protected | CA_PQ, ALT_CA, NAME_BIND | F | F | — |
| R7h | `P_ca_pq_single` | protected | CA_PQ | V | V | — |
| R7h | `M_ca_classical` | mutant: commitment chain PQ | ALT_CA, NAME_BIND | F | F | M_commitment_chain_classical=V |
| R7h | `M_no_namebind` | mutant: name binding | CA_PQ, ALT_CA | F | F | M_alt_ca_bypass=V |
| R7h | `E_ca_classical_single` | additional | — | F | F | M_commitment_chain_classical=V |
| R7hx | `X_repro_prereg` | exploration | CA_PQ, ALT_CA, NAME_BIND | F | F | X_alt_ca_key_used=V |
| R7hx | `X_namebind_unique` | exploration | CA_PQ, ALT_CA, NAME_BIND, UNIQUE_CA_NAMES | V | V | X_alt_ca_key_used=F |
| R7hx | `X_namebind_samename` | exploration | CA_PQ, ALT_CA, NAME_BIND, ALT_SAME_NAME | F | F | X_alt_ca_key_used=V |
| R7hx | `X_keybind_samename` | exploration | CA_PQ, ALT_CA, KEY_BIND, ALT_SAME_NAME | V | V | X_alt_ca_key_used=F |
| R7hx | `X_keybind_distinct` | exploration | CA_PQ, ALT_CA, KEY_BIND | V | V | X_alt_ca_key_used=F |

Source: `sonuc/ozet.csv`, `sonuc/izler.csv`.

**Unexpected result and its cause.**
- V was expected for `P_ca_pq_alt_namebind` (CA_PQ, ALT_CA, NAME_BIND); G5 and G1 came out **F**.
- Trace (JSON nodes):
  - `AltCA_Setup` obtains `<'ca_cert', $CA, pk(~ka)>` from the root. This is the **same name** as the legitimate CA (`$CA`).
  - After Q-day `CRQC_Break_AltCA` runs.
  - `Verify_Classical` satisfies the binding `!IssuerOfCA($I, $CA)` and accepts a certificate without a commitment.
- In R1 of Step 4, `X_alt_ca_namebind` came out verified. There the restriction `Unique(<'ca', name>)` made CA names unique. R7_mh did not have this assumption. So the result of R1 depended on the assumption of **unique CA names**.

**Exploration (R7hx, after the pre-registration, 35/35 as expected):**
- `X_repro_prereg` reproduces the deviation in the new file.
- `X_namebind_unique`: when CA names are made unique, name binding protects (V).
- `X_namebind_samename`: if the alternative CA comes **with the same name**, name binding is bypassed (F). This is the case where, at a key change of the CA, its pre-migration classical certificate is still valid.
- `X_keybind_samename` and `X_keybind_distinct`: when the issuer is bound to the **public key** of the CA, the protection holds in both cases (V).

**Answer to the question in the brief** ("commitment in a PQ chain but an alternative classical CA + no name binding → is it bypassed with a certificate without a commitment?"):
- **Yes.** Details:
  - `M_no_namebind`: G5 = F, `M_alt_ca_bypass` = V.
  - If name binding is done **by name** and the alternative CA can carry the same name, it is bypassed even with binding (`P_ca_pq_alt_namebind`, `X_namebind_samename`).
  - If the commitment is in a classical chain, it is forged after Q-day: `M_ca_classical` and `E_ca_classical_single` F; `M_commitment_chain_classical` = V.
  - In `M_ca_classical` the first G5 trace found by Tamarin also goes through the alternative CA with the same name. The CA-breaking path was shown separately with an M_ lemma.
- **Protecting setups:** key binding, unique CA names, or a single CA (`P_ca_pq_single` V).

### 12.6 M-f / M-g / M-h comparison (L-D1, L-D2)

| Mechanism | Source of the expectation | First contact | Protection condition (Tamarin) | Offline | Where it fails (trace) |
|---|---|---|---|---|---|
| **M-f** | Authoritative third party (TL/LoTE) | **Protected** (no FCD trace; `P_mf_online`, `P_mf_pinned`) | PQ channel + per entity + current (fresh or pinned) | Gt and NR protected with monotonicity and key expiry at the sunset; Gm needs pinning | Classical channel (`M_pq_chan`), stale object (`M_fresh`), global expectation (`M_per_entity`) |
| **M-g** | Self-declaration: the issuer's own PQ credential (TOFU) | **Not protected** (FCD trace; 3/3 variants) | Cache (MONOTONE) only for entities already seen; SUNSET_CHECK for after the sunset | The cache stays at the verifier; first contact open | Acceptance of the classical copy at first contact; no Q-day needed (`G_mg`) |
| **M-h** | Commitment embedded in the certificate (CA-signed) | Protected, **but only** if the path is PQ and the issuer is bound **by key** | CA PQ + (key binding or unique CA name or a single CA) | The commitment comes with every presentation | Classical CA (`M_ca_classical`); no name binding (`M_no_namebind`); classical CA with the same name (`P_ca_pq_alt_namebind`, `X_namebind_samename`) |

**Interpretation** [Y]:
- The distinguishing property of M-f listed in L-D2 (it protects at first contact too) was shown in Tamarin.
- M-h closes the first-contact gap of M-g, but moves the burden to the certificate path and to key binding.
- The bypass of M-h with a classical CA of the same name adds a concrete trace to the candidate "bypass of M-h via an alternative path" listed in L-D4. However, X_alt_ca itself is not new (L-D7).

### 12.7 Mutation score (Step 5A)

**Kill criterion** (`betik/degerlendir.py`, generalised): a mutant counts as killed if these two conditions hold together:
- all security lemmas expected F are falsified,
- all `M_` lemmas expected V are verified.

This also verifies that the trace goes through the path opened by the removed protection.

| Rule | Mutant | Removed protection (from which protected variant) | Result |
|---|---|---|---|
| R6 | `M_long_medium` | short key window (`P_tok_medium`) | KILLED |
| R6 | `M_long_slow` | short key window (`P_rot_slow`) | KILLED |
| R6 | `M_rot_fast` | τ longer than the window (`P_rot_slow`) | KILLED |
| R6 | `M_tok_fast` | τ longer than the window (`P_tok_medium`) | KILLED |
| R6 | `M_rot_id` | PQ identity binding (`P_rot_slow`) | KILLED |
| R6 | `M_rot_reuse` | no reuse of the key (`P_rot_slow`) | KILLED |
| R6 | `M_tok_id` | PQ identity binding (`P_tok_medium`) | KILLED |
| R6h5 | `M_single_fast` | validity window shorter than τ (`P_single_slow`) | KILLED |
| R6h5 | `M_single_slow_reuse` | device key per credential (`P_single_slow`) | KILLED |
| R7 | `M_pq_chan` | PQ channel (`P_mf_online`) | KILLED |
| R7 | `M_fresh` | freshness or pinning (`P_mf_online`) | KILLED |
| R7 | `M_per_entity` | per-entity scope (`P_mf_online`) | KILLED |
| R7 | `M_off_monotone` | monotonicity, offline (`M_fresh`) | KILLED |
| R7 | `M_off_sunset` | sunset check, offline (`M_fresh`) | KILLED |
| R7h | `M_ca_classical` | commitment chain being PQ (`P_ca_pq_alt_namebind`) | KILLED |
| R7h | `M_no_namebind` | name binding (`P_ca_pq_alt_namebind`) | KILLED |

**Score: 16/16 = 100%** (`sonuc/metrikler.txt`). 27/27 together with Step 4.

**Not in the score:**
- Ablation variants (`A_*`): the pre-registration predicted that the removed component is **not needed** in this setup; their giving no trace is the expected result.
- The M-g variants (`G_*`) are a separate mechanism.
- Exploration variants (R7hx).

### 12.8 Sanity lemmas and well-formedness evidence

**Sanity lemmas.** In Step 5A, 178 of the 178 sanity lemma runs came out as expected; 177 verified, 1 F. That F was predicted in the pre-registration: `executable_learn` in `M_per_entity` (`sonuc/degerlendirme.csv`).

| Lemma | Verified / runs | What it shows |
|---|---|---|
| `executable` | 41/41 | The honest flow is reachable in every variant |
| `executable_post_qday` | 28/28 | Honest acceptance exists after Q-day too; the protected verdicts are not vacuous |
| `attack_needs_crqc` | 28/28 | Every violation comes after a CRQC break (R6, R6h5, R7h, R7hx) |
| `executable_after_window_end` | 9/9 | In R6 the windows really close and the service continues |
| `executable_after_expiry` | 6/6 | In R6h5 the credentials expire and the service continues |
| `executable_single_use_enforced` | 4/4 | The single-use restrictions really work |
| `executable_legacy` | 23/23 | The classical path of the old issuer is alive (R7, R7h, R7hx) |
| `executable_pre_migration` | 13/13 | In R7 the expectation gate is open before migration |
| `executable_lifecycle` | 13/13 | Migrate and Sunset are reachable; PQ acceptance after the sunset exists |
| `executable_learn` | 12/13 | The verifier can learn `pq_required`. The only exception is `M_per_entity` with a global expectation; written in advance |

**Well-formedness** (rule: a run with a warning is invalid):
- Step 5A has 390 raw Tamarin outputs: 41 listing runs and 349 lemma runs.
- All 390 contain the line "All wellformedness checks were successful"; none contains "wellformedness check failed".
- `calistir.sh` checked it in every lemma run: `gecersiz_wf` = 0, `uyarilar.txt` empty.
- **620/620** together with Step 4. Source: `sonuc/metrikler.txt`, the lines of the well-formedness scan.

### 12.9 ProVerif 2.05 second opinion (R1–R5 subset)

**Method.**
- The 5 protected and 10 mutant variants of R1–R5 were generated from the templates `modeller/proverif/*.pvt` with `betik/pp.awk`.
- Q-day was modelled with `phase 1`: the classical keys are given to the attacker in phase 1, the honest processes run in both phases.
- **Differences from the Tamarin model:**
  - A single instance of each role. In R4 a single credential is set up at the top level; the `phase` instruction was not put inside a replicated process.
  - R3 was modelled only with the object-signature channel.
  - The expectation gate was written with an equality test `= none` instead of `<>`.
  - Key leakage does not wait for the public key to be observed. This means a stronger attacker.
- Run: `betik/proverif_calistir.sh`, 15 models, `--memory=4g`, `timeout 600`.

**Result** (`sonuc/proverif/metrikler.txt`, `karsilastirma.csv`):
- **20 of the 20** security queries gave a definite result; "cannot be proved" 0.
- Agreement with Tamarin **20/20**.
- 15/15 in the sanity (reachability) queries.
- Longest time per model 0.776 s, peak memory at most 7.9 MiB.

| Rule | Variant | Query | ProVerif raw | ProVerif verdict | Tamarin | Agreement |
|---|---|---|---|---|---|---|
| R1 | `P_all_pq` | executable | false | verified | verified | YES |
| R1 | `P_all_pq` | G1_claims_unforgeability | true | verified | verified | YES |
| R1 | `M_root` | executable | false | verified | verified | YES |
| R1 | `M_root` | G1_claims_unforgeability | false | falsified | falsified | YES |
| R1 | `M_ca` | executable | false | verified | verified | YES |
| R1 | `M_ca` | G1_claims_unforgeability | false | falsified | falsified | YES |
| R1 | `M_iss` | executable | false | verified | verified | YES |
| R1 | `M_iss` | G1_claims_unforgeability | false | falsified | falsified | YES |
| R2 | `P_expect_auth` | executable | false | verified | verified | YES |
| R2 | `P_expect_auth` | G1_claims_unforgeability | true | verified | verified | YES |
| R2 | `P_expect_auth` | G5_no_classical_acceptance | true | verified | verified | YES |
| R2 | `M_expect_unauth` | executable | false | verified | verified | YES |
| R2 | `M_expect_unauth` | G1_claims_unforgeability | false | falsified | falsified | YES |
| R2 | `M_expect_unauth` | G5_no_classical_acceptance | false | falsified | falsified | YES |
| R2 | `M_expect_absent` | executable | false | verified | verified | YES |
| R2 | `M_expect_absent` | G1_claims_unforgeability | false | falsified | falsified | YES |
| R2 | `M_expect_absent` | G5_no_classical_acceptance | false | falsified | falsified | YES |
| R3 | `P_obj_pq` | executable | false | verified | verified | YES |
| R3 | `P_obj_pq` | G1_claims_unforgeability | true | verified | verified | YES |
| R3 | `P_obj_pq` | G5_no_classical_acceptance | true | verified | verified | YES |
| R3 | `M_obj_classical` | executable | false | verified | verified | YES |
| R3 | `M_obj_classical` | G1_claims_unforgeability | false | falsified | falsified | YES |
| R3 | `M_obj_classical` | G5_no_classical_acceptance | false | falsified | falsified | YES |
| R4 | `P_dev_iss_pq` | executable | false | verified | verified | YES |
| R4 | `P_dev_iss_pq` | G2_presentation_unforgeability | true | verified | verified | YES |
| R4 | `M_dev` | executable | false | verified | verified | YES |
| R4 | `M_dev` | G2_presentation_unforgeability | false | falsified | falsified | YES |
| R4 | `M_iss` | executable | false | verified | verified | YES |
| R4 | `M_iss` | G2_presentation_unforgeability | false | falsified | falsified | YES |
| R5 | `P_pin_tlpq` | executable | false | verified | verified | YES |
| R5 | `P_pin_tlpq` | G1_claims_unforgeability | true | verified | verified | YES |
| R5 | `M_pin` | executable | false | verified | verified | YES |
| R5 | `M_pin` | G1_claims_unforgeability | false | falsified | falsified | YES |
| R5 | `M_tl` | executable | false | verified | verified | YES |
| R5 | `M_tl` | G1_claims_unforgeability | false | falsified | falsified | YES |

**Difference from the pilot** [Y]:
- In pilot B, 2 of 4 variants had given "cannot be proved".
- Here the trace was rebuilt in all mutants in which a classical key leaks.
- Possible reasons (not verified):
  - an equality test at the gate instead of an inequality,
  - separate copies of the honest processes for the two phases.
- The comparison is made only over definite results; an "unknown" would not have entered the agreement rate.

### 12.10 Limitations (Step 5A)

1. **Order-based time.**
   - τ and the windows are not numerical; the regimes were encoded by the order "is τ longer than the window class" (restrictions).
   - Which real window falls into which class is a numerical question; the job of ASP.
   - The CRQC performs a single-phase extraction per key; there is no per-window key limit k.
2. **Freshness is a restriction.** In R7 freshness was encoded as the restriction "the state does not change between the response and its use". This is the ideal form of the assumption "fresh enough". Real propagation delay was not modelled.
3. **Verifier behaviour as a restriction.** MONOTONE and SUNSET_CHECK were modelled as verifier behaviour with restrictions. In these setups `no_rollback` and `G5_timed` are easy results by definition; the informative results are the variants where the restriction is **removed**.
4. **Only PQ-capable verifiers.**
   - An old verifier without PQ support was not modelled as a separate role.
   - The timed form of G5 here is the behaviour of the PQ-capable verifier after the sunset.
5. **M-h was kept small.**
   - The validity period of the old certificate without a commitment was not modelled; a clean rotation was assumed.
   - The commitment cache (continuity period) was not modelled.
   - The TOFU form of M-h is similar to M-g and should be tested separately.
6. **The exploration was done after the pre-registration.** R7hx was designed after the R7h result was seen; its expectations were pinned with a separate digest before the run. Still, it is reported as an **exploration**; the pre-registered result is 347/349.
7. **ProVerif subset.**
   - Only the protected and mutant variants of R1–R5 were run.
   - R6/R7 were not transferred to ProVerif: phases are weak at expressing τ and windows [Y].
8. **No Datalog counterpart.** For R6/R7 no Layer 1 ↔ 2 comparison (clingo) was made; numerical windows and freshness are within the scope of the ASP model (proposal in §12.11).
9. **The limitations of Step 4 apply** (§8): symbolic cryptography, single-instance roles, honest parties.

### 12.11 Contribution to the technical gate and the next steps; recommendations

**Contribution:**
- R6/R7 and the formal form of H5: 41 variants, 349 lemmas, mutation score 16/16, well-formedness 0 warnings.
- ProVerif second opinion: 20/20 agreement on definite results.
- The unexpected result in R7h stays as the pre-registered result; the exploration isolated its cause.

**Recommendations:**
1. **For ASP (Step 3):**
   - The parameter `ad_baglama` should be defined as **key binding**. Or the uniqueness of CA names should be written as a separate assumption.
   - During a key change, the classical and PQ certificates of the same CA name can be valid together. In the "root first" analysis this case should be a separate cell.
   - For H2, `exposure(K)`, `last_accept(K)` and the window classes should be set up: long-lived / period / token.
   - The 3 variants of the status list signing key should be compared with the R6 grid.
2. **Pre-registration (maintainers):**
   - **H3:** instead of "every component of M-f is necessary", a context-sensitive form should be written. The core components (third party, PQ, per entity, current) are needed in every setup. Monotonicity and key expiry at the sunset are needed only in verification with an offline or stale value.
   - **G5:** the untimed form (R2, R3) and the timed form (R7) should be separated.
3. **Abstraction sampling** (once the ASP export is ready): the R6/R7 templates can be used directly because they are parameterised with flags. Median time per lemma 1.03 s.
4. **Step 7 (M-a…M-h):** for M-h the variants "continuity period + cache" and "validity of the old certificate" should be added. The TOFU gap of M-h should be compared with M-g.

### 12.12 Step 5A files

```
models/tamarin/
  modeller/R6_time.spthy  R6_h5.spthy  R7_monotone.spthy  R7_mh.spthy   (pre-registered)
  modeller/R7_mh_x.spthy                                                (exploration, after the pre-registration)
  modeller/proverif/R1_chain.pvt … R5_anchor.pvt                         (ProVerif templates)
  betik/varyantlar.tsv (41 new rows), calistir.sh, degerlendir.py (updated)
  betik/pp.awk, ic_kosum_pv.sh, proverif_calistir.sh, proverif_degerlendir.py, proverif_varyantlar.tsv
  sonuc/on_kayit_adim5a_varyantlar.sha256.txt, on_kayit_adim5a_kesif.sha256.txt, sha256_adim5a.txt
  sonuc/ozet.csv, degerlendirme.csv, izler.csv, varyant_ozeti.csv, metrikler.txt (Step 4 + 5A)
  sonuc/ham/R6__*, R6h5__*, R7__*, R7h__*, R7hx__* (390 files) ; sonuc/json/ (traces)
  sonuc/proverif/uretilen/*.pv, ham/*, ozet.csv, karsilastirma.csv, metrikler.txt, log.txt
```

**Reproduction** (Git Bash, Docker running):
```
for k in R6 R6h5 R7 R7h R7hx; do bash models/tamarin/betik/calistir.sh $k; done   # ≈ 18 min (15 + 3 min in this run)
bash models/tamarin/betik/proverif_calistir.sh                                       # ≈ 30 s
```
