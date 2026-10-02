# METHOD — Oracle B (Step 9, task 6)

> **Work:** Oracle B (branch B of the N-version oracle; PR §4.20). **Date:** 25.09.2026.
> **Output folder:** `experiment/oracle/oracle-B/` (written only there).
> **Status:** Derivation. No target library was run, no vector file was opened or verified. The decisions were derived only from (i) primary specification clauses and (ii) the `insa` / `dogrulama_girdileri` facts in `MANIFEST.json`.
>
> (Quotations from the pre-registration are translated from Turkish; quotations from specifications are verbatim.)

---

## 1. Purpose

To produce, for every vector × policy configuration × arm of battery v1.2, the **policy-parametric, four-valued** expected decision (PR Ö6: `accept-classical`, `accept-hybrid`, `reject`, `indeterminate`) against which the decisions of the targets will be compared in the C3 measurement. The derivation of the L4 oracle from the clauses is separately in `L4-DERIVATION-B.md`.

## 2. Independence protocol

- `experiment/oracle/oracle-A/` and nothing else in the root of `experiment/oracle/` was **listed or read**. Only `mkdir -p experiment/oracle/oracle-B` was run.
- `referans/` (including the pilot), `model/`, `gozden-gecirme/`, `IS-PLANI.md` were **not opened**.
- Every opened file and its scope is in `ACCESS-LOG.md`. Part B of PR §2D (items 9–17; results of the formal part) happened to be in the chunk that was read; it was **not used** in the derivation (see `L4-DERIVATION-B.md` §0).
- No network access, Docker or git was used. No personal data was sent anywhere.

## 3. Fixed inputs

| Input | SHA-256 |
|---|---|
| `experiment/vector-generator/vectors/v1.2/MANIFEST.json` | `bb17aaa76a3d1859b2dd5df54c62e7039948a715e2c4b4628fed82d184c6e738` (same as PR §2G item 2) |
| `experiment/vector-generator/vectors/v1.2/SHA256SUMS` | `92663b48f477f51e5a4cdd2a6942d97d36b2d9591fa67af451fd33eb14f0b2a3` (same as PR §2G item 2) |
| `experiment/vector-generator/BATTERY-MAPPING.md` | `d73352179cdf281825d498000b7f9dc6d1df0fe835c8258c6aa2c516e659e3fc` (same as PR §2G item 2) |
| `00-on-kayit/ON-KAYIT-TASLAK.md` (v0.8, as read) | `dcc84092e2ca5eee0fcca8277fbcbd6b06ff613dc3459f63195f44d1ce3df79a` |

The digests of the corpus files are in §8.

## 4. Derivation of the policy configurations (from PR §4.13 + §6.5, §4.8 and §2B item 6)

### 4.1 Input clauses (PR)

- **§6.5:** "First signature A = ES256." (l. 1048); "Required set per issuer R = {X}, allowed set {A, X}." (l. 1054). X: EdDSA in control; ML-DSA-65 or composite -04 in treatment.
- **§4.13:** levels L0–L5; L4 = "In the configured state K1 ACCEPT, K2 REJECT, K3 REJECT" (l. 844). Extra flag **B5 semantic class: "at least one valid / all present valid / required set / other"** (l. 859).
- **§2B item 6:** L4m (multi-signature; "reject if there is no PQ component") and L4c (compact only; "PQ/composite mandatory" per issuer in the same verifier; "A document of a migrated issuer signed only classically is rejected; the classically signed document of the old issuer is accepted.") (l. 255–257).
- **§4.8:** P0 any-valid; P1 all-present-valid ("Removal of a signature (stripping) goes unnoticed"); P2 = P1 + key–alg binding; P3 = P2 + R_I per issuer (classical channel); P4 = P3 (PQ channel) (l. 775–779).
- **§6.4:** F_K/F_T deviation from the oracle in K1–K3 "in the best reachable configuration"; D_soy acceptance of K3 in the default configuration (l. 1043–1044).

### 4.2 Derived configurations

In every arm X is the second algorithm of the arm; **allowed = {ES256, X}** is common to all three configurations (§6.5). The three configurations correspond one-to-one to the three named classes of B5 and to the policies of §4.8 that can be distinguished at library level:

