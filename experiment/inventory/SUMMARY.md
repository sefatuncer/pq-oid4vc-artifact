# C3 sampling frame — SUMMARY (Step 9a)

> **Date:** 24.09.2026. Frame date REF_TARIH = 23.09.2026.
> **Scope:** frame, metadata and a feature inventory at documentation/code level only. No behaviour was measured: no adapter was written and no test vector was run.
> **Sources:** the numbers come from `FRAME.csv`, `SELECTION.csv`, `THRESHOLD-SENSITIVITY.csv`, `SCREENING.csv` and `collect_record.json`. The full definition of the criteria is in `CRITERIA-DRAFT.md`.
> **Consistency with the pre-registration decision (PR §2A Ö6):**
> - Reference verifiers (REF) are kept **outside** n.
> - The main treatment arm is composite -04, the secondary arm ML-DSA-65.
> - The oracle is four-valued: accept-classical / accept-hybrid / reject / indeterminate.

---

## 1. Stratum counts (identification → screening → eligibility → selection)

| Stage | JOSE | SDJWT | COSE | **n (libraries)** | REF (outside n) |
|---|---|---|---|---|---|
| Frame candidates (198) | 109 | 29 | 37 | 175 | 23 |
| Meet the criteria (E2) | 41 | 15 | 17 | **73** | 14 |
| **Selected (quota)** | **18** | **8** | **5** | **31** | **3** |
| Reserve | 9 | 6 | 4 | 19 | 2 |

**Where did they come from?**
- jwt.io has 37 languages, 110 entries and 107 unique repositories.
- The GitHub topic and package registry searches gave 386 hits after the noise floor; they reduced to 306 screening rows.
- After screening 91 hits became candidates and 215 were eliminated:

  | Screening decision | Count |
  |---|---|
  | irrelevant | 60 |
  | below the floor | 46 |
  | application | 33 |
  | duplicate | 32 |
  | document | 26 |
  | wallet | 9 |
  | mdoc | 5 |
  | issuer | 3 |
  | duplicate of jwt.io | 1 |

**Is n within the range?** Yes. n = 31, inside the range 25–40.
- What ensures this is not the threshold but the quota and the selection rule.
- A census without quotas stays outside the range under all threshold options: 49–91 targets.
- With the quota applied, n comes out at 30–31 under all options.
- Details: `CRITERIA-DRAFT.md` §4.

**Exclusion reasons under E2** (a candidate can be excluded for several reasons):

| Code | Reason | Count |
|---|---|---|
| K5 | below the threshold | 85 |
| K2 | not active | 56 |
| K1 | symmetric only | 15 |
| K3 | archived/abandoned | 14 |
| K4 | licence | 12 |
| K6 | platform | 4 |

Eligible candidates outside the quota: 14 in JOSE, 1 in SDJWT, 8 in COSE.

## 2. Proposed final list (E2; n = 31) and reserves

**Column abbreviations:**
- GJ: General JSON multi-signature
- ML-DSA: RFC 9964 support
- Treatment path: the proposed treatment class of §3.2. "to be examined" = there may be a plug-in API, but it is not proven.

**All cells** are in `FRAME.csv` with a basis link (a line at a pinned commit, or a screening record).

### 2.1 JOSE (18)

