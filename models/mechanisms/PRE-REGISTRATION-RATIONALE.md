# Step 7 task 0 — Rationale of the mechanism-level expectations

- **Date:** 25.09.2026. **Written by:** the Tamarin work.
- **Status:** no mechanism run was made. The expectations are in `on_kayit_varyantlar.tsv`; this document gives the rationale and the source of every expectation.
- **Citation style:**
  - `T###`: row of the traceability matrix (`traceability/izlenebilirlik.csv`).
  - `reddy-01 §x`, `vicente-02 §x`, `sheffer-02 §x`: primary texts under `literatur/metin/`.
  - `#791`, `#2153`: OIDF GitHub discussions (archive: `../Yeni/_calisma/dogrulama_2026-09-23/c791.json`, `i2153.json`, `c2153.json`).
  - `R2`, `R3`, `R7`, `R7h`, `R7hx`, `S_online_core`: rule-level results (`models/tamarin/`). They are cited **as rationale**; rule-level expectations are not re-recorded here.
- **Category:** every expectation is one of these three:
  - **proof:** an all-traces lemma is expected verified;
  - **trace:** an all-traces lemma is expected falsified (attack trace);
  - **conditional proof:** the proof is expected under a written assumption. The assumption is written in the "assumption" line of the table.

(Translated from Turkish for this release. The original file `ON-KAYIT-GEREKCE.md`, whose hash is recorded in `SHA256-ON-KAYIT.txt`, is listed in `docs/INTEGRITY.md`. Variant names, flags and lemma names are kept as in the models.)

## 0. Shared definitions

**The three forms of G5** (PR §2D.10; `modeller/ortak_g5.spthy`, included in every model with `#include`):

| Form | Lemma | Meaning |
|---|---|---|
| G5-untimed | `G5_untimed` | An entity migrated from birth (`BornMigrated` at setup) is never accepted with classical evidence only. The static form in R2/R3 |
| G5-timed | `G5_timed`, `no_rollback` | No classical acceptance after the sunset; a verifier that has seen the expectation once does not go back |
| G5-migrated | `G5_migrated` | After migration, including first contact, no acceptance with classical evidence only |

Additional information lemma `first_contact_downgrade` (exists-trace): does a verifier that has never seen the expectation accept classically after migration (L-D1).

**Entity kinds** (in every model):
- migrated from birth (the G5-untimed setup),
- migrating (lifecycle `'none' → Migrate → 'pq_required' → Sunset → 'retired'`),
- old (never migrates; keeps the classical path alive; makes the per-entity scope meaningful).

The lifecycle is encoded by event order and restrictions (R7 method; no linear state loop).

**Attacker:** Dolev–Yao (S1) and, after Q-day, a CRQC that extracts the observed classical key (S2; single phase, no τ; the time dimension is in R6). PQ keys do not break.

**Note on "vacuous truth":** in mechanisms that do not keep an expectation state, `SeenPQReq` never arises. Therefore `no_rollback` = V is vacuously true and `executable_learn` = F is expected. In the tables this is marked "V (vac.)".

**Expectation category:**
- **trace:** a G5 or G4 violation is expected in the base setup;
- **proof:** all G5 forms are expected;
- **conditional proof:** the proof is expected under a written assumption (e.g. PQ WebPKI, an authenticated expectation at the wallet).

## 0.1 Scope economy (maintainers' decision, 25.09.2026)

The study lead's instruction: no work is done that would be academically useless or wasted effort. Therefore the expectation file has three kinds of rows:

| Role | Meaning | Run |
|---|---|---|
| to be run (`mekanizma`, `kosul`, `tasiyici`, `ablasyon`, `3b`, `3a`) | New mechanism-level result: `beklenti_kapsami` (3 × 3), carrier substitution, the two types of M-h, A.3.2.2, M-a / M-b / M-b0 / M-d / M-e / M-e′ | after the anchor and the technical gate |
| `5A-kapsandi` (covered in 5A) | Already tested with R7 in dimension 5A: authentication / PQ channel, freshness / pinning, monotonicity, per entity, sunset, self-declaration and first contact with M-g | none; the row refers to an R7 variant (anchor 3) |
| `indirgendi` (reduced) | Reduced to another row or to an R7 channel class; the justification of the reduction is in the relevant section | none |

- **The only formal argument used in the reductions (rule superset):** if one variant is obtained from another only by adding rules (with the same restrictions), its traces are a superset of the traces of the other. Therefore an all-traces lemma that is F in the smaller model and an exists-trace lemma that is V get the same verdict in the larger model. Example: `REG_PQ` removes only one breaking rule (§2.3); the `ATK_*` flags only add setup rules (§3.2).
- **Channel-class argument** (the other reductions): the result depends on the class of the channel: PQ-authenticated and current at decision time / replayable / classically authenticated / unauthenticated. Two channels of the same class get the same verdict. This is a modelling argument, not tool output; the carrier substitution rows (§4) test the same argument with runs.
- A ProVerif second opinion for the mechanisms and a trace export for the emulator are not done in this step.
- The number of rows to be run is 33: M_istek 3, M_metaveri 4, Mf_yol 17 (core 1 + 3b 9 + carrier 7), M_h 9. Amendment 8 added 10 rows (Mg_yol 6, Mf_ek 4); total 43 (§9).

## 1. Request direction: M-b0, M-a, M-b, M-c, OID4VP A.3.2.2 (task 3)

### 1.1 Model and expectations

**Model:** `modeller/M_istek.spthy`.
- **Parties:** the entity is the RP that signs the request; the verifier is the wallet. Requests are bound to the wallet's fresh nonce (wallet_nonce).
- **RP keys:** known authentically at the wallet. The access certificate chain was kept out; the path dimension is in `Mf_yol`.
- **G4 (RP authentication):** a request accepted after migration must have come from the RP.
- **Model restriction `RequestSamePhase`:** an honest request is accepted in the lifecycle phase in which it was created. Request objects are short-lived; the restriction excludes an artificial race across the migration boundary. It is not applied to forged requests.

| Variant | Flags | Category | G5 untimed / migrated / timed / NR | G4 | FCD trace | `M_downgrade_s1` / `M_forgery_crqc` |
|---|---|---|---|---|---|---|
| `MB0_taban` | MB0 | **trace** (S2) | F / F / F / V (vac.) | F | yes | F / V |
| `MB0_webpki_pq` | MB0, WEBPKI_PQ | **conditional proof** (assumption: origin verification over a PQ WebPKI) | V / V / V / V (vac.) | V | no | F / F |
| `MB0_wallet_expect` | MB0, WALLET_EXPECT | **conditional proof** (assumption: an authenticated, current per-RP expectation at the wallet) | V / V / V / V | V | no | F / F |
| `MA_taban` | MA | **trace** (S1) | F / F / F / V (vac.) | F | yes | V / V |
| `MA_wallet_expect` | MA, WALLET_EXPECT | **conditional proof** (same assumption) | V / V / V / V | V | no | F / F |
| `MB_taban` | MB | **trace** (S1) | F / F / F / V (vac.) | F | yes | V / V |
| `MB_wallet_expect` | MB, WALLET_EXPECT | **conditional proof** (same assumption) | V / V / V / V | V | no | F / F |
| `MB_key_expiry` | MB, KEY_EXPIRY | partial: timed form only | F / F / **V** / V (vac.) | F | yes | V / V |
| `MC_taban` | MC | **trace** (S1) | F / F / F / V (vac.) | F | yes | V / V |
| `A322_taban` | A322 | **trace** (S1) | F / F / F / V (vac.) | F | yes | V / V |
| `A322_wallet_expect` | A322, WALLET_EXPECT | **conditional proof** (same assumption) | V / V / V / V | V | no | F / F |

