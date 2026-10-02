# Derivation of the L4 oracle (PR Ö6) — Oracle A

> **Task (PR Ö6, line 173):** "**L4 oracle:** There is no direct normative clause. The oracle is derived from 8725bis §3.1 + composite AND + the definition of G5. The N-version oracle makes this derivation independently."
> **PR §4.20 (line 940):** "The oracle is the combination of 8725bis §3.1 with PQ/composite."
> Line numbers refer to the files `spec-corpus/metin/<DOCUMENT>.txt` and `00-on-kayit/ON-KAYIT-TASLAK.md` (v0.8, SHA-256 `dcc84092…`). Every quote is verified by `karar_uret.py`, which finds it in the text (`maddeler.tsv`).
> The derivation of Oracle B was not seen.
>
> (Quotations from the pre-registration are translated from Turkish; quotations from specifications are verbatim. Premises are numbered Pr1–Pr15.)

## 1. Premises (verbatim)

**8725bis-10 §3.1 (JWTBCP)**
- **Pr1** [T327] (l. 463–466): "Libraries MUST provide a mechanism that enables developers to explicitly restrict the set of algorithms permitted for use and MUST NOT employ any algorithms outside this configured set when performing cryptographic operations."
- **Pr2** [T328] (l. 482–485): "When a recipient receives a JWT signed by a particular issuer, it MUST determine which algorithms are permitted for itself and that issuer and ensure that the received JWT complies with those requirements."
- **Pr3** [T329] (l. 468–471): "The library MUST verify that the algorithm specified in the "alg" or "enc" header parameter is consistent with the algorithm associated with the key identified by the corresponding identifier (e.g., "kid") during key lookup."
- **Pr4** (l. 488–491): "each key MUST be used with exactly one algorithm. Compliance with this requirement MUST be enforced and validated at the time the cryptographic operation is executed."
- **Pr5** 8725bis §3.3 (l. 565–567): "All cryptographic operations used in the JWT MUST be validated and the entire JWT MUST be rejected if any of them fail to validate. This is true of JWTs with a single set of Header Parameters."

**composite -04 (JOSECOMP)**
- **Pr6** §4.3 [T345] (l. 452–453): "The Verify algorithm MUST validate a signature only if all component signatures were successfully validated."
- **Pr7** §6.1 (l. 1020–1030): "By requiring the successful verification of both the ML-DSA component and the traditional component, this construction ensures: … *Impersonation Prevention:* … even if the traditional signature component is compromised."

**G5 (PR §4.7)**
- **Pr8** (l. 767): "A migrated entity cannot be accepted with classical evidence only outside the legacy-version window it has announced."
- G5 has three forms (PR §2D item 10). One of them is **G5-migrated** (l. 447): "after the migration, including the first contact, no acceptance with classical evidence only".

**Binding framework**
- **Pr9** RFC 7515 §5.2 [T314, T315] (l. 810–816): "When there are multiple JWS Signature values, it is an application decision which of the JWS Signature values must successfully validate for the JWS to be accepted. … However, in all cases, at least one JWS Signature value MUST successfully validate, or the JWS MUST be considered invalid."
- **Pr10** RFC 7515 §5.2 last paragraph [T316] (l. 892–895): "Even if a JWS can be successfully validated, unless the algorithm(s) used in the JWS are acceptable to the application, it SHOULD consider the JWS to be invalid."

**PR definitions**
- **Pr11** §6.5 (l. 1054): "Required set per issuer R = {X}, allowed set {A, X}."
- **Pr12** §4.13 L4 (l. 844): "'Required algorithm set' semantics: reject if there is no PQ component … In the configured state K1 ACCEPT, K2 REJECT, K3 REJECT (§6.5)".
- **Pr13** §2B item 6 (l. 255–257): L4m "reject if there is no PQ component" and L4c "A document of a migrated issuer signed only classically is rejected; the classically signed document of the old issuer is accepted". "Y_i = L4m (if the target supports multi-signature), otherwise L4c."
- **Pr14** §4.8 (l. 775–779):
  - P1 "Accept if all present signatures are valid. Removal of a signature (stripping) goes unnoticed";
  - P3 "P2 + required set per issuer R_I".
- **Pr15** ECCG ACM v2 Note 51 [T135] (l. 946): "the veriﬁcation function accepting if and only if all signatures are correct".

## 2. Why does no single source give L4?