| id | Target | Language | Package | ★ | Monthly downloads | GJ | ML-DSA | Treatment path (proposed) |
|---|---|---|---|---|---|---|---|---|
| JOSE-065 | auth0/node-jsonwebtoken | JS/TS | npm `jsonwebtoken` | 18,193 | 204.6 M | no | no | T3 (to be examined) |
| JOSE-009 | panva/jose *(pilot)* | JS/TS | npm `jose` | 7,799 | 472.0 M | yes (any, documented) | **yes** | ML-DSA: T1; composite: T3 |
| JOSE-083 | jpadilla/pyjwt | Python | `pyjwt` | 5,703 | 523.0 M | no | no | T2 (`register_algorithm`) |
| JOSE-084 | mpdavis/python-jose | Python | `python-jose` | 1,759 | 30.7 M | no | no | T3 |
| JOSE-055 | jwtk/jjwt | JVM | `jjwt-api` | 11,137 | — | no | no | T2 (`parserBuilder.sig().add`) |
| JOSE-052 | auth0/java-jwt | JVM | `java-jwt` | 6,236 | — | no | no | to be examined |
| JOSE-033 | golang-jwt/jwt | Go | `jwt/v5` | 9,225 | — | no | no | to be examined |
| JOSE-034 | dvsekhvalnov/jose2go | Go | `jose2go` | 186 | — | no | no | T2 (`RegisterJws`) |
| JOSE-001 | Microsoft IdentityModel | .NET | `System.IdentityModel.Tokens.Jwt` | 1,154 | — | no | **yes** | ML-DSA: T1; composite: to be examined |
| JOSE-002 | jwt-dotnet/jwt (JWT.NET) | .NET | `JWT` | 2,190 | — | no | no | to be examined |
| JOSE-070 | firebase/php-jwt | PHP | `firebase/php-jwt` | 9,809 | 14.2 M | no | no | T3 |
| JOSE-071 | lcobucci/jwt | PHP | `lcobucci/jwt` | 7,478 | 9.8 M | no | no | to be examined |
| JOSE-087 | jwt/ruby-jwt | Ruby | `jwt` | 3,687 | — | no | no | to be examined |
| JOSE-089 | nov/json-jwt | Ruby | `json-jwt` | 297 | — | yes (first signature only) | no | to be examined |
| JOSE-092 | Keats/jsonwebtoken | Rust | `jsonwebtoken` | 2,093 | 16.9 M | no | no | T3 |
| JOSE-091 | GildedHonour/rust-jwt | Rust | `frank_jwt` | 251 | 8.9 k | no | no | T3 |
| JOSE-104 | Kitura/Swift-JWT | Swift | SwiftPM | 602 | — | no | no | T3 |
| JOSE-102 | vapor/jwt-kit | Swift | SwiftPM | 282 | — | no | partial (65/87; macOS 26+) | T3 likely on Linux |

**JOSE reserves.** The in-group reserve comes first; then the general reserve.
- JS/TS: jsrsasign
- Python: authlib/joserfc *(pilot; GJ yes: "all")*
- JVM: Nimbus JOSE+JWT *(GJ yes: "left to the application")*
- Go: lestrrat-go/jwx *(ML-DSA yes, composite yes)*
- .NET: jose-jwt
- PHP: web-token/jwt-framework *(ML-DSA yes)*
- Rust: biscuit
- General reserve: guardian (Elixir), jwt-cpp (C++)

### 2.2 SDJWT (8)

| id | Target | Language | Package | ★ | Monthly downloads | GJ | ML-DSA | Treatment path (proposed) |
|---|---|---|---|---|---|---|---|---|
| SDJWT-025 | spruceid/ssi | Rust | `ssi-sd-jwt` | 264 | 17.3 k | unclear | no | to be examined |
| SDJWT-015 | identity-common-ts *(pilot; successor of sd-jwt-js)* | TS | `@sd-jwt/core` | 7 | 100.4 k | yes (undocumented; "all" in the code) | unclear | T2 (verifier callback) |
| SDJWT-018 | OWF-Labs sd-jwt-python | Python | `sd-jwt` | 20 | 22.5 k | yes | unclear | T1-indirect (jwcrypto) |
| SDJWT-001 | a-sit-plus/vck | Kotlin | `vck` | 73 | — | unclear | no | to be examined |
| SDJWT-010 | iotaledger/sd-jwt-payload | Rust | `sd-jwt-payload` | 9 | 1.3 k | unclear | unclear | to be examined (crypto-agnostic) |
| SDJWT-021 | OWF-Labs wallet-framework-dotnet | .NET | `WalletFramework.SdJwtVc` | 32 | — | no | no | T3 (ES256 hard-coded) |
| SDJWT-004 | authlete/sd-jwt | Java | `com.authlete:sd-jwt` | 37 | — | unclear | no | to be examined |
| SDJWT-002 | affinidi selective_disclosure_jwt | Dart | pub | 5 | 5.0 k | unclear | no | to be examined |

