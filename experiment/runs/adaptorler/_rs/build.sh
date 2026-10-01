#!/usr/bin/env bash
# =====================================================================
#  Builds the Rust adapter images a10-<target>:1 from this folder.
#  Usage: bash build.sh [TARGET ...]     (default: JOSE-091 JOSE-092 SDJWT-010 SDJWT-025)
#  Base image: pq-a09-env-rust:1.0. Network is needed during the build only (crates.io).
# =====================================================================
set -eu
cd "$(dirname "$0")"
export MSYS_NO_PATHCONV=1
TARGETS=("$@")
[ ${#TARGETS[@]} -eq 0 ] && TARGETS=(JOSE-091 JOSE-092 SDJWT-010 SDJWT-025)
for t in "${TARGETS[@]}"; do
  img="a10-$(echo "$t" | tr 'A-Z' 'a-z'):1"
  t0=$(date +%s)
  docker build -q --build-arg TARGET="$t" -t "$img" -f Dockerfile . >/dev/null
  echo "$t -> $img $(docker image inspect --format '{{.Id}}' "$img") ($(( $(date +%s) - t0 )) s)"
done
