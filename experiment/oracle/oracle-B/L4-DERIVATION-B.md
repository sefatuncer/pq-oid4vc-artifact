# INDEPENDENT DERIVATION OF THE L4 ORACLE — Oracle B

> **Task:** PR Ö6: "**L4 oracle:** There is no direct normative clause. The oracle is derived from 8725bis §3.1 + composite AND + the definition of G5. The N-version oracle makes this derivation independently." (`ON-KAYIT-TASLAK.md:173`)
> **Written by:** Oracle B, 25.09.2026. The work of Oracle A was not seen (`ACCESS-LOG.md`).
> **Source texts** (`spec-corpus/metin/`, SHA-256 values in `METHOD.md` §8): 8725bis = draft-ietf-oauth-rfc8725bis-10 (`JWTBCP.txt`); composite = draft-ietf-jose-pq-composite-sigs-04 (`JOSECOMP.txt`); RFC 7515; RFC 9901; ECCG ACM v2.0 (`ACM2.txt`); PR v0.8 (`ON-KAYIT-TASLAK.md`, SHA-256 `dcc84092…`).
> The quotations below were copied verbatim from the source lines (hyphens at line ends joined). Short forms of the same quotations are verified automatically in the source by `derive_decisions.py`.
>
> (Quotations from the pre-registration are translated from Turkish; quotations from specifications are verbatim. Premises are numbered Pr-1 … Pr-12.)

---

## 0. Scope and a note on independence

- Subject of the derivation: whether a JOSE/SD-JWT verifier, under a policy configured **per issuer**, **accepts or rejects** a single- or multi-signature document; and if it accepts, whether the acceptance rests on **classical or hybrid (PQ-component)** evidence.
- The primary definition of G5 is PR §4.7 (Pr-8 below). The names "G5-untimed / G5-timed / G5-migrated" of PR §2D item 10 appeared in the chunk that was read; this derivation does not use their **results**, it only mentions their names when discussing the time dimension in §5.

## 1. Premises (verbatim quotations)

**Pr-1 — 8725bis §3.1, allowed set (library obligation)** (`JWTBCP.txt:463-466`; matrix T327):
> "Libraries MUST provide a mechanism that enables developers to explicitly restrict the set of algorithms permitted for use and MUST NOT employ any algorithms outside this configured set when performing cryptographic operations."

**Pr-2 — 8725bis §3.1, key–algorithm consistency** (`JWTBCP.txt:468-471`; T329):
> "The library MUST verify that the algorithm specified in the "alg" or "enc" header parameter is consistent with the algorithm associated with the key identified by the corresponding identifier (e.g., "kid") during key lookup."

**Pr-3 — 8725bis §3.1, algorithms permitted per issuer (recipient obligation)** (`JWTBCP.txt:482-485`; T328):
> "When a recipient receives a JWT signed by a particular issuer, it MUST determine which algorithms are permitted for itself and that issuer and ensure that the received JWT complies with those requirements."

**Pr-4 — 8725bis §3.1, one key one algorithm** (`JWTBCP.txt:488-491`):
> "In accordance with established cryptographic best practices, each key MUST be used with exactly one algorithm. Compliance with this requirement MUST be enforced and validated at the time the cryptographic operation is executed."

**Pr-5 — composite -04 §4.3, component AND** (`JOSECOMP.txt:452-453`; T345) and verification steps (`JOSECOMP.txt:489`, `497-502`):
> "The Verify algorithm MUST validate a signature only if all component signatures were successfully validated."
> "If Error during deserialization, or if any of the component keys or signature values are not of the correct type or length for the given component algorithm then output "Invalid signature" and stop."
> "if NOT ML-DSA.Verify(mldsaPK, M', ctx=Label) / output "Invalid signature" / if NOT Trad.Verify(tradPK, M') / output "Invalid signature" / if all succeeded, then / output "Valid signature""

**Pr-6 — composite -04 §6.1 and §6.3, purpose of the AND** (`JOSECOMP.txt:1020-1026`, `1075-1077`; T347):
> "By requiring the successful verification of both the ML-DSA component and the traditional component, this construction ensures: [...] *Dual-Algorithm Security:* An adversary that compromises only one of the component algorithms cannot produce cryptographically protected JOSE/COSE objects as long as the other component remains secure."
> "*Cross-Algorithm Prevention:* The unique label, specific to each composite algorithm, ensures that signatures cannot be removed from the composite and used in other contexts."