**SDJWT reserves:**
- eudi-lib-jvm-sdjwt-kt (GJ yes, but first signature only)
- OWF-Labs sd-jwt-rust (rejects multi-signature explicitly)
- affinidi-sd-jwt
- HeroSD-JWT (ML-DSA partial: alg names do not follow RFC 9964)
- sd-jwt-vc-dm
- eudi-lib-sdjwt-swift

**Note:** the EUDI reference library eudi-lib-jvm-sdjwt-kt stayed a reserve because of the popularity ranking (★25; vck ★73, authlete ★37). It nevertheless enters the measurement through the EUDI verifier in REF, because that verifier uses `eudi-lib-jvm-sdjwt-kt 0.20.1` and Nimbus.

### 2.3 COSE (5)

| id | Target | Language | ★ | COSE_Sign (multi-signer) | Semantics | ML-DSA | Treatment path (proposed) |
|---|---|---|---|---|---|---|---|
| COSE-001 | a-sit-plus/signum (`indispensable-cosef`) | Kotlin | 197 | no (Sign1 only) | — | no | T3 |
| COSE-034 | veraison/go-cose | Go | 66 | yes (API experimental) | **all** (documented) | partial | T2 (Signer/Verifier interface) |
| COSE-035 | web-auth/cose-lib | PHP | 19 (5.0 M/month) | yes | left to the application (documented) | **yes** (PHP 8.4 + OpenSSL 3.5) | T1 |
| COSE-036 | wolfSSL/wolfCOSE | C | 76 | yes | left to the application (per signer index) | **yes** | T1 (GPL-3.0) |
| COSE-014 | erdtman/cose-js | JS | 28 | yes (only the single signature matching the kid) | unclear | no | T3 |

**COSE reserves:** coset (ML-DSA identifier only; callback → T2), dark-bio crypto-rs (composite, with a custom COSE id), t_cose (version 2.x needed for COSE_Sign), ldclabs/cose.

### 2.4 REF — reference verifiers (outside n, 3 + 2 reserves)

| id | Verifier | Stack and dependency (evidence) |
|---|---|---|
| REF-003 | EUDI verifier endpoint | Kotlin. `eudi-lib-jvm-sdjwt-kt 0.20.1` + Nimbus (`gradle/libs.versions.toml` L17, L41–45) |
| REF-010 | ACA-Py `oid4vc` plug-in | Python. `cryptography<51` (`oid4vc/pyproject.toml` L35) |
| REF-011 | Credo `@credo-ts/openid4vc` | TS. `@openid4vc/*` 0.5.6 (identity-common-ts) |

**Reserves:**
- walt.id verifier-api
- irmago (Yivi): verifies the issuer signature with jwx v4.4+ and covers ML-DSA. **The only verifier candidate with a PQ arm** for the emulator.

### 2.5 Status of the pilot libraries

| Library | Status |
|---|---|
| jose | selected |
| @sd-jwt/core | selected (new repository: identity-common-ts) |
| joserfc | reserve |
| jwcrypto | eligible but outside the quota (pyjwt and python-jose lead in Python) |
| Authlib | excluded (K3: `authlib.jose` deprecated) |

Recommendation: do not force the pilots in. Report "n + pilots" as a sensitivity analysis.

## 3. PQ support landscape and its effect on the control–treatment design

### 3.1 Findings

Source: the 349 evidence rows in `support_evidence.csv`. 160 of them are automatic negative evidence: a pattern scan with 0 matches, at a pinned commit.

| Support | Within n = 31 | In the whole frame (those examined) |
|---|---|---|
| **Composite (JOSE/COSE, -04)** | **0** | Only jwx (reserve; the `jwx-go/compsig` extension is experimental, draft version not stated). Partial: dark-bio (custom COSE id, not the -04 identifier) |
| **ML-DSA (RFC 9964), native** | **4**: jose, IdentityModel, cose-lib, wolfCOSE | **8**: + jwcrypto, jwx, jwt-framework, irmago |
| ML-DSA partial | 2: jwt-kit (only 65/87, macOS 26+), go-cose (only via the interface) | 5: + coset (identifier only), HeroSD-JWT (incompatible alg names), dark-bio |
| ML-DSA unclear (crypto-agnostic or delegated) | 3: @sd-jwt/core, sd-jwt-python, sd-jwt-payload | — |

