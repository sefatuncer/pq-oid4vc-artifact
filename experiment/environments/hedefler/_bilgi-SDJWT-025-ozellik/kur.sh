#!/usr/bin/env bash
# INFORMATION (outside derleme-sonuc.csv): does ssi-sd-jwt 0.6.0 build with the ssi-jws/ssi-jwk features (secp256r1, ed25519) enabled?
# ssi-sd-jwt depends on these crates with default-features=false; the algorithms are enabled through feature unification.
set -uo pipefail
source /b/ortak.sh
yaz ekosistem crates.io; yaz paket ssi-sd-jwt; yaz istenen_surum 0.6.0; yaz arac "$(rustc --version | cut -d' ' -f1-2)"
P=/tmp/p; mkdir -p $P/src; cd $P
cat > Cargo.toml <<'T'
[package]
name = "ortam-deneme"
version = "0.0.0"
edition = "2021"
publish = false

[dependencies]
ssi-sd-jwt = "=0.6.0"
ssi-jws = { version = "=0.5.0", features = ["secp256r1", "ed25519"] }
ssi-jwk = { version = "=0.4.0", features = ["secp256r1", "ed25519"] }
T
cp /w/main.rs src/main.rs 2>/dev/null || printf 'use ssi_sd_jwt as _;\nfn main(){println!("ok");}\n' > src/main.rs
if ! cargo build 2>&1; then yaz not "özellikli derleme başarısız"; bitir basarisiz 10; fi
cp Cargo.toml Cargo.lock "$C/"; yaz kilit_sha256 "$(ozet Cargo.lock)"
for n in p256 ed25519-dalek rsa k256; do yaz not "kilitte $n: $(grep -c "^name = \"$n\"$" Cargo.lock)"; done
./target/debug/ortam-deneme > "$C/ice_aktar.txt" 2>&1 && bitir basarili 0 || bitir basarisiz 20
