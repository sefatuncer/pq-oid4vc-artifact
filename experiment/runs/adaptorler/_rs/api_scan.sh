#!/usr/bin/env bash
# =====================================================================
#  API scan (contract section 5.1): greps the pinned library sources inside the build stage
#  of each adapter image and writes command + output to <TARGET>/evidence/api-scan.txt.
#  The build stage is tagged as a temporary image and removed by name afterwards.
#  Usage: bash api_scan.sh [TARGET ...]   (default: all four)
# =====================================================================
set -u
cd "$(dirname "$0")"
export MSYS_NO_PATHCONV=1
P='algorithms|allow|register|deregister|required|eddsa|ed25519|ml-?dsa|mldsa|composite|okp|verifier|keyselector'
REG='/usr/local/cargo/registry/src/index.crates.io-*'

scan() { # <target> <command>
  local t=$1 cmd=$2 tmp="pq-a10-rs-b-$(echo "$1" | tr 'A-Z' 'a-z'):gecici"
  docker build -q --target build --build-arg TARGET="$t" -t "$tmp" -f Dockerfile . >/dev/null
  {
    echo "# $t API scan (contract section 5.1)"
    echo "# image: build stage of a10-$(echo "$t" | tr 'A-Z' 'a-z'):1, tagged temporarily as $tmp ($(docker image inspect --format '{{.Id}}' "$tmp"))"
    echo "# command: docker run --rm --network none --entrypoint sh $tmp -c '$cmd'"
    echo
    docker run --rm --network none --memory=4g --entrypoint sh "$tmp" -c "$cmd" 2>&1 | cut -c1-240 | head -400
  } > "$t/evidence/api-scan.txt"
  docker image rm "$tmp" >/dev/null
  echo "$t: $(wc -l < "$t/evidence/api-scan.txt") lines"
}

want() { [ $# -eq 0 ] && return 0; for a in "${ARGS[@]}"; do [ "$a" = "$1" ] && return 0; done; return 1; }
ARGS=("$@")
sel() { [ ${#ARGS[@]} -eq 0 ] || want "$1"; }

sel JOSE-091 && scan JOSE-091 "cd $REG/frank_jwt-3.1.4 && grep -m1 '^version' Cargo.toml && cat .cargo_vcs_info.json \
 && echo '## public API, algorithm selection and header handling (src/lib.rs)' \
 && grep -n -i -E '$P|pub (enum|struct|trait|fn)|Algorithm::[A-Z]|verify_signature|decode_segments|header' src/lib.rs | grep -v -E '^[0-9]+:\s*(//|#\[test)' | head -150 \
 && echo '## EdDSA / Ed25519 / ML-DSA / composite anywhere in the crate' && (grep -rn -i -E 'eddsa|ed25519|ml-?dsa|mldsa|composite' src README.md || echo '0 matches')"

sel JOSE-092 && scan JOSE-092 "cd $REG/jsonwebtoken-11.1.0 && grep -m1 '^version' Cargo.toml && cat .cargo_vcs_info.json \
 && echo '## features' && grep -n -A14 '^\[features\]' Cargo.toml \
 && echo '## allow-list, families, provider hooks (src/)' \
 && grep -rn -i -E '$P|new_for_family|fn family|pub enum Algorithm|InvalidAlgorithm|CryptoProvider|install_default|verifier_factory|validation\.algorithms|alg\.family' src --include=*.rs | head -160 \
 && echo '## algorithm names accepted from the header (Algorithm::from_str)' && sed -n '/impl FromStr for Algorithm/,/^}/p' src/algorithms.rs \
 && echo '## ML-DSA / composite' && (grep -rn -i -E 'ml-?dsa|mldsa|composite' src || echo '0 matches')"

sel SDJWT-010 && scan SDJWT-010 "cd $REG/sd-jwt-payload-0.5.1 && grep -m1 '^version' Cargo.toml && cat .cargo_vcs_info.json \
 && echo '## JOSE layer used by the crate (manifest, published lock)' && grep -n -B1 -A2 'josekit' Cargo.toml Cargo.toml.orig && grep -n -A2 'name = \"josekit\"' Cargo.lock \
 && echo '## signature handling in sd-jwt-payload (src, tests, examples, README)' \
 && grep -rn -i -E '$P|verif|signature|JwsSigner|josekit|decode_with|into_disclosed_object|key_binding' src tests examples README.md | head -120 \
 && echo '## ML-DSA / composite in sd-jwt-payload' && (grep -rn -i -E 'ml-?dsa|mldsa|composite' src || echo '0 matches') \
 && cd ../josekit-0.8.7 && echo '## josekit 0.8.7: JWS algorithms and verifier checks' \
 && grep -n -E 'pub use .* as (ES|RS|PS|HS|EdDSA)' src/jws.rs \
 && grep -n -E 'alg header claim|kid header claim|verifier\.algorithm|verifier\.key_id|A verifier is not found' src/jws/jws_context.rs \
 && grep -n -E 'pub fn decode_with_verifier' src/jwt.rs \
 && echo '## ML-DSA in josekit' && (grep -rn -i -E 'ml-?dsa|mldsa' src || echo '0 matches')"

sel SDJWT-025 && scan SDJWT-025 "cd $REG/ssi-sd-jwt-0.6.0 && grep -m1 '^version' Cargo.toml && cat .cargo_vcs_info.json \
 && echo '## dependencies on the JOSE crates' && grep -n -A3 -E '^\[dependencies\.ssi-jw[skt]\]' Cargo.toml \
 && echo '## verification entry points (ssi-sd-jwt src)' \
 && grep -rn -i -E '$P|pub (async )?fn (decode|verify|reveal)|decode_reveal_verify|VerificationParameters|KbJwtPayload|SdHash|sd_alg' src | head -90 \
 && cd ../ssi-jws-0.5.0 && echo '## ssi-jws 0.5.0 features' && grep -n -A8 '^\[features\]' Cargo.toml \
 && echo '## ssi-jws: algorithm choice and key binding in verification' \
 && grep -n -E 'fn validate_proof|fetch_public_jwk|verify_bytes\(claims|key\.algorithm|key_algorithm|AlgorithmMismatch|Err\(_\) => Err' src/verification.rs src/lib.rs | head -40 \
 && cd ../ssi-jwk-0.4.0 && echo '## ssi-jwk 0.4.0: Algorithm names' && grep -n -E '^\s+[A-Za-z0-9]+: \"' src/algorithm.rs \
 && cd ../ssi-claims-core-0.2.0 && echo '## VerificationParameters' && grep -n -E 'pub struct VerificationParameters|pub fn (from_resolver|with_date_time)|date_time' src/verification/parameters.rs \
 && echo '## ML-DSA / composite / allow-list in the ssi crates' \
 && (grep -rn -i -E 'ml-?dsa|mldsa|composite|allow.?list|allowed_alg' ../ssi-sd-jwt-0.6.0/src ../ssi-jws-0.5.0/src ../ssi-jwk-0.4.0/src ../ssi-jwt-0.6.0/src ../ssi-claims-core-0.2.0/src || echo '0 matches')"
