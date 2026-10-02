# UNDETERMINED DECISIONS — Oracle B

> Reasons of the **89 rows** with `karar = indeterminate` in `karar.tsv` (12.2 % of 732 rows). Criterion (`METHOD.md` §6.3): a decision is undetermined if the clauses do not choose between acceptance and rejection at MUST/MUST NOT/REQUIRED level, or if the context needed for the decision is missing from `insa` / `dogrulama_girdileri`. SHOULD/RECOMMENDED/MAY are written only as a **direction**.
>
> **Effect on pre-registered variables: none.** None of the 159 rows of the primary (vector, arm) pairs is `indeterminate`. All rows below are secondary, MR twins or outside the mapping (PR §2G item 4: descriptive).
>
> Abbreviation: `@-13` / `@-19` = the suffix `|sdjwtvc=-13` / `|sdjwtvc=-19` in the `politika` column.
>
> (Quotations from the pre-registration are translated from Turkish; quotations from specifications are verbatim.)

| # | Reason | Rows |
|---|---|---|
| B1 | `sd_hash` binding undefined in a multi-signed SD-JWT+KB | 18 |
| B2 | JSON serialization out of scope in SD-JWT VC -19 | 26 |
| B3 | Transition of `typ` = `vc+sd-jwt` | 16 |
| B4 | Only MAY in `crit` | 6 |
| B5 | Trust anchor inside x5c | 3 |
| B6 | x5c together with a kid pointing to another key | 3 |
| B7 | Non-minimal DER (composite ECDSA component) | 3 |
| B8 | DPoP nonce/ath context not given | 6 |
| B9 | Unsigned OID4VP request, L4 (expectation of a migrated RP) | 8 |
| | **Total** | **89** |

---

## B1 — In a multi-signed SD-JWT+KB, which signature does `sd_hash` bind? (18 rows)

**Rows:** `VP05_GJ_ES256_MLDSA65_kb`, `VP07_GJ_sd_hash_ikinci_imza`, `VP05_GJ_ES256_MLDSA65_kb-SIRA-ters` — `tedavi-ML-DSA-65`; `L4`, `P2`, `P0` × `@-13`, `@-19`.

**Clauses:**
- RFC 9901 §8.1 (`RFC9901.txt:1900-1909`): "the digest in the sd_hash claim MUST be computed over the SD-JWT as described in Section 4.3.1 [...] the SD-JWT Compact Serialization part is built by concatenating the protected header, the payload, and the signature of the JWS JSON serialized SD-JWT". In General JSON there are several "protected header" and "signature" values; which one is to be used is not written.
- RFC 9901 §8.3 (`:1987-1989`): the disclosures and `kb_jwt` "MUST be included in the first unprotected header" — this singles out the first signature object but does not bind the `sd_hash` computation.
- RFC 9901 §7.3 (5g) (`:1867-1870`): the verifier MUST match `sd_hash`.
- PR §2D item 4 (`:412`): "With several signatures in the General JSON serialization, which signature `sd_hash` binds is undefined."

**Why undetermined:** the issuer layer gives acceptance in all three configurations (both signatures valid; R met under L4). The result of the KB check depends on the verifier's reading of §8.1: in VP05 `sd_hash` was built with the first signature (ES256) — a verifier reading "first signature" accepts, another reading rejects; in VP07 it was built with the second signature — the opposite; in VP05-SIRA-ters the same KB is bound to the signature that the permutation moved to position 1. Every reading is consistent with §8.1. Under `@-19` B2 applies as well.

**Note:** this is the descriptive sub-cell of the PR ("the KB binding does not protect the multi-signature set", §2D item 4); it is not a hypothesis.

## B2 — JSON-serialized credential in SD-JWT VC -19 (26 rows)

**Rows (all `@-19`):**
- `VC09_GJ_ES256_EdDSA`, `VC09_GJ_ES256_EdDSA-SIRA-ters` (`kontrol-EdDSA`); `VC09_GJ_ES256_EdDSA-ED25519`, `VC09_GJ_ES256_EdDSA-SIRA-ters-ED25519` (`kontrol-Ed25519`); `VC07_GJ_ES256_MLDSA65`, `VC07_GJ_ES256_MLDSA65-SIRA-ters` (`tedavi-ML-DSA-65`); `VC08_GJ_ES256_composite`, `VC08_GJ_ES256_composite-SIRA-ters` (`tedavi-composite`) — `L4`, `P2`, `P0`.
- `VP06_GJ_pq_soyuldu_kb_gecerli` (`tedavi-ML-DSA-65`) — only `P2`, `P0`. The `L4@-19` row of this vector is `reject`: there is no acceptance path (if processed, R is missing; if not processed, the format is not supported).

