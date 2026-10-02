# Oracle A — Method (Step 9, tasks 6 and 7)

> **Date:** 25.09.2026 · **Work:** Oracle A (branch A of the N-version oracle).
> **Independence:** `experiment/oracle/oracle-B/` was not read. As required by the task description, `referans/pilot/`, `model/` and `gozden-gecirme/adim-0*` (including adim-09a and adim-09b) were not read either. The content of the D-E and D-S decisions was taken from PR §2B, §2D and Step 9 of `IS-PLANI.md`.
> **No measurement:** no target library was run. No vector was verified with a library or a cryptographic tool. The vector files were only decoded with base64url to read the construction facts (header, claims, time). No network access, Docker or git was used.
> **Script that produces the output:** `karar_uret.py` (Python 3, standard library only). It produces a byte-identical `karar.tsv` on every run with the same inputs (§6).
>
> (Quotations from the pre-registration are translated from Turkish; quotations from specifications are verbatim.)

## 0. Inputs and their identities

The script checks the digests below. It stops on a mismatch.

| Input | SHA-256 |
|---|---|
| `00-on-kayit/ON-KAYIT-TASLAK.md` (v0.8, anchor 7) | `dcc84092e2ca5eee0fcca8277fbcbd6b06ff613dc3459f63195f44d1ce3df79a` |
| `experiment/vector-generator/vektorler/v1.2/MANIFEST.json` (153 vectors) | `bb17aaa76a3d1859b2dd5df54c62e7039948a715e2c4b4628fed82d184c6e738` |
| `experiment/vector-generator/vektorler/v1.2/SHA256SUMS` | `92663b48f477f51e5a4cdd2a6942d97d36b2d9591fa67af451fd33eb14f0b2a3` |
| `experiment/vector-generator/BATARYA-ESLEME.md` | `d73352179cdf281825d498000b7f9dc6d1df0fe835c8258c6aa2c516e659e3fc` |
| `spec-corpus/metin/<document>.txt` (16 documents; quoted from 15, RFC 8725 checked by digest only) | identical to the `sha256_metin` column of `spec-corpus/MANIFEST.csv` |

Primary texts used and their versions:
- 8725bis-10 (JWTBCP), composite -04 (JOSECOMP), LAMPS composite -19;
- RFC 7515, 7518, 9864, 9964, 9901, 9449;
- SD-JWT VC -13 and -19, Token Status List -21;
- HAIP 1.0 Final, OID4VP 1.0 Final, ECCG ACM v2.

## 1. Decision space: four values (PR Ö6)

| Value | Definition (Oracle A) |
|---|---|
| `accept-hybrid` | The object is accepted **and** every acceptance path allowed by the configuration requires the verification of a valid PQ component. PQ component: an ML-DSA signature or the ML-DSA component of a composite signature. The acceptance of an object signed only with ML-DSA is also in this class |
| `accept-classical` | The object is accepted, but under the configuration verifying the classical signature(s) alone is enough for acceptance; or the object has only classical signatures |
| `reject` | A verifier that conforms to the configuration must reject the object (MUST level). Rejections at SHOULD level are marked "SHOULD" in the `not` column (only VC11/-19) |
| `indeterminate` | The clauses + construction facts do not determine the decision. The reasons are in `UNDETERMINED.md` |

In the control arms (X = EdDSA or Ed25519) every acceptance is `accept-classical`. In this way the L4 measurement in the control arm is separated from PQ support (PR §3.7).

**The label is a security floor.** Under P0 (at least one valid), the acceptance of an ES256 + ML-DSA-65 object is `accept-classical`, because ES256 alone is enough for acceptance. Under P1 (all present valid), the same object is `accept-hybrid`, because every present signature must be verified. This preserves the distinction of Kim et al. "classical acceptance ≠ hybrid authentication". Details: `L4-DERIVATION.md` §4.

