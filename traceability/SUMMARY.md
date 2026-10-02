# Traceability matrix — summary (Step 1)

> **Date:** 24.09.2026 · **Prepared by:** the corpus work (Step 1)
> **Input:** `spec-corpus/MANIFEST.csv` (51 files, SHA-256 pinned) · **Matrix:** `izlenebilirlik.csv`
> **Verification:** `alinti_dogrula.py` → `alinti_dogrulama.txt`: **395/395** quotes found verbatim in the text (391 with whitespace collapsing only, 4 additionally with joining of hyphens at line ends; none exceeds the 300-character limit).
> **Numbers:** `ozet_tablolari.py` → `kapsama_tablolari.md` (all numbers in this file come from there).
> **Builder:** `matris_olustur.py` (the rows were written by hand from the primary texts; the script only assigns ids and writes the CSV).
>
> (This summary was written at 395 rows; the matrix was later extended to 400 rows from 39 documents and the quote check gives 400/400, see `README.md`.)

## 1. Scope and method

- **395 rows**, **39 documents** occur in the matrix. **All 13** of the 13 artefacts are covered by at least 7 rows. General JOSE/COSE, hybrid and known-answer (DNSSEC) rules that cannot be tied to an artefact are under "general" (79 rows).
- Selection criterion: normative sentences (MUST/SHALL/SHOULD/MAY…) about algorithm selection/negotiation, trust chain, expectation conveyance, key binding, freshness/validity/caching, multi-signature and downgrade, or informative sentences needed to interpret these rules. No target number of rows was pursued.
- Rows with "anahtar_sozcuk = bilgi" are sentences that are not normative but directly affect the threat model (NOTE, rationale, assumption). Distribution of the dominant keyword: MUST 129 · informative/other 124 · SHALL 47 · SHOULD 30 · MUST NOT 25 · MAY 10 · RECOMMENDED 8 · OPTIONAL 8 · REQUIRED 6 · SHALL NOT 3 (`kapsama_tablolari.md` T3).
- Every row was tied to a **single** artefact; cases that concern several artefacts are written in the `not` column. The `kanal` column classifies what the sentence says about the channel of the artefact ("belirsiz", undetermined, in general rows).

### T1. Artefact × document group (number of rows; source `kapsama_tablolari.md`)

| Artefact | OIDF | IETF-OAuth | IETF-JOSE | IETF-COSE | IETF-PQUIP | IETF-LAMPS | ARF | ETSI | AB-rehber | BCT | Akademik | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A01 LOTL | · | · | · | · | 1 | · | · | 5 | 1 | · | · | 7 |
| A02 TL/LoTE | 2 | · | · | · | · | · | 6 | 21 | · | · | · | 29 |
| A03 CA (x5c chain) | 3 | · | 4 | 3 | · | 5 | 1 | 1 | · | · | · | 17 |
| A04 issuer certificate | 4 | 5 | 2 | 2 | · | · | 1 | 1 | · | · | 1 | 16 |
| A05 signed issuer metadata | 19 | · | · | · | · | · | 1 | · | · | · | · | 20 |
| A06 Type Metadata | · | 11 | · | · | · | · | · | · | · | · | · | 11 |
| A07 credential (SD-JWT VC) | 7 | 18 | 1 | · | · | · | 5 | · | · | · | · | 31 |
| A08 status list token | 4 | 25 | · | · | · | · | 6 | 1 | · | · | · | 36 |
| A09 wallet attestation (WUA: WIA/KA) | 11 | 21 | · | · | · | · | 7 | · | · | · | · | 39 |
| A10 WSCD key and KB-JWT | 18 | 9 | · | · | · | · | 4 | · | · | · | · | 31 |
| A11 RP access/registration certificate | 10 | · | · | · | · | · | 14 | 5 | · | · | · | 29 |
| A12 OID4VP request object | 35 | · | · | · | · | · | 1 | · | · | · | · | 36 |
| A13 transport (TLS/WebPKI) | 5 | 5 | 3 | · | · | · | · | · | · | · | 1 | 14 |
| general | 11 | 7 | 25 | 5 | 7 | · | · | 4 | 10 | 10 | · | 79 |
| **Total** | 129 | 101 | 35 | 10 | 8 | 5 | 46 | 38 | 11 | 10 | 2 | 395 |