**Pr-7 — ACM v2 Note 51, hybridisation by concatenated signatures** (`ACM2.txt:946`; T135):
> "For digital signatures, hybridization can consist in concatenating signatures from diﬀerent schemes, the veriﬁcation function accepting if and only if all signatures are correct."

**Pr-8 — Definition of G5, PR §4.7** (`ON-KAYIT-TASLAK.md:767`):
> G5 | downgrade resistance: "A migrated entity cannot be accepted with classical evidence only outside the legacy-version window it has announced." | ∀ E #j #m. AcceptClassicalOnly(E)@j ∧ Migrated(E)@m ∧ m < j ⇒ LegacyWindowOpen(E) at time j

**Pr-9 — RFC 7515 §5.2, with multiple signatures the decision is the application's** (`RFC7515.txt:810-816`; T314, T315):
> "When there are multiple JWS Signature values, it is an application decision which of the JWS Signature values must successfully validate for the JWS to be accepted. In some cases, all must successfully validate, or the JWS will be considered invalid. In other cases, only a specific JWS Signature value needs to be successfully validated. However, in all cases, at least one JWS Signature value MUST successfully validate, or the JWS MUST be considered invalid."

**Pr-10 — RFC 7515 §4.1.1, an unsupported alg is invalid** (`RFC7515.txt:508-511`; T319):
> "The JWS Signature value is not valid if the "alg" value does not represent a supported algorithm or if there is not a key for use with that algorithm associated with the party that digitally signed or MACed the content."

**Pr-11 — Policy and criterion clauses of the PR:**
- §6.5 (`:1048`, `:1054`): "First signature A = ES256." — "Required set per issuer R = {X}, allowed set {A, X}."
- §4.13 L4 (`:844`): "\"Required algorithm set\" semantics: reject if there is no PQ component | PQ-specific | In the configured state K1 ACCEPT, K2 REJECT, K3 REJECT (§6.5)"
- §4.8 P1 (`:776`): "P1 | all-present-valid | ECCG AND | Accept if all present signatures are valid. Removal of a signature (stripping) goes unnoticed"; P3 (`:778`): "P2 + required set per issuer R_I".
- §2B item 6 (`:255-256`): L4m "Reject if there is no PQ component."; L4c "In the same verifier instance, a policy "PQ/composite mandatory" **per issuer** with the documented API. A document of a migrated issuer signed only classically is rejected; the classically signed document of the old issuer is accepted."

**Pr-12 — Scope bridge (SD-JWT):** RFC 9901 §7.1 (2a) (`RFC9901.txt:1663-1665`; T103): "Ensure that the used signing algorithm was deemed secure for the application. Refer to [RFC8725], Sections 3.1 and 3.2 for details." — 8725bis §3.1 applies directly to the SD-JWT issuer signature. 8725bis itself recalls that JWTs are compact (§2.13, `JWTBCP.txt:446-447`: "While JWTs must use the Compact Serialization"); §3.1 applies to a multi-signature General JSON JWS only by **extension** (see §9, limitation S1).

## 2. Derivation (step by step)

Notation: a document D carries a set of signatures S(D) = {s₁ … sₙ} (n ≥ 1); for every s, alg(s) and key k(s). The verifier configuration for issuer I is (Perm_I, R_I).

**A1 — The object of the policy is the issuer.** Pr-3 says "permitted for itself and that issuer": the allowed set is determined per issuer. PR §6.5 makes it concrete: Perm_I = {A, X}, A = ES256. → *Rule 1:* the verifier keeps a separate (Perm_I, R_I) for every issuer.

**A2 — A signature outside the allowed set is not verified, and therefore not valid.** Pr-1: the library **may not use** an algorithm outside the configured set ("MUST NOT employ"). Pr-10: for an unsupported/unusable alg the signature is "not valid". → *Rule 2:* alg(s) ∉ Perm_I ⇒ s invalid. (The label is case-sensitive: RFC 7515 §4.1.1 "The "alg" value is a case-sensitive ASCII string"; the case attack of 8725bis §2.11.)

**A3 — Key–algorithm binding.** Pr-2 and Pr-4: alg(s) must be consistent with the algorithm to which k(s) is bound; a key is used with a single algorithm (RFC 9864 §7 says the same: "A cryptographic key MUST be used with only a single algorithm"; `alg` is mandatory in an AKP key, RFC 9964 §3). → *Rule 3:* alg(s) ≠ alg(k(s)) ⇒ s invalid. This is a **library** obligation; no configuration can switch it off (K10 is rejected in every configuration).

