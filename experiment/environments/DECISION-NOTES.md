# Notes from the environment work to the maintainers (Step 9, task 4a)

> **Date:** 25.09.2026. **Write area:** only `experiment/environments/`.
> **Limit:** the following are **installation facts** only. No test vector was run and no signature verification call was made. The link checks are limited to loading types or symbols. Capability flags (e.g. `MLDsa.IsSupported`, `SubtleCrypto.supports`) show that the runtime recognises the algorithm; they do not show that a target verifies correctly.
> **Source:** the numbers come from script outputs: `derleme-sonuc.csv` (`betikler/topla_sonuc.py`), `kayit/surum_ozet.csv` (`betikler/surum_ozet.py`), `kayit/surum_dayanak.csv` (`betikler/surum_dayanak.py`), `kayit/surum_commit.csv` (`betikler/etiket_coz.py`).

## 0. Summary

- **34 targets** (n 31 + REF 3): **33 succeeded, 1 failed** (JOSE-104 Swift-JWT), **0 not reachable**.
- **Reserve:** two general reserve candidates were built for JOSE-104: JOSE-031 guardian and JOSE-017 jwt-cpp, both succeeded. **The choice is yours** (§1 K1). Reserve use confirmed: 0.
- **Images:** 12 images `pq-a09-env-*:1.0` (`IMAGES.md`). apt/apk were never used.
- **Disk:** Docker total 67.30 → 79.95 GB (+12.65 GB; threshold 40 GB).
- **Time per target:** 3–138 s. All targets stayed far below the ~20 min budget.

## 1. Items awaiting a decision

**K1 — Reserve for JOSE-104.** There is no in-group reserve in the Swift/ObjC group. The general reserve (5.3-4-ii) points to two candidates: JOSE-031 guardian (rank 1, pop 0.899) and JOSE-017 jwt-cpp (rank 2, pop 0.8317). As required by the task description, no choice was made. The recommendation is JOSE-031 (the first candidate in the general ranking). Details: `TARGET-CHANGES.md` §1.2. The change must also be entered in `SECIM-DEGISIKLIK.csv` (outside the write area of this work).

**K2 — Version pinning: `son_surum` or `son_commit_sha`?**
- The task description asked for `son_surum` (last release); CRITERIA §7.6, however, says "pinned with `son_commit_sha`; if a release corresponds to the same code, it is recorded as well".
- In this task 30 targets were installed by release and 4 by commit. For **21 of the 30 targets installed by release, the release commit differs from the frame HEAD** (`kayit/surum_ozet.csv`).
- **Effect on TK1 (static source check, `kayit/surum_dayanak.csv`):**
  - **COSE-035 cose-lib 4.8.2** has no ML-DSA source (no `src/Algorithm/Signature/MLDSA`). The "yes" basis of the inventory belongs to the frame HEAD (`1c854bf63c5c`).
  - The README of **COSE-034 go-cose v1.3.0** (2024-07) does not contain the "partial" basis of the inventory.
  - The releases of JOSE-009, JOSE-001 and JOSE-102 show traces of ML-DSA.
  - So the "4 targets in n with native ML-DSA support" of D-E3 drop to 3 under pinning by release (cose-lib drops out).
- Both HEADs can be installed (informational runs outside the CSV):
  - `_bilgi-COSE-035-HEAD`: 159 classes loaded, including `MLDSA65`.
  - `_bilgi-COSE-034-HEAD`: built.
- Which one is pinned at the freeze is your decision. If the commit is chosen, the record of these two targets can be replaced by the HEAD run; 19 targets would need a reinstall.

**K3 — Resolver for the Kotlin multiplatform targets (COSE-001, SDJWT-001).** The primary record was made with the Gradle module metadata. Maven chose `kotlinx-serialization-json` 1.8.0 in vck (mixed with `-core` 1.11.0); Gradle chooses 1.11.0. Recommendation: use Gradle and the `verification-metadata.xml` lock in the adapters.

**K4 — Configuration choices that must be written into the pre-registration** (all installation facts):
- JOSE-092 `jsonwebtoken` 11 crypto back end: `aws_lc_rs` or `rust_crypto`. Both build; the primary record is `aws_lc_rs` (README example).
- SDJWT-025 `ssi-sd-jwt` 0.6.0 feature set. The library depends on `ssi-jws`/`ssi-jwk` with `default-features=false`; the default installation has no signature algorithm crate. It builds with `secp256r1` and `ed25519` enabled (`_bilgi-SDJWT-025-ozellik`).
- `spomky-labs/cbor-php` for COSE-035 (the extra package the library `suggest`s).
- The pyjwt `[crypto]` and python-jose `[cryptography]` extras.
- **SDJWT-004 authlete sd-jwt and SDJWT-010 sd-jwt-payload contain no signature verification:**
  - authlete: `nimbus-jose-jwt` is only in `test` scope in the POM.
  - sd-jwt-payload: the lock contains no signature crypto crate.
  - Which JOSE layer the adapter uses must be written into the pre-registration. This also affects the D-E7 delegation analysis.