| Source alone | What it gives | Why it is not L4 |
|---|---|---|
| 8725bis §3.1 (Pr1–Pr4) | Allow-list (L1/L2), allowed set per issuer and alg–key binding (L3) | "complies with those requirements" (Pr2) does not state the **content** of the requirement. A verifier with the allowed set {A, X} accepts an object signed only with A (K3) and still conforms to Pr1–Pr4 |
| composite AND (Pr6) | Joint verification of the two components inside **a single** composite signature (K7) | It says nothing about the set of signatures at JWS level. If the composite signature is stripped entirely (K3), Pr6 never comes into play |
| G5 (Pr8) | Security goal: a migrated entity cannot be accepted with classical evidence only | It is not a verifier rule. How the information "migrated" (R_I) reaches the verifier is outside the library level (P3/P4 channel) |
| P1 / ECCG AND (Pr14, Pr15) | Every present signature must be valid | The PR's own note: "Removal of a signature (stripping) goes unnoticed". K3 is accepted |
| RFC 7515 §5.2 (Pr9) | Minimal rule: at least one signature valid (P0) | It leaves to the application which signatures are required |

**Conclusion.** L4 is the **combination** of these sources. G5 puts a PQ-carrying algorithm into the content of the "requirement" of Pr2 as a necessity. Pr1 and Pr3 determine how this requirement is applied at the algorithm and key level. Pr6 makes sure that the PQ component must also be valid for a composite X to count as "valid".

## 3. Derivation

Let issuer I be migrated, and let its legacy-version window be closed at time `simdi`. The battery carries no time-dimensioned expectation; the oracle assumes the window is closed (§7).

1. **Content of the requirement (Pr2 + Pr8).**
   - By Pr8, an object of I presented with classical evidence only cannot be accepted.
   - By Pr2, the verifier must determine the permitted algorithms "for itself and that issuer" and ensure that the object complies with them.
   - Hence the requirement for I must contain: **at least one PQ-carrying algorithm X must be present and valid.**
   - This is the required set of the PR: R_I ⊇ {X}. The §6.5 policy fixes it as R = {X} (Pr11).
2. **Allowed set (Pr1).** W_I = {A, X}. An algorithm outside W cannot be used in a cryptographic operation.
3. **Key–alg binding (Pr3, Pr4; RFC 7515 §5.2 step 8; RFC 9864 §7 [T335]).** Every signature is verified with the alg in its header and with the key bound to that alg. A mismatch invalidates that signature (K10).
4. **AND inside the composite (Pr6).**
   - If X = ML-DSA-65-ES256, "X valid" ⇔ ML-DSA component valid **and** ECDSA component valid (K6, K7). So meeting R_I definitely includes the verification of the PQ component (Pr7).
   - If X = ML-DSA-65, it is directly PQ.
5. **Which signatures are verified (Pr9).** RFC 7515 leaves this to the application; L4 fixes it as follows: **for every algorithm in R_I there must be a present and valid signature.** Hence:
   - K1 (A + X, both valid) → accept;
   - K2 (X corrupted) → R not met → **reject**;
   - K3 (X stripped) → R not met → **reject**;
   - K4 (X only) → accept.

   These are exactly the behavioural criterion of Pr12 (K1 ACCEPT, K2 REJECT, K3 REJECT).
6. **Other signatures (Pr5, Pr10).**
   - The signatures inside W that are used must be valid (Pr5: "All cryptographic operations used … MUST be validated").
   - For extra signatures **outside** W the sources allow two readings. The PR also leaves K5 open as "Depending on the policy (MR2)" (l. 1062):
     - **S (strict):** Pr10 + Pr14 (P3 ⊇ P1) + Pr15. Every present signature must be in W and valid → K5 **reject**.
     - **Y (ignore):** Pr9 + Pr1. A signature outside W is not used and does not invalidate the object → K5 gets the same decision as K1.

**The L4 decision function.** Let Σ be the set of signatures of an object; for every σ ∈ Σ, alg(σ) and validity g(σ) are given.

