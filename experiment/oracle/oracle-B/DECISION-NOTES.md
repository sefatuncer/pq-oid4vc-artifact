# NOTES — to the maintainers (Oracle B)

> Ambiguities, contradictions and implementation gaps in the pre-registration (PR v0.8, SHA-256 `dcc84092…`) observed during the oracle derivation. **The PR was not changed.** Each note: problem → what Oracle B did in this derivation → recommendation. Priority: **Y** (affects a pre-registered variable), **O** (affects descriptive output), **D** (low; clarity).
>
> (Quotations from the pre-registration are translated from Turkish; quotations from specifications are verbatim.)

---

## Y — Items that may affect pre-registered variables

**N1 — The semantics of the four-valued oracle output is not defined (Ö6).**
- *Problem:* Ö6 only gives the names (`accept-classical`, `accept-hybrid`, `reject`, `indeterminate`). (i) Which value is a pure PQ acceptance (K4 treatment: ML-DSA-65 only)? (ii) In the control arm X = EdDSA is classical; is K1-control "hybrid" or "classical"? (iii) What if the JWS signature is PQ but the certificate path has a classical edge (K8)?
- *Done:* `accept-hybrid` = acceptance + a valid component of PQ class (including pure PQ); every acceptance in the control arm is `accept-classical`; the label classifies only the JWS layer (`METHOD.md` §6.3).
- *Recommendation:* the semantics should be written before the PR is frozen. If the comparison uses a binary mapping (`accept-*` → accept), a label difference between A and B should not count as a decision difference.

**N2 — The V+ check contradicts the §6.5 policy.**
- *Problem:* §4.15: "V+: a single valid classical signature → ACCEPT". But under the §6.5 policy (R = {X}) and §2B item 6 (L4c: "A document of a migrated issuer signed only classically is rejected"), `VPLUS_ES256` must be **REJECT** (G5). If V+ is run while the adapter is in the L4 configuration, a sound adapter may be counted as "invalid" (§4.15 → the target leaves n_eff).
- *Done:* `VPLUS_ES256` → `L4`: reject; `P2`/`P0`: accept-classical. The row note carries a warning.
- *Recommendation:* fix the configuration of the V± check: R_I = ∅ ("old issuer", `P2`), or V+ signed with the X of the arm (`VPLUS_EdDSA`, `VPLUS_ML-DSA-65`, `CMP00`) — these are accepted in all three configurations.

**N3 — Side effect of the K8/K9 adaptation in the composite arm.**
- *Problem:* §2F item 4 realises K8 with "leaf ML-DSA-65, intermediate CA classical" (X5C04); the mapping counts X5C04 and X5C07 as primary in the composite column as well. Since the allowed set of the composite arm is {ES256, ML-DSA-65-ES256}, these ML-DSA-65-signed vectors are rejected by the allow-list in this arm; the B2/B3 behaviour **cannot be measured** in the composite arm.
- *Done:* in the composite arm both vectors are `reject` in all three configurations (reason: allow-list; for X5C07 also the unprotected x5c); note: "ADAPTATION SIDE EFFECT".
- *Recommendation:* count K8/K9, as the mapping also says, as arm-independent flags and measure them only with the policy X = leaf alg (ML-DSA-65); record the composite column as "not applicable". (The alternative — adding ML-DSA-65 to the allowed set of the composite arm — changes §6.5.)

**N4 — The handling of an extra signature (K5) under L4 is not explicit in the PR.**
- *Problem:* §6.5 K5: "Depending on the policy (MR2); flag B1". §4.13 L4: "reject if there is no PQ component" — silent about an extra (not allowed / unregistered) signature. Two reasonable readings: (a) cumulative §4.8 P3 (= P1 "ECCG AND" + binding + R_I) → K5 **REJECT**; (b) "once the required set is met, the extra is ignored" → K5 **ACCEPT**.
- *Done:* (a) was chosen (`L4-DERIVATION-B.md` §2 A5, §9 S2): the cumulative definition of §4.8, ACM v2 Note 51 "accepting if and only if all signatures are correct", 8725bis §3.1 "ensure that the received JWT complies". Under `P0` K5 is accepted → the MR2 policy dependence becomes visible.
- *Recommendation:* add an extra-signature rule to the L4 definition and write its relation to the three values of B1 (reject / ignore / verification falls through). If Oracle A reads (b), a divergence is expected in the 4 primary K5 rows (`T7K`, `T7K-ED25519`, `T7P`, `T7C`, `L4`) and in the K5 secondary rows.