**Clauses:**
- SD-JWT VC -19 §2.2 (`SDJWTVC.txt:307-309`; T113): "Use of the JWS JSON Serialization per Section 8 of [RFC9901] for SD-JWT VC is not precluded but the specific details are beyond the scope of this specification."
- HAIP §6.1 (`HAIP.txt:468`; T115): "Compact serialization MUST be supported [...] JSON serialization MAY be supported."
- Contrast: SD-JWT VC -13 §3.2 (`SDJWTVC13.txt:302-304`; T114) defines the format ("Section 4 or Section 8 [...] support for the JWS JSON Serialization is OPTIONAL"); therefore the `@-13` rows are determined (a target that does not support the format is B6 "not applicable").
- PR §2D item 7 (`:423`): scope of the parameter "scenario (d) vectors (status of the JSON serialization)".

**Why undetermined:** -19 does not forbid the format but does not define its processing either. A verifier implementing RFC 9901 §8 gives the `@-13` decision; a verifier rejecting the format under the -19 reading is also conforming. **Direction:** none. MR3 ("flagged if the decision changes with the version") uses the difference between these rows and the `@-13` rows.

## B3 — `typ` = `vc+sd-jwt` (VC11) (16 rows)

**Rows:** `VC11_typ_vc+sd-jwt`, four arms × `P2`, `P0` × `@-13`, `@-19`. (The `L4` rows are `reject`: a single classical signature, R missing.)

**Clauses:**
- `@-13`: SD-JWT VC -13 §3.2.1 (`SDJWTVC13.txt:323-324`): "The typ value MUST use dc+sd-jwt." — and (`:336-343`): "it is RECOMMENDED that Verifiers and Holders accept both vc+sd-jwt and dc+sd-jwt as the value of the typ header for a reasonable transitional period."
- `@-19`: SD-JWT VC -19 §2.2.1 (`SDJWTVC.txt:328-329`; T119): "The Issuer MUST include the typ header parameter in the SD-JWT. The typ value MUST use dc+sd-jwt."; the transition note was removed (change log `:3614-3620`: "Remove: "Note that this draft used vc+sd-jwt [...]""); the verifier's `typ` check is only RECOMMENDED in RFC 9901 §9.11 (`:2316-2319`).

**Why undetermined:** in both versions the `typ` rule is a MUST for the producer and at most RECOMMENDED for the verifier. **Direction:** `@-13` accept (RECOMMENDED), `@-19` reject (no transition note; the check is recommended). The interpretation of the MR3 pair (VC01 ↔ VC11) can use these directions; a direction is not an oracle decision.

## B4 — A registered name or an empty list in `crit` (6 rows)

**Rows:** `CRIT03_kayitli_ad`, `CRIT04_bos_dizi` — `tedavi-ML-DSA-65`; `L4`, `P2`, `P0`.

**Clauses:** RFC 7515 §4.1.11 (`RFC7515.txt:703-711`): "Producers MUST NOT include Header Parameter names defined by this specification or [JWA] for use with JWS [...] Producers MUST NOT use the empty list "[]" as the "crit" value. Recipients MAY consider the JWS to be invalid if the critical list contains any Header Parameter names defined by this specification or [JWA] for use with JWS or if any other constraints on its use are violated."

**Why undetermined:** the prohibition is on the producer; the recipient is only given a MAY. Since `alg` is understood by every recipient, the rule "not understood → invalid" (first sentence of §4.1.11) is not triggered; an empty list has no unknown name either. **Direction:** none. (Comparison: in `CRIT01` and `CRIT05` the listed extension is not understood, so `reject` is determined; in `CRIT02` the unprotected `crit` is also `reject`.)

## B5 — Trust anchor inside x5c (3 rows)

**Rows:** `X5C06_guven_capasi_x5c_icinde` — `tedavi-ML-DSA-65`; `L4`, `P2`, `P0`.

**Clauses:** HAIP §6.1.1 (`HAIP.txt:490`): "The X.509 certificate of the trust anchor MUST NOT be included in the x5c JOSE header of the SD-JWT VC." — RFC 7515 §4.1.6 (`RFC7515.txt:596-599`; T038): "The recipient MUST validate the certificate chain according to RFC 5280 [...] and consider the certificate or certificate chain to be invalid if any validation failure occurs."

**Why undetermined:** the HAIP obligation is on the producer of the credential; it does not tell the verifier to "reject". The presence of the root in x5c does not break the RFC 5280 path validation (the anchor is configured locally; `guven_capalari`). Both acceptance (path valid) and rejection (profile non-conformance) are conforming. **Direction:** none.

## B6 — x5c and a kid pointing to another key (3 rows)

**Rows:** `X5C10_x5c_ve_baska_anahtar_kid` — `tedavi-ML-DSA-65`; `L4`, `P2`, `P0`.