| Code (`politika`) | Definition | PR counterpart | Acceptance rule |
|---|---|---|---|
| **`L4`** (primary) | R_I = {X}, allowed = {ES256, X}, key–alg binding | §6.5 policy; §4.13 L4; §2B item 6 L4m and the "migrated issuer" half of L4c; §4.8 P3 ≡ P4; B5 "required set" | **Every** present signature is valid with an allowed alg and the key bound to that alg **and** there is a valid signature for every alg in R_I |
| **`P2`** | R_I = ∅, allowed = {ES256, X}, key–alg binding | §4.8 P1/P2; the "old issuer" half of L4c in §2B item 6; B5 "all present valid" | **Every** present signature is valid with an allowed alg (at least one signature) |
| **`P0`** | R_I = ∅, allowed = {ES256, X}, key–alg binding | §4.8 P0; the minimum of RFC 7515 §5.2; B5 "at least one valid" | **At least one** signature is valid with an allowed alg |

**Rationale:**
1. **Why three configurations?** The pre-registered B5 flag of the PR divides the multi-signature semantics of a target into three named classes. Determining the class of a target needs the expected decision of each class; therefore the oracle produces a decision for each of these three classes. The H6 text also says that failures will be split into the modes "at least one valid" and "all present valid" (§2 H6).
2. **Why `P2` and not `P1`?** 8725bis §3.1 puts key–alg consistency unconditionally as a **library** obligation (`JWTBCP.txt:468-471`). For a conforming library there is no P1 configuration without binding; therefore P1 ≡ P2 and the code is `P2`. For the same reason `P0` also includes the binding (K10 is `reject` in every configuration).
3. **Why are P3 and P4 not separated?** The difference between P3 and P4 is the channel through which R_I is learned. The library receives R_I through the API configuration; the channel is outside the library's observation space. At library level P3 ≡ P4 ≡ `L4`.
4. **Where does L4c fall?** The two halves of L4c are two separate configurations: migrated issuer = `L4`; old issuer = `P2` (`P2` ≡ `P0` for single-signature documents). For single-signature (compact) vectors, comparing these two rows gives the behavioural criterion of L4c (e.g. `VPLUS_ES256`: `L4` → `reject`, `P2` → `accept-classical`).
5. **Why is there no "default configuration" oracle?** D_soy (§6.4) and L5 are not compared with an oracle; they are direct observations. The default behaviour is not defined in the specification (8725bis §3.1 only says "provide a mechanism"). A separate default row would mostly produce `indeterminate` and would enter no pre-registered variable.
6. **Behavioural criteria L1–L3:** L1 ("a disallowed algorithm is rejected") is tested in all three configurations with the common allowed set (e.g. `UNK01/03`, `VC04/05`, `CMP14/15` are `reject` in every configuration). The L3 criterion: K10 is `reject` in every configuration.

### 4.3 Why does `L4` contain the condition "every present signature valid"?

Source: in PR §4.8, P3 = P2 + R_I and P2 = P1 + binding, P1 = "Accept if all present signatures are valid" (cumulative definition). In addition, the premise "composite AND": composite -04 §4.3 "MUST validate a signature only if all component signatures were successfully validated" and ACM2 Note 51 "the veriﬁcation function accepting if and only if all signatures are correct". The detailed derivation is in `L4-DERIVATION-B.md` §2. Result: under `L4` an **extra** signature that is not allowed or invalid (K5) makes the decision `reject`; under `P0` the same vector is accepted. This is the policy dependence expected by MR2 ("its effect is predictable from the policy").

## 5. Arms and vector–arm assignment

| `kol` | X | allowed |
|---|---|---|
| `kontrol-EdDSA` | EdDSA | {ES256, EdDSA} |
| `kontrol-Ed25519` (PR §2D item 2 fallback) | Ed25519 | {ES256, Ed25519} |
| `tedavi-ML-DSA-65` | ML-DSA-65 | {ES256, ML-DSA-65} |
| `tedavi-composite` | ML-DSA-65-ES256 | {ES256, ML-DSA-65-ES256} |

- The `alg` comparison is case-sensitive and label-based (RFC 7515 §4.1.1). In `kontrol-EdDSA` an `Ed25519`-labelled signature is not allowed, and vice versa (consistent with the tool fact of PR §2E item 3).
- **Assignment rule:** if the `kol` in the manifest is one of the four arms, the vector is evaluated only in that arm. If `kol` ∈ {`ortak`, `klasik-taban`, `kapsam-pq`, `kapsam-hibrit`, `null`}, it is evaluated in all four arms (the decision of these vectors may depend on the X of the arm or be arm-independent; in both cases the rows are written explicitly).
- **Additional arm assignments from the mapping** (`BATTERY-MAPPING.md`): `X5C04` and `X5C07` → also `tedavi-composite` (primary column of K8/K9); `K10K_alg-ES256_anahtar-Ed25519` → also `kontrol-Ed25519` (no twin in the fallback arm, the same file); `VC10_ikili_ihrac` → four arms (K11 primary, "policy per arm").