- **SDJWT-021 WalletFramework.SdJwtVc:** the public types are wallet/holder oriented (`SdJwtVcHolderService`). The verifier is in the transitive dependency `WalletFramework.SdJwtLib` 3.1.0 (`Roles.Implementation.Verifier`). The target assembly of the adapter must be clarified. The K7 scope question is also yours.

**K5 — Sources outside the default allow-list.** All are anonymous and without credentials; only downloads were made. If approval or recording is needed, please say so:
- MCR (`mcr.microsoft.com`, the .NET SDK image; the official image registry of .NET).
- Gradle Plugin Portal and `maven.waltid.dev` (REF-003; `waltid-mdoc-credentials-jvm` 0.11.0 is not on Maven Central).
- pub.dev (SDJWT-002).
- hex.pm and builds.hex.pm (candidate JOSE-031).
- metadata queries to the crates.io API with an anonymous User-Agent.
- apt/apk were never used (§13 question 5 can stay open).

**K6 — New delegation candidates inside n (for the D-E7 sensitivity):**
- **SDJWT-001 vck 7.0.1 → Signum 3.24.0** (`indispensable-josef/cosef`, `supreme` 0.15.0). COSE-001 is Signum 3.26.0.
- **SDJWT-021 WalletFramework → IdentityModel 7.5.2/8.0.1 + jose-jwt 5.0.0.** A known delegation; but **not the same code** as the pinned version of JOSE-001 (8.23.0).
- REF-011 Credo 0.7.1 → `@sd-jwt/core` 0.21.0 (the same version as SDJWT-015).
- REF-003 EUDI → eudi-lib-jvm-sdjwt-kt 0.20.1 + Nimbus 10.9 (the reserve version of Nimbus is 10.10).
- Candidate JOSE-031 → erlang-jose 1.11.12.

## 2. Installation facts relevant to the treatment class (TK1/TK2/TK3) and the L4 form (L4m/L4c)

| Target | Installation fact | Relevance |
|---|---|---|
| JOSE-009 jose 6.2.12 | The release shows traces of ML-DSA. Node 24.21.0 WebCrypto recognises ML-DSA-44/65/87 (`SubtleCrypto.supports`; Node gives an "experimental" warning). The `generalVerify` symbol exists | The environment condition for TK1 (ML-DSA) is met; L4m exists at symbol level |
| JOSE-001 IdentityModel 8.23.0 | .NET 10.0.12 + OpenSSL 3.5.5: `IsSupported=True` for `MLDsa`, `CompositeMLDsa` and `SlhDsa`. Whether IdentityModel uses `CompositeMLDsa` was not examined | The environment condition for TK1 (ML-DSA) is met. "To be examined" for composite (relation to JOSE composite -04 not verified) |
| COSE-035 cose-lib | No ML-DSA in 4.8.2; present in HEAD. The gate of HEAD is PHP ≥ 8.4 + OpenSSL 3.5; the image has PHP 8.4.26 + OpenSSL 3.5.8 (`isSupported()` not called) | TK1 depends on the K2 decision |
| COSE-036 wolfCOSE | ML-DSA **depends on a build flag**: wolfSSL `--enable-mldsa` and the condition "newer than v5.9.1-stable". With v5.9.2-stable `WOLFSSL_HAVE_MLDSA` is defined. `wc_CoseSign1_Verify` and `wc_CoseSign_Verify` were linked | TK1 only in this configuration; the flag set must be written into the pre-registration. The COSE_Sign symbol exists (for L4m) |
| JOSE-102 jwt-kit 5.3.0 | The ML-DSA sources build on Linux (CryptoExtras / swift-crypto 4.5.2); behind `@_spi(PostQuantum)`. The `MLDSA` type was linked (`_bilgi-JOSE-102-mldsa-spi`) | The inventory note "macOS 26+ → T3 likely on Linux" should be re-evaluated. The runtime was not tested |
| COSE-034 go-cose | The Go 1.27.1 stdlib has `crypto/mldsa`. `NewVerifier`, `Sign1Message` and `SignMessage` were linked | The environment is ready for TK2 (Signer/Verifier interface); v1.3.0 has no ML-DSA basis (K2) |
| JOSE-083 pyjwt | The `PyJWS.register_algorithm` symbol exists | Consistent with the TK2 basis |
| JOSE-034 jose2go | The `RegisterJws` symbol exists | Consistent with the TK2 basis |
| JOSE-033 golang-jwt | The `RegisterSigningMethod` symbol exists | TK2 candidate ("to be examined" in the inventory) |
| JOSE-092 jsonwebtoken 11 | According to the README, if no back end is selected, "provide your own `CryptoProvider`" | Could be a TK2 path (to be examined; T3 in the inventory) |
| SDJWT-015 @sd-jwt/core 0.21.0 | `GeneralJSON` and `SDJwtGeneralJSONInstance` are exported | L4m exists at symbol level |
| SDJWT-018 sd-jwt-python 0.10.4 | jwcrypto is not pinned; 1.6.1 in this installation. cryptography 50.0.1 (bundled OpenSSL 4.0.2) has the `mldsa` module | TK1-indirect, depends on the jwcrypto version and the lock |
| REF-010 ACA-Py oid4vc | The lock pins cryptography 43.0.3 (OpenSSL 3.3.2; no `mldsa` module) | Not for the PQ arm of the emulator (consistent with the irmago decision) |
| REF-003 EUDI | The ML-DSA-44/65/87 signature names are registered in JDK 25 JCA (JEP 497). The verifier uses eudi-lib-jvm-sdjwt-kt + Nimbus 10.9 | The use of ML-DSA in the verifier chain was not tested |

