# C3 inclusion criteria — DRAFT (Step 9a; to enter the pre-registration)

> **Status:** draft. Submitted to the maintainers' approval before the pre-registration is frozen.
> **Scope:** frame and metadata only. No decision in this document rests on library **behaviour**. The behavioural measurement (adapters, test vectors) is done after the pre-registration is frozen.
> **Source:** all numbers come from the outputs of `topla.py`: `CERCEVE.csv`, `SECIM.csv`, `ESIK-DUYARLILIK.csv`, `TARAMA.csv`, `topla_kayit.json`. The snapshot is dated 23–24.09.2026; the raw responses are under `onbellek/` (cache).
> **Consistency with the pre-registration decision (PR §2A Ö6):**
> - Reference verifiers (REF) are kept **outside** n and reported separately.
> - The main treatment arm is composite -04, the secondary arm pure ML-DSA-65.
> - The oracle is four-valued: accept-classical / accept-hybrid / reject / indeterminate.

---

## 0. Unit, population, strata

- **Unit (target):** a software library that verifies a JWS, COSE or SD-JWT signature **asymmetrically**, or an OpenID4VP verifier (RP).
  - **One** unit is taken from a code base (repository).
  - In multi-package repositories the unit is the package or module that carries the verification API (`paket_adi`, `alt_dizin`).
- **Population:** targets that are accessible as open source on the frame date (**REF_TARIH = 23.09.2026**) and appear in at least one of the sources of §1.
- **Strata.** A unit enters one stratum. The assignment priority from high to low:
  1. **REF:** an OID4VP verifier, or an OID4VC stack with a verifier role. **Does not enter n**, reported separately.
  2. **SDJWT:** a library whose primary purpose is SD-JWT / SD-JWT VC.
  3. **COSE:** a library whose primary purpose is COSE (RFC 9052).
  4. **JOSE:** a general JWS/JWT library.
- **Sample size:** n = JOSE + SDJWT + COSE.
- General JOSE libraries with SD-JWT support stay in the JOSE stratum; the `sd_jwt` column shows this support separately.

## 1. Frame sources (identification)

| Code | Source | Full definition | Noise floor |
|---|---|---|---|
| **J** | jwt.io library list | `src/data/libraries-next.json` in `jsonwebtoken/jsonwebtoken.github.io@60b70f7d8d20` (SHA-256 `3b1573be…5477`). **37 languages, 110 entries, 107 unique repositories** (104 GitHub + 3 Bitbucket). `panva/jose` is repeated under 4 language headings. There is 1 difference from the "106" of audit A; it is likely caused by the moment of counting and the normalisation | none; all are candidates |
| **H** | Successor rule | The successor of a candidate that declares itself deprecated and names **an explicit successor** also enters the frame: square/go-jose → go-jose/go-jose; authlib.jose → authlib/joserfc; sd-jwt-js → identity-common-ts; Sphereon SSI-SDK → Sphereon IDK | none |
| **P** | Pilot set | Version 3 §9.2: `jose`, `@sd-jwt/core`, `jwcrypto`, `Authlib`, `joserfc` | none |
| **T** | GitHub topic searches | `topic:sd-jwt`, `topic:sd-jwt-vc`, `topic:cose`, `topic:oid4vp`, `topic:openid4vp` (search API, by stars, first 100) | ≥5★ |
| **K** | Package registry searches | npm (`text=sd-jwt`, `keywords:cose`, `text=cose`), crates.io, NuGet, Packagist, Maven Central, RubyGems, pub.dev, pkg.go.dev; for PyPI name probing (`sd-jwt`, `pyeudiw`, `pycose`, `cwt`, `joserfc`) | npm ≥100/month; crates ≥300/90 days; NuGet ≥1,000 total; Packagist ≥50 total; RubyGems ≥1,000 total; pub.dev ≥100/30 days; Go: repository ≥5★. SD-JWT/COSE must appear in the name or description |
| **O** | Organisation lists | `eu-digital-identity-wallet`, `openwallet-foundation`, `openwallet-foundation-labs`, `cose-wg` (ecosyste.ms). Name/description filter: `sd-?jwt\|cose\|verifier\|openid4vp\|oid4vp\|oid4vc\|jose\|jws` | filter |
| **G / Gt** | Plan and task description | G: the reference verifiers of version 3 §9.2 (EUDI, ACA-Py `oid4vc`, Credo `openid4vc`). Gt: those named in the task description of Step 9a (walt.id, Sphereon, Spruce, EUDIPLO) | none |

