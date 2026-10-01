#!/usr/bin/env bash
# Builds every adapter image a10-<target>:1 (31 targets): shared adapters via kur.sh and _rs/build.sh,
# per-target adapters from their own Dockerfile. Usage: bash _belge/kur_hepsi.sh   (from experiment/runs/adaptorler)
set -eu
cd "$(dirname "$0")/.."
export MSYS_NO_PATHCONV=1
bash _belge/kur.sh
bash _rs/build.sh
for d in */; do
  t=${d%/}
  case "$t" in _*) continue ;; esac
  [ -f "$t/Dockerfile" ] || continue
  docker build -q -t "a10-$(echo "$t" | tr 'A-Z' 'a-z'):1" "$t" >/dev/null && echo "$t built"
done