**A4 — The validity of a composite signature is the AND of its components.** Pr-5: a composite signature is valid only if both components are valid; a deserialization error or a wrong type/length is "Invalid signature". → *Rule 4:* composite s valid ⇔ ML-DSA component (over M′, ctx = Label) ∧ classical component (over M′) valid ∧ encoding correct.

**A5 — AND at document level (all-present-valid).** By Pr-9, which signatures must be valid with multiple signatures is **the application's decision**; RFC 7515 does not determine it, it only sets the lower bound "at least one". The decision is tied down by three premises:
- Pr-7 (ACM v2): in hybridisation by concatenating signatures, verification is "accepting if and only if all signatures are correct".
- Pr-5/Pr-6: composite enforces the same AND at component level; its purpose is that an attacker who breaks a single component cannot produce an object.
- Pr-11 (PR §4.8): P1 = "all-present-valid", its counterpart is "ECCG AND"; P3 = P2 + R_I = P1 + binding + R_I (cumulative).
→ *Rule 5:* under L4, **every signature in S(D)** must be valid in the sense of Rules 2–4. Otherwise reject. (Consequence: K2 — X signature corrupted — **reject**; K5 — extra signature with an unrecognised alg — **reject**; see §6.)

**A6 — G5 makes the required set (R_I) mandatory.** Rule 5 alone does not stop stripping: in a document whose X signature has been removed (K3), the only remaining signature A is valid, so it is "all present valid". PR §4.8 writes this explicitly: under P1 "Removal of a signature (stripping) goes unnoticed". Pr-8 (G5): a migrated entity cannot be accepted **with classical evidence only** outside its legacy-version window. The document in K3 is from a migrated issuer and carries only classical evidence (ES256) → G5 forbids acceptance. The smallest configuration expression that restricts acceptance so that it cannot reduce to classical evidence only is to make the issuer's PQ algorithm **required**: R_I = {X}, X ∈ PQ. This coincides with "Required set per issuer R = {X}" of PR §6.5 and with "ensure that the received JWT complies with those requirements" of Pr-3 (the issuer's requirement is now "there must be an X signature").
→ *Rule 6:* ∀ x ∈ R_I ∃ s ∈ S(D): alg(s) = x ∧ s valid. Otherwise reject.

**A7 — Combined L4 rule.**

```
L4(D; Perm_I = {A, X}, R_I = {X}) = ACCEPT  ⇔  n ≥ 1
                                            ∧ ∀ s ∈ S(D): alg(s) ∈ Perm_I ∧ alg(s) = alg(k(s)) ∧ valid(s)      [Rules 2–5]
                                            ∧ ∀ x ∈ R_I ∃ s ∈ S(D): alg(s) = x ∧ valid(s)                       [Rule 6]
                                    otherwise REJECT
```

**A8 — Four-valued output.** If ACCEPT: `accept-hybrid` if the valid signatures on which the acceptance rests include a component of PQ class (ML-DSA or composite), otherwise `accept-classical`. If the clauses do not decide between acceptance and rejection, `indeterminate` (§7). In the control arm X = EdDSA is classical; there Rule 6 tests not G5 but **the same API semantics** (PR §3.7: "L4 is measured in the control arm (second algorithm EdDSA). This separates the API capability from PQ support."). Therefore the L4 acceptances in the control arm are `accept-classical`.

**A9 — Consistency check against the PR §4.13 criterion.** Rule A7 gives the L4 behavioural criterion of the PR ("K1 ACCEPT, K2 REJECT, K3 REJECT") in all four arms (table of §3). The criterion was **derived** from the rule; it was not given to the rule as an input.

## 3. L4m — multi-signature form (General JSON)

L4m (PR §2B item 6: "'Required algorithm set' semantics with the documented API and without changing code. Reject if there is no PQ component.") is the direct application of A7 to multi-signature documents. The signature order does not enter the decision (RFC 7515 §5.2 step 9: "repeat this process (steps 4-8) for each digital signature or MAC value"; §7.2.1 computes every signature with its own header) → the MR4 twins get the same decision as their sources.

Primary cases (from decisions.tsv; `acc-cl` = accept-classical, `acc-hy` = accept-hybrid; P2 and P0 for comparison):