- **Identification flow.** 386 search hits passed the noise floor and reduced to 306 screening rows. The screening decisions were distributed as follows:

  | Decision | Count |
  |---|---|
  | candidate | 91 |
  | irrelevant | 60 |
  | below the floor | 46 |
  | application | 33 |
  | duplicate | 32 |
  | document | 26 |
  | wallet | 9 |
  | mdoc | 5 |
  | issuer | 3 |
  | duplicate of jwt.io | 1 |

  Frame total **198 candidates**: JOSE 109, SDJWT 29, COSE 37, REF 23.
- **Query left out on purpose:** `topic:selective-disclosure`. Its hits come mostly from approaches other than SD-JWT (BBS, ZK, Merkle).
- **Known coverage gap:** the JOSE frame is jwt.io. Some widely used libraries not on this list stay outside the frame: `fast-jwt`, `josekit`, `jwt-simple`, `did-jwt`, `erlang-jose`, `SimpleJWT`. This is written as a limitation.

## 2. Screening (relevance; K7)

Every hit is recorded in `tarama_kararlari.csv` with its decision and reason; all of them are in `TARAMA.csv`.

| Decision | Definition |
|---|---|
| `aday` (candidate) | A library with a verification API, or an RP verifier |
| `yinelenen` (duplicate) | The same code base: successor or predecessor, fork, sub-package, repackaging, type definitions |
| `uygulama` (application) | Application, demo, playground, debugging tool, product/service SDK, plug-in |
| `cuzdan` / `ihracci` (wallet / issuer) | Wallet side or issuer service. C3 measures RP verifiers |
| `kapsam-disi-mdoc` (out of scope: mdoc) | mdoc / ISO 18013-5 / ISO 23220-4 (version 3 §7.4) |
| `belge` (document) | Specification, draft, WG or example repository |
| `ilgisiz` (irrelevant) | A library that handles only CBOR or COSE_Key; another protocol (EDHOC, WebAuthn, FDO, SCITT); application-specific code |
| `taban-alti` (below the floor) | A hit below the noise floor |

## 3. Inclusion criteria (eligibility)

A candidate counts as "eligible" only if it meets **all of K1–K8**.

| Code | Criterion | Operational definition | Data source |
|---|---|---|---|
| **K1** | Asymmetric verification | Verifies a JWS/COSE/SD-JWT signature with at least one asymmetric algorithm (RS/PS/ES/EdDSA/ML-DSA) | J: jwt.io `support` flags. Others: documentation |
| **K2** | Activity | HEAD commit of the default branch (committer date) ≥ **2024-09-23** (REF_TARIH − 24 months) | `git clone --depth 1 --filter=tree:0` (anonymous; credential helpers disabled); Bitbucket API; fallback: ecosyste.ms `pushed_at` |
| **K3** | Maintenance status | Must not be archived; the README or the registry must not declare "deprecated / not maintained / moved / legacy" | ecosyste.ms `archived`; README; `elle_bayraklar.csv` |
| **K4** | Open licence | An OSI-approved licence (SPDX). Sources are read in order: deps.dev → ecosyste.ms → package registry. The first **valid** value is taken; the few repositories that deps.dev calls "non-standard" are resolved from another source (e.g. go-cose → MPL-2.0) | `lisans`, `lisans_kaynagi` |
| **K5** | Popularity threshold | The threshold of §4. The indicators are combined with "or": stars, monthly downloads, dependent packages (ecosyste.ms). For registries that publish no monthly statistics (NuGet, RubyGems), total ≥ 12 × the monthly threshold. **Exceptions:** (a) official reference implementations in SDJWT and REF (EUDI, OWF, OWF-Labs); (b) plan-sourced ones in REF (G). For small components of one large monorepo, the repository stars are not used (dotnet/runtime, poco, mORMot, catalyst-voices) | `CERCEVE.csv` |
| **K6** | Linux container | Must build and run in a Linux x86_64 container. **Now only a pre-screening:** those that, according to the documentation, depend on Apple, Windows or a proprietary runtime are excluded. **Final test** in §5.4 | `elle_bayraklar.csv` |
| **K7** | Scope | Must be a library or an RP verifier (§2) | screening |
| **K8** | Uniqueness | One unit per code base; forks and repackagings are excluded | screening; ecosyste.ms `fork` |