(Group names: AB-rehber = EU guidance, BCT = known-answer-test sources, Akademik = academic.)

Cells with weak coverage (deliberate): only ETSI defines A01 LOTL (the OIDF has no LOTL). A06 Type Metadata is defined only in SD-JWT VC. No separate TLS specification was taken into the corpus for A13; there are only the places where the OID4VC/JOSE texts rely on TLS.

## 2. Main findings

### Finding 1 — There is no normative channel that carries an algorithm **expectation** ("required")

Nowhere in the corpus is there an authenticated, per-entity expectation field in the sense of "this entity signs with **this** algorithm (or these); do not accept anything else". The existing channels fall into four classes:

| Class | Where | Semantics | Rows |
|---|---|---|---|
| (i) Capability declaration ("supported/uses") | OID4VCI issuer metadata; OID4VP wallet/verifier metadata; ABCA and DPoP AS metadata; HAIP §7-8 | "supported"/"uses"; the only enforcing rule is that the issuer applies the proof set that **it itself** publishes (T236) | T079, T081, T142, T226, T285, T389, T390, T188, T381, T125, T126 |
| (ii) Local/out-of-band policy | 8725bis §3.1 ("permitted for itself and that issuer"); SD-JWT VC §2.5 ("permitted … according to policy"); ABCA/DPoP "acceptable per local policy"; HAIP §7 "Verifiers are assumed to determine in advance…" | There is an obligation, **the transport channel is undefined** | T328, T046, T048, T184, T378, T123 |
| (iii) Ecosystem-level allow-list | ARF OIA_03/WUA_04 → ECCG ACM v2; HAIP §7 ES256 minimum | Not per entity; ACM v2 recommends ML-DSA only as a hybrid | T133, T202, T122, T134 |
| (iv) List membership | TL/LoTE ServiceDigitalIdentity (a set of certificates per entity) | Several valid certificates (possibly with different algorithms) = OR; no "required/sunset" | T008, T018, T017 |

Supporting observations:
- The metadata model **can express** "required", but only for encryption (`encryption_required`, T393) and key attestation (`key_attestations_required`, T394). There is no equivalent field for the signature algorithm.
- Metadata is **unsigned** by default and protected only by TLS (T070, T071, T086). The signed version is an ecosystem choice (T083, T085); `exp` is optional (T076).
- The closest precedents are in the corpus, but none of them binds the verifier in OpenID4VC:
  - The DNSSEC DS record (an algorithm signal authenticated from above). Nevertheless validators apply "any single valid path" (T366, T364, T365).
  - The DPoP "nonce downgrade" ban: the expectation given by the server cannot be stripped (T382).
  - JOSE `crit`: the only JOSE tool that makes an expectation mandatory inside the object (T386). Its opposite is ignoring unknown headers (T385, T387).
  - In OID4VP, "data from an authoritative source prevails over the `client_metadata` in the request" (T295). A natural attachment point for M-f.
- **Conclusion (for M-e):** the difference between "supported" and "required" was verified in the primary text. HAIP §7 and the OID4VCI metadata carry a capability, not an expectation. The metadata, in turn, is a fetched artefact that relies on TLS, in the sense of H1.

### Finding 2 — Channel classification of the artefacts (with basis rows)

