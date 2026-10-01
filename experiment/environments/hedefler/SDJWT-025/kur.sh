#!/usr/bin/env bash
# SDJWT-025 — kurulum/derleme ön testi (Adım 9 görev 4a). İmza doğrulama YOK.
export KRATE=ssi-sd-jwt SURUM=0.6.0 OZELLIK='' VARSAYILAN=true
exec bash /b/cargo.sh