**TK3 note:** a target that cannot verify the PQ signature cannot produce `accept-hybrid` (CRITERIA §5.5). The oracle assumes that the target supports all registered and draft algorithms in the battery (the TK1/TK2 ideal). TK3 targets are compared with the rule in `adapter-contract.md` §6.

## 2. Policy configurations: derivation from PR §4.13

Each configuration is defined by four elements:
- the allowed set **W**,
- the required set **R**,
- the multi-signature rule,
- the key path.

In every arm A = ES256. X changes with the arm: `kontrol-EdDSA` → EdDSA; `kontrol-Ed25519` → Ed25519 (fallback, PR §2D item 2); `tedavi-ML-DSA-65` → ML-DSA-65; `tedavi-composite` → ML-DSA-65-ES256. Key–alg binding (8725bis §3.1 [T329]; RFC 7515 §5.2 step 8) is on in **all** configurations, because every verification that conforms to RFC 7515 verifies the signature with the alg in the header.

| Configuration | W | R | Multi-signature rule | Which PR requirement asks for it |
|---|---|---|---|---|
| `GEC` | all algorithms supported in the battery | ∅ | (single-signature objects only) | §4.15 V± adapter validity gate; the "plain validity" baseline of single-signature objects |
| `IZIN-A` | {A} | ∅ | (single signature) | §4.13 L1 ("a disallowed algorithm is rejected") and L2 (two different allow-lists per call: A and AX) |
| `IZIN-AX` | {A, X} | ∅ | (single signature) | the positive side of L1/L2; **L3** (K10 → REJECT, §6.5 "REJECT (L2/L3)"); **L4c old issuer** (§2B item 6: "the classically signed document of the old issuer is accepted") |
| `L4` | {A, X} | {X} | extra signature outside W: `indeterminate` if S and Y diverge | the §6.5 policy verbatim; §4.13 **L4** and **L4c migration**; the oracle of F_K/F_T (§6.4) |
| `L4-S` | {A, X} | {X} | every present signature must be in W and valid | §4.8 P3 (= P2 + R_I; P2 ⊇ P1 "all present signatures valid"); ECCG ACM Note 51; last paragraph of RFC 7515 §5.2 (SHOULD) |
| `L4-Y` | {A, X} | {X} | signatures outside W are ignored; those in W must be valid | RFC 7515 §5.2 "application decision" [T314]; 8725bis §3.1 "MUST NOT employ … outside" [T327]; the L4 proposal of the inventory (CRITERIA §7.7) |
| `P0` | all supported | ∅ | at least one signature valid | §4.8 P0; semantic class of B5 ("at least one valid"); the failure-mode distinction of H6 |
| `P1` | all supported | ∅ | all present signatures valid | §4.8 P1 (and P2); B5 ("all present valid"); failure mode of H6 |
| `L4-YOL` | {A, X} | {X} | + every certificate signature on the x5c path must be PQ | **B2** ("can a mixed x5c chain policy be expressed?"); definition of `yol_sinifi` in §2D item 13; X5C vectors only |
| `GEC@-19`, `L4@-19` | as GEC / L4 | | | sensitivity to `sdjwtvc_surum` (§2C.2.3, Ö9); **MR3**; only VC01, VC11, VC07, VC08, VC09 (+ Ed25519 twin) |

**Why is this set sufficient?**
- **L0:** no separate configuration is needed. It is the failure of the L1 test (if VPLUS_X is accepted under `IZIN-A`, there is no allow-list or it does not work).
- **L5:** no separate oracle is needed. The battery run with the default configuration is compared with the rows `L4` (for L4) and `IZIN-AX` (for L3).
- **D_soy:** a descriptive proportion observed in the default configuration (PR §6.4, T5). No oracle decision is needed: RFC 7515 §5.2 leaves multi-signature as an "application decision".
- **B1:** `L4-S` vs. `L4-Y` captures it. The reading that the target's K5 behaviour follows is recorded; if it fits neither, it is marked as an MR2 violation.
- **B3:** captured by the X5C07–X5C09 rows under `L4`/`GEC`.
- **B5:** the rows `P0`, `P1`, `L4-S` and `L4-Y` classify it together (`adapter-contract.md` §5.4).
- **P2, P3 and P4:** P2 is identical to P1 on this battery, because the alg–key mismatch exists only in the single-signature K10 and is rejected in every configuration. P3 = `L4-S`. P4 is identical to P3 at library level: the channel through which R_I is learned is not represented in the vector; the adapter fixes R_I through the API.