| Artefact | Class | Basis | Nuance (from the corpus) |
|---|---|---|---|
| A01 LOTL | **fetched**; anchor **pinned** (OJEU) | T001–T003; T004, T005 | The certificate of the download channel is also pinned by digest in the OJEU (T002). Transport authentication can rest on pinning independent of the WebPKI |
| A02 TL/LoTE | **fetched** | T008–T025, T027, T028, T030 | The LoTE anchors are in the OJEU (T029). Publication is both signed and over a "secure channel" (T027, T028) |
| A03 CA (x5c) | **conveyed** (intermediate certificates); anchor **fetched** | T038, T040, T043; T063 | The anchor is FORBIDDEN in x5c (T043, T198, T243). The anchor always comes from the TL/LoTE |
| A04 issuer certificate | **conveyed** (x5c leaf) | T039, T042, T045 | **Alternative path:** with JWT VC Issuer Metadata the key is **fetched** over HTTPS only, without an object signature (T309–T311). A channel substitution is in fact defined in the specification |
| A05 signed issuer metadata | **fetched** | T070–T087 | The unsigned form is mandatory, the signed one optional (T071). The registration certificate is carried by value inside the metadata (T088) |
| A06 Type Metadata | **fetched**; digest binding **conveyed**; cache **pinned** | T094, T095; T090; T093 | Unsigned. Integrity comes from the digest in the credential via `vct#integrity`. Without a digest the only protection is HTTPS |
| A07 credential | **conveyed** | T102–T110, T112–T121 | — |
| A08 status list | **fetched** | T145–T165 | In offline use it can be **conveyed** (T166). TSL makes not relying on transport security a design principle (T157) |
| A09 WUA (WIA/KA) | **conveyed** | T181–T208 | The AS algorithm support is in fetched metadata (T188) |
| A10 WSCD key/KB-JWT | **conveyed** | T209–T214, T216–T236 | The device public key is in the `cnf` field of the credential, exposed in every presentation (T218, T220). c_nonce fetched (T237) |
| A11 RP access/registration certificate | **conveyed** (by value) | T240–T247, T249–T252 | The anchor is fetched from the LoTE (T245). Revocation fetched via CRL/OCSP (T255). Offline CRL cache pinned (T256) |
| A12 request object | **conveyed** | T268–T274, T276–T281, T283 | In the redirect flow it is **fetched** from the `request_uri` (T284). But the source is the RP to be authenticated itself, not an authorised third party. Therefore it should not count as "fetched" in the sense of H1 |
| A13 TLS/WebPKI | server certificate **conveyed**, root store **pinned** | T302–T305; T313 | The carrier of fetched artefacts such as x5u, jku and metadata (T306, T309, T312) |

For the full row list see T2 and T2b of `kapsama_tablolari.md`.

### Finding 3 — Validity/acceptance windows and caching rules

**A numerical upper bound is defined in only two places:** ≤ 6 months for the TL/LoTE and < 24 hours for the WIA. All other windows are an "acceptable window", "local policy" or an optional `exp`.

| Artefact | Window / caching rule | Rows |
|---|---|---|
| LOTL, TL | Next update − issue ≤ **6 months**. If Next update has passed, the list is discarded. That the cache may hold an earlier issue is taken into account; checked "regularly" | T010, T009, T003, T011, T012 |
| LoTE | ≤ **6 months** in the EUDI profiles; left to the profile in the general profile; discarded once passed | T021, T020, T019 |
| Signed issuer metadata | `iat` REQUIRED, `exp` OPTIONAL → **undefined** | T075, T076 |
| Type Metadata | With a digest, cached **indefinitely**; otherwise the HTTP caching model (max-age) | T093, T094, T101 |
| Credential | `exp`/`nbf` OPTIONAL. HAIP recommends limiting the lifetime (no number). ARF has a short-lived option of ≤ **24 h** (no status list needed). The time check is at the verifier; the wallet may present an expired one. Clock skew allowance "a few minutes" | T117, T118, T116, T175, T143, T144, T391, T392 |
| Status list | `exp` RECOMMENDED, `ttl` RECOMMENDED. `exp`/`ttl` prevail over the HTTP headers. `iat` depends on local policy. The limits are left to the use case; in the end the RP decides | T149, T148, T150, T151, T153, T162, T163, T164 |
| WUA (WIA/KA) | WIA < **24 h**; the revocation maintenance period is separate and long. KA `exp` (mandatory with the jwt proof). In ABCA freshness is "local policy" | T204, T205, T207, T200, T186, T187, T182 |
| KB-JWT | `iat` "acceptable window" (**undefined**). `nonce` fresh per request. With the DC API `aud` = origin | T212, T210, T211, T222, T224, T225, T227 |
| DPoP / key proof | "acceptable window" (undefined). If a nonce was provided, a proof without nonce is rejected. The c_nonce is not cached; the issuer determines its lifetime | T380, T382, T234, T237, T238 |
| RP access certificate | If valid for longer than 24 hours it must be revocable. Short-lived certificates are not used. Revocation via CRL/OCSP; offline CRL cache | T249, T261, T255, T256 |
| RP registration certificate | Revocable if longer than 24 hours. The verification obligation starts **24 months after** the regulation | T250, T254, T089, T253 |
| Verifier Attestation JWT | `exp` REQUIRED; rejected once expired | T265 |

