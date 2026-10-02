# Step 1 findings and impact on the plan

> **Date:** 24.09.2026 · **Prepared by:** the corpus work · **Purpose:** input to the "end-of-Step-1 review".
>
> **Basis:**
> - `MANIFEST.csv` (51 files; `korpus_dogrula.py` → 51/51 OK)
> - `traceability/izlenebilirlik.csv` (400 rows; 400/400 quotes verified)
> - `terim_sayimi.txt`, `korpus_on_karsilastirma.txt`
>
> `Txxx` = matrix row. Labels: **[fact]** from the primary text · **[inf]** inference of the study, to be tested in Step 2. ("Version 3" is version 3 of the internal design document.)
>
> **Privacy:** all queries were anonymous; no e-mail or personal data was sent anywhere.

---

## 1. New versions and events after 23.09.2026

**Between the evening of 23.09.2026 (after Version 3 was completed) and 24.09.2026 there is no new specification version and no overlapping work.** Checklist:

| Source | Check (anonymous) | Result |
|---|---|---|
| IETF datatracker (6 drafts) | Revision + history page | No new revision. Single event: the RPC state of `draft-ietf-lamps-pq-composite-sigs-19` became "Awaiting Second editor" on 23.09.2026 (it is moving forward in the RFC Editor queue) [fact] |
| OIDF GitHub | OpenID4VP #791, HAIP #381, connect #2153 | Latest comments 12.09 (#791), 26.08 (#381) and 28.08 (#2153). No new comment after Version 3 [fact] |
| openid.net | `-1_0.html` (errata URL) compared with `-final.html` | OID4VCI and HAIP byte-identical. OID4VP differs only in one bibliography entry ([OIDF.OID4VCI] draft 16 ↔ 15); the normative text is the same. No errata version [fact] |
| ETSI deliver | TS 119 612 / 602 / 475 / 411-8 / 312 folders; TR 119 330-4 | The newest versions are in the MANIFEST. TR 119 330-4 is not in `deliver` (unpublished) [fact] |
| arXiv (anonymous API) | "post-quantum credential", "OpenID4VP", "SD-JWT", "EUDI quantum" | No overlapping work. Tangential neighbour: arXiv:2609.04566 (03/07.09.2026), trust-domain partitioning + optimisation of the cost of PQ authentication. Can be added to the §6.5 neighbour matrix as a "method neighbour" [fact + inf] |

**Facts not included in Version 3, published before 23.09, with an impact on the plan:**

1. **ETSI TS 119 312 V2.1.1 (2026-06), "Cryptographic Suites"** [fact, T035, T356–T359, T036, T037]:
   - It contains PQC normatively: ML-DSA-44/65/87, SLH-DSA, LMS/XMSS. HashML-DSA is forbidden.
   - §6.4.1: "Acceptance requires both signatures to be valid" (AND).
   - §6.4.2: protocol-level hybrid, including "multi-signature constructions in XAdES".
   - New certificates with RSA<3000 bit are forbidden after 31.12.2026; old certificates end at the latest on 31.12.2028.
   - The migration schedule is left to a document "under development".
   - TL signatures are tied directly to this document (TS 119 612 §5.7.1, T014). Reviewer C's statement "none of them has produced normative text yet" is **no longer true** for the cryptographic layer of trust services. It is still true for expectation conveyance and coexistence (§2.b).
2. **The IETF Last Call of SD-JWT VC -19 was completed on 15.09.2026** [fact, datatracker]: SECDIR "Has Issues", ARTART "Ready with Issues". IESG state "Waiting for AD Go-Ahead"; IANA "Not OK" (11.09). A -20 revision is likely [inf]. Sensitivity to version pinning is needed.
3. **ETSI EUDI profiles** (not named in Version 3) [fact]:
   - TS 119 602 V1.1.1 (2025-11): LoTE; EUDI profiles compact JAdES, ≤ 6 months (T021–T025).
   - TS 119 475 V1.2.1 (2026-03): WRPRC; JAdES B-B, `x5c` (T257–T260).
   - TS 119 411-8 V1.1.1 (2025-10): WRPAC; not short-lived (T261).
4. **EU PQC roadmap FAQ (NIS CG, 15.04.2026):** guidance on hybrid signatures is outside the scope of the roadmap (T362, T363) [fact]. This strengthens the gap argument.
5. **RFC 9864 (October 2025):** it updates RFC 7518 and 9053; OID4VP metadata relies on "fully-specified" algorithm identifiers (T142, T226, T331, T334) [fact].

