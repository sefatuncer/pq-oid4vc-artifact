# Dil ortamı imajları — Adım 9, görev 4a (derleme ön testi)

> **Durum:** tamam (25.09.2026). 12 ortam imajı: 11'i n/REF hedefleri için, biri (`elixir`) yalnız yedek adayı JOSE-031 için.
> **Kural:** Taban imajlar resmîdir ve **özetle (digest)** sabitlenir. İmaj adı `pq-a09-env-<dil>:1.0`. İşletim sistemi paket deposu (apt/apk) **kullanılmadı** (IS-PLANI §3.3; §13 soru 5 açık).
> **Kapsam:** Bu imajlar yalnız kurulum/derleme ve içe aktarma (import/link) kontrolü içindir. Test vektörü koşulmadı, imza doğrulanmadı.

| Dil | İmaj (yerel kimlik) | Taban imaj ve özet | Araç sürümleri | OpenSSL (kaynağı) | Not |
|---|---|---|---|---|---|
| JS/TS | `pq-a09-env-node:1.0` (`sha256:e2650858bc9c…`) | `node:24.21.0-trixie@sha256:be40f6a87b9b22215ddb20da0a2320a5c6d583fe3ee3b0024d9fa4f05b40c8fd` (Debian 13) | Node 24.21.0 (LTS), npm 11.19.0; git 2.47.3; gcc 14.2.0; python3 3.13.5 | Node gömülü **3.5.8**; sistem 3.5.7 | WebCrypto ML-DSA-44/65/87 tanınıyor (`SubtleCrypto.supports`, deneysel uyarıyla). npm yalnız `registry.npmjs.org`; `--ignore-scripts`. Log: `loglar/imaj-node.log` |
| Python | `pq-a09-env-python:1.0` (`sha256:94dbdfc92827…`) | `python:3.13-trixie@sha256:82c46c08c991d3d3ff10476ac5e386c2c28f27bbd3985a02c5e39fe99ab272eb` (Debian 13; 2026-09-19 yapımı) | CPython 3.13.15, pip 26.2.1; git 2.47.3; gcc 14.2.0. Hedef başına venv; REF-010'da Poetry 2.3.2 (kilidi üreten sürüm) | sistem 3.5.7; `cryptography` tekerleği kendi OpenSSL'ini gömer (50.0.1 → 4.0.2; REF-010 kilidinde 43.0.3 → 3.3.2) | PyPI (`pypi.org`) + GitHub (REF-010 kaynağı ve `oscrypto` git bağımlılığı). Log: `loglar/imaj-python.log` |
| Go | `pq-a09-env-go:1.0` (`sha256:931657811dd7…`) | `golang:1.27.1-trixie@sha256:433790e515d27dc6003e847e644cc0af956985cf315c1c58a3b73ee2dd305183` (Debian 13) | Go 1.27.1; `GOPROXY=https://proxy.golang.org,direct`, `GOSUMDB=sum.golang.org`, `GOTOOLCHAIN=local` | Go kendi kriptosu; stdlib'de **`crypto/mldsa` var** (FIPS 204); sistem 3.5.7 | Log: `loglar/imaj-go.log` |
| JVM | `pq-a09-env-jvm:1.0` (`sha256:1900053fd579…`) | `maven:3.9.16-eclipse-temurin-25-noble@sha256:dd8e01b3be719853578c07b57ff8d9bbbbfe746f802226f05b19689420815221` (Ubuntu 24.04) + Gradle dağıtımı `gradle:9.6.1-jdk25-noble@sha256:b94f2560a917545c815a1dedbb0d0cfc9f31083c777dd2cb72235fbcd5cbe8e3`'den kopya | Temurin JDK 25.0.4+7, Maven 3.9.16, Gradle 9.6.1 (REF-003 sarmalayıcısıyla aynı); `maven-dependency-plugin` 3.8.1 sabit; Gradle araç zinciri otomatik indirme kapalı | Java kendi kriptosu: **JCA SUN'da ML-DSA-44/65/87 imza adları kayıtlı** (JEP 497); sistem 3.0.13 (kullanılmıyor) | Maven Central (`--strict-checksums`); REF-003 için ayrıca Gradle Plugin Portal ve `maven.waltid.dev` (§3 notu). Log: `loglar/imaj-jvm.log` |
| PHP | `pq-a09-env-php:1.0` (`sha256:a89612973cf4…`) | `php:8.4-cli-alpine3.24@sha256:de082dce8399ed408c47a303ac7f126de659088b403d791cefc81a7b707ea0c1` (Alpine 3.24.2) + Composer ikilisi `composer:2.10.3@sha256:9715c7f69044da2a212a5fbde29ee7da24e364d426560ae6367b060236f847d7`'den kopya | PHP 8.4.26 (NTS), Composer 2.10.3; modüller: openssl, sodium, mbstring, curl, json, zlib… (gmp/bcmath/zip yok); zip açma BusyBox `unzip`; `bash` yok (betikler POSIX sh) | **PHP openssl → OpenSSL 3.5.8** (Alpine) | cose-lib HEAD'in ML-DSA kapısı (PHP ≥ 8.4 + OpenSSL 3.5) sürüm düzeyinde sağlanıyor. Packagist + GitHub dist zip. Log: `loglar/imaj-php.log` |
| Ruby | `pq-a09-env-ruby:1.0` (`sha256:031c9c53bb1a…`) | `ruby:3.4.11-trixie@sha256:da59b74df06952ff6e99b792ac7713010b8039c5989f0accaf6c97448b31d0ff` (Debian 13) | Ruby 3.4.11, RubyGems 3.6.9, Bundler 2.6.9 (`lockfile_checksums`); gcc 14.2.0 | ruby-openssl → sistem **OpenSSL 3.5.7** | RubyGems (`rubygems.org`). Log: `loglar/imaj-ruby.log` |
| Rust | `pq-a09-env-rust:1.0` (`sha256:b21d9e67309a…`) | `rust:1.98.1-trixie@sha256:a8a5f0a1e5fe7dfe1d352591e4a1c7dd2c08fd70475cae872cf3458ba0df0546` (Debian 13) | rustc/cargo 1.98.1; gcc 14.2.0; pkg-config 1.8.1; cmake ve clang yok (gerekmedi) | sistem **OpenSSL 3.5.7** (libssl-dev başlıkları; frank_jwt bağlanıyor); jsonwebtoken aws-lc-rs kendi kriptosunu derler | crates.io seyrek indeks. Log: `loglar/imaj-rust.log` |
| .NET | `pq-a09-env-dotnet:1.0` (`sha256:4f1b25cf1a6e…`) | `mcr.microsoft.com/dotnet/sdk:10.0.401-resolute@sha256:d818bb3014d94172e93820d985130135870bd1760f02588a61263a85c966860e` (Ubuntu 26.04.1 LTS; **MCR** — Microsoft'un resmî kaydı, Docker Hub'da yok) | .NET SDK 10.0.401, çalışma zamanı 10.0.12; `net10.0`; **telemetri kapalı** (`DOTNET_CLI_TELEMETRY_OPTOUT=1`); NuGetAudit kapalı | sistem **OpenSSL 3.5.5**: `MLDsa`, `CompositeMLDsa`, `SlhDsa` → `IsSupported=True` (yansıma; anahtar/imza yok) | nuget.org. Log: `loglar/imaj-dotnet.log` |
| Swift | `pq-a09-env-swift:1.0` (`sha256:7422932f6627…`) | `swift:6.4.0-trixie@sha256:c90a484cbd45ff768e05bfdb2a73c4cc8978de0d940d8eb2cf68fcede6bad8f8` (Debian 13) | Swift 6.4 (swift-6.4-RELEASE), SwiftPM; git 2.47.3 | sistem **OpenSSL 3.5.7** (libssl-dev + pkg-config imajda hazır); jwt-kit swift-crypto (BoringSSL) kullanır | SwiftPM = GitHub git klonu (anonim). Log: `loglar/imaj-swift.log` |
| C/C++ | `pq-a09-env-c:1.0` (`sha256:2fa966ecdb8a…`) | `gcc:15.3.0-trixie@sha256:ead103e6d03b69232962d467f3520c3f70b6718c69ff71efcc08efe9011fadb6` (Debian 13; buildpack-deps tabanı) | GCC/G++ 15.3.0, GNU Make 4.4.1, autoconf 2.72, automake 1.17, libtool, pkg-config 1.8.1; cmake yok (gerekmedi) | sistem **OpenSSL 3.5.7** (libssl-dev; jwt-cpp bağlanıyor). wolfCOSE, konteyner içinde derlenen **wolfSSL v5.9.2-stable**'ı kullanır (`--enable-mldsa` ile) | Kaynaklar GitHub'dan anonim git. Log: `loglar/imaj-c.log` |
| Dart (Diğer) | `pq-a09-env-dart:1.0` (`sha256:ea785da036e5…`) | `dart:3.13.4-sdk@sha256:33faf91bc941466a767ce845b4bbb5d578ecd180abe5ee243e9c8c039109d215` | Dart SDK 3.13.4 (stable); **analitik kapalı** (`dart --disable-analytics`) | — (Dart kendi kriptosu/paketi) | pub.dev (varsayılan liste dışı; Dart'ın resmî kaydı). Log: `loglar/imaj-dart.log` |
| Elixir (Diğer; yalnız yedek adayı) | `pq-a09-env-elixir:1.0` (`sha256:7a7a4a5dd7e2…`) | `elixir:1.20.4@sha256:86ff0019e9f70662462d7394406e8dee03ea399fe11825708614b2a5ce5368aa` | Elixir 1.20.4, Erlang/OTP 29; Hex 2.5.1 ve rebar3 (`builds.hex.pm`) | Erlang crypto → **OpenSSL 3.5.7** | hex.pm (varsayılan liste dışı; Elixir'in resmî kaydı). Log: `loglar/imaj-elixir.log` |

## OpenSSL 3.5+ gereksinimi (belgelenmesi istenen)

| Hedef | Gereken | Bu imajda | Not |
|---|---|---|---|
| COSE-035 cose-lib | PHP ≥ 8.4 + çalışma zamanında ML-DSA'lı OpenSSL 3.5 (HEAD'deki `MLDSA::isSupported()` kapısı) | PHP 8.4.26 + OpenSSL 3.5.8 | 4.8.2 sürümünde ML-DSA kaynağı yok; kapı yalnız HEAD için anlamlı. `isSupported()` çağrılmadı |
| JOSE-001 IdentityModel | .NET `MLDsa` (Linux'ta sistem OpenSSL) | .NET 10.0.12 + OpenSSL 3.5.5 → `MLDsa.IsSupported=True` | Ubuntu 24.04 (OpenSSL 3.0) tabanında denenmedi |
| JOSE-009 jose | Çalışma zamanının WebCrypto ML-DSA'sı | Node 24.21.0 (gömülü OpenSSL 3.5.8) → `SubtleCrypto.supports` ML-DSA-44/65/87 = true | Node bunu "deneysel" diye uyarıyor |
| COSE-036 wolfCOSE | OpenSSL değil: wolfSSL > 5.9.1-stable ve `--enable-mldsa` | wolfSSL v5.9.2-stable, `WOLFSSL_HAVE_MLDSA` tanımlı | Derleme bayrağına bağlı |
| Python hedefleri | `cryptography`'nin gömülü OpenSSL'i (sistem değil) | cryptography 50.0.1 → OpenSSL 4.0.2, `mldsa` modülü var; REF-010 kilidi 43.0.3 → 3.3.2, `mldsa` yok | Sistem OpenSSL'i (3.5.7) Python kriptosunu belirlemiyor |

## Çekilen taban imajlar (silinmedi)

Kural gereği çalışma yalnız `pq-a09-env-*` imajlarını silebilir. Aşağıdakiler bu görevde çekildi. Oturum sonu temizliği yürütücüye aittir (IS-PLANI §3.4 madde 6): `composer:2.10.3`, `dart:3.13.4-sdk`, `elixir:1.20.4`, `gcc:15.3.0-trixie`, `golang:1.27.1-trixie`, `gradle:9.6.1-jdk25-noble`, `maven:3.9.16-eclipse-temurin-25-noble`, `mcr.microsoft.com/dotnet/sdk:10.0.401-resolute`, `node:24.21.0-trixie`, `php:8.4-cli-alpine3.24`, `python:3.13-trixie`, `ruby:3.4.11-trixie`, `rust:1.98.1-trixie`, `swift:6.4.0-trixie`. Liste: `_docker/yeni_imajlar_*.txt`. Bu listedeki `pq-a09-analiz:1.0` başka bir çalışmaya ait.

## Disk (`docker system df`)

| | Önce | Sonra |
|---|---|---|
| İmajlar | 28,76 GB | 45,76 GB |
| Yerel birimler | 2,194 GB | 2,194 GB |
| Build cache | 36,35 GB | 32,00 GB (arada başka süreçlerce azaltıldı) |
| **Toplam** | **67,30 GB** | **79,95 GB (+12,65 GB; eşik 40 GB)** |

Ham kayıtlar: `_docker/docker_df_once_*.txt`, `_docker/docker_df_sonra_*.txt`.

## Yeniden yapım

`docker build -t pq-a09-env-<dil>:1.0 imajlar/<dil>/`. Taban özetleri Dockerfile'larda sabittir. Hedef koşumu: `bash betikler/kos.sh <id> pq-a09-env-<dil>:1.0`. Konteyner `--rm`, `--memory=6g` ve `pq.agir=derleme` etiketiyle koşar. Yalnız `hedefler/<id>` (rw) ve `betikler/konteyner` (ro) bağlanır.
