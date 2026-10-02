# Oracle A — reasons for the `indeterminate` decisions

> **Scope:** the **75 rows** with `karar = indeterminate` in `karar.tsv` fall into six reasons. Only **4** of them are primary: T7K, T7K-ED25519, T7P and T7C in the base configuration `L4`, under B-1. These four are determined in the sub-configurations `L4-S` and `L4-Y`.
> **Rule:** `indeterminate` was written where the clauses + construction facts do not determine the decision. Oracle A did not guess and did not choose one of the two readings. For each group the following is given: the two readings, which clauses conflict, and what could remove the ambiguity.
> To reproduce the row lists: filter the rows of `karar.tsv` with `karar == "indeterminate"` and group them by the keyword in the `not` column.
>
> (Quotations from the pre-registration are translated from Turkish; quotations from specifications are verbatim.)

## B-1. Extra signature outside the allowed set (PR §6.5 K5, "depending on the policy") — 32 rows, 4 primary

**Vectors:**
- T7K/T7P/T7C (`X-KAYITSIZ-1`) and T7K-ED25519;
- T4K/T4P/T4C, T6 and their Ed25519 twins;
- UNK04 (`ML-DSA-65-P256`), UNK05 (`none`);
- all MR4 permutations of these vectors.

Undetermined only in configuration `L4`. Example T7P (ML-DSA arm):

| Reading | Basis | Decision |
|---|---|---|
| **S (strict, *sıkı*):** every present signature must be in W and valid | PR §4.8 P3 = P2 + R_I, P2 ⊇ P1 ("Accept if all present signatures are valid"); ECCG ACM v2 Note 51 [T135] "the veriﬁcation function accepting if and only if all signatures are correct"; RFC 7515 §5.2 [T316] "unless the algorithm(s) used in the JWS are acceptable to the application, it SHOULD consider the JWS to be invalid" | `reject` |
| **Y (ignore, *yok say*):** a signature outside W is not used; accept if those in R and W are valid | RFC 7515 §5.2 [T314] "it is an application decision which of the JWS Signature values must successfully validate"; 8725bis §3.1 [T327] "MUST NOT employ any algorithms outside this configured set" (an algorithm outside is not used in verification; it need not invalidate the object) | `accept-hybrid` (`accept-classical` in the control arm) |

**Why do the clauses not determine it?**
1. The K5 row of PR §6.5 leaves the decision explicitly to the policy: "Depending on the policy (MR2); flag B1".
2. The phrase "algorithm(s) used in the JWS" in RFC 7515 §5.2 can be read in two ways: every present signature, or the signatures the application relies on? The text does not distinguish.
3. The §6.5 policy ("R = {X}, allowed {A, X}") does not mention the P1 component of P3 explicitly.

**How is it used?**
- In Step 10, K5 is compared with the reading (S or Y) that the target's documented semantics follows. B1 records this class.
- Behaviour that fits neither reading is an **MR2 violation**. Example: `accept-classical` in T7 (acceptance without verifying the PQ signature), or an exception in T7 while T1 is accepted.
- Since F_K/F_T are computed only from K1–K3 (PR §6.4), B-1 does not affect the primary outcome variables.

**To remove it:** write in the PR whether the §6.5 policy is S or Y (decision notes N-1).

## B-2. General JSON + several issuer signatures + KB-JWT `sd_hash` — 15 rows, 0 primary

**Vectors:**
- VP05 (sd_hash built with the first signature),
- VP07 (sd_hash built with the second signature),
- VP05-SIRA-ters (descriptive, outside MR4).

Configurations: `L4`, `L4-S`, `L4-Y`, `P0`, `P1`.

**Conflict:**
- RFC 9901 §8.1: "the SD-JWT Compact Serialization part is built by concatenating the protected header, the payload, and the signature of the JWS JSON serialized SD-JWT". The singular "the signature" does not say which signature is meant when General JSON has several.
- RFC 9901 §7.3 (5g), on the other hand, makes the sd_hash match mandatory: "verify that it matches the value of the sd_hash claim".
- PR §2D item 4 has already recorded this: "which signature `sd_hash` binds is undefined". This is an external notification candidate (DB-1).

**Result:** At the level of the issuer signature the decision is determined. Example: VP05 under `L4` meets R and is `accept-hybrid` at signature level. The result of the KB verification, however, depends on the signature the verifier chooses: the first, the second, or trying all of them. Hence `indeterminate`.
- Cells that are rejected at issuer-signature level are not undetermined. Example: VP06 under `L4` does not meet R → `reject`.
- VP06 has a single signature, so the sd_hash binding is unique → `accept-classical` under `P0`/`P1`/`GEC`.

**To remove it:** an RFC 9901 erratum or an SD-JWT VC profile (DB-1). Under PR §2D item 4 these cells are reported as **descriptive** anyway. Which signature the target hashes is recorded as an observation.

## B-3. DER strictness of the composite ECDSA component — 10 rows, 0 primary