**Consequence for the model:** the "acceptance window" parameter of H2 can be taken from the specification as a number only for the TL/LoTE (≤6 months), the WIA (<24 h) and the ARF option of a ≤24 h short-lived credential. The windows of KB-JWT, DPoP, the status list and metadata must stay **parametric**; their value ranges must be justified in the pre-registration.

### Finding 4 — Multi-signature and OID4VP A.3.2.2: the de facto semantics is "one is enough"

- **A.3.2.2** defines only the syntax: per signature, `client_id`, `verifier_info` and the prefixed parameters in the protected header; everything else in the payload (T271, T272). **Which or how many signatures the wallet verifies is undefined** (T273).
- Each signature is for a different trust framework (T269, T270). A wallet can only verify the signature of its own framework; by its structure the semantics is **OR**. Security is determined by the **weakest** framework the wallet accepts (consistent with the M-b hypothesis).
- The general rule that fills the gap is RFC 7515 §5.2: which signatures must be valid is an "application decision", the minimum is "at least one" (T314, T315, T317).
- With the DC API even signature verification itself is at the wallet's discretion (T268). HAIP forces the wallet to support **unsigned, signed and multi-signed** requests (T281). Without a per-RP expectation, a downgrade from signed to unsigned is also open.
- Other multi-signature contexts:
  - SD-JWT General JSON: disclosures and the KB-JWT in the first signature; verification semantics undefined (T108, T109).
  - COSE_Sign: "one signature is usually enough" (T340, T341).
  - DNSSEC: "any single valid path" (T364).
  - In contrast, AND semantics is defined only by these sources: composite (within a single `alg`, T345), ECCG ACM v2 (T135) and ETSI TS 119 312 V2.1.1 §6.4.1 (T356). Even these can ensure the rejection of a stripped document only **with expectation information** (RFC 9955 mutual exclusion: T349, T350).

### Finding 5 — Undetermined, missing or contradictory clauses

1. **Cross-reference errors in HAIP 1.0.**
   - For signed metadata it writes "Section 11.2.3 in [OIDF.OID4VCI]"; in OID4VCI 1.0 the correct section is §12.2.3 (T083).
   - It writes "jwt proof type as specified in Appendix E"; correct is Appendix F.1, because Appendix E is Wallet Attestation (T395).
   - "section 3.5 of [SD-JWT VC]" is correct for -13, §2.5 in the current -19 (T042).
   - The sentence "The X.509 certificate signing the request MUST NOT be self-signed" was also copied into the credential and status list contexts (T044).
2. **Version fragmentation.**
   - SD-JWT VC: OID4VP pins -09, OID4VCI -11, HAIP -13; the current version is -19 (T131, T132, T130, T129).
   - TSL: OID4VCI pins -12, HAIP -14; the current version is -21 and in the RFC Editor queue.
   - A HAIP-conforming implementation must use -13 and -14.
3. **Scenario (d) (General JSON multi-signature) is not "outside the specification" but "undetermined".**
   - In -13 the JSON serialization is an optional format (T114); HAIP says "MAY" (T115).
   - In -19 it is out of scope but not forbidden (T113).
   - OID4VCI A.3.4 requires the credential as a "string" (T120).
   - The label in §7.5(d) of the design document should be corrected.