| Case | Arm | Vector | L4 | P2 | P0 |
|---|---|---|---|---|---|
| K1 | K-EdDSA | `T1K_both_valid` | acc-cl | acc-cl | acc-cl |
| K1 | K-Ed25519 | `T1K_both_valid-ED25519` | acc-cl | acc-cl | acc-cl |
| K1 | T-ML-DSA-65 | `T1P_both_valid` | acc-hy | acc-hy | acc-hy |
| K1 | T-composite | `T1C_both_valid` | acc-hy | acc-hy | acc-hy |
| K2 | K-EdDSA | `T2K_second_tampered` | reject | reject | acc-cl |
| K2 | K-Ed25519 | `T2K_second_tampered-ED25519` | reject | reject | acc-cl |
| K2 | T-ML-DSA-65 | `T2P_second_tampered` | reject | reject | acc-cl |
| K2 | T-composite | `T2C_second_tampered` | reject | reject | acc-cl |
| K3 | four arms | `T3_stripped_to_ES256` | reject | acc-cl | acc-cl |
| K4 | K-EdDSA | `T5K_only_EdDSA` | acc-cl | acc-cl | acc-cl |
| K4 | K-Ed25519 | `T5K_only_EdDSA-ED25519` | acc-cl | acc-cl | acc-cl |
| K4 | T-ML-DSA-65 | `T5P_only_ML-DSA-65` | acc-hy | acc-hy | acc-hy |
| K4 | T-composite | `T5C_only_ML-DSA-65-ES256` | acc-hy | acc-hy | acc-hy |
| K5 | K-EdDSA | `T7K_plus_kayitsiz` | reject | reject | acc-cl |
| K5 | K-Ed25519 | `T7K_plus_kayitsiz-ED25519` | reject | reject | acc-cl |
| K5 | T-ML-DSA-65 | `T7P_plus_kayitsiz` | reject | reject | acc-hy |
| K5 | T-composite | `T7C_plus_kayitsiz` | reject | reject | acc-hy |

Reading: L4 and P2 diverge only in **K3** (stripping; Rule 6). P2 and P0 diverge in **K2 and K5** (Rule 5). These three columns are the distinguishing signature of the B5 classes "required set / all present valid / at least one valid": the K1–K3 triple is (ACCEPT, REJECT, REJECT) / (ACCEPT, REJECT, ACCEPT) / (ACCEPT, ACCEPT, ACCEPT) respectively.

## 4. L4c — compact serialization only

A compact JWS carries a single signature (RFC 7515 §7.1: "Only one signature/MAC is supported by the JWS Compact Serialization"). With n = 1, A7 reduces to:

```
L4c(D; I) = ACCEPT ⇔ alg(s₁) ∈ Perm_I ∧ alg(s₁) = alg(k(s₁)) ∧ valid(s₁) ∧ (R_I = ∅ ∨ alg(s₁) ∈ R_I)
```

The two halves of L4c are **two issuers in the same verifier instance** (Pr-3 "for itself and that issuer"; PR §2B item 6):

| Issuer | Configuration | Oracle code | Classical-only (ES256) document | Document signed with X |
|---|---|---|---|---|
| Migrated (window closed) | R_I = {X}, Perm_I = {A, X} | `L4` | **reject** (G5) | accepted (`accept-hybrid` in treatment, `accept-classical` in control) |
| Old (not migrated) | R_I = ∅, Perm_I = {A, X} | `P2` (≡ `P0` with n = 1) | **accept-classical** | accepted |

Counterparts in the battery: `VPLUS_ES256` (four arms; `L4` → reject, `P2` → accept-classical), `VPLUS_EdDSA`, `VPLUS_ML-DSA-65`, `CMP00_gecerli_referans` (signed with X; accepted in the three configurations), `VMINUS_*` (reject in every configuration), `VC10_ikili_ihrac` (K11: the classical copy of a compact SD-JWT VC; `L4` → reject, `P2` → accept-classical). The behavioural criterion of L4c is whether a target can produce these two rows together in the same instance (PR §2B item 6: "the classically signed document of the old issuer is accepted").

## 5. Time dimension (the "legacy-version window" of G5)

The premise of G5 is LegacyWindowOpen(E): while the window is open, classical acceptance is **allowed**. At library level the window is expressed by the configuration itself: window open → R_I = ∅ for the issuer (`P2`); window closed → R_I = {X} (`L4`). The C3 battery uses a fixed `simdi` and carries no window parameter; the decisions of PR §6.5 K3/K11 (REJECT) assume a migrated issuer **whose window has closed**. The oracle applies this assumption in the `L4` rows; the `P2` rows correspond to an open window. (The names of the G5 forms of PR §2D item 10 evoke this distinction; their results were not used.)

## 6. Other cases under L4