The sanity lemmas are expected V in all variants. The only exception is `executable_learn`: V only with `WALLET_EXPECT`, F in the others (no learning rule).

All expectations in the table are recorded; which of them are run is in §1.3.

### 1.2 Rationale

**Rationale:**
- **M-b0 (unsigning baseline).** Sources:
  - HAIP 5.2: "The Wallet MUST support unsigned, signed, and multi-signed requests" (T281);
  - HAIP 5.2: "unsigned requests depend on the origin information provided by the platform and the web PKI" (T282).

  A migrated RP signs with PQ, but the wallet has to accept the unsigned request. Origin verification falls back to the classical WebPKI. After Q-day the RP's TLS key is extracted and an unsigned request is produced in the RP's name: G4 and G5 violation.
  - S1 alone is not enough; origin verification is sound before Q-day. Therefore `M_downgrade_s1` = F.
  - Under `WEBPKI_PQ` the unsigned request comes with PQ transport evidence (the H1 condition). There is no classical acceptance at all; therefore no FCD trace either.
  - The formal basis is `M_expect_unauth` from Step 4.
- **M-a (capability negotiation).** #791, comment of 12.09.2026:
  > "it sends an HTTP header indicating its signature capabilities (e.g., `Accept-Signature-Algorithms: ML-DSA-65, ES256`) … The Verifier dynamically signs the JWT using the strongest mutually supported algorithm"

  The header is unauthenticated; an impersonated endpoint or an intermediary sends "ES256 only". The RP signs classically; the wallet accepts because it supports ES256. This is a downgrade without Q-day (S1). The classical basis of downgrade resistance: Bhargavan et al. 2016 (L-D4: not counted as a non-obvious result).
  - After the sunset the honest RP does not sign classically, but S2 forgery remains because the key lifetime is not checked. Therefore `G5_timed` = F.
- **M-b ("one is enough").** RFC 7515 §5.2: "it is an application decision which of the JWS Signature values must successfully validate" (T314).
  - The attacker strips the PQ signature. The single-signature classical JWS is accepted.
  - `KEY_EXPIRY` rescues only the timed form; the migrated and untimed forms keep falling to S1 stripping. This shows that a sunset check alone is not enough.
- **M-c (multiple requests).** #791: "request_pqc … A PQC wallet evaluates request_pqc first, while a legacy wallet ignores unknown URL parameters and processes request".
  - In the symbolic model the preference "PQ first if present" cannot be expressed: there are no negative premises. The attacker drops `request_pqc`; the wallet processes `request`.
  - The result is expected to have the same structure as M-b (S1).
- **A.3.2.2 (multiple client_id / trust frameworks).** Sources:
  - "The JWS JSON Serialization … allows the Verifier to use multiple Client Identifiers and corresponding key material to protect the same request" (T269);
  - "needs to authenticate in the context of those trust frameworks" (T270);
  - semantics undefined (T273: "Every object in the signatures structure contains the parameters and the signature specific to a particular Client Identifier").

  If the wallet verifies with any framework it trusts, the F1 (PQ) signature is stripped and acceptance happens with F2 (classical): the M-b structure. If a trace comes out, the normative basis is the verbatim quotation in T273.
- **Conditional proofs (`WALLET_EXPECT`).** If there is an authenticated, current, per-RP expectation at the wallet, the classical gate closes after migration. This is the request-direction counterpart of M-f (carrier: TL/LoTE or WRPRC faz1; see §4). The expectations are consistent with the pinned setup of R7 (`A_pinned_min` V/V/V); rule-level results are not re-recorded here.

### 1.3 Run status and reductions (scope economy)

**To be run:** `MB0_taban`, `MA_taban`, `MB_taban`. The rule of the row `MB_taban` is "M-b / A.3.2.2"; the G4 and G5 results of task 3 are read from this row.

| Row | Role | Target | Rationale |
|---|---|---|---|
| `MC_taban` | reduced | `MB_taban` | The two parameters of M-c (`request`, `request_pqc`) are a two-signature container split into parameters. The attacker dropping `request_pqc` has the same effect as stripping the PQ signature from a multi-signature: the wallet processes the classical request. The preference "PQ first if present" cannot be expressed in the symbolic model (no negative premises); even if it could, the preference could not distinguish the absence of the PQ parameter from the presence of an attacker. |
| `A322_taban` | reduced | `MB_taban` | The same rules in the model (`#ifdef MB \| A322`). A.3.2.2 is the normative instance of the "one is enough" class: every signature belongs to one `client_id` and trust framework (T269, T273) and the wallet verifies with any one it trusts. Since the semantics is undefined (T273), the model uses the reading "verifies with any one it trusts"; this reading is an assumption and is written as such in the report. If a trace comes out, the normative basis is the verbatim quotation of T273 (§1.2). |
| `MB0_webpki_pq` | reduced | `MEP_signed_fresh` (channel class) | The only identity basis of the unsigned request is the origin channel. If the channel is PQ-authenticated and current per request, the class on which G4 and G5 rest is the same as fresh PQ-signed metadata (the H1 condition). |
| `MB0_wallet_expect`, `MA_wallet_expect`, `MB_wallet_expect`, `A322_wallet_expect` | reduced | M-f core (`MF_cekirdek`; R7 `A_pinned_min`) | The condition is an authenticated, current per-RP expectation at the wallet; this is the request direction of the M-f core. When the condition holds, the mechanism (M-a, M-b, M-b0) contributes nothing to the result: the expectation closes the classical gate. |
| `MB_key_expiry` | covered in 5A | R7 `M_off_sunset`, `G_mg` ↔ `G_mg_no_sunset` | A sunset check rescues only the timed form; the migrated and untimed forms keep falling. R7 result: `G_mg` G5_timed = V, `G_mg_no_sunset` G5_timed = F. |

The three rows that are run have no `WALLET_EXPECT`; `no_rollback` is vacuously true and `executable_learn` = F is expected.

## 2. Issuer metadata and registration: M-d, M-e, M-e′

### 2.1 Model and expectations

**Model:** `modeller/M_metaveri.spthy`.
- **Parties:** the entity is the issuer; the verifier is the party that accepts the credential.
- **Issuer keys:** known authentically at the verifier.
- **Expectation value:** the lifecycle state comes from the channel as a value. The mechanism reads this value with its own meaning; the restrictions are `GateValue` and `LearnReq`:
  - **M-e ("supported"):** the classical gate is open if classical is among the "supported" ones. That is, open in coexistence, closed after the sunset.
  - **M-e′ and M-d ("required"):** the gate is open only before migration.
- **Credentials are long-lived.** Presenting a classical credential issued before migration after migration or after the sunset is the situation G5 tests; therefore the "same phase" restriction of the request model is **absent** here.