**Evidence principle:**
- Every criterion decision is justified in `SECIM.csv` with the criterion code (`neden_E*`).
- If the data cannot be obtained, the criterion counts as "could not be verified" and the candidate is excluded.
- The support columns in `CERCEVE.csv` (General JSON, ML-DSA etc.) are **not used in the selection.** They are inventory and treatment-class information only (§5.5).

## 4. Threshold options (K5) and their effect on n

Source: `ESIK-DUYARLILIK.csv`. **n** = selected JOSE + SDJWT + COSE; **REF does not enter n.**

| Option | Definition | Eligible (JOSE / SDJWT / COSE / REF) | Eligible total (excl. REF) | Selected n | n in a census (no quota) |
|---|---|---|---|---|---|
| E1 | Uniform, loose: ≥50★ or ≥10k/month or ≥50 dependants | 52 / 10 / 14 / 11 | 76 | **31** | 76 (outside the range) |
| **E2 (proposed)** | Scaled per stratum: JOSE ≥200★ / ≥100k / ≥100 dependants; SDJWT and COSE ≥20★ / ≥1k / ≥10; REF ≥20★ | **41 / 15 / 17 / 14** | **73** | **31** (18 + 8 + 5) | 73 (outside the range) |
| E3 | Uniform, strict: ≥200★ or ≥100k/month or ≥100 dependants | 41 / 9 / 4 / 6 | 54 | 30 (COSE only 4) | 54 (outside the range) |
| E4 | Scaled per stratum, loose: JOSE ≥50★ / ≥10k / ≥50; SDJWT and COSE ≥10★ / ≥500 / ≥5 | 52 / 17 / 22 / 16 | 91 | 31 | 91 (outside the range) |
| E5 | High threshold + census: JOSE ≥1000★ / ≥1M / ≥500; SDJWT ≥50★ / ≥10k / ≥10; COSE ≥40★ / ≥10k / ≥10 | 25 / 10 / 14 / 7 | 49 | 31 | 49 (outside the range) |

**Interpretation:**
1. **No threshold alone reduces n to 25–40.** A census without quotas yields 49–91 targets. Therefore it is not the threshold that determines n but **the quotas and the selection rule of §5**. The threshold only defines the "eligible pool".
2. **A uniform threshold dries up the small strata.** Under E3 only 4 eligible targets remain in COSE and the quota (5) is not filled. The SD-JWT and COSE ecosystems are at least one order of magnitude smaller than JOSE. Hence a threshold scaled per stratum (E2) is proposed.
3. **n is almost independent of the option:** 31 under E1, E2, E4 and E5, 30 under E3. In JOSE all 9 core language groups are represented (8 of them under E5).
4. **Rationale of E2:** in JOSE, ≥200★ or ≥100k/month corresponds to the threshold "widely used in production". In SD-JWT/COSE, ≥20★ or ≥1k/month separates a maintained and actually used library from a hobby project. The official-reference exception compensates for the low star counts of the EUDI/OWF reference libraries (identity-common-ts has only 7★ but 100k/month downloads).