**Scope decisions:**
- **TSL, DPOP, the scope-pq/-hybrid vectors and VC12** were evaluated only under `GEC`. They are not objects of the per-issuer policy. Under L4 the scope vectors are outside W anyway.
- **The REQ family** is wallet-side (Step 11; mapping "scenario c"). L4 was adapted to the RP with the "per entity" reading: R_RP = {X}. G5 says "a migrated **entity**". Moreover, according to OID4VP §5.9.3 signature verification is at the wallet's discretion with the DC API [T268]. The rows were written under the assumption "the wallet verifies signatures".
- **The X5C family:** the key is resolved with x5c and the trust anchors (root-ec, root-ml) (PR §2D item 1). K8/K9 have an ML-DSA-65 leaf in the composite arm as well (adaptation of PR §2F item 4). Therefore in the X5C04/X5C07 rows of the composite arm the policy was instantiated with X = ML-DSA-65 (decision notes N-3).

## 3. Decision rule (clause + construction fact → decision)

1. **Signature validity from the manifest.** The `insa` field of each signature is translated into a three-valued validity: valid / invalid / undetermined. Bases:
   - `bozuk` (corrupted) → invalid (RFC 7515 §5.2 step 8).
   - Unregistered or unsupported alg (`ML-DSA-66`, `ML-DSA-65-P256`, `ml-dsa-65`, `X-KAYITSIZ-1`) → invalid [T319]. Case sensitivity is in RFC 7515 §4.1.1.
   - `none` → invalid (8725bis §3.2; RFC 9901 §4.1 [T102]).
   - K10 (header alg ≠ the key's algorithm) → invalid [T329], RFC 7515 §5.2 step 8, RFC 9864 §7 [T335], RFC 7518 §3.4.
   - CMP corruptions: composite -04 §4.2, §4.3 [T345], Table 5 and LAMPS -19 §4.3 (table per vector in `karar_uret.py`, `CMP_KURAL`).
   - CMP05 (non-minimal DER) and CMP06 (trailing byte) → **undetermined** (`UNDETERMINED.md` B-3).
   - CMP12/13 (component signature as an independent alg) → invalid. The signature was produced over M′; ES256/ML-DSA-65 verification is done over the JWS Signing Input with an empty ctx (RFC 7518 §3.4; RFC 9964 §5 [T338]). Independent use of a component key is forbidden [T057].
2. **The rule of the configuration is applied to the set of signatures** (table of §2). Three-valued logic is used:
   - `reject` if there is a definite failure: a signature outside W (only under S), an invalid signature in W, or R not met;
   - `indeterminate` if there is no definite failure and a validity on which the decision depends is undetermined;
   - acceptance if neither.
3. **Family-specific structural conditions are combined.** Rejection dominates everything. Undeterminedness only makes an acceptance undetermined:
   - SD-JWT VC `typ` (VC11: -13 SHOULD accept, -19 SHOULD reject);
   - position and duplication of x5c in the header (X5C07–X5C09);
   - trust anchor inside x5c (X5C06);
   - conflict between kid and x5c (X5C10);
   - `crit` (RFC 7515 §4.1.11);
   - KB-JWT `sd_hash` binding (RFC 9901 §8.1);
   - in DPoP, alg registration and a private key inside `jwk` (RFC 9449 §4.3 items 5 and 7);
   - x509_hash and unsigned requests (OID4VP §5.9.3, A.2; HAIP §5.2).
4. **The label** is given according to §1.
5. **The basis** starts with the clauses that determine the decision, followed by the definition of the configuration. If the row is a PR §6.5 case (K1–K11, V±), the PR row of that case is added. Every quote is found by the script in the corpus text and its line number is computed. A quote that is not found stops the generation. The full clause list with URLs is in `maddeler.tsv` (107 clauses).

**Construction audit (`insa_denetimi.txt`, 467 checks, all passed).** Every construction fact on which a decision rests was verified by base64url-decoding the vector file:
- time: every `exp` > `simdi` ≥ `iat`; KB-JWT `iat` = simdi − 100 s; DPoP `iat` = simdi − 10 s;
- signature alg sequences identical to the manifest;
- `typ` values, x5c position, `crit` position, K10 header alg ≠ key type;
- `priv` inside the DPoP `jwk` only in DPOP10; TSL `sub`.

## 4. Primary / secondary (PR §2G item 4)

- `sinif = birincil` (primary): the (vector, arm) pair appears as **primary** in that arm in §1 of `BATARYA-ESLEME.md`. The fallback arm is filled with the bracketed `-ED25519` twins and with the shared files (T3, VPLUS/VMINUS_ES256, VC10).
- `sinif = ikincil` (secondary): everything else. This covers the secondary vectors of the mapping, the vectors that appear only in the MR table (including the MR4 permutations) and the vectors outside the mapping (UNK01–03, CRIT, DPOP, TSL, …).
- The `vaka` column writes which case or relation the vector is bound to: `K1`, `K5(ikincil)`, `MR1`, `MR4(T1K_both_valid)`, `MR4-dışı tanımlayıcı(…)` (descriptive outside MR4), `eşleme-dışı` (outside the mapping).
- The primary coverage check is done in the script. Every primary (vector, arm) has an `L4` row. V± also has a `GEC` row, K8/K9 an `L4-YOL` row.

## 5. Out-of-scope and not-applicable cells

- **B6 (unsupported format):** for the General JSON and flattened JSON vectors the decision is given under the assumption that the target supports this serialization. On a target that does not support it, the observation becomes "not applicable" and does not count as an oracle deviation (PR §4.13 B6). The bases: RFC 9901 §8 "OPTIONAL", HAIP §6.1 "JSON serialization MAY", 8725bis §3.14 (a JWT library rejecting JSON input).
- **Composite X.509:** out of scope (PR §2D item 1, "deviation from HAIP §6.1.1"). Composite objects are resolved with kid/JWKS.
- **Status list check:** the VC vectors carry `status` (idx 7). The status list is a separate vector (TSL); under SD-JWT VC §2.4 the check is a SHOULD. The oracle decision was not tied to the status list.
- **Number of rows** (vector × configuration × arm): **858.** All 153 vectors are covered by at least one row.

## 6. Production and verification

```bash
cd <project root>
PYTHONIOENCODING=utf-8 python experiment/oracle/oracle-A/karar_uret.py "$(cygpath -w "$PWD")"
sha256sum -c experiment/oracle/oracle-A/SHA256SUMS
```

- **Outputs:** `karar.tsv`, `maddeler.tsv`, `karar_ozet.json`, `insa_denetimi.txt`.
- **Determinism:** the script uses no randomness, clock or network. Two runs are byte-identical (checked with `SHA256SUMS`).
- **Columns of `karar.tsv`:** `vektor_id`, `politika`, `kol`, `sinif`, `vaka`, `karar`, `dayanak`, `not`.
  - Format of `dayanak`: `[Tnnn] DOCUMENT §section (version; metin/DOCUMENT.txt:line): "verbatim quote"`; several clauses are separated by ` | `.
  - The `not` column starts with an `insa:` summary and gives the reason for the decision. Clause mentions for information only (e.g. B6) are in square brackets in `not`.