| Variant | Flags | Category | G5 untimed / migrated / timed / NR | G1 | FCD trace | `M_downgrade_s1` / `M_forgery_crqc` |
|---|---|---|---|---|---|---|
| `ME_taban` | ME, META_TLS | **trace** (S1: by design) | F / F / F / F | F | yes | V / V |
| `ME_signed_fresh` | ME, META_SIGNED, FRESH | channel ablation: timed form only | F / F / **V** / **V** | F | yes | V / V |
| `MEP_tls_classical` | MEP, META_TLS | **trace** (S2) | F / F / F / F | F | yes | F / V |
| `MEP_tls_pq` | MEP, META_TLS, WEBPKI_PQ | **conditional proof** (assumption: authentication of the metadata server is PQ; H1) | V / V / V / V | V | no | F / F |
| `MEP_signed_fresh` | MEP, META_SIGNED, FRESH | **conditional proof** (assumption: PQ-signed metadata current at decision time; the `iat/exp` window shorter than a state change) | V / V / V / V | V | no | F / F |
| `MEP_signed_stale` | MEP, META_SIGNED | channel ablation: no freshness | **V** / F / F / F | F | yes | V / V |
| `MD_static` | MD, MD_STATIC | **conditional proof** (assumption: the out-of-band configuration is authentic and updated at migration/sunset) | V / V / V / V | V | no | F / F |
| `MD_reg_classical` | MD | **trace** (S1 replay; S2 forgery) | F / F / F / F | F | yes | V / V |
| `MD_reg_pq` | MD, REG_PQ | channel ablation | **V** / F / F / F | F | yes | V / V |
| `MD_reg_pq_monotone` | MD, REG_PQ, MONOTONE | channel ablation | **V** / F / F / **V** | F | yes | V / V |

The sanity lemmas are expected V in all variants; `executable_learn` is V as well. In M-e learning happens only with `'retired'`.

All expectations in the table are recorded; which of them are run is in §2.3.

### 2.2 Rationale

**Rationale:**
- **M-e (`credential_signing_alg_values_supported`; T079, HAIP §7 T125).** "Supported" is not a requirement. In coexistence the issuer announces that it also supports classical; the verifier accepts classical evidence even without an attacker. Therefore G5-untimed and G5-migrated fall (S1).
  - The default channel is unsigned metadata: T071 "MUST support returning metadata in an unsigned form"; HAIP 9.3.1.1 T086 "Issuers use and Wallets support unsigned Issuer Metadata". After Q-day the TLS authentication is forged; even after the sunset "classical is supported" can be claimed. Therefore the timed form falls as well.
  - `ME_signed_fresh`: a PQ-signed and fresh "supported" list carries the sunset and rescues the timed form. The migrated and untimed forms, however, still fall because "supported ≠ required". The flaw of the mechanism comes from its meaning, not from the channel.
- **M-e′ (`*_alg_values_required`; the pattern of T393 `encryption_required`, T394 `key_attestations_required`).** "Required" can be expressed. Security depends on the channel; this is the H1 condition. Sources:
  - unsigned + classical TLS: after Q-day the response is forged. Trace (S2), S1 is not enough; a fresh query does not cross the migration boundary.
  - unsigned + PQ WebPKI, or PQ-signed + fresh (T073 "MUST establish trust in the signer"; T075 `iat`, T076 `exp`): conditional proof.
  - PQ-signed but without freshness: the pre-migration `'none'` object is replayed (S1). For an issuer migrated from birth such an object was never signed, so G5-untimed is preserved.
  - The expectations are consistent with the channel results of R7 (offline object `M_fresh`, fresh channel). Rule-level results are not re-recorded here.