```
L4-S(Σ) = ACCEPT  ⇔  ∀σ∈Σ: alg(σ)∈W  ∧  ∀σ∈Σ: g(σ)=valid  ∧  ∀x∈R: ∃σ∈Σ: alg(σ)=x ∧ g(σ)=valid
L4-Y(Σ) = L4-S(Σ ∩ {σ : alg(σ)∈W})          (REJECT if Σ ∩ W is empty; RFC 7515 §5.2 "at least one")
L4(Σ)   = L4-S(Σ)  if L4-S(Σ) = L4-Y(Σ);  otherwise indeterminate  (they diverge only if there is an extra signature outside W)
```

Validity is three-valued (valid / invalid / undetermined). A definite failure is always a rejection. If there is no definite failure and the decision depends on an undetermined signature, the result is `indeterminate` (`METHOD.md` §3).

## 4. Four-valued output (PR Ö6, l. 171)

The distinction of "the policy-parametric contract of Kim et al." is **what the acceptance rests on.** Oracle A's definition:
- `accept-hybrid` ⇔ acceptance **and** every acceptance path allowed by the configuration requires the verification of a valid PQ component.
- `accept-classical` ⇔ acceptance **and** verifying the classical signatures alone is enough for acceptance.

Since R = {X} under L4:
- if X carries PQ (ML-DSA-65, ML-DSA-65-ES256), every acceptance is `accept-hybrid`;
- in the control arms (X = EdDSA / Ed25519) every acceptance is `accept-classical`.

The control arm measures L4 as an **API capability**, independently of PQ support (PR §3.7).

**Contrast (a Kim-style pair):** the same T1P object is
- `accept-hybrid` under P1 (every present signature must be verified),
- `accept-classical` under P0 (ES256 alone is enough).

The stripped T3 is `accept-classical` under P0 and P1, and `reject` under L4. The difference "classical acceptance ≠ hybrid authentication" shows in these three rows.

## 5. K1–K11 and V± decisions (L4 family; generated from `karar.tsv`)

| Case | Arm | Vector | L4 | L4-S | L4-Y | Extra |
|---|---|---|---|---|---|---|
| K1 | kontrol-EdDSA | `T1K_both_valid` | accept-classical | accept-classical | accept-classical |  |
| K1 | tedavi-ML-DSA-65 | `T1P_both_valid` | accept-hybrid | accept-hybrid | accept-hybrid |  |
| K1 | tedavi-composite | `T1C_both_valid` | accept-hybrid | accept-hybrid | accept-hybrid |  |
| K2 | kontrol-EdDSA | `T2K_second_tampered` | reject | reject | reject |  |
| K2 | tedavi-ML-DSA-65 | `T2P_second_tampered` | reject | reject | reject |  |
| K2 | tedavi-composite | `T2C_second_tampered` | reject | reject | reject |  |
| K3 | three arms | `T3_stripped_to_ES256` | reject | reject | reject |  |
| K4 | kontrol-EdDSA | `T5K_only_EdDSA` | accept-classical | accept-classical | accept-classical |  |
| K4 | tedavi-ML-DSA-65 | `T5P_only_ML-DSA-65` | accept-hybrid | accept-hybrid | accept-hybrid |  |
| K4 | tedavi-composite | `T5C_only_ML-DSA-65-ES256` | accept-hybrid | accept-hybrid | accept-hybrid |  |
| K5 | kontrol-EdDSA | `T7K_plus_kayitsiz` | indeterminate | reject | accept-classical |  |
| K5 | tedavi-ML-DSA-65 | `T7P_plus_kayitsiz` | indeterminate | reject | accept-hybrid |  |
| K5 | tedavi-composite | `T7C_plus_kayitsiz` | indeterminate | reject | accept-hybrid |  |
| K6 | tedavi-composite | `CMP00_gecerli_referans` | accept-hybrid | accept-hybrid | accept-hybrid |  |
| K7 | tedavi-composite | `CMP01_ml_bileseni_bozuk` (CMP02 the same) | reject | reject | reject |  |
| K8 | ML-DSA-65, composite (adapted) | `X5C04_karisik_pq_yaprak_klasik_ara` | accept-hybrid | accept-hybrid | accept-hybrid | L4-YOL: reject → B2 |
| K9 | ML-DSA-65, composite (adapted) | `X5C07_korumasiz_x5c` | reject | reject | reject | B3 = 1 for an accepting target |
| K10 | control / ML-DSA / composite | `K10K_…`, `K10P_…`, `K10C_…` (two directions per arm) | reject | reject | reject | reject under IZIN-AX (L3) as well |
| K11 | three arms | `VC10_ikili_ihrac` (credentials[0]) | reject | reject | reject | accept-classical under IZIN-AX (old issuer) |
| V+ | every arm | `VPLUS_ES256` / `VPLUS_X` | GEC: accept / accept | | | L4: reject / accept (L4c migration) |
| V− | every arm | `VMINUS_ES256` / `VMINUS_X` | GEC: reject / reject | | | |