---

## 2. Findings that confirm or contradict the Version 3 assumptions

### 2.a Confirmed (primary text + script)

| Version 3 claim | Result | Basis |
|---|---|---|
| "quantum" occurs 0 times in HAIP and ARF v3.0.0 | ✓ | `terim_sayimi.txt`: HAIP 0; ARF (13 files) 0; OID4VCI/OID4VP 0; the 8 occurrences of "hybrid" in ARF concern only the CTAP transport; the single "quantum" in SD-JWT VC is in example data ("Quantum Mechanics") |
| 8725bis-10: 21.08.2026; §3.1 "permitted for itself and that issuer"; PQ/hybrid does not occur | ✓ | T327–T329; term count 0; datatracker: RFC Ed Queue, Blocked (25.08) |
| composite -04 §6.2 (`x5c` composite-signed) | ✓ | T055, T056, T057 |
| RFC 9955 mutual exclusion and stripping | ✓ | T348–T353 |
| RFC 6840 §5.11 "any single valid path" | ✓ | T364, T365 |
| ECCG ACM v2 Note 50/51, AND; 52/53 in the v3 draft | ✓ | T134–T136, T138 |
| HAIP "MUST support DPoP" (issuance side) | ✓ | T374 |
| client-attestation -11 §10.5 (8 kB) | ✓ | T192; WGLC 08.09.2026 |
| OID4VCI A.3.4 "MUST NOT be re-encoded" | ✓ | T121 |
| TSL -21 and LAMPS composite -19 in the RFC Editor queue | ✓ | MANIFEST notes (datatracker, 23.09.2026) |
| SD-JWT VC -19 dated 31.08.2026 | ✓ | Document header |
| OID4VP #791 "1.2 or later"; HAIP #381 "1.2" | ✓ | GitHub API (24.09.2026) |
| LOTL snapshot | ✓ | `data/` SHA-256 matches; seq 394, issued 2026-09-10, NextUpdate 2027-03-10 (181 days), `rsa-sha512`, 43 pointers |
| The pre-corpus copies are identical to a fresh download | ✓ | `korpus_on_karsilastirma.txt`: 3 `.txt` byte-equal; the text of 3 PDFs is reproduced byte/text-identical from the fresh PDF |

### 2.b Findings that require a correction or contradict the assumptions

1. **The S0 baseline ("all links ES256/P-256, HAIP 1.0") is only partly correct normatively.** [fact: T122, T170, T196, T221, T395–T398, T123]
   - HAIP §7 makes ES256 the minimum only for these verifications: WUA/KA/jwt proof (issuer), KB-JWT and status information (verifier), signed request and metadata (wallet).
   - **The issuer's credential signature, the `x5c` chains and the TL/LoTE are not in the list.** For them: "Verifiers are assumed to determine in advance the cryptographic suites supported by the Ecosystem."
   - Proposal: S0 = "HAIP minimum + classical suites chosen out of band by the ecosystem". This out-of-band nature can also be used as the normative basis of M-d.
2. **The label "outside the specification" for scenario (d) is a wrong generalisation.** [fact: T113–T115, T120]
   - HAIP 1.0 pins SD-JWT VC **-13**. In -13 the JWS JSON serialization (and therefore a General JSON multi-issuer signature) is an **OPTIONAL** format; HAIP §6.1 "JSON serialization MAY be supported".
   - In -19, however, it is "out of scope but not forbidden".
   - OID4VCI A.3.4 requires the credential as a "string".
   - Proposal: write §7.5(d) as: "optional (MAY) in the HAIP 1.0 profile, out of scope in SD-JWT VC -19, undetermined with the OID4VCI delivery format". This moves (d) from a stress configuration to a configuration **permitted by the specification**. Its value for H3/H6 increases.
3. **A09 "wallet attestation (WUA)" is no longer a single object.** [fact: T204–T208, T399, T400]
   - The ARF v3.0.0 main text distinguishes the Key Attestation (KA) and the Wallet Instance Attestation (WIA). WIA < 24 h; KA long-lived with a revocation maintenance period. Both are presented **only to the issuer**, not to the RP. The requirement ids in Annex 2.02, however, are still "WUA_xx".
   - Consequence: there is no WUA artefact on the presentation path (G2/G4). The WUA binds the device key only at issuance.
   - Proposal: in ASP, A09a WIA and A09b KA as separate nodes with separate windows.