## 3. Licence notes

- **COSE-036 wolfCOSE: GPL-3.0** (LICENSE header). **wolfSSL v5.9.2-stable: GPLv3** (LICENSING; a GPLv2 exception for certain software).
  - Both are only measured; their code is not distributed (D-E11).
  - `experiment/environments/` contains no third-party source code. Only our own scripts, lock files and metadata (POM, nuspec, `.cargo_vcs_info.json`).
- JOSE-002 JWT.NET: CC0-1.0. JOSE-104 Swift-JWT: Apache-2.0. The candidates guardian and jwt-cpp: MIT.
- The other targets are consistent with the licences in the inventory: MIT / Apache-2.0 / BSD-3-Clause / MPL-2.0 (go-cose). The licence reported by the registry is in the field `lisans_kayit` of `hedefler/<id>/cikti/sonuc.tsv`.

## 4. Limitations

- **The "smallest verification call" part of §5.4 was not done** (as required by the task description; V+/V− will be done separately with the adapters). The final K6 test was completed only with its build/link half. Since JOSE-104 dropped out at the build stage, this gap does not affect that target's result.
- The depth of the link check differs per language:
  - JVM: all classes loaded without initialisation.
  - .NET: `GetTypes`.
  - PHP: class map.
  - JS/Python/Ruby: import and presence of symbols.
  - Go/Rust/Swift/C/Dart: build and type/symbol reference.
  - None shows that the verification path works.
- The lock files are the resolution of this run. Transitive versions can drift over time, so these locks should be used at the freeze.
- A reproducible build is not claimed (REF-003 bootJar, `libwolfcose.a`). What is pinned are the source commits and the dependency digests. Observation nonetheless: the `verification-metadata.xml` of REF-003 and `libwolfcose.a` gave the same output in repeated runs.
- npm installations were done with `--ignore-scripts`; install scripts were not run.
- The time per target (`sure_s`) is only the container time of the last attempt. Image builds and base image pulls are excluded. The number of attempts and the total time are in the `not` column.
- The informational runs outside the CSV (`hedefler/_bilgi-*`) are decision inputs; they do not enter the result counts.

## 5. Process notes

- **Work errors (fixed; the affected targets were re-run, attempt counts in the CSV):**
  - Python `write_text` wrote CRLF.
  - Alpine has no `bash` (exit 127).
  - A backslash was lost in the PHP check script.
  - MANIFEST line folding in REF-003.
  - The .NET anchor type was actually a namespace.
  - A conditional symbol was chosen in wolfCOSE.
  - A non-exported type was chosen in Dart.
  - The SwiftPM version parsing was wrong.
  - None of them changed a target's result. The only changed result is JOSE-104, and that is a real build error.
- **Privacy:**
  - Telemetry was disabled: .NET (`DOTNET_CLI_TELEMETRY_OPTOUT=1`), Dart analytics, npm (audit/fund/update-notifier), Composer audit, NuGetAudit.
  - No registry was logged into; no token or e-mail was used.
  - All git calls were made with `GIT_TERMINAL_PROMPT=0`, `GCM_INTERACTIVE=never` and `-c credential.helper=`. No credential prompt appeared.
  - No outward-facing action was taken.
- **Docker:**
  - No `prune` and no bulk deletion.
  - Containers ran one at a time, named `pq-a09-ortam-*`, with `--rm`, `--memory=6g` and the lock label `pq.agir=derleme`.
  - The 14 pulled base images were not deleted (rule: the work may delete only `pq-a09-env-*` images). List in `IMAGES.md` and `_docker/yeni_imajlar_*.txt`.
  - The image builds added small entries to the build cache. The clean-up by id is yours (§3.4 item 6).
- **COSE note (instruction of the maintainers):** Oracle A found that the C3 battery (v1.2) has no COSE vectors. The five COSE targets (COSE-001, -014, -034, -035, -036) were installed; their measurement scope will be decided separately. After the instruction no further environment effort was spent on COSE; COSE-036 was built the standard way. The cbor-php fix for COSE-035 and the HEAD informational runs had been done before the instruction.
- **Personal data scan (for Step 15):**
  - The user's e-mail address occurs in no file in `experiment/environments/` (scanned).
  - The lock and report files contain the public e-mail addresses of third-party package authors from the registries: `composer.lock`, `pip-report.json`, `poetry-report.json`, REF-010 `pyproject.toml`.
  - The Windows user name occurs only in the local mount path in `betikler/kos.sh` (the same as the example in work plan §3.4).