**Additional observations:**
- **The jwt.io data is outdated.** jwt.io shows only `panva/jose` as supporting ML-DSA. Yet the source code of at least 7 more libraries carries ML-DSA.
- **Environment conditions.** For most targets, ML-DSA working depends on the runtime:

  | Target | Required environment |
  |---|---|
  | IdentityModel | .NET MLDsa |
  | cose-lib | PHP 8.4 + OpenSSL 3.5 |
  | jwcrypto | pyca `mldsa` |
  | jwx | Go 1.27 or the extension |
  | jwt-kit | macOS 26+ |

  The applicability of the treatment arm becomes final once these conditions are met in a Linux container.

### 3.2 Effect on the design (proposal)

1. **The main arm (composite -04) cannot be applied natively in any n target.** Therefore the treatment must be set up per target with one of three classes (`CRITERIA-DRAFT.md` §5.5):
   - **T1-native:** the library verifies the PQ algorithm itself.
     - For the ML-DSA-65 arm there are 4 targets in n (jose, IdentityModel, cose-lib, wolfCOSE); jwt-kit conditional.
     - None in n for the composite arm; only jwx (reserve).
   - **T2-plug-in:** our own composite -04 / ML-DSA-65 verifier is plugged in through the library's **public** algorithm registry or callback API.
     - Proven paths: PyJWT (`register_algorithm`), jjwt (`sig().add`), jose2go (`RegisterJws`), go-cose (Signer/Verifier interface), @sd-jwt/core (verifier callback).
     - Among the reserves: jose-jwt (`RegisterJws`), coset (callback).
     - The policy layer stays the library's. In this way the L0–L5 measurement is valid.
   - **T3-unknown-alg:** the library cannot verify the PQ signature. A composite/ML-DSA signature produced with our own signer is presented and the library's "unknown alg" behaviour is measured (metamorphic relation M2).
     - The oracle output can only be accept-classical, reject or indeterminate; accept-hybrid is impossible.
     - This is also a PQ-specific failure mode: because the policy "PQ required" cannot be expressed, the library either fails open (falls back to classical) or fails closed (rejects altogether).
2. **McNemar and the distinction of a "PQ-specific gap".**
   - The paired comparison between the control arm (second signature EdDSA) and the treatment is meaningful only in the T1 + T2 subset.
   - T3 must be reported separately as an "absence of capability" category. Otherwise the McNemar difference and "not recognising the algorithm at all" get mixed up.
3. **Distribution of n over the treatment classes (proposal, to be frozen before the measurement):**

   | Arm | T1 | T2 (proven) | to be examined | T3 |
   |---|---|---|---|---|
   | ML-DSA-65 | 4 (+ jwt-kit conditional, + sd-jwt-python indirect) | 5 | 9 | remainder |
   | composite -04 | 0 | ≈5 | 9 | remainder |

   The 9 targets "to be examined": java-jwt, golang-jwt, JWT.NET, lcobucci, ruby-jwt, json-jwt, IdentityModel, spruceid/ssi, the vck/authlete/affinidi group. Their plug-in API is assigned to T2 or T3 by **API review** (without behavioural measurement) during adapter writing.
4. **Signer requirement.** For composite -04 our own JOSE/COSE signer is mandatory (version 3 §9.2: "our own signer for composite -04 JOSE"). For ML-DSA-65, OpenSSL 3.5 / liboqs is sufficient.

### 3.3 Multi-signature and policy inventory (n = 31)

- **General JSON multi-signature:** yes 4 (jose, json-jwt, @sd-jwt/core, sd-jwt-python), no 17 (compact only), unclear 6, not applicable in COSE 4.
  - **Consequence:** the stress configuration (d), i.e. General JSON, can be tested directly on only a few targets in the JOSE stratum.
  - Most targets are compact-only. For them the form of expressing L4 is "a mandatory PQ/composite alg per issuer" (see §6-P2).
