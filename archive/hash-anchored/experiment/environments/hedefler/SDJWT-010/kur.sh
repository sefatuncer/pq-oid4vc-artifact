#!/usr/bin/env bash
# SDJWT-010 — kurulum/derleme ön testi (Adım 9 görev 4a). İmza doğrulama YOK.
export KRATE=sd-jwt-payload SURUM=0.5.1 OZELLIK='' VARSAYILAN=true
exec bash /b/cargo.sh