## 6. Decision rule

### 6.1 Signature level

For every signature s, under the allowed set of the arm:
- if `alg(s)` is not allowed → s is **not verified** and counts as invalid (8725bis §3.1 "MUST NOT employ any algorithms outside this configured set"; RFC 7515 §4.1.1 "not valid if the "alg" value does not represent a supported algorithm").
- if `alg(s)` is inconsistent with the algorithm to which the key is bound → invalid (8725bis §3.1; RFC 9964 §3 `alg` mandatory in an AKP key).
- if `insa` is not "gecerli" (valid) (corrupted byte, random bytes of an unregistered label, `none`) → invalid.
- A composite signature is valid only if both components are correctly encoded and valid over the correct M′/ctx (composite -04 §4.2–§4.5.1).

### 6.2 Document level

`P0`, `P2`, `L4` are applied with the acceptance rules of §4.2. With multiple signatures the order of the signatures does not affect the decision (RFC 7515 §5.2 steps 9–10 verify every signature separately; §7.2.1 computes every signature with its own header). Therefore the decision of the MR4 twins is the same as that of their sources.

### 6.3 Semantics of the four-valued output (values of PR Ö6; the semantics is not defined in the PR — `DECISION-NOTES.md` N1)

| Value | Meaning in this oracle |
|---|---|
| `accept-hybrid` | Accepted; the valid and allowed signatures on which the acceptance rests include **at least one PQ-class component** (ML-DSA or composite). Pure PQ acceptance (e.g. K4 treatment) also falls under this value; there is no separate "accept-pq" value. |
| `accept-classical` | Accepted; the acceptance rests only on classical signatures. In the control arm X = EdDSA is classical, so every acceptance in the control arm is `accept-classical`. |
| `reject` | There is no acceptance path under the relevant clauses and the configuration. |
| `indeterminate` | The clauses do not determine the decision: both acceptance and rejection are conforming (MAY/SHOULD level, undefined interpretation, missing context). The reason of every `indeterminate` row is in `UNDETERMINED.md`. |

- **Comparison mapping:** if the target output is binary (accept/reject), `accept-*` → accept. `indeterminate` rows do not enter the deviation count (the "undetermined" class of PR §4.15).
- **Determinedness threshold:** a decision counts as determined only if a clause at MUST / MUST NOT / REQUIRED level, or the definition of the configuration itself, forces it. SHOULD/RECOMMENDED/MAY alone does not determine the decision; the direction is written in `not`.
- The label `accept-hybrid` classifies only the JWS/signature layer. If the certificate path has a classical edge (K8), this is reported in `not` and through flag B2.

### 6.4 Context assumptions used for the determination (insa + dogrulama_girdileri)

- Every structure for which the `insa` field says "gecerli" (signature, chain, SD-JWT disclosures, time claims, `typ`) is taken as validly produced; this derivation opens no vector file.
- Key resolution: for the JWS core, SD-JWT VC (kid), DPoP and request vectors, the key/JWKS in `dogrulama_girdileri` (PR §2D item 1, D-S1). **In the X5C family** the key is resolved via `x5c` (PR §2D item 1: "chain behaviour is measured only on the X5C vectors ..."). The absence of x5c in composite credentials is accepted with the label "deviation from HAIP §6.1.1" (PR §2D item 1).
- The KB-JWT algorithm is also subject to the allowed set of the arm; R_I applies only to the signature of the issuer (the signing entity).
- For the request object (REQ), status list (TSL) and DPoP vectors, R_I is applied **by analogy** to the signing entity (RP, status issuer, DPoP client); for DPoP this is the condition "acceptable per local policy" of RFC 9449 §4.3(5). These rows enter no pre-registered variable.

## 7. Special cases and the version dimension