All cells agree with the table of PR §6.5 (l. 1058–1069):
- K1 ACCEPT, K2 REJECT, K3 REJECT, K4 ACCEPT;
- K5 "Depending on the policy": determined in the two sub-configurations;
- K6 ACCEPT, K7 REJECT;
- K8 "Flag B2": accepted under L4, rejected under L4-YOL;
- K9 "Flag B3", K10 REJECT (L2/L3), K11 REJECT (G5);
- V+ ACCEPT, V− REJECT.

## 6. L4m and L4c (PR §2B item 6)

**L4m (multi-signature; a target that supports General JSON).**
- L4m exists if the target's documented API can implement the function of §3 by configuration. Criterion: K1 accept, K2 reject, K3 reject in the `L4` (or `L4-S`/`L4-Y`) rows.
- The K5 behaviour shows which sub-configuration it follows: B1 and B5.

**L4c (compact only).**
- A per-issuer policy is needed in the same verifier instance. Oracle rows:

| Criterion | Vector × configuration | Oracle |
|---|---|---|
| A document of the migrated issuer that is classical only → REJECT | `VPLUS_ES256` × L4; `VC10_ikili_ihrac` × L4 (K11); `VC01_ES256_x5c` × L4 | reject |
| A document of the migrated issuer signed with X → ACCEPT | `VPLUS_X`, `CMP00`, `VC02`, `VC03` × L4 | accept-* |
| The classical document of the old issuer → ACCEPT | `VPLUS_ES256`, `VC01`, `VC10` × IZIN-AX | accept-classical |

- **Battery limit:** v1.2 has no separate "old issuer" identity. There is a single `iss` (`https://issuer.example`) and a single ES256 issuer key (issuer/ES256). Two issuer records "in the same verifier instance" can be tested only by evaluating the same bytes with two separate policy records (`adapter-contract.md` §5.3; decision notes N-2).

## 7. The time dimension of G5 and limits

- **Window assumption:** in the L4 family the oracle assumes "the legacy-version window is closed". If the window were open, classical evidence could be accepted; this case corresponds to the `IZIN-AX` (R = ∅) rows. Since the battery carries no expectation with a sunset or a date, the G5-timed form is not tested in the library battery. This form is the subject of Steps 7 and 11.
- **Channel (P3 ↔ P4):** the channel through which R_I is learned is not represented in the vector. At library level P3 and P4 give the same decision. The adapter fixes R_I via the API (like a pinned anchor).
- **Certificate path:** L4 is at signature level. That the x5c path is PQ is a separate policy (`L4-YOL`, B2). Its basis is `yol_sinifi` of PR §2D item 13 and composite -04 §6.2 [T055]: "Because the certificate itself is protected by a composite signature, an attacker cannot forge a fake certificate…".
- **KB-JWT:** L4 is a policy on the issuer signature. In General JSON with several issuer signatures the KB `sd_hash` binding is undefined (UNDETERMINED B-2).

## 8. Metamorphic relations (self-check on the oracle; `karar_ozet.json` → `mr_oz_denetim`)

| Relation | Holds on the oracle? | Count |
|---|---|---|
| **MR1** (if the required set is not met, stripping must not increase acceptance) | under L4, L4-S, L4-Y in 4 arms T1 → accept, T3 → reject | 12/12 |
| **MR2** (the effect of adding an unknown alg is predictable) | under S, T7 → reject; under Y, T7 = T1 | 4/4 arms |
| **MR3** (flag if the decision changes with the version) | VC07, VC08, VC09 and VC09-ED25519: the same under -13 and -19 (`L4` / `L4@-19`; assuming JSON support). VC01 ↔ VC11: both accept-classical under -13; under -19 VC11 is reject (SHOULD level). This is the expected "version effect" | 6 vectors |
| **MR4** (the signature order must not change the decision) | The decision function is order-independent. 165 (permutation, configuration, arm) rows are identical to the source vector. VP05-SIRA-ters is outside MR4 (descriptive; the sd_hash binding changes) | 165/165 |