4. **TL signature.**
   - TS 119 612 V2.4.1 assumes a single enveloped `ds:Signature` (T016); its algorithm list contains no PQ (T017).
   - TS 119 312 V2.1.1 (2026-06), however, accepts "XAdES multiple signatures" as protocol-level hybrid (T035) and requires **both signatures** to be valid when accepting a hybrid (T356).
   - How a second (PQ) signature is processed in the TL is undefined.
5. **LoTE and PQ JOSE.**
   - The EUDI LoTE profiles are signed with **compact JAdES**. Since the compact serialization carries a single signature, a hybrid is possible only with a single composite `alg` (T023–T025).
   - JOSE composite is only a draft (-04).
   - ARF makes ACM v2 mandatory (T133). ACM v2 qualifies pure ML-DSA with "shouldn't" (T134). RFC 9964, however, defines pure ML-DSA.
   - Today **there is no ARF-conforming PQ JOSE signature with a final standard** (an inference; not normative text).
6. **Candidate contradiction in RP authentication.**
   - ARF RPA_01a says that RP authentication cannot be left to the browser or the operating system (T248).
   - HAIP, however, notes that unsigned DC API requests rely on the origin and the WebPKI, and makes the wallet accept unsigned requests as well (T282, T281).
   - OID4VP leaves signature verification to the wallet's discretion with the DC API (T268).
7. **Fail-open options.**
   - If RP authentication fails, the user may be given a "present anyway" option (T247).
   - If the registration certificate fails, the decision to continue lies with the wallet provider (T253).
   - `verifier_info` is at the wallet's discretion (T264).
   - For the verifier, the revocation check (T178) and the device binding verification (T228) are "recommended, not mandatory".
   - Consequence: G2, G3 and G4 are **policy-dependent** in the ecosystem text; the threat model must write them under the assumption "the verifier applies the policy".
8. **Tension with channel substitution.**
   - TSL makes not relying on transport security or the WebPKI a design principle (T157).
   - RFC 8725 §3.2 said that TLS could take the place of the JWT signature (T307). 8725bis-10 **removed** this sentence; only "none, if protected by other means" remains (T308).
   - Nevertheless, the JWT VC Issuer Metadata path of SD-JWT VC authenticates the key only via HTTPS (T309). HAIP also accepts unsigned metadata as the default (T083, T086).
   - H1 should be framed not as a "design proposal" but as a situation that **already exists** and is handled contradictorily across the standards.
9. **Status list delegation.** In ARF the status list anchor may differ from the issuer (T180). TSL recommends the same CA and EKU only at "should" level (T159–T161). The delegation chain is undefined in the ecosystem; this is the textual basis of the H4 candidate cell.
10. **Undefined windows.** KB-JWT (T212), DPoP (T380), ABCA (T186), status list (T162), metadata `exp` (T076), credential `exp` (T118).
11. **ARF v3.0.0 terminology.** In the main text, WUA has given way to the Key Attestation (KA) and the Wallet Instance Attestation (WIA) (T204–T207). The requirement ids in Annex 2.02 are still "WUA_xx" (T202, T208). The artefact A09 of the design document should be split in two (see `spec-corpus/FINDINGS-AND-PLAN-IMPACT.md`).
12. **Known-answer tests.**
    - RFC 7583 does **not cover** algorithm rollover (T373).
    - The basis for DNSSEC algorithm rollover is RFC 6781 §4.1.4 (T369–T372) and RFC 6840 §5.11–5.12 (T364–T368).

## 3. Limitations

- The selection of rows and the assignments of `artefakt`/`kanal`/`kategori`/`hedef` are the interpretation of a single work. No second independent coding (N-version) was made. A consistency check on a sample is recommended in Step 2.
- 4 quotes match only with the joining of hyphens at line ends (D2): splits such as "end-\n entity" and "SD-\n JWT" in the IETF text.
- mdoc (ISO/IEC 18013-5) is out of scope; it is not in the corpus because it is paid.
- ETSI TS 119 182-1 (JAdES) is not in the corpus: TS 119 602 and TS 119 475 refer to it.
- ETSI TS 119 472-2/-3 (OID4VC profiles) are not in the corpus: ARF refers to them.
- Proposed additional documents: `spec-corpus/KARAR-NOTLARI.md` (not part of this release).
