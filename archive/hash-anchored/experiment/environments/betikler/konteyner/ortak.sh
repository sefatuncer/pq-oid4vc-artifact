#!/bin/sh
# POSIX sh uyumlu (Alpine/BusyBox ash dahil)
# Konteyner içi ortak yardımcılar (Adım 9 görev 4a). Davranış ölçümü yok: imza doğrulama çağrısı yapılmaz.
C=/w/cikti; mkdir -p "$C"
: > "$C/sonuc.tsv"
yaz() { printf '%s\t%s\n' "$1" "$2" >> "$C/sonuc.tsv"; }        # anahtar<TAB>değer
ozet() { sha256sum "$1" | cut -d' ' -f1; }                       # dosyanın SHA-256'sı
# Kimliksiz git (IS-PLANI §3.3, D-E12)
export GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never GIT_ASKPASS=/bin/true SSH_ASKPASS=/bin/true
git_anonim() { git -c credential.helper= -c core.askPass=/bin/true "$@"; }
bitir() {  # $1 = ice_aktar sonucu (basarili/basarisiz), $2 = cikis kodu
  yaz ice_aktar "$1"; yaz bitis "$(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "== SONUC: $1"; exit "${2:-0}"; }
yaz baslangic "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
yaz hedef "${HEDEF_ID:-?}"
