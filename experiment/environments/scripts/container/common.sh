#!/bin/sh
# POSIX sh compatible (Alpine/BusyBox ash included)
# Shared helpers inside the container (Step 9 task 4a). No behaviour measurement: no signature verification call is made.
C=/w/output; mkdir -p "$C"
: > "$C/result.tsv"
yaz() { printf '%s\t%s\n' "$1" "$2" >> "$C/result.tsv"; }        # key<TAB>value
ozet() { sha256sum "$1" | cut -d' ' -f1; }                       # SHA-256 of the file
# Git without credentials (work plan §3.3, D-E12)
export GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never GIT_ASKPASS=/bin/true SSH_ASKPASS=/bin/true
git_anonim() { git -c credential.helper= -c core.askPass=/bin/true "$@"; }
bitir() {  # $1 = ice_aktar result (basarili/basarisiz), $2 = exit code
  yaz ice_aktar "$1"; yaz bitis "$(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "== SONUC: $1"; exit "${2:-0}"; }
yaz baslangic "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
yaz hedef "${HEDEF_ID:-?}"