- **SD-JWT VC version** (`sdjwtvc_surum`, PR Ö9 and §2D item 7): the scope of the parameter is "scenario (d) vectors (status of the JSON serialization) and VC11" (§2D item 7). In these vectors (the `VC07/08/09` family and permutations, `VP05/06/07`, `VP05-SIRA-ters`, `VC11`) every configuration is split into two rows: `…|sdjwtvc=-13` and `…|sdjwtvc=-19`. In the other SD-JWT VC vectors the decision is the same in both versions; `politika` carries no version suffix and `not` says so. The flattened JSON vectors defined in the manifest only for `-13` (`X5C07/08/09`, `CRIT02`) have a single row with the `-13` reading.
- Under `-19` the details of a JSON-serialized SD-JWT VC are "beyond the scope", so decisions with an acceptance path become `indeterminate`; decisions without an acceptance path (`reject`) do not change.
- For a target that does not support the JSON serialization, these rows fall under B6 ("not applicable"); the oracle gives the decision of a verifier that supports the format.
- Vector-specific rules (CMP, X5C, CRIT, VP, REQ, DPoP, VC11/VC12) are in the `dayanak` and `not` columns of `decisions.tsv`; the undetermined ones in `UNDETERMINED.md`.

## 8. Format of the basis and quote verification

- Format: `DOCUMENT §section [matrix id Tnnn if any] “verbatim short quote” (version; file:line)`. Several clauses are separated by ` ; `. The matrix ids are the rows of `traceability/izlenebilirlik.csv`.
- Every quote is searched by the script in the source file **as a substring within the given line range, with whitespace normalised**; a quote that is not found stops the script (`derive_decisions.py`, `alinti_denetimi()`). Lines are split only at `\n` (the same as grep/sed numbering; form-feed characters do not count as lines). A hyphen at a line end is joined without a space (in the RFC texts it is a real hyphen: `case-`/`sensitive`, `ML-DSA-`/`65`). The quote in the basis is a verbatim substring of the source text; only line breaks have been reduced to a single space. The long quotations in `L4-DERIVATION-B.md` and `UNDETERMINED.md` were also verified separately with the same method.
- Cited documents (version; SHA-256):

| Short name | Document | SHA-256 (`spec-corpus/metin/…`) |
|---|---|---|
| JWTBCP | draft-ietf-oauth-rfc8725bis-10 (21.08.2026) | `0f20c55d5d4094225d57f68db16061659c7e31a617b32f192839669950cd1339` |
| JOSECOMP | draft-ietf-jose-pq-composite-sigs-04 (10.09.2026) | `f23f9ad996ac1f85e1d39584a03554754cc74e0a07f186d1288e009d9578250d` |
| LAMPSCOMP | draft-ietf-lamps-pq-composite-sigs-19 (21.04.2026) | `bedaa29011c2e076c7f7e47f46c03caf5b1283d41cf5d01f7685f38dfaa014f8` |
| RFC9964 | RFC 9964 (May 2026) | `00470379e12eeae80e37872b2b4b3163831c572dbfa90b9dc9a9a9eb0c92aa28` |
| RFC7515 | RFC 7515 (May 2015) | `dd12efc0e7f03477160e4f9e1a939897341a97684f9addf66c7fbfa7bab9040c` |
| RFC9864 | RFC 9864 (October 2025) | `52748a942507056e471b29e37baabcd7b15eb75ea78a2fda89cc4dee1dea8cbe` |
| RFC9901 | RFC 9901 (November 2025) | `072bfcdbd4c89f70004198a788b161bb25c341393d38232ea7dd7f2d360efbf0` |
| SDJWTVC | draft-ietf-oauth-sd-jwt-vc-19 (31.08.2026) | `4c05560e1f698ed7e40bbb710bb5accfb8126d647b769d45d8653834e35f49e6` |
| SDJWTVC13 | draft-ietf-oauth-sd-jwt-vc-13 (06.11.2025) | `d71c0078c2d8004cf5d8b0fc400585d5869c8fa6bbff06ecd7da23bf26b7f61d` |
| HAIP | OpenID4VC HAIP 1.0 Final (24.12.2025) | `37057efeac8a434699e15c2b723abc8076aa6b3a7775497627334f3e442809d0` |
| OID4VP | OpenID4VP 1.0 Final (09.07.2025) | `e0a2ae4ccc1bdda8ab6536be10c5e823c661fbef9813452df30ffc30cc101fa9` |
| RFC9449 | RFC 9449 (September 2023) | `e09416d29421414ac0ee47b81726538e9bc8cd20af2dcfae1a10bc337537a769` |
| TSL | draft-ietf-oauth-status-list-21 (21.06.2026) | `8bc7b293f92e4c38a4a04110276bc012de114026c3cd3a7d1b5b6a2dae0449f1` |
| ACM2 | ECCG Agreed Cryptographic Mechanisms v2.0 (April 2025) | `8d731a28dc0fd63b0f34e5bffd675163f4aed6ee37e3ef530769b451f6584e71` |
| PR | ON-KAYIT-TASLAK v0.8 | `dcc84092e2ca5eee0fcca8277fbcbd6b06ff613dc3459f63195f44d1ce3df79a` |
| Matrix | `traceability/izlenebilirlik.csv` | `79b6b19e9f06865888cde9f4a6a1ff441f6aa607f1f98dfd39a6d7492ef0c26d` |