- **Documentation status of the multi-signature semantics:**
  - Documented: any 1 (jose), all 1 (go-cose), left to the application 2 (cose-lib, wolfCOSE).
  - **Unclear: 10.**
  - According to code reading (not measured), several libraries look **only at the first signature** in General JSON: json-jwt, eudi-lib-jvm-sdjwt-kt, the compact conversion in sd-jwt-python, cose-js (kid match).
- **Algorithm allow-list:** per call 23, unclear 6, none 1 (cose-js), global/fixed 1 (WalletFramework: ES256 hard-coded).
- **Key–alg binding:** yes 18, no 3 (golang-jwt: left to the Keyfunc; cose-lib: "caller's responsibility"; cose-js), unclear 10.

## 4. Inter-library dependencies (for the independence assumption)

Units that delegate verification to another target:

| Unit | Target delegated to |
|---|---|
| sd-jwt-python | jwcrypto |
| eudi-lib-jvm-sdjwt-kt and the EUDI verifier | Nimbus |
| irmago | jwx |
| WalletFramework.SdJwtVc | Microsoft IdentityModel (`JwtSecurityTokenHandler`) |
| Credo | identity-common-ts (`@openid4vc/*`) |

The direct delegation cluster inside n: **WalletFramework → IdentityModel**. jwcrypto, on which sd-jwt-python depends, is outside n.

## 5. Risks

| # | Risk | Effect | Mitigation |
|---|---|---|---|
| R1 | **Change of the reference repository.** sd-jwt-js and oid4vc-ts were archived in September 2026 and moved to identity-common-ts. The commit `c7cf23dbc1b8` on which the pilot rests is in the old repository | Version gap between the pilot and C3 | Pin a commit in the new repository; re-run the pilot vectors on the new version (in the measurement phase) |
| R2 | **Linux build** (final K6). Swift targets (Swift-JWT, jwt-kit); ML-DSA environments (.NET MLDsa, PHP 8.4 + OpenSSL 3.5, wolfSSL ML-DSA build, Go 1.27) | Loss of a target or a treatment arm | Replacement rule (§5.4); a build pre-test as the first job |
| R3 | **Undocumented semantics.** The multi-signature semantics is unclear for 10 targets | The verdict "not expressible" becomes debatable | Evidence rule: two independent trials + line reference; otherwise "undetermined" |
| R4 | **The "first signature only" pattern** (code reading) | Acceptance may change with a permutation of the signature order | Add a permutation of the signature order as a metamorphic relation |
| R5 | **No native support for composite -04**, and the draft is unstable | In the main arm an accept-hybrid observation is possible only with T1 (jwx) and T2 | Treatment class into the pre-registration; compare the draft version of jwx-go/compsig with -04 (known-answer vector) |
| R6 | **Violation of independence** (§4) | The assumption of the binomial test weakens | Delegation clusters into the pre-registration; a sensitivity analysis that counts clusters as a single unit |
| R7 | **The popularity measure differs between ecosystems.** The language quota lets in low-popularity targets (frank_jwt 8.9 k/month; Swift-JWT) | Representativeness | Within-stratum percentile and the rule pre-registered; report an alternative rule (E5 without quotas) as a sensitivity |
| R8 | **Targets close to the activity limit:** Swift-JWT (2024-11-18), python-jose (2025-05-28), frank_jwt (2025-07-12) | Maintenance risk | K2 is recomputed at the freeze; a target that drops out is replaced by a reserve |
| R9 | **Coverage gap.** JOSE libraries outside jwt.io; PyPI has no search API; npm's COSE keyword may be incomplete | External validity | Limitations section; optional J4 scan |
| R10 | **Licence.** wolfCOSE GPL-3.0 | Distribution of the artifact | Separate container and licence note |
| R11 | **Snapshot drift.** Search and registry APIs change over time | Reproducibility | SHA-256 of `onbellek/` and of the input files into the pre-registration |
| R12 | **Privacy incident** (closed). An anonymous clone of a deleted Bitbucket repository triggered Git Credential Manager | — | The process was terminated **without receiving input**. All later git calls ran with credential helpers and prompts disabled (`credential.helper=`, `GCM_INTERACTIVE=never`). No credentials or personal data were sent |

