# Blind derivation: expected values of KAT-1/2/3 (kat-kor, Step 6 task 0)

> The values were derived only from the cell definitions in `GIRDI/KAT-BLIND-INPUT.md` (originally `GIRDI/KAT-KOR-GIRDI.md`) and from the primary sources. No model, draft code or table of the first work was seen; no tool was run. The line numbers in the primary sources are in the `satir` column of `BEKLENEN-KOR.tsv`. Label: [Y] my own inference.
>
> (Translated from Turkish for this release; "l." = line of the primary text file. Quotations from RFCs and papers are verbatim. The original file, whose hash is recorded in `SHA256SUMS`, is listed in `docs/INTEGRITY.md`.)

## 0. Shared interpretation decisions

### 0.1 Time constants (`now`, `qday`, `tau`, `exposure`)

The input file does not give these numerical values; they were removed together with the draft code:
- the default values of `now`, `qday`, `tau` and `exposure`,
- the signature validity intervals of the versions (`version(I,V,Inc,Exp)`).

The only explicit time definition in the input is in KAT-3b: "`qday=0` (all classical keys broken)" and "`qday=200` (no CRQC)". Therefore:

1. **The numerical interaction is undetermined for this work.** Which version's signature is valid at which `now`, or how much τ delays the moment of breaking, cannot be read from the input.
2. **I derived the values from the logical state.** The logical state is encoded by the Tamarin flags of the cell (CRQC yes/no, whether the old DS or DNSKEY version is usable). The rationale is in input §0:
   - criterion 2: "A logical cell is a cell whose time is represented only by a flag",
   - criterion 3: ASP and Tamarin must agree 100% in the shared cells.

   So the flag set is the logical projection of the ASP constants [Y].
3. **Default (if no `qday` is given in the cell):**
   - The CRQC is active and all classical keys are broken at time `now`. This is an analogy with the "qday=0" definition in KAT-3b [Y]. Its Tamarin counterpart is the absence of the flag `NO_QDAY`.
   - PQ keys do not break.
   - A `comp` key breaks only if all its components break (input §1.1). Hence composite does not break under the CRQC.
4. **τ:** Tamarin does not model τ (input §1.4). If τ > 0 and the moment a classical key breaks (max(qday, exposure) + τ [Y]) exceeds the `now` value of the cell, the ASP value of that cell may turn from SALDIRI (attack) to YOK (no attack). This conditional dependency is listed in `UNDETERMINED.md` §B.

### 0.2 Value mapping and attacker

- **Value mapping:** SALDIRI in ASP ⟺ the all-traces authentication lemma in Tamarin falsified, because the attack trace is a counterexample to the lemma.
- **Attacker:**
  - Dolev-Yao network attacker: selects, drops and replays responses.
  - CRQC: forges signatures with a broken classical key.
  - Can generate its own key (input §2(c) Note: "The attacker can generate its own key").
  - Can replay an old signed version as long as its signature stays valid (RFC 6781 §4.3.4).
- **Channel (input §1.1):** in KAT-1 the transport is unauthenticated. The attacker itself chooses which RRSIGs are present in the response.

---

## 1. KAT-1 DNSSEC

### 1.1 Semantics

**Stages.** RFC 6781 §4.1.4, Figure 8 lists six stages: initial, new RRSIGs, new DNSKEY, new DS, DNSKEY removal, RRSIGs removal.
- In the cells `r3` always comes with the flag DS_PQ. In Figure 8 the DS moves to the new key only in the "new DS" stage (lines 1566–1572: `DS_K_2`, `RRSIG_par(DS_K_2)`).
- From this the numbering comes out 0-based [Y]: r0 initial, r1 new RRSIGs, r2 new DNSKEY, r3 new DS, r4 DNSKEY removal, r5 RRSIGs removal.
- With a 1-based reading r3 would be new DNSKEY. In that stage the DS is still `DS_K_1` (classical), so this reading contradicts the flag DS_PQ.
- The results are insensitive to the numbering: r2 is DS_CL in both readings, and in r5 the DNSKEY RRset contains only Q keys in both readings.

**Keys.**
- Algorithm 1 classical (C): `K_1`, `Z_10`. Algorithm 2 PQ (Q): `K_2`, `Z_11`.
- **DK3:** the DNSKEY RRset containing the keys of both algorithms, {K_1, K_2, Z_10, Z_11} (Figure 8 lines 1558–1563).
- **DK5:** the RRset containing only the Q keys, {K_2, Z_11} (lines 1580–1582).
- **DK3_USABLE:** DK3 is usable; it is either current or an old version whose signature is still valid.
- **`dds`:** Double-DS stage. The parent zone publishes `DS_K_1` and `DS_K_2` together (RFC 6781 §4.1.2, Figure 5, lines 1307–1308) → DS_BOTH.
- **Parent zone key:** I took the default to be PQ, because K1-12 gives the deviation `parent_class=cl` separately [Y].