| Case | L4 decision | Determining premise |
|---|---|---|
| K5 (`T7*`, unregistered extra signature) | reject | Rule 2 (X-KAYITSIZ-1 ∉ Perm_I, no key) + Rule 5 (AND). Accepted under P0 → the policy dependence expected by MR2 |
| K5 secondary (`T4*`, `T6`, `UNK04/05`: a real extra signature that is not allowed) | reject | Rules 2 + 5 (the extra signature cannot be verified; the AND fails) |
| K6 (`CMP00`) | accept-hybrid | Rule 4 (both components valid) + Rule 6 |
| K7 (`CMP01/02`; secondary CMP03–04, 06–11, 16) | reject | Rule 4 (component/encoding/M′/ctx error → "Invalid signature") |
| K8 (`X5C04`, ML-DSA arm) | accept-hybrid | Rule 6 constrains the JWS signature; the chain is valid under RFC 5280. The §6.5 policy does not constrain the chain edges → the path class is reported with B2 |
| K9 (`X5C07`) | reject | Not from L4 but from key resolution: RFC 7515 §6 + SD-JWT VC -13 §3.5 (an unprotected x5c cannot enter the trust decision) |
| K10 (all directions) | reject | Rule 3 (Pr-2, Pr-4); independent of the configuration |
| K11 (`VC10` classical copy) | reject | Rule 6 (G5) |
| V+ `VPLUS_ES256` | reject | Rule 6. PR §4.15 expects ACCEPT for V+ → the V+ check must run under `P2` (decision notes N2) |

## 7. Cases not determined by the clauses (→ `indeterminate`)

Even where the L4 rule leaves an acceptance path, the clauses do not determine the decision in these cases (details and row list in `UNDETERMINED.md`):
1. Which signature `sd_hash` binds in a multi-signature SD-JWT+KB (RFC 9901 §8.1; PR §2D item 4).
2. In SD-JWT VC -19 the details of the JSON-serialized form are out of scope (SD-JWT VC -19 §2.2).
3. Transition of `typ` (VC11): acceptance under -13 only RECOMMENDED; under -19 the verifier's `typ` check only RECOMMENDED.
4. A registered name / an empty list in `crit`: only a MAY for the verifier.
5. Trust anchor inside x5c: MUST NOT for the producer in HAIP, no rule for the verifier.
6. x5c together with a kid pointing to another key: priority of key resolution undefined.
7. Non-minimal DER (composite ECDSA component): strict DER rejection is not explicitly placed on the verifier; the goal is EUF-CMA.
8. DPoP nonce/ath context not given.
9. Unsigned OID4VP request with the expectation of a migrated RP: HAIP's "MUST support unsigned" conflicts with G5.

## 8. Relation to P0–P4 and B5

| PR §4.8 | At library level | Oracle code | B5 class |
|---|---|---|---|
| P0 any-valid | + mandatory binding (Rule 3) | `P0` | at least one valid |
| P1 all-present-valid | P1 without binding does not exist in a conforming library → P1 ≡ P2 | `P2` | all present valid |
| P2 = P1 + binding | | `P2` | all present valid |
| P3 = P2 + R_I (classical channel) | the channel of R_I is outside the library → P3 ≡ P4 | `L4` | required set |
| P4 = P3 (PQ channel; M-f) | | `L4` | required set |

## 9. Limits of the derivation and alternative readings

- **S1 — JWT → JWS extension.** 8725bis §3.1 is for JWTs; a JWT is compact (§2.13). Its application to a General JSON multi-signature JWS (scenario d) is an extension. Rationale: SD-JWT (RFC 9901 §7.1 2a) refers to 8725bis §3.1, and RFC 9901 §8 defines the JSON serialization; PR §6.5 labels scenario (d) "outside the specification".
- **S2 — AND, or "required set only"?** The alternative to Rule 5 is to **ignore** extra signatures that are not allowed once R_I is met ("required set, the rest free"). Under this reading K5 and the K5 secondaries would be **accepted** under L4; K1–K4 would not change. This derivation chose the AND because (i) PR §4.8 defines P3 cumulatively on top of P1 (ECCG AND), (ii) ACM v2 says "all signatures are correct" for hybridisation, (iii) 8725bis §3.1 requires the recipient to make sure the document "complies" with the issuer's requirements, and a document carrying a signature with a non-allowed algorithm does not meet that requirement. The choice was flagged in `DECISION-NOTES.md` N4; if Oracle A reads it differently, a divergence is expected in K5 and falls into the "undetermined" class.
- **S3 — The name "accept-hybrid".** Pure PQ acceptance (K4 treatment) was also counted as `accept-hybrid` (the PR has no semantics for the four values; N1).
- **S4 — Chain class.** `accept-hybrid` classifies only the JWS layer; classical edges on the certificate path (K8) are reported separately with B2.