**Exclusion reasons under E2** (a candidate may have several reasons; 198 candidates including REF):

| Code | Count |
|---|---|
| K5 (below the threshold) | 85 |
| K2 (not active) | 56 |
| K1 (symmetric only) | 15 |
| K3 (archived/abandoned) | 14 |
| K4 (licence) | 12 |
| K6 (platform) | 4 |

The number excluded for K5 alone is 41.

## 5. Stratum quotas and selection rule

### 5.1 Quotas

| Stratum | Quota | Rationale |
|---|---|---|
| JOSE | 18 | 9 core language groups × 2 (task: "1–2 leading libraries per language") |
| SDJWT | 8 | The OID4VC-specific layer. ≥8 for the Fisher comparison |
| COSE | 5 | Small eligible pool (17 under E2). Low weight because mdoc is out of scope |
| **n** | **31** | Target n≈30 (25–40) |
| REF | 3 (outside n) | The three verifiers of version 3 §9.2. The emulator uses at most 2 verifiers (version 3 §7.14) |

### 5.2 Popularity score (threshold-independent, within the stratum)

- For every indicator, the **mid-rank percentile** is computed among all frame candidates of that stratum that have the indicator: p = (#<v + 0.5·#=v) / n. Indicators: stars, monthly downloads, dependent packages, total-only downloads.
- `pop_puani` is the highest of the available percentiles; the tie-breaker is the second highest percentile; at a final tie the `id` decides.
- In this way Bitbucket repositories without stars (Nimbus, jose4j), registries without download statistics (Maven, Go) and young but much-downloaded libraries (joserfc) become comparable.

### 5.3 Selection rule (deterministic; `topla.py` → `secim()`)

1. **JOSE:**
   - From each of the 9 core language groups (JS/TS, Python, JVM, Go, Rust, .NET, PHP, Ruby, Swift/ObjC) **at most 2** targets are taken in order of popularity.
   - If the quota is not filled, targets from the non-core groups (C/C++, Other) are added, again in order of popularity, at most 2 per group.
2. **SDJWT and COSE:** at most 2 targets per language group, in order of popularity, until the quota is filled.
3. **REF:** first the plan-sourced ones (G), then the popularity order; until the quota is filled.
4. **Reserves:**
   - (i) the next eligible candidate in every selected language group (for an in-group replacement).
   - (ii) the first 2 eligible candidates not selected in the general ranking of the stratum.

### 5.4 Linux test and replacement rule (K6, final)

- Every selected target is built in a Linux container with its version from the pre-registration (§7).
- The time limit is ≤4 working hours per target. If the build and a smallest verification call do not work, the target drops out.
- It is replaced first by the reserve of the same language group (5.3-4-i), otherwise by the general reserve of the stratum (5.3-4-ii).
- Every replacement is written with its reason to `SECIM-DEGISIKLIK.csv` (as an **addendum** to the pre-registration).
- A behavioural result **cannot be a reason** to replace a target.

### 5.5 Treatment class (for information; does not affect the selection)

Under PR §2A Ö6 the treatment arms are composite -04 (main) and ML-DSA-65 (secondary). Each target is assigned a treatment class:

| Class | Meaning |
|---|---|
| **T1-yerel** (native) | The library verifies the relevant PQ algorithm itself |
| **T2-eklenti** (plug-in) | Our own PQ verifier can be registered through the public API or supplied as a callback; the policy layer is the library's |
| **T3-bilinmeyen-alg** (unknown alg) | The library cannot verify the PQ signature. Only the "unknown alg" behaviour is observed; the oracle output can be accept-classical, reject or indeterminate |

The class is frozen before the measurement, based on `destek_kanitlari.csv`. (These classes later became TK1–TK3 in the pre-registration.)

## 6. Exclusion reasons (coded)

| Code | Reason | Example |
|---|---|---|
| D1 (K1) | Symmetric only (HS*) | pgjwt, jwt.q, 1c-jwt, JSONWebToken.swift |
| D2 (K2) | No commit in the last 24 months | ruby-jose (2024-01), COSE-JAVA (2021), COSE-C (2020), sd-jwt-kotlin (2024-05) |
| D3 (K3) | Archived, abandoned or handed over to a successor | square/go-jose, SermoDigital/jose, rhonabwy (archived); Authlib (`authlib.jose` deprecated → joserfc); Sphereon SSI-SDK ("legacy" → IDK); TBD ssi-sdk |
| D4 (K4) | Open licence could not be verified | deps.dev "non-standard" and no other source |
| D5 (K5) | Below the threshold | E2 table |
| D6 (K6) | Platform-dependent | JOSESwift (Apple Security/CommonCrypto/CryptoKit), yourkarma/JWT (iOS/macOS), SwiftyJWT (iOS), jose-rt (WinRT) |
| D7 (K7) | Out of scope | Application/demo/document/wallet/issuer/mdoc (screening stage) |
| D8 (K8) | Duplicate or fork | sd-jwt-js → identity-common-ts; oid4vc-ts; SIOP-OID4VP; mozilla go-cose forks |
| D9 | Eligible but outside the quota | Under E2, 14 JOSE, 1 SDJWT and 8 COSE candidates. Those not on the reserve list |

## 7. Constants to enter the pre-registration

1. `REF_TARIH = 2026-09-23`; activity limit `2024-09-23`.
2. jwt.io data file: commit `60b70f7d8d20`, SHA-256 `3b1573be…5477`.
3. The query strings and noise floors of §1; the `onbellek/` snapshot. Proposed: a SHA-256 list of `onbellek/` and the input files (`tarama_kararlari.csv`, `jwtio_esleme.csv`, `elle_bayraklar.csv`, `destek_kanitlari.csv`).
4. The definitions K1–K8, the E2 thresholds and exceptions; the set of invalid licences; the K5 total-download rule; the monorepo star exception.
5. Popularity score (§5.2), quotas (§5.1), selection and reserve rule (§5.3), Linux test and replacement rule (§5.4).
6. **Version pinning:** every target is pinned with the `son_commit_sha` value of `CERCEVE.csv` at the time of the freeze. If the package registry has a last release that corresponds to the same code, that release is also written. For the historical baseline, the last 3–5 releases (version 3 §7.10d) are chosen backwards from this pin.
7. **Operationalisation of L4 (proposal, see SUMMARY §6):** for a compact-only target, L4 is the application of the "required algorithm set per issuer" to a single-signature JWS. For a multi-signature target, L4 is requiring every algorithm in the required set to be **present and valid**.
8. The treatment class assignment (§5.5) and the dependency clusters (SUMMARY §5, risk R6) are frozen before the measurement.
9. Binomial thresholds: at n=31 the majority claim is **≥21/31** (p=0.035), the absence of a majority **≤10/31** (p=0.035). At n=30, ≥20 and ≤10 respectively (p=0.049). If n changes after a replacement, the threshold is recomputed with the same rule.

## 8. Items awaiting a decision (to the maintainers)

1. **Threshold:** E2 is proposed. E1, E4 and E5 produce the same n; only the width of the eligible pool changes. E3 does not fill the COSE quota.
2. **Pilot libraries:** by rule, `jose` and `@sd-jwt/core` were selected. `joserfc` stayed a reserve. `jwcrypto` is eligible but outside the quota (pyjwt and python-jose lead in Python). Authlib was excluded for K3. Recommendation: do not force the pilots in; report a sensitivity analysis "n + pilots".
3. **Fisher stratum:** is the comparison "SD-JWT-specific / general JOSE" done by stratum (SDJWT 8 / JOSE 18) or by the `sd_jwt` column? Recommendation: by stratum.
4. **COSE quota:** with 5 targets COSE can only be reported descriptively; no inferential test is possible.
5. **Scope extension (optional):** a registry scan for JOSE libraries outside jwt.io (J4). Cost ≈2–4 working hours; it does not change n, it only increases external validity.
