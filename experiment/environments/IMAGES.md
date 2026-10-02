# Language environment images — Step 9, task 4a (build pre-test)

> **Status:** done (25.09.2026). 12 environment images: 11 for the n/REF targets, one (`elixir`) only for the reserve candidate JOSE-031.
> **Rule:** Base images are official and pinned **by digest**. Image name `pq-a09-env-<language>:1.0`. No operating-system package repository (apt/apk) was **used** (work plan §3.3; §13 question 5 open).
> **Scope:** These images are only for installation/build and the import (import/link) check. No test vector was run and no signature was verified.

| Language | Image (local id) | Base image and digest | Tool versions | OpenSSL (source) | Note |
|---|---|---|---|---|---|
| JS/TS | `pq-a09-env-node:1.0` (`sha256:e2650858bc9c…`) | `node:24.21.0-trixie@sha256:be40f6a87b9b22215ddb20da0a2320a5c6d583fe3ee3b0024d9fa4f05b40c8fd` (Debian 13) | Node 24.21.0 (LTS), npm 11.19.0; git 2.47.3; gcc 14.2.0; python3 3.13.5 | Node bundles **3.5.8**; system 3.5.7 | WebCrypto ML-DSA-44/65/87 recognised (`SubtleCrypto.supports`, with an experimental warning). npm only `registry.npmjs.org`; `--ignore-scripts`. Log: `loglar/imaj-node.log` |
| Python | `pq-a09-env-python:1.0` (`sha256:94dbdfc92827…`) | `python:3.13-trixie@sha256:82c46c08c991d3d3ff10476ac5e386c2c28f27bbd3985a02c5e39fe99ab272eb` (Debian 13; built 2026-09-19) | CPython 3.13.15, pip 26.2.1; git 2.47.3; gcc 14.2.0. A venv per target; Poetry 2.3.2 for REF-010 (the version that produced the lock file) | system 3.5.7; the `cryptography` wheel bundles its own OpenSSL (50.0.1 → 4.0.2; in the REF-010 lock 43.0.3 → 3.3.2) | PyPI (`pypi.org`) + GitHub (REF-010 source and the `oscrypto` git dependency). Log: `loglar/imaj-python.log` |
| Go | `pq-a09-env-go:1.0` (`sha256:931657811dd7…`) | `golang:1.27.1-trixie@sha256:433790e515d27dc6003e847e644cc0af956985cf315c1c58a3b73ee2dd305183` (Debian 13) | Go 1.27.1; `GOPROXY=https://proxy.golang.org,direct`, `GOSUMDB=sum.golang.org`, `GOTOOLCHAIN=local` | Go has its own crypto; the stdlib **has `crypto/mldsa`** (FIPS 204); system 3.5.7 | Log: `loglar/imaj-go.log` |
| JVM | `pq-a09-env-jvm:1.0` (`sha256:1900053fd579…`) | `maven:3.9.16-eclipse-temurin-25-noble@sha256:dd8e01b3be719853578c07b57ff8d9bbbbfe746f802226f05b19689420815221` (Ubuntu 24.04) + Gradle distribution copied from `gradle:9.6.1-jdk25-noble@sha256:b94f2560a917545c815a1dedbb0d0cfc9f31083c777dd2cb72235fbcd5cbe8e3` | Temurin JDK 25.0.4+7, Maven 3.9.16, Gradle 9.6.1 (the same as the REF-003 wrapper); `maven-dependency-plugin` 3.8.1 pinned; Gradle automatic toolchain download disabled | Java has its own crypto: **the ML-DSA-44/65/87 signature names are registered in JCA SUN** (JEP 497); system 3.0.13 (not used) | Maven Central (`--strict-checksums`); for REF-003 also the Gradle Plugin Portal and `maven.waltid.dev` (§3 note). Log: `loglar/imaj-jvm.log` |
| PHP | `pq-a09-env-php:1.0` (`sha256:a89612973cf4…`) | `php:8.4-cli-alpine3.24@sha256:de082dce8399ed408c47a303ac7f126de659088b403d791cefc81a7b707ea0c1` (Alpine 3.24.2) + Composer binary copied from `composer:2.10.3@sha256:9715c7f69044da2a212a5fbde29ee7da24e364d426560ae6367b060236f847d7` | PHP 8.4.26 (NTS), Composer 2.10.3; modules: openssl, sodium, mbstring, curl, json, zlib… (no gmp/bcmath/zip); unzip via BusyBox `unzip`; no `bash` (scripts are POSIX sh) | **PHP openssl → OpenSSL 3.5.8** (Alpine) | The ML-DSA gate of cose-lib HEAD (PHP ≥ 8.4 + OpenSSL 3.5) is met at the version level. Packagist + GitHub dist zip. Log: `loglar/imaj-php.log` |
| Ruby | `pq-a09-env-ruby:1.0` (`sha256:031c9c53bb1a…`) | `ruby:3.4.11-trixie@sha256:da59b74df06952ff6e99b792ac7713010b8039c5989f0accaf6c97448b31d0ff` (Debian 13) | Ruby 3.4.11, RubyGems 3.6.9, Bundler 2.6.9 (`lockfile_checksums`); gcc 14.2.0 | ruby-openssl → system **OpenSSL 3.5.7** | RubyGems (`rubygems.org`). Log: `loglar/imaj-ruby.log` |
| Rust | `pq-a09-env-rust:1.0` (`sha256:b21d9e67309a…`) | `rust:1.98.1-trixie@sha256:a8a5f0a1e5fe7dfe1d352591e4a1c7dd2c08fd70475cae872cf3458ba0df0546` (Debian 13) | rustc/cargo 1.98.1; gcc 14.2.0; pkg-config 1.8.1; no cmake or clang (not needed) | system **OpenSSL 3.5.7** (libssl-dev headers; frank_jwt links to it); jsonwebtoken aws-lc-rs builds its own crypto | crates.io sparse index. Log: `loglar/imaj-rust.log` |
| .NET | `pq-a09-env-dotnet:1.0` (`sha256:4f1b25cf1a6e…`) | `mcr.microsoft.com/dotnet/sdk:10.0.401-resolute@sha256:d818bb3014d94172e93820d985130135870bd1760f02588a61263a85c966860e` (Ubuntu 26.04.1 LTS; **MCR** — Microsoft's official registry, not on Docker Hub) | .NET SDK 10.0.401, runtime 10.0.12; `net10.0`; **telemetry disabled** (`DOTNET_CLI_TELEMETRY_OPTOUT=1`); NuGetAudit disabled | system **OpenSSL 3.5.5**: `MLDsa`, `CompositeMLDsa`, `SlhDsa` → `IsSupported=True` (reflection; no key/signature) | nuget.org. Log: `loglar/imaj-dotnet.log` |
| Swift | `pq-a09-env-swift:1.0` (`sha256:7422932f6627…`) | `swift:6.4.0-trixie@sha256:c90a484cbd45ff768e05bfdb2a73c4cc8978de0d940d8eb2cf68fcede6bad8f8` (Debian 13) | Swift 6.4 (swift-6.4-RELEASE), SwiftPM; git 2.47.3 | system **OpenSSL 3.5.7** (libssl-dev + pkg-config already in the image); jwt-kit uses swift-crypto (BoringSSL) | SwiftPM = git clone from GitHub (anonymous). Log: `loglar/imaj-swift.log` |
| C/C++ | `pq-a09-env-c:1.0` (`sha256:2fa966ecdb8a…`) | `gcc:15.3.0-trixie@sha256:ead103e6d03b69232962d467f3520c3f70b6718c69ff71efcc08efe9011fadb6` (Debian 13; buildpack-deps base) | GCC/G++ 15.3.0, GNU Make 4.4.1, autoconf 2.72, automake 1.17, libtool, pkg-config 1.8.1; no cmake (not needed) | system **OpenSSL 3.5.7** (libssl-dev; jwt-cpp links to it). wolfCOSE uses **wolfSSL v5.9.2-stable**, built inside the container (with `--enable-mldsa`) | Sources from GitHub via anonymous git. Log: `loglar/imaj-c.log` |
| Dart (Other) | `pq-a09-env-dart:1.0` (`sha256:ea785da036e5…`) | `dart:3.13.4-sdk@sha256:33faf91bc941466a767ce845b4bbb5d578ecd180abe5ee243e9c8c039109d215` | Dart SDK 3.13.4 (stable); **analytics disabled** (`dart --disable-analytics`) | — (Dart's own crypto/packages) | pub.dev (outside the default list; Dart's official registry). Log: `loglar/imaj-dart.log` |
| Elixir (Other; reserve candidate only) | `pq-a09-env-elixir:1.0` (`sha256:7a7a4a5dd7e2…`) | `elixir:1.20.4@sha256:86ff0019e9f70662462d7394406e8dee03ea399fe11825708614b2a5ce5368aa` | Elixir 1.20.4, Erlang/OTP 29; Hex 2.5.1 and rebar3 (`builds.hex.pm`) | Erlang crypto → **OpenSSL 3.5.7** | hex.pm (outside the default list; Elixir's official registry). Log: `loglar/imaj-elixir.log` |

## OpenSSL 3.5+ requirement (requested to be documented)

| Target | Requirement | In this image | Note |
|---|---|---|---|
| COSE-035 cose-lib | PHP ≥ 8.4 + OpenSSL 3.5 with ML-DSA at run time (the `MLDSA::isSupported()` gate in HEAD) | PHP 8.4.26 + OpenSSL 3.5.8 | Release 4.8.2 has no ML-DSA source; the gate is meaningful only for HEAD. `isSupported()` was not called |
| JOSE-001 IdentityModel | .NET `MLDsa` (system OpenSSL on Linux) | .NET 10.0.12 + OpenSSL 3.5.5 → `MLDsa.IsSupported=True` | Not tried on an Ubuntu 24.04 (OpenSSL 3.0) base |
| JOSE-009 jose | WebCrypto ML-DSA of the runtime | Node 24.21.0 (bundled OpenSSL 3.5.8) → `SubtleCrypto.supports` ML-DSA-44/65/87 = true | Node warns that this is "experimental" |
| COSE-036 wolfCOSE | not OpenSSL: wolfSSL > 5.9.1-stable and `--enable-mldsa` | wolfSSL v5.9.2-stable, `WOLFSSL_HAVE_MLDSA` defined | depends on the build flag |
| Python targets | the OpenSSL bundled in `cryptography` (not the system one) | cryptography 50.0.1 → OpenSSL 4.0.2, `mldsa` module present; REF-010 lock 43.0.3 → 3.3.2, no `mldsa` | The system OpenSSL (3.5.7) does not determine Python crypto |

## Base images pulled (not deleted)

By rule, the work may delete only the `pq-a09-env-*` images. The following were pulled in this task. The end-of-session clean-up belongs to the maintainers (work plan §3.4 item 6): `composer:2.10.3`, `dart:3.13.4-sdk`, `elixir:1.20.4`, `gcc:15.3.0-trixie`, `golang:1.27.1-trixie`, `gradle:9.6.1-jdk25-noble`, `maven:3.9.16-eclipse-temurin-25-noble`, `mcr.microsoft.com/dotnet/sdk:10.0.401-resolute`, `node:24.21.0-trixie`, `php:8.4-cli-alpine3.24`, `python:3.13-trixie`, `ruby:3.4.11-trixie`, `rust:1.98.1-trixie`, `swift:6.4.0-trixie`. List: `_docker/yeni_imajlar_*.txt`. The `pq-a09-analiz:1.0` in this list belongs to another work.

## Disk (`docker system df`)

| | Before | After |
|---|---|---|
| Images | 28.76 GB | 45.76 GB |
| Local volumes | 2.194 GB | 2.194 GB |
| Build cache | 36.35 GB | 32.00 GB (reduced by other processes in between) |
| **Total** | **67.30 GB** | **79.95 GB (+12.65 GB; threshold 40 GB)** |

Raw records: `_docker/docker_df_once_*.txt`, `_docker/docker_df_sonra_*.txt` (`once` = before, `sonra` = after).

## Rebuilding

`docker build -t pq-a09-env-<language>:1.0 imajlar/<language>/`. The base digests are pinned in the Dockerfiles. Target run: `bash betikler/kos.sh <id> pq-a09-env-<language>:1.0`. The container runs with `--rm`, `--memory=6g` and the label `pq.agir=derleme`. Only `hedefler/<id>` (rw) and `betikler/konteyner` (ro) are mounted.