## 6. Items to enter the pre-registration

The full list is in `CRITERIA-DRAFT.md` §7. In short:
1. Frame sources and queries: jwt.io commit `60b70f7d8d20`; SHA-256 of `onbellek/` and of the input files.
2. K1–K8, the E2 thresholds and exceptions, the licence rule, the monorepo exception.
3. Popularity score; quotas (18/8/5; n = 31); REF 3 (outside n); selection, reserve and Linux replacement rules.
4. Version pinning: `son_commit_sha`; the historical baseline backwards from this point.
5. Binomial thresholds: ≥21 / ≤10 at n = 31 (p = 0.035). If it drops to n = 30, ≥20 / ≤10.
6. Treatment class assignment (T1/T2/T3), in its frozen form.
7. Operationalisation of L4 (P2 below).
8. Adding the signature-order permutation to the metamorphic relations (R4).
9. Dependency clusters and the sensitivity analysis (R6).
10. Handling of the pilots: not forced in; "n + pilots" sensitivity.

## 7. Recommendations for the plan

| No | Recommendation |
|---|---|
| P1 | Accept **E2 + quota 18/8/5 (n = 31), REF outside n**. The choice of threshold does not change n; it only defines the eligible pool |
| P2 | **Define L4 in two forms.** For the 17 compact-only targets, L4 = "a required PQ (composite) algorithm per issuer/key; reject otherwise". For multi-signature targets, L4 = "every alg in the required set present and valid". If not defined, L4 comes out "not applicable" for more than half of the targets and the denominator of H6 shrinks |
| P3 | **Make T3 a separate category.** The treatment classes enter the pre-registration; McNemar only on T1 + T2, T3 reported as "absence of capability" (fail-open/fail-closed) |
| P4 | **Do the Linux build pre-test (K6) as a separate step before the measurement** (≤4 working hours per target). Pin the container images with the ML-DSA environments: OpenSSL 3.5, .NET MLDsa, PHP 8.4, Go 1.27 |
| P5 | **During adapter writing, document the plug-in API of the 9 targets "to be examined" and freeze their treatment class.** This is an API review, not a behavioural measurement |
| P6 | **For the wallet-side request object verification** (OID4VP A.3.2.2, goal G4), optionally build a small extra frame (outside n): eudi-lib-jvm-openid4vp-kt, eudi-lib-ios-openid4vp-swift, Multipaz. They are now outside with the decision "wallet" |
| P7 | **irmago for the emulator** (the only REF candidate that verifies ML-DSA) can be moved forward in the reserve order. This, however, means changing the rule (G first); it needs a decision of the maintainers |
| P8 | **Under R1, re-run the pilot vectors on the pinned version of identity-common-ts** (in the measurement phase) |

## 8. Files and reproduction

| File | Content |
|---|---|
| `FRAME.csv` | 198 candidates. Identity, metadata, 8 support columns each with its basis, criterion result (E2), exclusion reason |
| `SELECTION.csv` | Criterion results and decisions for E1–E5; popularity scores |
| `THRESHOLD-SENSITIVITY.csv` | Threshold options × stratum: eligible and selected counts, census n |
| `SCREENING.csv` | 306 screening rows: source, query, decision, reason |
| `collect_record.json` | Run record |
| `CRITERIA-DRAFT.md` | Criteria, thresholds, quotas, selection rule, exclusion reasons, pre-registration constants |
| `SUMMARY.md` | This document |
| `collect.py` | Collection script. `python collect.py --cevrimdisi` produces the same outputs from the cache only. `--desen-tara` runs the evidence hint scan (shallow clone, anonymous git) |
| `screening_decisions.csv` | Manual input |
| `jwtio_mapping.csv` | Manual input |
| `manual_flags.csv` | Manual input |
| `support_evidence.csv` | Manual input; 349 evidence rows |
| `onbellek/` | HTTP responses (personal-data fields removed), git HEAD records, pattern scan outputs |

**Limit:** the `destek_*` cells are an **inventory**. They rest on a documentation or code line, but they are not an L0–L5 result. The evidence for H6 will be produced by the adapter tests after the pre-registration.