**Policies.**
- **`anyvalid`:** RFC 6840 §5.11 "Validators SHOULD accept any single valid path" (l. 594–595). Also §5.4 "accept any valid RRSIG as sufficient" (l. 446–448) and Appendix C.2 (l. 1027–1044).
- **`required`:** signature completeness test. §5.11 defines this test as the validator choosing to "insist that all algorithms signaled in the DS RRset work" (l. 595–599).
  - The required classes are the algorithms signalled by the DS (input §1.1: `signal_s/3`, `signal_v/4` = "algorithms signalled by the DS").
  - The algorithms in the DNSKEY RRset are not made required (§5.11: "MUST NOT insist that all algorithms signaled in the DNSKEY RRset work").
- **`allpresent`:** P1, "opportunistic: check if present" (policy mapping of input §1.1; DNSSEC column "—"). Every RRSIG present in the response is verified; an absent one is tolerated.
- **`monotone=1`:** "refusing to go back within the RRSIG validity" (input §1.1). The validator has seen the newest version (`seen`) and rejects an older one [Y].

**Tamarin lemma `a_rrset_authentic`:** the accepted A RRset is the RRset published by the honest zone. If there is an attack trace, the lemma is falsified.

### 1.2 Cell-by-cell derivation

| Cell | State | Determining rule (primary) | ASP | Tamarin |
|---|---|---|---|---|
| K1-01 | r2, DS=K_1 (C), anyvalid | The chain DS→K_1→DNSKEY→Z_10→A is entirely classical; the CRQC breaks K_1 (or Z_10). RFC 6781 §4.2.1: "vulnerable as long as … a DS record in the parent zone points to it" | SALDIRI | falsified |
| K1-02 | r2, DS=K_1, required | The DS signals only C. The completeness test requires only C; a forged C signature satisfies it. §4.2.1 the same; RFC 6840 §5.11 (l. 570–571: the DS "signal[s] which algorithms") [Y] | SALDIRI | falsified |
| K1-03 | r3, DS=K_2 (Q), DK3 current, anyvalid | DS→K_2 validates the real DK3. Z_10 remains in DK3; RFC 6840 §6.2: "any DNSKEY in the zone's signed DNSKEY RRset may be used to authenticate any RRset". A forged A with Z_10 is accepted | SALDIRI | falsified |
| K1-04 | r3, DS=K_2, required | The completeness test requires the Q signalled by the DS to work (§5.11 l. 595–599). A forged A RRset cannot carry a valid Q signature. Since the parent zone is PQ, the DS cannot be forged either | YOK | verified |
| K1-05 | K1-04 + now=50, OLD_DS_REPLAY | The parent zone signature of the old DS_K_1 is still valid. RFC 6781 §4.3.4: "the DS can be replayed as long as it has a valid signature". The replayed DS signals only C, and the completeness test requires only C | SALDIRI | falsified |
| K1-06 | K1-05 + monotone=1 | The monotone validator has seen the new DS version and rejects the old DS [Y]. The state reduces to K1-04 | YOK | verified |
| K1-07 | r5, DK5 current + DK3 old but its signature valid, anyvalid | The old DK3 is validated with DS→K_2 because its K_2 signature is valid, and the Z_10 in it can be used. RFC 6781 §4.2.2: "until the RRSIG over the compromised ZSK has expired, the zone may still be at risk"; §4.2.1.1 (l. 1893–1895) "upper limit on how long the compromised KSK can be used in a replay attack" | SALDIRI | falsified |
| K1-08 | K1-07 + monotone=1 | The validator has seen DK5 and rejects the old DK3. The current DK5 has no Z_10; RFC 6840 §5.12: "MUST disregard RRSIGs … that do not (currently) have a corresponding DNSKEY" | YOK | verified |
| K1-09 | r5, now=150, DK5 only | The signatures of DK3 and of the old DS have expired (no DK3_USABLE and no OLD_DS_REPLAY in the flags). The classical key is on no valid path; §5.12 excludes the forged Z_10 signature. The window is closed (§4.2.2 "until … has expired") | YOK | verified |
| K1-10 | dds, DS={K_1,K_2}, anyvalid | In Double-DS, DS_K_1 still points to K_1 (§4.1.2 l. 1307–1308). §4.2.1 "a DS record in the parent zone points to it"; under anyvalid a single valid path is enough | SALDIRI | falsified |
| K1-11 | dds, required | The DS signals both algorithms. The completeness test also requires Q (§5.11 l. 595–599); there is no Q signature for the forged A | YOK | verified |
| K1-12 | r3, required, parent zone classical | The broken parent zone key signs a forged DS (signalling C or the attacker's own key). Once the signal is forged, the completeness test requires only C. RFC 6781 §4.2.1 (l. 1842–1843): "A compromised KSK can be used to sign the key set of an attacker's version of the zone"; this sentence was applied to the parent zone [Y] | SALDIRI | falsified |
| K1-13 | r3, anyvalid, qday=200 | No CRQC (NO_QDAY), no key compromised. The weakness of §4.2.1 arises only with a "compromised" key [Y] | YOK | verified |
| K1-14 | K1-09 + extra_ta=1 | The extra trust anchor was interpreted as the old classical anchor [Y] (see 1.4). RFC 6840 Appendix C.2: "subject to the compromise of the weakest of these trust anchors … keep old trust anchors configured in perpetuity"; RFC 6781 §4.2.1: "vulnerable as long as the compromised KSK is configured as the trust anchor" | SALDIRI | falsified |
| K1-15 | r3, allpresent | RRSIGs are separate records; the attacker sends the forged A with only the forged Z_10 RRSIG. Every signature present is valid, and the absence of Q is tolerated. RFC 9955 §6.2: "if a system does skip a component signature, security does not rely on the security of all component signatures" | SALDIRI | falsified |

### 1.3 Time interaction (KAT-1)

- **K1-05 (`now=50`):** I inferred from the flag OLD_DS_REPLAY that the signature of the old DS is still valid at 50. The numerical interval is not in the input.
- **K1-07/K1-08 (default `now`):** I inferred from the flag DK3_USABLE that the K_2 signature of the old DK3 is still valid.
- **K1-09/K1-14 (`now=150`):** the flags contain no DK3_USABLE and no OLD_DS_REPLAY. From this I inferred that the signatures of DK3 and of the old DS have expired at 150.
- **K1-13 (`qday=200`):** inference from the flag NO_QDAY: default `now` < 200 and no CRQC.
- **τ and `exposure`:** not given in the KAT-1 cells. The SALDIRI value of K1-05 depends on K_1 or Z_10 having been broken before `now=50`. So max(qday, exposure) + τ ≤ 50 must hold [Y]. This condition is the state encoded by the Tamarin flags; it could not be verified numerically (UNDETERMINED.md §B).

### 1.4 Interpretation decisions (KAT-1)

1. **K1-14 `extra_ta` was interpreted as the old classical anchor.** The cell definition does not give the class of the anchor.
   - The result to be reproduced is the sentences "weakest of these trust anchors" and "old trust anchors configured in perpetuity" of RFC 6840 Appendix C.2. In a C→Q rollover the old anchor is classical.
   - If the anchor were PQ, the cell would be a copy of K1-09.
   - The source gives a single result for a classical anchor: SALDIRI.
2. **K1-15 `allpresent` was interpreted as "every RRSIG present in the response is verified".** The input mapping defines it as "opportunistic: check if present".
   - Alternative reading: "every algorithm in the DNSKEY RRset is required" (the "conservative approach" in RFC 6781 §4.1.4, l. 1477–1480). With this reading the value would be YOK.
   - I rejected this reading because: the input mapping gives "—" as the DNSSEC counterpart of `allpresent`; the policy that corresponds to the signature completeness test is already `required`; RFC 6840 §5.11 tells the validator "MUST NOT insist that all algorithms signaled in the DNSKEY RRset work".
3. **Monotonicity.** In the `monotone=1` cells it was assumed that the validator has seen the newest version (DS_K_2 or DK5). If it had not (first contact), K1-08 would be SALDIRI. This assumption comes from the definition "refusing to go back" in input §1.1.
4. **Forged ZSK path.** The completeness test requires the algorithms signalled by the DS along the whole chain, including the A RRset [Y]. RFC 6840 does not detail this test; it says only "insist that all algorithms signaled in the DS RRset work". If the test were done only on the DNSKEY RRset, a forged A with Z_10 would be accepted in the cells K1-04/06/11 and the value would be SALDIRI. I chose the first reading because the verb "work" expresses that the algorithm works on the validation path (UNDETERMINED.md §B).

## 2. KAT-2 X.509 hybrid

### 2.1 Semantics and vocabulary mapping

**Primary sources:**
- Kim et al. (`kim2026_x509_hybrid.txt`): §II-B designs, §III attackers M1/M2, §IV-B policies P0–P3, §IV-D five observation results, Tables IV/V/VI/VII.
- Lee et al. (`lee2026_eprint1416.txt`): §4.1, §4.3, §4.4, §6.

**Result vocabulary.** Kim uses two vocabularies:
- **observation:** classical-accept, hybrid-verified, loud-fail, identified-but-not-enforced,
- **contract:** accept-classical, accept-hybrid, reject, indeterminate (l. 130).

The value vocabulary is the contract vocabulary. I mapped observation to contract as follows [Y]:
- classical-accept and identified-but-not-enforced → `accept_classical`. Basis l. 130: "a contract result of accept-classical is a statement that such an acceptance is all the policy permits us to report". The default path arrow of Figure 1 also says "→ Accept-classical ✓" (l. 364).
- hybrid-verified → `accept_hybrid`.
- loud-fail → `reject`. Basis l. 101: "cannot parse or process the structure and rejects".

**`vb` values (mapping of input §3(b)) and the behaviours in the source:**

| vb | Policy | Behaviour in the source |
|---|---|---|
| `ignore` | P0 | classical-accept (Kim l. 102) |
| `parse_no_enforce` | P0 | identified-but-not-enforced (Kim l. 103, l. 296) |
| `enforce_if_present` | P1 | wolfSSL type: verifies if present, cannot make it required (Lee l. 121; Kim §VI-D l. 306) |
| `require` | P2 | "both classical and post-quantum evidence must be present and valid" (Kim l. 90) |
| `continuity` | P3 | "an identity previously established as hybrid may not silently regress to classical-only" (Kim l. 90). The mapping of input §1.1 ties P3 to `monotone=1` |
| `legacy_oid` | — | a verifier that does not recognise the composite OID → loud-fail (Kim l. 43, l. 101; Lee l. 99 "each rejects the others’ OID") |

**Attackers:**
- **M1 (withholding):** "It cannot forge a classical signature … so every certificate it presents was issued by a real authority" (Kim l. 60). It only "presents a legitimately issued classical-only certificate … and withholds the post-quantum one" (l. 66).
- **M2 (CRQC):** "can forge RSA or ECDSA signatures, including a certification authority’s, but not a post-quantum signature such as ML-DSA" (l. 61).

**Scope.** According to input §1.1 the anchor is CA→ee: "end-entity coverage only; Kim's test coverage". Therefore the warning in Kim l. 444 does not apply in these cells: "if a classical issuer signature is forgeable, post-quantum evidence at the leaf alone does not establish hybrid authentication". There is no intermediate CA; the alternative (PQ) public key of the CA is part of the anchor configuration [Y].

### 2.2 KAT-2a: honest decision (no attacker; `hon_decision`)

Row labels such as `KAT-2a-01/02` were expanded into individual cell ids: 01 = first `pqev` value, 02 = second value. 09…11 and 12…14 = valid / invalid / absent.

| Cell | scheme, vb, pqev | Rule | Decision |
|---|---|---|---|
| K2a-01 | catalyst, ignore, valid | The classical path is validated, the PQ evidence is not looked at (l. 102) | accept_classical |
| K2a-02 | catalyst, ignore, invalid | "In all 27 the two verdicts were identical" (l. 238); Lee §4.3 the same (l. 99) | accept_classical |
| K2a-03 | catalyst, parse_no_enforce, valid | IBNE: "does not let the evidence affect the outcome" (l. 103); acceptance rests on the classical evidence (l. 241) | accept_classical |
| K2a-04 | catalyst, parse_no_enforce, invalid | "in each the invalidated variant was accepted exactly as the valid one was" (l. 296) | accept_classical |
| K2a-05 | chameleon, ignore, valid | Chameleon row of Table IV: C-Acc in 6 of 8 stacks. Lee l. 128: "its non-critical delta likewise ignored" | accept_classical |
| K2a-06 | chameleon, ignore, invalid | In the 25 acceptance cells the invalid variant was accepted under the same condition (l. 239). The "Unsup" cell of NSS is a non-informative cell (input §3(a)); the `ignore` semantics does not change this | accept_classical |
| K2a-07 | related, ignore, leafB valid | Control row of Table V, default path classical-accept (l. 324, 386) | accept_classical |
| K2a-08 | related, ignore, leafB revoked | "revoking that certificate changes no verdict" (l. 29); Table V (l. 386) | accept_classical |
| K2a-09 | catalyst, enforce_if_present, valid | The enforcing build "accepts a valid alternative signature" (l. 306); Table VI P1 valid column accept-hybrid | accept_hybrid |
| K2a-10 | catalyst, enforce_if_present, invalid | Lee l. 121: "does verify a present alt-signature – a leaf with a forged ML-DSA alternative signature is rejected"; Kim l. 306 "rejects a forged one" | reject |
| K2a-11 | catalyst, enforce_if_present, absent | Lee l. 121: "a stripped classical-only leaf … is accepted"; Kim l. 445: P1 tolerates absence | accept_classical |
| K2a-12 | catalyst, require, valid | Definition of P2 (l. 90); Table VI P2 valid column accept-hybrid | accept_hybrid |
| K2a-13 | catalyst, require, invalid | Table VI P2: "non-accepting: reject, or indeterminate if status is unknown" (l. 429). No status uncertainty → reject | reject |
| K2a-14 | catalyst, require, absent | "Reject is returned when a required certificate is invalid or absent" (l. 443) | reject |
| K2a-15 | composite, require, valid | In composite the evidence is inside the single signature and affects the decision (l. 437); Table VII; Table IV BC composite = HV | accept_hybrid |
| K2a-16 | composite, require, invalid | Lee l. 99: "corrupting either the ML-DSA or the classical component … is rejected" | reject |
| K2a-17 | composite, legacy_oid, valid | "does not recognize the algorithm identifier and fails to process the certificate" (l. 43); loud-fail rejects (l. 101); composite row of Table IV LF in 7 of 8 stacks | reject |

**Interpretation decisions (2a):**

1. **K2a-10: reject.**
   - Kim Table VI says "accept-classical permitted; never accept-hybrid" for the "invalid, absent, or unsupported" column of P1. With this reading the value would be accept_classical.
   - I chose reject because: (i) the `vb` name of the cell says enforcement, and Kim's definition of "outcome-bearing" is "a failure in it would turn an otherwise accepting result into a non-accepting one" (l. 97); (ii) Kim's definition of P1 tolerates only absence: "check … when it is present, tolerate its absence" (l. 90); (iii) the verifier that shows this behaviour rejects in the measurement (Lee l. 121, Kim l. 306).
   - "permitted" in Table VI is a permissive modality; it does not forbid rejection (the condition "never accept-hybrid" is also met by rejecting).
   - The risk is in UNDETERMINED.md §B.
2. **K2a-17.** `legacy_oid` was read as "(old) verifier that does not recognise the composite OID". The result is the same under the reading "a different composite OID family", because according to Lee l. 99 the families "each rejects the others’ OID". The value is reject in both readings.
3. **Pairing of valid/invalid.** Kim's finding on the default path is an observation. The behaviour definitions of `ignore` and `parse_no_enforce` in the model give the same result structurally (l. 54: "a verifier can complete classical path validation without processing the post-quantum evidence").

### 2.3 KAT-2b: M2 (forgery with a CRQC)

- **Evidence classes:** Catalyst CA key = classical base signature + PQ alternative signature. A composite key is in class `comp`; it breaks only if all its components break (input §1.1). The CRQC does not break ML-DSA.
- **`coexist_cl=1`:** there is also a separate classical path for the same identity that the verifier trusts [Y]. Example: a parallel classical CA or a classical certificate during the transition period.
- **`expect_src`:** `local` = local P2. `tl_cl` / `tl_pq` = the expectation is carried by a TL signed with a classical / PQ key (policy mapping of input §1.1: "P3 (classical source) / P4 (PQ source)").

| Cell | State | Rule | ASP | Tamarin `cert_authentic` |
|---|---|---|---|---|
| K2b-01 | catalyst, anyvalid (P0) | M2 forges the classical signature of the CA, "can construct certificates that validate classically without any authority having issued them" (Kim l. 61). P0 does not look at PQ | SALDIRI | falsified |
| K2b-02 | catalyst, allpresent (P1) | M2 builds a purely classical leaf without the alternative extension, with a forged CA signature. "a stripped classical-only leaf … is accepted" (Lee l. 121); P1 tolerates absence (Kim l. 445) | SALDIRI | falsified |
| K2b-03 | catalyst, required, local | P2 requires a valid PQ alternative signature; M2 "not a post-quantum signature such as ML-DSA" (Kim l. 61). Since the anchor is CA→ee, the issuer's alternative public key cannot be forged | YOK | verified |
| K2b-04 | catalyst, required, tl_cl | The TL that carries the expectation is classically signed. M2 forges it and deletes the expectation [Y]. The rule becomes empty and the state reduces to K2b-01. Kim l. 433–434: the risk of P3 "depends on where that state comes from" | SALDIRI | (ASP only) |
| K2b-05 | catalyst, required, tl_pq | The TL is PQ-signed and cannot be forged (Kim l. 61). The expectation is real; the state reduces to K2b-03 | YOK | (ASP only) |
| K2b-06 | composite, anyvalid, coexist 0 | "There is no path through which it accepts while disregarding the post-quantum component" (Kim l. 43). `comp` does not break, no classical path | YOK | verified |
| K2b-07 | composite, anyvalid, coexist 1 | The parallel classical path is forged with M2, and anyvalid considers a single path sufficient. Lee l. 272: "no encoding alone defeats a full classical downgrade"; l. 173: "Composite included" | SALDIRI | falsified |
| K2b-08 | composite, required, local, coexist 1 | Lee l. 78: "no encoding prevents without a require-PQC policy". Here that policy exists: the classical path is rejected and composite cannot be forged | YOK | (ASP only) |

**Interpretation decisions (2b):**

1. **K2b-04/05.** The TL is not versioned (input §1.1: `version` is "—" in KAT-2). Therefore there is no path that replays an old TL.
   - The attacker dropping the TL entirely (validation without a TL) is not the only way to delete the expectation in the model. What does the verifier do without a TL? The input does not say.
   - The value YOK for `tl_pq` rests on this assumption: the signal can be removed only by forging its source [Y].
2. **Tamarin rows.** No Tamarin rows were written for the `(ASP only)` cells.

### 2.4 KAT-2c: Related, leafB state × {ignore, require}

Read directly from Kim Table V (l. 374–398). In the table the rows (l. 384) and the columns (l. 386, 388) are dumped column by column; the alignment was verified with the footnotes in l. 393–398.

| leafB | vb=ignore (default path) | vb=require (P2 reference) | Basis |
|---|---|---|---|
| revoked | accept_classical | reject | Table V; l. 443 "revoked, expired, or not presented" |
| expired | accept_classical | reject | the same |
| unknown (OCSP) | accept_classical | indeterminate | l. 327: "returns indeterminate; treating unknown as a rejection would assert a status the verifier does not have" |
| absent | accept_classical | reject | l. 327: "An absent peer certificate leaves a required certificate missing, so the procedure rejects" |
| valid (control) | accept_classical | accept_hybrid | l. 324–326: the default path accepts classically; "The policy rules return a hybrid result for that row" |

- The "classical-accept" observation of the default-path column was written as `accept_classical` (see 2.1).
- Invariance: "the default verdict does not change with leafB’s state" (l. 322).

### 2.5 KAT-2d: P0–P3, M1 withholding

**Evidence state.** No `pqev` is given in the cell. I interpreted the state as "PQ evidence withheld (absent)" [Y], for two reasons:
- `seen_hybrid` can change the decision only when the evidence is absent. If the evidence is valid, P1–P3 all give accept-hybrid (Table VI) and `seen_hybrid` becomes meaningless.
- Input §3(a) quotes Kim's M1 sentence for KAT-2d (l. 445).

| Cell | Policy | Rule | ASP decision | Tamarin |
|---|---|---|---|---|
| K2d-01 | P0 | "P0 (legacy): classical path validation only" (l. 89). Table VI P0 accept-classical in both columns | accept_classical | undetermined |
| K2d-02 | P1 | "Under M1, P1 provides no more protection than P0 … the result is accept-classical" (l. 445) | accept_classical | undetermined |
| K2d-03 | P2 | "Reject is returned when a required certificate is invalid or absent … or not presented" (l. 443); Table VI P2 | reject | undetermined |
| K2d-04 | P3, seen_hybrid=1 | "a later accept-classical for an identity recorded as hybrid-required is itself non-accepting" (l. 429). Withheld evidence "not presented" → reject (l. 443) | reject | (ASP only) |
| K2d-05 | P3, seen_hybrid=0 (first contact) | Definition of P3: "an identity previously established as hybrid may not silently regress" (l. 90). If no identity was established as hybrid before, there is no regression either → classical acceptance [Y] | accept_classical | (ASP only) |

(In `BEKLENEN-KOR.tsv` the undetermined Tamarin values are recorded as `belirsiz`.)

**Interpretation decisions (2d):**

1. **K2d-05.** The P3 row header of Kim Table VI is "P3 (hybrid + continuity)". This header can also be read as P3 containing P2; under that reading reject also comes out at first contact.
   - I chose accept_classical for these reasons:
     - the mapping of input §1.1 ties P3 only to the monotonicity component (`monotone=1`; in KAT-1 a flag independent of `required`);
     - Kim's §IV-B definition forbids only regression;
     - the note of Table VI says that P3 presupposes an external continuity state ("presupposes an external continuity state", l. 431), and §VIII-D limits the P3 condition to "an identity the inventory records as hybrid-required" (l. 452).
   - The risk is in UNDETERMINED.md §B.
2. **K2d Tamarin (01–03) undetermined.** The value vocabulary names the lemma for KAT-2b (`cert_authentic`) but not for KAT-2d. According to input §1.4 the KAT-2 file has two candidates: an authentication lemma (all-traces) and a sensitivity lemma (exists-trace). The candidates give different results (UNDETERMINED.md §A1).


## 3. KAT-3 S/MIME

Primary source: Das and Chattopadhyay (`das2026_smime_eprint1374.txt`) §3 and §3.1.

**Basic rules:**
- **Equation (8)** (l. 149): Accept(ED, P_t) = 1 ⟺ ∀i ∈ R, V_i(t) = 1 ⇒ χ_i(t) ∈ A_t.
  - V_i is certificate validity and also covers "policy constraints" (l. 142).
  - Only valid paths are classified: "Assign each valid CEK path to …" (Figure 3, l. 181).
- **Stage 3, path classes** (l. 190):
  - ML-KEM (approved OID) → PQC.
  - Recognised hybrid KEM → "Hybrid only when the policy explicitly permits the construction".
  - RSA KeyTrans and ECDH KeyAgree → Classical.
  - "Unsupported OIDs … are classified as Unknown".
  - "mandatory profile violations are classified as Invalid".
  - "Unknown mechanisms fail closed".
- **Stage 4, modes** (l. 191):
  - strict-PQC: A_t = {PQC}.
  - transitional-hybrid: A_t = {PQC, approved Hybrid}, but it "still rejects an independent standalone classical fallback to the same CEK".
- **Stage 5, precedence** (l. 205): "malformed artifacts are rejected as invalid; unsafe mixed-mode exposure is reported before weaker uncertainty labels; and unknown mechanisms fail closed".
- **Table 1** (l. 199–203): definition of the six message classes.

### 3.1 KAT-3a: literal CMS classification (o1…o12)

**In which mode is `out` computed?** The cell has a single `out` column.
- I read the class from the definitions of Table 1. Whether the hybrid KEM is approved is stated by the vector label ("(approved)" / "(not approved)") [Y].
- The acceptance columns apply Equation (8) with the A_t set of the two modes.

| Vector | Path classes (valid paths) | `out` (rule) | strict | transitional |
|---|---|---|---|---|
| o1 | PQC | pqc_protected (Table 1: "Every valid recipient path to the CEK is classified as PQC") | 1 | 1 |
| o2 | PQC, PQC | pqc_protected | 1 | 1 |
| o3 | Classical | classical_only (Table 1) | 0 | 0 (Classical ∉ A_t) |
| o4 | PQC, Classical | unsafe_mixed (Table 1: "At least one valid PQC or hybrid path coexists with at least one independent valid classical path") | 0 (l. 162) | 0 ("still rejects an independent standalone classical fallback") |
| o5 | Hybrid (approved) | hybrid_protected (Table 1) | 0 (strict PQC only) | 1 |
| o6 | Hybrid, Classical | unsafe_mixed (hybrid counted as approved [Y]) | 0 | 0 |
| o7 | PQC, Unknown | unknown (Stage 3 "Unsupported OIDs … Unknown"; Table 1 unknown; pqc-protected requires "no … unknown fallback path") | 0 | 0 (fail closed) |
| o8 | PQC (rsa_kt path V=0, out of scope) | pqc_protected (the V_i ⇒ condition of Equation (8); Table 1 speaks of "valid" paths) | 1 | 1 |
| o9 | cannot be parsed | invalid (Stage 5: "malformed artifacts are rejected as invalid"; Stage 1: "rejects malformed objects") | 0 | 0 |
| o10 | not Hybrid (not approved) → Unknown | unknown (Stage 3 "Hybrid only when the policy explicitly permits"; fail closed) | 0 | 0 |
| o11 | PQC, Hybrid (approved) | hybrid_protected (pqc-protected requires "no … hybrid … fallback") | 0 (l. 205: "only when every valid CEK-recovery path is positively classified as PQC") | 1 |
| o12 | Classical, Classical | classical_only | 0 | 0 |

**Interpretation decisions (3a):**

1. **o8 as written.** Under Das's rule the path with an invalid certificate (V=0) is outside the evaluation → pqc_protected, 1, 1.
   - The reading note in the input marks this vector as a "model difference": an attacker with a CRQC can extract the CEK from the RSA RecipientInfo regardless of certificate validity (the RecoverCEK of Proposition 1 does not look at V_i).
   - This difference will be reported separately. The expected value is Das's literal rule.
   - The class "invalid" (Table 1: "violates a mandatory … certificate … requirement") was not applied to o8, because Das explicitly separates certificate validity from path classification (l. 143: "We separate certificate validity from recipient-path classification").
2. **o10 → unknown.** By Stage 3 an unapproved hybrid does not enter the class Hybrid. Das does not state explicitly which class it enters.
   - "Unsupported … are classified as Unknown" and "fail closed" are the closest rules; "invalid" is only for mandatory profile violations and malformed structure.
   - The acceptance values (0, 0) are the same under both readings; only `out` may change (UNDETERMINED.md §B).
3. **The hybrid in o6 was counted as approved.** There is no label. o6 is the hybrid counterpart of o4 and tests the "standalone classical fallback" sentence of the transitional mode; for this test to be meaningful the hybrid must be approved.
   - If it were not approved, the path set would be {Unknown, Classical} and `out` would come out unknown. The acceptance values are 0 in both cases.
4. **Acceptance values of o9.** For a malformed object the ∀ quantifier of Equation (8) would be vacuously true on the empty set. But Stage 1 rejects the object before the policy evaluation → acceptance 0.

### 3.2 KAT-3a Tamarin `cek_secrecy`

The Tamarin pattern has the rules `rule Qday` and `Break_*` (input §1.4). The CRQC moment can come in every trace; the threat is the HNDL attacker of Das §3 (l. 127).

| Flag | Configuration [Y] | Rule | Value |
|---|---|---|---|
| MIXED | ML-KEM + RSA/ECDH recipient to the same CEK | Proposition 1 (l. 159): "the confidentiality level of ED is bounded by the weakest valid recipient path protecting K"; the classical path is opened with the CRQC | falsified |
| PQ_ONLY | ML-KEM only | The single path is PQC; the CRQC does not break ML-KEM | verified |
| HYBRID_KEM | hybrid KEM only (ECDH + ML-KEM) | Table 1 hybrid-protected. Obtaining the combined secret requires both components [Y]; the KEM analogue of the principle "provided that a least one component … remains 'secure'" in RFC 9955 §1.3.1 | verified |

**Interpretation:** it was assumed that the flag HYBRID_KEM is run on its own (without adding a classical path). If it were run together with a classical path, it would correspond to o6 and the value would be falsified.

### 3.3 KAT-3b: authentication dual (V1…V6)

**Semantics** (input §1.1, KAT-3 column) [Y]:
- `tl_class`: class of the anchor key (`ktl`) that signs the TL.
- `expect=1`: the TL carries the "pq_required" signal for the issuer.
- `coexist=1`: the TL introduces a classical key of the issuer next to its PQ key.
- The TL is of the fetched kind, the credential of the conveyed kind. The attacker can present a forged TL (network position).

**Dual of Das's rule.** A path to a credential is the chain ktl → TL → issuer key → credential. The class of the path is its weakest link; the dual of Proposition 1 [Y]. A path being "valid" means that the verifier accepts that path: V_i includes "policy constraints" (l. 142). An expectation from a PQ-signed source invalidates the path that goes through the classical issuer key.

- **Static `violation`:** a violation of Equation (8) under P = {PQ}, i.e. there is a valid path containing a classical link.
- **Dynamic `attack(qday=0)`:** all classical keys are broken (input vocabulary). Can a forged credential be accepted through a broken link?
  - If the broken link is the TL, the attacker introduces its own key with a forged TL. Input §2(c) Note: "The attacker can generate its own key".
  - If the broken link is the classical key of the issuer, the attacker forges the credential directly.
- **`attack(qday=200)`:** no CRQC. No classical signature can be forged → YOK in every cell.

| V | tl_class, expect, coexist | Weak link | attack(qday=0) | violation | attack(qday=200) | Tamarin `claims_unforgeability` |
|---|---|---|---|---|---|---|
| V1 base | cl, 0, 1 | ktl (C) and the issuer's C key | SALDIRI | 1 | YOK | falsified |
| V2 expectTL | cl, 1, 1 | ktl (C). The expectation comes from a classical source; a forged TL deletes it or introduces the attacker's key | SALDIRI | 1 | YOK | falsified |
| V3 tlPQ | pq, 0, 1 | the issuer's C key. The TL is real but there is no expectation | SALDIRI | 1 | YOK | falsified |
| V4 tlPQ_expectTL | pq, 1, 1 | none. The expectation in the real TL invalidates the path with the C key (V_i = 0) | YOK | 0 | YOK | verified |
| V5 tlPQ_nocoexist | pq, 0, 0 | none. All links are PQ | YOK | 0 | YOK | verified |
| V6 tlClassical_nocoexist | cl, 0, 0 | ktl (C). A forged TL introduces the attacker's key | SALDIRI | 1 | YOK | falsified |

**Bases:**
- Das l. 157: "a single classical recipient path remains enough to expose the protected content if that path can recover K". Its counterpart in authentication: a single classical path is enough for forgery.
- Proposition 1 (l. 159).
- Equation (8) (l. 149).
- A Tamarin trace with Qday corresponds to the state qday=0 (input §1.4).

**Equivalence:** the static `violation` and the dynamic `attack(qday=0)` point the same way in every V. This is consistent with the assumption tested by KAT-3, "equivalence of static policy checking and dynamic attack search".

**Interpretation decisions (3b):**
1. **`violation=0` in V4.** This value rests on the assumption that the static check takes the expectation into account as a policy constraint. According to Das l. 142, V_i contains this constraint.
   - If the static check counted only the structural paths without seeing the expectation (the TL also introduces the C key), violation=1 would come out in V4 and the equivalence would break (UNDETERMINED.md §B).
2. **Verifier policy.** It was assumed that with `expect=0` the verifier accepts any valid path (anyvalid). The input gives no `pol` for KAT-3b. The names of the six pilot configurations (base / expectTL / tlPQ …) indicate that the expectation is the only tightening factor [Y].

## 4. Summary counts

- **KAT-1:** 15 cells, 30 rows (ASP + Tamarin).
- **KAT-2:** 40 cells, 48 rows.
  - 2a: 17 cells, 17 rows.
  - 2b: 8 cells, 13 rows (5 Tamarin).
  - 2c: 10 cells (5 leafB × 2 vb), 10 rows.
  - 2d: 5 cells, 8 rows (3 Tamarin).
- **KAT-3:** 21 cells, 63 rows.
  - 3a: 12 vectors × 3 = 36 rows.
  - `cek_secrecy`: 3 cells, 3 rows.
  - 3b: 6 × 4 = 24 rows.
- **Total:** 141 data rows. `belirsiz` (undetermined): 3 rows (K2d-01/02/03 Tamarin).

## 5. Interruption and check note

- **Session 1 (24.09.2026):** the 30 rows of KAT-1 and sections §0–§1 of this file were written. The session was interrupted at about 20:14.
- **Session 2 (25.09.2026):** the KAT-1 rows were not derived again, only checked. Then KAT-2, KAT-3, `UNDETERMINED.md` and `SHA256SUMS` were written.
- **Quotation check:** in all 141 rows the field `alinti` occurs verbatim in the first primary file named in the field `kaynak`, within the `satir` range. Whitespace was normalised. Script: `alinti_denetle.py` in the session's temporary folder; it only compares text. Result: **errors 0**.
- No error was found in KAT-1; no correction was made.
- In-text line references were verified by sampling with `grep -n` (Kim l. 54, 97, 241, 324, 326, 364, 396, 431, 452; Das l. 143, 162, 181; RFC 6781 l. 1477, 1558, 1584, 1894; RFC 6840 l. 446, 570, 1027).