- **M-d (DCR / CIMD / out of band; #2153 items 3 and 5).**
  - Source: "How can a client indicate that they only want post-quantum cryptography if the server also offers traditional cryptography? This can't be per-request since that would allow downgrade attacks. Potential solutions include DCR, CIMD and out-of-band configuration" (13.08.2026).
  - Item 5: "How can a client … registered to use a non-PQ algorithm change its configuration to use PQ algorithms?"
  - **Static out-of-band configuration** (pinned view): conditional proof. It exists before the first contact, so the first contact is protected.
  - **Configuration updated by registration messages:** if the channel is classical, it is forged after Q-day. Even if it is PQ, the update messages can be replayed; the pre-migration `'none'` registration is replayed (S1). Therefore the migrated and timed forms fall.
  - Monotonicity rescues only NR; this has the same structure as the offline result in R7.
  - The expected answer to the question "can the expectation be forged if the moment of registration goes through a classical channel?" (S3 §7.5): **yes** (`MD_reg_classical`, S2). Even with a PQ channel, rollback via an update is possible (`MD_reg_pq`, S1).

### 2.3 Run status and reductions (scope economy)

**To be run:** `ME_signed_fresh` (M-e), `MEP_signed_fresh` (M-e′, conditional proof), `MEP_tls_classical` (M-e′, fetched channel condition), `MD_reg_pq` (M-d).
- **M-e′ is not a separate model:** it is the "required" parameter of the M-e family (`GateRequired`). The pair `ME_signed_fresh` ↔ `MEP_signed_fresh` uses the same channel and differs only in meaning. This directly tests the question in the task text, "the difference from 'supported'".
- **`ME_signed_fresh` is the M-e row:** the task defines M-e as "PQ-signed issuer metadata". The unsigned TLS channel (`ME_taban`) is outside this definition.
- **`MD_reg_pq` is the M-d row**, and it contradicts the expectation in the work plan text. The plan (7.4 item 2) says "from a PQ channel → proof". The pre-registration here, however, is G5_migrated = F: even if the update messages are PQ-signed, they can be replayed, and the pre-migration `'none'` registration is replayed after migration (S1). This difference was written deliberately at pre-registration time; the run will show whether the plan or this file is right.

| Row | Role | Target | Rationale |
|---|---|---|---|
| `ME_taban` | reduced | `ME_signed_fresh` (meaning) + R7 `M_pq_chan` (channel) | The flaw "supported ≠ required" drops G5_migrated and G5_untimed even with the best channel. Unsigned classical TLS adds only the channel dimension (after Q-day G5_timed and NR fall too); this dimension was tested in 5A. |
| `MEP_tls_pq` | reduced | `MEP_signed_fresh` | Same channel class: fetched metadata that is PQ-authenticated and current per query (the H1 condition). |
| `MEP_signed_stale` | covered in 5A | R7 `M_fresh` | A PQ-signed object without freshness = the freshness dimension. R7 result: G5_migrated = F, first_contact_downgrade = V. |
| `MD_static` | covered in 5A | R7 `A_pinned_min` | Static out-of-band configuration = a pinned per-entity expectation. R7 result: G5_migrated / G5_timed / NR = V / V / V, FCD = F. |
| `MD_reg_classical` | reduced | `MD_reg_pq` (rule superset) + R7 `M_pq_chan` | `REG_PQ` removes only the rule `CRQC_Break_Registration`. The traces of `MD_reg_classical` are a superset of the traces of `MD_reg_pq`: the F verdicts in `MD_reg_pq` (G5_migrated, G5_timed, NR, G1) and the exists-trace verdicts that are V are inherited. Only G5_untimed being F comes from the channel dimension (S2). |
| `MD_reg_pq_monotone` | covered in 5A | R7 `M_off_monotone` | Monotonicity rescues only NR. R7 result: `M_fresh` NR = V, `M_off_monotone` NR = F. |

## 3. M-f (simplified; including the certificate path) and task 3b

### 3.1 Model

**Model:** `modeller/Mf_yol.spthy`. The carrier dimension is also in this file (mode flag; §4).
- **Anchors and path.** The TL/LoTE lists the anchors with an algorithm label: `!Anchor(name, pk, alg)`. The anchor is out of band: HAIP 6.1.1 "The X.509 certificate of the trust anchor MUST NOT be included in the x5c JOSE header" (T043); ARF 6.6.3.6 "uses a trust anchor of the Provider obtained from a LoTE or Trusted List" (T063).
  - The honest anchor `CAM` (PQ) certifies all issuers.
  - The path depth is 1 or 2. The basis of a path with an intermediate CA is T064: "the Provider may use an intermediate signing certificate to sign the PID or attestation".
- **Path validation carries no algorithm policy.** RFC 7515 §4.1.6 has the chain validated according to RFC 5280 (T038). OID4VP 6.1.1.2 requires only "at least one X.509 Certificate that matches one of the entries of the Trusted List" (T033). Therefore every classical anchor in the list is an attack surface after Q-day (TS 119 312 §9.4, T069: "A trust anchor shall remain secure during the whole time period…").
- **Edge class:** the algorithm of the signing key. That of the anchor comes from the TL, that of an intermediate CA from its own certificate. `EdgeAlg(V, I, c, a)` records the classes on the accepted path.
- **Attack surfaces (task 3b):**
  - `ATK_DIFF`: classical CA with a different name;
  - `ATK_SAME`: classical CA with the same name, i.e. an old key left over from a key change. The pattern is in TS 119 612 A.2: "at all times two or more scheme operator public key certificates, with shifted validity periods" (T018);
  - `ATK_ROOT`: classical root; under it the attacker sets up its own intermediate CA labelled PQ.

  In all M-f rows other than the 3b cells, the three surfaces are open together ("A").
- **The scope is applied only when the expectation is not `'none'`.** With `'none'` the verifier accepts every valid path as it does today.
- **Path-class lemmas** (acceptance criterion 2, "including the certificate path"):
  - `G5_path_untimed`, `G5_path_migrated`, `G5_path_timed`, `no_rollback_path`: the path of a credential accepted with a PQ leaf has no classical edge.
  - For the algorithm class the lemmas of `ortak_g5.spthy` apply unchanged (`AcceptClassical` = classical leaf).
  - Attribution lemma `M_weak_path_forgery` (exists-trace): acceptance of a forged credential with a PQ leaf via a path with a classical edge (scope bypass).
- **`SCOPE_KEY` idealisation:** the bound PQ key comes from the same authenticated view as the expectation (`!PinPQ`). In 3b it is used only in the authenticated core mode (FRESH + PQ_CHAN).
- **Modes run in the pre-registration:** FRESH (core, 3b), OBJ, WRPRC, FED, CRIT (§4). The other modes and modifiers (PINNED, UNAUTH, GLOBAL, SELF, LAZY, MONOTONE, SUNSET_CHECK, KEY_EXPIRY) stay in the model but are not run (§3.3, §3.4).

### 3.2 Core and task 3b

| Variant | Flags | Category | G5 untimed / migrated / timed / NR | Path: untimed / migrated / timed / NR | G1 | FCD trace | `M_downgrade_s1` / `M_forgery_crqc` / `M_weak_path_forgery` |
|---|---|---|---|---|---|---|---|
| `MF_cekirdek` | FRESH, PQ_CHAN, SCOPE_PATH, A | **proof** (model assumption `Freshness`: the response is current until the moment of use; delay is the subject of R6) | V / V / V / V | V / V / V / V | V | no | F / F / F |

**Task 3b: scope × attack** (flags FRESH, PQ_CHAN, scope, a single attack; variant name `MF_3b_<scope>_<attack>`):

| Scope \ attack | `ATK_DIFF` (classical CA with a different name) | `ATK_SAME` (classical CA with the same name) | `ATK_ROOT` (classical root + attacker's PQ intermediate) |
|---|---|---|---|
| `yol_sinifi` (path class; SCOPE_PATH) | **proof**: G1 V, path 4 × V | **proof** | **proof** |
| `anahtar` (key; SCOPE_KEY) | **proof** (G1 V). Path lemmas F: structural trace, no forgery (`M_weak_path_forgery` F) | the same | the same |
| `yaprak_alg` (leaf algorithm; SCOPE_LEAF) | **trace** (S2): G1 F, path 4 × F, `M_weak_path_forgery` V | **trace** | **trace** |

- In all nine cells the algorithm-class G5 forms are expected V, no FCD and `M_downgrade_s1` F: the expectation channel is the core. `M_forgery_crqc` is expected F in the yol_sinifi and anahtar scopes and V in the yaprak_alg scope.
- **Consistency check:** the `ATK_*` flags only add setup rules. Therefore the V verdicts in `MF_cekirdek` cover the three `yol_sinifi` cells (§0.1). The cells are still run separately, because acceptance criterion 2b requires tool output per cell; the overlap is checked separately.

**Rationale (3b):**
- **`yol_sinifi`.** sheffer-02 §3.2: "Post-quantum authentication requires signatures along the entire path … a PQC end-entity certificate paired with a classically signed intermediate does not provide this property".
  - The scope requires every edge to be PQ. A broken classical anchor cannot produce a PQ edge.
  - The anchor class comes from the TL entry, not from the name. Therefore the same name (`ATK_SAME`) and an intermediate labelled PQ (`ATK_ROOT`) do not change the result.
- **`anahtar`.** The expectation binds the issuer's PQ key. Path validation still accepts classical anchors; the attacker can re-certify the real PQ key under a broken classical CA. But the credential is still the issuer's: G1 is preserved, and the path-class lemmas fall structurally.
  - 5A R7hx: key binding holds against a CA with the same name, CA name binding does not (M-h, §6).
- **`yaprak_alg`.** The leaf label comes from a certificate that the attacker signed with the broken classical CA key; a forged leaf labelled PQ is accepted.
  - The opposite rationale is in JOSECOMP 6.2: "Because the certificate itself is protected by a composite signature, an attacker cannot forge a fake certificate to swap a public key even if the traditional algorithm is broken" (T055). If the certificate signature is classical, a key swap is possible.
  - `ATK_ROOT` is a depth-2 path (T064; the "classically signed intermediate" of sheffer-02 §3.2).

**Rationale (core).** A per-entity third-party expectation that is PQ-authenticated and current at decision time, with the yol_sinifi scope. Without the path, the same core was proven with R7 `S_online_core` (11/11, after anchor 4). Here the path and the three attack surfaces are added; the expectation is that the path does not change the G5 result.
- A current view is not provided by TS 119 612: the TL can be cached until "Next update" (T011), and the download frequency is undefined (T030). The online query is part of the M-f proposal.

### 3.3 A3 dimensions 1–6: covered in 5A (R7; anchor 3)

There is no new model or run for these dimensions. The `5A-kapsandi` rows of the expectation file refer to the R7 variants below. The results are 5A tool output (`models/tamarin/sonuc/ozet.csv`); the maintainers' rerun gave the same verdict 47/47.

| A3 dimension | Referring row | R7 variant | R7 result: G5_migrated / G5_timed / NR / FCD |
|---|---|---|---|
| 1 authentication / PQ channel | `MF_a3_kimliksiz`, `MF_a3_klasik_kanal` | `M_pq_chan` | F / V / V / V (`M_source_key_broken` V) |
| 2 freshness / pinning | `MF_a3_tazelik`, `MF_cekirdek_sabit` | `M_fresh`; `A_pinned_min`, `P_mf_pinned` | `M_fresh` F / V / V / V; `A_pinned_min` V / V / V / F |
| 3 monotonicity | `MF_cevrimdisi_monoton_yok` | `A_online_no_monotone` (online), `M_off_monotone` (offline) | V / V / V / F; F / V / **F** / V |
| 4 per entity | `MF_a3_kuresel` | `M_per_entity` | F / V / V / V (`M_global_expectation` V) |
| sunset | `MF_cevrimdisi_sunset_yok`, `MF_cevrimdisi_anahtar_suresi` | `A_online_no_sunset` (online), `M_off_sunset` (offline) | V / V / V / F; F / **F** / V / V |
| 5 third party ↔ self-declaration | `MF_a3_oz_beyan` | `G_mg`, `G_mg_no_cache` | F / V / V / V; F / V / **F** / V |
| 6 first contact | `MF_a3_ilk_temas` | `G_mg` ↔ `P_mf_online` | FCD V ↔ FCD F |
| offline add-on | `MF_cevrimdisi` | `M_fresh` | F / V / V / V |

- R7 has no G5-untimed and no certificate path. The A3 × path cross is not run (scope economy). The path dimension is tested only in the 3b and carrier rows.
- A3-7 (carrier) and A3-8 (scope) are new: §4 and §3.2.

### 3.4 Path-sensitive definition notes (no run; input to M-f-DEFINITION)

When the path is added, two definitions of R7 become narrower. The model carries these definitions as flags, but they are not run in the pre-registration; if the maintainers wish, they can be taken into the pre-registration later as separate rows. **Amendment 8 (26.09.2026):** the two definitions were taken into the pre-registration in a 2 × 2 layout with `Mf_ek.spthy` (§9.2).
1. **`MONOTONE`:** in R7 it was "no classical acceptance after `SeenPQReq`". Path-sensitive definition: "after `SeenPQReq` the `'none'` expectation is never used" (`UseNone`). Under the narrow definition a monotone verifier would accept a forged path labelled PQ but with a classical edge, using a stale `'none'` object. For the algorithm class the two definitions give the same result.
2. **Sunset:** a key-level sunset (`KEY_EXPIRY`; the schedule in TS 119 312 §8.4, T036/T037) closes only the classical leaf. After the sunset a stale `'none'` expectation still gets a path labelled PQ with a classical edge accepted. Therefore the sunset of M-f must be at expectation level (`SUNSET_CHECK`: the `'none'` expectation is not used after the sunset; the sunset moment must be announced in advance). The other option is to remove the classical anchors from the TL at the sunset.

## 4. M-f carrier dimension (A3-7)

**Substitution, not removal.** The carrier is changed, the other dimensions stay fixed (A, SCOPE_PATH; PQ_CHAN or its counterpart). The carrier is a mode flag in `Mf_yol.spthy`.

**Hypothesis:** the result depends on the channel class, not on the name of the carrier:
- fetched and current,
- conveyed or cached, replayable,
- unauthenticated.

The signing algorithm also determines the result. The expectation vectors are therefore identical in rows with the same channel class; after the run this equality is tested separately. Expected equivalence classes:
- {`MF_cekirdek`, `MF_tas_federasyon_pq`}: fetched and current, PQ;
- {`MF_tas_tl_onbellek`, `MF_tas_wrprc_faz1`, `MF_tas_federasyon_bayat`}: signed but replayable;
- {`MF_tas_wrprc_faz0`, `MF_tas_crit_baslik`}: unauthenticated or inside the protected object;
- {`MF_tas_federasyon_klasik_ara`}: fetched and current, but the signer is classical (same structure as 5A `M_pq_chan`).

| Variant | Carrier and channel class | Flags | Category | G5 untimed / migrated / timed / NR (path the same) | G1 | `M_downgrade_s1` / `M_forgery_crqc` / `M_weak_path_forgery` |
|---|---|---|---|---|---|---|
| `MF_cekirdek` (§3.2) | TL/LoTE, fetched and current | FRESH, PQ_CHAN, SCOPE_PATH, A | **proof** | V / V / V / V | V | F / F / F |
| `MF_tas_tl_onbellek` | TL/LoTE, cache (≤ Next update) | OBJ, PQ_CHAN, SCOPE_PATH, A | carrier | V / F / F / F | F | V / V / V |
| `MF_tas_wrprc_faz0` | WRPRC, conveyed, not verified (T254) | WRPRC, PQ_CHAN, SCOPE_PATH, A | **trace** (S1) | F / F / F / F | F | V / V / V |
| `MF_tas_wrprc_faz1` | WRPRC, conveyed, signed, replayable | WRPRC, WRPRC_FAZ1, PQ_CHAN, SCOPE_PATH, A | carrier | V / F / F / F | F | V / V / V |
| `MF_tas_federasyon_pq` | OpenID Federation, fetched and current, PQ intermediate | FED, FED_INT_PQ, SCOPE_PATH, A | **conditional proof** (assumption: the resolution response is bound to the query and current) | V / V / V / V | V | F / F / F |
| `MF_tas_federasyon_klasik_ara` | OpenID Federation, fetched, classical intermediate key | FED, SCOPE_PATH, A | **trace** (S2 only) | F / F / F / F | F | F / V / V |
| `MF_tas_federasyon_bayat` | OpenID Federation, `trust_chain` header or cache | FED, FED_INT_PQ, FED_STALE, SCOPE_PATH, A | carrier | V / F / F / F | F | V / V / V |
| `MF_tas_crit_baslik` | `crit` header (ablation only) | CRIT, SCOPE_PATH, A | ablation, **trace** (S1) | F / F / F / F | F | V / V / V |

- An FCD trace is expected in all carrier rows; the only exception is `MF_tas_federasyon_pq` (none). The sanity lemmas are expected V.
- **`MF_tas_wrprc_faz1_ek` reduced:** WRPRC faz1 + offline add-on. The effect of the offline add-on was tested in 5A (R7 `M_fresh`); the carrier equivalence is tested with the row `MF_tas_wrprc_faz1`.

**Rationale:**
- **TL/LoTE.** Sources:
  - signature: "Lists of trusted entities shall be signed" (T022); JAdES-B (T023–T025);
  - anchor pinned in the OJEU (T001, T029);
  - replay window "Next update" (T009/T019, ≤ 6 months T010/T021);
  - cache (T011).

  A current view or an online query is the core assumption of M-f (§3.2).
- **WRPRC.**
  - Signed (T258: "shall be signed with the digital signature of provider of the wallet-relying party registration certificates"). The signer's certificate is in the TL (T260).
  - It is carried by value in the request and in the metadata (T252, T088; for the issuer T087). So it is a conveyed artefact; the entity chooses which version to present, which means an old version can be replayed.
  - In faz0 the wallet does not verify: "only applies as of 24 months after entry into force" (T254). In this period the WRPRC is an unauthenticated field.
  - Revocation is mandatory only for validity longer than 24 hours (T250). A revocation check could provide freshness, but this was not modelled (note for the limitations table).
- **OpenID Federation** (`spec-corpus/metin/OIDFED.txt`):
  - The TA keys are distributed out of band: "The Trust Anchor's public keys are distributed … in some secure out-of-band way" (§4, line 897).
  - Subordinate statements are fetched from the fetch endpoint (§8.1, line 2407).
  - `exp` is mandatory and the statement is accepted until then (§3.1 line 646, §3.2 line 760). Therefore a cached statement can be replayed within its validity period.
  - The chain can be conveyed with the `trust_chain` JWS header: "Most signed JWTs MAY include the trust_chain JWS header parameter" (§4.3, lines 964–966). This case is `FED_STALE`.
  - If the intermediate entity key is classical, the statement is forged after Q-day: a PQ TA is not enough, the federation chain itself must also be PQ.
- **`crit` (ablation only).** RFC 7515 §4.1.11: "If any of the listed extension Header Parameters are not understood and supported by the recipient, then the JWS is invalid" (T386).
  - `crit` puts the expectation inside the protected object. The classical copy presented by the attacker does not carry the marker; with a stateless verifier NR falls too.
  - If the marker is remembered, it turns into A3-5 (self-declaration / TOFU; 5A `G_mg`).
  - Its only side effect is that a marked PQ object is rejected by old verifiers: an interoperability cost, not a security one; it is written into the limitations table.

## 5. M-g (sheffer-02): covered in 5A

There is no new model. The three rows in the expectation file refer to R7:

| Referring row | R7 variant | R7 result: G5_migrated / G5_timed / NR / FCD |
|---|---|---|
| `MG_ozbeyan` | `G_mg` (MG, MONOTONE, SUNSET_CHECK) | F / V / V / V |
| `MG_sunset_yok` | `G_mg_no_sunset` (MG, MONOTONE) | F / **F** / V / V |
| `MG_onbellek_yok` | `G_mg_no_cache` (MG, SUNSET_CHECK) | F / V / **F** / V |

- **Category:** first-contact trace (G5_migrated F, FCD V); conditional proof in later contacts (NR V). The condition is that the validity period of the cache lasts (`G_mg_no_cache` NR F).
- **Source:** sheffer-02 §1 ("A client begins enforcing the server's PQC commitment only after it has successfully connected to the legitimate server at least once"), §3.6 (cache rules), §5.1 ("behavior matches the usual trust-on-first-use limitation").

**Candidate not pre-registered (no run; for the maintainers' decision).** The chain policy of sheffer-02 is open to two readings.
- Definition in §3.1: "a PQC end-entity certificate is one that is not traditional-only: the EE signature employs post-quantum cryptography".
- Rule in §3.2: "the client MUST apply its PQC policy to every CertificateEntry … using the same criterion as in Section 3.1".

The two readings are:
- **Signature reading** (the signature on every certificate is PQ): the same as `yol_sinifi`. Once the cache is filled, the 3b attacks are closed.
- **Key reading** (the key of every certificate is "not traditional-only"): a certificate with a PQ key signed by a classical CA passes. In this case the 3b attacks pass even after the cache is filled. In addition, with such a chain the attacker can send `algorithm_validity_period = 0` and have the cache deleted (§3.6 item 2: "the client MUST clear the cached information"), and then downgrade to the classical path.

The first sentence of §3.2 indicates that the signature reading is intended, but the normative criterion refers to §3.1. This ambiguity was not tested with a run. It can be taken into the pre-registration as a 2–4 row addition with the path infrastructure in `M_h.spthy`. **Amendment 8 (26.09.2026):** the two readings were taken into the pre-registration with `Mg_yol.spthy` (§9.1).

## 6. M-h (reddy-01, vicente-02) and task 3a

### 6.1 Model

**Model:** `modeller/M_h.spthy`. The path infrastructure (anchors, `ATK_*`, depth 1–2) is the same as in Mf_yol; path validation does not change in either draft.
- **reddy type (`MH_REDDY`).** The PQCHC extension is in the PQC certificate.
  - After path validation the verifier caches the SAN and the leaf algorithm (§3.3).
  - While the cache exists, a traditional-only leaf is rejected (§3.3, "SHOULD treat the behavior as suspicious and terminate"; assumption R1: the SHOULD is applied).
  - Window, revocation and PQC→PQC change are not modelled.
- **vicente type (`MH_VICENTE`).** The classical certificate carries a digest of the future PQ key (§4.1).
  - The verifier keeps the first commitment it sees (assumption V2).
  - The successor PQ certificate is accepted only if the digest matches (assumption V1: a commitment failure is rejected).
  - Acceptance of the classical certificate does not change: the commitment is advisory.
- **Without `CA_PQ`** the honest CA is classical: task 3a (i).
- **`NAME_BIND`** (reddy only): the cache also keeps the name of the CA that signed the leaf (name binding as in R7h).
- **Lemmas:**
  - `ortak_g5` (including first contact);
  - `G1_claims_unforgeability`;
  - after learning: `G1_learned` (every acceptance), `G1_learned_pq` (acceptance with a PQ leaf; 3b criterion), `no_rollback_path`;
  - vicente only: `G1_learned_pq_genuine` (verifier that pinned the genuine commitment);
  - attribution: `M_downgrade_s1`, `M_forgery_crqc`.

### 6.2 Variants and expectations

| Variant | Flags | Role | G5 untimed / migrated / timed / NR | FCD trace | G1 | `G1_learned` | `G1_learned_pq` | `G1_learned_pq_genuine` | `no_rollback_path` | `M_downgrade_s1` / `M_forgery_crqc` |
|---|---|---|---|---|---|---|---|---|---|---|
| `MH_reddy_klasik_zincir` | MH_REDDY | 3a (i) | F / F / F / V | yes | F | F | F | — | F | V / V |
| `MH_reddy_farkli_ad` | MH_REDDY, CA_PQ, ATK_DIFF | 3b | F / F / F / V | yes | F | F | F | — | F | V / V |
| `MH_reddy_ayni_ad` | MH_REDDY, CA_PQ, ATK_SAME | 3b | F / F / F / V | yes | F | F | F | — | F | V / V |
| `MH_reddy_klasik_kok` | MH_REDDY, CA_PQ, ATK_ROOT | 3b | F / F / F / V | yes | F | F | F | — | F | V / V |
| `MH_reddy_adbag_farkli_ad` | MH_REDDY, CA_PQ, NAME_BIND, ATK_DIFF | 3a (ii) boundary | F / F / F / V | yes | F | F | F | — | F | V / V |
| `MH_vicente_klasik_zincir` | MH_VICENTE | 3a (i) | F / F / F / F | yes | F | F | F | V | F | V / V |
| `MH_vicente_farkli_ad` | MH_VICENTE, CA_PQ, ATK_DIFF | 3b | F / F / F / F | yes | F | F | F | V | F | V / V |
| `MH_vicente_ayni_ad` | MH_VICENTE, CA_PQ, ATK_SAME | 3b | F / F / F / F | yes | F | F | F | V | F | V / V |
| `MH_vicente_klasik_kok` | MH_VICENTE, CA_PQ, ATK_ROOT | 3b | F / F / F / F | yes | F | F | F | V | F | V / V |

- **Categories:**
  - In all rows the G5 forms are a **trace**: first contact is not protected. This is the drafts' own bootstrap limit (reddy §5.3; sheffer-02 §5.1).
  - reddy NR is a **proof** (with assumption R1); vicente NR is a **trace** (advisory).
  - `G1_learned_pq` is a **trace** in both types.
  - vicente `G1_learned_pq_genuine` is a **conditional proof** (V1, V2).
- The sanity lemmas are expected V; `executable_learn` is V.
- The source of `no_rollback_path` F differs by type:
  - reddy and classical chain: a forged or honest path with a classical edge;
  - vicente + `CA_PQ`: re-certification of the real PQ key under a classical CA (structural, as in the `anahtar` scope).

### 6.3 Rationale

- **reddy.** Sources:
  - §3.1: "This extension does not extend the certificate’s validity period and does not modify path validation procedures as defined in [RFC5280]."
  - §3.3 cache: "the server identity (as indicated in the certificate’s SubjectAltName), the PQC or composite algorithm identifier … associated with the end-entity certificate".
  - §3.3 rule: "If, within the effective continuity window, a relying party observes only a traditional certificate while the cached PQC/composite certificate remains unrevoked, the relying party SHOULD treat the behavior as suspicious and terminate the connection."
  - There is no rejection even if the algorithm differs: "If the operator changes from one PQC algorithm to another … the relying party MUST start a new continuity period."

  The only check is the leaf algorithm. After Q-day any classical CA key signs a certificate labelled PQC for the same SAN; the classical chain is valid under RFC 5280; the reddy check passes too. Result: `G1_learned_pq` = F.
- **vicente.** Sources:
  - §4.1: the commitment is in the classical certificate, protected by the CA signature.
  - §4.2: "When a subsequently issued certificate for the same subject presents a post-quantum key, the following verification procedure applies".
  - §4.2: "A relying party MUST NOT treat a PQCHC commitment as a reason to accept a certificate it would otherwise reject. The commitment is advisory."
  - §7: "The commitment is advisory and MUST NOT be treated as authentication of the committed post-quantum key."
  - REQ-3 (mismatch = commitment failure), REQ-4 (not applied after expiry).

  Results:
  - Classical acceptance does not change: NR = F, `G1_learned` = F.
  - Since the commitment is carried in the classical certificate, after Q-day a forged commitment can be the first commitment the verifier learns (poisoning): `G1_learned_pq` = F.
  - For a verifier that pinned the genuine commitment, PQ successors are accepted only with the honest key: `G1_learned_pq_genuine` = V.
  - §7.2 counts a re-issuance by the CA as a "CA-compromise scenario". Under a CRQC every classical CA is compromised in this sense, i.e. the draft's own threat assumption falls.
- **Name-binding boundary (`MH_reddy_adbag_farkli_ad`).** 5A R7hx: name binding holds only if CA names are unique. At mechanism level there are intermediate CAs: an attacker holding any classical CA key can issue an intermediate CA certificate that carries the name of the legitimate CA. Thereby the binding falls even against an alternative CA with a different name. The pre-registration is F. If V comes out, either the path model is wrong or the intermediate CAs are limited by a name constraint; this will be examined.
- **After the window (no run):** after reddy's "effective continuity window" and vicente's `commitmentNotAfter` (REQ-4) end, there is no protection. This follows directly from the draft text and has the same structure as 5A `G_mg_no_cache`; no separate row was opened.

**Qualifier (b) (PR §2C item 3; to be justified in the report):**
- **reddy: candidate.** Under the draft's own processing rules (§3.1 path validation unchanged; §3.3 cache SAN + algorithm), a CRQC attacker presents a forged PQC certificate from any classical CA in the trust store and goes unnoticed. Yet the purpose of the draft (§1) is to prevent MitM with a CRQC.
  - **Warning:** sheffer-02 §3.2 (co-author Reddy) says "a PQC end-entity certificate paired with a classically signed intermediate does not provide this property". The fact has been anticipated in the neighbouring literature; therefore the "not derivable" condition of (b) is debatable. The report must discuss this openly.
- **vicente: not a candidate.** The draft says explicitly that the commitment is advisory and not authentication (§7). The classical fallback is by design. The poisoning is a direct consequence of carrying the commitment in the classical certificate (3a-i).

### 6.4 Task 3a: expected answers

- **(i) Does the commitment extension protect if it is carried only in a classical chain?** → **No.**
  - reddy (`MH_reddy_klasik_zincir`): `G1_learned_pq` = F. After Q-day the classical CA key signs a certificate labelled PQC for the attacker's key; the cached algorithm matches.
  - vicente (`MH_vicente_klasik_zincir`): `G1_learned_pq` = F (the forged commitment is learned first) and NR = F (advisory). Key binding holds only at a verifier that pinned the genuine commitment (`G1_learned_pq_genuine` = V).
  - In both types the three forms of G5 are F (first contact).
- **(ii) Without name binding, can a certificate without a commitment be accepted via an alternative CA?** → **Yes.**
  - reddy (`MH_reddy_farkli_ad`): the PQC certificate of the alternative CA is accepted, with or without the PQCHC extension; reddy does not check the CA that signed the leaf.
  - vicente (`MH_vicente_farkli_ad`): the classical certificate of the alternative CA without a commitment is accepted (advisory; `G1_learned` = F). The PQ path is also open through poisoning (`G1_learned_pq` = F).
  - With name binding the answer is also yes: the attacker uses an intermediate CA that carries the name of the legitimate CA (`MH_reddy_adbag_farkli_ad`).
- **(iii) Does the per-entity scope of M-f close this path?**
  - **Yes**, with `yol_sinifi` (`MF_3b_yol_*`: G1 V, path lemmas V) and `anahtar` (`MF_3b_anahtar_*`: G1 V).
  - **No**, with `yaprak_alg` (`MF_3b_yaprak_*`: G1 F).
  - reddy's cache is in effect the yaprak_alg scope plus the first-contact gap; the matching F comes from this.

## 7. KB multi-signature sub-cell (task 3c; descriptive)

No model was written (scope economy). 3c is a descriptive sub-cell, not a new verifier hypothesis (work plan 3c). The expected answer comes from the text of RFC 9901 (`spec-corpus/metin/RFC9901.txt`):
- **§8.1:** "the digest in the sd_hash claim MUST be computed over the SD-JWT as described in Section 4.3.1 … the SD-JWT Compact Serialization part is built by concatenating the protected header, the payload, and the signature of the JWS JSON serialized SD-JWT". With several signatures in General JSON, "the signature" is singular; which one it is, is undefined.
- **§8.3:** "disclosures and kb_jwt MUST be included in the first unprotected header". In practice this points to the first signature.
- **§8.1:** "Unprotected headers other than disclosures are not covered by the digest".
- **Expected result:** the KB-JWT binds at most one signature.
  - If the bound signature is classical, the KB-JWT stays valid when the PQ signature is stripped.
  - If the bound signature is PQ, stripping is caught by an `sd_hash` mismatch.

  This is a sub-cell note for scenario (d) and H5; the content is the same as D-S3 and DB-1.
- If tool evidence is wanted, a small model (two signatures × choice of the bound signature) can be taken into the pre-registration later.

## 8. Summary table: mechanism × G5 form (pre-registration)

| Mechanism | Evidence row | G5 untimed | G5 migrated | G5 timed | NR | Expected category |
|---|---|---|---|---|---|---|
| M-b0 | `MB0_taban` | F | F | F | V (vac.) | trace (S2). Condition: PQ-authenticated origin channel (reduced, §1.3) |
| M-a | `MA_taban` | F | F | F | V (vac.) | trace (S1) |
| M-b / A.3.2.2 | `MB_taban` | F | F | F | V (vac.) | trace (S1); the A.3.2.2 reading is an assumption (T273) |
| M-c | → `MB_taban` | F | F | F | V (vac.) | trace (S1); reduction (§1.3) |
| M-d | `MD_reg_pq` | V | F | F | F | trace (S1: replay of the registration update). Static configuration conditional proof (R7 `A_pinned_min`). Pre-registration contradicting the plan text (§2.3) |
| M-e | `ME_signed_fresh` | F | F | V | V | trace (S1: supported ≠ required) |
| M-e′ | `MEP_signed_fresh` / `MEP_tls_classical` | V / F | V / F | V / F | V / F | conditional proof (PQ-authenticated fresh channel) / trace (S2, classical WebPKI) |
| M-f core (including path) | `MF_cekirdek` | V | V | V | V | proof; the path forms also V |
| M-f offline add-on | R7 `M_fresh` (5A) | — | F | V | V | 5A result |
| M-g | R7 `G_mg` (5A) | — | F | V | V | first-contact trace; conditional proof in later contacts |
| M-h reddy | `MH_reddy_*` | F | F | F | V | trace (first contact); after learning the 3b attacks pass (`G1_learned_pq` F) |
| M-h vicente | `MH_vicente_*` | F | F | F | F | trace (advisory); conditional proof for PQ successors at a verifier that pinned the genuine commitment |

## 9. ADDENDUM — Amendment 8 (26.09.2026): the two readings of the M-g chain policy and the path-sensitive M-f definitions

The maintainers took the two candidate groups of §3.4 and §5 into the pre-registration. The previous 63 rows and the previous model files did not change. To avoid touching files whose digests are to be bound to the anchor, two new model files were added: `Mg_yol.spthy` and `Mf_ek.spthy`. The new rows are in block [8] at the end of the expectation file.

### 9.1 M-g (sheffer-02) chain policy × task 3b (`modeller/Mg_yol.spthy`)

**Model:**
- The path infrastructure is the same as in `Mf_yol` and `M_h`: `CAM` (PQ), `ATK_*`, depth 1–2.
- **The commitment** is carried inside the PQ-signed credential: `m` ∈ {`'commit'`, `'zero'`, `'nocommit'`}.
  - An honest PQ credential carries `'commit'` (§3.7: "If a PQC certificate is used, the server MUST send exactly the four-octet algorithm_validity_period").
  - A classical credential carries `'nocommit'`.
- **Cache (§3.6):**
  - A policy-conforming acceptance + `'commit'` fills the cache (`SeenPQReq`).
  - A policy-conforming acceptance + `'zero'` deletes the cache (`CacheEnd`; item 2: "the client MUST clear the cached information").
  - While the cache exists there is no non-conforming acceptance (§3.2).
  - An object with the extension is not accepted with a non-conforming chain (§3.2: "including because the server sends non-empty pq_cert_available extension data").
  - Time is not modelled; the time dimension was tested in 5A (R7 `G_mg_no_cache`).
- **Readings:**
  - `MG_ANAHTAR`: the **key** of every CertificateEntry is PQ (§3.1: "not traditional-only"). The anchor is not a CertificateEntry (HAIP 6.1.1, T043), so the edge leaving the anchor is not checked.
  - `MG_IMZA`: the **signature** on every CertificateEntry is PQ and the leaf key is PQ (first sentence of §3.2: "signatures along the entire path"). This reading is the same as `yol_sinifi`.
- **New attribution lemma `M_cache_cleared`** (exists-trace): can a filled cache be deleted by the attacker.

| Variant | Reading | Attack | G5 untimed / migrated / timed / NR | FCD trace | G1 | `G1_learned` | `G1_learned_pq` | `no_rollback_path` | `M_downgrade_s1` / `M_forgery_crqc` / `M_cache_cleared` |
|---|---|---|---|---|---|---|---|---|---|
| `EK_mg_anahtar_farkli_ad`, `_ayni_ad`, `_klasik_kok` | key | DIFF / SAME / ROOT | F / F / F / **F** | yes | F | **F** | **F** | **F** | V / V / **V** |
| `EK_mg_imza_farkli_ad`, `_ayni_ad`, `_klasik_kok` | signature | DIFF / SAME / ROOT | F / F / F / V | yes | F | V | V | V | V / V / F |

**Rationale:**
- **Under both readings first contact is not protected** (§5.1: "behavior matches the usual trust-on-first-use limitation"). The three forms of G5 are F; the readings diverge only after the cache is filled.
- **Key reading.** After Q-day the attacker certifies its own PQ key under a broken classical CA (any of the three surfaces).
  - At depth 1 the single CertificateEntry is the leaf and its key is PQ; at depth 2 (`ATK_ROOT`) the key of the attacker's intermediate CA is also PQ. The policy is satisfied.
  - After the cache is filled, a forged PQ credential is accepted: `G1_learned_pq` = F.
  - `'zero'` is sent with the same chain and the cache is deleted (`M_cache_cleared` = V). Then the classical path reopens: NR = F.
  - §5.1 senses this dependency ("Cached entries are only as reliable as the authenticated channel that produced them"). §5.2, however, treats changing zero/non-zero only as DoS, not as a downgrade.
- **Signature reading.** Every certificate signature must be PQ. The single PQ anchor `CAM` does not sign the attacker's key. After the cache is filled, every acceptance is genuine (`G1_learned` = V) and the cache cannot be deleted. There are two reasons for this: the honest entity does not withdraw the commitment in this lifecycle, and the attacker cannot produce a policy-conforming chain.
- **Category:**
  - key reading: **trace** after the cache (S2);
  - signature reading: **conditional proof** after the cache (conditions: the cache lifetime lasts; the honest entity does not withdraw).
- **Why it matters:** the draft's own processing rule determines the result. The first sentence of §3.2 indicates that the signature reading is intended. But the normative criterion refers to §3.1; the phrase "not traditional-only" in §3.1 naturally reads like a property of the key (a PQ or composite key).
  - Under the key reading the protection of the draft falls against a CRQC attacker holding any classical CA key. This is a candidate for qualifier (b) of the same kind as reddy.
  - The same warning applies: the draft explicitly mentions a classically signed intermediate CA in §3.2. The report must present both readings and discuss which one fits the draft text.

### 9.2 Path-sensitive definitions of the M-f offline add-on, 2 × 2 (`modeller/Mf_ek.spthy`)

**Model:** an identical copy of the OBJ mode of `Mf_yol`: TL/LoTE cache, a PQ-signed but replayable expectation object, `SCOPE_PATH` and the three attack surfaces together. Only two axes are flagged:
- **monotonicity:**
  - `MONOTONE_DAR` (narrow; the R7 definition: no classical leaf after `'pq_required'`);
  - `MONOTONE_GENIS` (wide; after `'pq_required'` the `'none'` expectation is never used);
- **sunset:**
  - `SUNSET_ANAHTAR` (key; work plan 7.1: "expiry of the classical key at the sunset"; the TS 119 312 §8.4 schedule, T036/T037);
  - `SUNSET_BEKLENTI` (expectation; the `'none'` expectation is not used after the sunset; the sunset moment must be announced in advance).

| Variant | Monotonicity | Sunset | G5 untimed / migrated / timed / NR | Path: untimed / migrated / timed / NR | G1 | FCD trace | `M_downgrade_s1` / `M_forgery_crqc` / `M_weak_path_forgery` |
|---|---|---|---|---|---|---|---|
| `EK_mf_r7_tanimlari` | narrow | key | V / F / V / V | V / F / **F** / **F** | F | yes | V / V / V |
| `EK_mf_monoton_genis` | wide | key | V / F / V / V | V / F / **F** / V | F | yes | V / V / V |
| `EK_mf_sunset_beklenti` | narrow | expectation | V / F / V / V | V / F / V / **F** | F | yes | V / V / V |
| `EK_mf_yola_duyarli` | wide | expectation | V / F / V / V | V / F / V / V | F | yes | V / V / V |

**Prediction:**
- The algorithm-class G5 forms are the same in the four rows. This is a reproduction of the R7 result (`M_fresh`, `M_off_monotone`, `M_off_sunset`) with the path: the migrated form F at first contact, the timed form and NR V.
- The path-class forms diverge by axis: the monotonicity axis determines NR_path, the sunset axis determines timed_path.
- Only the path-sensitive combination gives the path forms the same profile as the algorithm forms.

**Rationale:**
- Narrow monotonicity closes only the classical leaf. If a verifier that has seen the cache uses a stale `'none'` object in a later session, a forged path labelled PQ but with a classical edge is accepted.
- A key-level sunset closes only the classical issuer key. After the sunset a PQ path with a classical edge is accepted with a stale `'none'`; this path does not use the classical issuer key.

**Category** (`EK_mf_yola_duyarli`):
- untimed form and NR **proof**;
- migrated form **trace** (first contact);
- timed form **conditional proof** (sunset announced in advance);
- the path forms have the same profile.

The other three rows are ablations.

**If the result confirms the prediction:** M-f-DEFINITION (task 9) uses the path-sensitive definitions. Instead of the phrase "expiry of the classical key at the sunset" in the work plan, an expectation-level sunset (or removal of the classical anchors from the TL at the sunset) is written.

### 9.3 Run and well-formedness

- 10 new run rows were added: 6 `Mg_yol`, 4 `Mf_ek`. Well-formedness 10/10 clean (warnings 0; `--derivcheck-timeout=60`). Record: the ADDENDUM block at the end of `iyi_bicimlilik_on_kayit.txt`.
- The number of rows to be run rose to 43 (33 + 10). The run is made after anchor 8 and the technical gate.