4. **H1 "channel substitution" is not a proposal; it already exists in the specifications and is handled inconsistently.** [fact: T309–T311, T071, T083, T086, T282, T002, T157, T307, T308]
   - Examples that already exist:
     - JWT VC Issuer Metadata: the issuer key only over HTTPS;
     - unsigned issuer metadata as the default;
     - unsigned DC API request: origin and WebPKI;
     - LOTL download channel: pinned by the OJEU digest.
   - The other side: TSL designs the status list independently of transport. 8725bis-10 removed the sentence "TLS may be sufficient" of RFC 8725.
   - Proposal: let the narrative of H1 shift from the question "under which condition can substitution happen" to "the specifications already do this substitution; in which cells is it secure". The falsification condition does not change.
5. **The statement about how current ETSI is must be updated** (see §1, item 1).
   - TS 119 312 V2.1.1 brings normative PQ and AND hybrid. It does not, however, define expectation conveyance, sunset and coexistence.
   - The gap definition should be narrowed to: "an algorithm catalogue exists, **expectation/migration semantics** do not".
   - The undetermined area between the single-`ds:Signature` rule of TS 119 612 (T016) and the "XAdES multiple signatures" hybrid of TS 119 312 (T035) is a concrete TS 119 612 amendment point for the M-f/sunset proposal.
6. **There is no final PQ JOSE path in EUDI.** [fact + inf: T133, T134, T023–T025, T345]
   - ARF OIA_03/WUA_04 makes ACM v2 mandatory. ACM v2 qualifies pure ML-DSA with "shouldn't". RFC 9964 is pure ML-DSA. JOSE composite is a draft (-04). The EUDI LoTEs are compact JAdES, i.e. a single signature.
   - Consequence: scenario (a) (composite `alg`) is almost the **only** conforming path for EUDI. (b) (dual issuance), in turn, can be done with a single signature at the credential level.
   - Proposal: in the C3 control–treatment design let "treatment = composite -04" be the main arm and "pure ML-DSA" the secondary arm.
7. **Basis of the known-answer test: RFC 7583 does not cover algorithm rollover.** [fact: T373]
   - Correct basis: RFC 6781 §4.1.4 (order of adding and removing, TTL wait: T369–T372) together with RFC 6840 §5.11–5.12 (T364–T368).
   - The phrase "RFC 6781 and/or RFC 7583" in decision §7.9 should be made precise as "RFC 6781 §4.1.4 + RFC 6840 §5.11".
8. **Most windows are undefined.** [fact: traceability SUMMARY Finding 3]
   - A numerical bound exists only for the TL/LoTE (≤ 6 months), the WIA (< 24 h) and the ARF option of a ≤ 24 h short-lived credential.
   - The KB-JWT, DPoP, status list, metadata and credential `exp` windows are "acceptable/local policy".
   - The clock skew allowance is "a few minutes" (T392): the same scale as the fast τ regime.
   - The claim of H2 about "specification windows" can rest only on these three numbers; the rest must be a parameter range justified in the pre-registration.
9. **G2–G4 are policy-dependent in the ecosystem text.** [fact: T178, T228, T247, T253, T264, T254]
   - For the RP, the revocation and device-binding checks are "recommended, not mandatory".
   - When RP authentication fails, the user has a "present anyway" option.
   - Verification of the registration certificate is postponed by 24 months.
   - The Version 3 assumption "the verifier works correctly outside the tested policy" can be kept, but the **policy parameters** must be listed explicitly.
10. **In the DC API flow the replay protection of G2 also depends on the WebPKI.** [fact + inf: T227, T280]
    - `aud` = origin and `expected_origins` rely on the origin that the platform verifies with the WebPKI.
    - The WebPKI dependency in H1 is not limited to fetched artefacts; with the DC API it extends to the presentation context. A separate rule candidate in Tamarin R3.

---

## 3. Concrete impact on the next steps and proposals

### 3.1 ASP model (artefact, edge, channel, window)

- **Artefact set:** the 13 artefacts are kept; A09 is split in two (A09a WIA, A09b KA). Three **edge artefacts** outside the 13 are added:
  - Access CA CRL/OCSP (T255, T256);
  - JWT VC Issuer Metadata / JWK Set (T309);
  - the issuer's OAuth AS metadata (T188, T381).