**Clauses:**
- SD-JWT VC -13 §3.5 (`SDJWTVC13.txt:748-754`): "When the protected header of the Issuer-signed JWT contains the x5c parameter, the recipient uses the public key from the end-entity certificate of the certificates from that x5c parameter" → the signature is valid with the leaf (ML-DSA-65) key → accept.
- 8725bis §3.1 (`JWTBCP.txt:468-471`): "The library MUST verify that the algorithm specified in the "alg" [...] is consistent with the algorithm associated with the key identified by the corresponding identifier (e.g., "kid") during key lookup." → a library that looks up by kid finds the ES256 key, inconsistent with ML-DSA-65 → reject.
- RFC 7515 §4.1.4 (`:551-552`): kid "is a hint".

**Why undetermined:** when x5c and kid are both present, the clauses do not determine which one takes precedence in key resolution; both paths are consistent with their own clause, and one gives acceptance, the other rejection. The manifest also describes the vector as "key resolution ambiguity". **Direction:** none (the reject path is on the safe side but not mandatory).

## B7 — Non-minimal DER, composite ECDSA component (3 rows)

**Rows:** `CMP05_ecdsa_asgari_olmayan_der` — `tedavi-composite`; `L4`, `P2`, `P0`.

**Clauses:**
- composite -04 §4.5 (`JOSECOMP.txt:555-557`): "the DER-encoded Ecdsa-Sig-Value [RFC3279]"; §4.5.1 (`:606`): "Decoding simply reverses these two steps."; §4.3 (`:489`): wrong "type or length" → "Invalid signature".
- LAMPS composite -19 §4.3 (`LAMPSCOMP.txt:1300-1301`): "raising an error in the event that the input is malformed".
- composite -04 §6.4 (`JOSECOMP.txt:1101-1103`): "existential unforgeability under chosen-message attack (EUF-CMA) is sufficient to meet the intended security goals."

**Why undetermined:** the encoding is BER, not DER (an extra 0x00 before r); the numerical values belong to a valid signature (`insa`). A strict DER decoder counts it as "malformed" and rejects; a decoder that "reverses these two steps" obtains the same r, s and accepts. There is no MUST that explicitly puts strict DER rejection on the verifier; the stated security goal is EUF-CMA (signature malleability is outside the goal). **Direction:** none. (Comparison: `CMP03` corrupted length byte, `CMP04` not DER, `CMP06` trailing byte at the end → `reject` determined as a "type or length" error.)

## B8 — DPoP nonce/ath context (6 rows)

**Rows:** `DPOP08_ML-DSA-65_ath_nonce` (`tedavi-ML-DSA-65`), `DPOP09_ML-DSA-65-ES256_ath_nonce` (`tedavi-composite`) — `L4`, `P2`, `P0`.

**Clauses:** RFC 9449 §4.3 (`RFC9449.txt:506-507`): "If the server provided a nonce value to the client, the nonce claim matches the server-provided nonce value." — (`:511-516`): "If presented to a protected resource in conjunction with an access token, [...] ensure that the value of the ath claim equals the hash of that access token".

**Why undetermined:** at signature and algorithm level there is an acceptance path. `dogrulama_girdileri` gives only `htm`, `htu` (token endpoint) and `simdi`; the server-provided nonce and the access token are missing. The result of checks 10 and 12 depends on this context. **Direction:** none. (These vectors are for the size threshold table; PR §2D item 6.)

## B9 — Unsigned OID4VP request, L4 (8 rows)

**Rows:** `REQ08_imzasiz_M-b0`, `REQ09_imzasiz_M-b0_client_id_korundu` — four arms × `L4`. (The `P2`/`P0` rows are `accept-classical`: an unsigned request must be supported; in REQ09 the `client_id` is ignored.)

**Clauses:**
- HAIP §5.2 (`HAIP.txt:426`; T281): "The Wallet MUST support unsigned, signed, and multi-signed requests as defined in Appendices A.3.1 and A.3.2 of [OIDF.OID4VP]." — (`:428`; T282): "unsigned requests depend on the origin information provided by the platform and the web PKI".
- OID4VP §5.9.3 (`OID4VP.txt:894`; T268): with the DC API "it is at the discretion of the Wallet whether it validates the signature on the Request Object".
- OID4VP A.2 (`:2500`; T279): "The Wallet MUST ignore any client_id parameter that is present in an unsigned request."
- PR §4.7 G5 (`:767`): a migrated entity "cannot be accepted with classical evidence only" outside its window.

**Why undetermined:** the `L4` configuration expects R = {X} for the signing RP; an unsigned request has no signature, and the RP identity comes only from the origin + Web PKI (classical). HAIP makes support mandatory, while G5 (the security goal of the PR) forbids acceptance with classical evidence only; moreover, since `client_id` is ignored, the wallet may not be able to match this request to "the migrated RP". The clauses conflict or do not determine. This is the baseline class **M-b0 (unsigning)** of PR Ö4 and is examined in the formal part of H3; the library-level oracle does not decide. **Direction:** none.
