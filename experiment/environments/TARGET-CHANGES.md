# Target changes (CRITERIA-DRAFT §5.4) — Step 9, task 4a

> **Rule (§5.4):** A target that cannot be built or reached is replaced first by the reserve of the same language group (5.3-4-i); if there is none, by the general reserve of the stratum (5.3-4-ii). A behavioural result cannot be a reason. No behaviour was measured in this pre-test.
> **Status (25.09.2026):** 1 of the 34 targets dropped out (JOSE-104). For its replacement the rule points to **two** general reserve candidates. As required by the task description ("the rule allows two reserves" → no choice is made), **the choice was left to the maintainers**. Both candidates were built.
> **Reserve use confirmed: 0. Candidates built: 2.**
> Machine-readable record: `records/changes.csv`. Reserve types are in `records/target_list.csv`; `scripts/make_target_list.py` derives them from `collect_record.json`.

## 1. Change table

| # | Dropped target | Reason (pre-registered) | Replacement | Branch of the rule | Build result of the reserve | Evidence |
|---|---|---|---|---|---|---|
| 1 | **JOSE-104** Swift-JWT (Kitura), JOSE, Swift/ObjC; commit `29fe084d8740` (no release) | **K6 final: could not be built in a Linux container.** The dependency BlueRSA 1.0.203 does not build with the OpenSSL 3.x headers: `cannot find 'EVP_PKEY_size' / 'EVP_CIPHER_iv_length' in scope`. In OpenSSL 3 these names are macro aliases; Swift cannot import them. Kitura/OpenSSL 2.3.1 and BlueRSA 1.0.203 are the latest versions that can be resolved | **DECISION PENDING:** candidate 1 **JOSE-031** guardian (Elixir), candidate 2 **JOSE-017** jwt-cpp (C++) | 5.3-4-ii (general). There is no in-group reserve (5.3-4-i) for Swift/ObjC | JOSE-031: **succeeded** (guardian 2.5.0). JOSE-017: **succeeded** (commit `0a503e75084c`) | `logs/JOSE-104.log`, `logs/JOSE-104-attempt1.log`, `logs/JOSE-031.log`, `logs/JOSE-017.log` |

### 1.1 Why it could not be fixed (~20 min rule)

- Time spent ≈ 10 min: two runs and the analysis.
- No reasonable environment fix was found:
  - The error is not a missing system package but an OpenSSL 3 API incompatibility: BlueRSA calls names that became macros in OpenSSL 3.
  - A fix would require one of two routes. The first is an old Linux environment based on OpenSSL 1.1/1.0; for the development files this would most likely need an OS package repository, which is not permitted (work plan §3.3). The second is changing the dependency's code, which the task description forbids.
  - Other Swift base images were not tried (≈20 min rule and the "no wasted effort" instruction).
- In the same image JOSE-102 jwt-kit (swift-crypto/BoringSSL) built without problems. The problem is not the Swift environment but Swift-JWT's OpenSSL dependency.

### 1.2 Information for the choice (the decision is the maintainers')

| | JOSE-031 guardian | JOSE-017 jwt-cpp |
|---|---|---|
| Rank in the general reserve list (pop_puani) | 1st (0.899) | 2nd (0.8317) |
| Language group | Other (Elixir) | C/C++ |
| Version / commit | 2.5.0 / tag `v2.5.0` → `a9c9838b40f8` (not the same as the frame HEAD `6e86224f9c0a`) | no release → frame `son_commit_sha` `0a503e75084c` |
| Verification layer (installation fact) | delegates to erlang-jose 1.11.12 (`JOSE.JWS`); Erlang crypto → OpenSSL 3.5.7 | header-only; links to the system OpenSSL 3.5.7 |
| Source | hex.pm (outside the default list) | GitHub (anonymous git) |
| Licence | MIT | MIT |

**Recommendation (not binding):** JOSE-031. Reason: the first candidate in the general ranking. The natural reading of the rule follows the popularity ranking.

**Effect:**
- n = 31 does not change.
- Only JOSE-102 jwt-kit remains in the Swift/ObjC group.
- If JOSE-031 is chosen, Elixir is added to the "Other" group. If JOSE-017 is chosen, C/C++ is added.
- Under CRITERIA §5.4 the change must also be written to `SECIM-DEGISIKLIK.csv`. That file is not in the write area of this work (outside `experiment/environments/`).

## 2. Environment fixes without a target change

These do not change library code; they are reasonable fixes documented during installation.

| Target | Fix | Rationale | Evidence |
|---|---|---|---|
| COSE-035 cose-lib 4.8.2 | `spomky-labs/cbor-php` (^3.4 → 3.4.2) installed alongside | The `suggest` field of cose-lib: "Required by the RFC 9052 header reader and cryptographic structures … CoseSign1Tag and its siblings". Without the package, 6 COSE message Tag classes could not be loaded | `targets/COSE-035/output/composer.lock`, `logs/COSE-035-attempt3.log` |
| COSE-001, SDJWT-001 (Kotlin multiplatform) | Primary record with the Gradle module metadata, under the canonical coordinate. The Maven result was kept as well | Maven needs the `-jvm` artefact. Maven's "nearest wins" rule chose `kotlinx-serialization-json` 1.8.0 in vck; Gradle chooses 1.11.0 | `targets/{COSE-001,SDJWT-001}/output/` and `output-maven/` |
| REF-003 EUDI verifier | the installed Gradle 9.6.1 (the same version as the wrapper) instead of `./gradlew`. JDK 25 in the image; automatic toolchain download disabled | No download from services.gradle.org or of a foojay JDK is needed | `images/jvm/Dockerfile`, `logs/REF-003.log` |
| JOSE-083 pyjwt, JOSE-084 python-jose | `[crypto]` and `[cryptography]` extras | Asymmetric algorithms and the cryptography back end | `targets/JOSE-08{3,4}/output/requirements.lock` |
| JOSE-092 jsonwebtoken 11 | `aws_lc_rs` feature (primary); `rust_crypto` also builds (informational run) | The library requires a back end to be selected, or your own `CryptoProvider` (README) | `targets/JOSE-092/`, `targets/_info-JOSE-092-rust_crypto/` |