**Vectors:**
- CMP05: non-minimal DER, values valid;
- CMP06: valid signature + 1 trailing byte at the end.

Configurations: `GEC`, `IZIN-AX`, `L4`, `L4-S`, `L4-Y`. In `IZIN-A`, `reject` is determined because the alg is outside W.

**Conflict:**
- composite -04 §4.2: "the ECDSA signature is encoded as an Ecdsa-Sig-Value". §4.5.1 defines the encoding as DER but for decoding only says: "Decoding simply reverses these two steps."
  - A non-minimal INTEGER decodes to the same r value by "reversing the steps" → accept direction.
  - A strict DER parser rejects → reject direction.
- LAMPS -19 §4.3: "Deserialization reverses this process, raising an error in the event that the input is malformed." "Malformed" is not defined.
- The tradSig of CMP06 is 72 bytes and fits the "≤ 72" bound of -04 Table 2. Therefore the length check of -04 §4.3 does not distinguish either.
- The canonicity rule of DER (X.690) is not in the corpus.

**To remove it:** add a sentence such as "Ecdsa-Sig-Value MUST be DER-encoded and verifiers MUST reject non-canonical encodings and trailing data" to the composite draft. This is a candidate editorial note next to DB-2 (decision notes N-6). The vectors are secondary (K7 secondary).

## B-4. MAY for the recipient of `crit` — 8 rows, 0 primary

**Vectors:**
- CRIT03: `crit=["alg"]`,
- CRIT04: `crit=[]`.

Configurations: `GEC`, `L4`, `L4-S`, `L4-Y`.

- RFC 7515 §4.1.11 says MUST NOT to the producer: "Producers MUST NOT include Header Parameter names defined by this specification … Producers MUST NOT use the empty list".
- To the recipient it only gives permission: "Recipients MAY consider the JWS to be invalid if the critical list contains any Header Parameter names defined by this specification … or if any other constraints on its use are violated."
- In CRIT03 the listed "alg" is an understood parameter, so the rule "not understood → invalid" is not triggered either.

**For comparison:** CRIT01, CRIT02 and CRIT05 are determined (`reject`), because the listed extension is not understood: "If any of the listed extension Header Parameters are not understood and supported by the recipient, then the JWS is invalid" [T386].

## B-5. Trust anchor inside `x5c` (X5C06) — 5 rows, 0 primary

Configurations: `GEC`, `L4`, `L4-S`, `L4-Y`, `L4-YOL`.

- HAIP §6.1.1 [T043]: "The X.509 certificate of the trust anchor MUST NOT be included in the x5c JOSE header of the SD-JWT VC." This is an obligation on the **content** of the SD-JWT VC (on the producer). Whether the verifier must reject such an object is not written.
- Under RFC 7515 §4.1.6 [T038] the RFC 5280 path is built from the trust anchor even if the root certificate is inside x5c.
- **Two readings:** "profile violation → reject" and "path valid → accept (`accept-hybrid`)".

## B-6. `kid` and `x5c` point to different keys (X5C10) — 5 rows, 0 primary

Configurations: `GEC`, `L4`, `L4-S`, `L4-Y`, `L4-YOL`.

- **Accept direction:** SD-JWT VC -19 §2.5 [T045]: "When the protected header of the Issuer-signed JWT contains the x5c parameter, the recipient uses the public key from the end-entity certificate". The key is taken from the leaf certificate and the signature is valid.
- **Reject direction:** 8725bis §3.1 [T329]: "The library MUST verify that the algorithm specified in the "alg" … is consistent with the algorithm associated with the key identified by the corresponding identifier (e.g., "kid")". The kid points to issuer/ES256 (an EC key), the alg is ML-DSA-65.
- Which identifier governs the "key lookup" is not defined. RFC 7515 §6 and Appendix D do not address several identifiers that contradict each other. SD-JWT VC §7.3 [T048] ("an attacker cannot influence the type of verification process used") favours reading the effect of the kid in the reject direction, but gives no direct ruling.

## Rows that are NOT undetermined but are at SHOULD level (information)

| Row | Decision | Basis | Note |
|---|---|---|---|
| VC11 × `GEC` (-13) | `accept-classical` | SD-JWT VC -13 §3.2.1: "it is RECOMMENDED that Verifiers and Holders accept both vc+sd-jwt and dc+sd-jwt … for a reasonable transitional period" | RECOMMENDED; a rejection is not a MUST violation |
| VC11 × `GEC@-19` | `reject` | -19 §2.2.1 [T119] "The typ value MUST use dc+sd-jwt"; the transition note was removed in -19 (-19 change log); RFC 9901 §9.11 "Verifiers check this value" (RECOMMENDED) | Verifier side at SHOULD level. MR3 flags this change as a "version effect" |
| DPOP06/07/09 × `GEC` | `reject` | RFC 9449 §4.3 item 5 [T378] "registered asymmetric digital signature algorithm"; composite -04 §7.1 "are requested to be added" | MUST level, but tied to the IANA registration. If registered, the decision becomes `accept-hybrid` (decision notes N-4) |