## 9. Primary / secondary

- `birincil_mi = evet` (primary): the (vector, arm) pair appears as **primary** in that arm's column in §1 of `BATTERY-MAPPING.md` (including the fallback `-ED25519` twins and V+/V−). PR §2G item 4: the pre-registered variables are computed only from these.
- `birincil_mi = hayır` (secondary): secondary in the mapping, only an MR twin (MR1/MR3/MR4), or outside the mapping. Their role is written in their `not`.

## 10. Output format

- `decisions.tsv`: UTF-8, tab-separated, **no quote character** (use `csv.QUOTE_NONE` when reading). Fields contain no tabs or newlines (checked by the script). Header row: `vektor_id politika kol birincil_mi karar dayanak not`.
- Row order: arm → vector (manifest order) → policy (`L4`, `P2`, `P0`; for those with a version suffix, `-13` first).

## 11. Tool and reproduction

- `derive_decisions.py` (Python 3, standard library only): applies a hand-written fact table per vector (the signature list is **cross-checked** against the manifest) and the special rules; verifies the quotes in the source text; produces `decisions.tsv` and the distribution summary. It opens no vector file and uses no network.
- Running: `PYTHONIOENCODING=utf-8 python derive_decisions.py` (from the folder; it finds the project root automatically).
- Incremental generation: with the option `--kollar k1,k2,…` the arms were written cumulatively (kontrol-EdDSA → + kontrol-Ed25519 → + tedavi-ML-DSA-65 → + tedavi-composite); every run rewrites `decisions.tsv` in the canonical order of the selected arms. The final state is the union of the four arms (run without the option).

## 12. Limitations

- The decisions are this work's reading of the specification and PR clauses; a disagreement with Oracle A falls into the "undetermined" class (PR §4.15).
- The `insa` facts were taken as correct (generator self-verification T10 and the maintainers' regeneration in PR §2G item 3).
- The R_I analogy in the REQ/TSL/DPoP rows is not pre-registered; these rows are descriptive.

## 13. Result summary (output of `derive_decisions.py`, 25.09.2026)

- **732 rows**; all 153 vectors; 53 primary (vector, arm) pairs × 3 configurations = 159 primary rows. Rows with a version suffix: 96 (§7).
- Quote check: all 116 clauses of the script were found in their source line range. Manifest cross-check: every signature whose `insa` value is not "gecerli" has a hand-written state; all ids are in the manifest.
- Two independent runs gave the same digest of `decisions.tsv` (deterministic).

| Slice | Rows | accept-classical | accept-hybrid | reject | indeterminate |
|---|---|---|---|---|---|
| All | 732 | 169 | 101 | 373 | 89 |
| Primary (birincil_mi = evet) | 159 | 48 | 23 | 88 | 0 |
| Secondary / MR / outside the mapping | 573 | 121 | 78 | 285 | 89 |
| policy L4 (incl. version suffix) | 244 | 14 | 29 | 172 | 29 |
| policy P2 (incl. version suffix) | 244 | 64 | 29 | 121 | 30 |
| policy P0 (incl. version suffix) | 244 | 91 | 43 | 80 | 30 |
| arm kontrol-EdDSA | 144 | 56 | 0 | 76 | 12 |
| arm kontrol-Ed25519 | 144 | 56 | 0 | 76 | 12 |
| arm tedavi-ML-DSA-65 | 246 | 31 | 62 | 106 | 47 |
| arm tedavi-composite | 198 | 26 | 39 | 115 | 18 |

- The PR §4.13 L4 criterion (K1 ACCEPT, K2 REJECT, K3 REJECT) **came out** of the derivation in the `L4` rows of the four arms (it was not given as an input); table in `L4-DERIVATION-B.md` §3.
- There is no `indeterminate` in the primary rows; all 89 undetermined rows are in descriptive vectors (`UNDETERMINED.md`).