**N5 — The mapping has no K1–K3 counterparts for L4c.**
- *Problem:* §2B item 6 defines Y_i with L4c for targets that support only compact serialization; but the §6.5 battery realises K1–K5 with General JSON, and `BATTERY-MAPPING.md` does not say which vectors give the behavioural criterion of L4c. It is unclear how F_K/F_T (which rest on K1–K3) are computed for a compact-only target.
- *Done:* the oracle gives the compact vectors under two issuer configurations (`L4-DERIVATION-B.md` §4).
- *Recommendation:* L4c mapping: K1c ≈ `VPLUS_X` @`L4` (ACCEPT), K2c ≈ `VMINUS_X` @`L4` (REJECT), K3c ≈ `VPLUS_ES256` @`L4` (REJECT; migrated issuer), old-issuer check ≈ `VPLUS_ES256` @`P2` (ACCEPT); in the composite arm `CMP00` / `CMP01`.

**N6 — Which oracle is used for the B5 classification?**
- *Problem:* §6.4 defines F_K/F_T against the L4 oracle "in the best reachable configuration"; no comparison criterion is written for B5 (at least one valid / all present valid / required set / other).
- *Done:* the three configurations were derived so that they correspond one-to-one to the three classes of B5 (`P0`, `P2`, `L4`).
- *Recommendation:* B5 = the column with which the target's K1, K2, K3 (and K5) behaviour coincides; none → "other".

## O — Items that affect descriptive output

**N7 — The legacy-version window of G5 is not a parameter in C3.** The K3/K11 REJECT decisions assume "a migrated issuer whose window has closed"; while the window is open the correct decision is the `P2` column (`L4-DERIVATION-B.md` §5). The PR should state this assumption explicitly.

**N8 — The `sdjwtvc_surum` dimension.** §2D item 7 limits the scope to "scenario (d) vectors ... and VC11". In these vectors the oracle split every configuration into `|sdjwtvc=-13` / `|sdjwtvc=-19`; under `-19` the acceptance rows with JSON serialization are `indeterminate` (UNDETERMINED B2). (i) How will the MR3 criterion "if the decision changes" count a determined ↔ undetermined transition? (ii) The flattened JSON vectors (X5C07/08/09, CRIT02; including the K9 primary) are defined in the manifest only for `-13`; how are they run on a target set to `-19`? (iii) HAIP §9.4 pins SD-JWT VC to -13; which is the primary version?

**N9 — Key resolution path in the X5C family.** §2D item 1 says "the verification key is given in all arms through the target's documented API (JWK/JWKS or a direct key)", but "chain behaviour is measured only on the X5C vectors". In the X5C family Oracle B assumed resolution **via x5c**. The REJECT decision of K9 (X5C07) depends on this: if the key is given from the JWKS and the unprotected x5c is ignored, acceptance is also consistent with RFC 7515 §6 ("if the only information used in the trust decision is a key, these parameters need not be integrity protected"). The path should be written explicitly in the adapter contract.

**N10 — K10 "REJECT (L2/L3)".** Under 8725bis §3.1 alg–key consistency is a **library** MUST; rejection is expected in every configuration (including P0). The phrase "(L2/L3)" can be read as expecting the rejection only in an L2/L3 configuration; it should be clarified.

**N11 — The 46 vectors outside the mapping and the R_I analogy.** For the REQ (RP), TSL (status issuer) and DPoP (client; RFC 9449 §4.3(5) "acceptable per local policy") vectors, R_I was applied by analogy. The PR does not say how vectors outside the mapping are reported (§2G item 4 says only "secondary vectors are descriptive").

**N12 — Which copy is evaluated in K11.** The mapping note evaluates VC10.credentials[0]; whether a target processes the two copies in the batch response separately depends on the adapter. "credentials[0]" should be written explicitly in the adapter contract.

**N13 — Reading of L4 in the control arm.** §4.13 L4 says "reject if there is no PQ component"; in the control arm (X = EdDSA) this must be read as "reject if there is no X component" (it follows from §3.7 but is not written explicitly). Oracle B read it this way.

## D — Clarity / statement

**N14 — PR version.** `BATTERY-MAPPING.md` quotes PR v0.6 (`c239d423…`); Oracle B read PR v0.8 (`dcc84092…`). The items used (§6.5, §4.13, §4.20, §2B items 6–8) are identical to the quotes in the mapping.

**N15 — The "specification ambiguity" label of CMP10.** The normative Table 5 (pre-hash of ML-DSA-65-ES256 is SHA512) determines the decision (REJECT); the "SHA-256" in the IANA description of -04 §7.1.2 is the inner hash of the ECDSA component. The oracle did not count this as undetermined; it stays in the descriptive class D-S5 "wrong pre-hash".

**N16 — MR4 and SD-JWT VC.** In the SD-JWT VC permutations the disclosures were moved to the new first header (consistent with RFC 9901 §8.3); Oracle B bound the MR4 twins to the same decision as their sources. `VP05…-SIRA-ters` is outside MR4 and undetermined because of B1.

**N17 — Reading statement.** While reading the requested §2D items 1–8, part B (items 9–17, formal results) appeared in the same chunk; it was not used in the derivation. The `not` column of the first 8 rows of the traceability matrix appeared in the `head` output (LOTL/TL; unrelated). Details in `ACCESS-LOG.md`.