- **Channel classes:** two labels are added to conveyed / fetched / pinned:
  - `sunan-ucundan-cekilen` (fetched from the presenter's endpoint): A12 `request_uri` (T284);
  - `yalniz-tasima` (transport only): fetched paths without an object signature (T309, T071, T282, Type Metadata without a digest).

  The formal test of H1 must distinguish these two labels.
- **Edges:** `threat-model/guven-bagimliligi.dot` can be translated directly into an ASP fact list (28 edges).
  - Status list delegation (EKU) is a separate and optional edge (T159–T161, T180).
  - "Several valid TL signers" is an OR edge (T008, T018).
- **Windows:**
  - Fixed: TL/LoTE ≤ 6 months (LOTL example 181 days); WIA < 24 h; credential ≤ 24 h option.
  - Parametric: KB-JWT `iat` window, DPoP window, status list `exp`/`ttl`, metadata `exp`, credential `exp`, clock allowance (minutes).
  - The proposed sweep ranges must be written in the pre-registration [inf].
- **Policy parameters:** in addition to P0–P4, `iptal_denetimi ∈ {var, yok}` (revocation check ∈ {yes, no}), `cihaz_bagi ∈ {var, yok}` (device binding), `rp_auth_fail_open ∈ {var, yok}`, `wrprc_dogrulama ∈ {faz0, faz1}` (WRPRC verification ∈ {phase 0, phase 1}), `sdjwtvc_surum ∈ {-13, -19}` (SD-JWT VC version).

### 3.2 Tamarin rule schemata R1–R7

| Rule | Concrete content from the corpus | Proposal |
|---|---|---|
| R1 chain | OJEU → LOTL → TL/LoTE → CA → issuer → credential; the anchor is not in `x5c` (T043); LoTE compact JAdES single signature (T023) | Do not model multiple signatures at the LoTE node; only composite `alg` |
| R2 downgrade | JWS JSON "application decision / at least one" (T314, T315); with the DC API signature verification is discretionary (T268); the wallet also accepts unsigned requests (T281); an unknown parameter is ignored (T385, T387); countermeasure `crit` (T386) | Add the sub-rules "unsigning" (M-b0) and "ignoring an unknown header" to R2 |
| R3 channel | Contrast of the `yalniz-tasima` paths (T309, T071, T282) with "object signature + channel" (TLPub_03/05: T027, T028) and "object only" (TSL T157); DC API origin (T227, T280) | Parametrise R3 with three channel types; add the origin dependency for G2 |
| R4 WSCD | `cnf` exposed in every presentation (T218, T220); single use only in the wallet, with fallback (T230, T231); the verifier performs the time check (T143) | For the H5 trace, take as fixed the fact "single use is not enforced" on the verifier side |
| R5 anchor | OJEU pinning (T001, T029); the channel certificate is also in the OJEU (T002); several TL signers = OR (T008, T018) | The cell "anchor pinned but list classically signed" is a candidate for H4 |
| R6 time window | The windows in §3.1; rejection after `exp` (T391); clock allowance (T392) | Put the boundary τ_fast ≈ clock allowance on the grid |
| R7 monotone expectation | Precedents: revocation cannot be undone (VCR_04, T176); DPoP nonce downgrade ban (T382); in DNSSEC "remove the DS first" (T371) | M-f carrier candidates: TL/LoTE service extension (TS 119 612/602), WRPRC field (TS 119 475), OpenID Federation metadata ("authoritative data takes precedence", T295) |

### 3.3 Mechanism classes M-a…M-f

- **M-a** (unauthenticated capability). Normative examples with the same semantics are added to the class:
  - the metadata `Accept` header (T072);
  - `wallet_metadata` / `request_object_signing_alg_values_supported` (T285);
  - AS metadata alg lists (T188, T381);
  - `client_metadata.vp_formats_supported` (T390).
- **M-b** (multiple signatures, one is enough): the text does not define the semantics (T273); de facto OR. **A new baseline M-b0 is proposed:** "unsigning". HAIP forces the wallet to support unsigned requests (T281); with the DC API signature verification is discretionary (T268). M-b0 may be a weaker and more widespread downgrade path than M-b [inf].
- **M-c** (multiple requests): a client-level counterpart exists in ABCA: "client MAY try … different algorithms" (T189).
- **M-d** (out of band): its normative basis is HAIP §7 "Verifiers are assumed to determine in advance…" (T123) and 8725bis §3.1 (T328).
- **M-e** (metadata, "supported"): confirmed (T079, T125). It was shown that the metadata model can express "required": `encryption_required`, `key_attestations_required` (T393, T394). A sub-variant **M-e′** ("if `*_alg_values_required` is added to the metadata") can be modelled as an ablation; since metadata is fetched and depends on TLS, it interacts with H1 [inf].
- **M-f** (proposed): the corpus constrains the choice of carrier.
  - LoTE compact JAdES, single signature (T023–T025). A LoTE can carry a PQ expectation only if it is itself composite-signed.
  - WRPRC verification is postponed by 24 months (T254). In the early phase the WRPRC carrier cannot be relied on.
  - OpenID Federation precedence (T295) is the third candidate.
  - Proposal: let the first carrier of M-f be the TL/LoTE service extension and WRPRC the secondary one; in the ablation report the "carrier" separately as a component.

### 3.4 C3 oracle clauses

Primary sentences to which the oracle can be tied clause by clause:

| Capability level | Clause (row) |
|---|---|
| L1 global allow-list | RFC 8725 §3.1 (T323); 8725bis §3.1 first sentence (T327) |
| L2 per-call allow-list | RFC 7515 §5.2 last paragraph (T316); RFC 9901 §7.1-2a and §7.3-5b (T103, T213) |
| L3 per-key/per-issuer binding | 8725bis §3.1 "permitted for itself and that issuer" (T328); alg ↔ `kid` consistency (T329); one key one alg (T324, T335); `alg` mandatory for PQ keys (T337) |
| L4 required algorithm set | There is **no** direct normative clause. Nearby bases: composite AND (T345), TS 119 312 §6.4.1 AND (T356), ACM v2 AND (T135) + expectation (G5: T048, T215) |
| Flag: unknown alg/header | RFC 7515 §4 unknown header is ignored (T385); `crit` (T386) |
| Flag: mixed/unprotected `x5c` | RFC 7515 §6 (T040); COSE unprotected bucket (T060); composite not backward compatible (T053) |
| Flag: MAC accepted | TSL (T145), ABCA (T183) |

Proposal: state the fact "no normative clause" for L4 explicitly in the pre-registration. The L4 oracle is derived from the combination "8725bis §3.1 + composite AND + definition of G5". The N-version oracle must make this derivation independently.

### 3.5 Hypotheses H1–H6

- **H1:** the narrative should be updated to "substitution that already exists" (§2.b-4). The falsification condition can stay as it is. The DC API origin dependency (G2) becomes an additional sub-cell.
- **H2:** the fixed windows rest on three numbers; the rest is parametric. The boundary "clock allowance ≈ τ_fast" should be added to the grid.
- **H3:** M-b0 should be added. A "carrier" dimension should be added to the M-f component ablation (§3.3).
- **H4:** the candidate cells became concrete with the corpus.
  - Status list delegation: different anchor, EKU only "should" (T159–T161, T180).
  - A.3.2.2: semantics undefined (T273).
  - WebPKI: JWT VC Issuer Metadata, unsigned request (T309, T282).
- **H5:** single use is enforced in the wallet and falls back (T230, T231); the verifier does not enforce it (T143, T144).
  - Additional observation [inf]: a short lifetime does not protect G1 once the long-lived issuer key has been extracted. The footnote in §8 of the threat model was added for this reason.
- **H6:** the oracle bases are in §3.4. Version pinning (-13/-19) should be written into the C3 inclusion criteria.

### 3.6 Documents proposed for addition to the corpus (before Step 2)

- **ETSI TS 119 182-1 (JAdES):** signature profile of the LoTE and the WRPRC; compact/single-signature details.
- **ETSI TS 119 472-2/-3:** OID4VP/OID4VCI EUDI profiles; ARF refers to them.
- **ETSI EN 319 411-1:** CRL/OCSP windows and the 24-hour revocation rule.
- **OpenID Federation 1.0:** M-f carrier candidate.
- **RFC 5280** (path validation) and **RFC 9101** (JAR): details for R1 and R2.
- All are open access. ISO/IEC 18013-5 is paid and out of scope.
